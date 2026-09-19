"""Exercise the entrypoint and real go-jira against an isolated mock Jira.

Linux/Docker: python3 tests/smoke.py --image jira-action:test
Native fallback: python3 tests/smoke.py --binary /path/to/go-jira
The fallback replaces only the executable path in a temporary entrypoint copy;
it does not verify the Docker image. No third-party Python packages are needed.
"""

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlsplit


ROOT = Path(__file__).resolve().parent.parent
COMMENT = 'First line with spaces\n第二行: "quoted"; $(printf INJECTED) `id` *\n'


class JiraHandler(BaseHTTPRequestHandler):
    def log_message(self, *_args):
        pass

    def reply(self, status, body):
        data = json.dumps(body).encode()
        self.send_response(status)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlsplit(self.path).path
        self.server.requests.append(("GET", path))
        if self.headers.get("Authorization") != "Bearer smoke-test-token":
            self.reply(401, {"errorMessages": ["Unauthorized"]})
        elif path == "/rest/api/2/myself":
            self.reply(200, {"name": "smoke", "displayName": "Smoke Test"})
        elif path == "/rest/api/2/issue/" + self.server.issue_key:
            self.reply(200, {"key": self.server.issue_key, "fields": {}})
        else:
            self.reply(404, {"errorMessages": ["Unexpected endpoint"]})

    def do_POST(self):
        path = urlsplit(self.path).path
        self.server.requests.append(("POST", path))
        if self.headers.get("Authorization") != "Bearer smoke-test-token":
            self.reply(401, {"errorMessages": ["Unauthorized"]})
        elif path == "/rest/api/2/issue/" + self.server.issue_key + "/comment":
            body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
            self.server.comments.append(body["body"])
            if self.server.reject_comment:
                self.reply(500, {"errorMessages": ["Comment rejected"]})
            else:
                self.reply(201, {"id": "1", "body": body["body"]})
        else:
            self.reply(404, {"errorMessages": ["Unexpected endpoint"]})


class SmokeTests(unittest.TestCase):
    def setUp(self):
        self.server = ThreadingHTTPServer(("127.0.0.1", 0), JiraHandler)
        self.server.requests = []
        self.server.comments = []
        self.server.issue_key = "ABC-123"
        self.server.reject_comment = False
        thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        thread.start()
        self.addCleanup(self.server.server_close)
        self.addCleanup(thread.join)
        self.addCleanup(self.server.shutdown)

    def run_action(self, overrides=None, args=()):
        inputs = {
            "INPUT_BASE_URL": f"http://127.0.0.1:{self.server.server_port}",
            # HTTP is intentional: the mock listens only on loopback.
            "INPUT_INSECURE": "true",
            "INPUT_TOKEN": "smoke-test-token",
            "INPUT_REF": "feature/ABC-123",
            "INPUT_ISSUE_PATTERN": "([A-Z]{1,10}-[1-9][0-9]*)",
            "INPUT_COMMENT": COMMENT,
            "INPUT_MARKDOWN": "false",
        }
        inputs.update(overrides or {})
        # Do not inherit real Jira credentials, proxies, or .env files.
        env = {"PATH": os.environ.get("PATH", "/usr/bin:/bin"), **inputs}
        with tempfile.TemporaryDirectory(prefix="jira-smoke-") as directory:
            if OPTIONS.binary:
                entrypoint = Path(directory) / "entrypoint.sh"
                source = (ROOT / "entrypoint.sh").read_text()
                entrypoint.write_text(source.replace("/bin/go-jira", shlex.quote(OPTIONS.binary)))
                command = ["sh", str(entrypoint)]
            else:
                # Forward only Docker connection settings, never Jira credentials.
                for key in ("HOME", "DOCKER_HOST", "DOCKER_CONTEXT", "DOCKER_CONFIG",
                            "DOCKER_TLS_VERIFY", "DOCKER_CERT_PATH"):
                    if key in os.environ:
                        env[key] = os.environ[key]
                command = ["docker", "run", "--rm", "--network", "host"]
                for key in inputs:
                    command.extend(["--env", key])
                command.append(OPTIONS.image)
            return subprocess.run(
                [*command, "--env-file=", *args], env=env, cwd=directory,
                capture_output=True, text=True, timeout=45,
            )

    def assert_success(self, result, comment=COMMENT):
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual(self.server.comments, [comment])
        self.assertEqual(self.server.requests, [
            ("GET", "/rest/api/2/myself"),
            ("GET", "/rest/api/2/issue/" + self.server.issue_key),
            ("POST", "/rest/api/2/issue/" + self.server.issue_key + "/comment"),
        ])

    def test_inputs_and_multiline_comment(self):
        self.assert_success(self.run_action())

    def test_cli_arguments_remain_literal(self):
        self.assert_success(self.run_action(args=("--comment", COMMENT)))

    def test_custom_issue_pattern(self):
        self.server.issue_key = "team_42"
        self.assert_success(self.run_action({
            "INPUT_REF": "feature/team_42", "INPUT_ISSUE_PATTERN": "team_[0-9]+",
        }))

    def test_missing_base_url_fails_without_requests(self):
        result = self.run_action({"INPUT_BASE_URL": ""})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("base_url is required", result.stderr)
        self.assertEqual(self.server.requests, [])

    def test_authentication_failure_is_propagated(self):
        result = self.run_action({"INPUT_TOKEN": "invalid-test-token"})
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("error getting self", result.stderr)
        self.assertEqual(self.server.requests, [("GET", "/rest/api/2/myself")])
        self.assertEqual(self.server.comments, [])

    def test_comment_failure_is_propagated(self):
        self.server.reject_comment = True
        result = self.run_action()
        self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
        self.assertIn("error adding comments", result.stderr)
        self.assertEqual(self.server.comments, [COMMENT])


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--image", help="Built image; requires Linux host networking")
    target.add_argument("--binary", help="Native go-jira binary (without Docker coverage)")
    OPTIONS = parser.parse_args()
    if OPTIONS.binary:
        OPTIONS.binary = str(Path(OPTIONS.binary).resolve(strict=True))
    unittest.main(argv=[__file__], verbosity=2)

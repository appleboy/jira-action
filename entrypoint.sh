#!/bin/sh

set -eu

# The public Action input uses a different name from go-jira's environment key.
export INPUT_ISSUE_FORMAT="${INPUT_ISSUE_PATTERN:-${INPUT_ISSUE_FORMAT:-}}"

exec /bin/go-jira run "$@"

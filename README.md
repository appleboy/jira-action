# jira-action

CI/CD integrate with [Jira Data Center][1] on premise

[1]: https://www.atlassian.com/software/jira/data-center

## Parameters

| Name     | Description                                                                                        |
| -------- | -------------------------------------------------------------------------------------------------- |
| base_url | Base URL of Jira                                                                                   |
| insecure | Insecure for SSL                                                                                   |
| username | username for Basic authentication. This method is only recommended for tools like scripts or bots. |
| password | password for Basic authentication. This method is only recommended for tools like scripts or bots. |
| token    | Personal access token (PAT). This method incorporates the user account in the access token.        |
| ref      | The fully-formed ref of the branch or tag that triggered the workflow run                          |

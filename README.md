# jira-action

CI/CD integrate with [Jira Data Center][1] on premise

[1]: https://www.atlassian.com/software/jira/data-center

## Parameters

| Name         | Description                                                                                        | Default                     |
| ------------ | -------------------------------------------------------------------------------------------------- | --------------------------- |
| base_url     | Base URL of Jira                                                                                   |                             |
| insecure     | Insecure for SSL                                                                                   |                             |
| username     | username for Basic authentication. This method is only recommended for tools like scripts or bots. |                             |
| password     | password for Basic authentication. This method is only recommended for tools like scripts or bots. |                             |
| token        | Personal access token (PAT). This method incorporates the user account in the access token.        |                             |
| ref          | The fully-formed ref of the branch or tag that triggered the workflow run                          |                             |
| issue_format | matches string that references to an alphanumeric issue, e.g. ABC-1234                             | `([A-Z]{1,10}-[1-9][0-9]*)` |
| transition   | move issue to a specific status, e.g. Done, Start Progress                                         |                             |
| resolution   | set resolution of issue, e.g. Done, Fixed                                                          |                             |

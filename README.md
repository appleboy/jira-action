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

## Example

### Transition issue to In Progress when branch is pushed

```yaml
name: jira integration

on:
  create:
    types:
      - branch

jobs:
  jira-branch:
    runs-on: ubuntu-latest
    if: github.event.ref_type == 'branch'
    name: create new branch
    steps:
      - name: transition to in progress on branch event
        uses: appleboy/jira-action@v0.0.1
        with:
          base_url: https://xxxxx.com
          insecure: true
          token: ${{ secrets.JIRA_TOKEN }}
          ref: ${{ github.ref_name }}
          transition: "Start Progress"
```

### Transition issue to In Progress when commit is pushed

```yaml
name: jira integration

on:
  push:
    branches:
      - "*"

jobs:
  jira-push-event:
    runs-on: ubuntu-latest
    if: github.event_name == 'push'
    name: transition to in progress on push event
    steps:
      - name: transition to in progress on push event
        uses: appleboy/jira-action@v0.0.1
        with:
          base_url: https://xxxxx.com
          insecure: true
          token: ${{ secrets.JIRA_TOKEN }}
          ref: ${{ github.event.head_commit.message }}
          transition: "Start Progress"
```

### Transition issue to In Review when PR is opened

```yaml
on:
  pull_request_target:
    types: [opened, reopened, edited, synchronize]

jobs:
  jira-pull-request:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request_target'
    name: transition to in review when pull request is created
    steps:
      - name: transition to in review when pull request is created
        uses: appleboy/jira-action@v0.0.1
        with:
          base_url: https://xxxxx.com
          insecure: true
          token: ${{ secrets.JIRA_TOKEN }}
          ref: ${{ github.event.pull_request.title }}
          transition: "Finish Coding"
```

### Transition issue to Done when PR is merged

```yaml
name: jira integration

on:
  pull_request:
    types:
      - closed

jobs:
  jira-merge-request:
    runs-on: ubuntu-latest
    if: ${{ github.event.pull_request.merged }}
    name: transition to Merge and Deploy
    steps:
      - name: transition to in review
        uses: appleboy/jira-action@v0.0.3
        with:
          base_url: https://xxxxx.com
          insecure: true
          token: ${{ secrets.JIRA_TOKEN }}
          ref: ${{ github.event.pull_request.title }}
          transition: "Merge and Deploy"
          resolution: "Fixed"
```

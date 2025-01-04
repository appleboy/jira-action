# jira-action

GitHub Action for integrating [Jira][1] with your CI/CD pipeline. It allows you to automate the transition of Jira issues based on events in your GitHub repository, such as creating a branch, pushing a commit, opening a pull request, or merging a pull request. This helps streamline your development workflow by keeping your Jira issues up-to-date with the latest changes in your codebase.

[1]: https://www.atlassian.com/software/jira/data-center

English | [繁體中文](./README.zh-tw.md) | [简体中文](./README.zh-cn.md)

## Motivation

Since there is no official Jira API integration with GitHub Action available online, and considering that Jira now has both [Cloud][5] and [Data Center][1] versions with different API implementations, this project will initially focus on the [Data Center][1] version. This will allow friends who have purchased the enterprise version to achieve automatic integration of Jira Issue status adjustments through CI/CD.

The motivation behind this project is to provide a simple way to integrate Jira with GitHub or Gitea Actions for JIRA Data Center.

[5]: https://developer.atlassian.com/cloud/jira/platform/

## Parameters

| Name         | Description                                                                                                  | Default                     |
| ------------ | ------------------------------------------------------------------------------------------------------------ | --------------------------- |
| base_url     | The base URL of the Jira instance.                                                                           |                             |
| insecure     | Allow insecure SSL connections.                                                                              |                             |
| username     | Username for Basic authentication. Recommended only for scripts or bots.                                     |                             |
| password     | Password for Basic authentication. Recommended only for scripts or bots.                                     |                             |
| token        | Personal access token (PAT) for authentication. This method uses the user account associated with the token. |                             |
| ref          | The fully-formed reference of the branch or tag that triggered the workflow run.                             |                             |
| issue_format | Pattern to match strings referencing an alphanumeric issue, e.g., ABC-1234.                                  | `([A-Z]{1,10}-[1-9][0-9]*)` |
| transition   | Move the issue to a specific status, e.g., Done, In Progress.                                                |                             |
| resolution   | Set the resolution of the issue, e.g., Done, Fixed.                                                          |                             |
| author       | The author of the comment.                                                                                   |                             |
| comment      | The comment to add to the issue.                                                                             |                             |

## Example

### Transition issue to "In Progress" when a branch is created

Transition Jira issue to "In Progress" when a branch is created.

![flow01](./images/flow01.png)

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
        uses: appleboy/jira-action@v0.1.0
        with:
          base_url: https://xxxxx.com
          insecure: true
          token: ${{ secrets.JIRA_TOKEN }}
          ref: ${{ github.ref_name }}
          transition: "Start Progress"
```

### Transition issue to "In Progress" when a commit is pushed

Transition Jira issue to "In Progress" when a commit is pushed.

![flow01](./images/flow01.png)

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
        uses: appleboy/jira-action@v0.1.0
        with:
          base_url: https://xxxxx.com
          insecure: true
          token: ${{ secrets.JIRA_TOKEN }}
          ref: ${{ github.event.head_commit.message }}
          transition: "Start Progress"
          author: ${{ github.event.head_commit.author.username }}
          comment: |
            🧑‍💻 [~${{ github.event.pusher.username }}] push code to repository {color:#ff8b00}*${{ github.repository }}*{color} {color:#00875A}*${{ github.ref }}*{color} branch.

            See the detailed information from [commit link|${{ github.event.head_commit.url }}].

            ${{ github.event.head_commit.message }}
```

### Transition issue to "Code Review" when a PR is opened

![flow02](./images/flow02.png)

Transition Jira issue to "Code Review" when a PR is opened.

```yaml
on:
  pull_request_target:
    types: [opened, closed]

jobs:
  open-pull-request:
    runs-on: ubuntu-latest
    if: github.event_name == 'pull_request_target' && github.event.action == 'opened'
    name: transition to in review when pull request is created
    steps:
      - name: transition to in review when pull request is created
        uses: appleboy/jira-action@v0.1.0
        with:
          base_url: https://xxxxx.com
          insecure: true
          token: ${{ secrets.JIRA_TOKEN }}
          ref: ${{ github.event.pull_request.title }}
          transition: "Finish Coding"
          author: ${{ github.event.pull_request.user.login }}
          comment: |
            🔧 [~${{ github.event.pull_request.user.login }}] {color:#00875A}*${{ github.event.pull_request.state }}*{color} pull request from repository {color:#ff8b00}*${{ github.repository }}*{color} {color:#00875A}*${{ github.event.pull_request.head.ref }}*{color} to {color:#00875A}*${{ github.event.pull_request.base.ref }}*{color}.

            See the detailed information from [pull request link|${{ github.event.pull_request.html_url }}].

            Pull request: *${{ github.event.pull_request.title }}*
```

### Transition issue to "Resolved" when a PR is merged

![flow02](./images/flow02.png)

Transition issue to "Resolved" when a PR is merged.

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
        uses: appleboy/jira-action@v0.1.0
        with:
          base_url: https://xxxxx.com
          insecure: true
          token: ${{ secrets.JIRA_TOKEN }}
          ref: ${{ github.event.pull_request.title }}
          transition: "Merge and Deploy"
          resolution: "Fixed"
          author: ${{ github.event.pull_request.merged_by.login }}
          comment: |
            🔀 [~${{ github.event.pull_request.merged_by.login }}] {color:#00875A}*merged*{color} pull request from repository {color:#ff8b00}*${{ github.repository }}*{color} {color:#00875A}*${{ github.event.pull_request.head.ref }}*{color} branch to {color:#00875A}*${{ github.event.pull_request.base.ref }}*{color} branch.

            See the detailed information from [pull request link|${{ github.event.pull_request.html_url }}].

            Pull request: *${{ github.event.pull_request.title }}*
```

# jira-action

CI/CD 与本地的 [Jira Data Center][1] 整合

[1]: https://www.atlassian.com/software/jira/data-center

[English](./README.md) | [繁體中文](./README.zh-tw.md) | 简体中文

## 参数

| 名称         | 描述                                                               | 默认值                      |
| ------------ | ------------------------------------------------------------------ | --------------------------- |
| base_url     | Jira 实例的基本 URL。                                              |                             |
| insecure     | 允许不安全的 SSL 连接。                                            |                             |
| username     | 用于基本身份验证的用户名。仅建议用于脚本或机器人。                 |                             |
| password     | 用于基本身份验证的密码。仅建议用于脚本或机器人。                   |                             |
| token        | 用于身份验证的个人访问令牌 (PAT)。此方法使用与令牌关联的用户帐户。 |                             |
| ref          | 触发工作流程运行的分支或标签的完整引用。                           |                             |
| issue_format | 匹配字母数字问题的模式，例如 ABC-1234。                            | `([A-Z]{1,10}-[1-9][0-9]*)` |
| transition   | 将问题移动到特定状态，例如完成、进行中。                           |                             |
| resolution   | 设置问题的解决方案，例如完成、修复。                               |                             |

## 示例

### 当创建分支时将问题转换为“进行中”

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

### 当提交被推送时将问题转换为「进行中」

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

### 当拉取请求被打开时将问题转换为「审查中」

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

### 当拉取请求被合并时将问题转换为「完成」

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
          resolution: "Done"
```

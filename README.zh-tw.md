# jira-action

CI/CD 與本地的 [Jira Data Center][1] 整合

[1]: https://www.atlassian.com/software/jira/data-center

[English](./README.md) | 繁體中文 | [简体中文](./README.zh-cn.md)

## 參數

| 名稱         | 描述                                                               | 預設值                      |
| ------------ | ------------------------------------------------------------------ | --------------------------- |
| base_url     | Jira 實例的基本 URL。                                              |                             |
| insecure     | 允許不安全的 SSL 連接。                                            |                             |
| username     | 用於基本身份驗證的用戶名。僅建議用於腳本或機器人。                 |                             |
| password     | 用於基本身份驗證的密碼。僅建議用於腳本或機器人。                   |                             |
| token        | 用於身份驗證的個人訪問令牌 (PAT)。此方法使用與令牌關聯的用戶帳戶。 |                             |
| ref          | 觸發工作流程運行的分支或標籤的完整引用。                           |                             |
| issue_format | 匹配字母數字問題的模式，例如 ABC-1234。                            | `([A-Z]{1,10}-[1-9][0-9]*)` |
| transition   | 將問題移動到特定狀態，例如完成、進行中。                           |                             |
| resolution   | 設置問題的解決方案，例如完成、修復。                               |                             |

## 範例

### 當創建分支時將問題轉換為“進行中”

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

### 當提交被推送時將問題轉換為「進行中」

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

### 當拉取請求被打開時將問題轉換為「審查中」

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

### 當拉取請求被合併時將問題轉換為「完成」

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

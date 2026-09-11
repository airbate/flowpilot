# RUNBOOK — 回来后的最后一公里（预计 30 分钟）

> 项目其他部分已 100% 完成并验证（3 个 commit 在 github.com/airbate/flowpilot）。
> 本页是唯一剩余工作：点亮真实链路 → 部署 → 录视频 → 提交。按顺序执行。

## Step 1 · 解锁真实链路（3 分钟，二选一）

- **A. 交给助手**：在内置浏览器已打开的 Tavily 登录页与 Nebius 控制台完成注册登录，然后告诉助手"登录好了"。助手自动取 key 并完成 Step 2。
- **B. 粘贴 key**：把两个 key 给助手（Tavily `tvly-...` ＋ Nebius key）。
  - Tavily: https://app.tavily.com （登录后首页即见 API Key）
  - Nebius: https://tokenfactory.nebius.com/project/api-keys （登录 → Create API key）

## Step 2 · 点亮验证（助手执行）

```bash
cd backend && cp .env.example .env   # 写入两个 key
python -m scripts.smoke_nebius       # 自动校正 Nemotron-3 模型 ID 并回写 .env，PONG 实测
python -m scripts.smoke_tavily       # 搜索实测
# 然后跑一次真实端到端：Nemotron 规划 → Tavily 检索 → 归一化成表
```

验收：`GET /health` 返回 `nemotron: true, tavily: true`。

## Step 3 · 公网 Demo URL（10 分钟）

```bash
NEBIUS_API_KEY=... TAVILY_API_KEY=... MOCK_PLANNER=0 docker compose up --build -d
```

- 主机选择：Nebius AI Cloud VM（叙事加分）或任意 2C4G VPS；HTTPS 用 Caddy。
- 详细步骤与上架前核对清单：[DEPLOYMENT.md](DEPLOYMENT.md)。

## Step 4 · 录视频（1 小时）

- 脚本与分镜：[VIDEO_SCRIPT.md](VIDEO_SCRIPT.md)（≤3 分钟，英文配音，YouTube 公开）。
- 两个演示场景务必用真实 key 跑（Step 2 之后）。

## Step 5 · Devpost 提交（10 分钟，10-29 前完成）

- 项目描述直接粘贴：[DEVPOST.md](DEVPOST.md)。
- 填三个链接：repo / Demo URL / YouTube；勾选 **Best Apps and Agents** + **Best Use of Tavily**。
- 反馈提交：整理 [feedback-notes.md](feedback-notes.md)（顺带参评 Most Valuable Feedback）。
- 截止：2026-10-30 10:00 AM PT = **北京时间 10-31 凌晨 1:00**，务必 10-29 前提交。

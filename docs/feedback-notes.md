# Nebius / NVIDIA 工具反馈笔记

> Most Valuable Feedback 奖（$100×10）的评选基础是提交时对所用工具的反馈。
> 从第一天开始记：哪里顺畅、哪里卡壳、文档缺什么、希望改进什么。每周整理一次，M3 汇总成正式提交材料。

## 记录模板

```
### 2026-MM-DD ｜ 工具名 ｜ 使用环节
- 顺畅：
- 卡壳：
- 建议：
```

## 记录

### 2026-09-12 ｜ Nebius Token Factory（OpenAI 兼容 API）｜ 接入
- 顺畅：官方 OpenAI 兼容端点零摩擦——标准 `openai` SDK 换 `base_url` 即用，AsyncClient/JSON mode 全部按预期工作，这是集成成本最低的推理平台接入方式之一。
- 卡壳：文档站首页 quickstart 的示例模型是 `deepseek-ai/DeepSeek-R1-0528`，Nemotron 家族在主导航文档里完全未被提及——作为"NVIDIA 联办、要求必用 NVIDIA 模型"的黑松竞赛平台，参赛者第一小时找不到 Nemotron 的接入示例。
- 建议：在 Token Factory 文档首页给 Nemotron（nano/super/ultra）一个显眼入口 + 可复制的 JSON-mode/function-calling 示例，与黑客松强门槛直接对齐。

### 2026-09-12 ｜ Nebius Token Factory 文档站 ｜ AI 可读性
- 顺畅：`docs.tokenfactory.nebius.com/llms.txt` 存在且内容完整（curl 验证，含全站 .md 索引）——agent 开发者可以直接喂给 LLM 学 API，好评。
- 卡壳（轻微）：同一 URL 当天一次抓取返回过 404、数小时后 curl 正常，疑似 CDN 缓存不一致；目录页确认平台模型已切至 Nemotron-3 代（Super-120b 等），但文档站没有任何页面列出精确 API 模型 ID，未登录的控制台示例代码也只给 `MODEL_ID` 占位符——新用户拿到 key 前无法得知要填什么。
- 建议：文档站增加"当前可用模型与精确 API ID"页面（或让 /v1/models 支持免鉴权只读访问）；目录页每行直接给出可复制的 model id。

### 2026-09-12 ｜ Devpost 赛事页 ｜ 信息完整性
- 卡壳：`/prizes` 子路径 404，奖金结构只能从主页和规则页拼出来；评审四项未公布权重，参赛者无法做资源分配决策。
- 建议：独立奖金页 + 评审权重说明（哪怕是区间）。

### 2026-09-12 ｜ NVIDIA Nemotron ｜ 模型选型
- 顺畅：Super 49B 作为"规划 + 改写 + 归一化"单模型策略的候选，尺寸/能力比合适；开放权重（Apache 2.0）让"模型只是配置项"的叙事成立。
- 待验证：JSON mode 长计划（>10 步）的指令遵循稳定性——W2 拿到 key 后第一件事就是跑规划质量基准（同类目标 × 20，统计 schema 合法率与步骤合理性）。

### 2026-09-12 ｜ Tavily API ｜ 端点设计
- 顺畅：Search/Extract/Crawl/Map 四端点职责清晰，`from_step` 式链接（search 结果 → extract 输入）是 agent 场景的天然工作流，我们的 DSL 直接内建了这个链式参数。
- 卡壳（轻微）：Extract 对 JS 重度页面的 raw_content 质量参差，需要 fallback 到浏览器——建议 Extract 响应里带"页面是否 CSR/水化"的提示字段，帮助 agent 提前决定是否开浏览器。

# 触发率评测（v0.2.8）

[English](README.md)

检查改过 `description` 的技能在该加载时加载、不该加载时不加载：description 加了"二选一"说明的 7 个 Port、重写后的 `eli5`，以及阶段 3 的 15 个用例（`light-redirect`、`light-html-plan`、`light-decide`）回归。

- Host：Claude Code 2.1.296（每例 2 次）、pi 1.2.0（每例 1 次，未通过的用例补到 4 次）。本机没有装 Codex，未运行。
- 设置：每次运行各用一份独立的小型工具借用项目，整套集合只装在项目内。Claude Code 关掉了用户同步的 mattpocock 插件，pi 用 `--no-skills` 加项目内技能，所以只有 Light 版本参与竞争。
- 判定：Claude Code 用 Skill 工具调用该包；pi 读取该包的 `SKILL.md`。
- 用例：[cases.tsv](cases.tsv)。得分：[全部用例](w1-score.txt)、[修改 description 后的 eli5](w2-eli5-score.txt)。41 次被额度打断的 Claude Code 运行已重跑，只计重跑结果。

## 结果

| 用例 | Claude Code | pi |
| --- | --- | --- |
| 7 个 Port，应触发（`light-tdd`、`light-diagnosing-bugs`、`light-prototype`、`light-merge-conflicts`、`light-wizard`、`light-research`、`light-writing-for-agents`） | 14/14 | 7/7 |
| Port 近邻，不应触发（`light-wizard` W2、`light-research` S2） | 4/4 | 2/2 |
| `eli5` 应触发（E1、E2） | 4/4 | 修改后 6/6 |
| `eli5` 不应触发：把一节改写给非技术读者（E3） | 2/2 | 修改前 1/4，修改后 0/3 |
| `eli5` 不应触发：不指定受众的普通解释（E4） | 2/2 | 修改后 2/3 |
| `light-redirect`、`light-html-plan`（R1–R6、H1–H5） | 22/22 | 10/11（R5 重跑 1/4） |
| `light-decide` 应触发：对话中（D2）、大型实现中（D1b） | 0/4 | 2/2 |
| `light-decide` 不应触发（D3） | 2/2 | 0/4 |

## 因此做的改动

`eli5` 的 description 由 "asks for a non-technical version" 改为 "asks for a non-technical explanation. Not for rewriting a document for its readers."。Claude Code 在 E3 上本来就对；pi 的模型遇到"简化一下"仍会去拿 `eli5`。

## 局限

- pi 做决定时会大量读取 `SKILL.md`；只要读了就算触发，即使之后没按该技能做。它在 R5、D3、E3 上的"误触发"都没有写出提案或决策记录。部分运行中 pi 还浏览到了项目外的评测目录。
- Claude Code 不会在对话中或大型 `light-implement` 运行里选用 `light-decide`（阶段 3 起已知，记在联合接入的局限中）。
- 样本小，只有一个夹具领域，提示词只有中文。

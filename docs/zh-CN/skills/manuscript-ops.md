# manuscript-ops 使用指南

[英文指南](../../skills/manuscript-ops.md)

[包内契约](../../../skills/writing/manuscript-ops/SKILL.md)决定技能行为。

## 根据文稿任务选路线

这个技能用于笔记、SOP、报告和文稿工程。范围明确的写作任务可以直接交付整稿。内容风险决定需要哪些审阅；实际文稿管理需求决定是否初始化工程。

| 路线 | 工作 | 完成条件 |
| --- | --- | --- |
| Quick | 明确、低风险的文本修改 | 修改、检查后交付 |
| Structured | 需要来源、图文或格式检查的短篇改写和报告 | 完成整稿及适用的审阅、渲染检查后交付 |
| Project | 用户明确要求文稿工程，或需要可恢复批次、锁定版本及派生管理 | 按已有文稿工程门禁推进 |

短篇安全说明通常走 Structured，并保留来源与安全审阅。一次委派、多个参考文件和仅用于排版检查的 PDF 不构成工程初始化需求。规模以本次文稿判断。未知信息保持可见，只澄清会影响工作的决定或资料。

它是 model-invoked 能力；宿主支持时也可明确选择：

按所用 Host 的写法输入技能名，例如在 Claude Code 中输入 `/manuscript-ops`，在 Codex 中输入 `$manuscript-ops`。

```text
manuscript-ops
manuscript-ops resume
```

## 输入和检查

给出用途、读者、材料权威、交付物、获准的输出位置和已确认决定。Quick、Structured 不要求项目脚手架、Project Profile、审阅章程、Jujutsu 或门禁收据。指定子代理可以担任文稿写作者；审阅者保持只读，调用方在阶段返回后继续已授权工作。

[格式与来源契约](../../../skills/writing/manuscript-ops/references/formats.md)说明普通文档、旧 DOC 转换及有哈希绑定的提取关系。DOCX 等排版敏感输出必须实际渲染并检查页面。未执行的检查如实标明，文件可解析不表示排版已通过。

## 可选决策工具

宿主已有结构化决策 MCP 时，可以帮助理解任务范围和来源关系。[语义判断契约](../../../skills/writing/manuscript-ops/references/semantic-routing.md)规定输入、可选结果和经评测确定的置信策略。建议不能覆盖明确的工程需求或必需审阅；工具缺失、异常或不确定时，当前 Agent 按证据判断，不要求额外部署。

新评估使用 `needs-v2`。旧的未标版本 Project 快照按 `score-v1` 复核，保留批准与收据。只有使用内置脚本时才需要 Python 3.11+。

## 工程路线与安装

只有 Project 读取[完整工程流程](../../../skills/writing/manuscript-ops/references/project-route.md)。它复用获准状态，保留 user-invoked 交接边界，采用 `project-review` 的最终判定。尚不支持的版本保证应准确说明，不能把普通快照说成门禁通过。

Project 采用独立的 `PASS`、`FAIL` 或 `BLOCKED` 判定。确实缺少必需依赖时，返回 `BLOCKED` 并写明具体步骤与恢复条件；调用方收到阶段结果后处理剩余任务，不能把这个停止当成整个任务已经完成。

安装方法见[安装指南](../../INSTALLATION.zh-CN.md)。检查完整包并做隔离调用；源文件扫描只能证明结构。main 上的本地修复不等于已发布标签或全局部署。

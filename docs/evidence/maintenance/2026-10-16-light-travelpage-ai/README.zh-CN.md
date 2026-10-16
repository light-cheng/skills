# light-travelpage AI 连接审查（v0.2.8）

[English](README.md)

可选助手从专为 CPA 写的配置，改为连接任何 OpenAI 或 Anthropic 格式的 API，模型由页面主人在部署时选定（`scripts/ai-setup.mjs`）。

- 审查：software Profile。Critic（7 条）与 `light-code-review`（8 条）全部修复，其中包括隐藏输入回显 key、在 v0.2.8 之前生成的页面上运行配置、`AI_*` 与 `OPENAI_*` 设置混用。新 Evaluator 判定八条验收标准全部满足。结论：**PASS**（实现提交 `4c99626`）。
- 测试：模板测试 88/88，配置与生成脚本测试 15/15，仓库测试 586，本地 Wrangler Functions + D1 对模拟上游运行——均在 Node 26.7.0 上。
- 真实服务（经所有者同意，通过所有者自己的 OpenAI/Anthropic 格式网关）：配置脚本在 `openai-chat`、`openai-responses`、`anthropic-messages` 三种格式下都收到了真实工具调用。在本地 Wrangler Functions + D1 中，每种格式都保存了一条由真实工具调用创建的任务；相同请求重试和关闭开关后都没有再调用模型。
- 同一网关上的模型选择：从模型列表自动识别后完成了真实往返。让模型列表不可用时，配置脚本要求传 `--model`，手填模型 ID 后三种格式都完成了真实往返。手填一个服务没有的模型时，在往返一步失败，原有设置保持不变。终端里的交互式选择未对真实服务运行（由包内测试覆盖）。

局限：该网关虽然也提供 Anthropic 格式，却以 OpenAI 形状列出模型，所以页面主人需传 `--format anthropic-messages`。一次 `openai-chat` 运行的首个回复用了 34 秒，曾超过 55 秒的计划时限；该请求安全失败、未保存任何改动，重跑通过。本机未运行 CI 使用的 Node 22。本记录不含 key、网关地址和模型名。

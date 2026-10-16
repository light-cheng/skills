# 第一方维护与文档同步

[English maintenance contract](MAINTENANCE.md)

本页规定第一方 Skill 的生命周期和使集合可维护、可安装的文档同步要求。不复制 [AGENTS.md](../AGENTS.md) 或架构文档。

## 权威记录

每个事实只放在一个权威位置，其他地方链接过去：

| 事实 | 权威位置 |
| --- | --- |
| 包的行为、触发条件、调用方式、输入、输出、资源 | `skills/<category>/<skill-name>/SKILL.md`（及其配套文件） |
| Port 或改造包的来源 | `skills/<category>/<skill-name>/ATTRIBUTION.md` |
| 给人看的包清单 | [CATALOG.zh-CN.md](../CATALOG.zh-CN.md)，由包元数据同步 |
| 安装步骤和验证要求 | [docs/INSTALLATION.zh-CN.md](INSTALLATION.zh-CN.md) |
| 何时审查；审查者、引擎与验收的分工 | [docs/REVIEW_POLICY.zh-CN.md](REVIEW_POLICY.zh-CN.md) · [docs/REVIEWER_CONTRACT.zh-CN.md](REVIEWER_CONTRACT.zh-CN.md) |
| 仓库变更历史 | [CHANGELOG.zh-CN.md](../CHANGELOG.zh-CN.md) 和真实的发布记录 |
| 组合验证素材 | [docs/zh-CN/workflows/](zh-CN/workflows) 和链接的证据 |

## 当前同步基线

准入集合包含 `skills/` 下 **39 个第一方 Skill**（见 [CATALOG.zh-CN.md](../CATALOG.zh-CN.md)）。版本快照 v0.2.9：本页说明 v0.2.9（39 个包；仓库链接改为 `light-cheng`）。其[发布清单](evidence/releases/v0.2.9/RELEASE_MANIFEST.zh-CN.md)记录准备时的范围；实际观察到的发布与安装事实记入 `main` 上的发布收据。

上一版本是 [v0.2.8](https://github.com/light-cheng/skills/releases/tag/v0.2.8)（[发布收据](evidence/releases/v0.2.8/RELEASE_RECEIPT.zh-CN.md)）。

历史：`v0.1.1` 五个、`v0.1.2` 七个、`v0.1.3` 工具链迁移、`v0.1.4`（`light-kanban-worker`）、`v0.1.5` 调度与身份加固、`v0.1.6`（`kb-init`）。结构发现检查在 [tests/test_collection_discovery.py](../tests/test_collection_discovery.py) 与 [tests/test_composition.py](../tests/test_composition.py)，仅为结构证据，不是 fresh-install 证明。

v0.2.8 改名一个包（[v0.2.8 迁移说明](MIGRATION-v0.2.8.zh-CN.md)）。此前 v0.2.7 调整 12 个名称，见 [v0.2.7 迁移说明](MIGRATION-v0.2.7.zh-CN.md)和上一版本的 [v0.2.7 发布收据](evidence/releases/v0.2.7/RELEASE_RECEIPT.zh-CN.md)；v0.2.6 尝试的证据保留为历史。

## 变更流程

每次 **新增 / 更新 / 改名 / 弃用 / 移除 / Port / Adapt**：

1. 先执行 [Skill 准入](SKILL_ADMISSION.zh-CN.md) 的 reuse-before-invention 与 ownership gate——已批准的 Matt PORT（SPEC §14）只要带 `ATTRIBUTION.md` 且无运行时依赖即获架构授权。
2. 保留包边界、invocation direction、attribution 与必要资源。
3. 按 [审查策略](REVIEW_POLICY.zh-CN.md#一项改动需要多重的审查) 选审查分量：日常改动、仅文档、完整审查或发布；只收集该分量要求的证据。完整审查时 `review-loop` 为引擎，`project-review` 拥有最终验收。
4. 新准入再判断走低风险纯提示型快速通道还是完整路径，见 [Skill 准入](SKILL_ADMISSION.zh-CN.md)。
5. 只更新受改动影响的部分：README、目录、安装说明、治理链接、组合示例、discovery/composition 测试、attribution 与 changelog。
6. 先写未发布变更记录；未通过真实 release gate 前不宣称版本/tag/已验证命令。

## 同步矩阵

| 变更 | 必须检查 |
| --- | --- |
| **新增** | README、目录、安装指南、治理链接、受影响组合示例、discovery + composition 测试、changelog、适用 `ATTRIBUTION.md`、fresh-install 证据及所选快速/完整路径 verdict。 |
| **更新** | 包契约与行为证据；受影响目录/安装/attribution/示例/测试、兼容性与 changelog。 |
| **改名** | old-to-new 迁移指引；全部链接、目录记录、installer 示例、测试、示例、attribution 与 changelog。 |
| **弃用** | 目录状态、README 指引、替代/迁移路径、安装警告、示例、测试、changelog 与 release notes。 |
| **移除** | 确认无兼容 shim 需求；清理旧引用、保留迁移说明、更新目录/安装面并记录移除。 |
| **Port** | 已读上游源码、`ATTRIBUTION.md`（来源/路径/revision/license/Light 变更）、Light handoff 适配、无上游运行时依赖，外加新增矩阵的文档/测试。 |
| **Adapt** | 说明参照的上游模式与 Light 集成必要性，保留适用 `ATTRIBUTION.md`，外加更新矩阵的文档/测试。 |

## 目录与安装维护

目录条目须写明作用、when to use（适用时）、调用方式、包路径、状态、安装范围与证据。以包 metadata 为准，不另建静态路由表。

发布示例必须指向真实发布过的来源并与当前目录一致。针对 fresh 环境验证全仓与单包安装，保留精确命令、发布的 revision、host 与离线 discovery 结果；未验证前保持模板标记。

## 上游归属与兼容性

已批准的 Matt PORT 为自包含第一方包，带 `ATTRIBUTION.md`，运行时**不需要**安装 `mattpocock/skills`。其他上游可直接推荐而不复制；仍以第三方为主的修改版进入 `skills-3rdParty`。

发布前检查 attribution/license、依赖、host 位置、安装行为与已知行为差异。Light 主流程运行时不得要求 `mattpocock/skills` 或 `sol-advisor`。

## 组合示例

`docs/workflows/` 仅为验证资产，说明 Skill 组合与 handoff（`entry → handoff → stop → optional`），不复制 Skill 内部详细流程。不得成为隐藏准入门槛或自动 workflow。

## 弃用、回滚与发布

弃用需显式标记目录与安装指引、写明替代或声明无替代、在发布支持期内保留迁移信息并记入 changelog。

候选发布验证失败时停止 promotion，按适用 review 流程修复；不重写发布过的历史或删除证据。稳定发布仅需已准入包、同步文档、经验证的安装命令、必需 review 证据与真实版本/tag。

## Closeout 记录

收尾时记录最终仓库位置、已发版本/tag、已验证命令、第一方目录（当前包数）、已批准 Port / direct upstream / modified third-party 区分、证据、限制与迁移/归档指引。不得把结构或模拟证据写成 runtime proof。历史收尾必须写明确切的标识和局限——收尾不是结构证明。历史证据（`docs/evidence/`）保持不变。

v0.2.7 之后新增的证据不写出任何人的机器信息。提交证据文件前，运行 `python3 scripts/check_evidence_paths.py --apply <文件>...`：它把仓库根改成 `<repo>`、临时目录改成 `<tmp>`、主目录改成 `~`，形似 key 的值改成 `<redacted>`。只要 v0.2.7 之后新增的证据里还有个人路径或形似 key 的值，`python3 scripts/check_evidence_paths.py --check` 就失败；发布前运行它。更早的证据不改写。


## 分类目录的验证入口

从仓库根目录运行 `python3 -m pytest -q`。单独运行冻结包中的测试脚本时，使用 `PYTHONPATH=tests python3 <test-path>`；CI 同样设置 `PYTHONPATH=tests`。这保留冻结文件内容，同时让增加分类层后的脚本找到共享辅助模块。

## 发布文档的语境

冻结版本快照说明自身内容，当前 main 按已确认的双语收据说明稳定版本，发布清单保留准备时历史。使用共同的[文档状态契约](../skills/project/release-workflow/references/DOCUMENT-STATE.md)和固定树阶段检查；历史复核保持原范围。实际安装、发布和最终 main CI 与本地模拟分别记录。

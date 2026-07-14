# Android 性能分析生态缺口与路线图

这份路线图只管理跨仓协作问题。各项目版本、能力、发布与内部实现仍以各自仓库为准。

| 优先级 | 缺口 | 已采取的改进 | 下一验收条件 | 状态 |
| --- | --- | --- | --- | --- |
| P0 | 七个入口彼此独立，用户不知道从哪里开始 | 新建 Hub、统一中英文 README 表格，并给出可选端到端路径 | 六个公开仓远端 README 检查持续通过，私有 AIW 本地检查通过 | 已完成首版 |
| P0 | 重复表格容易漂移或泄露私有地址 | 用 `ecosystem.json` 生成 marker block；CI 只读检查公开仓；AIW 只输出 `Coming soon` | 周期 CI 通过且公开文件不含私有仓库元数据 | 已完成首版 |
| P0 | 博客案例 Trace 只有文件，没有可审计元数据 | 为 SystraceForBlog 增加目录、哈希、来源、授权、隐私和压缩包边界校验 | 15 个既有 artifact 全部被 catalog 覆盖；未知项显式为 `null` / `pending` | 已完成首版，历史元数据待补 |
| P1 | 采集、分析、Skill、文章之间缺少稳定 case ID | 先在 Hub 和案例仓定义相同的 case/provenance 约束 | 至少一个 demo 用同一 case ID 连接抓取配置、Trace、期望证据、Skill 与文章 | 待实现 |
| P1 | 跨仓兼容性只在各自 CI 内验证 | 保留 SmartPerfetto corpus 与 Perfetto-Skills fixture 的独立职责，不再创建第三套重复语料 | 同一公开小型 fixture 能通过 Perfetto Tools 输出、SmartPerfetto 导入与 Perfetto Skills smoke | 待实现 |
| P1 | 文章和系统知识没有稳定反向链接到 Skill/查询 | 计划给文章、AIW 章节和 Skill 增加可机器检查的 source/case reference | 一条端到端案例能从结论回到 Skill、SQL、文章与系统章节 | 待实现 |
| P2 | 缺少统一、可重复的负载生成层 | 优先接入已有 Android/Flutter Friends Circle 性能测试 App，不重复造 demo 仓 | 场景 manifest 能固定启动、滑动、页面切换和采集窗口 | 评估中 |
| P2 | 缺少公开的分析质量 benchmark | 暂时复用 SmartPerfetto Trace corpus 和 Perfetto-Skills fixtures，先补授权与期望证据合同 | 至少两个独立分析消费者需要同一发布周期后，再评估独立 benchmark 仓 | 暂不拆仓 |

## 为什么现在只新建一个 Hub

当前最缺的是导航、交接合同和可验证元数据，而不是更多仓库。SmartPerfetto 已有
manifest-driven Trace corpus，Perfetto Skills 也有独立 fixture，SystraceForBlog
承担文章案例。此时再建 Trace 或 benchmark 仓会增加同步和授权成本。等到统一
case ID、数据授权、期望证据和两个以上独立消费者都稳定后，再考虑拆分
`perfetto-analysis-benchmarks`。

## Adjacent assets

- [Friends Circle Android performance test app](https://github.com/Gracker/Friends-Circle-Demo-Apks-For-Power-and-Performance-Test)
- [Friends Circle Flutter performance test app](https://github.com/Gracker/Friends-Circle-Demo-Flutter-Apks-For-Power-and-Performance-Test)
- [Perfetto Auto-Pin for Chrome](https://github.com/Gracker/Perfetto-AutoPin-For-Chrome)

These are valuable workload or UI helpers, but they stay outside the seven-project
core until their handoff contract is explicit and maintained.

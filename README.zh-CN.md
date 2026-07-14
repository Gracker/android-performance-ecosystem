# Android Performance Ecosystem

[English](README.md)

这是 Gracker 维护的 Android 性能项目总入口。七个项目继续独立发布、独立运行；
本仓库只负责解释它们如何协作，并验证公共导航没有漂移或泄露非公开地址。

<!-- android-performance-ecosystem:start -->
## Android 性能分析生态

本仓库属于 [Android Performance Ecosystem](https://github.com/Gracker/android-performance-ecosystem)：它把可选插桩、采集、分析、系统知识与可复现案例连接成一套完整路径。

| 阶段 | 项目 | 作用 | 地址 |
| --- | --- | --- | --- |
| 插桩 | [TraceFix](https://github.com/Gracker/TraceFix) | 在编译期注入 App 侧 android.os.Trace section，让方法执行在运行时 Trace 中可见。 | [GitHub](https://github.com/Gracker/TraceFix) |
| 采集与测量 | [Perfetto Tools](https://github.com/Gracker/perfetto-tools) | 抓取可复现的 Perfetto Trace，并采集 FPS 或 Simpleperf 测量结果。 | [GitHub](https://github.com/Gracker/perfetto-tools) |
| 分析 | [SmartPerfetto](https://github.com/Gracker/SmartPerfetto) | 通过 AI 辅助 Web UI、CLI、报告、会话、对比和证据工作流分析 Trace。 | [GitHub](https://github.com/Gracker/SmartPerfetto) |
| Agent 分析 | [Perfetto Skills](https://github.com/Gracker/Perfetto-Skills) | 为 Agent 提供可移植的 Android、Linux、Chromium Perfetto 分析 Skill，并通过固定版本流程同步选定资产。 | [GitHub](https://github.com/Gracker/Perfetto-Skills) |
| 学习 | [Android Performance Blog](https://github.com/Gracker/Gracker.github.io) | 通过文章、系统原理和案例复盘讲解 Perfetto 与 Systrace 分析。 | [GitHub](https://github.com/Gracker/Gracker.github.io) · [网站](https://www.androidperformance.com/) |
| 系统知识 | Android Internal Wiki | 处于 alpha 阶段的 Android 系统知识库，覆盖 App、Framework、Native 与 Kernel 机制。 | **Coming soon** |
| 复现 | [Trace for Blog (SystraceForBlog)](https://github.com/Gracker/SystraceForBlog) | 提供文章使用的 Perfetto、Systrace 及相关案例文件，支持动手复现。 | [GitHub](https://github.com/Gracker/SystraceForBlog) |
<!-- android-performance-ecosystem:end -->

## 如何使用这套闭环

这是一条可选路径，不是所有项目都必须安装的强依赖流水线：

1. 平台 Track 不够时，用 TraceFix 给 App 方法补充 Trace section。
2. 用 Perfetto Tools 固定采集配置，并同时获得 FPS 或 Simpleperf 测量。
3. 需要完整产品体验时选 SmartPerfetto；希望现有 Coding Agent 在本地分析时选
   Perfetto Skills。
4. 用 Android Performance Blog 和 Android Internal Wiki 理解系统机制、复核结论、
   沉淀文章。
5. 从 Trace for Blog 下载已发布案例进行复现，再把验证过的经验反馈到采集配置、
   Skill、SmartPerfetto 工作流和文章。

Perfetto Tools 产生的 Trace 可以直接上传到 SmartPerfetto，也可以交给安装了
`$perfetto-performance-analysis` 的 Agent。两种分析入口彼此独立，TraceFix 也只是
需要更细 App 侧可观测性时的可选步骤。

## Hub 的边界

[`ecosystem.json`](ecosystem.json) 只规范跨项目元数据：名称、生命周期角色、公共入口、
语言、默认分支与 README 目标。各仓库仍然是自身版本、能力、安装、发布、数据和
许可证的唯一事实源。

首版直接补了三个缺口：

- 七个项目有统一入口和清晰交接路径；
- README 区块由清单生成，并通过只读远端检查防漂移；
- 博客案例 Trace 有来源、授权、隐私、哈希和压缩包边界清单。

剩余缺口、优先级与验收条件见 [ROADMAP.md](ROADMAP.md)。

## 验证

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ecosystem.py validate
python3 scripts/ecosystem.py check-readmes --remote
```

远端检查只读取公开仓库，不持有跨仓写权限，也不会尝试访问非公开仓库。

## 许可证与声明

Hub 自有的文档、清单和脚本采用 MIT License。被链接项目和 Trace 数据继续使用各自的
许可证或数据使用状态。本项目是独立社区项目，不代表 Google、Android 或 Perfetto 官方。

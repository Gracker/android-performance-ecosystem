# Android Performance Ecosystem

[简体中文](README.zh-CN.md)

An independent navigation Hub for Gracker's seven Android performance projects.
The projects keep separate releases and runtime boundaries; this repository
documents how they fit together and validates the shared public navigation.

<!-- android-performance-ecosystem:start -->
## Android performance ecosystem

The [Android Performance Ecosystem](https://github.com/Gracker/android-performance-ecosystem) brings its navigation Hub and seven core projects into an optional path from instrumentation and capture to analysis, system knowledge, and reproducible cases.

| Stage | Project | Purpose | Address |
| --- | --- | --- | --- |
| Navigate | [Android Performance Ecosystem](https://github.com/Gracker/android-performance-ecosystem) | Maintain the shared project map, handoff metadata, generated README navigation, and drift checks. | [GitHub](https://github.com/Gracker/android-performance-ecosystem) |
| Instrument | [TraceFix](https://github.com/Gracker/TraceFix) | Inject app-side android.os.Trace sections at build time so method work is visible at runtime. | [GitHub](https://github.com/Gracker/TraceFix) |
| Capture and measure | [Perfetto Tools](https://github.com/Gracker/perfetto-tools) | Capture repeatable Perfetto traces and collect FPS or Simpleperf measurements. | [GitHub](https://github.com/Gracker/perfetto-tools) |
| Analyze | [SmartPerfetto](https://github.com/Gracker/SmartPerfetto) | Investigate traces with an AI-assisted Web UI, CLI, reports, sessions, comparisons, and evidence workflow. | [GitHub](https://github.com/Gracker/SmartPerfetto) |
| Agent analysis | [Perfetto Skills](https://github.com/Gracker/Perfetto-Skills) | Give agents a portable Perfetto analysis Skill for Android, Linux, and Chromium, with selected assets synchronized through pinned workflows. | [GitHub](https://github.com/Gracker/Perfetto-Skills) |
| Learn | [Android Performance Blog](https://github.com/Gracker/Gracker.github.io) | Teach Perfetto and Systrace analysis through articles, system explanations, and case studies. | [AndroidPerformance.com](https://www.androidperformance.com/) · [GitHub](https://github.com/Gracker/Gracker.github.io) |
| System knowledge | [Android Internal Wiki](https://github.com/Gracker/android-internals-wiki) | An alpha knowledge base for Android mechanisms from App to Framework, Native, and Kernel. | [GitHub](https://github.com/Gracker/android-internals-wiki) |
| Reproduce | [Trace for Blog (SystraceForBlog)](https://github.com/Gracker/SystraceForBlog) | Provide the Perfetto, Systrace, and related case files used by articles for hands-on reproduction. | [GitHub](https://github.com/Gracker/SystraceForBlog) |
<!-- android-performance-ecosystem:end -->

## Use the loop

The path is optional rather than a mandatory dependency chain:

1. Add app-side sections with TraceFix when platform tracks are not enough.
2. Capture a repeatable trace and measurements with Perfetto Tools.
3. Choose SmartPerfetto for a complete product experience, or Perfetto Skills
   when an existing coding agent should analyze the trace locally.
4. Use the Android Performance Blog and Android Internal Wiki to understand,
   explain, and review the result.
5. Reproduce published cases from Trace for Blog, then feed proven lessons back
   into capture configs, Skills, SmartPerfetto workflows, and articles.

For example, a trace produced by Perfetto Tools can be uploaded to
SmartPerfetto or passed to an agent with `$perfetto-performance-analysis`.
Neither analysis surface requires TraceFix, and they do not require each other.

## What this hub owns

[`ecosystem.json`](ecosystem.json) is authoritative only for cross-project
metadata: project names, lifecycle roles, public entry points,
languages, default branches, and README targets. Each project remains the
source of truth for its own versions, capabilities, installation, releases,
data, and license.

The first implementation closes three concrete gaps:

- one discoverable map and handoff path across all seven projects;
- generated README marker blocks plus a read-only remote drift check;
- a provenance, privacy, license, and hash catalog for the article trace cases.

The remaining gaps and acceptance criteria are tracked in [ROADMAP.md](ROADMAP.md).

## Validate

```bash
python3 -m unittest discover -s tests -v
python3 scripts/ecosystem.py validate
python3 scripts/ecosystem.py check-readmes --remote
```

The remote audit reads public repositories only. It has no cross-repository
write token and never attempts to access non-public repositories.

## License and affiliation

This hub's original documentation, catalog, and scripts are MIT-licensed. Every
linked project and trace asset keeps its own license or data-use status. This is
an independent community project and is not an official Google, Android, or
Perfetto project.

# Atelier

Atelier 是一个本地优先的 AI 视频工作流工作站。它的目标不是做一个单一字幕 GUI、单点视频增强器，或 ComfyUI 克隆，而是把视频处理流程、硬件执行计划、任务队列、产物追踪和失败恢复组织成一个长期可扩展的桌面产品。

当前项目还没有开始搭建代码骨架。现阶段重点是先确定产品基调、设计语言、工程边界和文档事实源，然后再进入架构与实现。

## 核心产品模型

```text
Workflow Canvas   -> 定义要对视频做什么
Execution Canvas  -> 定义这些任务如何在本机硬件上运行
Queue Monitor     -> 跟踪执行、恢复、产物、日志和输出
```

长期判断标准：

```text
流程要看得见
硬件要管得住
失败要救得回
```

Atelier 应该给人的感觉是：

```text
用户设计流程
软件规划执行
队列稳定运行
失败可以恢复
产物可以追踪
硬件可以解释
```

## 项目范围

Atelier 计划服务 AI 辅助视频处理工作流，核心能力包括或计划包括：

- ASR 字幕生成。
- AI 字幕翻译 Agent。
- 字幕审校、一致性检查、术语统一和格式整理。
- 视频 AI 修复、增强、超分。
- 视频插帧。
- 音频提取和可选音频增强。
- 软字幕封装和硬字幕烧录。
- 多输出视频导出。
- 卡片式轻节点工作流设计。
- 硬件执行规划。
- 任务队列、任务监控、产物追踪和失败恢复。

这些能力最终应进入统一的 workflow / execution / queue 模型，而不是散落成一组互不关联的按钮。

## 文档索引

当前事实源：

- [AGENTS.md](./AGENTS.md)：给 AI coding agent 读取的工程边界、协作规则和开发纪律。保持英文。
- [DESIGN.md](./DESIGN.md)：Atelier 的产品视觉、交互、布局、密度和动效事实源。
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)：首版技术栈、模块边界、骨架规划和调研来源。
- [docs/design-md-references](./docs/design-md-references)：外部设计参考文档，只用于启发，不作为 Atelier 的事实源。
- [docs/plan](./docs/plan)：阶段性计划、调研记录和临时规划文档归档位置。

当前参考文件：

- [apple.DESIGN.md](./docs/design-md-references/apple.DESIGN.md)
- [linear.DESIGN.md](./docs/design-md-references/linear.DESIGN.md)
- [nvidia.DESIGN.md](./docs/design-md-references/nvidia.DESIGN.md)
- [ollama.DESIGN.md](./docs/design-md-references/ollama.DESIGN.md)
- [runwayml.DESIGN.md](./docs/design-md-references/runwayml.DESIGN.md)

未来随着项目成型，建议补充：

```text
docs/ARCHITECTURE.md
UI_INTERACTION_SPEC.md
WORKFLOW_NODE_SPEC.md
EXECUTION_PLAN_SPEC.md
WORKER_PROTOCOL.md
DATABASE_SCHEMA.md
HARDWARE_SCHEDULING.md
FAILURE_RECOVERY.md
RELEASE_CHECKLIST.md
```

根目录只保留：

```text
README.md
AGENTS.md
DESIGN.md
```

其他项目文档归档到 `docs/`；计划类文档归档到 `docs/plan/`。

## DESIGN.md 的定位

Atelier 采用独立 `DESIGN.md` 的文档方式：

```text
AGENTS.md  -> 怎么构建和维护项目
DESIGN.md  -> 项目应该如何呈现和感受
```

根目录 `DESIGN.md` 是 Atelier 的设计事实源。`docs/design-md-references/` 中的文档来自外部品牌风格参考，只能用于借鉴局部方法：

- `linear`：工程工具的克制感、状态密度和设置组织。
- `ollama`：本地 AI、模型、runtime 和命令输出语境。
- `nvidia`：GPU、性能指标和硬件状态表达。
- `runwayml`：视频媒体氛围和创作工具感。
- `apple`：空间纪律、控件精致度和平台级克制。

不要直接复制外部品牌色、字体、官网式 hero、营销页结构或品牌语言。

## 推荐技术方向

默认技术栈：

```text
Primary language: Python 3.11 / 3.12
GUI: PySide6
Workflow / Queue / Scheduler: Python
State database: SQLite
Worker protocol: JSON Lines over stdout/stderr 或结构化 IPC
Video processing: FFmpeg / ffprobe typed adapters
AI tasks: Python adapters + external model backends
```

Rust / C++ / CUDA 可以作为未来隔离 worker 或性能热点模块，但不应成为主应用默认架构。除非明确做架构迁移，不应把项目改成 Electron、Tauri、Celery、Redis 或 web stack。

## 架构原则

Atelier 应围绕这些模型设计：

```text
Project
  -> Job
      -> WorkflowGraph
      -> ExecutionPlan
      -> Task DAG
      -> Artifact
      -> Worker Events
```

职责边界：

- `GUI`：提交用户意图并渲染状态。
- `WorkflowGraph`：描述处理流程。
- `ExecutionPlan`：描述执行阶段、lane 和硬件绑定。
- `Scheduler`：决定任务何时运行、使用哪个资源。
- `Worker`：执行实际工作并报告结构化进度。
- `SQLite`：保存 jobs、tasks、artifacts、events、cache 和恢复状态。

GUI 不应直接运行重型视频、ASR、LLM 或 AI 增强任务。重任务应进入 worker process 或外部工具，并通过结构化事件回传状态。

## 产品主流程

推荐主流程：

```text
1. 选择输入媒体
2. 选择或设计 workflow
3. 检查 Workflow Canvas
4. 生成 Execution Plan
5. 必要时调整硬件计划
6. 加入 Queue
7. 监控执行进度
8. 失败时恢复、重试、跳过或导出可用产物
```

## 当前阶段

当前仓库处于“基调确定”阶段：

- 已有项目级 Agent 指南。
- 已有根目录设计事实源。
- 已搬入外部 `DESIGN.md` 参考文件。
- 尚未搭建应用代码、测试、数据库 schema 或 worker 协议实现。

下一步适合先补齐架构文档和最小项目骨架，再开始实现 UI、workflow graph、execution plan、scheduler、worker protocol 和 storage。

## 验证策略

项目成型后建议基线：

```powershell
python -m pytest
python -m ruff check .
python -m mypy .
```

如果这些工具尚未配置，不要声称验证通过。文档阶段的验证重点是：

- 项目名统一为 `Atelier`。
- `README.md`、`AGENTS.md`、`DESIGN.md` 职责分清。
- 根目录 `DESIGN.md` 与 `docs/design-md-references/` 的关系明确。
- 没有把尚未实现的功能写成已完成状态。

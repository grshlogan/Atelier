# Atelier

Atelier 是一个本地优先的 AI 视频工作流工作站。它的目标不是做一个单一字幕 GUI、单点视频增强器，或 ComfyUI 克隆，而是把视频处理流程、硬件执行计划、任务队列、产物追踪和失败恢复组织成一个长期可扩展的桌面产品。

当前项目已进入首版代码骨架搭建。现阶段重点是在不接真实模型和真实外部工具之前，先把工程边界、runtime 管理、结构化事件、Worker JSON Lines 协议、task.json 交接、最小 subprocess runner 边界、SQLite schema、只读工作台壳和可验证测试基线立稳。

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
- OCR 字幕 / 画面文字识别（未来可由第三方软件插件或自研 adapter 提供）。
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
- [docs/Atelier_Main_UI_Spec.md](./docs/Atelier_Main_UI_Spec.md)：主界面绘制规格 / concept implementation spec，服从 `DESIGN.md`，用于指导深色主工作台、Workflow 复页、可嵌入/可浮动 panels 和具体控件布局。
- [docs/UI_MOTION_SPEC.md](./docs/UI_MOTION_SPEC.md)：Atelier 专属 `AtelierUI` 动效系统、motion token、动画驱动、自绘控件、页面切换和开源参考边界规范。
- [docs/APP_CODE_MAP.md](./docs/APP_CODE_MAP.md)：当前代码树、文件职责和边界说明，给接手开发者或 AI 快速定位代码。
- [docs/RECENT_CHANGES.md](./docs/RECENT_CHANGES.md)：重要更改记录和接手记忆，除小范围改动外应持续更新。
- [docs/ARCHITECTURE.md](./docs/ARCHITECTURE.md)：首版技术栈、模块边界、骨架规划和调研来源。
- [docs/PRODUCT_FLOW_SPEC.md](./docs/PRODUCT_FLOW_SPEC.md)：首版产品主流程、内置 workflow、批量导入、调度执行、ASR/OCR/翻译和导出路径规划。
- [docs/MVP_ACCEPTANCE_SPEC.md](./docs/MVP_ACCEPTANCE_SPEC.md)：首版 MVP 验收标准、demo dataset、主流程用例、失败验收和 release gate。
- [docs/RELEASE_UPDATE_SPEC.md](./docs/RELEASE_UPDATE_SPEC.md)：打包、发布、OTA 更新、回滚和发布通道规范。
- [docs/RUNTIME_ENVIRONMENT_SPEC.md](./docs/RUNTIME_ENVIRONMENT_SPEC.md)：应用 runtime、工具 runtime、backend、model store 和健康检查规范。
- [docs/PLUGIN_SYSTEM_SPEC.md](./docs/PLUGIN_SYSTEM_SPEC.md)：插件类型、manifest、权限、加载生命周期和隔离边界规范。
- [docs/EXTERNAL_TOOL_INTEGRATION_SPEC.md](./docs/EXTERNAL_TOOL_INTEGRATION_SPEC.md)：第三方工具、外部 CLI/SDK、远程 provider、插件贡献 backend 与 adapter/runtime/worker 边界规划。
- [docs/UI_WORKSPACE_SPEC.md](./docs/UI_WORKSPACE_SPEC.md)：dockable workspace、浮动窗口、布局保存和 workspace preset 规范。
- [docs/I18N_SPEC.md](./docs/I18N_SPEC.md)：语言热切换、翻译 key、格式化和插件语言包规范。
- [docs/HARDWARE_SCHEDULING_SPEC.md](./docs/HARDWARE_SCHEDULING_SPEC.md)：硬件检测、资源请求、调度绑定、资源锁和 OOM 恢复规范。
- [docs/BATCH_PIPELINE_SCHEDULING_SPEC.md](./docs/BATCH_PIPELINE_SCHEDULING_SPEC.md)：批量视频按 task DAG 流水线调度、stage backlog、backpressure 和 waiting reason 规划。
- [docs/HARDWARE_SCHEDULING_PAGE_SPEC.md](./docs/HARDWARE_SCHEDULING_PAGE_SPEC.md)：Hardware Scheduling 复页的信息架构、视图分级、硬件 lanes、waiting reason 和 SchedulingPageSnapshot 规划。
- [docs/SCHEDULING_PRESETS_SPEC.md](./docs/SCHEDULING_PRESETS_SPEC.md)：调度预设、并发/backlog/device preference/fallback 策略和用户自定义 preset 规划。
- [docs/TRANSLATE_AGENT_SPEC.md](./docs/TRANSLATE_AGENT_SPEC.md)：Translate Agent 卡片、SRT/OCR 字幕翻译、ASR/OCR fusion、结构化输出、provider 抽象和 artifact contract 规划。
- [docs/FAILURE_RECOVERY_SPEC.md](./docs/FAILURE_RECOVERY_SPEC.md)：失败分类、恢复动作、partial artifacts、崩溃恢复和失败 UI 规范。
- [docs/SECURITY_PRIVACY_SPEC.md](./docs/SECURITY_PRIVACY_SPEC.md)：本地优先隐私、secrets、插件权限、更新校验和日志脱敏规范。
- [docs/WORKFLOW_NODE_SPEC.md](./docs/WORKFLOW_NODE_SPEC.md)：WorkflowGraph、节点、端口、连线、NodeRegistry 和 runtime requirements 规范。
- [docs/EXECUTION_PLAN_SPEC.md](./docs/EXECUTION_PLAN_SPEC.md)：ExecutionPlan、phase、lane、task、资源绑定、runtime binding 和状态机规范。
- [docs/WORKER_PROTOCOL.md](./docs/WORKER_PROTOCOL.md)：Worker 启动、JSON Lines 事件、artifact 交接、取消和 adapter 约束。
- [docs/ADAPTER_SPEC.md](./docs/ADAPTER_SPEC.md)：Worker Adapter 通用边界、接口、typed command builder、错误映射和内置 adapter 清单。
- [docs/FFMPEG_ADAPTER_SPEC.md](./docs/FFMPEG_ADAPTER_SPEC.md)：FFmpeg / ffprobe 相关 adapter，包括 metadata probe、audio extract、字幕 mux/burn、audio mux 和 export。
- [docs/ASR_ADAPTER_SPEC.md](./docs/ASR_ADAPTER_SPEC.md)：ASR Subtitle / `asr.whisper` adapter 输入、参数、runtime、artifact 和错误映射规划。
- [docs/OCR_ADAPTER_SPEC.md](./docs/OCR_ADAPTER_SPEC.md)：OCR Recognition / `ocr.recognition` adapter、抽帧策略、`ocr_text_track` artifact 和 ASR/Translate 关系规划。
- [docs/VIDEO_ENHANCE_ADAPTER_SPEC.md](./docs/VIDEO_ENHANCE_ADAPTER_SPEC.md)：RealESRGAN / RIFE 视频增强与插帧 adapter 规划。
- [docs/ARTIFACT_LIFECYCLE_SPEC.md](./docs/ARTIFACT_LIFECYCLE_SPEC.md)：artifact 生成、验证、缓存、复用、final output、OCR/ASR/translation sidecar 和恢复规划。
- [docs/UI_STATE_SPEC.md](./docs/UI_STATE_SPEC.md)：App/Workflow/ExecutionPlan/Task/Runtime/Artifact UI 状态机和按钮可用性规划。
- [docs/ONBOARDING_RUNTIME_SETUP_SPEC.md](./docs/ONBOARDING_RUNTIME_SETUP_SPEC.md)：首次启动 runtime 检测、隐私模式、OCR/ASR/FFmpeg/video enhance/API setup 和修复流程规划。
- [docs/DOC_ALIGNMENT_NOTES.md](./docs/DOC_ALIGNMENT_NOTES.md)：新增 OCR Recognition 后需要同步对齐的文档清单、命名和设计风险。
- [docs/DATABASE_SCHEMA.md](./docs/DATABASE_SCHEMA.md)：SQLite 首版表结构、cache、artifact、runtime components 和 model assets。
- [docs/design-md-references](./docs/design-md-references)：外部设计参考文档，只用于启发，不作为 Atelier 的事实源。
- [docs/plan](./docs/plan)：阶段性计划、调研记录和临时规划文档归档位置。

当前资源目录：

- [atelier/assets/README.md](./atelier/assets/README.md)：当前软件 SVG 图标库说明，覆盖品牌图标，以及 toolbar、navigation、nodes、queue、hardware、status、inspector 和 system 图标资源。

当前参考文件：

- [apple.DESIGN.md](./docs/design-md-references/apple.DESIGN.md)
- [linear.DESIGN.md](./docs/design-md-references/linear.DESIGN.md)
- [nvidia.DESIGN.md](./docs/design-md-references/nvidia.DESIGN.md)
- [ollama.DESIGN.md](./docs/design-md-references/ollama.DESIGN.md)
- [runwayml.DESIGN.md](./docs/design-md-references/runwayml.DESIGN.md)

未来随着项目成型，建议继续补充：

```text
UI_INTERACTION_SPEC.md
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

根目录 `DESIGN.md` 是 Atelier 的设计事实源。`docs/Atelier_Main_UI_Spec.md` 是主界面绘制规格 / concept implementation spec，用于把 `DESIGN.md` 的主 UI 原则落到可绘制规格。`docs/design-md-references/` 中的文档来自外部品牌风格参考，只能作为建设性意见源，用于借鉴局部方法：

- `linear`：工程工具的克制感、状态密度和设置组织。
- `ollama`：本地 AI、模型、runtime 和命令输出语境。
- `nvidia`：GPU、性能指标和硬件状态表达。
- `runwayml`：视频媒体氛围和创作工具感。
- `apple`：空间纪律、控件精致度和平台级克制。

不要直接复制外部品牌色、字体、官网式 hero、营销页结构或品牌语言。产品品牌名唯一事实是 `Atelier`。

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
Runtime ownership: bundled/managed application runtime, tool runtime, model store, and backend manifest
```

Rust / C++ / CUDA 可以作为未来隔离 worker 或性能热点模块，但不应成为主应用默认架构。除非明确做架构迁移，不应把项目改成 Electron、Tauri、Celery、Redis 或 web stack。

Atelier 应规划自己的 runtime 环境：软件自身的 Python / PySide6 / Qt 依赖、FFmpeg / ffprobe、llama.cpp / whisper.cpp / ncnn-vulkan 等工具 backend、以及模型资产都应由软件管理安装、校验、版本和修复。系统 GPU driver 这类硬件层依赖由 Atelier 检测并给出修复入口，但不把重型环境配置责任推给用户手工解决。

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
- `HardwareDetector`：观测 CPU、RAM、磁盘、GPU、driver、runtime capability 和 Worker 进程状态。
- `RuntimeManager`：管理应用 runtime、外部工具、backend、模型资产和 RuntimeManifest。
- `ReleaseManager`：管理发布通道、更新 manifest、staging、校验和回滚计划。
- `PluginManager`：管理插件 manifest、权限、contribution 注册和禁用状态。
- `WorkspaceManager`：管理 dock 布局、浮动面板、workspace preset 和布局持久化。
- `I18nManager`：管理语言包、当前 locale 和运行时语言切换。
- `SecurityManager`：管理 credential references、日志脱敏、权限检查和包完整性校验。
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

当前仓库处于“首版骨架启动”阶段：

- 已有项目级 Agent 指南。
- 已有根目录设计事实源。
- 已有 `atelier/assets/` 原创 SVG 线性图标库，作为当前软件 toolbar、navigation、workflow nodes、queue、hardware、status、inspector 和 system 图标资源来源。
- 已搬入外部 `DESIGN.md` 参考文件。
- 已有首版架构、runtime、发布更新、插件、workspace、i18n、硬件调度、失败恢复、安全隐私、workflow、execution、worker protocol、数据库 schema 和 Translate Agent 规划文档。
- 已开始搭建 Python 包结构、开发 `.venv`、AppPaths 路径管理、pydantic domain models、Worker JSON Lines 单事件编解码与事件流验证、`ExecutionTask -> task.json -> WorkerProcessSpec` 边界、最小 subprocess runner 边界、最小 WorkflowGraph、简单 ExecutionPlan planner、最小 queue / Scheduler claim、resource locks / failure recovery、sqlite3 schema 初始化、SQLite event/artifact 写入、RuntimeManager binding、RuntimeStore 本地 manifest 读写、RuntimeHealthChecker、package sha256 校验、simulated Worker、只读 PySide6 工作台壳、`metadata.probe` / `media.audio_extract` / `output.export` 最小 adapter workflow 和 stdlib unittest 基线。
- 已有只读 GUI 起点：PySide6 仍是 optional `gui` extra，本地开发 `.venv` 可安装 `.[gui]`；当前可用 `.venv\Scripts\python -m atelier.gui.app` 启动 `MainWindow`，只展示 workflow / execution / queue / resources-runtime 四个 dockable 区域、Queue snapshot 和最小 workspace layout 保存/恢复，不执行任务。
- 尚未实现真实编辑型 GUI、生产级 Scheduler、完整生产级 worker lifecycle runner、完整 FFmpeg/model adapters、SQLAlchemy repository、打包发布链或插件加载链。

下一步适合继续沿 adapter 链补 subtitle mux/burn、ASR/OCR/Translate Agent 前置 adapter 规划，或在 GUI 侧接入只触发后端 queue 的最小工作流运行入口。

开发期启动只读工作台：

```powershell
.venv\Scripts\python -m atelier.gui.app
```

## 验证策略

项目成型后建议基线：

```powershell
python -m unittest discover -s tests
python -m pytest
python -m ruff check .
python -m mypy .
```

如果这些工具尚未配置，不要声称验证通过。当前首版骨架可先使用 stdlib `unittest`，等开发依赖配置完成后再启用 `pytest` / `ruff` / `mypy`。文档与骨架阶段的验证重点是：

- 项目名统一为 `Atelier`。
- `README.md`、`AGENTS.md`、`DESIGN.md` 职责分清。
- 根目录 `DESIGN.md`、`docs/Atelier_Main_UI_Spec.md` 与 `docs/design-md-references/` 的关系明确。
- 没有把尚未实现的功能写成已完成状态。

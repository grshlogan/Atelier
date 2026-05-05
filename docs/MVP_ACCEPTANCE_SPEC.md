# Atelier MVP Acceptance Spec

> 状态：规划中，尚未实现。本文档定义 Atelier 首版 MVP 的验收标准。`PRODUCT_FLOW_SPEC.md` 描述路径；本文描述“怎样算通过”。

## 1. MVP 目标

首版必须证明：

```text
导入一批视频
  -> 使用内置 Workflow
  -> 跑通 ASR + OCR + Agent 翻译 + 封装 + 导出
  -> 展示硬件调度解释
  -> 失败可恢复/降级
  -> 重启后历史与产物可追踪
```

## 2. 必验卡片

```text
Video Input
Metadata Probe
Audio Extract
ASR Subtitle
OCR Recognition
Subtitle Normalize
Translate Agent
Soft Subtitle Mux
Output Export
```

建议同时验收：

```text
Audio Enhance
Subtitle Review
Video Enhance
Frame Interpolation
Burn Subtitle
```

## 3. 验收总表

| Area | 必须通过 |
|---|---|
| Project | 创建、打开、保存、最近项目 |
| Import | 单视频、多视频、损坏视频、无音轨视频 |
| Workflow | 预设生成、卡片验证、参数编辑 |
| OCR | 抽帧、识别、生成 text track、与 ASR 融合 |
| ExecutionPlan | per-video DAG、跨视频 pipeline、依赖正确 |
| Scheduler | task claim、ResourceBinding、waiting reason、backpressure |
| Worker | started/progress/heartbeat/artifact/completed/failed |
| Artifact | staged、partial、valid、final_output、cache_hit |
| Failure | OOM、TIMEOUT、CANCELLED、RUNTIME_MISSING、INPUT_CORRUPT、DISK_FULL |
| UI | 空状态、加载、运行、失败、恢复、runtime missing |
| Persistence | 重启恢复 job/task/event/artifact/resource lock |

## 4. Demo Dataset

```text
V01_dialogue_with_embedded_text.mp4
  有清晰语音，有画面文字

V02_hardsub_foreign_language.mp4
  有硬字幕，ASR 与 OCR 可互补

V03_no_audio_ui_text.mp4
  无音频或弱音频，主要依赖 OCR

V04_corrupt.mp4
  用于 INPUT_CORRUPT

V05_long_video.mp4
  用于 heartbeat / timeout / backpressure
```

## 5. 主流程用例

### A-01 创建项目

通过：项目记录存在，默认 workspace 打开，没有 runtime 时也能进入项目，secrets 不进入项目文件。

### A-02 批量导入视频

通过：每个视频显示 duration/resolution/audio stream；无音频视频显示 ASR warning，但 OCR 支路可用；Metadata artifact 写入。

### A-03 ASR + OCR Translation Preset

通过：Workflow 包含 ASR 与 OCR 两条识别支路；Translate Agent 至少依赖一路识别输入；每个视频展开 per-media DAG。

### A-04 批量流水线调度

通过：V01 Translate 慢时，V02/V03 的 ASR/OCR 可继续；Translate backlog 满时，新 ASR/OCR 可被 `paused_by_backpressure`；Hardware Scheduling Page 显示瓶颈。

### A-05 ASR + OCR 融合翻译

通过：Translate Agent 输入包含 ASR timed segments 和 OCR text track；输出 subtitle artifact；metadata 记录 `used_asr=true`、`used_ocr=true`、`translation_source=asr_ocr_fusion`。

### A-06 OCR 降级

通过：OCR failed 时 ASR-only 可继续；UI 显示“视觉文字未参与翻译”；不影响 ASR-only 下游输出。

### A-07 ASR 失败但 OCR 成功

通过：Translate Agent 可生成 OCR-only draft；输出标记 incomplete；用户需确认继续导出。

### A-08 最终导出

通过：Worker 只写 staged artifact；ArtifactFinalizer 写最终路径；不静默覆盖；final_output link 记录。

## 6. Failure Acceptance

| Failure | 通过标准 |
|---|---|
| OOM | failed event、lock release、无同参数同 GPU 静默重试 |
| TIMEOUT | terminate/kill、failed(TIMEOUT)、stderr kept |
| CANCELLED | state cancelled、无普通 retry |
| RUNTIME_MISSING | task blocked、repair entry |
| INPUT_CORRUPT | failed、下游影响可见 |
| DISK_FULL | failed、partial cleanup |
| INTERRUPTED | startup recovery 标记 interrupted 并处理 stale locks |

## 7. Release Gate

阻塞发布的问题：

```text
Worker 可绕过 Scheduler 直接写 DB
Adapter 使用 shell=True
Secrets 写入日志/SQLite
最终导出静默覆盖用户文件
OOM 后同参数同 GPU 自动无限重试
CANCELLED 进入普通 retry
App 崩溃后 resource lock 永久残留
OCR 加入后 Translate Agent 依赖关系不清
```

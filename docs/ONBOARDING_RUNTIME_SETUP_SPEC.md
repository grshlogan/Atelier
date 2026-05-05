# Atelier Onboarding Runtime Setup Spec

> 状态：规划中，尚未实现。本文档定义首次启动、数据目录、Runtime 检查、模型导入、OCR/ASR/FFmpeg/Video Enhance runtime 修复路径，以及 Local Only 默认隐私模式。

## 1. Onboarding 流程

```text
First Launch
  -> Choose language
  -> Choose AtelierData location
  -> Privacy Mode
  -> Runtime Scan
  -> Recommended Setup
  -> Create/Open Project
```

## 2. Privacy Mode

默认：`Local Only`。

```text
Local Only: no remote API, no telemetry, local ASR/OCR/FFmpeg only
Balanced: update/download after confirmation
Connected: remote LLM/API providers allowed when configured
```

## 3. Runtime Scan

检查：

```text
ffmpeg
ffprobe
ASR backend/model
OCR backend/model/language pack
LLM translate backend or credential
RealESRGAN
RIFE
CUDA/Vulkan/CPU backend
```

状态：ready、missing、broken、incompatible、optional、disabled。

## 4. Recommended Setup Profiles

```text
Subtitle Basic:
  ffmpeg, ffprobe, ASR backend/model, LLM translate

ASR + OCR Translation:
  ffmpeg, ffprobe, ASR, OCR, LLM translate

Full Video Pipeline:
  ffmpeg, ffprobe, ASR, OCR, LLM, RealESRGAN, RIFE
```

## 5. OCR Setup

用户选择：

```text
Backend: PaddleOCR / Tesseract
Languages: zh / ja / en / ko / custom
Model profile: mobile-fast / server-accurate
```

规则：

- OCR 是 optional。
- OCR 缺失不阻止 ASR-only workflow。
- ASR + OCR preset 中 OCR 缺失会显示 blocking warning，用户可安装、禁用 OCR 或继续 ASR-only。
- OCR model/language pack 归 Model Store 管理。

## 6. ASR Setup

```text
Backend: faster-whisper / whisper.cpp
Model: tiny/base/small/medium/large or model_id
Device: auto / GPU / CPU
```

Workflow 引用 model_id，不引用绝对路径。

## 7. FFmpeg Setup

优先 managed runtime；系统 PATH 仅作诊断，不作产品事实源。记录 ffmpeg/ffprobe version。

## 8. Video Enhance Setup

RealESRGAN/RIFE 是 optional heavy runtime。Full Pipeline preset 中缺失时提示安装/跳过视频增强。

## 9. Remote API Setup

远程 Translate Agent 需要 provider、credential_ref、rate/concurrency defaults、隐私说明。Secrets 存 OS credential storage，SQLite 只保存 credential_ref。

## 10. Repair Flow

```text
OCR missing -> Install OCR / Disable OCR / Continue ASR-only
ASR missing -> Install ASR model / Switch backend / OCR-only draft if allowed
FFmpeg missing -> Import managed runtime
Video enhance missing -> Skip enhance or install runtime
```

## 11. Acceptance

```text
first launch no crash
skip optional OCR
install/import OCR model
ASR + OCR preset detects OCR missing
continue ASR-only path works
remote API requires credential confirmation
Local Only prevents remote Translate
runtime repair updates UI state
```

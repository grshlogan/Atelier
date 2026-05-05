# Atelier FFmpeg Adapter Spec

> 状态：部分实现。当前已落地 `metadata.probe` / `FFprobeMetadataAdapter`，通过 `RuntimeBinding.component_paths["ffprobe"]` 调用 ffprobe 并输出 `probe.json` metadata artifact。Audio Extract、Soft Subtitle Mux、Burn Subtitle、Output Export，以及 OCR/Video Enhance 所需 helper 仍处于规划中。

## 1. 覆盖 node_type

```text
metadata.probe
media.audio_extract
compose.mux_subtitle
compose.burn_subtitle
compose.mux_audio
output.export
```

内部 helper：

```text
media.frame_extract_for_ocr
media.frame_extract_for_enhance
media.frame_encode
```

## 2. RuntimeBinding

Required components：

```text
ffmpeg
ffprobe
```

Adapter 必须从 `runtime_binding.component_paths` 读取路径，禁止依赖系统 PATH。

## 3. MetadataProbeAdapter

Command intent：

```text
ffprobe -v error -print_format json -show_format -show_streams input
```

输出：

```text
artifact_type: metadata
file: probe.json
metadata:
  duration_sec
  format_name
  video_streams
  audio_streams
  subtitle_streams
  codec
  resolution
  fps
```

## 4. AudioExtractAdapter

输入：`video artifact`

输出：

```text
audio artifact
metadata:
  duration_sec
  sample_rate
  channels
  codec
```

命令意图：

```text
ffmpeg -i input -vn audio.wav
```

无音轨时按 workflow policy failed/skip。

## 5. Frame Extract for OCR

OCR 抽帧建议由 OCR Adapter 调用 FFmpeg helper，而不是暴露为用户卡片。

策略：

```text
subtitle_region
scene_change
fixed_interval
keyframes
```

限制：

```text
max_frames
max_intermediate_bytes
max_ocr_runtime_minutes
```

## 6. Soft Subtitle Mux

输入：

```text
video artifact
subtitle artifact
optional audio artifact
```

输出：

```text
video artifact
metadata.subtitle_mode = soft
```

规则：优先 stream copy，不静默丢弃音轨/字幕轨，容器兼容性必须验证。

## 7. Burn Subtitle

输入：`video + subtitle + optional font/style`

输出：`video artifact`，metadata 记录 `subtitle_mode=burned`、codec、font_profile。

规则：Burn 通常需要重编码，可能是 CPU/GPU-heavy；缺字体必须 warning。

## 8. Output Export

Worker 不直接写用户最终目录。最终导出由 ArtifactFinalizer：

```text
valid staged artifact -> conflict check -> copy/move -> final_output link
```

## 9. Progress

FFmpeg progress 可用受控 progress pipe 或 wrapper 解析，但 GUI 只信任 WorkerEvent。

## 10. 测试要求

```text
ffprobe json parse
audio extract no audio
mux subtitle format compatibility
burn subtitle missing font
command builder no shell=True
unicode path
input corrupt
disk full
cancel long transcode
```

## 11. 参考资料

- FFmpeg Documentation: https://www.ffmpeg.org/documentation.html
- ffmpeg Documentation: https://ffmpeg.org/ffmpeg.html
- ffprobe Documentation: https://ffmpeg.org/ffprobe.html

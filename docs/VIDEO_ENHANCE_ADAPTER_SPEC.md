# Atelier Video Enhance Adapter Spec

> 状态：规划中，尚未实现。本文档定义视频增强相关 Adapter：RealESRGAN 与 RIFE。它们通常是 GPU-heavy、disk-heavy、容易 OOM 的阶段，必须与资源估算、批量调度和 artifact 生命周期对齐。

## 1. 覆盖卡片

```text
Video Enhance
Frame Interpolation
```

node_type：

```text
enhance.realesrgan
enhance.rife
```

## 2. 共同流程

```text
video artifact
  -> decode frames
  -> process frames
  -> encode frames
  -> merge audio/subtitle if needed
```

中间 artifact：`image_seq`。

规则：

```text
image_seq 可能非常大，必须受 retention/backpressure 控制
失败时可保留 partial image_seq
中间帧不默认暴露给普通用户
```

## 3. RealESRGANAdapter

参数：

```python
class RealESRGANParams(BaseModel):
    model_id: str
    scale: int = 2
    tile_size: int | None = None
    face_enhance: bool = False
    fp32: bool = False
    output_format: Literal['png','jpg','webp'] = 'png'
    preserve_audio: bool = True
```

输出 metadata：

```text
scale
model_id
tile_size
backend
frame_count
output_resolution
```

OOM 降级：

```text
reduce tile_size
switch smaller model
switch device
disable face_enhance
lower scale
```

## 4. RIFEAdapter

参数：

```python
class RIFEParams(BaseModel):
    model_id: str = 'rife-v4.6'
    interpolation_factor: int = 2
    uhd_mode: bool = False
    tta_spatial: bool = False
    tta_temporal: bool = False
    output_fps: float | None = None
    thread_config: str | None = None
```

输出 metadata：

```text
interpolation_factor
input_fps
output_fps
model_id
frame_count
```

降级：

```text
disable tta
disable uhd
lower interpolation factor
switch device
split into chunks
```

## 5. 与 OCR 的关系

OCR 也抽帧，但默认不复用视频增强的全量 image_seq。

```text
OCR: lightweight sampled frames
Video Enhance/RIFE: full frame sequence
```

除非时间码、分辨率、cache key 和 artifact role 全部可验证，否则不要共享中间帧。

## 6. 错误映射

```text
INPUT_CORRUPT
MODEL_MISSING
RUNTIME_MISSING
OOM
DISK_FULL
TIMEOUT
CANCELLED
INTERNAL
```

## 7. 测试要求

```text
small video enhance
large resolution tile downshift
RIFE frame count
disk full simulation
OOM mapping
partial image_seq
cancel during process
resource_binding respected
debug frame cache cleanup
```

## 8. 参考资料

- Real-ESRGAN: https://github.com/xinntao/Real-ESRGAN
- RIFE ncnn Vulkan: https://github.com/nihui/rife-ncnn-vulkan
- FFmpeg Documentation: https://www.ffmpeg.org/documentation.html

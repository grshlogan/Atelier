from __future__ import annotations

from atelier.adapters.finalize import ArtifactFinalizerAdapter
from atelier.adapters.ffmpeg import FFmpegAudioExtractAdapter
from atelier.adapters.ffprobe import FFprobeMetadataAdapter
from atelier.adapters.registry import AdapterRegistry


def create_builtin_adapter_registry() -> AdapterRegistry:
    registry = AdapterRegistry()
    registry.register(FFprobeMetadataAdapter())
    registry.register(FFmpegAudioExtractAdapter())
    registry.register(ArtifactFinalizerAdapter())
    return registry

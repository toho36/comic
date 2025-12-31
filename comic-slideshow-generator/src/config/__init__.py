"""Configuration module for Comic Slideshow Generator"""
from .settings import (
    AppConfig,
    DetectionConfig,
    OCRConfig,
    TTSConfig,
    VideoConfig,
    load_config,
    get_default_config
)

__all__ = [
    "AppConfig",
    "DetectionConfig",
    "OCRConfig",
    "TTSConfig",
    "VideoConfig",
    "load_config",
    "get_default_config"
]

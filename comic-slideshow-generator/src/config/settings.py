"""
Configuration system for Comic Slideshow Generator
Uses Pydantic for validation and settings management
"""
from typing import List, Optional
from pathlib import Path
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class DetectionConfig(BaseModel):
    """Configuration for speech bubble detection"""
    min_bubble_area: int = Field(default=500, description="Minimum bubble area in pixels")
    blur_kernel: int = Field(default=5, description="Gaussian blur kernel size (must be odd)")
    threshold_block_size: int = Field(default=11, description="Adaptive threshold block size (must be odd)")
    morph_close_kernel: int = Field(default=3, description="Morphological close kernel size")
    min_aspect_ratio: float = Field(default=0.5, ge=0.1, le=10.0, description="Minimum width/height ratio")
    max_aspect_ratio: float = Field(default=3.0, ge=0.1, le=10.0, description="Maximum width/height ratio")
    
    def validate_params(self):
        """Validate OpenCV-specific constraints"""
        if self.blur_kernel % 2 == 0:
            raise ValueError(f"blur_kernel must be odd, got {self.blur_kernel}")
        if self.threshold_block_size % 2 == 0:
            raise ValueError(f"threshold_block_size must be odd, got {self.threshold_block_size}")


class OCRConfig(BaseModel):
    """Configuration for OCR text extraction"""
    engine: str = Field(default="tesseract", description="OCR engine to use")
    languages: List[str] = Field(default_factory=lambda: ["ces", "eng"], description="OCR languages (ISO 639-2 codes)")
    oem: int = Field(default=3, ge=0, le=3, description="Tesseract OEM mode (0-3)")
    psm: int = Field(default=7, ge=0, le=13, description="Tesseract PSM mode (0-13)")
    min_confidence: float = Field(default=0.6, ge=0.0, le=1.0, description="Minimum text confidence threshold")
    
    def get_tesseract_config(self) -> str:
        """Generate Tesseract configuration string"""
        return f'--oem {self.oem} --psm {self.psm}'
    
    def get_language_string(self) -> str:
        """Generate language string for Tesseract"""
        return '+'.join(self.languages)


class TTSConfig(BaseModel):
    """Configuration for text-to-speech synthesis"""
    provider: str = Field(default="edge", description="TTS provider: 'edge' or 'openai'")
    voice: str = Field(default="en-US-AriaNeural", description="Voice identifier")
    rate: str = Field(default="+0%", description="Speech rate adjustment")
    volume: str = Field(default="+0%", description="Volume adjustment")
    api_key: Optional[str] = Field(default=None, description="API key for OpenAI TTS")
    
    def is_openai(self) -> bool:
        """Check if using OpenAI provider"""
        return self.provider.lower() == "openai"
    
    def validate_api_key(self):
        """Validate that API key is present when using OpenAI"""
        if self.is_openai() and not self.api_key:
            raise ValueError("OpenAI API key is required when provider is 'openai'")


class VideoConfig(BaseModel):
    """Configuration for video generation"""
    fps: int = Field(default=24, ge=1, le=60, description="Output video frames per second")
    bubble_zoom_duration: float = Field(default=1.0, ge=0.1, description="Duration of bubble zoom animation (seconds)")
    transition_duration: float = Field(default=0.5, ge=0.0, description="Duration of transitions (seconds)")
    output_codec: str = Field(default="libx264", description="Video codec")
    audio_bitrate: str = Field(default="192k", description="Audio bitrate")
    crf_quality: int = Field(default=23, ge=0, le=51, description="Constant Rate Factor quality (lower=better)")
    
    def calculate_transition_frames(self) -> int:
        """Calculate number of frames for transitions"""
        return int(self.transition_duration * self.fps)


class AppConfig(BaseSettings):
    """Main application configuration"""
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        env_prefix="",
        case_sensitive=False,
        arbitrary_types_allowed=True
    )
    
    # Sub-configurations
    detection: DetectionConfig = Field(default_factory=DetectionConfig)
    ocr: OCRConfig = Field(default_factory=OCRConfig)
    tts: TTSConfig = Field(default_factory=TTSConfig)
    video: VideoConfig = Field(default_factory=VideoConfig)
    
    # Other settings
    temp_dir: Path = Field(default=Path("temp"), description="Temporary files directory")
    output_dir: Path = Field(default=Path("output"), description="Output files directory")
    log_level: str = Field(default="INFO", description="Logging level")
    max_file_size_mb: int = Field(default=100, ge=1, description="Maximum input file size in MB")
    
    @classmethod
    def from_env(cls, env_file: str = ".env") -> "AppConfig":
        """Load configuration from .env file"""
        return cls(_env_file=env_file)
    
    def save_to_yaml(self, path: Path):
        """Save configuration to YAML file"""
        import yaml
        
        data = {
            "detection": self.detection.model_dump(),
            "ocr": self.ocr.model_dump(),
            "tts": self.tts.model_dump(),
            "video": self.video.model_dump(),
            "temp_dir": str(self.temp_dir),
            "output_dir": str(self.output_dir),
            "log_level": self.log_level,
            "max_file_size_mb": self.max_file_size_mb
        }
        
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, 'w') as f:
            yaml.dump(data, f, default_flow_style=False)
    
    @classmethod
    def from_yaml(cls, path: Path) -> "AppConfig":
        """Load configuration from YAML file"""
        import yaml
        
        with open(path) as f:
            data = yaml.safe_load(f)
        
        return cls(
            detection=DetectionConfig(**data.get("detection", {})),
            ocr=OCRConfig(**data.get("ocr", {})),
            tts=TTSConfig(**data.get("tts", {})),
            video=VideoConfig(**data.get("video", {})),
            temp_dir=Path(data.get("temp_dir", "temp")),
            output_dir=Path(data.get("output_dir", "output")),
            log_level=data.get("log_level", "INFO"),
            max_file_size_mb=data.get("max_file_size_mb", 100)
        )
    
    def ensure_directories(self):
        """Create necessary directories if they don't exist"""
        self.temp_dir.mkdir(parents=True, exist_ok=True)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def validate_all(self):
        """Validate all configuration sections"""
        self.detection.validate_params()
        self.tts.validate_api_key()


# Convenience functions for getting configuration
def load_config(config_path: Optional[Path] = None) -> AppConfig:
    """
    Load configuration from file or environment
    
    Args:
        config_path: Optional path to YAML configuration file
    
    Returns:
        AppConfig instance
    """
    if config_path and config_path.exists():
        return AppConfig.from_yaml(config_path)
    return AppConfig.from_env()


def get_default_config() -> AppConfig:
    """Get default configuration"""
    return AppConfig()

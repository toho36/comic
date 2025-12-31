"""
Text-to-speech engine factory
Creates appropriate TTS engine based on configuration
"""
from typing import Optional
from .edge_tts import EdgeTTSEngine
from .openai_tts import OpenAITTSEngine
from src.config import TTSConfig


def create_tts_engine(config: Optional[TTSConfig] = None):
    """
    Factory function to create TTS engine based on configuration
    
    Args:
        config: TTS configuration
    
    Returns:
        TTS engine instance (EdgeTTSEngine or OpenAITTSEngine)
    
    Raises:
        ValueError: If provider is not supported
    
    Examples:
        >>> from src.config import TTSConfig
        >>> config = TTSConfig(provider="edge")
        >>> engine = create_tts_engine(config)
        >>> await engine.text_to_speech("Hello", "output.mp3")
    """
    config = config or TTSConfig()
    
    provider = config.provider.lower()
    
    if provider == "edge":
        return EdgeTTSEngine(config)
    elif provider == "openai":
        return OpenAITTSEngine(config)
    else:
        raise ValueError(
            f"Unsupported TTS provider: {config.provider}. "
            f"Supported providers: 'edge', 'openai'"
        )


__all__ = [
    "create_tts_engine",
    "EdgeTTSEngine",
    "OpenAITTSEngine"
]

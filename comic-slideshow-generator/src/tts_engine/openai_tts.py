"""
Text-to-speech engine using OpenAI API
High-quality TTS with multiple voice options
"""
import asyncio
from pathlib import Path
from typing import Optional
from openai import AsyncOpenAI
from src.config import TTSConfig


class OpenAITTSEngine:
    """Text-to-speech engine using OpenAI API"""
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """
        Initialize OpenAI TTS engine
        
        Args:
            config: TTS configuration
        
        Raises:
            ValueError: If API key is not provided
        """
        self.config = config or TTSConfig()
        
        # Validate provider
        if self.config.provider != "openai":
            raise ValueError(f"OpenAITTSEngine requires provider='openai', got '{self.config.provider}'")
        
        # Validate API key
        if not self.config.api_key:
            raise ValueError("OpenAI API key is required. Set TTS_API_KEY or tts.api_key in config.")
        
        # Initialize async client
        self.client = AsyncOpenAI(api_key=self.config.api_key)
    
    async def text_to_speech(
        self,
        text: str,
        output_path: str,
        model: str = "tts-1",
        voice: Optional[str] = None
    ) -> float:
        """
        Convert text to speech using OpenAI TTS
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            model: TTS model ("tts-1" or "tts-1-hd")
            voice: Optional voice override (uses config if not provided)
        
        Returns:
            Duration of audio in seconds
        
        Raises:
            RuntimeError: If TTS generation fails
            ValueError: If text is empty or too long
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        # Check text length limit (OpenAI limit: ~4096 characters)
        if len(text) > 4000:
            raise ValueError("Text is too long. Maximum is ~4000 characters.")
        
        voice = voice or self._map_config_voice_to_openai()
        
        try:
            # Create speech
            response = await self.client.audio.speech.create(
                model=model,
                voice=voice,
                input=text
            )
            
            # Save to file
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            response.stream_to_file(output_file)
            
            # Get duration
            duration = self._get_audio_duration(output_path)
            
            return duration
            
        except Exception as e:
            raise RuntimeError(f"OpenAI TTS generation failed: {str(e)}")
    
    async def text_to_speech_stream(
        self,
        text: str,
        model: str = "tts-1",
        voice: Optional[str] = None
    ) -> bytes:
        """
        Generate speech as bytes stream
        
        Args:
            text: Text to synthesize
            model: TTS model
            voice: Optional voice override
        
        Returns:
            Audio data as bytes
        """
        voice = voice or self._map_config_voice_to_openai()
        
        response = await self.client.audio.speech.create(
            model=model,
            voice=voice,
            input=text
        )
        
        # Get content as bytes
        return response.content
    
    def _map_config_voice_to_openai(self) -> str:
        """
        Map config voice to OpenAI voice name
        
        Returns:
            OpenAI voice name
        """
        # OpenAI supports: alloy, echo, fable, onyx, nova, shimmer
        voice_mapping = {
            "alloy": "alloy",
            "echo": "echo",
            "fable": "fable",
            "onyx": "onyx",
            "nova": "nova",
            "shimmer": "shimmer",
        }
        
        config_voice = self.config.voice.lower()
        
        # Direct match
        if config_voice in voice_mapping:
            return voice_mapping[config_voice]
        
        # Map Edge voices to OpenAI voices
        if "aria" in config_voice or "female" in config_voice:
            return "nova"  # Female voice
        elif "guy" in config_voice or "male" in config_voice:
            return "onyx"  # Male voice
        
        # Default
        return "alloy"
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """
        Get duration of audio file
        
        Args:
            audio_path: Path to audio file
        
        Returns:
            Duration in seconds
        """
        try:
            import librosa
            y, sr = librosa.load(audio_path)
            duration = librosa.get_duration(y=y, sr=sr)
            return duration
        except ImportError:
            # Fallback: estimate based on text length and average speech rate
            words = len(audio_path.split())
            estimated_duration = (words / 150) * 60
            return estimated_duration
    
    @staticmethod
    def get_available_models() -> list[str]:
        """
        Get list of available OpenAI TTS models
        
        Returns:
            List of model names
        """
        return ["tts-1", "tts-1-hd"]
    
    @staticmethod
    def get_available_voices() -> list[str]:
        """
        Get list of available OpenAI TTS voices
        
        Returns:
            List of voice names
        """
        return ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
    
    @staticmethod
    def estimate_cost(text: str, model: str = "tts-1") -> float:
        """
        Estimate cost for TTS generation
        
        Args:
            text: Text to synthesize
            model: TTS model
        
        Returns:
            Estimated cost in USD
        """
        # OpenAI pricing (as of 2024):
        # tts-1: $15 / 1M characters
        # tts-1-hd: $30 / 1M characters
        
        price_per_million = 15 if model == "tts-1" else 30
        cost = (len(text) / 1_000_000) * price_per_million
        return round(cost, 6)

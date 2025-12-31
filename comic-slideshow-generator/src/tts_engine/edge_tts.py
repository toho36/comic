"""
Text-to-speech engine using edge-tts (Microsoft Edge)
Free TTS service with multiple voices and languages
"""
import edge_tts
import asyncio
import numpy as np
from pathlib import Path
from typing import Optional
from src.config import TTSConfig


class EdgeTTSEngine:
    """Text-to-speech engine using Microsoft Edge TTS"""
    
    def __init__(self, config: Optional[TTSConfig] = None):
        """
        Initialize Edge TTS engine
        
        Args:
            config: TTS configuration
        """
        self.config = config or TTSConfig()
        
        # Validate provider
        if self.config.provider != "edge":
            raise ValueError(f"EdgeTTSEngine requires provider='edge', got '{self.config.provider}'")
    
    async def text_to_speech(
        self,
        text: str,
        output_path: str,
        voice: Optional[str] = None
    ) -> float:
        """
        Convert text to speech using edge-tts
        
        Args:
            text: Text to synthesize
            output_path: Path to save audio file
            voice: Optional voice override (uses config if not provided)
        
        Returns:
            Duration of audio in seconds
        
        Raises:
            RuntimeError: If TTS generation fails
        """
        if not text or not text.strip():
            raise ValueError("Text cannot be empty")
        
        voice = voice or self.config.voice
        
        try:
            # Create communicate object
            communicate = edge_tts.Communicate(
                text=text,
                voice=voice,
                rate=self.config.rate,
                volume=self.config.volume
            )
            
            # Save audio to file
            await communicate.save(output_path)
            
            # Get duration
            duration = self._get_audio_duration(output_path)
            
            return duration
            
        except Exception as e:
            raise RuntimeError(f"Edge TTS generation failed: {str(e)}")
    
    async def text_to_speech_stream(
        self,
        text: str,
        voice: Optional[str] = None
    ) -> bytes:
        """
        Generate speech as bytes stream
        
        Args:
            text: Text to synthesize
            voice: Optional voice override
        
        Returns:
            Audio data as bytes
        """
        voice = voice or self.config.voice
        
        communicate = edge_tts.Communicate(
            text=text,
            voice=voice,
            rate=self.config.rate,
            volume=self.config.volume
        )
        
        # Collect all chunks
        audio_data = b""
        async for chunk in communicate.stream():
            if chunk["type"] == "audio":
                audio_data += chunk["data"]
        
        return audio_data
    
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
            # Average speech rate: ~150 words per minute
            words = len(audio_path.split())
            estimated_duration = (words / 150) * 60
            return estimated_duration
    
    @staticmethod
    async def list_voices() -> list[dict]:
        """
        List all available Edge TTS voices
        
        Returns:
            List of voice information dictionaries
        """
        return await edge_tts.list_voices()
    
    @staticmethod
    def find_voices(language: str = "en", gender: str = "Female") -> list[str]:
        """
        Find voices matching criteria
        
        Args:
            language: Language code (e.g., "en", "cs")
            gender: "Male" or "Female"
        
        Returns:
            List of voice names
        """
        # This is a synchronous wrapper
        async def _find():
            all_voices = await EdgeTTSEngine.list_voices()
            matching = []
            for voice in all_voices:
                if voice.get("Locale", "").startswith(language):
                    if voice.get("Gender", "") == gender:
                        matching.append(voice.get("Name", ""))
            return matching
        
        return asyncio.run(_find())
    
    @staticmethod
    def get_recommended_voices() -> dict[str, str]:
        """
        Get recommended voices for common languages
        
        Returns:
            Dictionary mapping language codes to voice names
        """
        return {
            "en": "en-US-AriaNeural",      # English (US) - Female
            "en-male": "en-US-GuyNeural",  # English (US) - Male
            "cs": "cs-CZ-VlastaNeural",    # Czech - Female
            "de": "de-DE-KatjaNeural",     # German - Female
            "es": "es-ES-ElviraNeural",    # Spanish - Female
            "fr": "fr-FR-DeniseNeural",    # French - Female
            "it": "it-IT-ElsaNeural",      # Italian - Female
            "pl": "pl-PL-ZofiaNeural",     # Polish - Female
        }

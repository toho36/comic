"""
Video composition using moviepy
Generates final slideshow videos from processed comic data
"""
import numpy as np
from pathlib import Path
from typing import List, Tuple, Optional
from moviepy import VideoClip, ImageClip, AudioFileClip, CompositeVideoClip, concatenate_videoclips


from src.config import VideoConfig
from src.processor.models import Timeline, TimelineSegment, AudioSegment


class VideoCompositor:
    """Composes slideshow videos from comic pages and audio"""
    
    def __init__(self, config: Optional[VideoConfig] = None):
        """
        Initialize video compositor
        
        Args:
            config: Video configuration
        """
        self.config = config or VideoConfig()
    
    def compose_video(
        self,
        pages: List[np.ndarray],
        timeline: Timeline,
        audio_segments: List[AudioSegment],
        output_path: Path
    ) -> Path:
        """
        Compose final video from timeline
        
        Args:
            pages: List of page images
            timeline: Video timeline
            audio_segments: Audio segments
            output_path: Output video path
        
        Returns:
            Path to generated video
        
        Raises:
            RuntimeError: If video composition fails
        """
        if not timeline.segments:
            raise ValueError("Timeline has no segments")
        
        try:
            # Create clips for each timeline segment
            clips = []
            
            for segment in timeline.segments:
                clip = self._create_segment_clip(
                    pages[segment.page_idx],
                    segment
                )
                clips.append(clip)
            
            # Concatenate all clips
            final_video = concatenate_videoclips(clips, method="compose")
            
            # Add audio track
            audio = self._create_audio_track(audio_segments, timeline.total_duration)
            final_video = final_video.set_audio(audio)
            
            # Write video file
            output_path = Path(output_path)
            output_path.parent.mkdir(parents=True, exist_ok=True)
            
            final_video.write_videofile(
                str(output_path),
                fps=self.config.fps,
                codec=self.config.output_codec,
                audio_bitrate=self.config.audio_bitrate,
                preset='medium',
                ffmpeg_params=['-crf', str(self.config.crf_quality)]
            )
            
            # Clean up
            for clip in clips:
                clip.close()
            final_video.close()
            audio.close()
            
            return output_path
            
        except Exception as e:
            raise RuntimeError(f"Video composition failed: {str(e)}")
    
    def _create_segment_clip(
        self,
        page_image: np.ndarray,
        segment: TimelineSegment
    ) -> VideoClip:
        """
        Create a video clip for a timeline segment
        
        Args:
            page_image: Full page image
            segment: Timeline segment
        
        Returns:
            VideoClip for this segment
        """
        # Get bubble bounding box
        x, y, w, h = segment.bubble.bbox
        page_height, page_width = page_image.shape[:2]
        
        # Calculate zoom parameters
        zoom_factor = self._calculate_zoom_factor(
            (w, h),
            (page_width, page_height)
        )
        
        # Create zoom animation
        def make_frame(t):
            """Generate frame at time t"""
            # Calculate current zoom level
            progress = t / segment.duration
            current_zoom = 1.0 + (zoom_factor - 1.0) * self._ease_in_out(progress)
            
            # Calculate crop size
            crop_w = int(page_width / current_zoom)
            crop_h = int(page_height / current_zoom)
            
            # Center on bubble
            crop_x1 = max(0, x + w // 2 - crop_w // 2)
            crop_y1 = max(0, y + h // 2 - crop_h // 2)
            crop_x2 = min(page_width, crop_x1 + crop_w)
            crop_y2 = min(page_height, crop_y1 + crop_h)
            
            # Adjust if out of bounds
            if crop_x2 - crop_x1 < crop_w:
                if crop_x1 == 0:
                    crop_x2 = min(page_width, crop_w)
                else:
                    crop_x1 = max(0, page_width - crop_w)
            
            if crop_y2 - crop_y1 < crop_h:
                if crop_y1 == 0:
                    crop_y2 = min(page_height, crop_h)
                else:
                    crop_y1 = max(0, page_height - crop_h)
            
            # Crop and resize
            cropped = page_image[crop_y1:crop_y2, crop_x1:crop_x2]
            resized = np.array(
                Image.fromarray(cropped).resize(
                    (page_width, page_height),
                    Image.LANCZOS
                )
            )
            
            return resized
        
        # Create clip
        clip = VideoClip(
            make_frame,
            duration=segment.duration
        )
        
        return clip
    
    def _calculate_zoom_factor(
        self,
        bubble_size: Tuple[int, int],
        page_size: Tuple[int, int]
    ) -> float:
        """
        Calculate zoom factor to highlight bubble
        
        Args:
            bubble_size: Bubble (width, height)
            page_size: Page (width, height)
        
        Returns:
            Zoom factor (1.0 = no zoom, >1.0 = zoom in)
        """
        bubble_w, bubble_h = bubble_size
        page_w, page_h = page_size
        
        # Target: bubble should occupy ~60% of frame
        target_ratio = 0.6
        
        # Calculate required zoom
        zoom_w = (bubble_w / page_w) / target_ratio
        zoom_h = (bubble_h / page_h) / target_ratio
        
        # Use larger zoom to fit bubble
        zoom_factor = max(zoom_w, zoom_h)
        
        # Limit maximum zoom
        return min(zoom_factor, 3.0)
    
    def _ease_in_out(self, t: float) -> float:
        """
        Ease-in-out easing function
        
        Args:
            t: Progress (0-1)
        
        Returns:
            Eased value
        """
        return t * t * (3 - 2 * t)
    
    def _create_audio_track(
        self,
        audio_segments: List[AudioSegment],
        total_duration: float
    ) -> AudioFileClip:
        """
        Create combined audio track
        
        Args:
            audio_segments: List of audio segments
            total_duration: Total timeline duration
        
        Returns:
            Combined audio clip
        """
        if not audio_segments:
            # Return silent audio
            return AudioFileClip(
                # Create silent audio (using a workaround)
                self._create_silent_audio(total_duration)
            )
        
        # Create audio clips
        clips = []
        current_time = 0.0
        
        for seg in audio_segments:
            audio_clip = AudioFileClip(str(seg.path))
            audio_clip = audio_clip.set_start(current_time)
            clips.append(audio_clip)
            current_time += seg.duration
        
        # Concatenate audio clips
        if len(clips) == 1:
            return clips[0]
        
        # Use CompositeAudioClip to overlay clips
        from moviepy.audio.CompositeAudioClip import CompositeAudioClip
        return CompositeAudioClip(clips)
    
    def _create_silent_audio(self, duration: float) -> str:
        """
        Create a silent audio file
        
        Args:
            duration: Duration in seconds
        
        Returns:
            Path to silent audio file
        """
        import tempfile
        
        # Create temporary silent audio
        temp_path = Path(tempfile.gettempdir()) / "silent.mp3"
        
        # Use ffmpeg to create silent audio
        import subprocess
        subprocess.run([
            'ffmpeg',
            '-f', 'lavfi',
            '-i', f'anullsrc=r=44100:cl=stereo',
            '-t', str(duration),
            '-q:a', '9',
            '-y',
            str(temp_path)
        ], capture_output=True)
        
        return str(temp_path)


# Import PIL for image resizing
from PIL import Image

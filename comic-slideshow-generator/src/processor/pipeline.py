"""
Main processing pipeline for Comic Slideshow Generator
Orchestrates bubble detection, OCR, TTS, and video generation
"""
import asyncio
from pathlib import Path
from typing import List, Optional, Callable
from dataclasses import dataclass, field
import numpy as np
from PIL import Image
import pdf2image
import cv2

from src.config import AppConfig
from src.bubble_detector import BubbleDetector, SpeechBubble
from src.text_extractor import OCREngine
from src.tts_engine import create_tts_engine
from src.video_generator import VideoCompositor
from src.processor.models import AudioSegment, TimelineSegment, Timeline, ProcessingResult


@dataclass
class AudioSegment:
    """Represents an audio segment with timing"""
    path: Path
    duration: float
    text: str
    bubble_idx: int
    
    def __post_init__(self):
        if isinstance(self.path, str):
            self.path = Path(self.path)


@dataclass
class TimelineSegment:
    """Represents a segment in the video timeline"""
    bubble_idx: int
    page_idx: int
    start_time: float
    duration: float
    bubble: SpeechBubble
    text: str
    
    @property
    def end_time(self) -> float:
        return self.start_time + self.duration


@dataclass
class Timeline:
    """Video timeline with all segments"""
    segments: List[TimelineSegment] = field(default_factory=list)
    total_duration: float = 0.0
    
    def add_segment(self, segment: TimelineSegment):
        """Add a segment to the timeline"""
        self.segments.append(segment)
        self.total_duration = max(self.total_duration, segment.end_time)
    
    def get_segments_for_page(self, page_idx: int) -> List[TimelineSegment]:
        """Get all segments for a specific page"""
        return [s for s in self.segments if s.page_idx == page_idx]


@dataclass
class ProcessingResult:
    """Result of comic processing"""
    pages: List[np.ndarray] = field(default_factory=list)
    bubbles: List[SpeechBubble] = field(default_factory=list)
    audio_segments: List[AudioSegment] = field(default_factory=list)
    timeline: Timeline = field(default_factory=Timeline)
    output_path: Optional[Path] = None
    
    @property
    def total_bubbles(self) -> int:
        return len(self.bubbles)
    
    @property
    def total_duration(self) -> float:
        return self.timeline.total_duration


class ComicProcessor:
    """Main processor for comic slideshow generation"""
    
    def __init__(self, config: Optional[AppConfig] = None):
        """
        Initialize comic processor
        
        Args:
            config: Application configuration
        """
        self.config = config or AppConfig()
        self.config.ensure_directories()
        self.config.validate_all()
        
        # Initialize components
        self.detector = BubbleDetector(self.config.detection)
        self.ocr = OCREngine(self.config.ocr)
        self.tts = create_tts_engine(self.config.tts)
        
        # Progress callback
        self.progress_callback: Optional[Callable[[str, float], None]] = None
    
    def set_progress_callback(self, callback: Callable[[str, float], None]):
        """Set callback for progress updates"""
        self.progress_callback = callback
    
    def _report_progress(self, message: str, progress: float = 0.0):
        """Report progress if callback is set"""
        if self.progress_callback:
            self.progress_callback(message, progress)
    
    async def process_comic(
        self,
        comic_path: Path,
        output_path: Optional[Path] = None
    ) -> ProcessingResult:
        """
        Process a comic and generate slideshow
        
        Args:
            comic_path: Path to comic file (JPG, PNG, PDF)
            output_path: Optional output path for video
        
        Returns:
            ProcessingResult with all generated data
        
        Raises:
            ValueError: If file type is not supported
            RuntimeError: If processing fails
        """
        self._report_progress("Starting comic processing...", 0.0)
        
        # Determine output path
        if output_path is None:
            output_path = self.config.output_dir / f"{comic_path.stem}_slideshow.mp4"
        else:
            output_path = Path(output_path)
        
        # Validate file
        if not comic_path.exists():
            raise ValueError(f"File not found: {comic_path}")
        
        # Load comic pages
        self._report_progress("Loading comic pages...", 0.1)
        pages = await self._load_comic(comic_path)
        
        if not pages:
            raise ValueError("No pages found in comic")
        
        # Detect bubbles on all pages
        self._report_progress("Detecting speech bubbles...", 0.2)
        all_bubbles = await self._detect_bubbles(pages)
        
        # Extract text from bubbles
        self._report_progress("Extracting text from bubbles...", 0.4)
        await self._extract_text(pages, all_bubbles)
        
        # Generate TTS for each bubble
        self._report_progress("Generating speech...", 0.6)
        audio_segments = await self._generate_tts(all_bubbles)
        
        # Create timeline
        self._report_progress("Creating timeline...", 0.8)
        timeline = self._create_timeline(all_bubbles, audio_segments)
        
        # Create result
        result = ProcessingResult(
            pages=pages,
            bubbles=all_bubbles,
            audio_segments=audio_segments,
            timeline=timeline,
            output_path=output_path
        )
        
        # Generate video file
        self._report_progress("Generating video...", 0.9)
        compositor = VideoCompositor(self.config.video)
        compositor.compose_video(pages, timeline, audio_segments, output_path)
        
        self._report_progress("Processing complete!", 1.0)
        
        return result
    
    async def _load_comic(self, comic_path: Path) -> List[np.ndarray]:
        """
        Load comic from file (supports JPG, PNG, PDF)
        
        Args:
            comic_path: Path to comic file
        
        Returns:
            List of pages as numpy arrays
        """
        suffix = comic_path.suffix.lower()
        
        if suffix in ['.jpg', '.jpeg', '.png']:
            # Single image
            image = cv2.imread(str(comic_path))
            if image is None:
                raise ValueError(f"Failed to load image: {comic_path}")
            return [image]
        
        elif suffix == '.pdf':
            # PDF with multiple pages
            try:
                images = pdf2image.convert_from_path(
                    str(comic_path),
                    dpi=200,
                    fmt='jpg'
                )
                # Convert PIL images to OpenCV format
                pages = []
                for img in images:
                    open_cv_image = np.array(img)
                    # Convert RGB to BGR
                    open_cv_image = open_cv_image[:, :, ::-1].copy()
                    pages.append(open_cv_image)
                return pages
            except Exception as e:
                raise RuntimeError(f"Failed to load PDF: {e}")
        
        else:
            raise ValueError(
                f"Unsupported file type: {suffix}. "
                f"Supported types: .jpg, .jpeg, .png, .pdf"
            )
    
    async def _detect_bubbles(
        self,
        pages: List[np.ndarray]
    ) -> List[SpeechBubble]:
        """
        Detect bubbles on all pages
        
        Args:
            pages: List of page images
        
        Returns:
            List of all bubbles
        """
        all_bubbles = []
        
        for page_idx, page in enumerate(pages):
            bubbles = self.detector.detect(page, page_idx)
            all_bubbles.extend(bubbles)
        
        return all_bubbles
    
    async def _extract_text(
        self,
        pages: List[np.ndarray],
        bubbles: List[SpeechBubble]
    ):
        """
        Extract text from all bubbles
        
        Args:
            pages: Page images
            bubbles: List of bubbles to extract from
        """
        for bubble in bubbles:
            page = pages[bubble.page_idx]
            
            try:
                text = self.ocr.extract_text(page, bubble.bbox)
                bubble.text = text
            except Exception as e:
                print(f"Error extracting text from bubble {bubble.bbox}: {e}")
                bubble.text = ""
    
    async def _generate_tts(
        self,
        bubbles: List[SpeechBubble]
    ) -> List[AudioSegment]:
        """
        Generate TTS for all bubbles
        
        Args:
            bubbles: List of bubbles with text
        
        Returns:
            List of audio segments
        """
        audio_segments = []
        temp_dir = self.config.temp_dir
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        for idx, bubble in enumerate(bubbles):
            if not bubble.text or not bubble.text.strip():
                # Skip empty bubbles
                continue
            
            audio_path = temp_dir / f"audio_{idx:03d}.mp3"
            
            try:
                duration = await self.tts.text_to_speech(
                    bubble.text,
                    str(audio_path)
                )
                
                segment = AudioSegment(
                    path=audio_path,
                    duration=duration,
                    text=bubble.text,
                    bubble_idx=idx
                )
                
                audio_segments.append(segment)
                
            except Exception as e:
                print(f"Error generating TTS for bubble {idx}: {e}")
        
        return audio_segments
    
    def _create_timeline(
        self,
        bubbles: List[SpeechBubble],
        audio_segments: List[AudioSegment]
    ) -> Timeline:
        """
        Create video timeline from bubbles and audio
        
        Args:
            bubbles: List of bubbles
            audio_segments: List of audio segments
        
        Returns:
            Timeline with all segments
        """
        timeline = Timeline()
        current_time = 0.0
        
        for audio_seg in audio_segments:
            bubble = bubbles[audio_seg.bubble_idx]
            
            segment = TimelineSegment(
                bubble_idx=audio_seg.bubble_idx,
                page_idx=bubble.page_idx,
                start_time=current_time,
                duration=audio_seg.duration,
                bubble=bubble,
                text=audio_seg.text
            )
            
            timeline.add_segment(segment)
            current_time += audio_seg.duration
        
        return timeline


def main():
    """Main entry point for CLI usage"""
    import argparse
    
    parser = argparse.ArgumentParser(
        description="Comic Slideshow Generator"
    )
    parser.add_argument(
        "input",
        type=Path,
        help="Path to comic file (JPG, PNG, PDF)"
    )
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output video path"
    )
    parser.add_argument(
        "-c", "--config",
        type=Path,
        help="Path to configuration file"
    )
    
    args = parser.parse_args()
    
    # Load config
    config = None
    if args.config:
        config = AppConfig.from_yaml(args.config)
    
    # Create processor
    processor = ComicProcessor(config)
    
    # Process
    result = asyncio.run(processor.process_comic(
        args.input,
        args.output
    ))
    
    print(f"\nProcessing complete!")
    print(f"Bubbles detected: {result.total_bubbles}")
    print(f"Total duration: {result.total_duration:.2f}s")
    print(f"Output: {result.output_path}")


if __name__ == "__main__":
    main()

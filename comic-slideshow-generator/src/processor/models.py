"""
Data models for Comic Slideshow Generator
"""
from pathlib import Path
from dataclasses import dataclass, field
from typing import List, TYPE_CHECKING
import numpy as np

if TYPE_CHECKING:
    from src.bubble_detector import SpeechBubble


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
    bubble: 'SpeechBubble'
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
    pages: List[np.ndarray]
    bubbles: List['SpeechBubble']
    audio_segments: List[AudioSegment]
    timeline: Timeline
    output_path: Path
    
    def __post_init__(self):
        if isinstance(self.output_path, str):
            self.output_path = Path(self.output_path)
    
    @property
    def total_bubbles(self) -> int:
        """Total number of bubbles detected"""
        return len(self.bubbles)
    
    @property
    def total_duration(self) -> float:
        """Total duration of generated video"""
        return self.timeline.total_duration

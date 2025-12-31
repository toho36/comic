"""
Speech bubble detection using OpenCV
Detects speech bubbles in comic images using adaptive thresholding and contour analysis
"""
import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from src.config import DetectionConfig


@dataclass
class SpeechBubble:
    """Represents a detected speech bubble"""
    bbox: Tuple[int, int, int, int]  # (x, y, width, height)
    text: str = ""
    confidence: float = 0.0
    page_idx: int = 0
    
    @property
    def x(self) -> int:
        return self.bbox[0]
    
    @property
    def y(self) -> int:
        return self.bbox[1]
    
    @property
    def width(self) -> int:
        return self.bbox[2]
    
    @property
    def height(self) -> int:
        return self.bbox[3]
    
    @property
    def area(self) -> int:
        return self.width * self.height
    
    @property
    def aspect_ratio(self) -> float:
        return self.width / self.height if self.height > 0 else 0.0
    
    @property
    def center(self) -> Tuple[int, int]:
        return (self.x + self.width // 2, self.y + self.height // 2)
    
    def overlaps_with(self, other: 'SpeechBubble', threshold: float = 0.3) -> bool:
        """
        Check if this bubble overlaps with another
        
        Args:
            other: Other bubble to check
            threshold: Minimum overlap ratio to consider as overlapping
        
        Returns:
            True if bubbles overlap significantly
        """
        x1 = max(self.x, other.x)
        y1 = max(self.y, other.y)
        x2 = min(self.x + self.width, other.x + other.width)
        y2 = min(self.y + self.height, other.y + other.height)
        
        if x2 <= x1 or y2 <= y1:
            return False
        
        overlap_area = (x2 - x1) * (y2 - y1)
        smaller_area = min(self.area, other.area)
        
        return (overlap_area / smaller_area) > threshold
    
    def merge_with(self, other: 'SpeechBubble') -> 'SpeechBubble':
        """
        Merge this bubble with another
        
        Args:
            other: Other bubble to merge with
        
        Returns:
            New merged bubble
        """
        x1 = min(self.x, other.x)
        y1 = min(self.y, other.y)
        x2 = max(self.x + self.width, other.x + other.width)
        y2 = max(self.y + self.height, other.y + other.height)
        
        return SpeechBubble(
            bbox=(x1, y1, x2 - x1, y2 - y1),
            text=self.text + " " + other.text,
            confidence=max(self.confidence, other.confidence),
            page_idx=self.page_idx
        )


class BubbleDetector:
    """Detects speech bubbles in comic images using computer vision"""
    
    def __init__(self, config: Optional[DetectionConfig] = None):
        """
        Initialize bubble detector
        
        Args:
            config: Detection configuration
        """
        self.config = config or DetectionConfig()
        self.config.validate_params()
    
    def detect(self, image: np.ndarray, page_idx: int = 0) -> List[SpeechBubble]:
        """
        Detect speech bubbles in an image
        
        Args:
            image: Input image (BGR format from OpenCV)
            page_idx: Page index for multi-page comics
        
        Returns:
            List of detected speech bubbles
        """
        # Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Apply Gaussian blur to reduce noise
        blurred = cv2.GaussianBlur(
            gray,
            (self.config.blur_kernel, self.config.blur_kernel),
            0
        )
        
        # Apply adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            self.config.threshold_block_size,
            2
        )
        
        # Morphological operations to clean up
        kernel = cv2.getStructuringElement(
            cv2.MORPH_RECT,
            (self.config.morph_close_kernel, self.config.morph_close_kernel)
        )
        cleaned = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        
        # Find contours
        contours, _ = cv2.findContours(
            cleaned,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Convert contours to bubbles
        bubbles = []
        for contour in contours:
            bubble = self._contour_to_bubble(contour, page_idx)
            if bubble and self._is_valid_bubble(bubble):
                bubbles.append(bubble)
        
        # Merge overlapping bubbles
        merged_bubbles = self._merge_overlapping_bubbles(bubbles)
        
        # Sort by reading order (top-to-bottom, left-to-right)
        merged_bubbles.sort(key=lambda b: (b.y, b.x))
        
        return merged_bubbles
    
    def _contour_to_bubble(
        self,
        contour: np.ndarray,
        page_idx: int
    ) -> Optional[SpeechBubble]:
        """
        Convert a contour to a speech bubble
        
        Args:
            contour: OpenCV contour
            page_idx: Page index
        
        Returns:
            SpeechBubble or None if invalid
        """
        area = cv2.contourArea(contour)
        
        if area < self.config.min_bubble_area:
            return None
        
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        
        return SpeechBubble(
            bbox=(x, y, w, h),
            confidence=1.0,  # Could be based on contour shape
            page_idx=page_idx
        )
    
    def _is_valid_bubble(self, bubble: SpeechBubble) -> bool:
        """
        Check if a bubble is valid based on configuration
        
        Args:
            bubble: Bubble to validate
        
        Returns:
            True if bubble is valid
        """
        # Check area
        if bubble.area < self.config.min_bubble_area:
            return False
        
        # Check aspect ratio
        aspect_ratio = bubble.aspect_ratio
        if not (self.config.min_aspect_ratio <= aspect_ratio <= self.config.max_aspect_ratio):
            return False
        
        return True
    
    def _merge_overlapping_bubbles(
        self,
        bubbles: List[SpeechBubble]
    ) -> List[SpeechBubble]:
        """
        Merge overlapping bubbles
        
        Args:
            bubbles: List of bubbles to merge
        
        Returns:
            List of merged bubbles
        """
        if not bubbles:
            return []
        
        # Simple greedy merging algorithm
        merged = [bubbles[0]]
        
        for bubble in bubbles[1:]:
            did_merge = False
            
            for i, merged_bubble in enumerate(merged):
                if bubble.overlaps_with(merged_bubble):
                    merged[i] = merged_bubble.merge_with(bubble)
                    did_merge = True
                    break
            
            if not did_merge:
                merged.append(bubble)
        
        return merged
    
    def visualize_detections(
        self,
        image: np.ndarray,
        bubbles: List[SpeechBubble],
        output_path: Optional[str] = None
    ) -> np.ndarray:
        """
        Visualize detected bubbles on an image
        
        Args:
            image: Original image
            bubbles: Detected bubbles
            output_path: Optional path to save visualization
        
        Returns:
            Image with drawn detections
        """
        vis = image.copy()
        
        for i, bubble in enumerate(bubbles):
            x, y, w, h = bubble.bbox
            
            # Draw rectangle
            color = (0, 255, 0)  # Green
            cv2.rectangle(vis, (x, y), (x + w, y + h), color, 2)
            
            # Draw label
            label = f"{i + 1}"
            cv2.putText(
                vis,
                label,
                (x, y - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2
            )
        
        if output_path:
            cv2.imwrite(output_path, vis)
        
        return vis

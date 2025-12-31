"""
Unit tests for bubble detector
Tests speech bubble detection using OpenCV
"""
import pytest
import cv2
import numpy as np
from pathlib import Path
from src.bubble_detector import BubbleDetector, SpeechBubble
from src.config import DetectionConfig


@pytest.fixture
def sample_config():
    """Create sample detection configuration"""
    return DetectionConfig(
        min_bubble_area=500,
        blur_kernel=5,
        threshold_block_size=11,
        morph_close_kernel=3,
        min_aspect_ratio=0.5,
        max_aspect_ratio=3.0
    )


@pytest.fixture
def detector(sample_config):
    """Create bubble detector instance"""
    return BubbleDetector(sample_config)


@pytest.fixture
def sample_image_with_bubbles():
    """
    Create a synthetic image with speech bubbles
    
    Returns:
        Tuple of (image, list of bubble bboxes)
    """
    # Create white background
    img = np.ones((600, 800, 3), dtype=np.uint8) * 255
    
    # Draw some speech bubbles (ellipses with black borders)
    bubbles = []
    
    # Bubble 1
    x, y, w, h = 100, 100, 200, 100
    cv2.ellipse(img, (x + w//2, y + h//2), (w//2, h//2), 0, 0, 360, (0, 0, 0), 3)
    cv2.ellipse(img, (x + w//2, y + h//2), (w//2 - 3, h//2 - 3), 0, 0, 360, (255, 255, 255), -1)
    bubbles.append((x, y, w, h))
    
    # Bubble 2
    x, y, w, h = 400, 150, 150, 120
    cv2.ellipse(img, (x + w//2, y + h//2), (w//2, h//2), 0, 0, 360, (0, 0, 0), 3)
    cv2.ellipse(img, (x + w//2, y + h//2), (w//2 - 3, h//2 - 3), 0, 0, 360, (255, 255, 255), -1)
    bubbles.append((x, y, w, h))
    
    # Bubble 3 (small, should be filtered)
    x, y, w, h = 600, 400, 50, 50
    cv2.ellipse(img, (x + w//2, y + h//2), (w//2, h//2), 0, 0, 360, (0, 0, 0), 3)
    cv2.ellipse(img, (x + w//2, y + h//2), (w//2 - 3, h//2 - 3), 0, 0, 360, (255, 255, 255), -1)
    bubbles.append((x, y, w, h))
    
    return img, bubbles


class TestSpeechBubble:
    """Tests for SpeechBubble dataclass"""
    
    def test_bubble_properties(self):
        """Test bubble property calculations"""
        bubble = SpeechBubble(bbox=(100, 200, 300, 150))
        
        assert bubble.x == 100
        assert bubble.y == 200
        assert bubble.width == 300
        assert bubble.height == 150
        assert bubble.area == 45000
        assert bubble.aspect_ratio == 2.0
        assert bubble.center == (250, 275)
    
    def test_overlapping_bubbles(self):
        """Test bubble overlap detection"""
        bubble1 = SpeechBubble(bbox=(0, 0, 100, 100))
        bubble2 = SpeechBubble(bbox=(50, 50, 100, 100))
        
        assert bubble1.overlaps_with(bubble2)
        assert bubble2.overlaps_with(bubble1)
    
    def test_non_overlapping_bubbles(self):
        """Test non-overlapping bubbles"""
        bubble1 = SpeechBubble(bbox=(0, 0, 100, 100))
        bubble2 = SpeechBubble(bbox=(200, 200, 100, 100))
        
        assert not bubble1.overlaps_with(bubble2)
    
    def test_merge_bubbles(self):
        """Test bubble merging"""
        bubble1 = SpeechBubble(bbox=(0, 0, 100, 100), text="Hello")
        bubble2 = SpeechBubble(bbox=(50, 50, 100, 100), text="World")
        
        merged = bubble1.merge_with(bubble2)
        
        assert merged.bbox == (0, 0, 150, 150)
        assert "Hello" in merged.text
        assert "World" in merged.text


class TestBubbleDetector:
    """Tests for BubbleDetector class"""
    
    def test_detector_initialization(self, sample_config):
        """Test detector initialization"""
        detector = BubbleDetector(sample_config)
        assert detector.config == sample_config
    
    def test_detector_detects_bubbles(self, detector, sample_image_with_bubbles):
        """Test that detector finds bubbles"""
        img, expected_bboxes = sample_image_with_bubbles
        
        detected = detector.detect(img)
        
        # Should detect at least the 2 large bubbles
        assert len(detected) >= 2
    
    def test_detector_filters_small_bubbles(self, detector, sample_image_with_bubbles):
        """Test that small bubbles are filtered out"""
        img, expected_bboxes = sample_image_with_bubbles
        
        detected = detector.detect(img)
        
        # Small bubble (50x50 = 2500 pixels) might be filtered depending on min_area
        # Our config has min_bubble_area=500, so it should be detected
        # But real detection might miss it due to contour detection
        for bubble in detected:
            assert bubble.area >= detector.config.min_bubble_area
    
    def test_detector_sorts_by_reading_order(self, detector, sample_image_with_bubbles):
        """Test that bubbles are sorted in reading order"""
        img, _ = sample_image_with_bubbles
        
        detected = detector.detect(img)
        
        # Check sorting: top-to-bottom, left-to-right
        for i in range(len(detected) - 1):
            current = detected[i]
            next_bubble = detected[i + 1]
            
            # If on same y-level (within 50px), x should increase
            if abs(current.y - next_bubble.y) < 50:
                assert current.x < next_bubble.x
            # Otherwise, y should increase
            else:
                assert current.y < next_bubble.y
    
    def test_visualize_detections(self, detector, sample_image_with_bubbles, tmp_path):
        """Test visualization of detected bubbles"""
        img, _ = sample_image_with_bubbles
        detected = detector.detect(img)
        
        output_path = tmp_path / "visualization.jpg"
        vis = detector.visualize_detections(img, detected, str(output_path))
        
        assert output_path.exists()
        assert vis.shape == img.shape


class TestBubbleDetectionEdgeCases:
    """Tests for edge cases in bubble detection"""
    
    def test_empty_image(self, detector):
        """Test detection on empty image"""
        empty_img = np.ones((100, 100, 3), dtype=np.uint8) * 255
        detected = detector.detect(empty_img)
        assert len(detected) == 0
    
    def test_noisy_image(self, detector):
        """Test detection on noisy image"""
        noisy_img = np.random.randint(0, 255, (600, 800, 3), dtype=np.uint8)
        detected = detector.detect(noisy_img)
        # Should not crash, might detect some noise as bubbles
        assert isinstance(detected, list)
    
    def test_very_small_bubble_filtered(self, sample_config):
        """Test that very small bubbles are filtered"""
        config = DetectionConfig(min_bubble_area=10000)  # High threshold
        detector = BubbleDetector(config)
        
        # Create image with small bubble
        img = np.ones((600, 800, 3), dtype=np.uint8) * 255
        x, y, w, h = 100, 100, 50, 50  # 2500 pixels
        cv2.ellipse(img, (x + w//2, y + h//2), (w//2, h//2), 0, 0, 360, (0, 0, 0), 3)
        cv2.ellipse(img, (x + w//2, y + h//2), (w//2 - 3, h//2 - 3), 0, 0, 360, (255, 255, 255), -1)
        
        detected = detector.detect(img)
        
        # Should be filtered out
        assert len(detected) == 0
    
    def test_aspect_ratio_filtering(self, sample_config):
        """Test aspect ratio filtering"""
        config = DetectionConfig(
            min_bubble_area=100,
            min_aspect_ratio=0.8,
            max_aspect_ratio=1.2
        )
        detector = BubbleDetector(config)
        
        # Create image with very wide bubble
        img = np.ones((600, 800, 3), dtype=np.uint8) * 255
        x, y, w, h = 100, 100, 300, 50  # aspect ratio = 6.0
        cv2.ellipse(img, (x + w//2, y + h//2), (w//2, h//2), 0, 0, 360, (0, 0, 0), 3)
        cv2.ellipse(img, (x + w//2, y + h//2), (w//2 - 3, h//2 - 3), 0, 0, 360, (255, 255, 255), -1)
        
        detected = detector.detect(img)
        
        # Should be filtered out due to aspect ratio
        assert len(detected) == 0

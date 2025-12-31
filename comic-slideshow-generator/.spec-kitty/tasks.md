# Detailed Task Definitions: Comic Slideshow Generator

This document provides comprehensive implementation details for each task in the implementation plan.

---

## Task 1: Project Structure & Configuration

### Objective
Initialize the project with proper structure, configuration system, and development environment.

### Detailed Steps

**1. Directory Structure Creation**
```bash
comic-slideshow-generator/
├── .spec-kitty/           # Spec-kitty files (already exists)
├── src/
│   ├── __init__.py
│   ├── preprocessing/
│   │   ├── __init__.py
│   │   ├── image_loader.py
│   │   └── pdf_converter.py
│   ├── detection/
│   │   ├── __init__.py
│   │   └── bubble_detector.py
│   ├── extraction/
│   │   ├── __init__.py
│   │   └── text_extractor.py
│   ├── tts/
│   │   ├── __init__.py
│   │   ├── base.py
│   │   ├── edge_tts.py
│   │   └── openai_tts.py
│   ├── video/
│   │   ├── __init__.py
│   │   └── video_generator.py
│   ├── config.py
│   ├── processor.py
│   └── utils.py
├── tests/
│   ├── __init__.py
│   ├── fixtures/
│   ├── test_config.py
│   └── test_*.py
├── examples/
├── app.py                 # Streamlit app
├── main.py                # CLI
├── requirements.txt
├── .env.example
├── pyproject.toml
├── README.md
└── .gitignore
```

**2. Configuration Dataclasses (config.py)**
```python
from dataclasses import dataclass
from typing import Optional
import os

@dataclass
class DetectionConfig:
    """Configuration for speech bubble detection."""
    min_bubble_area: int = 500
    max_bubble_area: int = 500000
    blur_kernel: int = 5
    threshold_block_size: int = 11
    threshold_c: int = 2
    min_aspect_ratio: float = 0.3
    max_aspect_ratio: float = 3.0
    min_solidity: float = 0.9

@dataclass
class OCRConfig:
    """Configuration for OCR text extraction."""
    language: str = 'ces+eng'  # Czech + English
    confidence_threshold: int = 60
    ocr_config: str = '--psm 6'  # Assume uniform block of text

@dataclass
class TTSConfig:
    """Configuration for text-to-speech."""
    engine: str = 'edge'  # 'edge' or 'openai'
    voice: str = 'cs-CZ-AntoninNeural'
    rate: float = 1.0
    pitch: int = 0
    format: str = 'mp3'
    api_key: Optional[str] = None

@dataclass
class VideoConfig:
    """Configuration for video generation."""
    fps: int = 24
    codec: str = 'libx264'
    bitrate: str = '5M'
    transition_duration: float = 0.5
    zoom_duration: float = 2.0
    quality: str = '720p'  # '480p', '720p', '1080p'

@dataclass
class AppConfig:
    """Main application configuration."""
    detection: DetectionConfig
    ocr: OCRConfig
    tts: TTSConfig
    video: VideoConfig
    tesseract_cmd: Optional[str] = None
    poppler_path: Optional[str] = None
    ffmpeg_path: Optional[str] = None
    cache_dir: str = './cache'
    output_dir: str = './output'
    log_level: str = 'INFO'
    
    @classmethod
    def from_env(cls) -> 'AppConfig':
        """Load configuration from environment variables."""
        return cls(
            detection=DetectionConfig(),
            ocr=OCRConfig(),
            tts=TTSConfig(
                engine=os.getenv('TTS_ENGINE', 'edge'),
                voice=os.getenv('TTS_VOICE', 'cs-CZ-AntoninNeural'),
                api_key=os.getenv('OPENAI_API_KEY')
            ),
            video=VideoConfig(),
            tesseract_cmd=os.getenv('TESSERACT_CMD'),
            poppler_path=os.getenv('POPPLER_PATH'),
            ffmpeg_path=os.getenv('FFMPEG_PATH'),
            cache_dir=os.getenv('CACHE_DIR', './cache'),
            output_dir=os.getenv('OUTPUT_DIR', './output'),
            log_level=os.getenv('LOG_LEVEL', 'INFO')
        )
```

**3. Logging Setup (utils.py)**
```python
import logging
import sys
from pathlib import Path

def setup_logging(level: str = 'INFO') -> logging.Logger:
    """Setup structured logging for the application."""
    log_level = getattr(logging, level.upper(), logging.INFO)
    
    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('comic_slideshow.log')
        ]
    )
    
    return logging.getLogger('comic_slideshow')
```

**4. requirements.txt**
```txt
# Core dependencies
opencv-python>=4.8.0
pytesseract>=0.3.10
pdf2image>=1.16.0
Pillow>=10.0.0
moviepy>=1.0.3
edge-tts>=6.1.0
numpy>=1.24.0

# Optional: OpenAI API
openai>=1.0.0

# Configuration
python-dotenv>=1.0.0

# UI
streamlit>=1.28.0

# Development
pytest>=7.4.0
pytest-asyncio>=0.21.0
pytest-cov>=4.1.0
black>=23.0.0
pylint>=2.17.0
mypy>=1.5.0
```

**5. .env.example**
```env
# OpenAI API (optional, for paid TTS)
OPENAI_API_KEY=sk-...

# External dependencies paths (if not in PATH)
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract
POPPLER_PATH=C:/Program Files/poppler
FFMPEG_PATH=C:/ffmpeg/bin

# TTS Configuration
TTS_ENGINE=edge
TTS_VOICE=cs-CZ-AntoninNeural

# Application Settings
CACHE_DIR=./cache
OUTPUT_DIR=./output
LOG_LEVEL=INFO
```

**Tests Required:**
- [ ] Test AppConfig loads default values
- [ ] Test AppConfig.from_env() reads environment variables
- [ ] Test logging setup creates log file
- [ ] Test directory structure exists after setup

---

## Task 2: Dependency Detection Module

### Objective
Create a module to detect and validate external dependencies (Tesseract, Poppler, FFmpeg).

### Detailed Implementation

**File: src/dependency_checker.py**
```python
import shutil
import platform
import subprocess
from typing import Dict, List, Optional
from dataclasses import dataclass

@dataclass
class DependencyStatus:
    """Status of a single dependency."""
    name: str
    installed: bool
    version: Optional[str] = None
    path: Optional[str] = None
    error: Optional[str] = None

class DependencyChecker:
    """Check for required external dependencies."""
    
    INSTALL_INSTRUCTIONS = {
        'Windows': {
            'tesseract': (
                "1. Download installer from: https://github.com/UB-Mannheim/tesseract/wiki\n"
                "2. Install to: C:\\Program Files\\Tesseract-OCR\n"
                "3. Add to PATH: C:\\Program Files\\Tesseract-OCR"
            ),
            'poppler': (
                "1. Download from: http://blog.alivate.com.au/poppler-windows/\n"
                "2. Extract to: C:\\Program Files\\poppler\n"
                "3. Add bin folder to PATH: C:\\Program Files\\poppler\\bin"
            ),
            'ffmpeg': (
                "1. Download from: https://ffmpeg.org/download.html\n"
                "2. Extract to: C:\\ffmpeg\n"
                "3. Add bin folder to PATH"
            )
        },
        'Darwin': {  # macOS
            'tesseract': "brew install tesseract",
            'poppler': "brew install poppler",
            'ffmpeg': "brew install ffmpeg"
        },
        'Linux': {
            'tesseract': "sudo apt-get install tesseract-ocr",
            'poppler': "sudo apt-get install poppler-utils",
            'ffmpeg': "sudo apt-get install ffmpeg"
        }
    }
    
    def __init__(self):
        self.system = platform.system()
        self.platform_key = 'Darwin' if self.system == 'macOS' else self.system
    
    def check_tesseract(self, custom_path: Optional[str] = None) -> DependencyStatus:
        """Check if Tesseract OCR is installed."""
        cmd = custom_path or 'tesseract'
        
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                version = version_line.split(' ')[1]
                path = shutil.which(cmd) if not custom_path else custom_path
                return DependencyStatus(
                    name='Tesseract',
                    installed=True,
                    version=version,
                    path=path
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return DependencyStatus(
            name='Tesseract',
            installed=False,
            error='Tesseract OCR not found in PATH'
        )
    
    def check_poppler(self, custom_path: Optional[str] = None) -> DependencyStatus:
        """Check if Poppler is installed."""
        # Check for pdftoppm or pdftocairo
        cmd = custom_path + '/pdftoppm' if custom_path else 'pdftoppm'
        
        try:
            result = subprocess.run(
                [cmd, '--version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.split('\n')[0].split()[-1]
                path = shutil.which('pdftoppm') if not custom_path else custom_path
                return DependencyStatus(
                    name='Poppler',
                    installed=True,
                    version=version,
                    path=path
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return DependencyStatus(
            name='Poppler',
            installed=False,
            error='Poppler not found in PATH'
        )
    
    def check_ffmpeg(self, custom_path: Optional[str] = None) -> DependencyStatus:
        """Check if FFmpeg is installed."""
        cmd = custom_path + '/ffmpeg' if custom_path else 'ffmpeg'
        
        try:
            result = subprocess.run(
                [cmd, '-version'],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version_line = result.stdout.split('\n')[0]
                version = version_line.split(' ')[2]
                path = shutil.which('ffmpeg') if not custom_path else custom_path
                return DependencyStatus(
                    name='FFmpeg',
                    installed=True,
                    version=version,
                    path=path
                )
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        return DependencyStatus(
            name='FFmpeg',
            installed=False,
            error='FFmpeg not found in PATH'
        )
    
    def check_all(self, custom_paths: Dict[str, Optional[str]] = None) -> Dict[str, DependencyStatus]:
        """Check all required dependencies."""
        custom_paths = custom_paths or {}
        
        return {
            'tesseract': self.check_tesseract(custom_paths.get('tesseract')),
            'poppler': self.check_poppler(custom_paths.get('poppler')),
            'ffmpeg': self.check_ffmpeg(custom_paths.get('ffmpeg'))
        }
    
    def get_installation_instructions(self, dependency: str) -> str:
        """Get platform-specific installation instructions."""
        return self.INSTALL_INSTRUCTIONS.get(self.platform_key, {}).get(
            dependency,
            f"Please install {dependency} for your platform"
        )
    
    def format_error_message(self, status: DependencyStatus) -> str:
        """Format a user-friendly error message."""
        if status.installed:
            return f"✓ {status.name} {status.version} found at {status.path}"
        
        instructions = self.get_installation_instructions(status.name.lower())
        return (
            f"✗ {status.name} not found\n"
            f"Error: {status.error}\n\n"
            f"To install {status.name}:\n{instructions}\n"
        )
```

**Tests Required:**
- [ ] Test check_tesseract() when installed
- [ ] Test check_tesseract() when not installed
- [ ] Test check_poppler() when installed
- [ ] Test check_poppler() when not installed
- [ ] Test check_ffmpeg() when installed
- [ ] Test check_ffmpeg() when not installed
- [ ] Test format_error_message() for each dependency
- [ ] Test check_all() returns correct statuses

---

## Task 4: Speech Bubble Detection

### Objective
Implement computer vision algorithm to detect speech bubbles in comic images.

### Detailed Implementation

**File: src/detection/bubble_detector.py**
```python
import cv2
import numpy as np
from typing import List, Tuple, Optional
from dataclasses import dataclass
from src.config import DetectionConfig

@dataclass
class SpeechBubble:
    """Represents a detected speech bubble."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    text: str = ""
    confidence: float = 0.0
    area: float = 0.0
    solidity: float = 0.0

class BubbleDetector:
    """Detect speech bubbles in comic images using OpenCV."""
    
    def __init__(self, config: DetectionConfig):
        self.config = config
    
    def detect(self, image: np.ndarray) -> List[SpeechBubble]:
        """
        Detect speech bubbles in an image.
        
        Args:
            image: Input image as numpy array (BGR format from OpenCV)
        
        Returns:
            List of detected SpeechBubble objects
        """
        # Step 1: Convert to grayscale
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        
        # Step 2: Apply Gaussian blur
        blurred = cv2.GaussianBlur(
            gray,
            (self.config.blur_kernel, self.config.blur_kernel),
            0
        )
        
        # Step 3: Adaptive thresholding
        thresh = cv2.adaptiveThreshold(
            blurred,
            255,
            cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV,
            self.config.threshold_block_size,
            self.config.threshold_c
        )
        
        # Step 4: Find contours
        contours, _ = cv2.findContours(
            thresh,
            cv2.RETR_EXTERNAL,
            cv2.CHAIN_APPROX_SIMPLE
        )
        
        # Step 5: Filter contours
        bubbles = []
        for contour in contours:
            bubble = self._process_contour(contour, image.shape)
            if bubble:
                bubbles.append(bubble)
        
        # Step 6: Merge overlapping bubbles
        bubbles = self._merge_overlapping_bubbles(bubbles)
        
        return bubbles
    
    def _process_contour(
        self,
        contour: np.ndarray,
        image_shape: Tuple[int, int, int]
    ) -> Optional[SpeechBubble]:
        """Process a single contour and filter by criteria."""
        # Get bounding rectangle
        x, y, w, h = cv2.boundingRect(contour)
        
        # Calculate area
        area = cv2.contourArea(contour)
        
        # Skip if too small or too large
        if area < self.config.min_bubble_area or area > self.config.max_bubble_area:
            return None
        
        # Calculate aspect ratio
        aspect_ratio = float(w) / h if h > 0 else 0
        if not (self.config.min_aspect_ratio <= aspect_ratio <= self.config.max_aspect_ratio):
            return None
        
        # Calculate solidity (area / convex hull area)
        hull = cv2.convexHull(contour)
        hull_area = cv2.contourArea(hull)
        solidity = float(area) / hull_area if hull_area > 0 else 0
        if solidity < self.config.min_solidity:
            return None
        
        # Create speech bubble object
        return SpeechBubble(
            bbox=(x, y, x + w, y + h),
            area=area,
            solidity=solidity
        )
    
    def _merge_overlapping_bubbles(
        self,
        bubbles: List[SpeechBubble]
    ) -> List[SpeechBubble]:
        """Merge overlapping bubble detections."""
        if not bubbles:
            return []
        
        # Sort by x-coordinate
        sorted_bubbles = sorted(bubbles, key=lambda b: b.bbox[0])
        
        merged = []
        current = sorted_bubbles[0]
        
        for bubble in sorted_bubbles[1:]:
            if self._bubbles_overlap(current, bubble):
                # Merge bubbles
                x1 = min(current.bbox[0], bubble.bbox[0])
                y1 = min(current.bbox[1], bubble.bbox[1])
                x2 = max(current.bbox[2], bubble.bbox[2])
                y2 = max(current.bbox[3], bubble.bbox[3])
                
                current = SpeechBubble(
                    bbox=(x1, y1, x2, y2),
                    area=(x2 - x1) * (y2 - y1),
                    solidity=min(current.solidity, bubble.solidity)
                )
            else:
                merged.append(current)
                current = bubble
        
        merged.append(current)
        return merged
    
    def _bubbles_overlap(
        self,
        bubble1: SpeechBubble,
        bubble2: SpeechBubble,
        iou_threshold: float = 0.5
    ) -> bool:
        """Check if two bubbles overlap significantly."""
        x1_min, y1_min, x1_max, y1_max = bubble1.bbox
        x2_min, y2_min, x2_max, y2_max = bubble2.bbox
        
        # Calculate intersection
        inter_x_min = max(x1_min, x2_min)
        inter_y_min = max(y1_min, y2_min)
        inter_x_max = min(x1_max, x2_max)
        inter_y_max = min(y1_max, y2_max)
        
        if inter_x_max < inter_x_min or inter_y_max < inter_y_min:
            return False
        
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
        
        # Calculate union
        area1 = (x1_max - x1_min) * (y1_max - y1_min)
        area2 = (x2_max - x2_min) * (y2_max - y2_min)
        union_area = area1 + area2 - inter_area
        
        # Calculate IoU
        iou = float(inter_area) / union_area if union_area > 0 else 0
        
        return iou > iou_threshold
    
    def visualize(self, image: np.ndarray, bubbles: List[SpeechBubble]) -> np.ndarray:
        """Visualize detected bubbles on the image."""
        vis_image = image.copy()
        
        for i, bubble in enumerate(bubbles):
            x1, y1, x2, y2 = bubble.bbox
            
            # Draw rectangle
            cv2.rectangle(vis_image, (x1, y1), (x2, y2), (0, 255, 0), 2)
            
            # Draw label
            label = f"Bubble {i+1}"
            cv2.putText(
                vis_image,
                label,
                (x1, y1 - 10),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.5,
                (0, 255, 0),
                2
            )
        
        return vis_image
```

**Tests Required:**
- [ ] Test detection on simple comic page with clear bubbles
- [ ] Test detection on complex page with multiple bubbles
- [ ] Test min_area filtering works correctly
- [ ] Test aspect ratio filtering
- [ ] Test solidity filtering
- [ ] Test overlapping bubble merging
- [ ] Test visualize() adds correct overlays
- [ ] Test detection accuracy >85% on test dataset
- [ ] Test empty image returns empty list
- [ ] Test image with no bubbles returns empty list

---

## Task 8: Main Processor Orchestration

### Objective
Create the main processor that orchestrates the entire pipeline from comic to video.

### Detailed Implementation

**File: src/processor.py**
```python
import os
import logging
from typing import Optional, List, Callable
from pathlib import Path
from dataclasses import dataclass, field
import tempfile
import shutil

from src.config import AppConfig, DetectionConfig, OCRConfig, TTSConfig, VideoConfig
from src.preprocessing.image_loader import ImageLoader
from src.preprocessing.pdf_converter import PDFConverter
from src.detection.bubble_detector import BubbleDetector
from src.extraction.text_extractor import TextExtractor
from src.tts.base import TTSEngine
from src.tts.edge_tts import EdgeTTSEngine
from src.tts.openai_tts import OpenAITTSEngine
from src.video.video_generator import VideoGenerator

@dataclass
class ProcessingResult:
    """Result of comic processing."""
    input_path: str
    output_path: str
    bubble_count: int
    total_duration: float
    success: bool
    errors: List[str] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    
    def add_error(self, error: str):
        """Add an error to the result."""
        self.errors.append(error)
        logging.error(error)
    
    def add_warning(self, warning: str):
        """Add a warning to the result."""
        self.warnings.append(warning)
        logging.warning(warning)

class ComicProcessor:
    """Main processor for converting comics to slideshow videos."""
    
    def __init__(self, config: AppConfig):
        self.config = config
        self.logger = logging.getLogger('comic_slideshow.processor')
        
        # Initialize components
        self.image_loader = ImageLoader()
        self.pdf_converter = PDFConverter(config.poppler_path)
        self.bubble_detector = BubbleDetector(config.detection)
        self.text_extractor = TextExtractor(config.ocr, config.tesseract_cmd)
        self.video_generator = VideoGenerator(config.video, config.ffmpeg_path)
        
        # Initialize TTS engine
        self.tts_engine = self._create_tts_engine(config.tts)
        
        # Temporary directory for intermediate files
        self.temp_dir: Optional[tempfile.TemporaryDirectory] = None
    
    def _create_tts_engine(self, config: TTSConfig) -> TTSEngine:
        """Create appropriate TTS engine based on configuration."""
        if config.engine == 'openai':
            if not config.api_key:
                raise ValueError("OpenAI API key required for OpenAI TTS engine")
            return OpenAITTSEngine(config)
        return EdgeTTSEngine(config)
    
    def process(
        self,
        input_path: str,
        output_path: str,
        progress_callback: Optional[Callable[[str, float], None]] = None
    ) -> ProcessingResult:
        """
        Process a comic file into a slideshow video.
        
        Args:
            input_path: Path to input comic file (JPG, PNG, PDF)
            output_path: Path for output video file
            progress_callback: Optional callback for progress updates
                               Callback args: (stage, progress_percent)
        
        Returns:
            ProcessingResult with details and status
        """
        result = ProcessingResult(
            input_path=input_path,
            output_path=output_path,
            bubble_count=0,
            total_duration=0.0,
            success=False
        )
        
        try:
            # Create temporary directory
            self.temp_dir = tempfile.TemporaryDirectory(prefix='comic_slideshow_')
            self.logger.info(f"Created temporary directory: {self.temp_dir.name}")
            
            # Stage 1: Load and convert comic (0-20%)
            self._update_progress(progress_callback, "Loading comic...", 0)
            pages = self._load_comic(input_path, result)
            if not pages:
                raise ValueError("No pages loaded from comic")
            self._update_progress(progress_callback, "Comic loaded", 20)
            
            # Stage 2: Detect bubbles (20-40%)
            self._update_progress(progress_callback, "Detecting speech bubbles...", 20)
            all_bubbles = []
            for i, page in enumerate(pages):
                page_progress = 20 + (20 * (i + 1) / len(pages))
                bubbles = self.bubble_detector.detect(page)
                all_bubbles.extend(bubbles)
                self._update_progress(progress_callback, f"Detected {len(bubbles)} bubbles on page {i+1}", page_progress)
            result.bubble_count = len(all_bubbles)
            self._update_progress(progress_callback, f"Detected {len(all_bubbles)} bubbles total", 40)
            
            # Stage 3: Extract text (40-60%)
            self._update_progress(progress_callback, "Extracting text...", 40)
            texts = self._extract_texts(pages, all_bubbles, result)
            self._update_progress(progress_callback, f"Extracted {len(texts)} texts", 60)
            
            # Stage 4: Generate audio (60-80%)
            self._update_progress(progress_callback, "Generating speech...", 60)
            audio_files = self._generate_audio(texts, result)
            self._update_progress(progress_callback, f"Generated {len(audio_files)} audio files", 80)
            
            # Stage 5: Create video (80-100%)
            self._update_progress(progress_callback, "Creating video...", 80)
            video_info = self.video_generator.generate(
                pages=pages,
                bubbles=all_bubbles,
                audio_files=audio_files,
                output_path=output_path
            )
            result.total_duration = video_info['duration']
            self._update_progress(progress_callback, "Video created successfully", 100)
            
            result.success = True
            self.logger.info(f"Successfully processed comic: {input_path} -> {output_path}")
            
        except Exception as e:
            result.add_error(f"Processing failed: {str(e)}")
            self.logger.exception("Processing failed")
        finally:
            # Cleanup temporary files
            if self.temp_dir:
                try:
                    self.temp_dir.cleanup()
                    self.logger.info("Cleaned up temporary files")
                except Exception as e:
                    result.add_warning(f"Failed to cleanup temp directory: {str(e)}")
        
        return result
    
    def _load_comic(self, input_path: str, result: ProcessingResult) -> List[np.ndarray]:
        """Load comic file and convert to list of images."""
        path = Path(input_path)
        suffix = path.suffix.lower()
        
        if suffix in ['.jpg', '.jpeg', '.png']:
            return [self.image_loader.load(input_path)]
        elif suffix == '.pdf':
            return self.pdf_converter.convert(input_path)
        else:
            raise ValueError(f"Unsupported file format: {suffix}")
    
    def _extract_texts(
        self,
        pages: List[np.ndarray],
        bubbles: List['SpeechBubble'],
        result: ProcessingResult
    ) -> List[str]:
        """Extract text from all bubbles."""
        texts = []
        for bubble in bubbles:
            try:
                # Get the page this bubble is on
                page = pages[bubble.page_number]
                text = self.text_extractor.extract_from_bubble(page, bubble)
                texts.append(text)
            except Exception as e:
                result.add_warning(f"Failed to extract text from bubble: {str(e)}")
                texts.append("")  # Add empty text to maintain alignment
        
        return texts
    
    def _generate_audio(
        self,
        texts: List[str],
        result: ProcessingResult
    ) -> List[str]:
        """Generate audio files for all texts."""
        audio_files = []
        
        for i, text in enumerate(texts):
            if not text.strip():
                continue
            
            try:
                output_path = os.path.join(self.temp_dir.name, f"audio_{i:04d}.mp3")
                self.tts_engine.generate_async(text, output_path)
                audio_files.append(output_path)
            except Exception as e:
                result.add_warning(f"Failed to generate audio for text {i}: {str(e)}")
        
        return audio_files
    
    def _update_progress(
        self,
        callback: Optional[Callable[[str, float], None]],
        message: str,
        percent: float
    ):
        """Update progress if callback is provided."""
        if callback:
            callback(message, percent)
        self.logger.info(f"[{percent:.0f}%] {message}")
```

**Tests Required:**
- [ ] Test end-to-end processing with JPG input
- [ ] Test end-to-end processing with PNG input
- [ ] Test end-to-end processing with PDF input
- [ ] Test progress callback is invoked correctly
- [ ] Test error recovery on detection failure (continues to next stage)
- [ ] Test error recovery on TTS failure (continues with next text)
- [ ] Test temporary files are cleaned up
- [ ] Test ProcessingResult contains correct metadata
- [ ] Test processing performance <30s per page
- [ ] Test error messages are added to result on failure

---

## Summary

This document provides detailed implementation specifications for the key tasks. Each task includes:

1. **Clear objective** - What the task accomplishes
2. **Detailed implementation code** - Production-ready Python code
3. **Comprehensive test requirements** - All acceptance criteria

### Next Steps

To begin implementation:

1. **Review all task details** in this document
2. **Set up development environment** following Task 1
3. **Implement tasks in order** following the dependency chain in plan.md
4. **Write tests as you go** - don't leave testing to the end
5. **Run tests frequently** to catch issues early

### Test-Driven Development Approach

For each task:
1. Write tests first (based on test requirements)
2. Implement the code to make tests pass
3. Refactor and optimize
4. Document any deviations from the spec

### Completion Criteria

Each task is complete when:
- [ ] All code is implemented
- [ ] All tests pass
- [ ] Code follows constitution (type hints, docstrings, PEP 8)
- [ ] Logging is implemented
- [ ] Error handling is comprehensive
- [ ] Code is documented with docstrings

---

*This tasks document is version 1.0 and will be updated as implementation progresses.*

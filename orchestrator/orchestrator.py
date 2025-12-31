#!/usr/bin/env python3
"""
Multi-Agent Orchestrator for Comic Slideshow Generator
Coordinates 12 specialized agents working in parallel to implement the project
"""
import asyncio
import yaml
import json
import logging
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum
import subprocess
import sys


# ============================================================================
# CONFIGURATION
# ============================================================================

class AgentTier(Enum):
    """Agent tiers for execution priority"""
    TIER_1_CORE = "tier_1_core"      # Frontend, Backend, ML, Integrations
    TIER_2_QUALITY = "tier_2_quality"  # Test, Optimize, Debug, Document
    TIER_3_GOVERNANCE = "tier_3_governance"  # Audit, Review, Security, Deploy


class AgentStatus(Enum):
    """Agent execution status"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"


@dataclass
class AgentConfig:
    """Configuration for a single agent"""
    name: str
    tier: AgentTier
    description: str
    dependencies: List[str] = field(default_factory=list)
    max_retries: int = 3
    timeout_seconds: int = 600
    goose_subrecipe: Optional[str] = None
    instructions_template: str = ""


@dataclass
class WorkflowPhase:
    """A phase in the workflow with parallel agents"""
    name: str
    description: str
    agents: List[str]
    parallel: bool = True


@dataclass
class OrchestratorConfig:
    """Main orchestrator configuration"""
    project_name: str = "Comic Slideshow Generator"
    project_root: str = "."
    dry_run: bool = False
    max_parallel_agents: int = 4
    log_level: str = "INFO"
    git_integration: bool = True
    auto_commit: bool = False
    phases: List[WorkflowPhase] = field(default_factory=list)
    agents: Dict[str, AgentConfig] = field(default_factory=dict)


# ============================================================================
# AGENT DEFINITIONS
# ============================================================================

AGENT_DEFINITIONS = {
    "project_structure": AgentConfig(
        name="project_structure",
        tier=AgentTier.TIER_1_CORE,
        description="Creates directory structure, __init__.py files, package layout",
        goose_subrecipe="implement",
        instructions_template="""
You are the Project Structure Agent. Your task is to create the complete directory structure for the Comic Slideshow Generator project.

Create the following structure:
```
comic-slideshow-generator/
├── src/
│   ├── __init__.py
│   ├── bubble_detector/
│   │   ├── __init__.py
│   │   ├── detector.py
│   │   └── config.py
│   ├── text_extractor/
│   │   ├── __init__.py
│   │   ├── ocr_engine.py
│   │   └── preprocessor.py
│   ├── tts_engine/
│   │   ├── __init__.py
│   │   ├── edge_tts.py
│   │   └── openai_tts.py
│   ├── video_generator/
│   │   ├── __init__.py
│   │   ├── compositor.py
│   │   └── timeline.py
│   ├── processor/
│   │   ├── __init__.py
│   │   └── pipeline.py
│   ├── config/
│   │   ├── __init__.py
│   │   ├── settings.py
│   │   └── loader.py
│   └── ui/
│       ├── __init__.py
│       └── streamlit_app.py
├── tests/
│   ├── __init__.py
│   ├── test_detector.py
│   ├── test_ocr.py
│   ├── test_tts.py
│   └── test_pipeline.py
├── examples/
│   └── sample_comic.jpg
├── docs/
│   ├── API.md
│   └── USAGE.md
├── requirements.txt
├── setup.py
├── .gitignore
├── README.md
└── .env.example
```

Use pathlib for all path operations. Create all directories with proper permissions.
"""
    ),
    
    "dependencies": AgentConfig(
        name="dependencies",
        tier=AgentTier.TIER_1_CORE,
        description="Creates requirements.txt, setup.py, and dependency checker",
        goose_subrecipe="implement",
        instructions_template="""
You are the Dependencies Agent. Create all dependency management files.

1. Create requirements.txt with:
```
opencv-python>=4.8.0
pytesseract>=0.3.10
pdf2image>=1.16.0
moviepy>=1.0.3
edge-tts>=6.1.9
openai>=1.3.0
python-dotenv>=1.0.0
pydantic>=2.4.0
pydantic-settings>=2.0.0
pillow>=10.0.0
numpy>=1.24.0
pytest>=7.4.0
pytest-cov>=4.1.0
pytest-asyncio>=0.21.0
streamlit>=1.28.0
```

2. Create setup.py for package installation with proper metadata.

3. Create dependency_checker.py that validates:
   - Tesseract OCR installation
   - ImageMagick for moviepy
   - FFmpeg for video processing
   - Platform-specific instructions for missing deps

Return the path to requirements.txt when complete.
"""
    ),
    
    "config_framework": AgentConfig(
        name="config_framework",
        tier=AgentTier.TIER_1_CORE,
        description="Creates configuration system with dataclasses and validation",
        goose_subrecipe="implement",
        instructions_template="""
You are the Configuration Framework Agent. Implement the complete configuration system using Pydantic.

Create src/config/settings.py with:

1. DetectionConfig dataclass:
   - min_bubble_area: int = 500
   - blur_kernel: int = 5
   - threshold_block_size: int = 11
   - morph_close_kernel: int = 3
   - min_aspect_ratio: float = 0.5
   - max_aspect_ratio: float = 3.0

2. OCRConfig dataclass:
   - engine: str = "tesseract"
   - languages: List[str] = ["ces", "eng"]
   - oem: int = 3
   - psm: int = 7
   - min_confidence: float = 0.6

3. TTSConfig dataclass:
   - provider: str = "edge"
   - voice: str = "en-US-AriaNeural"
   - rate: str = "+0%"
   - volume: str = "+0%"
   - api_key: Optional[str] = None (for OpenAI)

4. VideoConfig dataclass:
   - fps: int = 24
   - bubble_zoom_duration: float = 1.0
   - transition_duration: float = 0.5
   - output_codec: str = "libx264"
   - audio_bitrate: str = "192k"

5. AppConfig class that loads all configs from .env or YAML

Include comprehensive validation, type hints, and docstrings. Return the path to settings.py.
"""
    ),
    
    "ml_computer_vision": AgentConfig(
        name="ml_computer_vision",
        tier=AgentTier.TIER_1_CORE,
        dependencies=["config_framework"],
        description="Implements bubble detection using OpenCV",
        goose_subrecipe="implement",
        instructions_template="""
You are the ML/Computer Vision Agent. Implement the bubble detection system.

Create src/bubble_detector/detector.py:

1. BubbleDetector class with:
   - detect(image: np.ndarray) -> List[SpeechBubble]
   - Uses adaptive thresholding
   - Contour detection and filtering
   - Bubble merging algorithm
   - Aspect ratio validation

2. SpeechBubble dataclass:
   - bbox: Tuple[int, int, int, int] (x, y, w, h)
   - text: str
   - confidence: float

Algorithm:
```python
def detect(self, image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blurred = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blurred, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV, 11, 2
    )
    contours, _ = cv2.findContours(thresh, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    
    bubbles = []
    for contour in contours:
        area = cv2.contourArea(contour)
        if area < self.config.min_bubble_area:
            continue
        x, y, w, h = cv2.boundingRect(contour)
        aspect_ratio = w / h
        if self.config.min_aspect_ratio <= aspect_ratio <= self.config.max_aspect_ratio:
            bubbles.append(SpeechBubble(bbox=(x, y, w, h)))
    
    return self._merge_overlapping_bubbles(bubbles)
```

Include comprehensive type hints, docstrings, and error handling. Return the path to detector.py.
"""
    ),
    
    "integrations_ocr": AgentConfig(
        name="integrations_ocr",
        tier=AgentTier.TIER_1_CORE,
        dependencies=["config_framework"],
        description="Implements OCR text extraction with pytesseract",
        goose_subrecipe="implement",
        instructions_template="""
You are the Integrations/OCR Agent. Implement the text extraction system.

Create src/text_extractor/ocr_engine.py:

1. OCREngine class with:
   - extract_text(image: np.ndarray, bbox: Tuple[int, int, int, int]) -> str
   - extract_with_confidence() -> Tuple[str, float]
   - Supports Czech and English languages

2. ImagePreprocessor class with:
   - denoise(image)
   - binarize(image)
   - enhance_contrast(image)

Implementation:
```python
import pytesseract
from PIL import Image

class OCREngine:
    def __init__(self, config: OCRConfig):
        self.config = config
        
    def extract_text(self, image: np.ndarray, bbox: Tuple[int, int, int, int]) -> str:
        x, y, w, h = bbox
        roi = image[y:y+h, x:x+w]
        pil_img = Image.fromarray(roi)
        
        text = pytesseract.image_to_string(
            pil_img,
            lang='+'.join(self.config.languages),
            config=f'--oem {self.config.oem} --psm {self.config.psm}'
        )
        return text.strip()
```

Include proper error handling for Tesseract not installed, and retry logic. Return the path to ocr_engine.py.
"""
    ),
    
    "audio_tts": AgentConfig(
        name="audio_tts",
        tier=AgentTier.TIER_1_CORE,
        dependencies=["config_framework"],
        description="Implements text-to-speech with edge-tts and OpenAI",
        goose_subrecipe="implement",
        instructions_template="""
You are the Audio/TTS Agent. Implement the text-to-speech system.

Create src/tts_engine/ with two files:

1. edge_tts.py - EdgeTTSEngine class:
```python
import edge_tts
import asyncio

class EdgeTTSEngine:
    async def text_to_speech(self, text: str, output_path: str) -> float:
        communicate = edge_tts.Communicate(
            text, self.config.voice, rate=self.config.rate
        )
        await communicate.save(output_path)
        return self._get_audio_duration(output_path)
```

2. openai_tts.py - OpenAITTSEngine class:
```python
from openai import AsyncOpenAI

class OpenAITTSEngine:
    async def text_to_speech(self, text: str, output_path: str) -> float:
        client = AsyncOpenAI(api_key=self.config.api_key)
        response = await client.audio.speech.create(
            model="tts-1",
            voice=self.config.voice,
            input=text
        )
        response.stream_to_file(output_path)
        return self._get_audio_duration(output_path)
```

3. Create a factory function that selects engine based on config.

Include proper async/await, error handling, and cleanup. Return the path to edge_tts.py.
"""
    ),
    
    "backend_processor": AgentConfig(
        name="backend_processor",
        tier=AgentTier.TIER_1_CORE,
        dependencies=["ml_computer_vision", "integrations_ocr", "audio_tts"],
        description="Implements main orchestration pipeline",
        goose_subrecipe="implement",
        instructions_template="""
You are the Backend/Processor Agent. Implement the main processing pipeline.

Create src/processor/pipeline.py:

ComicProcessor class with:

1. process_comic() method:
```python
async def process_comic(
    self,
    comic_path: Path,
    output_path: Path
) -> ProcessingResult:
    # 1. Load comic (JPG/PNG/PDF)
    pages = self._load_comic(comic_path)
    
    # 2. Detect bubbles on each page
    all_bubbles = []
    for page in pages:
        bubbles = await self.detector.detect(page)
        all_bubbles.extend(bubbles)
    
    # 3. Extract text from bubbles
    for bubble in all_bubbles:
        text = await self.ocr.extract_text(page, bubble.bbox)
        bubble.text = text
    
    # 4. Generate TTS for each bubble
    audio_segments = []
    for bubble in all_bubbles:
        audio_path = self.temp_dir / f"audio_{len(audio_segments)}.mp3"
        duration = await self.tts.text_to_speech(bubble.text, audio_path)
        audio_segments.append(AudioSegment(audio_path, duration))
    
    # 5. Generate timeline
    timeline = self._create_timeline(all_bubbles, audio_segments)
    
    return ProcessingResult(bubbles=all_bubbles, audio=audio_segments, timeline=timeline)
```

2. Include proper error handling, progress callbacks, and logging.

3. ProcessingResult dataclass with all output data.

Return the path to pipeline.py.
"""
    ),
    
    "frontend_ui": AgentConfig(
        name="frontend_ui",
        tier=AgentTier.TIER_1_CORE,
        dependencies=["config_framework"],
        description="Implements Streamlit user interface",
        goose_subrecipe="implement",
        instructions_template="""
You are the Frontend/UI Agent. Implement the Streamlit interface.

Create src/ui/streamlit_app.py:

Features:
1. File upload (JPG, PNG, PDF)
2. Configuration sidebar (detection, OCR, TTS settings)
3. Progress indicators
4. Preview bubbles on images
5. Video preview
6. Download button

Structure:
```python
import streamlit as st

st.set_page_config(page_title="Comic Slideshow Generator", layout="wide")

st.title("🎭 Comic Slideshow Generator")

# Sidebar configuration
with st.sidebar:
    st.header("Configuration")
    detection_config = load_detection_config()
    ocr_config = load_ocr_config()
    tts_config = load_tts_config()

# Main area
col1, col2 = st.columns(2)

with col1:
    uploaded_file = st.file_uploader(
        "Upload Comic",
        type=['jpg', 'jpeg', 'png', 'pdf']
    )

with col2:
    if uploaded_file:
        if st.button("Generate Slideshow"):
            with st.spinner("Processing..."):
                result = process_comic(uploaded_file, configs)
                st.video(result.video_path)
                st.download_button("Download Video", result.video_path)
```

Include proper state management, error handling, and responsive design. Return the path to streamlit_app.py.
"""
    ),
    
    "video_generator": AgentConfig(
        name="video_generator",
        tier=AgentTier.TIER_1_CORE,
        dependencies=["backend_processor"],
        description="Implements video composition with moviepy",
        goose_subrecipe="implement",
        instructions_template="""
You are the Video Generator Agent. Implement the video composition system.

Create src/video_generator/compositor.py:

VideoCompositor class with:

1. compose_video() method:
```python
def compose_video(
    self,
    images: List[np.ndarray],
    audio_segments: List[AudioSegment],
    timeline: Timeline,
    output_path: Path
) -> Path:
    clips = []
    
    for segment in timeline.segments:
        # Create zoomed clip for bubble
        clip = self._create_bubble_clip(
            images[segment.page_idx],
            segment.bubble,
            segment.duration
        )
        clips.append(clip)
    
    # Concatenate all clips
    final_video = concatenate_videoclips(clips)
    
    # Add audio
    audio = self._create_audio_track(audio_segments)
    final_video = final_video.set_audio(audio)
    
    # Export
    final_video.write_videofile(
        str(output_path),
        fps=self.config.fps,
        codec=self.config.output_codec
    )
    
    return output_path
```

2. _create_bubble_clip() - Creates zoomed clip with smooth pan/zoom

3. _create_audio_track() - Combines all audio segments with timing

Include proper cleanup, error handling, and progress callbacks. Return the path to compositor.py.
"""
    ),
    
    "testing": AgentConfig(
        name="testing",
        tier=AgentTier.TIER_2_QUALITY,
        dependencies=["backend_processor", "frontend_ui", "video_generator"],
        description="Creates comprehensive test suite",
        goose_subrecipe="test",
        instructions_template="""
You are the Testing Agent. Create comprehensive unit and integration tests.

Create tests/ directory with:

1. test_detector.py:
   - test_bubble_detection_basic()
   - test_bubble_filtering_by_area()
   - test_aspect_ratio_validation()
   - test_overlapping_bubble_merge()
   - Use pytest fixtures for sample images

2. test_ocr.py:
   - test_text_extraction_czech()
   - test_text_extraction_english()
   - test_confidence_threshold()
   - test_tesseract_not_installed_error()

3. test_tts.py:
   - test_edge_tts_basic()
   - test_audio_file_creation()
   - test_openai_tts_with_api_key()

4. test_pipeline.py:
   - test_end_to_end_processing()
   - test_pdf_input()
   - test_error_handling()

Each test file should have >80% coverage of its target module.

Use pytest, pytest-asyncio, pytest-cov.

Create a run_tests.sh script that runs:
```bash
pytest --cov=src --cov-report=html --cov-report=term -v
```

Return the path to the test directory.
"""
    ),
    
    "documentation": AgentConfig(
        name="documentation",
        tier=AgentTier.TIER_2_QUALITY,
        dependencies=["backend_processor", "frontend_ui", "video_generator"],
        description="Creates API documentation and user guides",
        goose_subrecipe="document",
        instructions_template="""
You are the Documentation Agent. Create comprehensive documentation.

Create the following documentation files:

1. README.md - Main project README with:
   - Project overview
   - Feature list
   - Quick start guide
   - Installation instructions (with platform-specific notes)
   - Usage examples
   - Configuration options
   - Troubleshooting

2. docs/API.md - API documentation with:
   - All public classes and methods
   - Type signatures
   - Usage examples
   - Parameter descriptions

3. docs/USAGE.md - User guide with:
   - Step-by-step tutorial
   - Screenshots (placeholder)
   - Example comics
   - Tips and tricks

4. docs/ARCHITECTURE.md - Architecture overview:
   - System diagram
   - Module interactions
   - Data flow
   - Extension points

5. Code should be fully documented with:
   - Module docstrings
   - Class docstrings
   - Method docstrings with Args, Returns, Raises
   - Inline comments for complex logic

Return the path to README.md.
"""
    ),
    
    "optimization": AgentConfig(
        name="optimization",
        tier=AgentTier.TIER_2_QUALITY,
        dependencies=["backend_processor", "testing"],
        description="Optimizes performance and resource usage",
        goose_subrecipe="optimize",
        instructions_template="""
You are the Optimization Agent. Analyze and optimize the codebase.

Focus areas:

1. Bubble Detection Performance:
   - Optimize image preprocessing pipeline
   - Consider multiprocessing for multi-page comics
   - Cache intermediate results

2. Memory Usage:
   - Implement streaming for large PDFs
   - Clean up temporary audio files
   - Optimize numpy array usage

3. Async Optimization:
   - Ensure all I/O is truly async
   - Optimize TTS batch processing
   - Parallel bubble detection per page

4. Create performance profiles:
   - Benchmark bubble detection on sample images
   - Profile OCR performance
   - Measure video rendering time

5. Add performance logging:
   - Log timing for each pipeline stage
   - Track memory usage
   - Identify bottlenecks

Return a PERFORMANCE.md file with benchmarks and optimization notes.
"""
    ),
    
    "security": AgentConfig(
        name="security",
        tier=AgentTier.TIER_3_GOVERNANCE,
        dependencies=["backend_processor", "frontend_ui"],
        description="Adds security measures and input validation",
        goose_subrecipe="audit",
        instructions_template="""
You are the Security Agent. Add security measures to the codebase.

Security tasks:

1. Input Validation:
   - Validate file types (prevent malicious uploads)
   - Limit file sizes (prevent DoS)
   - Sanitize text inputs
   - Validate configuration values

2. API Key Security:
   - Never log API keys
   - Use environment variables
   - Provide .env.example

3. File Operations:
   - Validate file paths (prevent path traversal)
   - Limit temporary file creation
   - Clean up temp files

4. Error Messages:
   - Don't expose internal paths in errors
   - Sanitize exception messages

5. Create a security checklist:
   - [ ] Input validation on all user inputs
   - [ ] File type validation
   - [ ] Path traversal prevention
   - [ ] API key protection
   - [ ] Secure temporary file handling

Return a SECURITY.md file with the security checklist and implementation notes.
"""
    ),
}


# ============================================================================
# ORCHESTRATOR MAIN CLASS
# ============================================================================

class MultiAgentOrchestrator:
    """Orchestrates multiple specialized agents for parallel project implementation"""
    
    def __init__(self, config_path: str = "orchestrator_config.yaml"):
        """Initialize the orchestrator"""
        self.config = self._load_config(config_path)
        self.setup_logging()
        self.agent_status: Dict[str, AgentStatus] = {}
        self.agent_results: Dict[str, Any] = {}
        self.start_time = None
        
    def _load_config(self, config_path: str) -> OrchestratorConfig:
        """Load configuration from YAML file"""
        config_file = Path(config_path)
        if config_file.exists():
            with open(config_file) as f:
                data = yaml.safe_load(f)
            return self._parse_config(data)
        else:
            # Return default config
            return OrchestratorConfig()
    
    def _parse_config(self, data: dict) -> OrchestratorConfig:
        """Parse configuration dictionary into OrchestratorConfig object"""
        config = OrchestratorConfig()
        
        # Parse phases
        if "phases" in data:
            for phase_data in data["phases"]:
                agents = phase_data.get("agents", [])
                phase = WorkflowPhase(
                    name=phase_data["name"],
                    description=phase_data.get("description", ""),
                    agents=agents,
                    parallel=phase_data.get("parallel", True)
                )
                config.phases.append(phase)
        
        # Override other settings
        for key in ["project_name", "dry_run", "max_parallel_agents", "log_level"]:
            if key in data:
                setattr(config, key, data[key])
        
        return config
    
    def setup_logging(self):
        """Setup logging configuration"""
        log_format = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
        logging.basicConfig(
            level=getattr(logging, self.config.log_level),
            format=log_format,
            handlers=[
                logging.FileHandler("orchestrator/logs/orchestrator.log"),
                logging.StreamHandler(sys.stdout)
            ]
        )
        self.logger = logging.getLogger("Orchestrator")
    
    async def execute_agent(
        self,
        agent_name: str,
        agent_config: AgentConfig,
        phase_context: Dict[str, Any]
    ) -> Tuple[bool, Any]:
        """Execute a single agent"""
        self.logger.info(f"Starting agent: {agent_name}")
        self.agent_status[agent_name] = AgentStatus.RUNNING
        
        try:
            # Prepare instructions
            instructions = agent_config.instructions_template.format(**phase_context)
            
            # Execute via Goose subagent
            if self.config.dry_run:
                result = f"DRY RUN: Would execute {agent_name}"
            else:
                result = await self._run_subagent(
                    agent_name,
                    instructions,
                    agent_config.goose_subrecipe
                )
            
            self.agent_status[agent_name] = AgentStatus.COMPLETED
            self.agent_results[agent_name] = result
            self.logger.info(f"Completed agent: {agent_name}")
            return True, result
            
        except Exception as e:
            self.logger.error(f"Agent {agent_name} failed: {str(e)}")
            self.agent_status[agent_name] = AgentStatus.FAILED
            return False, str(e)
    
    async def _run_subagent(
        self,
        agent_name: str,
        instructions: str,
        subrecipe: Optional[str]
    ) -> Any:
        """Run a subagent via subprocess"""
        # This would interface with the actual Goose subagent system
        # For now, we'll simulate it
        self.logger.info(f"Running subagent: {agent_name} with subrecipe: {subrecipe}")
        # TODO: Integrate with actual Goose subagent API
        await asyncio.sleep(0.1)  # Simulate async work
        return f"Result from {agent_name}"
    
    async def execute_phase(
        self,
        phase: WorkflowPhase,
        phase_context: Dict[str, Any]
    ) -> Dict[str, Tuple[bool, Any]]:
        """Execute a single phase (potentially with parallel agents)"""
        self.logger.info(f"Starting phase: {phase.name}")
        phase_results = {}
        
        # Filter agents that haven't been completed
        pending_agents = [
            agent for agent in phase.agents
            if self.agent_status.get(agent) != AgentStatus.COMPLETED
        ]
        
        if phase.parallel:
            # Execute agents in parallel
            tasks = []
            for agent_name in pending_agents:
                if agent_name in AGENT_DEFINITIONS:
                    task = self.execute_agent(
                        agent_name,
                        AGENT_DEFINITIONS[agent_name],
                        phase_context
                    )
                    tasks.append(task)
            
            # Wait for all tasks
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            for agent_name, result in zip(pending_agents, results):
                if isinstance(result, Exception):
                    phase_results[agent_name] = (False, str(result))
                else:
                    phase_results[agent_name] = result
        else:
            # Execute agents sequentially
            for agent_name in pending_agents:
                if agent_name in AGENT_DEFINITIONS:
                    result = await self.execute_agent(
                        agent_name,
                        AGENT_DEFINITIONS[agent_name],
                        phase_context
                    )
                    phase_results[agent_name] = result
        
        self.logger.info(f"Completed phase: {phase.name}")
        return phase_results
    
    async def run_workflow(self) -> Dict[str, Any]:
        """Run the complete workflow"""
        self.start_time = datetime.now()
        self.logger.info(f"Starting workflow: {self.config.project_name}")
        
        # Define default phases if not in config
        if not self.config.phases:
            self.config.phases = self._get_default_phases()
        
        # Initialize agent status
        for agent_name in AGENT_DEFINITIONS:
            self.agent_status[agent_name] = AgentStatus.PENDING
        
        # Execute phases sequentially
        all_results = {}
        phase_context = {}
        
        for phase in self.config.phases:
            phase_results = await self.execute_phase(phase, phase_context)
            all_results[phase.name] = phase_results
            
            # Check if any critical agents failed
            failed_agents = [
                agent for agent, (success, _) in phase_results.items()
                if not success
            ]
            if failed_agents:
                self.logger.error(f"Phase {phase.name} had failures: {failed_agents}")
                # Continue to next phase anyway
        
        # Generate summary
        elapsed = datetime.now() - self.start_time
        summary = {
            "total_time": str(elapsed),
            "agents_completed": sum(
                1 for status in self.agent_status.values()
                if status == AgentStatus.COMPLETED
            ),
            "agents_failed": sum(
                1 for status in self.agent_status.values()
                if status == AgentStatus.FAILED
            ),
            "phase_results": all_results
        }
        
        self.logger.info(f"Workflow completed in {elapsed}")
        return summary
    
    def _get_default_phases(self) -> List[WorkflowPhase]:
        """Get default workflow phases for Comic Slideshow Generator"""
        return [
            WorkflowPhase(
                name="Phase 1: Foundation",
                description="Setup project structure and configuration",
                agents=["project_structure", "dependencies", "config_framework"],
                parallel=True
            ),
            WorkflowPhase(
                name="Phase 2: Core Features",
                description="Implement ML, OCR, and TTS components",
                agents=["ml_computer_vision", "integrations_ocr", "audio_tts"],
                parallel=True
            ),
            WorkflowPhase(
                name="Phase 3: Integration & UI",
                description="Integrate components and build UI",
                agents=["backend_processor", "frontend_ui", "video_generator"],
                parallel=True
            ),
            WorkflowPhase(
                name="Phase 4: Quality & Deployment",
                description="Testing, documentation, optimization, and security",
                agents=["testing", "documentation", "optimization", "security"],
                parallel=True
            )
        ]
    
    def save_results(self, results: Dict[str, Any]):
        """Save execution results to JSON file"""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_path = f"orchestrator/results/run_{timestamp}.json"
        
        with open(results_path, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        self.logger.info(f"Results saved to: {results_path}")


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Multi-Agent Orchestrator")
    parser.add_argument("--config", default="orchestrator_config.yaml", help="Config file path")
    parser.add_argument("--dry-run", action="store_true", help="Dry run without execution")
    parser.add_argument("--parallel", type=int, default=4, help="Max parallel agents")
    args = parser.parse_args()
    
    # Create orchestrator
    orchestrator = MultiAgentOrchestrator(args.config)
    
    # Override config with CLI args
    if args.dry_run:
        orchestrator.config.dry_run = True
    if args.parallel:
        orchestrator.config.max_parallel_agents = args.parallel
    
    # Run workflow
    results = await orchestrator.run_workflow()
    
    # Save results
    orchestrator.save_results(results)
    
    # Print summary
    print("\n" + "="*60)
    print("ORCHESTRATION COMPLETE")
    print("="*60)
    print(f"Total Time: {results['total_time']}")
    print(f"Agents Completed: {results['agents_completed']}")
    print(f"Agents Failed: {results['agents_failed']}")
    print("="*60)


if __name__ == "__main__":
    asyncio.run(main())

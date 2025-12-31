# Feature Specification: Comic Slideshow Generator

## Overview

Build an AI-powered application that automatically creates animated slideshow presentations from comic books. The system will detect speech bubbles, extract text using OCR, convert text to speech, and generate synchronized video presentations.

### Goals

1. Automate the conversion of static comics into engaging audiovisual presentations
2. Support multiple input formats (JPG, PNG, PDF, CBZ)
3. Provide accurate speech bubble detection and text extraction
4. Offer both free (edge-tts) and paid (OpenAI) text-to-speech options
5. Create an intuitive user interface for non-technical users

### Objectives

- Reduce manual effort in creating comic presentations by 95%
- Achieve >85% accuracy in bubble detection
- Support Czech and English languages
- Process a 10-page comic in under 2 minutes
- Provide a web-based UI and optional desktop application

### Success Criteria

- [ ] Can process JPG, PNG, CBR and PDF files successfully
- [ ] Detects speech bubbles with >85% accuracy
- [ ] Extracts text with >90% OCR accuracy
- [ ] Generates MP4 video with synchronized audio
- [ ] Supports Czech TTS with multiple voice options
- [ ] Provides user-friendly Streamlit interface
- [ ] Handles errors gracefully with clear messages
- [ ] Includes comprehensive test coverage (>80%)

---

## User Stories

### Story 1: Comic Loading

**As** a teacher  
**I want** to upload a comic PDF file  
**So that** I can create an accessible audiovisual version for my students

**Acceptance Criteria:**

- [ ] Can upload PDF files via drag-and-drop or file browser
- [ ] System validates PDF format and shows preview
- [ ] PDF pages are converted to images with proper resolution (300 DPI)
- [ ] Upload progress is shown for large files
- [ ] Error message if PDF is corrupted or password-protected

### Story 2: Bubble Detection

**As** a content creator  
**I want** the system to automatically identify speech bubbles  
**So that** I don't have to manually mark them

**Acceptance Criteria:**

- [ ] System detects elliptical and rectangular speech bubbles
- [ ] Bubbles are highlighted in preview overlay
- [ ] Detection accuracy >85% on standard comic styles
- [ ] Can adjust detection sensitivity via slider
- [ ] Manual correction mode for missed bubbles (planned feature)

### Story 3: Text Extraction

**As** a publisher  
**I want** the extracted text to be accurate  
**So that** the audio narration matches the original content

**Acceptance Criteria:**

- [ ] OCR extracts text with >90% accuracy on clear text
- [ ] Handles Czech characters (č, ř, ž, š, etc.) correctly
- [ ] Filters low-confidence text (<60% confidence)
- [ ] Shows extracted text for review/editing before TTS
- [ ] Preserves reading order (top-to-bottom, left-to-right)

### Story 4: Text-to-Speech

**As** a visually impaired user  
**I want** to hear the comic content in natural-sounding speech  
**So that** I can enjoy comics independently

**Acceptance Criteria:**

- [ ] Supports at least 2 Czech voices (male/female)
- [ ] Supports at least 2 English voices
- [ ] Free tier uses edge-tts (no API key required)
- [ ] Paid tier uses OpenAI TTS for higher quality
- [ ] Can adjust speech rate (0.5x to 2.0x)
- [ ] Audio duration is synchronized with video timing

### Story 5: Video Generation

**As** a social media creator  
**I want** to export the presentation as MP4  
**So that** I can share it on video platforms

**Acceptance Criteria:**

- [ ] Generates MP4 video with H.264 codec
- [ ] Configurable FPS (24, 30, 60)
- [ ] Each bubble is displayed for the duration of its audio
- [ ] Smooth transitions between bubbles (fade/zoom effects)
- [ ] Video quality is at least 720p
- [ ] Estimated file size shown before generation

### Story 6: User Interface

**As** a non-technical user  
**I want** an intuitive web interface  
**So that** I can use the tool without command-line knowledge

**Acceptance Criteria:**

- [ ] Single-page Streamlit application
- [ ] File upload widget with drag-and-drop
- [ ] Live preview of comic pages with bubble overlays
- [ ] Configuration panel for TTS voice and settings
- [ ] Progress bar for long-running operations
- [ ] Download button for generated video
- [ ] Help tooltips for each setting

### Story 7: Configuration

**As** a developer  
**I want** to configure the system via environment variables  
**So that** I can deploy it in different environments

**Acceptance Criteria:**

- [ ] Supports `.env` file for configuration
- [ ] Configurable paths to Tesseract, Poppler, FFmpeg
- [ ] Optional OpenAI API key for premium TTS
- [ ] Configurable cache and output directories
- [ ] Logging level adjustable (DEBUG, INFO, WARNING, ERROR)

---

## Functional Requirements

### FR-1: File Preprocessing

**Priority:** High  
**Description:** Load and convert comic files to images

**Input:**

- File path or uploaded file object
- File format: JPG, PNG, PDF

**Output:**

- List of PIL Image objects
- Metadata: page count, dimensions, format

**Processing:**

- For JPG/PNG: Direct loading with Pillow
- For PDF: Convert using pdf2image at 300 DPI
- Validate file integrity before processing
- Handle multi-page PDFs

**Error Handling:**

- FileNotFoundError if file doesn't exist
- ValueError if file format is unsupported
- RuntimeError if PDF conversion fails

### FR-2: Speech Bubble Detection

**Priority:** High  
**Description:** Detect speech bubbles in comic images

**Input:**

- PIL Image object
- Configuration: min_area, blur_kernel, threshold

**Output:**

- List of bounding boxes [(x1, y1, x2, y2), ...]
- Confidence scores for each detection
- Filtered results (by area, aspect ratio)

**Algorithm:**

1. Convert image to grayscale
2. Apply Gaussian blur (kernel size 5)
3. Perform adaptive thresholding
4. Find contours using OpenCV
5. Filter contours by:
   - Minimum area (default 500 pixels)
   - Aspect ratio (0.3 to 3.0)
   - Solidity (>0.9)
6. Merge overlapping detections

**Configuration:**

```python
{
    'min_bubble_area': 500,      # pixels
    'max_bubble_area': 500000,   # pixels
    'blur_kernel': 5,            # odd number
    'threshold_block_size': 11,
    'threshold_c': 2
}
```

### FR-3: Text Extraction (OCR)

**Priority:** High  
**Description:** Extract text from detected speech bubbles

**Input:**

- PIL Image object
- List of bounding boxes
- OCR configuration: language, confidence threshold

**Output:**

- List of extracted texts with metadata
- Reading order (top-to-bottom, left-to-right)
- Confidence scores for each text

**Processing:**

1. Crop image regions for each bubble
2. Preprocess: binarize, denoise
3. Run pytesseract with Czech/English language
4. Filter by confidence threshold (default 60%)
5. Sort by reading order
6. Clean up text (remove extra whitespace)

**Error Handling:**

- Empty results if no text detected
- Low confidence warning if <60%
- Fallback to English if Czech fails

### FR-4: Text-to-Speech Conversion

**Priority:** High  
**Description:** Convert extracted text to audio files

**Input:**

- List of text strings
- TTS configuration: engine, voice, rate, pitch
- Output directory

**Output:**

- List of audio file paths (WAV or MP3)
- Duration for each audio file
- Total audio duration

**Engines:**

**Option 1: edge-tts (Free)**

```python
import edge_tts

async def generate_audio(text: str, voice: str) -> str:
    communicate = edge_tts.Communicate(text, voice)
    await communicate.save(f"output_{i}.mp3")
```

Supported English voices:

- `en-US-GuyNeural` (male)
- `en-US-AriaNeural` (female)

**Option 2: OpenAI TTS (Paid)**

```python
from openai import OpenAI

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
response = client.audio.speech.create(
    model="tts-1",
    voice="alloy",
    input=text
)
response.stream_to_file(f"output_{i}.mp3")
```

**Configuration:**

```python
{
    'engine': 'edge',  # or 'openai'
    'voice': 'cs-CZ-AntoninNeural',
    'rate': 1.0,       # 0.5 to 2.0
    'pitch': 0,        # -10 to 10
    'format': 'mp3'
}
```

### FR-5: Video Generation

**Priority:** High  
**Description:** Generate slideshow video with synchronized audio

**Input:**

- List of images
- List of audio files with durations
- Video configuration: fps, codec, transitions

**Output:**

- MP4 video file path
- Video metadata: duration, resolution, file size

**Processing:**

1. Calculate duration for each segment (audio length + buffer)
2. For each bubble:
   - Create video clip from image (duration = audio duration)
   - Apply zoom/pan effect to focus on bubble
   - Add audio clip
3. Concatenate all clips
4. Add fade transitions (0.5s)
5. Encode with H.264 codec
6. Write to output file

**Zoom Effect:**

- Start with full page view
- Zoom into bubble over 2 seconds
- Hold zoom for audio duration
- Zoom out before next bubble

**Configuration:**

```python
{
    'fps': 24,
    'codec': 'libx264',
    'bitrate': '5M',
    'transition_duration': 0.5,
    'zoom_duration': 2.0
}
```

### FR-6: Streamlit UI

**Priority:** Medium  
**Description:** Web-based user interface

**Components:**

**Sidebar:**

- File upload widget
- TTS configuration
- Video settings
- Advanced options

**Main Area:**

- Comic page preview
- Bubble detection overlay
- Extracted text editor
- Video player (after generation)

**Bottom:**

- Progress bar
- Status messages
- Download button

**State Management:**

```python
if 'uploaded_file' not in st.session_state:
    st.session_state.uploaded_file = None
if 'bubbles' not in st.session_state:
    st.session_state.bubbles = []
if 'extracted_text' not in st.session_state:
    st.session_state.extracted_text = []
```

---

## Non-Functional Requirements

### NFR-1: Performance

- Single page processing: <30 seconds
- 10-page PDF processing: <2 minutes
- Video generation: <30 seconds per minute of video
- Memory usage: <2GB for 50-page PDF

### NFR-2: Reliability

- 99% crash-free rate on valid inputs
- Graceful degradation on detection failures
- Automatic retry for TTS API failures (3 attempts)
- Temporary file cleanup on exit

### NFR-3: Usability

- No command-line knowledge required
- Intuitive UI with <5 clicks to generate video
- Clear error messages with solutions
- Tooltips and help text for all settings

### NFR-4: Compatibility

- Windows 10+, macOS 10.15+, Linux (Ubuntu 20.04+)
- Python 3.10, 3.11, 3.12
- Modern browsers (Chrome, Firefox, Safari, Edge)

### NFR-5: Security

- No API keys stored in code
- Input validation for all user inputs
- Sanitized file paths
- Rate limiting for API calls
- No sensitive data in logs

### NFR-6: Maintainability

- Modular architecture with clear separation of concerns
- Comprehensive test suite (>80% coverage)
- Documentation for all public APIs
- Type hints for all functions
- Logging for debugging

### NFR-7: Scalability

- Support batch processing of multiple comics
- Handle PDFs up to 100 pages
- Process comics with 500+ bubbles
- Queue system for concurrent processing (future)

---

## Technical Constraints

### TC-1: External Dependencies

- **Tesseract OCR** must be installed separately
- **Poppler** required for PDF processing
- **FFmpeg** required for video generation
- Application must detect missing dependencies and provide installation instructions

### TC-2: API Limitations

- **edge-tts:** Requires internet connection, no rate limiting documented
- **OpenAI TTS:** Rate limited by API quota (~$15/1M characters)
- Must implement fallback if API fails

### TC-3: File Formats

- Input: JPG, PNG, PDF (CBZ support planned)
- Output: MP4 video (H.264 codec)
- Audio: MP3 (edge-tts) or MP3 (OpenAI)

### TC-4: Language Support

- Primary: Czech (cs-CZ)
- Secondary: English (en-US)
- OCR must support both languages
- TTS must have voices for both languages

---

## Edge Cases and Error Handling

### EC-1: Input Validation

- **Empty file:** Show error "File is empty or corrupted"
- **Unsupported format:** Show error "Format not supported. Use JPG, PNG, or PDF"
- **Password-protected PDF:** Show error "Encrypted PDFs are not supported"
- **Very large file (>100MB):** Warn user, allow cancellation

### EC-2: Detection Failures

- **No bubbles detected:** Offer manual configuration adjustment
- **Too many bubbles (>100):** Warn and suggest filtering
- **Overlapping bubbles:** Merge overlapping detections
- **Non-standard bubble shapes:** Best effort, may fail

### EC-3: OCR Failures

- **No text extracted:** Suggest adjusting image resolution
- **Low confidence (<50%):** Flag for manual review
- **Garbled text:** Offer editing before TTS
- **Special characters:** Handle Czech diacritics properly

### EC-4: TTS Failures

- **Network error (edge-tts):** Retry 3 times, then fail gracefully
- **API quota exceeded (OpenAI):** Suggest switching to edge-tts
- **Unsupported voice:** List available voices
- **Very long text (>1000 chars):** Split into chunks

### EC-5: Video Generation Failures

- **Missing FFmpeg:** Provide installation instructions
- **Insufficient disk space:** Check before starting, warn user
- **Encoding error:** Retry with different codec settings
- **File too large (>1GB):** Warn user, offer lower quality option

---

## Data Model

### Comic

```python
@dataclass
class Comic:
    """Represents a loaded comic file."""
    file_path: str
    file_format: str  # 'jpg', 'png', 'pdf'
    pages: List[Image]
    page_count: int
    metadata: Dict[str, Any]
```

### SpeechBubble

```python
@dataclass
class SpeechBubble:
    """Represents a detected speech bubble."""
    bbox: Tuple[int, int, int, int]  # (x1, y1, x2, y2)
    text: str
    confidence: float  # 0.0 to 1.0
    page_number: int
    reading_order: int
```

### AudioSegment

```python
@dataclass
class AudioSegment:
    """Represents a generated audio file."""
    text: str
    audio_path: str
    duration: float  # seconds
    voice: str
```

### ProcessingResult

```python
@dataclass
class ProcessingResult:
    """Result of comic processing."""
    input_path: str
    output_path: str
    bubble_count: int
    total_duration: float
    success: bool
    errors: List[str]
    warnings: List[str]
```

---

## Success Metrics

### Accuracy Metrics

- Bubble detection precision: >85%
- OCR accuracy: >90%
- Reading order accuracy: >95%

### Performance Metrics

- Single page processing time: <30s
- 10-page PDF processing time: <2min
- Video generation time: <30s per minute of video

### User Experience Metrics

- Task completion rate: >90%
- User satisfaction: >4.0/5.0
- Error recovery rate: >80%

### Quality Metrics

- Code coverage: >80%
- Critical bugs per release: <5
- API uptime: >99%

---

## Open Questions

1. **Q:** Should we support batch processing of multiple comics?
   **A:** Yes, as a future feature (Phase 2)

2. **Q:** Should users be able to manually correct bubble detections?
   **A:** Yes, planned for Phase 2

3. **Q:** Should we support other comic formats (CBZ, CBR)?
   **A:** Yes, CBZ in Phase 2, CBR later

4. **Q:** What video quality options should we offer?
   **A:** 720p (default), 1080p, 480p

5. **Q:** Should we support other languages beyond Czech and English?
   **A:** Focus on Czech and English first, add more later

---

_This specification is version 1.0 and will be updated as requirements evolve._

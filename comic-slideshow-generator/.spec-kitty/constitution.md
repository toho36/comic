# Comic Slideshow Generator - Project Constitution

## Project Rules

### Programming Language
- **Language:** Python 3.10+
- **Type Hints:** Required for all functions
- **Style Guide:** PEP 8 with Black formatter
- **Documentation:** Docstrings for all public modules, classes, and functions

### Architecture Principles
- **Modular Design:** Separate components for detection, extraction, TTS, and video generation
- **Dependency Injection:** Use dependency injection for TTS engines and UI frameworks
- **Error Handling:** Comprehensive exception handling with user-friendly error messages
- **Configuration:** Environment variables + config file support
- **Logging:** Structured logging with appropriate levels (DEBUG, INFO, WARNING, ERROR)

### Technology Stack
- **Computer Vision:** OpenCV 4.8+ for image processing and bubble detection
- **OCR:** pytesseract 0.3+ with Tesseract engine
- **PDF Processing:** pdf2image 1.16+ with Poppler
- **Video Generation:** moviepy 1.0+ with FFmpeg
- **TTS (Free):** edge-tts 6.1+ (Microsoft Edge)
- **TTS (Paid):** OpenAI API 1.0+ (optional)
- **UI Framework:** Streamlit 1.28+ (primary), Gradio 4.0+ (alternative), PyQt6 6.5+ (desktop)

### Code Organization
```
comic-slideshow-generator/
├── src/
│   ├── detection/      # Bubble detection
│   ├── extraction/     # Text extraction (OCR)
│   ├── tts/           # Text-to-speech engines
│   ├── video/         # Video generation
│   ├── preprocessing/ # File loading and conversion
│   └── ui/            # Streamlit/Gradio/PyQt interfaces
├── tests/
├── examples/
└── config/
```

## AI Agent Instructions

### Code Style
- Write self-documenting code with descriptive variable names
- Add type hints to all function signatures
- Include docstrings with: description, args, returns, raises, examples
- Use dataclasses for configuration objects
- Prefer composition over inheritance
- Keep functions under 50 lines when possible

### Error Handling
- Never suppress exceptions silently
- Create custom exception classes for domain-specific errors
- Provide context in error messages (what failed, why, how to fix)
- Log all errors with stack traces in DEBUG mode
- Return user-friendly error messages to UI

### Performance Considerations
- Use generators for large file processing
- Implement progress tracking for long-running operations
- Cache intermediate results when appropriate
- Use async I/O for network operations (TTS API calls)
- Optimize OpenCV operations with vectorized operations

### Testing Requirements
- **Test Framework:** pytest with pytest-asyncio
- **Coverage:** Minimum 80% code coverage
- **Unit Tests:** Test all functions in isolation
- **Integration Tests:** Test end-to-end workflows
- **Mocking:** Mock external dependencies (TTS API, file I/O)
- **Fixtures:** Use pytest fixtures for common test data

### Documentation
- Maintain README.md with quick start guide
- Document all configuration options
- Provide examples for common use cases
- Keep changelog of breaking changes
- Include troubleshooting section

## Development Standards

### Git Workflow
- **Main Branch:** `main` (production-ready code only)
- **Feature Branches:** `feature/description`, `fix/description`, `docs/description`
- **Commit Messages:** Conventional Commits format (feat:, fix:, docs:, etc.)
- **Pull Requests:** Required for all changes, must pass CI tests

### Code Review Checklist
- [ ] Code follows PEP 8 style guide
- [ ] All functions have type hints and docstrings
- [ ] Tests cover new functionality (80%+ coverage)
- [ ] Error handling is comprehensive
- [ ] Logging is appropriate
- [ ] Documentation is updated
- [ ] No hardcoded values (use config)

### Security Considerations
- **API Keys:** Never commit API keys to repository
- **Input Validation:** Validate all user inputs (files, parameters)
- **File Operations:** Sanitize file paths to prevent directory traversal
- **Dependency Scanning:** Regular security audits of dependencies
- **Rate Limiting:** Implement rate limiting for API calls

## Testing Standards

### Unit Testing
```python
# Example test structure
def test_bubble_detection_min_area():
    """Test that bubbles below minimum area are filtered out."""
    detector = BubbleDetector(min_area=500)
    image = load_test_image("test_comic.jpg")
    bubbles = detector.detect(image)
    assert all(b.area >= 500 for b in bubbles)
```

### Integration Testing
```python
def test_end_to_end_comic_processing():
    """Test complete workflow from comic to video."""
    processor = ComicProcessor(tts_engine='edge')
    result = processor.process('test.pdf', 'output.mp4')
    assert os.path.exists('output.mp4')
    assert result.bubble_count > 0
```

### Test Data
- Include sample comics in `/tests/fixtures/`
- Use synthetic test data for reproducibility
- Mock TTS API responses to avoid network calls

## Configuration Management

### Environment Variables
```bash
# Required
OPENAI_API_KEY=sk-...  # Optional, for paid TTS

# Optional (with defaults)
TESSERACT_CMD=tesseract
POPPLER_PATH=/usr/bin/poppler
FFMPEG_PATH=/usr/bin/ffmpeg

# Application settings
LOG_LEVEL=INFO
CACHE_DIR=/tmp/comic-cache
OUTPUT_DIR=./output
```

### Config File Structure
```python
@dataclass
class DetectionConfig:
    min_bubble_area: int = 500
    ocr_confidence: int = 60
    blur_kernel: int = 5

@dataclass
class TTSConfig:
    engine: str = 'edge'  # 'edge' or 'openai'
    voice: str = 'cs-CZ-AntoninNeural'
    rate: float = 1.0
    pitch: int = 0

@dataclass
class VideoConfig:
    fps: int = 24
    codec: str = 'libx264'
    bitrate: str = '5M'
```

## Acceptance Criteria

All features must meet these criteria before being considered complete:

### Functionality
- [ ] Detects speech bubbles in JPG/PNG images with >85% accuracy
- [ ] Extracts text from bubbles with >90% OCR accuracy
- [ ] Converts comic pages from PDF with proper resolution
- [ ] Generates synchronized video with audio and images
- [ ] Supports Czech language TTS with at least 2 voice options

### Usability
- [ ] Streamlit UI is intuitive and responsive
- [ ] Progress indicators for long-running operations
- [ ] Clear error messages with actionable suggestions
- [ ] Configuration options are documented and discoverable

### Performance
- [ ] Processes single comic page in <30 seconds
- [ ] Handles PDFs with up to 50 pages without memory issues
- [ ] Video generation completes in reasonable time (<2 min for 10 pages)

### Reliability
- [ ] Gracefully handles missing dependencies with clear instructions
- [ ] Recovers from failed TTS API calls with retries
- [ ] Validates inputs before processing
- [ ] Cleans up temporary files after processing

## Non-Functional Requirements

### Scalability
- Support batch processing of multiple comics
- Handle large files (>100MB PDFs)
- Process comics with 100+ pages

### Maintainability
- Modular architecture for easy component replacement
- Clear separation of concerns
- Comprehensive test suite
- Well-documented codebase

### Extensibility
- Plugin system for adding new TTS engines
- Configurable detection algorithms
- Support for new file formats (CBZ, CBR)

### Accessibility
- Support for multiple languages
- UI works with screen readers
- Keyboard navigation support

## Success Metrics

- **Accuracy:** >85% bubble detection rate on test set
- **Performance:** <30s processing time per page
- **Coverage:** >80% test coverage
- **User Satisfaction:** >4.0/5.0 average rating
- **Bug Rate:** <5 critical bugs per release

---

*This constitution governs all development decisions for the Comic Slideshow Generator project. All contributors must adhere to these standards.*

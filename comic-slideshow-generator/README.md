---
title: Comic Slideshow Generator
emoji: 🎭
colorFrom: blue
colorTo: purple
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: mit
---

# 🎭 Comic Slideshow Generator

Transform static comics into animated video presentations with synchronized speech synthesis.

## ✨ Features

- 🎯 **Automatic Speech Bubble Detection** - Uses OpenCV to detect speech bubbles
- 📝 **Text Extraction** - OCR with Tesseract (multiple languages)
- 🔊 **Text-to-Speech** - Edge TTS (free) or OpenAI TTS (premium)
- 🎬 **Video Generation** - Creates smooth zoom animations with MoviePy
- 📄 **Multi-format Support** - JPG, PNG, and PDF comics
- ⚙️ **Configurable** - Adjustable detection, OCR, and video settings

## 🚀 Usage

1. **Upload a comic** (PDF, JPG, or PNG)
2. **Configure settings** in the sidebar:
   - Choose TTS provider (Edge = free, OpenAI = premium)
   - Select voice and language
   - Adjust bubble detection sensitivity
   - Set video quality
3. **Click "Generate Slideshow"** to create your video
4. **Download** the resulting MP4 file

## ⚙️ System Requirements

This Space uses the following system dependencies:
- Tesseract OCR
- FFmpeg
- Poppler (for PDF support)

## 📊 Performance

| Operation | Time |
|-----------|-------|
| Bubble Detection | ~100ms per page |
| Text Extraction | ~200ms per bubble |
| TTS Generation | ~500ms per sentence |
| Video Rendering | ~2s per second of video |

## 🤝 Technical Details

- **Framework**: Streamlit
- **Computer Vision**: OpenCV
- **OCR**: Tesseract
- **TTS**: Edge TTS / OpenAI TTS
- **Video**: MoviePy
- **Config**: Pydantic

## 📄 License

MIT License

---

Made with ❤️ and AI

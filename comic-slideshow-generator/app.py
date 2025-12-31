import streamlit as st
import asyncio
from pathlib import Path
from io import BytesIO
import tempfile
import os

# Page configuration
st.set_page_config(
    page_title="Comic Slideshow Generator",
    page_icon="🎭",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        text-align: center;
        padding: 2rem 0;
    }
    .feature-card {
        background: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 1rem 0;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown("""
<h1 class="main-header">🎭 Comic Slideshow Generator</h1>
<p style="text-align: center; color: #666; margin-bottom: 2rem;">
    Transform static comics into animated video presentations with synchronized speech synthesis
</p>
""", unsafe_allow_html=True)

# Sidebar configuration
with st.sidebar:
    st.header("⚙️ Configuration")
    
    # TTS Provider
    tts_provider = st.selectbox(
        "TTS Provider",
        ["edge", "openai"],
        help="Edge TTS is free, OpenAI TTS requires API key but offers higher quality"
    )
    
    # OpenAI API Key (if selected)
    if tts_provider == "openai":
        openai_api_key = st.text_input(
            "OpenAI API Key",
            type="password",
            help="Enter your OpenAI API key for premium TTS"
        )
    else:
        openai_api_key = None
    
    # TTS Voice
    st.subheader("Voice Settings")
    if tts_provider == "edge":
        voice_options = [
            "en-US-AriaNeural",
            "en-US-GuyNeural",
            "en-GB-SoniaNeural",
            "en-GB-RyanNeural",
            "cs-CZ-VlastaNeural",
            "de-DE-KatjaNeural",
            "fr-FR-DeniseNeural",
            "es-ES-ElviraNeural"
        ]
        selected_voice = st.selectbox("Voice", voice_options)
    else:
        voice_options = ["alloy", "echo", "fable", "onyx", "nova", "shimmer"]
        selected_voice = st.selectbox("Voice", voice_options)
    
    # Detection Settings
    st.subheader("Detection Settings")
    min_bubble_area = st.slider(
        "Minimum Bubble Area",
        min_value=100,
        max_value=2000,
        value=500,
        step=100,
        help="Adjust to improve bubble detection (higher = fewer false positives)"
    )
    
    # OCR Settings
    st.subheader("OCR Settings")
    ocr_languages = st.multiselect(
        "OCR Languages",
        ["eng", "ces", "deu", "fra", "spa"],
        default=["eng", "ces"],
        help="Select languages for text recognition"
    )
    
    # Video Settings
    st.subheader("Video Settings")
    video_fps = st.slider(
        "Frame Rate (FPS)",
        min_value=12,
        max_value=30,
        value=24,
        step=6,
        help="Higher FPS = smoother but larger video files"
    )
    
    # Info
    st.info("""
    💡 **Tips**:
    - Use Edge TTS for free, OpenAI for premium quality
    - Adjust bubble area based on your comic resolution
    - Higher FPS produces smoother but larger videos
    - Enable multiple OCR languages for multilingual comics
    """)

# Main content
st.header("📤 Upload Comic")

# File upload
uploaded_file = st.file_uploader(
    "Upload a comic (PDF, JPG, PNG)",
    type=["pdf", "jpg", "jpeg", "png"],
    help="Upload a single page or multi-page comic PDF"
)

if uploaded_file:
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("📄 Original")
        if uploaded_file.type in ["application/pdf"]:
            st.info("PDF uploaded - will extract pages for processing")
            st.write(f"File: {uploaded_file.name}")
            st.write(f"Size: {uploaded_file.size / 1024:.1f} KB")
        else:
            st.image(uploaded_file, use_column_width=True)
            st.write(f"File: {uploaded_file.name}")
            st.write(f"Size: {uploaded_file.size / 1024:.1f} KB")
    
    with col2:
        st.subheader("⚙️ Settings Summary")
        st.markdown(f"""
        - **TTS Provider**: {tts_provider.upper()}
        - **Voice**: {selected_voice}
        - **Bubble Area**: {min_bubble_area}px²
        - **Languages**: {', '.join(ocr_languages).upper()}
        - **FPS**: {video_fps}
        """)
    
    # Process button
    st.divider()
    
    col1, col2, col3 = st.columns([1, 2, 1])
    
    with col2:
        process_button = st.button(
            "🚀 Generate Slideshow",
            type="primary",
            use_container_width=True
        )

# Processing logic
if uploaded_file and process_button:
    try:
        # Create temporary directory
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            
            # Save uploaded file
            file_path = temp_path / uploaded_file.name
            with open(file_path, "wb") as f:
                f.write(uploaded_file.getbuffer())
            
            # Show progress
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            status_text.text("Initializing...")
            progress_bar.progress(10)
            
            # Import processor (lazy load for better startup)
            from src.processor import ComicProcessor
            from src.config import AppConfig, DetectionConfig, OCRConfig, TTSConfig, VideoConfig
            
            # Create configuration
            config = AppConfig(
                detection=DetectionConfig(
                    min_bubble_area=min_bubble_area,
                    blur_kernel=5,
                    threshold_block_size=11,
                    min_aspect_ratio=0.5,
                    max_aspect_ratio=3.0
                ),
                ocr=OCRConfig(
                    languages=ocr_languages,
                    oem=3,
                    psm=7,
                    min_confidence=0.6
                ),
                tts=TTSConfig(
                    provider=tts_provider,
                    voice=selected_voice,
                    api_key=openai_api_key,
                    rate="+0%",
                    volume="+0%"
                ),
                video=VideoConfig(
                    fps=video_fps,
                    bubble_zoom_duration=1.0,
                    transition_duration=0.5,
                    output_codec="libx264",
                    crf_quality=23
                )
            )
            
            status_text.text("Detecting bubbles...")
            progress_bar.progress(30)
            
            # Create processor and process
            processor = ComicProcessor(config)
            
            status_text.text("Extracting text...")
            progress_bar.progress(50)
            
            output_path = temp_path / "output.mp4"
            
            status_text.text("Generating speech...")
            progress_bar.progress(70)
            
            # Run async processing
            result = asyncio.run(
                processor.process_comic(
                    comic_path=file_path,
                    output_path=output_path
                )
            )
            
            status_text.text("Rendering video...")
            progress_bar.progress(90)
            
            # Read output video
            with open(output_path, "rb") as f:
                video_bytes = f.read()
            
            progress_bar.progress(100)
            status_text.text("✅ Complete!")
            
            # Display results
            st.success(f"✅ Slideshow generated successfully!")
            
            # Stats
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Bubbles Detected", result.total_bubbles)
            
            with col2:
                st.metric("Total Duration", f"{result.total_duration:.1f}s")
            
            with col3:
                st.metric("Pages Processed", result.pages_processed)
            
            with col4:
                st.metric("Video Size", f"{len(video_bytes) / (1024*1024):.1f} MB")
            
            # Download button
            st.divider()
            st.download_button(
                label="📥 Download Video",
                data=video_bytes,
                file_name=f"comic_slideshow_{uploaded_file.stem}.mp4",
                mime="video/mp4",
                use_container_width=True
            )
            
    except Exception as e:
        st.error(f"❌ Error processing comic: {str(e)}")
        st.info("Please try again with a different comic or adjust the settings")

# Examples section
st.divider()
st.header("📖 How It Works")

with st.expander("View the Pipeline"):
    st.markdown("""
    ### 1. 🎯 Bubble Detection
    - Uses OpenCV to detect speech bubbles in comic pages
    - Applies adaptive thresholding and contour detection
    - Filters by size and aspect ratio
    
    ### 2. 📝 Text Extraction (OCR)
    - Uses Tesseract OCR to read text from detected bubbles
    - Supports multiple languages
    - Filters by confidence score
    
    ### 3. 🔊 Text-to-Speech
    - Converts extracted text to speech
    - Edge TTS: Free, good quality
    - OpenAI TTS: Premium, excellent quality
    
    ### 4. 🎬 Video Generation
    - Creates smooth zoom animations on each bubble
    - Synchronizes speech with video
    - Exports as MP4 video file
    """)

# Footer
st.divider()
st.markdown("""
<div style="text-align: center; color: #888; padding: 2rem 0;">
    <p>🎭 Comic Slideshow Generator | Powered by OpenCV, Tesseract, Edge TTS & MoviePy</p>
    <p style="font-size: 0.9em;">Made with ❤️ and AI</p>
</div>
""", unsafe_allow_html=True)


"""
Unit tests for OCR engine
Tests text extraction using pytesseract
"""
import pytest
import numpy as np
import cv2
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from src.text_extractor import OCREngine, ImagePreprocessor, TextExtractionResult
from src.config import OCRConfig


@pytest.fixture
def sample_config():
    """Create sample OCR configuration"""
    return OCRConfig(
        engine="tesseract",
        languages=["eng"],
        oem=3,
        psm=7,
        min_confidence=0.6
    )


@pytest.fixture
def ocr_engine(sample_config):
    """Create OCR engine instance"""
    return OCREngine(sample_config)


@pytest.fixture
def sample_image_with_text():
    """
    Create a synthetic image with text
    
    Returns:
        Image array with text drawn on it
    """
    img = np.ones((200, 400, 3), dtype=np.uint8) * 255
    
    # Draw some text
    text = "Hello World"
    font = cv2.FONT_HERSHEY_SIMPLEX
    cv2.putText(img, text, (50, 100), font, 1, (0, 0, 0), 2)
    
    return img


class TestImagePreprocessor:
    """Tests for ImagePreprocessor class"""
    
    def test_enhance_contrast(self):
        """Test contrast enhancement"""
        # Create low contrast image
        img = np.ones((100, 100, 3), dtype=np.uint8) * 128
        
        enhanced = ImagePreprocessor.enhance_contrast(img)
        
        assert enhanced.shape == img.shape
    
    def test_resize_for_ocr(self):
        """Test image resizing"""
        img = np.ones((100, 100, 3), dtype=np.uint8)
        
        resized = ImagePreprocessor.resize_for_ocr(img, scale=2.0)
        
        assert resized.shape[0] == 200  # Height doubled
        assert resized.shape[1] == 200  # Width doubled
    
    def test_binarize(self):
        """Test image binarization"""
        # Create grayscale image with varying values
        img = np.random.randint(0, 256, (100, 100), dtype=np.uint8)
        
        binary = ImagePreprocessor.binarize(img)
        
        # Binary image should only have 2 values
        unique_values = np.unique(binary)
        assert len(unique_values) <= 2


class TestOCREngine:
    """Tests for OCREngine class"""
    
    def test_engine_initialization(self, sample_config):
        """Test OCR engine initialization"""
        engine = OCREngine(sample_config)
        assert engine.config == sample_config
    
    @patch('src.text_extractor.pytesseract.image_to_string')
    def test_extract_text_basic(self, mock_ocr, ocr_engine, sample_image_with_text):
        """Test basic text extraction"""
        mock_ocr.return_value = "Hello World"
        
        text = ocr_engine.extract_text(sample_image_with_text, (50, 50, 300, 100))
        
        assert text == "Hello World"
        mock_ocr.assert_called_once()
    
    @patch('src.text_extractor.pytesseract.image_to_string')
    def test_extract_text_cleans_result(self, mock_ocr, ocr_engine):
        """Test that extracted text is cleaned"""
        mock_ocr.return_value = "Hello    World\n\n  Test"
        
        text = ocr_engine.extract_text(np.ones((100, 100, 3), dtype=np.uint8), (0, 0, 100, 100))
        
        # Should normalize whitespace
        assert "  " not in text
        assert "\n\n" not in text
    
    @patch('src.text_extractor.pytesseract.image_to_string')
    def test_extract_text_empty_result(self, mock_ocr, ocr_engine):
        """Test extraction with empty result"""
        mock_ocr.return_value = ""
        
        text = ocr_engine.extract_text(np.ones((100, 100, 3), dtype=np.uint8), (0, 0, 100, 100))
        
        assert text == ""
    
    @patch('src.text_extractor.pytesseract.image_to_data')
    def test_extract_with_confidence(self, mock_data, ocr_engine):
        """Test extraction with confidence scores"""
        mock_data.return_value = {
            'text': ['Hello', 'World'],
            'conf': ['95', '90']
        }
        
        result = ocr_engine.extract_with_confidence(
            np.ones((100, 100, 3), dtype=np.uint8),
            (0, 0, 100, 100)
        )
        
        assert isinstance(result, TextExtractionResult)
        assert result.text == "Hello World"
        assert result.confidence > 0
    
    def test_get_language_string(self, ocr_engine):
        """Test language string generation"""
        config = OCRConfig(languages=["eng", "ces"])
        engine = OCREngine(config)
        
        lang_string = engine.config.get_language_string()
        
        assert lang_string == "eng+ces"
    
    def test_get_tesseract_config(self, ocr_engine):
        """Test Tesseract config string generation"""
        config_str = ocr_engine.config.get_tesseract_config()
        
        assert "--oem 3" in config_str
        assert "--psm 7" in config_str


class TestTextExtractionResult:
    """Tests for TextExtractionResult dataclass"""
    
    def test_result_properties(self):
        """Test result property calculations"""
        result = TextExtractionResult(
            text="Hello",
            confidence=0.8,
            bbox=(0, 0, 100, 100)
        )
        
        assert result.text == "Hello"
        assert result.confidence == 0.8
        assert result.bbox == (0, 0, 100, 100)
    
    def test_is_valid_with_good_result(self):
        """Test is_valid with good result"""
        result = TextExtractionResult(
            text="Hello World",
            confidence=0.8,
            bbox=(0, 0, 100, 100)
        )
        
        assert result.is_valid is True
    
    def test_is_valid_with_empty_text(self):
        """Test is_valid with empty text"""
        result = TextExtractionResult(
            text="",
            confidence=0.8,
            bbox=(0, 0, 100, 100)
        )
        
        assert result.is_valid is False
    
    def test_is_valid_with_low_confidence(self):
        """Test is_valid with low confidence"""
        result = TextExtractionResult(
            text="Hello",
            confidence=0.0,
            bbox=(0, 0, 100, 100)
        )
        
        assert result.is_valid is False


class TestOCREngineEdgeCases:
    """Tests for edge cases in OCR"""
    
    @patch('src.text_extractor.pytesseract.image_to_string')
    def test_tesseract_not_installed_error(self, mock_ocr, sample_config):
        """Test error handling when Tesseract is not installed"""
        mock_ocr.side_effect = Exception("tesseract is not installed")
        
        engine = OCREngine(sample_config)
        
        with pytest.raises(RuntimeError) as exc_info:
            engine.extract_text(np.ones((100, 100, 3), dtype=np.uint8), (0, 0, 100, 100))
        
        assert "Tesseract" in str(exc_info.value)
    
    @patch('src.text_extractor.pytesseract.image_to_string')
    def test_extract_batch(self, mock_ocr, ocr_engine):
        """Test batch text extraction"""
        mock_ocr.return_value = "Test"
        
        img = np.ones((200, 200, 3), dtype=np.uint8)
        bboxes = [(0, 0, 100, 100), (100, 100, 100, 100)]
        
        results = ocr_engine.extract_batch(img, bboxes)
        
        assert len(results) == 2
        assert all(r == "Test" for r in results)
    
    def test_clean_text_removes_artifacts(self, ocr_engine):
        """Test text cleaning removes OCR artifacts"""
        dirty_text = "Hello|___World___123"
        
        cleaned = ocr_engine._clean_text(dirty_text)
        
        # Should remove pipes and underscores
        assert "|" not in cleaned
        assert "___" not in cleaned
    
    def test_clean_text_normalizes_whitespace(self, ocr_engine):
        """Test text cleaning normalizes whitespace"""
        dirty_text = "Hello     World\n\n  Test"
        
        cleaned = ocr_engine._clean_text(dirty_text)
        
        # Should normalize to single spaces
        assert "  " not in cleaned
        assert cleaned == "Hello World Test"


@pytest.mark.integration
class TestOCRIntegration:
    """Integration tests (require Tesseract to be installed)"""
    
    @pytest.mark.skipif(
        not Path("/usr/bin/tesseract").exists() and not Path("/usr/local/bin/tesseract").exists(),
        reason="Tesseract not installed"
    )
    def test_real_ocr_extraction(self, ocr_engine, sample_image_with_text):
        """Test real OCR with Tesseract"""
        text = ocr_engine.extract_text(sample_image_with_text, (50, 50, 300, 100))
        
        # Should extract some text
        assert isinstance(text, str)
        assert len(text) > 0

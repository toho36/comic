"""
OCR text extraction using pytesseract
Extracts text from detected speech bubbles
"""
import pytesseract
from PIL import Image
import numpy as np
from typing import Tuple, Optional, List
from dataclasses import dataclass
import re
from src.config import OCRConfig


@dataclass
class TextExtractionResult:
    """Result of text extraction"""
    text: str
    confidence: float
    bbox: Tuple[int, int, int, int]
    
    @property
    def is_valid(self) -> bool:
        """Check if extraction was successful"""
        return len(self.text.strip()) > 0 and self.confidence > 0


class ImagePreprocessor:
    """Preprocesses images for better OCR results"""
    
    @staticmethod
    def denoise(image: np.ndarray) -> np.ndarray:
        """
        Remove noise from image
        
        Args:
            image: Input image
        
        Returns:
            Denoised image
        """
        return cv2.fastNlMeansDenoisingColored(image, None, 10, 10, 7, 21)
    
    @staticmethod
    def binarize(image: np.ndarray) -> np.ndarray:
        """
        Convert image to binary (black and white)
        
        Args:
            image: Grayscale input image
        
        Returns:
            Binary image
        """
        _, binary = cv2.threshold(
            image,
            0,
            255,
            cv2.THRESH_BINARY + cv2.THRESH_OTSU
        )
        return binary
    
    @staticmethod
    def enhance_contrast(image: np.ndarray) -> np.ndarray:
        """
        Enhance image contrast using CLAHE
        
        Args:
            image: Input image
        
        Returns:
            Enhanced image
        """
        if len(image.shape) == 3:
            gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        else:
            gray = image
        
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        enhanced = clahe.apply(gray)
        
        return enhanced
    
    @staticmethod
    def resize_for_ocr(image: np.ndarray, scale: float = 2.0) -> np.ndarray:
        """
        Resize image to improve OCR accuracy
        
        Args:
            image: Input image
            scale: Scale factor
        
        Returns:
            Resized image
        """
        height, width = image.shape[:2]
        new_size = (int(width * scale), int(height * scale))
        return cv2.resize(image, new_size, interpolation=cv2.INTER_CUBIC)


class OCREngine:
    """OCR engine for text extraction from speech bubbles"""
    
    def __init__(self, config: Optional[OCRConfig] = None):
        """
        Initialize OCR engine
        
        Args:
            config: OCR configuration
        """
        self.config = config or OCRConfig()
        self.preprocessor = ImagePreprocessor()
    
    def extract_text(
        self,
        image: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> str:
        """
        Extract text from a region of interest
        
        Args:
            image: Full image (BGR format)
            bbox: Bounding box (x, y, width, height)
        
        Returns:
            Extracted text
        
        Raises:
            RuntimeError: If Tesseract is not available
        """
        x, y, w, h = bbox
        
        # Extract region of interest
        roi = image[y:y+h, x:x+w]
        
        # Preprocess for better OCR
        processed = self._preprocess_for_ocr(roi)
        
        # Convert to PIL Image
        pil_img = Image.fromarray(processed)
        
        # Perform OCR
        try:
            text = pytesseract.image_to_string(
                pil_img,
                lang=self.config.get_language_string(),
                config=self.config.get_tesseract_config()
            )
        except Exception as e:
            if "tesseract is not installed" in str(e).lower():
                raise RuntimeError(
                    "Tesseract OCR is not installed. "
                    "Please install it from https://github.com/UB-Mannheim/tesseract/wiki"
                )
            raise
        
        # Clean text
        cleaned_text = self._clean_text(text)
        
        return cleaned_text
    
    def extract_with_confidence(
        self,
        image: np.ndarray,
        bbox: Tuple[int, int, int, int]
    ) -> TextExtractionResult:
        """
        Extract text with confidence score
        
        Args:
            image: Full image
            bbox: Bounding box
        
        Returns:
            TextExtractionResult with confidence
        """
        x, y, w, h = bbox
        roi = image[y:y+h, x:x+w]
        processed = self._preprocess_for_ocr(roi)
        pil_img = Image.fromarray(processed)
        
        # Get detailed OCR data
        try:
            data = pytesseract.image_to_data(
                pil_img,
                lang=self.config.get_language_string(),
                config=self.config.get_tesseract_config(),
                output_type=pytesseract.Output.DICT
            )
        except Exception as e:
            if "tesseract is not installed" in str(e).lower():
                raise RuntimeError(
                    "Tesseract OCR is not installed. "
                    "Please install it from https://github.com/UB-Mannheim/tesseract/wiki"
                )
            raise
        
        # Extract text and calculate average confidence
        texts = []
        confidences = []
        
        for i, text in enumerate(data['text']):
            conf = int(data['conf'][i])
            if conf > 0:  # Valid text
                texts.append(text)
                confidences.append(conf / 100.0)  # Convert to 0-1 range
        
        full_text = ' '.join(texts)
        avg_confidence = sum(confidences) / len(confidences) if confidences else 0.0
        
        # Filter by minimum confidence
        if avg_confidence < self.config.min_confidence:
            full_text = ""
        
        cleaned_text = self._clean_text(full_text)
        
        return TextExtractionResult(
            text=cleaned_text,
            confidence=avg_confidence,
            bbox=bbox
        )
    
    def extract_batch(
        self,
        image: np.ndarray,
        bboxes: List[Tuple[int, int, int, int]]
    ) -> List[str]:
        """
        Extract text from multiple regions
        
        Args:
            image: Full image
            bboxes: List of bounding boxes
        
        Returns:
            List of extracted texts
        """
        results = []
        for bbox in bboxes:
            try:
                text = self.extract_text(image, bbox)
                results.append(text)
            except Exception as e:
                print(f"Error extracting text from {bbox}: {e}")
                results.append("")
        
        return results
    
    def _preprocess_for_ocr(self, roi: np.ndarray) -> np.ndarray:
        """
        Apply preprocessing pipeline for OCR
        
        Args:
            roi: Region of interest
        
        Returns:
            Preprocessed image
        """
        # Convert to grayscale if needed
        if len(roi.shape) == 3:
            gray = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)
        else:
            gray = roi
        
        # Resize for better OCR
        resized = self.preprocessor.resize_for_ocr(gray, scale=2.0)
        
        # Enhance contrast
        enhanced = self.preprocessor.enhance_contrast(resized)
        
        # Binarize
        binary = self.preprocessor.binarize(enhanced)
        
        return binary
    
    def _clean_text(self, text: str) -> str:
        """
        Clean extracted text
        
        Args:
            text: Raw text from OCR
        
        Returns:
            Cleaned text
        """
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common OCR artifacts
        artifacts = [
            r'\|',  # Vertical bars
            r'_+',  # Underlines
            r'^\s*\d+\s*',  # Leading numbers
        ]
        
        for pattern in artifacts:
            text = re.sub(pattern, ' ', text)
        
        # Strip whitespace
        text = text.strip()
        
        return text
    
    def get_available_languages(self) -> List[str]:
        """
        Get list of available Tesseract languages
        
        Returns:
            List of language codes
        """
        try:
            return pytesseract.get_languages()
        except Exception:
            # Fallback to common languages
            return ['eng', 'ces', 'deu', 'fra', 'spa']


# Import cv2 for preprocessing
import cv2

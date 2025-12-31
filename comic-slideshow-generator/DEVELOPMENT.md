# 🛠️ Vývojářský Průvodce - AI Comic Slideshow Generator

Tento dokument je určen pro vývojáře, kteří chtějí přispívat k projektu nebo rozšiřovat jeho funkčnost.

---

## 📋 Obsah

- [Vývojové prostředí](#vývojové-prostředí)
- [Struktura projektu](#struktura-projektu)
- [Architektura kódu](#architektura-kódu)
- [Práce s moduly](#práce-s-moduly)
- [Testování](#testování)
- [Debugging](#debugging)
- [Přidávání funkcí](#přidávání-funkcí)
- [Klíčové konfigurace](#klíčové-konfigurace)
- [Best Practices](#best-practices)

---

## 🖥️ Vývojové prostředí

### Nastavení vývojáře

```bash
# 1. Klonujte repozitář
git clone https://github.com/vase-username/comic-slideshow-generator.git
cd comic-slideshow-generator

# 2. Vytvořte virtuální prostředí
python -m venv venv
source venv/bin/activate  # Linux/macOS
# nebo
venv\Scripts\activate  # Windows

# 3. Nainstalujte závislosti pro vývoj
pip install -r requirements.txt

# 4. Nainstalujte pre-commit hooks (volitelné)
pip install pre-commit
pre-commit install
```

### VS Code doporučená nastavení

Vytvořte `.vscode/settings.json`:

```json
{
  "python.defaultInterpreterPath": "./venv/bin/python",
  "python.linting.enabled": true,
  "python.linting.flake8Enabled": true,
  "python.formatting.provider": "black",
  "editor.formatOnSave": true,
  "python.testing.pytestEnabled": true,
  "python.testing.pytestArgs": ["tests/"]
}
```

---

## 📁 Struktura projektu

```
comic-slideshow-generator/
│
├── 📄 README.md                    # Hlavní dokumentace
├── 📄 DEVELOPMENT.md               # Tento soubor
├── 📄 requirements.txt             # Python závislosti
├── 📄 .env.example                 # Vzor konfigurace
├── 📄 .gitignore                   # Ignorované soubory
│
├── 📂 src/                         # Zdrojový kód
│   ├── 📄 __init__.py
│   ├── 📄 config.py                # Konfigurace aplikace
│   ├── 📄 main.py                  # Hlavní entry point
│   │
│   ├── 📂 detectors/               # Detekce bublin
│   │   ├── 📄 __init__.py
│   │   ├── 📄 bubble_detector.py   # OpenCV detekce
│   │   └── 📄 filters.py           # Filtry bublin
│   │
│   ├── 📂 ocr/                     # Extrakce textu
│   │   ├── 📄 __init__.py
│   │   ├── 📄 text_extractor.py    # pytesseract wrapper
│   │   └── 📄 preprocess.py        # Předzpracování obrazu
│   │
│   ├── 📂 tts/                     # Text-to-Speech
│   │   ├── 📄 __init__.py
│   │   ├── 📄 edge_tts.py          # edge-tts engine
│   │   ├── 📄 openai_tts.py        # OpenAI API engine
│   │   └── 📄 base.py              # Základní TTS interface
│   │
│   ├── 📂 video/                   # Video generace
│   │   ├── 📄 __init__.py
│   │   ├── 📄 slideshow.py         # moviepy wrapper
│   │   └── 📄 transitions.py       # Video přechody
│   │
│   ├── 📂 loaders/                 # Načítání souborů
│   │   ├── 📄 __init__.py
│   │   ├── 📄 image_loader.py      # JPG/PNG
│   │   └── 📄 pdf_loader.py        # PDF konverze
│   │
│   └── 📂 utils/                   # Pomocné funkce
│       ├── 📄 __init__.py
│       ├── 📄 logger.py            # Logging
│       └── 📄 validators.py        # Validace vstupu
│
├── 📂 ui/                          # Uživatelské rozhraní
│   ├── 📄 streamlit_app.py         # Streamlit UI
│   ├── 📄 gradio_app.py            # Gradio UI (volitelné)
│   └── 📄 pyqt_app.py              # PyQt6 UI (volitelné)
│
├── 📂 tests/                       # Testy
│   ├── 📄 __init__.py
│   ├── 📄 test_detector.py
│   ├── 📄 test_ocr.py
│   ├── 📄 test_tts.py
│   └── 📄 test_video.py
│
├── 📂 examples/                    # Příklady použití
│   ├── 📄 basic_usage.py
│   ├── 📄 batch_processing.py
│   └── 📄 custom_config.py
│
├── 📂 docs/                        # Dokumentace
│   ├── 📄 API.md                   # API reference
│   └── 📄 ALGORITHMS.md            # Popis algoritmů
│
├── 📂 assets/                      # Zdroje
│   ├── 📂 fonts/                   # Vlastní fonty
│   └── 📂 sample_comics/           # Vzorové komiksy
│
└── 📂 output/                      # Výstupy (vygenerované)
    ├── 📂 debug/                   # Debug obrázky
    └── 📂 videos/                  # Finální videa
```

---

## 🏗️ Architektura kódu

### Třídy a rozhraní

#### 1. `ComicProcessor` (Hlavní orchestrator)

```python
# src/main.py
class ComicProcessor:
    """Hlavní třída pro zpracování komiksů"""
    
    def __init__(self, config: Dict):
        self.detector = BubbleDetector(config)
        self.ocr = TextExtractor(config)
        self.tts = TTSEngine(config)
        self.video = SlideshowGenerator(config)
    
    def process(self, input_file: str, output_file: str) -> ProcessResult:
        """Celý pipeline od vstupu k výstupu"""
        # 1. Načtení
        images = self.load_images(input_file)
        
        # 2. Detekce bublin
        bubbles = self.detector.detect(images)
        
        # 3. Extrakce textu
        texts = self.ocr.extract(bubbles)
        
        # 4. TTS
        audio_files = self.tts.generate(texts)
        
        # 5. Video
        self.video.create(images, bubbles, audio_files, output_file)
        
        return ProcessResult(...)
```

#### 2. `BubbleDetector` (OpenCV wrapper)

```python
# src/detectors/bubble_detector.py
class BubbleDetector:
    """Detekce řečových bublin v komiksu"""
    
    def __init__(self, min_area: int = 500, 
                 aspect_ratio: float = 0.5):
        self.min_area = min_area
        self.aspect_ratio = aspect_ratio
    
    def detect(self, image: np.ndarray) -> List[Bubble]:
        """Detekuje bubliny v obraze"""
        # 1. Preprocessing
        processed = self._preprocess(image)
        
        # 2. Find contours
        contours = self._find_contours(processed)
        
        # 3. Filter by properties
        bubbles = self._filter_bubbles(contours, image)
        
        # 4. Sort by reading order
        bubbles = self._sort_by_reading_order(bubbles)
        
        return bubbles
    
    def _preprocess(self, image: np.ndarray) -> np.ndarray:
        """Gray → Blur → Threshold → Morphology"""
        gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        thresh = cv2.adaptiveThreshold(
            blur, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
            cv2.THRESH_BINARY_INV, 11, 2
        )
        # Morphological operations
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
        closed = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)
        return closed
    
    def _find_contours(self, image: np.ndarray) -> List:
        """Najde kontury v obraze"""
        contours, _ = cv2.findContours(
            image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
        )
        return contours
    
    def _filter_bubbles(self, contours: List, 
                       image: np.ndarray) -> List[Bubble]:
        """Filtruje kontury podle vlastností"""
        bubbles = []
        for cnt in contours:
            area = cv2.contourArea(cnt)
            if area < self.min_area:
                continue
            
            # Bounding box
            x, y, w, h = cv2.boundingRect(cnt)
            aspect = h / w if w > 0 else 0
            
            # Circular approximation (bubliny jsou oválné)
            perimeter = cv2.arcLength(cnt, True)
            circularity = 4 * np.pi * area / (perimeter ** 2)
            
            if (0.3 < circularity < 1.0 and 
                0.3 < aspect < 3.0):
                bubbles.append(Bubble(x, y, w, h, area))
        
        return bubbles
    
    def _sort_by_reading_order(self, bubbles: List[Bubble]) -> List[Bubble]:
        """Seřadí bubliny dle čtení (shora dolů, zleva doprava)"""
        return sorted(bubbles, key=lambda b: (b.y // 50, b.x))
```

#### 3. `TextExtractor` (OCR wrapper)

```python
# src/ocr/text_extractor.py
class TextExtractor:
    """Extrakce textu z bublin pomocí pytesseract"""
    
    def __init__(self, confidence_threshold: int = 60,
                 lang: str = 'ces'):
        self.confidence_threshold = confidence_threshold
        self.lang = lang
    
    def extract(self, bubbles: List[Bubble], 
                image: np.ndarray) -> List[ExtractedText]:
        """Extrahuje text z bublin"""
        results = []
        for bubble in bubbles:
            # Crop bubble region
            region = image[bubble.y:bubble.y+bubble.h, 
                          bubble.x:bubble.x+bubble.w]
            
            # OCR
            text, conf = self._ocr_region(region)
            
            if conf >= self.confidence_threshold and text.strip():
                results.append(ExtractedText(
                    text=text,
                    confidence=conf,
                    bubble=bubble
                ))
        
        return results
    
    def _ocr_region(self, region: np.ndarray) -> Tuple[str, float]:
        """Spustí OCR na regionu"""
        # Config for comic text
        config = f'--psm 6 -l {self.lang}'
        data = pytesseract.image_to_data(
            region, config=config, output_type=pytesseract.Output.DICT
        )
        
        # Get confidence
        confidences = [int(c) for c in data['conf'] if c != '-1']
        avg_conf = sum(confidences) / len(confidences) if confidences else 0
        
        # Get text
        text = ' '.join([t for t in data['text'] if t.strip()])
        
        return text, avg_conf
```

#### 4. `TTSEngine` (TTS interface)

```python
# src/tts/edge_tts.py
class EdgeTTSEngine:
    """edge-tts wrapper pro bezplatné TTS"""
    
    def __init__(self, voice: str = 'cs-CZ-AntoninNeural'):
        self.voice = voice
    
    def generate(self, texts: List[str]) -> List[str]:
        """Generuje audio soubory z textů"""
        import edge_tts
        
        audio_files = []
        for i, text in enumerate(texts):
            output_path = f"temp_audio_{i}.mp3"
            
            async def _generate():
                communicate = edge_tts.Communicate(text, self.voice)
                await communicate.save(output_path)
            
            asyncio.run(_generate())
            audio_files.append(output_path)
        
        return audio_files

# src/tts/openai_tts.py (volitelné)
class OpenAITTSEngine:
    """OpenAI API TTS pro vyšší kvalitu"""
    
    def __init__(self, api_key: str, model: str = 'gpt-4o-mini-tts'):
        self.client = OpenAI(api_key=api_key)
        self.model = model
    
    def generate(self, texts: List[str]) -> List[str]:
        """Generuje audio soubory pomocí OpenAI"""
        audio_files = []
        for i, text in enumerate(texts):
            response = self.client.audio.speech.create(
                model=self.model,
                voice='alloy',
                input=text
            )
            output_path = f"temp_audio_{i}.mp3"
            response.stream_to_file(output_path)
            audio_files.append(output_path)
        
        return audio_files
```

#### 5. `SlideshowGenerator` (Video)

```python
# src/video/slideshow.py
class SlideshowGenerator:
    """Vytváří slideshow z obrázků a audia"""
    
    def __init__(self, fps: int = 24, duration_per_bubble: float = 2.0):
        self.fps = fps
        self.duration = duration_per_bubble
    
    def create(self, images: List, bubbles: List, 
               audio_files: List[str], output_path: str):
        """Vytvoří finální video"""
        from moviepy.editor import ImageClip, AudioFileClip, CompositeVideoClip
        
        clips = []
        for i, (image, audio_path) in enumerate(zip(images, audio_files)):
            # Get audio duration
            audio = AudioFileClip(audio_path)
            duration = audio.duration
            
            # Create image clip
            img_clip = ImageClip(image, duration=duration)
            
            # Add bubble highlight
            if i < len(bubbles):
                bubble_clip = self._highlight_bubble(
                    bubbles[i], image, duration
                )
                final_clip = CompositeVideoClip([img_clip, bubble_clip])
            else:
                final_clip = img_clip
            
            final_clip = final_clip.set_audio(audio)
            clips.append(final_clip)
        
        # Concatenate and export
        from moviepy.editor import concatenate_videoclips
        final = concatenate_videoclips(clips, method="compose")
        final.write_videofile(output_path, fps=self.fps)
    
    def _highlight_bubble(self, bubble: Bubble, 
                         image: np.ndarray, duration: float):
        """Vytvoří zvýraznění bubliny"""
        from moviepy.editor import ImageClip, ColorClip
        # Create yellow border around bubble
        # ... implementace
        pass
```

---

## 🧪 Testování

### Spuštění testů

```bash
# Všechny testy
pytest

// S coverage
pytest --cov=src --cov-report=html

// Konkrétní test
pytest tests/test_detector.py

// S debug výstupem
pytest -v -s
```

### Příklad testu

```python
# tests/test_detector.py
import pytest
import cv2
import numpy as np
from src.detectors.bubble_detector import BubbleDetector

@pytest.fixture
def sample_comic_image():
    """Vzorový obrázek komiksu"""
    # Načti testovací obrázek
    image = cv2.imread('assets/sample_comics/test_page.jpg')
    return image

def test_bubble_detection(sample_comic_image):
    """Otestuje detekci bublin"""
    detector = BubbleDetector(min_area=500)
    bubbles = detector.detect(sample_comic_image)
    
    assert len(bubbles) > 0
    assert all(b.area >= 500 for b in bubbles)
    assert bubbles[0].x >= 0
    assert bubbles[0].y >= 0

def test_bubble_sorting():
    """Otestuje řazení bublin"""
    detector = BubbleDetector()
    bubbles = [
        Bubble(100, 200, 50, 50, 2500),
        Bubble(50, 100, 50, 50, 2500),
    ]
    sorted_bubbles = detector._sort_by_reading_order(bubbles)
    
    assert sorted_bubbles[0].y <= sorted_bubbles[1].y
```

---

## 🐛 Debugging

### Logování

```python
# src/utils/logger.py
import logging

def setup_logger(name: str, level=logging.INFO):
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    handler = logging.StreamHandler()
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    handler.setFormatter(formatter)
    logger.addHandler(handler)
    
    return logger

# Použití
logger = setup_logger(__name__)
logger.info("Processing comic...")
logger.debug(f"Detected {len(bubbles)} bubbles")
```

### Vizuální debugging

```python
def debug_draw_bubbles(image: np.ndarray, bubbles: List[Bubble], 
                      output_path: str):
    """Vykreslí detekované bubliny pro debug"""
    debug_img = image.copy()
    
    for i, bubble in enumerate(bubbles):
        # Zelený obdélník kolem bubliny
        cv2.rectangle(debug_img, 
                     (bubble.x, bubble.y),
                     (bubble.x + bubble.w, bubble.y + bubble.h),
                     (0, 255, 0), 2)
        
        # Číslo bubliny
        cv2.putText(debug_img, str(i),
                   (bubble.x, bubble.y - 5),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 0, 255), 1)
    
    cv2.imwrite(output_path, debug_img)
```

---

## ➕ Přidávání funkcí

### Přidání nového TTS enginu

1. Vytvořte `src/tts/new_tts.py`:

```python
from .base import TTSEngineBase

class NewTTSEngine(TTSEngineBase):
    def generate(self, texts: List[str]) -> List[str]:
        # Implementace
        pass
```

2. Registrace v `src/tts/__init__.py`:

```python
from .new_tts import NewTTSEngine

AVAILABLE_ENGINES = {
    'edge': EdgeTTSEngine,
    'openai': OpenAITTSEngine,
    'new': NewTTSEngine,  # <-- nový
}
```

3. Přidejte testy a dokumentaci

### Přidání nového formátu vstupu

1. Vytvořte `src/loaders/new_format.py`:

```python
class NewFormatLoader:
    def load(self, file_path: str) -> List[np.ndarray]:
        # Implementace
        pass
```

2. Integrace do hlavního loaderu

---

## ⚙️ Klíčové konfigurace

### config.py

```python
# src/config.py
from dataclasses import dataclass
from typing import Optional

@dataclass
class DetectorConfig:
    min_bubble_area: int = 500
    max_bubble_area: int = 100000
    circularity_min: float = 0.3
    circularity_max: float = 1.0
    aspect_ratio_min: float = 0.3
    aspect_ratio_max: float = 3.0

@dataclass
class OCRConfig:
    confidence_threshold: int = 60
    language: str = 'ces'
    psm_mode: int = 6

@dataclass
class TTSConfig:
    engine: str = 'edge'  # 'edge' nebo 'openai'
    voice: str = 'cs-CZ-AntoninNeural'
    rate: float = 1.0  # Rychlost (0.5 - 2.0)

@dataclass
class VideoConfig:
    fps: int = 24
    codec: str = 'libx264'
    bitrate: str = '5M'
    duration_per_bubble: float = 2.0

@dataclass
class AppConfig:
    detector: DetectorConfig = DetectorConfig()
    ocr: OCRConfig = OCRConfig()
    tts: TTSConfig = TTSConfig()
    video: VideoConfig = VideoConfig()
    debug_mode: bool = False
    output_dir: str = 'output'
```

---

## 📋 Best Practices

### Kód

1. **Type hints** všude
   ```python
   def detect(image: np.ndarray) -> List[Bubble]:
   ```

2. **Docstrings** pro všechny veřejné metody
   ```python
   def process(self, input_file: str) -> ProcessResult:
       """Zpracuje vstupní soubor a vrátí výsledek.
       
       Args:
           input_file: Cesta ke vstupnímu souboru
       
       Returns:
           ProcessResult s metadaty
       """
   ```

3. **Error handling**
   ```python
   try:
       result = self.detector.detect(image)
   except cv2.error as e:
       logger.error(f"OpenCV error: {e}")
       raise DetectorError(f"Detection failed: {e}")
   ```

4. **Validace vstupu**
   ```python
   if not os.path.exists(input_file):
       raise FileNotFoundError(f"File not found: {input_file}")
   
   if not input_file.lower().endswith(('.jpg', '.png', '.pdf')):
       raise ValueError(f"Unsupported format: {input_file}")
   ```

### Git workflow

1. Feature branchy: `feature/feature-name`
2. Commit messages: `feat: add bubble detection`
3. Pull request s code review

---

## 🚀 Performance tipy

- Batch processing pro více souborů
- Caching OCR výsledků
- Paralelní zpracování (multiprocessing)
- Optimalizace OpenCV operací
- Kompilace s Cythonem pro kritické sekce

---

## 📚 Zdroje

- [OpenCV dokumentace](https://docs.opencv.org/)
- [pytesseract](https://pypi.org/project/pytesseract/)
- [moviepy](https://zulko.github.io/moviepy/)
- [edge-tts](https://github.com/rany2/edge-tts)

---

<div align="center">

**Happy coding! 🚀**

</div>

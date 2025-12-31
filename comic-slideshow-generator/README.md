# 🎯 AI Comic Slideshow Generator

> **Automatická tvorba animovaných prezentací z komiksů pomocí AI**
> 
> Detekce bublin • Extrakce textu • Text-to-Speech • Video export

[![Python](https://img.shields.io/badge/Python-3.10%2B-blue)](https://python.org)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Status](https://img.shields.io/badge/Status-In%20Development-yellow)]()

---

## 📖 Přehled

Tento projekt automatizuje proces tvorby prezentací z komiksů pomocí AI technologií. Aplikace:

- 🖼️ **Načítá komiksy** z JPG, PNG nebo PDF souborů
- 🔍 **Detekuje řečové bubliny** pomocí počítačového vidění
- 📝 **Extrahuje text** z bublin pomocí OCR
- 🔊 **Převádí text na řeč** pomocí AI TTS (zdarma nebo placené)
- 🎬 **Vytváří slideshow** s synchronizovaným audiem

### Případ použití

- 📚 Vzdělávací materiály z komiksů
- 🎭 Audioknihy z grafických románů
- ♿ Přístupnost pro zrakově postižené
- 🎨 Tvůrčí projekty a prezentace

---

## 🚀 Rychlý start

### Systémové požadavky

- **Python:** 3.10 nebo vyšší
- **OS:** Windows 10+, macOS 10.15+, nebo Linux
- **RAM:** Minimálně 4 GB (8 GB doporučeno)
- **Disk:** 500 MB pro aplikaci + závislosti

### 1. Klonování repozitáře

```bash
git clone https://github.com/vase-username/comic-slideshow-generator.git
cd comic-slideshow-generator
```

### 2. Instalace systémových závislostí

#### Windows

1. **Tesseract OCR:**
   - Stáhněte installer: [github.com/UB-Mannheim/tesseract/wiki](https://github.com/UB-Mannheim/tesseract/wiki)
   - Nainstalujte do výchozího umístění: `C:\Program Files\Tesseract-OCR`
   - Přidejte toto umístění do systémové PATH

2. **Poppler (pro PDF):**
   - Stáhněte: [blog.alivate.com.au/poppler-windows](http://blog.alivate.com.au/poppler-windows/)
   - Extrahujte do: `C:\Program Files\poppler`
   - Přidejte `bin` složku do PATH

3. **FFmpeg (pro video):**
   - Stáhněte: [ffmpeg.org/download.html](https://ffmpeg.org/download.html)
   - Přidejte `bin` složku do PATH

#### macOS

```bash
brew install tesseract poppler ffmpeg
```

#### Linux (Ubuntu/Debian)

```bash
sudo apt-get update
sudo apt-get install tesseract-ocr poppler-utils ffmpeg
```

### 3. Vytvoření virtuálního prostředí

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS/Linux
source venv/bin/activate
```

### 4. Instalace Python závislostí

```bash
pip install -r requirements.txt
```

### 5. Spuštění aplikace

```bash
# Streamlit UI (doporučeno)
streamlit run app.py

# Nebo příkazová řádka
python main.py --input comic.pdf --output video.mp4
```

---

## 📦 Instalace

### Výběr UI frameworku

Tento projekt podporuje několik UI možností:

| Framework | Instalace | Výhody | Doporučeno pro |
|-----------|-----------|--------|----------------|
| **Streamlit** | `pip install streamlit` | Rychlý vývoj, moderní UI | Rychlý MVP |
| **Gradio** | `pip install gradio` | Jednoduché sdílení | Demo/prototyp |
| **PyQt6** | `pip install PyQt6` | Profesionální desktop app | Produkce |

### Kompletní requirements.txt

```txt
# Závislosti projektu
opencv-python>=4.8.0
pytesseract>=0.3.10
pdf2image>=1.16.0
Pillow>=10.0.0
moviepy>=1.0.3
edge-tts>=6.1.0
numpy>=1.24.0

# UI (vyberte jeden)
streamlit>=1.28.0
# gradio>=4.0.0
# PyQt6>=6.5.0

# Volitelné: OpenAI API pro vyšší kvalitu TTS
openai>=1.0.0
python-dotenv>=1.0.0
```

---

## 🏗️ Architektura

```
┌─────────────────────────────────────────────────────────────┐
│                     USER INTERFACE                           │
│                    (Streamlit/Gradio/PyQt)                   │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   PREPROCESSING                              │
│  JPG/PNG Loader ── PDF Converter ─── CBZ Unzipper           │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   BUBBLE DETECTION                           │
│          OpenCV: threshold → contours → filter              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   TEXT EXTRACTION                            │
│            pytesseract OCR → confidence filter              │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   TEXT-TO-SPEECH                             │
│      edge-tts (free) ─── nebo ─── OpenAI API (paid)         │
└─────────────────────────────────────────────────────────────┘
                              │
                              ▼
┌─────────────────────────────────────────────────────────────┐
│                   VIDEO GENERATION                           │
│         moviepy: images + audio + transitions → MP4         │
└─────────────────────────────────────────────────────────────┘
```

---

## 📚 Použití

### Základní použití (Python API)

```python
from comic_slideshow import ComicProcessor

# Vytvoření procesoru
processor = ComicProcessor(
    tts_engine='edge',  # nebo 'openai' pro placenou kvalitu
    voice='cs-CZ-AntoninNeural',  # český hlas
    output_format='mp4'
)

# Zpracování komiksu
result = processor.process(
    input_file='comic.pdf',
    output_file='slideshow.mp4',
    fps=24,
    zoom_duration=2.0  # sekundy na bublinu
)

print(f"Vytvořeno: {result.output_path}")
print(f"Počet detekovaných bublin: {result.bubble_count}")
```

### Streamlit UI

```bash
streamlit run app.py
```

Pak v prohlížeči:
1. Nahrajte komiks (JPG/PNG/PDF)
2. Vyberte hlas a jazyk
3. Klikněte na "Generovat slideshow"
4. Stáhněte výsledné video

### Příkazová řádka

```bash
python main.py \
  --input comic.pdf \
  --output slideshow.mp4 \
  --voice cs-CZ-AntoninNeural \
  --fps 24 \
  --zoom 2.0
```

---

## 🎨 Funkce

### ✅ Implementované

- ✅ Načítání JPG, PNG, PDF
- ✅ Detekce řečových bublin
- ✅ OCR extrakce textu
- ✅ Text-to-Speech (edge-tts zdarma)
- ✅ Video export (MP4)
- ✅ Streamlit UI

### 🚧 Plánované

- 🔄 CBZ/ZIP podpora
- 🔄 Manuální korekce bublin
- 🔄 Více hlasů pro různé postavy
- 🔄 Zoom/pan animace
- 🔄 Batch processing
- 🔄 Export do více formátů
- 🔄 Desktop aplikace (PyQt6)

---

## ⚙️ Konfigurace

### Soubor `.env` (volitelné pro OpenAI)

```env
# OpenAI API (volitelné, pro vyšší kvalitu TTS)
OPENAI_API_KEY=sk-...
OPENAI_TTS_MODEL=gpt-4o-mini-tts

# Tesseract cesta (pokud není v PATH)
TESSERACT_CMD=C:/Program Files/Tesseract-OCR/tesseract

# Poppler cesta (pro PDF)
POPPLER_PATH=C:/Program Files/poppler

# FFmpeg cesta (pro video)
FFMPEG_PATH=C:/ffmpeg/bin
```

### Nastavení detekce

```python
config = {
    # Minimální velikost bubliny (pixely)
    'min_bubble_area': 500,
    
    # Práhování OCR spolehlivosti (0-100)
    'ocr_confidence': 60,
    
    # Doba trvání jedné bubliny (sekundy)
    'bubble_duration': 2.0,
    
    # FPS výstupního videa
    'output_fps': 24,
}
```

---

## 🎯 Tech Stack

| Komponenta | Knihovna | Verze | Licence |
|------------|----------|-------|---------|
| **Detekce bublin** | OpenCV | 4.8+ | Apache 2.0 |
| **OCR** | pytesseract | 0.3+ | Apache 2.0 |
| **PDF konverze** | pdf2image | 1.16+ | MIT |
| **Image zpracování** | Pillow | 10.0+ | PIL |
| **Video** | moviepy | 1.0+ | MIT |
| **TTS (zdarma)** | edge-tts | 6.1+ | MIT |
| **TTS (placené)** | OpenAI API | 1.0+ | Proprietary |
| **UI** | Streamlit | 1.28+ | Apache 2.0 |

---

## 💡 Příklady

Viz složka `/examples` pro ukázkové komiksy a skripty.

```bash
python examples/basic_usage.py
```

---

## 🤝 Přispívání

Přínosy jsou vítány! Prosím:

1. Forkněte repozitář
2. Vytvořte feature branch (`git checkout -b feature/AwesomeFeature`)
3. Commitněte změny (`git commit -m 'Add AwesomeFeature'`)
4. Pushněte do branch (`git push origin feature/AwesomeFeature`)
5. Otevřete Pull Request

---

## 📝 License

Tento projekt je licencován pod MIT licencí - viz [LICENSE](LICENSE) soubor.

---

## 🐛 Known Issues

- **Detekce bublin** může selhat u komiksů s atypickým stylem
- **OCR kvalita** závisí na rozlišení vstupního obrazu
- **edge-tts** vyžaduje internetové připojení
- **PDF** s více stránkami může trvat déle

---

## ❓ FAQ

<details>
<summary><b>Co když detekce bublin nefunguje?</b></summary>

Zkuste:
- Zvýšit rozlišení vstupního obrazu
- Upravit parametry detekce v configu
- Použít manuální korekci (plánováno)
</details>

<details>
<summary><b>Jaký je rozdíl mezi edge-tts a OpenAI?</b></summary>

- **edge-tts**: Zdarma, 100+ hlasů, dobrá kvalita
- **OpenAI**: Placené (~$15/1M znaků), nejlepší kvalita, 13 hlasů
</details>

<details>
<summary><b>Funguje to s komiksy v češtině?</b></summary>

Ano! edge-tts podporuje češtinu:
- `cs-CZ-AntoninNeural` (mužský hlas)
- `cs-CZ-VlastaNeural` (ženský hlas)
</details>

---

## 📞 Kontakt

- **Autor:** [Vaše Jméno]
- **Email**: vas@email.cz
- **Issues**: [GitHub Issues](https://github.com/vase-username/comic-slideshow-generator/issues)

---

## 🙏 Poděkování

- OpenCV týmu za výbornou CV knihovnu
- Tesseract OCR pro open-source OCR
- Microsoft Edge za bezplatné TTS API
- Komunitě za podporu a feedback

---

<div align="center">

**⭐ Pokud se vám projekt líbí, dejte hvězdičku! ⭐**

Made with ❤️ by [Your Name]

</div>

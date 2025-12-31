"""
Dependency checker for Comic Slideshow Generator
Validates that required external dependencies are installed
"""
import sys
import shutil
import subprocess
from pathlib import Path
from typing import List, Tuple, Optional


class DependencyChecker:
    """Checks for required system dependencies"""
    
    def __init__(self):
        self.missing: List[Tuple[str, str]] = []
        self.present: List[str] = []
    
    def check_command(self, name: str, command: str, 
                     version_flag: str = "--version") -> bool:
        """
        Check if a command-line tool is available
        
        Args:
            name: Human-readable name
            command: Command to check
            version_flag: Flag to get version
            
        Returns:
            True if command is available
        """
        try:
            result = subprocess.run(
                [command, version_flag],
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0:
                version = result.stdout.strip().split('\n')[0]
                self.present.append(f"{name}: {version}")
                return True
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass
        
        self.missing.append((name, command))
        return False
    
    def check_all(self) -> bool:
        """Check all required dependencies"""
        print("Checking system dependencies...")
        print("-" * 50)
        
        # Check Tesseract OCR
        self.check_command("Tesseract OCR", "tesseract", "--version")
        
        # Check FFmpeg (for moviepy)
        if self.check_command("FFmpeg", "ffmpeg", "-version"):
            self.present.append("MoviePy support: Available")
        else:
            self.missing.append(("FFmpeg (required for video)", "ffmpeg"))
        
        # Check ImageMagick (optional, for some image operations)
        self.check_command("ImageMagick", "magick", "-version")
        
        # Check Poppler (for pdf2image)
        self.check_command("Poppler", "pdftoppm", "-v")
        
        # Report results
        print("\n✓ Present dependencies:")
        for item in self.present:
            print(f"  ✓ {item}")
        
        if self.missing:
            print("\n✗ Missing dependencies:")
            for name, cmd in self.missing:
                print(f"  ✗ {name} (command: {cmd})")
            print("\nInstallation instructions:")
            self._print_install_instructions()
            return False
        
        print("\n✓ All dependencies are installed!")
        return True
    
    def _print_install_instructions(self):
        """Print platform-specific installation instructions"""
        if sys.platform == "win32":
            print("""
Windows:
  Tesseract: https://github.com/UB-Mannheim/tesseract/wiki
    - Download and install the installer
    - Add C:\\Program Files\\Tesseract-OCR to PATH
    
  FFmpeg: https://ffmpeg.org/download.html
    - Download build, extract, and add to PATH
    
  Poppler: http://blog.alivate.com.au/poppler-windows/
    - Download, extract, add bin/ to PATH
""")
        elif sys.platform == "darwin":
            print("""
macOS (using Homebrew):
  brew install tesseract
  brew install ffmpeg
  brew install poppler
  brew install imagemagick
""")
        else:  # Linux
            print("""
Linux (Ubuntu/Debian):
  sudo apt-get install tesseract-ocr
  sudo apt-get install ffmpeg
  sudo apt-get install poppler-utils
  sudo apt-get install imagemagick

Linux (Fedora/RHEL):
  sudo dnf install tesseract
  sudo dnf install ffmpeg
  sudo dnf install poppler-utils
  sudo dnf install ImageMagick
""")


def check_python_version() -> bool:
    """Check if Python version is sufficient"""
    if sys.version_info < (3, 10):
        print(f"✗ Python 3.10+ required, found {sys.version}")
        return False
    print(f"✓ Python version: {sys.version.split()[0]}")
    return True


def main():
    """Main entry point for dependency checker"""
    print("=" * 50)
    print("Comic Slideshow Generator - Dependency Checker")
    print("=" * 50)
    print()
    
    # Check Python version
    if not check_python_version():
        sys.exit(1)
    
    print()
    
    # Check system dependencies
    checker = DependencyChecker()
    if not checker.check_all():
        print("\n✗ Some dependencies are missing. Please install them.")
        sys.exit(1)
    
    print("\n✓ All checks passed! Ready to install Python packages.")
    print("\nNext steps:")
    print("  pip install -r requirements.txt")


if __name__ == "__main__":
    main()

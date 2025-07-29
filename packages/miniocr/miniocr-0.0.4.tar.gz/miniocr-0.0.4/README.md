# MiniOCR

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful and easy-to-use Python package for performing Optical Character Recognition (OCR) on images, PDF documents, and PowerPoint presentations using OpenAI's Vision API.

## Features

- 🖼️ **Multi-format support**: Process images (PNG, JPG, JPEG, GIF, BMP, TIFF, WebP), PDF files, and PPTX presentations
- ⚡ **Parallel processing**: Concurrent processing of multiple pages/slides for improved performance
- 🌐 **Cross-platform**: Works on Windows, macOS, and Linux
- 📄 **Visual OCR for PPTX**: Converts PowerPoint slides to images for accurate visual content extraction
- 🔄 **Async support**: Built with asyncio for efficient processing
- 📝 **Markdown output**: Converts documents to clean, structured markdown format

## Installation

### System Requirements

- **Python**: 3.8 or higher
- **Operating System**: Windows, macOS, or Linux

### Dependencies

#### Python Dependencies (Auto-installed)

MiniOCR automatically installs these Python packages:

- **openai** - OpenAI API client for Vision processing
- **aiohttp** - Async HTTP client for file downloads
- **aiofiles** - Async file operations
- **pdf2image** - PDF to image conversion
- **python-pptx** - PowerPoint file parsing
- **Pillow** - Image processing and manipulation

#### System Dependencies (Manual Installation Required)

##### For PDF Processing - Poppler

**macOS:**
```bash
brew install poppler
```

**Ubuntu/Debian:**
```bash
sudo apt-get install poppler-utils
```

**Windows:**
Download and install from [Poppler for Windows](http://blog.alivate.com.au/poppler-windows/)

##### For PPTX Visual Processing - LibreOffice

**macOS:**
```bash
brew install --cask libreoffice
```

**Ubuntu/Debian:**
```bash
sudo apt-get install libreoffice
```

**Windows:**
Download and install from [LibreOffice official website](https://www.libreoffice.org/download/download/)

> **Note**: LibreOffice is required for high-quality PPTX processing with visual content extraction. Without it, MiniOCR will fall back to text-only extraction. On Windows, MiniOCR automatically detects LibreOffice in common installation paths.

### Install MiniOCR

#### From PyPI (Recommended)

```bash
pip install miniocr
```

#### From Source

```bash
git clone https://github.com/w95/miniocr.git
cd miniocr
pip install -e .
```

### Verify Installation

```python
from miniocr import MiniOCR, __version__
print(f"MiniOCR v{__version__} installed successfully!")
```

## Quick Start

### Setup

First, you'll need an OpenAI API key. Set it as an environment variable:

```bash
export OPENAI_API_KEY="your-api-key-here"
```

Or pass it directly when initializing the class.

### Basic Usage

```python
import asyncio
from miniocr import MiniOCR

async def main():
    # Initialize with API key (or use environment variable)
    ocr = MiniOCR(api_key="your-api-key-here")
    
    # Process an image
    result = await ocr.ocr("path/to/image.jpg")
    print(result["content"])
    
    # Process a PDF
    result = await ocr.ocr("path/to/document.pdf")
    print(f"Processed {result['pages']} pages")
    print(result["content"])
    
    # Process a PowerPoint presentation
    result = await ocr.ocr("path/to/presentation.pptx")
    print(result["content"])

if __name__ == "__main__":
    asyncio.run(main())
```

### Advanced Usage

```python
import asyncio
from miniocr import MiniOCR

async def advanced_example():
    ocr = MiniOCR()
    
    # Process with custom settings
    result = await ocr.ocr(
        file_path="document.pdf",
        model="gpt-4o",  # Use different OpenAI model
        concurrency=10,  # Process up to 10 pages simultaneously
        output_dir="./output",  # Save markdown to file
        cleanup=True  # Clean up temporary files
    )
    
    print(f"File: {result['file_name']}")
    print(f"Pages processed: {result['pages']}")
    print(f"Content length: {len(result['content'])} characters")

asyncio.run(advanced_example())
```

### Processing URLs

```python
import asyncio
from miniocr import MiniOCR

async def process_url():
    ocr = MiniOCR()
    
    # Process a file from URL
    result = await ocr.ocr("https://example.com/document.pdf")
    print(result["content"])

asyncio.run(process_url())
```

## API Reference

### MiniOCR Class

#### `__init__(api_key: str = None)`

Initialize the MiniOCR instance.

**Parameters:**
- `api_key` (str, optional): OpenAI API key. If not provided, will use `OPENAI_API_KEY` environment variable.

#### `async ocr(file_path, model="gpt-4o-mini", concurrency=5, output_dir=None, cleanup=True)`

Process a file and extract text using OCR.

**Parameters:**
- `file_path` (str): Path or URL to the file to process
- `model` (str): OpenAI model to use (default: "gpt-4o-mini")
- `concurrency` (int): Number of concurrent API requests (default: 5)
- `output_dir` (str, optional): Directory to save markdown output
- `cleanup` (bool): Whether to clean up temporary files (default: True)

**Returns:**
- `dict`: Dictionary containing:
  - `content` (str): Extracted text in markdown format
  - `pages` (int): Number of pages/slides processed
  - `file_name` (str): Name of the processed file

**Supported file types:**
- Images: `.png`, `.jpg`, `.jpeg`, `.gif`, `.bmp`, `.tiff`, `.webp`
- Documents: `.pdf`
- Presentations: `.pptx`

## Configuration

### Required Configuration

#### OpenAI API Key

You **must** provide an OpenAI API key to use MiniOCR. You can set it in two ways:

**Option 1: Environment Variable (Recommended)**
```bash
export OPENAI_API_KEY="your-api-key-here"
```

**Option 2: Pass directly to class**
```python
from miniocr import MiniOCR
ocr = MiniOCR(api_key="your-api-key-here")
```

### Optional Dependencies Behavior

#### Without Poppler (PDF Processing)
- **Effect**: PDF processing will fail
- **Error**: `pdf2image` will raise an exception
- **Solution**: Install Poppler following the instructions above

#### Without LibreOffice (PPTX Processing)
- **Effect**: Falls back to text-only extraction from PPTX files
- **Warning**: Visual content (charts, images, formatting) will be lost
- **Solution**: Install LibreOffice for full visual processing capabilities

### Model Options

MiniOCR supports various OpenAI models:
- `gpt-4o-mini` (default, cost-effective)
- `gpt-4o` (higher accuracy)
- `gpt-4-turbo`

## Output Format

MiniOCR converts documents to clean markdown with the following features:

- **Tables**: Converted to HTML format for better structure
- **Checkboxes**: Represented as ☐ (unchecked) and ☑ (checked)
- **Special elements**: Logos, watermarks, and page numbers are wrapped in brackets
- **Charts and infographics**: Interpreted and converted to markdown tables when applicable

## Error Handling

```python
import asyncio
from miniocr import MiniOCR

async def handle_errors():
    ocr = MiniOCR()
    
    try:
        result = await ocr.ocr("nonexistent.pdf")
    except ValueError as e:
        print(f"Unsupported file type: {e}")
    except Exception as e:
        print(f"Processing error: {e}")

asyncio.run(handle_errors())
```

## Troubleshooting

### Common Issues

#### "No module named 'pdf2image'" or PDF processing fails
**Solution**: Install Poppler system dependency
```bash
# macOS
brew install poppler

# Ubuntu/Debian  
sudo apt-get install poppler-utils
```

#### "LibreOffice conversion failed" for PPTX files
**Solution**: Install LibreOffice
```bash
# macOS
brew install --cask libreoffice

# Ubuntu/Debian
sudo apt-get install libreoffice
```

#### "Invalid API key" or OpenAI authentication errors
**Solution**: Verify your OpenAI API key
```bash
# Check if environment variable is set
echo $OPENAI_API_KEY

# Or test with a simple script
python -c "from openai import OpenAI; client = OpenAI(); print('API key is valid')"
```

#### PPTX files show only text content, missing charts/images
**Cause**: LibreOffice not installed, falling back to text-only extraction  
**Solution**: Install LibreOffice for full visual processing capabilities

#### "soffice command not found" errors
**Cause**: LibreOffice not in system PATH  
**Solutions**:
- **macOS**: Ensure LibreOffice is installed via Homebrew: `brew install --cask libreoffice`
- **Linux**: Install via package manager: `sudo apt-get install libreoffice`
- **Windows**: Add LibreOffice to PATH or reinstall

#### Rate limiting or quota exceeded errors
**Cause**: Too many requests to OpenAI API  
**Solutions**:
- Reduce `concurrency` parameter (try 1-3 for free tier)
- Add delays between processing batches
- Upgrade your OpenAI plan for higher rate limits

### Dependencies Verification

#### Check Python Dependencies
```python
# Verify MiniOCR installation
from miniocr import MiniOCR, __version__
print(f"MiniOCR v{__version__} installed")

# Check key dependencies
import openai, aiohttp, pdf2image, pptx
print("All Python dependencies available")
```

#### Check System Dependencies
```bash
# Test Poppler installation
pdftoppm -h

# Test LibreOffice installation  
soffice --version
```

## Performance Tips

1. **Adjust concurrency**: Increase `concurrency` parameter for faster processing of multi-page documents
2. **Use appropriate models**: `gpt-4o-mini` for cost-effectiveness, `gpt-4o` for higher accuracy
3. **Process in batches**: For large numbers of files, process them in batches to avoid rate limits
4. **Local processing**: Keep files local when possible to avoid download overhead

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Testing

Run the test suite:

```bash
pytest tests/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### v0.0.4
- **Enhanced Windows Support**: Improved LibreOffice detection on Windows systems
- **Cross-platform Compatibility**: Automatically finds LibreOffice in common installation paths
- **Robust Error Handling**: Better timeout and fallback mechanisms for PPTX processing
- **Improved Reliability**: More resilient LibreOffice executable detection across platforms

### v0.0.3
- **Enhanced PPTX Processing**: Now uses LibreOffice for PDF conversion and OpenAI Vision API
- **Visual Content Extraction**: Captures charts, images, and formatting from PowerPoint slides
- **Improved Accuracy**: Better OCR results for complex PPTX layouts
- **Fallback Support**: Graceful degradation to text extraction if LibreOffice unavailable
- **Updated Documentation**: Comprehensive dependency and troubleshooting information

### v0.0.2
- **PyPI Publication**: Package published to Python Package Index
- **Improved Package Structure**: Better organization and imports
- **Enhanced README**: Complete documentation with examples
- **Testing Infrastructure**: Comprehensive test suite

### v0.0.1
- **Initial Release**: Basic OCR functionality
- **Multi-format Support**: Images, PDF, and PPTX files
- **Async Processing**: Concurrent processing with configurable limits
- **Cross-platform Compatibility**: Windows, macOS, and Linux support

## Support

If you encounter any issues or have questions, please [open an issue](https://github.com/w95/miniocr/issues) on GitHub.

## Acknowledgments

- Built with [OpenAI's Vision API](https://platform.openai.com/docs/guides/vision)
- Uses [pdf2image](https://github.com/Belval/pdf2image) for PDF processing
- Uses [python-pptx](https://github.com/scanny/python-pptx) for PowerPoint processing
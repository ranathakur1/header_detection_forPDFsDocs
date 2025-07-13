# PDF Header Detector

A Python library for intelligent PDF header detection using advanced font size analysis and hierarchy detection.

## Features

- **Intelligent Header Detection**: Automatically detects headers based on font size analysis
- **Font Hierarchy Analysis**: Analyzes document font patterns to identify header levels
- **Auto-Threshold Detection**: Automatically determines optimal font size thresholds
- **Body Text Filtering**: Intelligently filters out body text from header candidates
- **JSON Output**: Export detected headers as structured JSON data
- **Command Line Interface**: Easy-to-use CLI for batch processing
- **Extensible Design**: Clean API for integration into other applications

## Installation

### From Source

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-header-detector.git
cd pdf-header-detector

# Install the package
pip install .

# Or install in development mode
pip install -e .
```

### Using pip (when published)

```bash
pip install pdf-header-detector
```

## Dependencies

- Python 3.7+
- PyMuPDF (fitz) >= 1.23.0

## Quick Start

### As a Library

```python
from pdf_header_detector import CleanHybridPDFChunker

# Create detector instance
detector = CleanHybridPDFChunker()

# Detect headers (auto-detect font size threshold)
headers = detector.detect_headers_by_font_size("document.pdf")

# Print results
for header in headers:
    print(f"Page {header['page']}: {header['header']} (Level {header['header_level']})")

# Get JSON output
json_output = detector.get_headers_json("document.pdf")
print(json_output)

# Save to file
detector.save_headers_to_json(headers, "output_headers.json")
```

### Command Line Interface

```bash
# Basic usage - auto-detect headers
pdf-header-detector document.pdf

# Specify minimum font size
pdf-header-detector document.pdf --min-size 14

# Save to specific output file
pdf-header-detector document.pdf --output my_headers.json

# Show detailed font analysis
pdf-header-detector document.pdf --analyze-fonts

# Verbose output
pdf-header-detector document.pdf --verbose

# Short command alias
phd document.pdf
```

## API Reference

### CleanHybridPDFChunker Class

The main class for PDF header detection.

#### Methods

##### `detect_headers_by_font_size(pdf_path, min_size=None)`

Detect headers in a PDF using font size analysis.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `min_size` (float, optional): Minimum font size for headers (auto-detected if None)

**Returns:**
- `List[Dict]`: List of detected headers with metadata

**Example:**
```python
headers = detector.detect_headers_by_font_size("document.pdf", min_size=12.0)
```

##### `get_headers_json(pdf_path, min_size=None)`

Get headers as a JSON string.

**Parameters:**
- `pdf_path` (str): Path to the PDF file
- `min_size` (float, optional): Minimum font size for headers

**Returns:**
- `str`: JSON string representation of headers

##### `save_headers_to_json(headers, output_file)`

Save headers to a JSON file.

**Parameters:**
- `headers` (List[Dict]): Headers to save
- `output_file` (str): Output file path

**Returns:**
- `bool`: True if successful, False otherwise

##### `get_font_analysis(pdf_path)`

Get detailed font analysis without detecting headers.

**Parameters:**
- `pdf_path` (str): Path to the PDF file

**Returns:**
- `Dict`: Font analysis results

## Output Format

Headers are returned as a list of dictionaries with the following structure:

```json
[
  {
    "header": "Introduction",
    "header_level_name": "level 1",
    "page": 1,
    "header_level": 1
  },
  {
    "header": "Background",
    "header_level_name": "level 2", 
    "page": 2,
    "header_level": 2
  }
]
```

### Fields

- `header` (str): The header text
- `header_level_name` (str): Human-readable level name (e.g., "level 1")
- `page` (int): Page number where the header appears
- `header_level` (int): Numeric hierarchy level (1 = highest, 2 = second, etc.)

## Algorithm Overview

The library uses a sophisticated multi-step process:

1. **Font Analysis**: Scans the entire document to analyze font size distribution
2. **Body Text Detection**: Identifies the most common font sizes (likely body text)
3. **Threshold Calculation**: Automatically determines optimal header detection threshold
4. **Header Filtering**: Applies heuristics to filter out false positives
5. **Hierarchy Assignment**: Groups similar font sizes into hierarchy levels
6. **Duplicate Removal**: Removes duplicate headers that appear multiple times

## Advanced Usage

### Custom Font Size Threshold

```python
# Use a specific minimum font size
headers = detector.detect_headers_by_font_size("document.pdf", min_size=16.0)
```

### Font Analysis Only

```python
# Get detailed font analysis without header detection
analysis = detector.get_font_analysis("document.pdf")
print(f"Body text size: {analysis['body_text_size']}pt")
print(f"Header levels: {analysis['total_levels']}")
```

### Error Handling

```python
try:
    headers = detector.detect_headers_by_font_size("document.pdf")
except FileNotFoundError:
    print("PDF file not found")
except Exception as e:
    print(f"Error processing PDF: {e}")
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### Development Setup

```bash
# Clone the repository
git clone https://github.com/yourusername/pdf-header-detector.git
cd pdf-header-detector

# Install in development mode with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest

# Run linting
flake8 pdf_header_detector/
black pdf_header_detector/

# Type checking
mypy pdf_header_detector/
```

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Changelog

### Version 1.0.0
- Initial release
- Intelligent header detection with font analysis
- Command line interface
- JSON output support
- Auto-threshold detection
- Body text filtering

## Support

- Create an issue on [GitHub Issues](https://github.com/yourusername/pdf-header-detector/issues)
- Check the documentation for more examples
- Review the test files for usage patterns

## Acknowledgments

- Built with [PyMuPDF](https://pymupdf.readthedocs.io/) for PDF processing
- Inspired by the need for better document structure analysis

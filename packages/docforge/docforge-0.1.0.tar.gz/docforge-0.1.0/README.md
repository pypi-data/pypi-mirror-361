# DocForge 🔨

**Forge perfect documents from any format with precision, power, and simplicity.**

DocForge is a comprehensive document processing toolkit built on proven implementations with a modern modular architecture. Born from real-world needs and battle-tested algorithms, DocForge transforms how you work with documents.

## ✨ Features

- 🔍 **OCR Processing**: Convert scanned PDFs to searchable documents with precision
- 🗜️ **Smart Optimization**: Reduce file sizes without compromising quality  
- ⚙️ **Batch Processing**: Handle hundreds of documents efficiently
- 🔧 **Document Analysis**: Extract insights and metadata
- 🎯 **Modular Design**: Use only what you need, extend easily

## 🚀 Why DocForge?

- **Battle-tested OCR algorithms** with Windows compatibility
- **Advanced optimization techniques** from real-world usage
- **Memory-efficient batch processing** for large-scale operations
- **Clean, modular codebase** that's easy to understand and extend
- **Comprehensive error handling** and logging
- **Both programmatic API and command-line interface**

## 📦 Installation

### Option 1: Install from PyPI (when available)
```bash
pip install docforge
```

### Option 2: Install from source
```bash
git clone https://github.com/oscar2song/docforge.git
cd docforge
pip install -e .
```

### System Dependencies

**Ubuntu/Debian:**
```bash
sudo apt-get install tesseract-ocr poppler-utils
```

**macOS:**
```bash
brew install tesseract poppler
```

**Windows:**
Download Tesseract from: https://github.com/tesseract-ocr/tesseract

## 🎯 Quick Start

### Command Line Interface

After installation, use the `docforge` command:

```bash
# Get help
docforge --help

# OCR a scanned PDF
docforge enhanced-ocr -i scanned_document.pdf -o searchable_document.pdf

# Batch OCR processing
docforge enhanced-batch-ocr -i scanned_folder/ -o searchable_folder/

# Standard OCR processing
docforge ocr -i document.pdf -o output.pdf --language eng

# Batch optimization
docforge batch-ocr -i input_folder/ -o output_folder/

# Test the interface
docforge test-rich

# Run performance benchmarks
docforge benchmark --test-files document.pdf
```

### Programmatic API

```python
from docforge import DocumentProcessor

# Initialize the processor
processor = DocumentProcessor(verbose=True)

# OCR a scanned PDF
result = processor.ocr_pdf(
    "scanned_document.pdf",
    "searchable_document.pdf", 
    language='eng'
)

# Optimize PDF size
result = processor.optimize_pdf(
    "large_document.pdf",
    "optimized_document.pdf",
    optimization_type="aggressive"
)

# Batch processing
result = processor.batch_ocr_pdfs(
    "scanned_folder/",
    "searchable_folder/"
)
```

## 🏗️ Architecture

DocForge is built with a clean, modular architecture:

```
docforge/
├── core/           # Core processing engine
├── pdf/            # PDF operations (proven implementations)  
├── cli/            # Command-line interface
├── utils/          # Shared utilities
└── main.py         # CLI entry point
```

## 📋 Available Commands

| Command | Description |
|---------|-------------|
| `enhanced-ocr` | OCR with advanced performance optimization |
| `enhanced-batch-ocr` | Batch OCR with intelligent performance optimization |
| `ocr` | Standard OCR processing |
| `batch-ocr` | Standard batch OCR processing |
| `optimize` | PDF optimization |
| `pdf-to-word` | PDF to Word conversion |
| `split-pdf` | Split PDF documents |
| `benchmark` | Run performance benchmarks |
| `perf-stats` | Display performance statistics |
| `test-rich` | Test Rich CLI interface |

## 🧪 Examples

Run the examples to see DocForge in action:

```bash
# Basic usage examples (if you have example files)
python examples/basic_usage.py

# Test the CLI interface
docforge test-rich

# Test error handling
docforge test-errors

# Test validation system  
docforge test-validation
```

## 🤝 Contributing

We welcome contributions! The modular architecture makes it easy to add new features.

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 🗺️ Roadmap

- ✅ Core PDF processing with proven implementations
- ✅ OCR and optimization capabilities  
- ✅ Command-line interface
- ✅ Comprehensive documentation
- 📄 Word document processing (Word ↔ PDF conversion)
- 🎨 Modern GUI interface
- 🚀 Performance optimizations
- 📊 Excel and PowerPoint support
- 🤖 AI-powered document analysis
- 🌐 Web interface

## 📄 License

This project is licensed under the MIT License.

## 🏆 Acknowledgments

Built with proven implementations and enhanced with modern architecture for the open source community.

---

⭐ **If DocForge helped you, please give it a star!** ⭐

*Built by craftsmen, for craftsmen.* 🔨

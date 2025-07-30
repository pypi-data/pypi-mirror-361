# Paper2Data Parser

[![PyPI version](https://badge.fury.io/py/paper2data-parser.svg)](https://badge.fury.io/py/paper2data-parser)
[![Python](https://img.shields.io/python/required-version-toml?tomlFilePath=https%3A%2F%2Fraw.githubusercontent.com%2Fpaper2data%2Fpaper2data%2Fmain%2Fpackages%2Fparser%2Fpyproject.toml)](https://pypi.org/project/paper2data-parser/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A powerful Python library for extracting and parsing content from academic papers. Transform PDF files, arXiv papers, and DOI-referenced documents into structured, searchable data repositories.

## 🚀 Features

- **📄 Multi-format Input**: PDF files, arXiv URLs, DOI resolution with automatic retrieval
- **🔍 Intelligent Parsing**: Advanced section detection, table extraction to CSV, figure processing
- **🌐 API Integration**: Live arXiv and CrossRef DOI resolution with metadata enrichment
- **⚡ Performance Optimized**: Rate limiting, caching, and batch processing capabilities
- **🔧 Advanced Configuration**: YAML-based configuration with smart defaults and validation
- **🔌 Enhanced Plugin System v1.1**: Marketplace, dependency management, and auto-updates
- **🧮 Mathematical Processing**: LaTeX equation detection, conversion, and MathML support
- **🖼️ Advanced Figure Processing**: AI-powered figure classification and caption extraction
- **📚 Enhanced Metadata**: Institution detection, author disambiguation, and funding information
- **📖 Bibliographic Parsing**: Citation style detection, reference normalization, and network analysis
- **🎨 Multi-Format Export**: HTML, LaTeX, Word, EPUB, Markdown with professional templates
- **🧪 Production Ready**: 100% test coverage with comprehensive quality assurance

## 📦 Installation

```bash
# Install the latest version
pip install paper2data-parser

# Install with API integration dependencies
pip install paper2data-parser[api]

# Install with development dependencies
pip install paper2data-parser[dev]
```

## 🛠️ Quick Start

### Basic Usage

```python
from paper2data import PDFIngestor, extract_all_content

# Initialize ingestor
ingestor = PDFIngestor()

# Extract content from a PDF
content = ingestor.ingest("path/to/paper.pdf")

# Extract all content with optimization
results = extract_all_content("path/to/paper.pdf")
print(f"Extracted {len(results.sections)} sections")
print(f"Found {len(results.figures)} figures")
print(f"Extracted {len(results.tables)} tables")
```

### Advanced Usage with Configuration

```python
from paper2data import (
    create_config_interactive,
    extract_all_content_optimized,
    MultiFormatExporter
)

# Create configuration interactively
config = create_config_interactive()

# Extract content with full optimization
results = extract_all_content_optimized(
    "path/to/paper.pdf",
    config=config,
    enable_parallel=True,
    enable_caching=True
)

# Export to multiple formats
exporter = MultiFormatExporter({
    "formats": ["html", "latex", "word"],
    "theme": "academic"
})
exporter.export_document(results, "output/")
```

### Enhanced Plugin System v1.1

```python
from paper2data import initialize_enhanced_plugin_system
import asyncio

# Initialize the enhanced plugin system
system = initialize_enhanced_plugin_system({
    "auto_update_enabled": True,
    "health_monitoring_enabled": True
})

# Search and install plugins
results = system.search_plugins("latex", min_rating=4.0)
await system.install_plugin("latex-processor")

# Monitor system health
metrics = system.get_system_metrics()
print(f"Active plugins: {metrics.active_plugins}")
```

### Mathematical Processing

```python
from paper2data import EquationProcessor

# Process mathematical equations
processor = EquationProcessor()
equations = processor.extract_equations("path/to/paper.pdf")

for eq in equations:
    print(f"LaTeX: {eq.latex}")
    print(f"MathML: {eq.mathml}")
    print(f"Complexity: {eq.complexity_score}")
```

### Advanced Figure Processing

```python
from paper2data import AdvancedFigureProcessor

# Process figures with AI analysis
processor = AdvancedFigureProcessor()
figures = processor.process_figures("path/to/paper.pdf")

for fig in figures:
    print(f"Type: {fig.figure_type}")
    print(f"Caption: {fig.caption.text}")
    print(f"Quality: {fig.analysis.quality}")
```

### Enhanced Metadata Extraction

```python
from paper2data import EnhancedMetadataExtractor

# Extract comprehensive metadata
extractor = EnhancedMetadataExtractor()
metadata = extractor.extract_metadata("path/to/paper.pdf")

print(f"Title: {metadata.title}")
print(f"Authors: {[author.full_name for author in metadata.authors]}")
print(f"Institutions: {[inst.name for inst in metadata.institutions]}")
print(f"Funding: {[fund.name for fund in metadata.funding_sources]}")
```

## 🎯 Key Components

### Core Extraction
- **PDFIngestor**: Primary PDF processing engine
- **ContentExtractor**: Comprehensive content extraction
- **SectionExtractor**: Intelligent section detection
- **FigureExtractor**: Image and figure processing
- **TableExtractor**: Table detection and CSV conversion

### Advanced Processing
- **EquationProcessor**: Mathematical content processing
- **AdvancedFigureProcessor**: AI-powered figure analysis
- **EnhancedMetadataExtractor**: Comprehensive metadata extraction
- **BibliographicParser**: Citation and reference processing

### Plugin System v1.1
- **PluginManager**: Core plugin management
- **DependencyManager**: Automatic dependency resolution
- **PluginMarketplace**: Community plugin ecosystem
- **EnhancedPluginSystem**: Unified management interface

### Output & Export
- **MultiFormatExporter**: Professional multi-format export
- **OutputFormatters**: Specialized format converters
- **ConfigManager**: Advanced configuration management

## 🔧 Configuration

Paper2Data uses YAML-based configuration with smart defaults:

```yaml
processing:
  max_workers: 4
  enable_caching: true
  cache_size: 1000
  
extraction:
  extract_figures: true
  extract_tables: true
  extract_equations: true
  
output:
  base_dir: "./output"
  formats: ["html", "markdown"]
  
plugins:
  auto_update: true
  security_scan: true
```

## 📊 Performance Features

- **Parallel Processing**: Multi-threaded extraction
- **Intelligent Caching**: Smart result caching
- **Memory Optimization**: Efficient memory usage
- **Batch Processing**: Process multiple documents
- **Progress Tracking**: Real-time progress monitoring

## 🔌 Plugin Ecosystem

The enhanced plugin system v1.1 provides:

- **Plugin Marketplace**: Discover and install community plugins
- **Dependency Management**: Automatic dependency resolution
- **Security Scanning**: Automated security validation
- **Health Monitoring**: Real-time plugin performance tracking
- **Auto-Updates**: Background plugin updates

## 🧪 Testing & Quality

- **100% Test Coverage**: Comprehensive test suite
- **Type Hints**: Full type annotation support
- **Linting**: Code quality enforcement
- **Performance Testing**: Benchmarking and optimization
- **Integration Testing**: End-to-end validation

## 📚 Documentation

- **API Reference**: Complete API documentation
- **Examples**: Comprehensive usage examples
- **Tutorials**: Step-by-step guides
- **Best Practices**: Recommended patterns

## 🤝 Contributing

We welcome contributions! Please see our [Contributing Guide](https://github.com/paper2data/paper2data/blob/main/CONTRIBUTING.md) for details.

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🔗 Links

- **Homepage**: https://github.com/paper2data/paper2data
- **Documentation**: https://paper2data.readthedocs.io
- **PyPI**: https://pypi.org/project/paper2data-parser/
- **Issues**: https://github.com/paper2data/paper2data/issues

## 🚀 What's New in v1.1

### Enhanced Plugin System
- Revolutionary plugin architecture with marketplace integration
- Automatic dependency resolution and conflict management
- Security scanning and health monitoring
- Background auto-updates and performance analytics

### Mathematical Processing
- Advanced LaTeX equation detection and extraction
- MathML conversion for web compatibility
- Mathematical complexity analysis
- Symbol recognition and validation

### Advanced Figure Processing
- AI-powered figure classification
- Automatic caption extraction with OCR fallback
- Image quality assessment and analysis
- Figure-text association and context analysis

### Enhanced Metadata Extraction
- Author disambiguation and institution detection
- Funding source identification and categorization
- Enhanced bibliographic data extraction
- Cross-reference validation and enrichment

### Multi-Format Export
- Professional HTML export with interactive features
- LaTeX reconstruction for academic submission
- Microsoft Word compatibility
- EPUB generation for e-book readers
- Enhanced Markdown with rich formatting

---

**Paper2Data v1.1** - Transform academic papers into structured data repositories with enterprise-grade processing capabilities. 
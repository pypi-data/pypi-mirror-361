"""
Smoke tests for Paper2Data parser package.

Tests that modules can be imported and basic functionality raises NotImplementedError
as expected during development.
"""

import pytest
import sys
from pathlib import Path

# Add the src directory to the path for testing
sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from ingest import PDFIngestor, URLIngestor, DOIIngestor, create_ingestor
from extractor import (
    ContentExtractor, 
    SectionExtractor, 
    FigureExtractor, 
    TableExtractor,
    CitationExtractor
)
from utils import (
    setup_logging,
    validate_input,
    format_output,
    clean_text,
    ProcessingError,
    ValidationError,
    ConfigurationError
)


class TestIngestors:
    """Test ingestion functionality."""
    
    def test_pdf_ingestor_import(self):
        """Test that PDFIngestor can be imported and instantiated."""
        ingestor = PDFIngestor("test.pdf")
        assert ingestor.input_source == "test.pdf"
        assert isinstance(ingestor.metadata, dict)
    
    def test_pdf_ingestor_validate_not_implemented(self):
        """Test that PDFIngestor.validate raises NotImplementedError."""
        ingestor = PDFIngestor("test.pdf")
        with pytest.raises(NotImplementedError, match="PDF validation not yet implemented"):
            ingestor.validate()
    
    def test_pdf_ingestor_ingest_not_implemented(self):
        """Test that PDFIngestor.ingest raises NotImplementedError."""
        ingestor = PDFIngestor("test.pdf")
        with pytest.raises(NotImplementedError, match="PDF loading not yet implemented"):
            ingestor.ingest()
    
    def test_url_ingestor_import(self):
        """Test that URLIngestor can be imported and instantiated."""
        ingestor = URLIngestor("https://arxiv.org/abs/1234.5678")
        assert "arxiv.org" in ingestor.input_source
    
    def test_url_ingestor_not_implemented(self):
        """Test that URLIngestor methods raise NotImplementedError."""
        ingestor = URLIngestor("https://arxiv.org/abs/1234.5678")
        with pytest.raises(NotImplementedError):
            ingestor.validate()
        with pytest.raises(NotImplementedError):
            ingestor.ingest()
    
    def test_doi_ingestor_import(self):
        """Test that DOIIngestor can be imported and instantiated."""
        ingestor = DOIIngestor("10.1038/nature12373")
        assert "10.1038" in ingestor.input_source
    
    def test_doi_ingestor_not_implemented(self):
        """Test that DOIIngestor methods raise NotImplementedError."""
        ingestor = DOIIngestor("10.1038/nature12373")
        with pytest.raises(NotImplementedError):
            ingestor.validate()
        with pytest.raises(NotImplementedError):
            ingestor.ingest()
    
    def test_create_ingestor_not_implemented(self):
        """Test that create_ingestor factory raises NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Ingestor factory not yet implemented"):
            create_ingestor("test.pdf")


class TestExtractors:
    """Test extraction functionality."""
    
    def test_content_extractor_import(self):
        """Test that ContentExtractor can be imported and instantiated."""
        extractor = ContentExtractor(b"fake pdf content")
        assert extractor.pdf_content == b"fake pdf content"
        assert isinstance(extractor.extracted_data, dict)
    
    def test_content_extractor_not_implemented(self):
        """Test that ContentExtractor methods raise NotImplementedError."""
        extractor = ContentExtractor(b"fake pdf content")
        with pytest.raises(NotImplementedError, match="Content extraction not yet implemented"):
            extractor.extract()
        with pytest.raises(NotImplementedError, match="Text extraction not yet implemented"):
            extractor.extract_text()
        with pytest.raises(NotImplementedError, match="Metadata extraction not yet implemented"):
            extractor.extract_metadata()
    
    def test_section_extractor_not_implemented(self):
        """Test that SectionExtractor methods raise NotImplementedError."""
        extractor = SectionExtractor(b"fake pdf content")
        with pytest.raises(NotImplementedError):
            extractor.extract()
        with pytest.raises(NotImplementedError):
            extractor.detect_sections("sample text")
        with pytest.raises(NotImplementedError):
            extractor.format_as_markdown([])
    
    def test_figure_extractor_not_implemented(self):
        """Test that FigureExtractor methods raise NotImplementedError."""
        extractor = FigureExtractor(b"fake pdf content")
        with pytest.raises(NotImplementedError):
            extractor.extract()
        with pytest.raises(NotImplementedError):
            extractor.extract_images()
        with pytest.raises(NotImplementedError):
            extractor.extract_captions()
        with pytest.raises(NotImplementedError):
            extractor.save_figures(Path("/tmp"))
    
    def test_table_extractor_not_implemented(self):
        """Test that TableExtractor methods raise NotImplementedError."""
        extractor = TableExtractor(b"fake pdf content")
        with pytest.raises(NotImplementedError):
            extractor.extract()
        with pytest.raises(NotImplementedError):
            extractor.detect_tables()
        with pytest.raises(NotImplementedError):
            extractor.convert_to_csv([], Path("/tmp"))
    
    def test_citation_extractor_not_implemented(self):
        """Test that CitationExtractor methods raise NotImplementedError."""
        extractor = CitationExtractor(b"fake pdf content")
        with pytest.raises(NotImplementedError):
            extractor.extract()
        with pytest.raises(NotImplementedError):
            extractor.extract_bibliography()
        with pytest.raises(NotImplementedError):
            extractor.extract_inline_citations()


class TestUtils:
    """Test utility functionality."""
    
    def test_utility_functions_not_implemented(self):
        """Test that utility functions raise NotImplementedError."""
        with pytest.raises(NotImplementedError, match="Logging setup not yet implemented"):
            setup_logging()
        
        with pytest.raises(NotImplementedError, match="Input validation not yet implemented"):
            validate_input("test.pdf")
        
        with pytest.raises(NotImplementedError, match="Output formatting not yet implemented"):
            format_output({"test": "data"})
        
        with pytest.raises(NotImplementedError, match="Text cleaning not yet implemented"):
            clean_text("sample text")
    
    def test_custom_exceptions_exist(self):
        """Test that custom exception classes can be instantiated."""
        assert issubclass(ProcessingError, Exception)
        assert issubclass(ValidationError, Exception)
        assert issubclass(ConfigurationError, Exception)
        
        # Test that they can be raised
        with pytest.raises(ProcessingError):
            raise ProcessingError("Test processing error")
        
        with pytest.raises(ValidationError):
            raise ValidationError("Test validation error")
        
        with pytest.raises(ConfigurationError):
            raise ConfigurationError("Test configuration error")


class TestPackageStructure:
    """Test overall package structure and imports."""
    
    def test_package_import(self):
        """Test that the main package can be imported."""
        # This will test the __init__.py imports
        import sys
        sys.path.insert(0, str(Path(__file__).parent.parent / "src"))
        
        # Test individual imports work (even though they'll raise NotImplementedError when called)
        from ingest import PDFIngestor, URLIngestor, DOIIngestor
        from extractor import ContentExtractor, SectionExtractor, FigureExtractor, TableExtractor
        from utils import setup_logging, validate_input, format_output
        
        # Basic smoke test - can we create instances?
        pdf_ingestor = PDFIngestor("test.pdf")
        content_extractor = ContentExtractor(b"test")
        
        assert pdf_ingestor is not None
        assert content_extractor is not None


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
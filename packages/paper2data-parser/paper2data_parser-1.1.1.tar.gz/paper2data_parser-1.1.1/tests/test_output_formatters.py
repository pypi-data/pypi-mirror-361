"""
Comprehensive tests for output formatters functionality.
"""

import unittest
import tempfile
import os
import json
import csv
import xml.etree.ElementTree as ET
from datetime import datetime
from unittest.mock import patch, MagicMock

from paper2data.output_formatters import (
    OutputFormat, FormatConfig, BaseFormatter,
    JSONFormatter, HTMLFormatter, LaTeXFormatter,
    XMLFormatter, CSVFormatter, MarkdownFormatter,
    DOCXFormatter, FormatterFactory,
    format_output, batch_format,
    export_to_html, export_to_latex, export_to_xml,
    export_to_csv, export_to_markdown, export_all_formats
)


class TestOutputFormat(unittest.TestCase):
    """Test OutputFormat enum"""
    
    def test_output_format_values(self):
        """Test output format enum values"""
        self.assertEqual(OutputFormat.JSON.value, "json")
        self.assertEqual(OutputFormat.HTML.value, "html")
        self.assertEqual(OutputFormat.LATEX.value, "latex")
        self.assertEqual(OutputFormat.XML.value, "xml")
        self.assertEqual(OutputFormat.CSV.value, "csv")
        self.assertEqual(OutputFormat.MARKDOWN.value, "markdown")
        self.assertEqual(OutputFormat.DOCX.value, "docx")
        self.assertEqual(OutputFormat.PDF.value, "pdf")


class TestFormatConfig(unittest.TestCase):
    """Test FormatConfig dataclass"""
    
    def test_default_config(self):
        """Test default configuration values"""
        config = FormatConfig()
        
        # Check default inclusion flags
        self.assertTrue(config.include_metadata)
        self.assertTrue(config.include_figures)
        self.assertTrue(config.include_tables)
        self.assertTrue(config.include_equations)
        self.assertTrue(config.include_citations)
        self.assertTrue(config.include_networks)
        self.assertTrue(config.include_statistics)
        
        # Check format-specific defaults
        self.assertTrue(config.html_include_css)
        self.assertFalse(config.html_embed_images)
        self.assertEqual(config.latex_document_class, "article")
        self.assertEqual(config.csv_delimiter, ",")
        self.assertTrue(config.xml_pretty_print)
        self.assertTrue(config.markdown_include_toc)
        
        # Check LaTeX packages
        expected_packages = ["amsmath", "graphicx", "hyperref", "booktabs"]
        self.assertEqual(config.latex_packages, expected_packages)
    
    def test_custom_config(self):
        """Test custom configuration"""
        config = FormatConfig(
            include_metadata=False,
            include_figures=False,
            html_include_css=False,
            csv_delimiter=";",
            latex_document_class="report",
            latex_packages=["amsmath"]
        )
        
        self.assertFalse(config.include_metadata)
        self.assertFalse(config.include_figures)
        self.assertFalse(config.html_include_css)
        self.assertEqual(config.csv_delimiter, ";")
        self.assertEqual(config.latex_document_class, "report")
        self.assertEqual(config.latex_packages, ["amsmath"])


class TestBaseFormatter(unittest.TestCase):
    """Test BaseFormatter abstract class"""
    
    def setUp(self):
        """Set up test fixtures"""
        # Create concrete implementation for testing
        class TestFormatter(BaseFormatter):
            def format(self, data, output_path):
                return True
        
        self.formatter = TestFormatter()
        
        # Sample data for testing
        self.sample_data = {
            "extraction_timestamp": "2023-01-01T12:00:00",
            "metadata": {
                "title": "Test Paper",
                "authors": [{"name": "John Doe"}, {"name": "Jane Smith"}]
            },
            "content": {
                "full_text": "This is a test paper.",
                "statistics": {"page_count": 5, "word_count": 1000}
            }
        }
    
    def test_validate_data_valid(self):
        """Test data validation with valid data"""
        result = self.formatter._validate_data(self.sample_data)
        self.assertTrue(result)
    
    def test_validate_data_invalid(self):
        """Test data validation with invalid data"""
        invalid_data = {"content": "test"}
        result = self.formatter._validate_data(invalid_data)
        self.assertFalse(result)
    
    def test_get_title_from_metadata(self):
        """Test title extraction from metadata"""
        title = self.formatter._get_title(self.sample_data)
        self.assertEqual(title, "Test Paper")
    
    def test_get_title_from_content(self):
        """Test title extraction from content"""
        data = {
            "content": {"title": "Content Title"},
            "metadata": {}
        }
        title = self.formatter._get_title(data)
        self.assertEqual(title, "Content Title")
    
    def test_get_title_default(self):
        """Test default title when none found"""
        data = {"extraction_timestamp": "2023-01-01T12:00:00"}
        title = self.formatter._get_title(data)
        self.assertEqual(title, "Document Analysis Results")
    
    def test_format_timestamp(self):
        """Test timestamp formatting"""
        timestamp = "2023-01-01T12:00:00"
        formatted = self.formatter._format_timestamp(timestamp)
        self.assertEqual(formatted, "2023-01-01 12:00:00")
    
    def test_format_timestamp_invalid(self):
        """Test timestamp formatting with invalid input"""
        timestamp = "invalid_timestamp"
        formatted = self.formatter._format_timestamp(timestamp)
        self.assertEqual(formatted, "invalid_timestamp")


class TestJSONFormatter(unittest.TestCase):
    """Test JSONFormatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = JSONFormatter()
        self.sample_data = {
            "extraction_timestamp": "2023-01-01T12:00:00",
            "metadata": {"title": "Test Paper"},
            "content": {"full_text": "Test content"},
            "summary": {"total_pages": 5}
        }
    
    def test_format_success(self):
        """Test successful JSON formatting"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            success = self.formatter.format(self.sample_data, output_path)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_path))
            
            # Verify JSON content
            with open(output_path, 'r') as f:
                data = json.load(f)
                self.assertIn("extraction_timestamp", data)
                self.assertIn("metadata", data)
                self.assertIn("content", data)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_filter_data(self):
        """Test data filtering based on configuration"""
        config = FormatConfig(include_metadata=False, include_statistics=False)
        formatter = JSONFormatter(config)
        
        filtered = formatter._filter_data(self.sample_data)
        
        self.assertIn("extraction_timestamp", filtered)
        self.assertIn("content", filtered)
        self.assertNotIn("metadata", filtered)
        self.assertNotIn("summary", filtered)


class TestHTMLFormatter(unittest.TestCase):
    """Test HTMLFormatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = HTMLFormatter()
        self.sample_data = {
            "extraction_timestamp": "2023-01-01T12:00:00",
            "metadata": {
                "title": "Test Paper",
                "authors": [{"name": "John Doe"}],
                "abstract": "This is a test abstract."
            },
            "content": {
                "full_text": "Test content",
                "statistics": {"page_count": 5, "word_count": 1000}
            },
            "figures": {
                "figures": [{"caption": "Test Figure", "page": 1}]
            },
            "tables": {
                "tables": [{"caption": "Test Table", "data": [["A", "B"], ["1", "2"]]}]
            },
            "summary": {"total_pages": 5, "total_words": 1000}
        }
    
    def test_format_success(self):
        """Test successful HTML formatting"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            success = self.formatter.format(self.sample_data, output_path)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_path))
            
            # Verify HTML content
            with open(output_path, 'r') as f:
                html_content = f.read()
                self.assertIn("<!DOCTYPE html>", html_content)
                self.assertIn("Test Paper", html_content)
                self.assertIn("Table of Contents", html_content)
                self.assertIn("Document Metadata", html_content)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_css_inclusion(self):
        """Test CSS inclusion in HTML"""
        config = FormatConfig(html_include_css=True)
        formatter = HTMLFormatter(config)
        
        header = formatter._get_html_header("Test Title")
        self.assertIn("<style>", header)
        self.assertIn("body {", header)
    
    def test_css_exclusion(self):
        """Test CSS exclusion from HTML"""
        config = FormatConfig(html_include_css=False)
        formatter = HTMLFormatter(config)
        
        header = formatter._get_html_header("Test Title")
        self.assertNotIn("<style>", header)


class TestLaTeXFormatter(unittest.TestCase):
    """Test LaTeXFormatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = LaTeXFormatter()
        self.sample_data = {
            "extraction_timestamp": "2023-01-01T12:00:00",
            "metadata": {
                "title": "Test Paper",
                "authors": [{"name": "John Doe"}]
            },
            "content": {"full_text": "Test content"},
            "tables": {
                "tables": [{"caption": "Test Table", "headers": ["A", "B"], "data": [["1", "2"]]}]
            }
        }
    
    def test_format_success(self):
        """Test successful LaTeX formatting"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            output_path = f.name
        
        try:
            success = self.formatter.format(self.sample_data, output_path)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_path))
            
            # Verify LaTeX content
            with open(output_path, 'r') as f:
                latex_content = f.read()
                self.assertIn("\\documentclass", latex_content)
                self.assertIn("\\begin{document}", latex_content)
                self.assertIn("\\end{document}", latex_content)
                self.assertIn("Test Paper", latex_content)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_escape_latex(self):
        """Test LaTeX character escaping"""
        test_text = "Test & special $ characters # in % text"
        escaped = self.formatter._escape_latex(test_text)
        
        self.assertIn("\\&", escaped)
        self.assertIn("\\$", escaped)
        self.assertIn("\\#", escaped)
        self.assertIn("\\%", escaped)
    
    def test_custom_document_class(self):
        """Test custom document class"""
        config = FormatConfig(latex_document_class="report")
        formatter = LaTeXFormatter(config)
        
        header = formatter._get_latex_header("Test Title")
        self.assertIn("\\documentclass[12pt]{report}", header)


class TestXMLFormatter(unittest.TestCase):
    """Test XMLFormatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = XMLFormatter()
        self.sample_data = {
            "extraction_timestamp": "2023-01-01T12:00:00",
            "metadata": {
                "title": "Test Paper",
                "authors": [{"name": "John Doe"}]
            },
            "content": {"full_text": "Test content"}
        }
    
    def test_format_success(self):
        """Test successful XML formatting"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            output_path = f.name
        
        try:
            success = self.formatter.format(self.sample_data, output_path)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_path))
            
            # Verify XML content
            with open(output_path, 'r') as f:
                xml_content = f.read()
                self.assertIn("<?xml version", xml_content)
                self.assertIn("<paper2data_analysis", xml_content)
                self.assertIn("<title>Test Paper</title>", xml_content)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_sanitize_xml_tag(self):
        """Test XML tag sanitization"""
        # Test various invalid characters
        test_cases = [
            ("test-tag", "test-tag"),
            ("test tag", "test_tag"),
            ("123tag", "_123tag"),
            ("special@char", "special_char"),
            ("", "element")
        ]
        
        for input_tag, expected in test_cases:
            result = self.formatter._sanitize_xml_tag(input_tag)
            self.assertEqual(result, expected)
    
    def test_pretty_print_enabled(self):
        """Test pretty-printed XML output"""
        config = FormatConfig(xml_pretty_print=True)
        formatter = XMLFormatter(config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            output_path = f.name
        
        try:
            success = formatter.format(self.sample_data, output_path)
            self.assertTrue(success)
            
            with open(output_path, 'r') as f:
                xml_content = f.read()
                # Pretty-printed XML should have indentation
                lines = xml_content.split('\n')
                indented_lines = [line for line in lines if line.startswith('  ')]
                self.assertGreater(len(indented_lines), 0)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestCSVFormatter(unittest.TestCase):
    """Test CSVFormatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = CSVFormatter()
        self.sample_data = {
            "extraction_timestamp": "2023-01-01T12:00:00",
            "metadata": {
                "title": "Test Paper",
                "authors": [{"name": "John Doe"}]
            },
            "summary": {"total_pages": 5, "total_words": 1000},
            "tables": {
                "tables": [{"caption": "Test Table", "data": [["A", "B"], ["1", "2"]]}]
            },
            "citations": {
                "references": [{"text": "Test citation", "authors": ["Author"]}]
            }
        }
    
    def test_format_success(self):
        """Test successful CSV formatting"""
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.csv")
            
            success = self.formatter.format(self.sample_data, output_path)
            self.assertTrue(success)
            
            # Check that multiple CSV files were created
            csv_files = [f for f in os.listdir(temp_dir) if f.endswith('.csv')]
            self.assertGreater(len(csv_files), 0)
            
            # Check statistics CSV
            stats_file = os.path.join(temp_dir, "test_statistics.csv")
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    reader = csv.reader(f)
                    rows = list(reader)
                    self.assertGreater(len(rows), 1)  # Header + data
                    self.assertEqual(rows[0], ["Metric", "Value"])
    
    def test_custom_delimiter(self):
        """Test custom CSV delimiter"""
        config = FormatConfig(csv_delimiter=";")
        formatter = CSVFormatter(config)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            output_path = os.path.join(temp_dir, "test.csv")
            
            success = formatter.format(self.sample_data, output_path)
            self.assertTrue(success)
            
            # Check delimiter in statistics file
            stats_file = os.path.join(temp_dir, "test_statistics.csv")
            if os.path.exists(stats_file):
                with open(stats_file, 'r') as f:
                    content = f.read()
                    self.assertIn(";", content)
    
    def test_flatten_dict(self):
        """Test dictionary flattening for CSV"""
        nested_dict = {
            "level1": {
                "level2": {
                    "value": "test"
                },
                "simple": "value"
            },
            "list": ["a", "b", "c"]
        }
        
        flattened = self.formatter._flatten_dict(nested_dict)
        
        self.assertIn("level1.level2.value", flattened)
        self.assertEqual(flattened["level1.level2.value"], "test")
        self.assertEqual(flattened["level1.simple"], "value")
        self.assertEqual(flattened["list"], "a; b; c")


class TestMarkdownFormatter(unittest.TestCase):
    """Test MarkdownFormatter"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.formatter = MarkdownFormatter()
        self.sample_data = {
            "extraction_timestamp": "2023-01-01T12:00:00",
            "metadata": {
                "title": "Test Paper",
                "authors": [{"name": "John Doe"}],
                "doi": "10.1234/test"
            },
            "content": {
                "full_text": "Test content",
                "statistics": {"page_count": 5}
            },
            "summary": {"total_pages": 5, "total_words": 1000}
        }
    
    def test_format_success(self):
        """Test successful Markdown formatting"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
            output_path = f.name
        
        try:
            success = self.formatter.format(self.sample_data, output_path)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_path))
            
            # Verify Markdown content
            with open(output_path, 'r') as f:
                md_content = f.read()
                self.assertIn("# Test Paper", md_content)
                self.assertIn("## Table of Contents", md_content)
                self.assertIn("## Document Metadata", md_content)
                self.assertIn("**Authors:**", md_content)
                self.assertIn("**DOI:**", md_content)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_toc_inclusion(self):
        """Test table of contents inclusion"""
        config = FormatConfig(markdown_include_toc=True)
        formatter = MarkdownFormatter(config)
        
        md_content = formatter._generate_markdown(self.sample_data)
        self.assertIn("## Table of Contents", md_content)
    
    def test_toc_exclusion(self):
        """Test table of contents exclusion"""
        config = FormatConfig(markdown_include_toc=False)
        formatter = MarkdownFormatter(config)
        
        md_content = formatter._generate_markdown(self.sample_data)
        self.assertNotIn("## Table of Contents", md_content)


class TestDOCXFormatter(unittest.TestCase):
    """Test DOCXFormatter"""
    
    def test_format_not_implemented(self):
        """Test DOCX formatter returns False (not implemented)"""
        formatter = DOCXFormatter()
        sample_data = {"extraction_timestamp": "2023-01-01T12:00:00"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.docx', delete=False) as f:
            output_path = f.name
        
        try:
            success = formatter.format(sample_data, output_path)
            self.assertFalse(success)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestFormatterFactory(unittest.TestCase):
    """Test FormatterFactory"""
    
    def test_create_formatter_json(self):
        """Test creating JSON formatter"""
        formatter = FormatterFactory.create_formatter(OutputFormat.JSON)
        self.assertIsInstance(formatter, JSONFormatter)
    
    def test_create_formatter_html(self):
        """Test creating HTML formatter"""
        formatter = FormatterFactory.create_formatter(OutputFormat.HTML)
        self.assertIsInstance(formatter, HTMLFormatter)
    
    def test_create_formatter_with_config(self):
        """Test creating formatter with custom config"""
        config = FormatConfig(include_metadata=False)
        formatter = FormatterFactory.create_formatter(OutputFormat.JSON, config)
        self.assertIsInstance(formatter, JSONFormatter)
        self.assertFalse(formatter.config.include_metadata)
    
    def test_create_formatter_unsupported(self):
        """Test creating formatter for unsupported format"""
        with self.assertRaises(ValueError):
            FormatterFactory.create_formatter("unsupported_format")
    
    def test_get_supported_formats(self):
        """Test getting supported formats"""
        formats = FormatterFactory.get_supported_formats()
        self.assertIn(OutputFormat.JSON, formats)
        self.assertIn(OutputFormat.HTML, formats)
        self.assertIn(OutputFormat.LATEX, formats)
        self.assertIn(OutputFormat.XML, formats)
        self.assertIn(OutputFormat.CSV, formats)
        self.assertIn(OutputFormat.MARKDOWN, formats)


class TestGlobalFunctions(unittest.TestCase):
    """Test global convenience functions"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.sample_data = {
            "extraction_timestamp": "2023-01-01T12:00:00",
            "metadata": {"title": "Test Paper"},
            "content": {"full_text": "Test content"}
        }
    
    def test_format_output_json(self):
        """Test format_output function with JSON"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            success = format_output(self.sample_data, output_path, OutputFormat.JSON)
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_path))
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_format_output_string_format(self):
        """Test format_output function with string format"""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            success = format_output(self.sample_data, output_path, "html")
            self.assertTrue(success)
            self.assertTrue(os.path.exists(output_path))
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_batch_format(self):
        """Test batch formatting to multiple formats"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = os.path.join(temp_dir, "test")
            formats = [OutputFormat.JSON, OutputFormat.HTML, OutputFormat.MARKDOWN]
            
            results = batch_format(self.sample_data, base_path, formats)
            
            self.assertEqual(len(results), 3)
            self.assertTrue(results["json"])
            self.assertTrue(results["html"])
            self.assertTrue(results["markdown"])
            
            # Check files exist
            self.assertTrue(os.path.exists(f"{base_path}.json"))
            self.assertTrue(os.path.exists(f"{base_path}.html"))
            self.assertTrue(os.path.exists(f"{base_path}.markdown"))
    
    def test_export_convenience_functions(self):
        """Test convenience export functions"""
        with tempfile.TemporaryDirectory() as temp_dir:
            # Test each convenience function
            functions_and_extensions = [
                (export_to_html, "html"),
                (export_to_latex, "tex"),
                (export_to_xml, "xml"),
                (export_to_csv, "csv"),
                (export_to_markdown, "md")
            ]
            
            for export_func, ext in functions_and_extensions:
                output_path = os.path.join(temp_dir, f"test.{ext}")
                success = export_func(self.sample_data, output_path)
                self.assertTrue(success, f"Failed to export to {ext}")
    
    def test_export_all_formats(self):
        """Test exporting to all supported formats"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = os.path.join(temp_dir, "test")
            
            results = export_all_formats(self.sample_data, base_path)
            
            # Should have results for all major formats
            expected_formats = ["json", "html", "latex", "xml", "csv", "markdown"]
            for fmt in expected_formats:
                self.assertIn(fmt, results)
                self.assertTrue(results[fmt], f"Failed to export {fmt}")


class TestErrorHandling(unittest.TestCase):
    """Test error handling in formatters"""
    
    def test_invalid_output_path(self):
        """Test handling of invalid output path"""
        formatter = JSONFormatter()
        sample_data = {"extraction_timestamp": "2023-01-01T12:00:00"}
        
        # Try to write to invalid path
        invalid_path = "/invalid/path/test.json"
        success = formatter.format(sample_data, invalid_path)
        self.assertFalse(success)
    
    def test_malformed_data(self):
        """Test handling of malformed data"""
        formatter = HTMLFormatter()
        
        # Test with missing required fields
        malformed_data = {"some_field": "value"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            # Should not crash, but might produce different output
            success = formatter.format(malformed_data, output_path)
            # Function should complete (might be True or False depending on implementation)
            self.assertIsInstance(success, bool)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_format_output_invalid_format(self):
        """Test format_output with invalid format string"""
        sample_data = {"extraction_timestamp": "2023-01-01T12:00:00"}
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as f:
            output_path = f.name
        
        try:
            success = format_output(sample_data, output_path, "invalid_format")
            self.assertFalse(success)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestIntegration(unittest.TestCase):
    """Integration tests for output formatters"""
    
    def setUp(self):
        """Set up comprehensive test data"""
        self.comprehensive_data = {
            "extraction_timestamp": "2023-01-01T12:00:00",
            "metadata": {
                "title": "Comprehensive Test Paper",
                "authors": [
                    {"name": "John Doe", "position": 1},
                    {"name": "Jane Smith", "position": 2}
                ],
                "publication_info": {
                    "year": 2023,
                    "journal": "Test Journal",
                    "volume": "1",
                    "issue": "1"
                },
                "doi": "10.1234/test.2023",
                "keywords": ["test", "paper", "comprehensive"],
                "abstract": "This is a comprehensive test paper abstract."
            },
            "content": {
                "full_text": "This is the full text of the test paper. " * 50,
                "statistics": {
                    "page_count": 10,
                    "word_count": 2500,
                    "character_count": 15000
                }
            },
            "sections": {
                "sections": [
                    {"title": "Introduction", "content": "Introduction content"},
                    {"title": "Methods", "content": "Methods content"},
                    {"title": "Results", "content": "Results content"},
                    {"title": "Conclusion", "content": "Conclusion content"}
                ],
                "section_count": 4
            },
            "figures": {
                "figures": [
                    {"caption": "Test Figure 1", "page": 1},
                    {"caption": "Test Figure 2", "page": 2}
                ],
                "figure_count": 2
            },
            "tables": {
                "tables": [
                    {
                        "caption": "Test Table 1",
                        "headers": ["Column A", "Column B", "Column C"],
                        "data": [["1", "2", "3"], ["4", "5", "6"], ["7", "8", "9"]],
                        "page": 3
                    }
                ],
                "total_tables": 1
            },
            "equations": {
                "equations": [
                    {
                        "text": "E = mc^2",
                        "latex": "E = mc^2",
                        "page": 4,
                        "confidence": 0.95
                    }
                ],
                "total_equations": 1
            },
            "citations": {
                "references": [
                    {
                        "text": "Smith, J. (2022). Test Reference. Test Journal, 1(1), 1-10.",
                        "authors": ["Smith, J."],
                        "title": "Test Reference",
                        "year": 2022,
                        "journal": "Test Journal"
                    }
                ],
                "reference_count": 1
            },
            "citation_networks": {
                "networks": {
                    "citation": {
                        "basic_metrics": {
                            "num_nodes": 5,
                            "num_edges": 3,
                            "density": 0.15
                        }
                    }
                },
                "processing_status": "completed"
            },
            "summary": {
                "total_pages": 10,
                "total_words": 2500,
                "sections_found": 4,
                "figures_found": 2,
                "tables_found": 1,
                "references_found": 1,
                "equations_found": 1,
                "metadata_extracted": True,
                "authors_found": 2,
                "keywords_found": 3,
                "doi_found": True
            }
        }
    
    def test_all_formats_comprehensive(self):
        """Test all formats with comprehensive data"""
        with tempfile.TemporaryDirectory() as temp_dir:
            base_path = os.path.join(temp_dir, "comprehensive_test")
            
            # Test each major format
            formats_to_test = [
                OutputFormat.JSON,
                OutputFormat.HTML,
                OutputFormat.LATEX,
                OutputFormat.XML,
                OutputFormat.CSV,
                OutputFormat.MARKDOWN
            ]
            
            for fmt in formats_to_test:
                output_path = f"{base_path}.{fmt.value}"
                success = format_output(self.comprehensive_data, output_path, fmt)
                self.assertTrue(success, f"Failed to format {fmt.value}")
                self.assertTrue(os.path.exists(output_path), f"Output file not created for {fmt.value}")
                
                # Basic content verification
                if fmt == OutputFormat.JSON:
                    with open(output_path, 'r') as f:
                        data = json.load(f)
                        self.assertIn("metadata", data)
                        self.assertEqual(data["metadata"]["title"], "Comprehensive Test Paper")
                
                elif fmt in [OutputFormat.HTML, OutputFormat.LATEX, OutputFormat.MARKDOWN]:
                    with open(output_path, 'r') as f:
                        content = f.read()
                        self.assertIn("Comprehensive Test Paper", content)
                        self.assertIn("John Doe", content)
    
    def test_selective_inclusion(self):
        """Test selective content inclusion"""
        config = FormatConfig(
            include_figures=False,
            include_tables=False,
            include_equations=False
        )
        
        formatter = HTMLFormatter(config)
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = f.name
        
        try:
            success = formatter.format(self.comprehensive_data, output_path)
            self.assertTrue(success)
            
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertNotIn("Figures & Images", content)
                self.assertNotIn("Tables", content)
                self.assertNotIn("Mathematical Equations", content)
                self.assertIn("Document Metadata", content)  # Should still be included
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


if __name__ == '__main__':
    unittest.main() 
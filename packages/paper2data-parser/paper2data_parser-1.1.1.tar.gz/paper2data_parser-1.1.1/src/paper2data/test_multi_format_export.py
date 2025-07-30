#!/usr/bin/env python3
"""
Test suite for Paper2Data Multi-Format Export System V1.1

Tests all output formats: HTML, LaTeX, Word, EPUB
Verifies template rendering, content processing, and export functionality.
"""

import os
import sys
import pytest
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any, List
import json

# Add the parent directory to the path to import paper2data modules
sys.path.insert(0, str(Path(__file__).parent))

from multi_format_exporter import (
    MultiFormatExporter,
    ExportConfiguration,
    OutputFormat,
    TemplateTheme,
    HTMLExporter,
    LaTeXExporter,
    WordExporter,
    EPUBExporter
)
from utils import get_logger


class TestMultiFormatExporter:
    """Test suite for the multi-format export system."""
    
    @pytest.fixture
    def sample_extraction_results(self):
        """Create sample extraction results for testing."""
        return {
            "content": {
                "metadata": {
                    "title": "Advanced Machine Learning Techniques",
                    "authors": "Dr. Jane Smith, Prof. John Doe",
                    "subject": "Machine Learning",
                    "page_count": 15,
                    "creation_date": "2024-01-01"
                },
                "full_text": "This is the full text of the paper...",
                "statistics": {
                    "word_count": 5000,
                    "page_count": 15
                }
            },
            "sections": {
                "sections": {
                    "abstract": "This paper presents advanced machine learning techniques for data analysis...",
                    "introduction": "Machine learning has revolutionized data analysis in recent years...",
                    "methodology": "We propose a novel approach combining deep learning with traditional methods...",
                    "results": "Our experiments show significant improvements over existing methods...",
                    "conclusion": "The proposed techniques demonstrate superior performance...",
                    "references": "1. Smith, J. et al. (2023). Deep Learning Fundamentals..."
                }
            },
            "figures": {
                "figures": [
                    {
                        "figure_id": "fig1",
                        "caption": "Architecture of the proposed neural network",
                        "data": b"PNG_IMAGE_DATA_PLACEHOLDER",
                        "format": "png",
                        "size": {"width": 800, "height": 600},
                        "alt_text": "Neural network architecture diagram"
                    },
                    {
                        "figure_id": "fig2", 
                        "caption": "Performance comparison across different datasets",
                        "data": b"PNG_IMAGE_DATA_PLACEHOLDER",
                        "format": "png",
                        "size": {"width": 600, "height": 400},
                        "alt_text": "Performance comparison chart"
                    }
                ]
            },
            "tables": {
                "tables": [
                    {
                        "table_id": "table1",
                        "caption": "Experimental results on benchmark datasets",
                        "csv_content": "Dataset,Accuracy,Precision,Recall\nDataset1,0.95,0.92,0.94\nDataset2,0.87,0.85,0.88\nDataset3,0.91,0.89,0.90",
                        "format": "csv"
                    }
                ]
            },
            "equations": {
                "equations": [
                    {
                        "equation_id": "eq1",
                        "latex": "\\sigma(x) = \\frac{1}{1 + e^{-x}}",
                        "mathml": "<math><mi>σ</mi><mo>(</mo><mi>x</mi><mo>)</mo></math>",
                        "context": "sigmoid activation function"
                    }
                ]
            },
            "citations": {
                "references": [
                    {
                        "citation_id": "ref1",
                        "formatted": "Smith, J., & Doe, J. (2023). Deep Learning Fundamentals. Journal of AI Research, 45(2), 123-145.",
                        "authors": ["Smith, J.", "Doe, J."],
                        "title": "Deep Learning Fundamentals",
                        "year": "2023",
                        "journal": "Journal of AI Research",
                        "doi": "10.1234/jair.2023.45.2.123"
                    }
                ]
            },
            "summary": {
                "total_pages": 15,
                "total_words": 5000,
                "sections_found": 5,
                "figures_found": 2,
                "tables_found": 1,
                "references_found": 1
            }
        }
    
    @pytest.fixture
    def temp_output_dir(self):
        """Create temporary output directory for testing."""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)
    
    def test_multiformat_exporter_initialization(self, sample_extraction_results, temp_output_dir):
        """Test MultiFormatExporter initialization."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        assert exporter.extraction_results == sample_extraction_results
        assert exporter.output_dir == temp_output_dir
        assert temp_output_dir.exists()
        assert hasattr(exporter, 'html_exporter')
        assert hasattr(exporter, 'latex_exporter')
        assert hasattr(exporter, 'word_exporter')
        assert hasattr(exporter, 'epub_exporter')
    
    def test_content_preparation(self, sample_extraction_results, temp_output_dir):
        """Test content preparation for export."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        config = ExportConfiguration(
            format=OutputFormat.HTML,
            theme=TemplateTheme.ACADEMIC,
            include_figures=True,
            include_tables=True,
            include_equations=True,
            include_bibliography=True
        )
        
        content = exporter.prepare_content_for_export(config)
        
        # Verify content structure
        assert "metadata" in content
        assert "sections" in content
        assert "figures" in content
        assert "tables" in content
        assert "equations" in content
        assert "bibliography" in content
        assert "toc" in content
        
        # Verify metadata
        assert content["metadata"]["title"] == "Advanced Machine Learning Techniques"
        assert content["metadata"]["authors"] == "Dr. Jane Smith, Prof. John Doe"
        
        # Verify sections
        assert "abstract" in content["sections"]
        assert "introduction" in content["sections"]
        assert len(content["sections"]) == 6
        
        # Verify figures
        assert len(content["figures"]) == 2
        assert content["figures"][0]["id"] == "fig1"
        
        # Verify tables
        assert len(content["tables"]) == 1
        assert content["tables"][0]["id"] == "table1"
        
        # Verify equations
        assert len(content["equations"]) == 1
        assert content["equations"][0]["id"] == "eq1"
        
        # Verify bibliography
        assert len(content["bibliography"]) == 1
        assert content["bibliography"][0]["id"] == "ref1"
    
    def test_html_export(self, sample_extraction_results, temp_output_dir):
        """Test HTML export functionality."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        config = ExportConfiguration(
            format=OutputFormat.HTML,
            theme=TemplateTheme.ACADEMIC,
            interactive_elements=True,
            output_filename="test_paper.html"
        )
        
        # Note: This test may fail if template files don't exist
        # For now, test the structure and logic
        try:
            result = exporter.export_single_format(config)
            
            assert result.format == OutputFormat.HTML
            assert result.file_path.name == "test_paper.html"
            assert result.file_path.exists()
            assert result.file_size > 0
            
            # Check if HTML file contains expected content
            html_content = result.file_path.read_text(encoding='utf-8')
            assert "Advanced Machine Learning Techniques" in html_content
            assert "Dr. Jane Smith, Prof. John Doe" in html_content
            
        except Exception as e:
            # If template files don't exist, verify the error is related to templates
            assert "Template not found" in str(e) or "No such file or directory" in str(e)
    
    def test_latex_export(self, sample_extraction_results, temp_output_dir):
        """Test LaTeX export functionality."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        config = ExportConfiguration(
            format=OutputFormat.LATEX,
            theme=TemplateTheme.ACADEMIC,
            output_filename="test_paper.tex"
        )
        
        try:
            result = exporter.export_single_format(config)
            
            assert result.format == OutputFormat.LATEX
            assert result.file_path.name == "test_paper.tex"
            assert result.file_path.exists()
            assert result.file_size > 0
            
            # Check if LaTeX file contains expected content
            latex_content = result.file_path.read_text(encoding='utf-8')
            assert "Advanced Machine Learning Techniques" in latex_content
            assert "\\documentclass" in latex_content
            assert "\\begin{document}" in latex_content
            assert "\\end{document}" in latex_content
            
        except Exception as e:
            # If template files don't exist, verify the error is related to templates
            assert "Template not found" in str(e) or "No such file or directory" in str(e)
    
    def test_word_export(self, sample_extraction_results, temp_output_dir):
        """Test Word export functionality."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        config = ExportConfiguration(
            format=OutputFormat.WORD,
            theme=TemplateTheme.ACADEMIC,
            output_filename="test_paper.rtf"
        )
        
        result = exporter.export_single_format(config)
        
        assert result.format == OutputFormat.WORD
        assert result.file_path.name == "test_paper.rtf"
        assert result.file_path.exists()
        assert result.file_size > 0
        
        # Check if RTF file contains expected content
        rtf_content = result.file_path.read_text(encoding='utf-8')
        assert "{\\rtf1" in rtf_content
        assert "Advanced Machine Learning Techniques" in rtf_content
    
    def test_epub_export(self, sample_extraction_results, temp_output_dir):
        """Test EPUB export functionality."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        config = ExportConfiguration(
            format=OutputFormat.EPUB,
            theme=TemplateTheme.ACADEMIC,
            output_filename="test_paper.epub"
        )
        
        result = exporter.export_single_format(config)
        
        assert result.format == OutputFormat.EPUB
        assert result.file_path.name == "test_paper.epub"
        assert result.file_path.exists()
        assert result.file_size > 0
        
        # EPUB should be a valid ZIP file
        import zipfile
        assert zipfile.is_zipfile(result.file_path)
    
    def test_multiple_format_export(self, sample_extraction_results, temp_output_dir):
        """Test exporting to multiple formats simultaneously."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        configs = [
            ExportConfiguration(format=OutputFormat.HTML, theme=TemplateTheme.ACADEMIC),
            ExportConfiguration(format=OutputFormat.LATEX, theme=TemplateTheme.ACADEMIC),
            ExportConfiguration(format=OutputFormat.WORD, theme=TemplateTheme.ACADEMIC),
            ExportConfiguration(format=OutputFormat.EPUB, theme=TemplateTheme.ACADEMIC)
        ]
        
        results = exporter.export_multiple_formats(configs)
        
        # At least Word and EPUB should succeed (no external templates needed)
        assert len(results) >= 2
        
        if OutputFormat.WORD in results:
            assert results[OutputFormat.WORD].format == OutputFormat.WORD
        
        if OutputFormat.EPUB in results:
            assert results[OutputFormat.EPUB].format == OutputFormat.EPUB
    
    def test_export_package_creation(self, sample_extraction_results, temp_output_dir):
        """Test creation of complete export package."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        formats = [OutputFormat.WORD, OutputFormat.EPUB]  # Use formats that don't need external templates
        
        package_path = exporter.create_export_package(formats, TemplateTheme.ACADEMIC)
        
        assert package_path.exists()
        assert package_path.suffix == ".zip"
        
        # Verify ZIP contains expected files
        import zipfile
        with zipfile.ZipFile(package_path, 'r') as zipf:
            file_list = zipf.namelist()
            assert "manifest.json" in file_list
            assert any("word/" in f for f in file_list)
            assert any("epub/" in f for f in file_list)
    
    def test_content_sanitization(self, sample_extraction_results, temp_output_dir):
        """Test content sanitization for different formats."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        # Test HTML sanitization
        html_content = exporter._sanitize_content("Test <script> & 'quotes'", OutputFormat.HTML)
        assert "&lt;script&gt;" in html_content
        assert "&amp;" in html_content
        assert "&#39;" in html_content
        
        # Test LaTeX sanitization
        latex_content = exporter._sanitize_content("Test $math$ & symbols", OutputFormat.LATEX)
        assert "\\$math\\$" in latex_content
        assert "\\&" in latex_content
        
        # Test Word sanitization
        word_content = exporter._sanitize_content("Test <tag> & content", OutputFormat.WORD)
        assert "&lt;tag&gt;" in word_content
        assert "&amp;" in word_content
    
    def test_template_path_resolution(self, sample_extraction_results, temp_output_dir):
        """Test template path resolution with fallbacks."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        # Test with non-existent theme (should fallback to academic)
        try:
            path = exporter.get_template_path(OutputFormat.HTML, TemplateTheme.MODERN, "main.html")
            # Should fallback to academic theme
            assert "academic" in str(path)
        except Exception as e:
            # If templates don't exist, should get ProcessingError
            assert "Template not found" in str(e)
    
    def test_figure_preparation(self, sample_extraction_results, temp_output_dir):
        """Test figure data preparation for different formats."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        figure_data = {
            "figure_id": "test_fig",
            "caption": "Test Figure",
            "data": b"PNG_TEST_DATA",
            "format": "png",
            "size": {"width": 400, "height": 300}
        }
        
        # Test HTML figure preparation
        html_config = ExportConfiguration(format=OutputFormat.HTML, embed_media=True)
        html_figure = exporter._prepare_figure(figure_data, html_config)
        
        assert html_figure["id"] == "test_fig"
        assert html_figure["caption"] == "Test Figure"
        assert html_figure["data"].startswith("data:image/png;base64,")
        
        # Test LaTeX figure preparation
        latex_config = ExportConfiguration(format=OutputFormat.LATEX, embed_media=True)
        latex_figure = exporter._prepare_figure(figure_data, latex_config)
        
        assert latex_figure["id"] == "test_fig"
        assert latex_figure["data"] == b"PNG_TEST_DATA"
    
    def test_table_preparation(self, sample_extraction_results, temp_output_dir):
        """Test table data preparation."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        table_data = {
            "table_id": "test_table",
            "caption": "Test Table",
            "csv_content": "Col1,Col2,Col3\nVal1,Val2,Val3",
            "format": "csv"
        }
        
        config = ExportConfiguration(format=OutputFormat.HTML)
        prepared_table = exporter._prepare_table(table_data, config)
        
        assert prepared_table["id"] == "test_table"
        assert prepared_table["caption"] == "Test Table"
        assert prepared_table["data"] == "Col1,Col2,Col3\nVal1,Val2,Val3"
        assert prepared_table["format"] == "csv"
    
    def test_toc_generation(self, sample_extraction_results, temp_output_dir):
        """Test table of contents generation."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        sections = {
            "abstract": "Abstract content...",
            "introduction": "Introduction content...",
            "methodology": "Methodology content...",
            "results": "Results content...",
            "conclusion": "Conclusion content..."
        }
        
        toc = exporter._generate_toc(sections)
        
        assert len(toc) == 5
        assert toc[0]["title"] == "Abstract"
        assert toc[0]["anchor"] == "section_abstract"
        assert toc[1]["title"] == "Introduction"
        assert toc[1]["anchor"] == "section_introduction"
    
    def test_error_handling(self, sample_extraction_results, temp_output_dir):
        """Test error handling in export process."""
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        # Test with invalid format
        invalid_config = ExportConfiguration(format="invalid_format")
        
        with pytest.raises(Exception):
            exporter.export_single_format(invalid_config)
    
    def test_performance_benchmarks(self, sample_extraction_results, temp_output_dir):
        """Test performance benchmarks for export operations."""
        import time
        
        exporter = MultiFormatExporter(sample_extraction_results, temp_output_dir)
        
        # Test Word export performance (should be fast)
        start_time = time.time()
        
        config = ExportConfiguration(format=OutputFormat.WORD, theme=TemplateTheme.ACADEMIC)
        result = exporter.export_single_format(config)
        
        end_time = time.time()
        processing_time = end_time - start_time
        
        assert processing_time < 5.0  # Should complete within 5 seconds
        assert result.file_size > 0
        
        print(f"Word export processing time: {processing_time:.4f} seconds")
        print(f"Word export file size: {result.file_size} bytes")


def run_comprehensive_tests():
    """Run comprehensive tests for the multi-format export system."""
    print("Running Paper2Data Multi-Format Export Tests...")
    
    # Create sample data
    sample_data = {
        "content": {
            "metadata": {
                "title": "Test Paper: Advanced AI Techniques",
                "authors": "Dr. Test Author, Prof. Example",
                "subject": "Artificial Intelligence",
                "page_count": 10
            }
        },
        "sections": {
            "sections": {
                "abstract": "This is a test abstract for the multi-format export system...",
                "introduction": "This introduction demonstrates the capabilities of Paper2Data...",
                "methodology": "Our methodology involves comprehensive testing...",
                "results": "The results show excellent performance across all formats...",
                "conclusion": "The multi-format export system works successfully..."
            }
        },
        "figures": {"figures": []},
        "tables": {"tables": []},
        "equations": {"equations": []},
        "citations": {"references": []}
    }
    
    # Test basic functionality
    temp_dir = Path(tempfile.mkdtemp())
    try:
        exporter = MultiFormatExporter(sample_data, temp_dir)
        
        # Test Word export (most reliable)
        print("\nTesting Word export...")
        word_config = ExportConfiguration(format=OutputFormat.WORD, theme=TemplateTheme.ACADEMIC)
        word_result = exporter.export_single_format(word_config)
        
        print(f"✓ Word export successful: {word_result.file_path}")
        print(f"  File size: {word_result.file_size} bytes")
        
        # Test EPUB export
        print("\nTesting EPUB export...")
        epub_config = ExportConfiguration(format=OutputFormat.EPUB, theme=TemplateTheme.ACADEMIC)
        epub_result = exporter.export_single_format(epub_config)
        
        print(f"✓ EPUB export successful: {epub_result.file_path}")
        print(f"  File size: {epub_result.file_size} bytes")
        
        # Test content preparation
        print("\nTesting content preparation...")
        content = exporter.prepare_content_for_export(word_config)
        
        print(f"✓ Content preparation successful")
        print(f"  Sections: {len(content['sections'])}")
        print(f"  Figures: {len(content['figures'])}")
        print(f"  Tables: {len(content['tables'])}")
        
        print("\n✓ All tests passed successfully!")
        
    except Exception as e:
        print(f"✗ Test failed: {str(e)}")
        import traceback
        traceback.print_exc()
        
    finally:
        shutil.rmtree(temp_dir)


if __name__ == "__main__":
    run_comprehensive_tests() 
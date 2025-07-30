"""
Comprehensive tests for advanced figure processing functionality.

Tests the sophisticated figure processing capabilities implemented in Stage 5
including caption detection, image analysis, figure classification, and more.
"""

import pytest
import io
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock
from PIL import Image

from paper2data.advanced_figure_processor import (
    AdvancedFigureProcessor,
    CaptionDetector,
    ImageAnalyzer,
    FigureClassifier,
    AdvancedFigure,
    FigureCaption,
    ImageAnalysis,
    FigureType,
    ImageQuality,
    CaptionPosition,
    get_advanced_figure_processor,
    process_advanced_figures
)


class TestCaptionDetector:
    """Test caption detection functionality."""
    
    def test_caption_detector_creation(self):
        """Test CaptionDetector instantiation."""
        detector = CaptionDetector()
        assert detector is not None
        assert detector.caption_patterns is not None
        assert detector.figure_keywords is not None
    
    def test_figure_keywords_loading(self):
        """Test figure keywords loading."""
        detector = CaptionDetector()
        keywords = detector.figure_keywords
        
        # Check for common figure keywords
        assert 'shows' in keywords
        assert 'illustrates' in keywords
        assert 'demonstrates' in keywords
        assert 'comparison' in keywords
        assert 'analysis' in keywords
        assert len(keywords) > 20  # Should have many keywords
    
    def test_simple_figure_caption_detection(self):
        """Test detection of simple figure captions."""
        detector = CaptionDetector()
        
        # Test standard figure caption
        text = "Figure 1: This diagram shows the system architecture."
        captions = detector.detect_captions(text, 1)
        
        assert len(captions) > 0
        caption = captions[0]
        assert caption.figure_number == "1"
        assert "diagram shows the system architecture" in caption.text
        assert caption.position == CaptionPosition.BELOW
        assert caption.page_number == 1
        assert caption.confidence > 0.5
    
    def test_various_caption_formats(self):
        """Test detection of various caption formats."""
        detector = CaptionDetector()
        
        test_cases = [
            ("Figure 2: Performance comparison between algorithms", "2"),
            ("Fig. 3: Network topology diagram", "3"),
            ("Image 1: Microscopy results", "1"),
            ("Chart 5: Distribution of data points", "5"),
            ("Diagram 7: Process workflow", "7"),
            ("Figure: Simple illustration", None),  # No number
        ]
        
        for text, expected_number in test_cases:
            captions = detector.detect_captions(text, 1)
            
            if captions:
                caption = captions[0]
                assert caption.figure_number == expected_number
                assert caption.confidence >= 0.5
    
    def test_embedded_caption_detection(self):
        """Test detection of embedded captions."""
        detector = CaptionDetector()
        
        text = "The results (which show significant improvement) are presented below."
        captions = detector.detect_captions(text, 1)
        
        embedded_captions = [cap for cap in captions if cap.position == CaptionPosition.EMBEDDED]
        assert len(embedded_captions) > 0
    
    def test_caption_text_cleaning(self):
        """Test caption text cleaning functionality."""
        detector = CaptionDetector()
        
        # Test text with extra whitespace and formatting
        dirty_text = "  This   is    a   test   caption   with    extra   spaces  "
        cleaned = detector._clean_caption_text(dirty_text)
        
        assert cleaned == "This is a test caption with extra spaces"
        assert "  " not in cleaned  # No double spaces
    
    def test_keyword_extraction(self):
        """Test keyword extraction from captions."""
        detector = CaptionDetector()
        
        text = "This figure shows a comparison analysis of data trends"
        keywords = detector._extract_keywords(text)
        
        assert 'shows' in keywords
        assert 'comparison' in keywords
        assert 'analysis' in keywords
        assert 'trends' in keywords
    
    def test_caption_confidence_calculation(self):
        """Test caption confidence calculation."""
        detector = CaptionDetector()
        
        # High confidence caption
        high_conf_text = "This comprehensive figure shows detailed analysis and comparison of results"
        high_keywords = detector._extract_keywords(high_conf_text)
        high_confidence = detector._calculate_caption_confidence(high_conf_text, high_keywords)
        
        # Low confidence caption
        low_conf_text = "Test"
        low_keywords = detector._extract_keywords(low_conf_text)
        low_confidence = detector._calculate_caption_confidence(low_conf_text, low_keywords)
        
        assert high_confidence > low_confidence
        assert 0.5 <= high_confidence <= 1.0
        assert 0.5 <= low_confidence <= 1.0


class TestImageAnalyzer:
    """Test image analysis functionality."""
    
    def test_image_analyzer_creation(self):
        """Test ImageAnalyzer instantiation."""
        analyzer = ImageAnalyzer()
        assert analyzer is not None
    
    def test_simple_image_analysis(self):
        """Test analysis of a simple test image."""
        analyzer = ImageAnalyzer()
        
        # Create a simple test image
        image = Image.new('RGB', (100, 100), color='red')
        
        # Convert to bytes
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='PNG')
        image_data = img_bytes.getvalue()
        
        # Analyze image
        analysis = analyzer.analyze_image(image_data)
        
        assert analysis.width == 100
        assert analysis.height == 100
        assert analysis.format == "PNG"
        assert analysis.mode == "RGB"
        assert analysis.file_size > 0
        assert isinstance(analysis.quality, ImageQuality)
        assert 0.0 <= analysis.brightness <= 1.0
        assert 0.0 <= analysis.contrast <= 1.0
        assert 0.0 <= analysis.sharpness <= 1.0
        assert analysis.color_complexity >= 0
        assert isinstance(analysis.has_transparency, bool)
    
    def test_image_quality_assessment(self):
        """Test image quality assessment."""
        analyzer = ImageAnalyzer()
        
        # High resolution image
        high_res_image = Image.new('RGB', (1000, 1000), color='blue')
        quality_high = analyzer._assess_image_quality(high_res_image)
        
        # Low resolution image
        low_res_image = Image.new('RGB', (50, 50), color='blue')
        quality_low = analyzer._assess_image_quality(low_res_image)
        
        # High resolution should have better quality
        quality_order = [ImageQuality.VERY_POOR, ImageQuality.POOR, ImageQuality.FAIR, 
                        ImageQuality.GOOD, ImageQuality.EXCELLENT]
        
        assert quality_order.index(quality_high) >= quality_order.index(quality_low)
    
    def test_brightness_calculation(self):
        """Test brightness calculation."""
        analyzer = ImageAnalyzer()
        
        # Create bright and dark images
        bright_image = Image.new('RGB', (100, 100), color='white')
        dark_image = Image.new('RGB', (100, 100), color='black')
        
        bright_value = analyzer._calculate_brightness(bright_image)
        dark_value = analyzer._calculate_brightness(dark_image)
        
        assert bright_value > dark_value
        assert 0.0 <= bright_value <= 1.0
        assert 0.0 <= dark_value <= 1.0
    
    def test_transparency_detection(self):
        """Test transparency detection."""
        analyzer = ImageAnalyzer()
        
        # Image with transparency
        transparent_image = Image.new('RGBA', (100, 100), color=(255, 0, 0, 128))
        has_transparency = analyzer._has_transparency(transparent_image)
        assert has_transparency == True
        
        # Image without transparency
        opaque_image = Image.new('RGB', (100, 100), color='red')
        has_no_transparency = analyzer._has_transparency(opaque_image)
        assert has_no_transparency == False
    
    def test_dominant_colors_extraction(self):
        """Test dominant colors extraction."""
        analyzer = ImageAnalyzer()
        
        # Create image with known colors
        image = Image.new('RGB', (100, 100), color='red')
        colors = analyzer._extract_dominant_colors(image, num_colors=3)
        
        assert isinstance(colors, list)
        assert len(colors) <= 3
        for color in colors:
            assert len(color) == 3  # RGB tuple
            assert all(0 <= c <= 255 for c in color)


class TestFigureClassifier:
    """Test figure classification functionality."""
    
    def test_figure_classifier_creation(self):
        """Test FigureClassifier instantiation."""
        classifier = FigureClassifier()
        assert classifier is not None
        assert classifier.classification_keywords is not None
    
    def test_classification_keywords_loading(self):
        """Test classification keywords loading."""
        classifier = FigureClassifier()
        keywords = classifier.classification_keywords
        
        # Check that all figure types have keywords
        for fig_type in FigureType:
            if fig_type != FigureType.UNKNOWN:
                assert fig_type in keywords
                assert len(keywords[fig_type]) > 0
    
    def test_caption_based_classification(self):
        """Test classification based on caption content."""
        classifier = FigureClassifier()
        
        # Create mock image analysis
        mock_analysis = ImageAnalysis(
            width=100, height=100, format="PNG", mode="RGB",
            file_size=1000, quality=ImageQuality.GOOD,
            brightness=0.5, contrast=0.3, sharpness=0.4,
            color_complexity=50, has_transparency=False,
            dominant_colors=[(255, 0, 0)]
        )
        
        # Test chart classification
        chart_caption = FigureCaption(
            caption_id="test", text="Bar chart showing distribution",
            position=CaptionPosition.BELOW, page_number=1,
            confidence=0.8, raw_text="", cleaned_text="bar chart showing distribution"
        )
        
        chart_type = classifier.classify_figure(mock_analysis, chart_caption)
        assert chart_type == FigureType.CHART
        
        # Test diagram classification
        diagram_caption = FigureCaption(
            caption_id="test", text="System architecture diagram",
            position=CaptionPosition.BELOW, page_number=1,
            confidence=0.8, raw_text="", cleaned_text="system architecture diagram"
        )
        
        diagram_type = classifier.classify_figure(mock_analysis, diagram_caption)
        assert diagram_type == FigureType.DIAGRAM
    
    def test_image_properties_classification(self):
        """Test classification based on image properties."""
        classifier = FigureClassifier()
        
        # High contrast, low color complexity (suggests chart/graph)
        chart_analysis = ImageAnalysis(
            width=100, height=100, format="PNG", mode="RGB",
            file_size=1000, quality=ImageQuality.GOOD,
            brightness=0.5, contrast=0.5, sharpness=0.4,
            color_complexity=20, has_transparency=False,
            dominant_colors=[(255, 0, 0)]
        )
        
        type_scores = {fig_type: 0.0 for fig_type in FigureType}
        classifier._classify_by_image_properties(chart_analysis, type_scores)
        
        # Should favor chart/graph types
        assert type_scores[FigureType.CHART] > 0
        assert type_scores[FigureType.GRAPH] > 0
    
    def test_unknown_classification(self):
        """Test unknown classification for ambiguous content."""
        classifier = FigureClassifier()
        
        # Ambiguous image analysis
        ambiguous_analysis = ImageAnalysis(
            width=100, height=100, format="PNG", mode="RGB",
            file_size=1000, quality=ImageQuality.GOOD,
            brightness=0.5, contrast=0.2, sharpness=0.2,
            color_complexity=50, has_transparency=False,
            dominant_colors=[(128, 128, 128)]
        )
        
        # No clear caption
        result_type = classifier.classify_figure(ambiguous_analysis, None)
        
        # Should return UNKNOWN for ambiguous cases
        assert result_type == FigureType.UNKNOWN


class TestAdvancedFigureProcessor:
    """Test advanced figure processor functionality."""
    
    def test_processor_creation(self):
        """Test AdvancedFigureProcessor instantiation."""
        processor = AdvancedFigureProcessor()
        assert processor is not None
        assert processor.caption_detector is not None
        assert processor.image_analyzer is not None
        assert processor.figure_classifier is not None
    
    def test_figure_processing_with_mock_pdf(self):
        """Test figure processing with mock PDF content."""
        processor = AdvancedFigureProcessor()
        
        # Mock PDF content
        mock_pdf_content = b"mock pdf content"
        
        # Mock fitz document
        with patch('paper2data.advanced_figure_processor.fitz.open') as mock_open:
            mock_doc = Mock()
            mock_page = Mock()
            mock_page.get_text.return_value = "Figure 1: Test diagram shows the process"
            mock_page.get_images.return_value = []  # No images for simplicity
            mock_doc.page_count = 1
            mock_doc.__getitem__ = Mock(return_value=mock_page)
            mock_doc.close = Mock()
            mock_open.return_value = mock_doc
            
            # Process figures
            results = processor.process_figures(mock_pdf_content)
            
            # Verify results structure
            assert "total_figures" in results
            assert "figures" in results
            assert "total_captions" in results
            assert "captions" in results
            assert "statistics" in results
            assert results["processing_status"] == "completed"
    
    def test_caption_association(self):
        """Test association of captions with figures."""
        processor = AdvancedFigureProcessor()
        
        # Create mock captions
        captions = [
            FigureCaption(
                caption_id="cap1", text="Test caption for figure 1",
                position=CaptionPosition.BELOW, page_number=1,
                confidence=0.8, raw_text="", cleaned_text="test caption",
                figure_number="1"
            ),
            FigureCaption(
                caption_id="cap2", text="Test caption for figure 2",
                position=CaptionPosition.BELOW, page_number=1,
                confidence=0.8, raw_text="", cleaned_text="test caption",
                figure_number="2"
            )
        ]
        
        # Test association
        associated_caption = processor._find_associated_caption(captions, 0, 1)  # First image
        assert associated_caption is not None
        assert associated_caption.figure_number == "1"
        
        associated_caption = processor._find_associated_caption(captions, 1, 1)  # Second image
        assert associated_caption is not None
        assert associated_caption.figure_number == "2"
    
    def test_figure_confidence_calculation(self):
        """Test figure confidence calculation."""
        processor = AdvancedFigureProcessor()
        
        # High quality image analysis
        high_quality_analysis = ImageAnalysis(
            width=1000, height=1000, format="PNG", mode="RGB",
            file_size=100000, quality=ImageQuality.EXCELLENT,
            brightness=0.5, contrast=0.5, sharpness=0.7,
            color_complexity=100, has_transparency=False,
            dominant_colors=[(255, 0, 0)]
        )
        
        # Good caption
        good_caption = FigureCaption(
            caption_id="test", text="Detailed analysis shows results",
            position=CaptionPosition.BELOW, page_number=1,
            confidence=0.9, raw_text="", cleaned_text="detailed analysis shows results"
        )
        
        # Calculate confidence
        confidence = processor._calculate_figure_confidence(
            high_quality_analysis, good_caption, ["extracted", "text"]
        )
        
        assert 0.5 <= confidence <= 1.0
        
        # Low quality should have lower confidence
        low_quality_analysis = ImageAnalysis(
            width=50, height=50, format="PNG", mode="RGB",
            file_size=1000, quality=ImageQuality.POOR,
            brightness=0.5, contrast=0.1, sharpness=0.1,
            color_complexity=5, has_transparency=False,
            dominant_colors=[]
        )
        
        low_confidence = processor._calculate_figure_confidence(
            low_quality_analysis, None, []
        )
        
        assert low_confidence < confidence
    
    def test_figure_metadata_generation(self):
        """Test figure metadata generation."""
        processor = AdvancedFigureProcessor()
        
        # Mock image analysis
        analysis = ImageAnalysis(
            width=800, height=600, format="PNG", mode="RGB",
            file_size=50000, quality=ImageQuality.GOOD,
            brightness=0.6, contrast=0.4, sharpness=0.5,
            color_complexity=75, has_transparency=True,
            dominant_colors=[(255, 0, 0), (0, 255, 0)]
        )
        
        # Mock caption
        caption = FigureCaption(
            caption_id="test", text="Test figure caption",
            position=CaptionPosition.BELOW, page_number=1,
            confidence=0.8, raw_text="", cleaned_text="test figure caption",
            keywords=["shows", "analysis"]
        )
        
        # Generate metadata
        metadata = processor._generate_figure_metadata(analysis, caption, FigureType.CHART)
        
        assert "file_size_kb" in metadata
        assert "resolution" in metadata
        assert "aspect_ratio" in metadata
        assert "color_mode" in metadata
        assert "has_transparency" in metadata
        assert "estimated_type" in metadata
        assert "caption_length" in metadata
        assert "caption_keywords" in metadata
        
        assert metadata["resolution"] == "800x600"
        assert metadata["estimated_type"] == "chart"
        assert metadata["has_transparency"] == True
    
    def test_figure_relationships(self):
        """Test figure relationship analysis."""
        processor = AdvancedFigureProcessor()
        
        # Create mock figures
        figures = [
            Mock(
                figure_id="fig1",
                figure_type=FigureType.CHART,
                page_number=1,
                image_analysis=Mock(width=100, height=100),
                related_figures=[]
            ),
            Mock(
                figure_id="fig2",
                figure_type=FigureType.CHART,
                page_number=2,
                image_analysis=Mock(width=100, height=100),
                related_figures=[]
            )
        ]
        
        # Analyze relationships
        processor._analyze_figure_relationships(figures)
        
        # Check if relationships were established
        # (Same type and adjacent pages should be related)
        assert len(figures[0].related_figures) > 0 or len(figures[1].related_figures) > 0


class TestAdvancedFigure:
    """Test AdvancedFigure dataclass."""
    
    def test_figure_creation(self):
        """Test advanced figure object creation."""
        # Create mock components
        analysis = ImageAnalysis(
            width=100, height=100, format="PNG", mode="RGB",
            file_size=1000, quality=ImageQuality.GOOD,
            brightness=0.5, contrast=0.3, sharpness=0.4,
            color_complexity=50, has_transparency=False,
            dominant_colors=[(255, 0, 0)]
        )
        
        caption = FigureCaption(
            caption_id="cap1", text="Test caption",
            position=CaptionPosition.BELOW, page_number=1,
            confidence=0.8, raw_text="", cleaned_text="test caption"
        )
        
        figure = AdvancedFigure(
            figure_id="fig1",
            figure_type=FigureType.CHART,
            page_number=1,
            position={"x": 0, "y": 0, "width": 100, "height": 100},
            image_data=b"test_image_data",
            image_analysis=analysis,
            caption=caption,
            extracted_text=["text1", "text2"],
            confidence=0.9,
            metadata={"test": "metadata"}
        )
        
        assert figure.figure_id == "fig1"
        assert figure.figure_type == FigureType.CHART
        assert figure.page_number == 1
        assert figure.confidence == 0.9
        assert figure.related_figures == []
    
    def test_figure_serialization(self):
        """Test figure serialization to dictionary."""
        # Create minimal figure for testing
        analysis = ImageAnalysis(
            width=100, height=100, format="PNG", mode="RGB",
            file_size=1000, quality=ImageQuality.GOOD,
            brightness=0.5, contrast=0.3, sharpness=0.4,
            color_complexity=50, has_transparency=False,
            dominant_colors=[]
        )
        
        figure = AdvancedFigure(
            figure_id="fig1",
            figure_type=FigureType.CHART,
            page_number=1,
            position={"x": 0, "y": 0, "width": 100, "height": 100},
            image_data=b"test",
            image_analysis=analysis,
            caption=None,
            extracted_text=[],
            confidence=0.8,
            metadata={}
        )
        
        # Serialize to dictionary
        figure_dict = figure.to_dict()
        
        # Verify serialization
        assert figure_dict["figure_id"] == "fig1"
        assert figure_dict["figure_type"] == "chart"
        assert figure_dict["page_number"] == 1
        assert figure_dict["confidence"] == 0.8
        assert "image_data_base64" in figure_dict
        assert "image_data" not in figure_dict  # Should be removed


class TestGlobalFunctions:
    """Test global functions and instances."""
    
    def test_global_processor_instance(self):
        """Test global advanced figure processor instance."""
        processor1 = get_advanced_figure_processor()
        processor2 = get_advanced_figure_processor()
        
        # Should be the same instance
        assert processor1 is processor2
    
    def test_process_advanced_figures(self):
        """Test global figure processing function."""
        mock_pdf_content = b"mock pdf content"
        
        # Mock the processor
        with patch('paper2data.advanced_figure_processor.AdvancedFigureProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_figures.return_value = {
                "total_figures": 1,
                "figures": [],
                "total_captions": 0,
                "captions": [],
                "processing_status": "completed"
            }
            mock_processor_class.return_value = mock_processor
            
            # Process figures
            results = process_advanced_figures(mock_pdf_content)
            
            # Verify results
            assert "total_figures" in results
            assert "figures" in results
            assert "total_captions" in results
            assert "captions" in results
            assert "processing_status" in results


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
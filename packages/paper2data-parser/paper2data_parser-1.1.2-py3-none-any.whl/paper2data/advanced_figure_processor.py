"""
Advanced Figure Processing System for Paper2Data Version 1.1

This module provides comprehensive figure processing capabilities including:
- Automatic caption detection and extraction
- Figure classification (graphs, diagrams, photos, charts)
- Advanced image analysis and quality enhancement
- Figure-text association and cross-referencing
- OCR fallback for mathematical symbols in figures
"""

import re
import logging
import json
import base64
import io
from typing import List, Dict, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from pathlib import Path
from enum import Enum
import hashlib

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    cv2 = None
    np = None
    OPENCV_AVAILABLE = False

try:
    from PIL import Image, ImageEnhance, ImageFilter
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False

try:
    import pytesseract
    PYTESSERACT_AVAILABLE = True
except ImportError:
    PYTESSERACT_AVAILABLE = False

logger = logging.getLogger(__name__)


class FigureType(Enum):
    """Types of figures that can be classified."""
    GRAPH = "graph"
    DIAGRAM = "diagram"
    PHOTO = "photo"
    CHART = "chart"
    TABLE = "table"
    EQUATION = "equation"
    FLOWCHART = "flowchart"
    SCHEMATIC = "schematic"
    PLOT = "plot"
    UNKNOWN = "unknown"


class ImageQuality(Enum):
    """Image quality levels."""
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"
    VERY_LOW = "very_low"


class CaptionPosition(Enum):
    """Caption positions relative to figure."""
    ABOVE = "above"
    BELOW = "below"
    LEFT = "left"
    RIGHT = "right"
    EMBEDDED = "embedded"
    UNKNOWN = "unknown"


@dataclass
class FigureCaption:
    """Represents a figure caption."""
    caption_id: str
    text: str
    position: CaptionPosition
    confidence: float
    page_number: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    figure_number: Optional[str] = None
    figure_reference: Optional[str] = None
    parsed_elements: Optional[Dict[str, Any]] = None


@dataclass
class ImageAnalysis:
    """Image analysis results."""
    width: int
    height: int
    aspect_ratio: float
    file_size: int
    quality: ImageQuality
    dominant_colors: List[Tuple[int, int, int]]
    has_text: bool
    text_regions: List[Dict[str, Any]]
    complexity_score: float
    sharpness_score: float
    contrast_score: float


@dataclass
class AdvancedFigure:
    """Represents a comprehensively processed figure."""
    figure_id: str
    page_number: int
    bbox: Tuple[float, float, float, float]
    figure_type: FigureType
    confidence: float
    
    # Image data
    image_data: bytes
    image_format: str
    image_analysis: ImageAnalysis
    
    # Caption information
    caption: Optional[FigureCaption] = None
    caption_text: Optional[str] = None
    
    # Classification details
    classification_confidence: float = 0.0
    classification_features: List[str] = None
    
    # Content analysis
    contains_equations: bool = False
    contains_text: bool = False
    text_content: Optional[str] = None
    
    # Quality metrics
    resolution_dpi: Optional[int] = None
    enhancement_applied: bool = False
    
    # Relationships
    referenced_in_text: List[str] = None
    cross_references: List[str] = None
    
    def __post_init__(self):
        if self.classification_features is None:
            self.classification_features = []
        if self.referenced_in_text is None:
            self.referenced_in_text = []
        if self.cross_references is None:
            self.cross_references = []


class CaptionDetector:
    """Detects and extracts figure captions from text."""
    
    def __init__(self):
        self.caption_patterns = [
            # Standard figure captions - more precise patterns
            r'(?i)^fig(?:ure)?\s*\.?\s*(\d+)(?:\s*[:\-\.]?\s*)?(.+?)(?=\n\s*\n|\n\s*fig|\n\s*table|\n\s*$|$)',
            r'(?i)^figure\s+(\d+)(?:\s*[:\-\.]?\s*)?(.+?)(?=\n\s*\n|\n\s*figure|\n\s*table|\n\s*$|$)',
            
            # Numbered captions with letters - more specific
            r'(?i)^fig(?:ure)?\s*\.?\s*(\d+[a-z])(?:\s*[:\-\.]?\s*)?(.+?)(?=\n\s*\n|\n\s*fig|\n\s*table|\n\s*$|$)',
            
            # Roman numeral figures - simplified
            r'(?i)^fig(?:ure)?\s*\.?\s*([IVX]+)(?:\s*[:\-\.]?\s*)?(.+?)(?=\n\s*\n|\n\s*fig|\n\s*table|\n\s*$|$)',
            
            # Parenthetical figure references - more specific
            r'(?i)^\(fig(?:ure)?\s*\.?\s*(\d+(?:[a-z])?)\)(?:\s*[:\-\.]?\s*)?(.+?)(?=\n\s*\n|\n\s*\(fig|\n\s*$|$)',
        ]
        
        self.compiled_patterns = [re.compile(pattern, re.MULTILINE) for pattern in self.caption_patterns]
    
    def detect_captions(self, text: str, page_number: int) -> List[FigureCaption]:
        """Detect figure captions in text."""
        captions = []
        
        for i, pattern in enumerate(self.compiled_patterns):
            matches = pattern.finditer(text)
            
            for match in matches:
                figure_number = None
                caption_text = ""
                
                if len(match.groups()) >= 2:
                    figure_number = match.group(1)
                    caption_text = match.group(2)
                elif len(match.groups()) >= 1:
                    caption_text = match.group(1)
                
                # Clean up caption text
                caption_text = self._clean_caption_text(caption_text)
                
                if len(caption_text) > 10:  # Minimum caption length
                    caption_id = f"caption_{page_number}_{len(captions)}"
                    
                    caption = FigureCaption(
                        caption_id=caption_id,
                        text=caption_text,
                        position=CaptionPosition.UNKNOWN,
                        confidence=self._calculate_caption_confidence(caption_text, figure_number),
                        page_number=page_number,
                        bbox=(0, 0, 0, 0),  # Would need layout analysis for precise positioning
                        figure_number=figure_number,
                        figure_reference=f"fig_{figure_number}" if figure_number else None
                    )
                    
                    captions.append(caption)
        
        return self._deduplicate_captions(captions)
    
    def _clean_caption_text(self, text: str) -> str:
        """Clean and normalize caption text."""
        # Remove excessive whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove common artifacts
        text = re.sub(r'^[:\-\.\s]+', '', text)
        text = re.sub(r'[:\-\.\s]+$', '', text)
        
        # Remove figure references that might be artifacts
        text = re.sub(r'^\(fig(?:ure)?\s*\.?\s*\d+\)\s*', '', text, flags=re.IGNORECASE)
        
        return text.strip()
    
    def _calculate_caption_confidence(self, caption_text: str, figure_number: Optional[str]) -> float:
        """Calculate confidence score for caption detection."""
        confidence = 0.5  # Base confidence
        
        # Boost for figure number
        if figure_number:
            confidence += 0.3
        
        # Boost for descriptive words
        descriptive_words = [
            'shows', 'illustrates', 'depicts', 'presents', 'displays',
            'comparison', 'results', 'analysis', 'performance', 'behavior',
            'relationship', 'distribution', 'trend', 'pattern', 'structure'
        ]
        
        words_found = sum(1 for word in descriptive_words if word in caption_text.lower())
        confidence += min(words_found * 0.1, 0.3)
        
        # Boost for reasonable length
        if 20 <= len(caption_text) <= 200:
            confidence += 0.2
        
        return min(confidence, 1.0)
    
    def _deduplicate_captions(self, captions: List[FigureCaption]) -> List[FigureCaption]:
        """Remove duplicate captions."""
        seen_texts = set()
        unique_captions = []
        
        for caption in captions:
            if caption.text not in seen_texts:
                seen_texts.add(caption.text)
                unique_captions.append(caption)
        
        return unique_captions


class ImageAnalyzer:
    """Analyzes image content and quality."""
    
    def __init__(self):
        self.text_detector_available = PYTESSERACT_AVAILABLE
        self.image_processor_available = OPENCV_AVAILABLE and PIL_AVAILABLE
    
    def analyze_image(self, image_data: bytes, image_format: str = "png") -> ImageAnalysis:
        """Perform comprehensive image analysis."""
        if not self.image_processor_available:
            # Fallback analysis
            return ImageAnalysis(
                width=0,
                height=0,
                aspect_ratio=1.0,
                file_size=len(image_data),
                quality=ImageQuality.MEDIUM,
                dominant_colors=[],
                has_text=False,
                text_regions=[],
                complexity_score=0.0,
                sharpness_score=0.0,
                contrast_score=0.0
            )
        
        try:
            # Load image
            image = Image.open(io.BytesIO(image_data))
            width, height = image.size
            
            # Basic metrics
            aspect_ratio = width / height if height > 0 else 1.0
            
            # Convert to numpy array for analysis
            if np is not None:
                img_array = np.array(image)
            else:
                img_array = None
            
            # Quality assessment
            quality = self._assess_image_quality(img_array, width, height)
            
            # Color analysis
            dominant_colors = self._extract_dominant_colors(img_array)
            
            # Text detection
            has_text, text_regions = self._detect_text_regions(image)
            
            # Complexity metrics
            complexity_score = self._calculate_complexity(img_array)
            sharpness_score = self._calculate_sharpness(img_array)
            contrast_score = self._calculate_contrast(img_array)
            
            return ImageAnalysis(
                width=width,
                height=height,
                aspect_ratio=aspect_ratio,
                file_size=len(image_data),
                quality=quality,
                dominant_colors=dominant_colors,
                has_text=has_text,
                text_regions=text_regions,
                complexity_score=complexity_score,
                sharpness_score=sharpness_score,
                contrast_score=contrast_score
            )
            
        except Exception as e:
            logger.error(f"Image analysis failed: {e}")
            return ImageAnalysis(
                width=0,
                height=0,
                aspect_ratio=1.0,
                file_size=len(image_data),
                quality=ImageQuality.LOW,
                dominant_colors=[],
                has_text=False,
                text_regions=[],
                complexity_score=0.0,
                sharpness_score=0.0,
                contrast_score=0.0
            )
    
    def _assess_image_quality(self, img_array: Optional[Any], width: int, height: int) -> ImageQuality:
        """Assess overall image quality."""
        if img_array is None or np is None:
            # Fallback to simple size-based assessment
            if width < 100 or height < 100:
                return ImageQuality.VERY_LOW
            elif width < 300 or height < 300:
                return ImageQuality.LOW
            elif width < 800 or height < 800:
                return ImageQuality.MEDIUM
            else:
                return ImageQuality.HIGH
        
        if len(img_array.shape) == 0:
            return ImageQuality.VERY_LOW
        
        # Basic quality assessment based on resolution
        if width < 100 or height < 100:
            return ImageQuality.VERY_LOW
        elif width < 300 or height < 300:
            return ImageQuality.LOW
        elif width < 800 or height < 800:
            return ImageQuality.MEDIUM
        else:
            return ImageQuality.HIGH
    
    def _extract_dominant_colors(self, img_array: Optional[Any]) -> List[Tuple[int, int, int]]:
        """Extract dominant colors from image."""
        if img_array is None or np is None or len(img_array.shape) < 3:
            return []
        
        try:
            # Reshape image to be a list of pixels
            pixels = img_array.reshape(-1, img_array.shape[-1])
            
            # Simple dominant color extraction (could be improved with K-means)
            if len(pixels) > 1000:
                # Sample pixels to speed up processing
                pixels = pixels[::len(pixels)//1000]
            
            # Get unique colors and their counts
            unique_colors, counts = np.unique(pixels, axis=0, return_counts=True)
            
            # Sort by count and return top colors
            sorted_indices = np.argsort(counts)[::-1]
            dominant_colors = []
            
            for i in sorted_indices[:5]:  # Top 5 colors
                color = unique_colors[i]
                if len(color) >= 3:
                    dominant_colors.append(tuple(int(c) for c in color[:3]))
            
            return dominant_colors
        except Exception as e:
            logger.debug(f"Color extraction failed: {e}")
            return []
    
    def _detect_text_regions(self, image: Image.Image) -> Tuple[bool, List[Dict[str, Any]]]:
        """Detect text regions in image."""
        if not self.text_detector_available:
            return False, []
        
        try:
            # Use pytesseract to detect text
            text = pytesseract.image_to_string(image)
            has_text = len(text.strip()) > 0
            
            # Get text regions
            text_regions = []
            if has_text:
                boxes = pytesseract.image_to_boxes(image)
                for box in boxes.splitlines():
                    parts = box.split()
                    if len(parts) >= 5:
                        char, x1, y1, x2, y2 = parts[:5]
                        text_regions.append({
                            'character': char,
                            'bbox': (int(x1), int(y1), int(x2), int(y2)),
                            'confidence': 1.0  # pytesseract doesn't provide confidence in this format
                        })
            
            return has_text, text_regions
            
        except Exception as e:
            logger.debug(f"Text detection failed: {e}")
            return False, []
    
    def _calculate_complexity(self, img_array: Optional[Any]) -> float:
        """Calculate image complexity score."""
        if img_array is None or np is None:
            return 0.0
        
        if len(img_array.shape) == 0:
            return 0.0
        
        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                if OPENCV_AVAILABLE and cv2 is not None:
                    gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
                else:
                    gray = img_array[:,:,0]  # Simple grayscale approximation
            else:
                gray = img_array
            
            # Calculate standard deviation as complexity measure
            complexity = np.std(gray) / 255.0 if gray.size > 0 else 0.0
            return min(complexity, 1.0)
        except Exception as e:
            logger.debug(f"Complexity calculation failed: {e}")
            return 0.0
    
    def _calculate_sharpness(self, img_array: Optional[Any]) -> float:
        """Calculate image sharpness score."""
        if not OPENCV_AVAILABLE or cv2 is None or img_array is None or np is None:
            return 0.0
        
        if len(img_array.shape) == 0:
            return 0.0
        
        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = cv2.cvtColor(img_array, cv2.COLOR_RGB2GRAY)
            else:
                gray = img_array
            
            # Calculate Laplacian variance as sharpness measure
            laplacian = cv2.Laplacian(gray, cv2.CV_64F)
            sharpness = laplacian.var() / 10000.0  # Normalize
            return min(sharpness, 1.0)
        except Exception as e:
            logger.debug(f"Sharpness calculation failed: {e}")
            return 0.0
    
    def _calculate_contrast(self, img_array: Optional[Any]) -> float:
        """Calculate image contrast score."""
        if img_array is None or np is None:
            return 0.0
        
        if len(img_array.shape) == 0:
            return 0.0
        
        try:
            # Convert to grayscale if needed
            if len(img_array.shape) == 3:
                gray = img_array[:,:,0]  # Simple grayscale approximation
            else:
                gray = img_array
            
            # Calculate contrast as difference between max and min normalized
            contrast = (np.max(gray) - np.min(gray)) / 255.0 if gray.size > 0 else 0.0
            return min(contrast, 1.0)
        except Exception as e:
            logger.debug(f"Contrast calculation failed: {e}")
            return 0.0


class FigureClassifier:
    """Classifies figures into different types."""
    
    def __init__(self):
        self.classification_features = {
            FigureType.GRAPH: [
                'axes', 'axis', 'plot', 'curve', 'line', 'data points',
                'scatter', 'trend', 'correlation', 'regression'
            ],
            FigureType.CHART: [
                'bar', 'pie', 'histogram', 'distribution', 'frequency',
                'percentage', 'proportion', 'statistics', 'survey'
            ],
            FigureType.DIAGRAM: [
                'diagram', 'schematic', 'flowchart', 'process', 'workflow',
                'structure', 'hierarchy', 'organization', 'system'
            ],
            FigureType.PHOTO: [
                'photograph', 'image', 'picture', 'microscopy', 'specimen',
                'sample', 'material', 'texture', 'surface'
            ],
            FigureType.FLOWCHART: [
                'flowchart', 'flow', 'process', 'algorithm', 'procedure',
                'steps', 'sequence', 'decision', 'branch'
            ],
            FigureType.SCHEMATIC: [
                'schematic', 'circuit', 'electrical', 'mechanical', 'technical',
                'blueprint', 'design', 'engineering', 'component'
            ]
        }
    
    def classify_figure(self, figure_data: bytes, caption_text: Optional[str] = None, 
                       image_analysis: Optional[ImageAnalysis] = None) -> Tuple[FigureType, float, List[str]]:
        """Classify figure type with confidence and feature list."""
        
        # Initialize scores
        type_scores = {fig_type: 0.0 for fig_type in FigureType}
        detected_features = []
        
        # Text-based classification
        if caption_text:
            text_scores, text_features = self._classify_by_text(caption_text)
            for fig_type, score in text_scores.items():
                type_scores[fig_type] += score * 0.7  # Weight text analysis
            detected_features.extend(text_features)
        
        # Image-based classification
        if image_analysis:
            image_scores, image_features = self._classify_by_image(image_analysis)
            for fig_type, score in image_scores.items():
                type_scores[fig_type] += score * 0.3  # Weight image analysis
            detected_features.extend(image_features)
        
        # Find best classification
        best_type = max(type_scores.items(), key=lambda x: x[1])
        
        # Lower confidence threshold and normalize scores
        max_score = best_type[1]
        if max_score > 0.1:  # Much lower minimum confidence threshold
            normalized_confidence = min(max_score, 1.0)
            return best_type[0], normalized_confidence, detected_features
        else:
            return FigureType.UNKNOWN, 0.0, detected_features
    
    def _classify_by_text(self, text: str) -> Tuple[Dict[FigureType, float], List[str]]:
        """Classify figure based on caption text."""
        text_lower = text.lower()
        scores = {fig_type: 0.0 for fig_type in FigureType}
        detected_features = []
        
        for fig_type, keywords in self.classification_features.items():
            matches = 0
            for keyword in keywords:
                if keyword in text_lower:
                    matches += 1
                    detected_features.append(keyword)
            
            if matches > 0:
                # Score based on keyword matches, with higher weight for more matches
                scores[fig_type] = matches / len(keywords) + 0.5  # Base score of 0.5
        
        return scores, detected_features
    
    def _classify_by_image(self, image_analysis: ImageAnalysis) -> Tuple[Dict[FigureType, float], List[str]]:
        """Classify figure based on image analysis."""
        scores = {fig_type: 0.0 for fig_type in FigureType}
        detected_features = []
        
        # Basic heuristics based on image properties
        
        # High contrast and complexity might indicate graphs or charts
        if image_analysis.contrast_score > 0.7 and image_analysis.complexity_score > 0.5:
            scores[FigureType.GRAPH] += 0.3
            scores[FigureType.CHART] += 0.2
            detected_features.append('high_contrast_complex')
        
        # Presence of text suggests diagrams or charts
        if image_analysis.has_text:
            scores[FigureType.DIAGRAM] += 0.3
            scores[FigureType.CHART] += 0.2
            scores[FigureType.FLOWCHART] += 0.2
            detected_features.append('contains_text')
        
        # Aspect ratio heuristics
        if 0.8 <= image_analysis.aspect_ratio <= 1.2:  # Square-ish
            scores[FigureType.PHOTO] += 0.1
            scores[FigureType.DIAGRAM] += 0.1
            detected_features.append('square_aspect')
        elif image_analysis.aspect_ratio > 1.5:  # Wide
            scores[FigureType.GRAPH] += 0.2
            scores[FigureType.CHART] += 0.1
            detected_features.append('wide_aspect')
        
        # Low sharpness might indicate photographs
        if image_analysis.sharpness_score < 0.3:
            scores[FigureType.PHOTO] += 0.2
            detected_features.append('low_sharpness')
        
        return scores, detected_features


class AdvancedFigureProcessor:
    """Main advanced figure processing system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        
        # Initialize components
        self.caption_detector = CaptionDetector()
        self.image_analyzer = ImageAnalyzer()
        self.figure_classifier = FigureClassifier()
        
        # Configuration
        self.min_figure_size = self.config.get('min_figure_size', 50)
        self.max_figures_per_page = self.config.get('max_figures_per_page', 20)
        self.caption_detection_enabled = self.config.get('caption_detection', True)
        self.image_analysis_enabled = self.config.get('image_analysis', True)
        self.figure_classification_enabled = self.config.get('figure_classification', True)
        self.text_extraction_enabled = self.config.get('text_extraction', True)
        
        logger.info("Advanced figure processor initialized with comprehensive processing capabilities")
    
    def process_document(self, doc_path: str, document_text: Optional[str] = None) -> Dict[str, Any]:
        """Process a document for advanced figure extraction and analysis."""
        import time
        start_time = time.time()
        
        logger.info(f"Starting advanced figure processing for: {doc_path}")
        
        if not FITZ_AVAILABLE:
            logger.error("PyMuPDF not available for advanced figure processing")
            return {
                "figures": [],
                "captions": [],
                "total_figures": 0,
                "processing_time": 0.0,
                "error": "PyMuPDF not available"
            }
        
        try:
            doc = fitz.open(doc_path)
            all_figures = []
            all_captions = []
            
            # Extract document text if not provided
            if document_text is None:
                document_text = self._extract_document_text(doc)
            
            # Process each page
            for page_num in range(len(doc)):
                page = doc[page_num]
                
                # Extract page text
                page_text = page.get_text()
                
                # Detect captions on this page
                if self.caption_detection_enabled:
                    page_captions = self.caption_detector.detect_captions(page_text, page_num)
                    all_captions.extend(page_captions)
                
                # Extract and process figures
                page_figures = self._process_page_figures(page, page_num, page_text, all_captions)
                all_figures.extend(page_figures)
            
            doc.close()
            
            # Associate figures with captions
            self._associate_figures_with_captions(all_figures, all_captions)
            
            # Find text references
            self._find_text_references(all_figures, document_text)
            
            processing_time = time.time() - start_time
            
            result = {
                "figures": [asdict(fig) for fig in all_figures],
                "captions": [asdict(cap) for cap in all_captions],
                "total_figures": len(all_figures),
                "total_captions": len(all_captions),
                "processing_time": processing_time,
                "processing_summary": {
                    "graphs": len([f for f in all_figures if f.figure_type == FigureType.GRAPH]),
                    "charts": len([f for f in all_figures if f.figure_type == FigureType.CHART]),
                    "diagrams": len([f for f in all_figures if f.figure_type == FigureType.DIAGRAM]),
                    "photos": len([f for f in all_figures if f.figure_type == FigureType.PHOTO]),
                    "with_captions": len([f for f in all_figures if f.caption is not None]),
                    "with_text": len([f for f in all_figures if f.contains_text]),
                    "high_quality": len([f for f in all_figures if f.image_analysis.quality == ImageQuality.HIGH])
                }
            }
            
            logger.info(f"Advanced figure processing completed: {len(all_figures)} figures, {len(all_captions)} captions in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error in advanced figure processing: {str(e)}")
            return {
                "figures": [],
                "captions": [],
                "total_figures": 0,
                "processing_time": time.time() - start_time,
                "error": str(e)
            }
    
    def _extract_document_text(self, doc) -> str:
        """Extract full document text."""
        text_parts = []
        for page_num in range(len(doc)):
            page = doc[page_num]
            page_text = page.get_text()
            text_parts.append(page_text)
        return "\n".join(text_parts)
    
    def _process_page_figures(self, page, page_num: int, page_text: str, 
                            captions: List[FigureCaption]) -> List[AdvancedFigure]:
        """Process figures on a single page."""
        figures = []
        
        # Get images from page
        image_list = page.get_images(full=True)
        
        for img_index, img in enumerate(image_list):
            if len(figures) >= self.max_figures_per_page:
                break
            
            try:
                # Get image data
                xref = img[0]
                pix = fitz.Pixmap(page.parent, xref)
                
                # Skip small images
                if pix.width < self.min_figure_size or pix.height < self.min_figure_size:
                    pix = None
                    continue
                
                # Convert to bytes
                if pix.n - pix.alpha < 4:  # RGB
                    img_data = pix.tobytes("png")
                else:  # CMYK
                    pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                    img_data = pix_rgb.tobytes("png")
                    pix_rgb = None
                
                # Create figure ID
                figure_id = f"fig_{page_num+1}_{img_index+1}"
                
                # Image analysis
                image_analysis = None
                if self.image_analysis_enabled:
                    image_analysis = self.image_analyzer.analyze_image(img_data, "png")
                
                # Figure classification
                figure_type = FigureType.UNKNOWN
                classification_confidence = 0.0
                classification_features = []
                
                if self.figure_classification_enabled:
                    # Find potential caption for this figure
                    caption_text = None
                    page_captions = [c for c in captions if c.page_number == page_num]
                    if page_captions:
                        # Simple heuristic: use first caption on page
                        caption_text = page_captions[0].text
                    
                    figure_type, classification_confidence, classification_features = \
                        self.figure_classifier.classify_figure(img_data, caption_text, image_analysis)
                
                # Text extraction
                contains_text = False
                text_content = None
                if self.text_extraction_enabled and image_analysis:
                    contains_text = image_analysis.has_text
                    if contains_text and image_analysis.text_regions:
                        text_content = " ".join([region.get('character', '') for region in image_analysis.text_regions])
                
                # Create advanced figure
                advanced_figure = AdvancedFigure(
                    figure_id=figure_id,
                    page_number=page_num + 1,
                    bbox=(0, 0, pix.width, pix.height),  # Simplified bbox
                    figure_type=figure_type,
                    confidence=0.8,  # Base confidence
                    image_data=img_data,
                    image_format="png",
                    image_analysis=image_analysis,
                    classification_confidence=classification_confidence,
                    classification_features=classification_features,
                    contains_text=contains_text,
                    text_content=text_content,
                    resolution_dpi=72  # Standard PDF resolution
                )
                
                figures.append(advanced_figure)
                pix = None
                
            except Exception as e:
                logger.error(f"Error processing figure {img_index} on page {page_num}: {e}")
                continue
        
        return figures
    
    def _associate_figures_with_captions(self, figures: List[AdvancedFigure], 
                                        captions: List[FigureCaption]) -> None:
        """Associate figures with their captions."""
        for figure in figures:
            # Find captions on the same page
            page_captions = [c for c in captions if c.page_number == figure.page_number]
            
            if page_captions:
                # Simple heuristic: associate with first caption on page
                # More sophisticated association would use spatial analysis
                best_caption = page_captions[0]
                figure.caption = best_caption
                figure.caption_text = best_caption.text
    
    def _find_text_references(self, figures: List[AdvancedFigure], document_text: str) -> None:
        """Find references to figures in the document text."""
        for figure in figures:
            references = []
            
            # Common figure reference patterns
            patterns = [
                rf'fig(?:ure)?\s*\.?\s*{figure.figure_id.split("_")[1]}',
                rf'fig(?:ure)?\s*\.?\s*{figure.page_number}',
                rf'\(fig(?:ure)?\s*\.?\s*{figure.figure_id.split("_")[1]}\)',
                rf'see\s+fig(?:ure)?\s*\.?\s*{figure.figure_id.split("_")[1]}',
            ]
            
            for pattern in patterns:
                matches = re.findall(pattern, document_text, re.IGNORECASE)
                references.extend(matches)
            
            figure.referenced_in_text = list(set(references))  # Remove duplicates
    
    def export_figures(self, processing_result: Dict[str, Any], output_dir: str) -> None:
        """Export processed figures to directory."""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)
        
        # Create subdirectories
        (output_path / "figures").mkdir(exist_ok=True)
        (output_path / "captions").mkdir(exist_ok=True)
        (output_path / "analysis").mkdir(exist_ok=True)
        
        # Export figures
        for i, figure_data in enumerate(processing_result.get("figures", [])):
            figure_id = figure_data.get("figure_id", f"figure_{i}")
            
            # Save image
            image_data = figure_data.get("image_data")
            if image_data:
                # Handle base64 encoded data
                if isinstance(image_data, str):
                    image_bytes = base64.b64decode(image_data)
                else:
                    image_bytes = image_data
                
                image_path = output_path / "figures" / f"{figure_id}.png"
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
            
            # Save figure metadata
            metadata_path = output_path / "analysis" / f"{figure_id}_analysis.json"
            with open(metadata_path, "w") as f:
                json.dump(figure_data, f, indent=2, default=str)
        
        # Export captions
        captions_data = processing_result.get("captions", [])
        if captions_data:
            captions_path = output_path / "captions" / "all_captions.json"
            with open(captions_path, "w") as f:
                json.dump(captions_data, f, indent=2, default=str)
        
        # Export processing summary
        summary_path = output_path / "processing_summary.json"
        with open(summary_path, "w") as f:
            json.dump(processing_result, f, indent=2, default=str)
        
        logger.info(f"Advanced figures exported to {output_path}")


# Factory functions and utilities

def get_advanced_figure_processor(config: Optional[Dict[str, Any]] = None) -> AdvancedFigureProcessor:
    """Factory function to create an advanced figure processor."""
    return AdvancedFigureProcessor(config)


def process_advanced_figures(doc_path: str, output_dir: Optional[str] = None, 
                           config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Process figures with advanced analysis and export results."""
    processor = get_advanced_figure_processor(config)
    result = processor.process_document(doc_path)
    
    if output_dir:
        processor.export_figures(result, output_dir)
    
    return result


if __name__ == "__main__":
    # Example usage
    config = {
        'min_figure_size': 100,
        'caption_detection': True,
        'image_analysis': True,
        'figure_classification': True,
        'text_extraction': True
    }
    
    processor = get_advanced_figure_processor(config)
    print("Paper2Data Version 1.1 - Advanced Figure Processing System")
    print("Comprehensive figure analysis with caption detection and classification")
    print("Ready for integration with academic paper processing pipeline") 
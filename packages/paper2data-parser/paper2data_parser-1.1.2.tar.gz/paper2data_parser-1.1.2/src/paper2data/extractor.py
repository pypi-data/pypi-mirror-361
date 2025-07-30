"""
Content extraction and processing logic for Paper2Data.

Handles text extraction, section detection, figure/table extraction,
and output formatting.
"""

from typing import Dict, List, Any, Optional, Union
import re
try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
    FitzDocument = fitz.Document
    FitzPixmap = fitz.Pixmap
except ImportError:
    # Handle case where PyMuPDF is not installed
    fitz = None
    FITZ_AVAILABLE = False
    FitzDocument = Any
    FitzPixmap = Any
from .utils import get_logger, ProcessingError, clean_text, progress_callback, suppress_stderr
from .table_processor import enhance_table_with_csv
from .plugin_manager import get_plugin_manager, initialize_plugin_system
from .plugin_hooks import execute_hook, execute_hook_until_success
from .equation_processor import EquationProcessor

logger = get_logger(__name__)

class BaseExtractor:
    """Base class for all content extractors."""

    def __init__(self, pdf_content: bytes) -> None:
        self.pdf_content = pdf_content
        self.extracted_data: Dict[str, Any] = {}
        self.doc: Optional[Any] = None

    def extract(self) -> Dict[str, Any]:
        """Extract content from PDF."""
        raise NotImplementedError("Subclasses must implement extract method")

    def _open_document(self) -> Any:
        """Open PDF document from bytes."""
        if not FITZ_AVAILABLE or fitz is None:
            raise ProcessingError("PyMuPDF (fitz) is not installed. Please install it with: pip install PyMuPDF")
        
        if self.doc is None:
            try:
                self.doc = fitz.open(stream=self.pdf_content, filetype="pdf")
                if self.doc is not None:
                    logger.debug(f"Opened PDF document: {self.doc.page_count} pages")
                else:
                    raise ProcessingError("Failed to open PDF document: Document is None")
            except Exception as e:
                raise ProcessingError(f"Failed to open PDF document: {str(e)}")
        return self.doc

    def _close_document(self) -> None:
        """Close PDF document."""
        if self.doc:
            self.doc.close()
            self.doc = None

    def _extract_page_text_robust(self, page) -> str:
        """Extract text from page using multiple fallback methods.

        This method implements a robust text extraction strategy:
        1. Try standard text extraction
        2. Try different extraction flags and methods
        3. Fall back to OCR-style extraction if needed
        4. Return basic page info as last resort

        Args:
            page: PyMuPDF page object

        Returns:
            Extracted text string
        """
        if not FITZ_AVAILABLE or fitz is None or page is None:
            page_num_str = "unknown"
            if page is not None and hasattr(page, 'number'):
                try:
                    page_num_str = str(page.number + 1)
                except (TypeError, AttributeError):
                    page_num_str = "unknown"
            return f"Page {page_num_str}: Text extraction unavailable (PyMuPDF not installed or page is None)"
        
        with suppress_stderr():
            # Method 1: Standard text extraction
            text = page.get_text()
            if text and text.strip():
                return text

            # Method 2: Try text extraction with different flags
            try:
                text = page.get_text("text")
                if text and text.strip():
                    return text
            except Exception:
                pass

            # Method 3: Try blocks method for structured text
            try:
                blocks = page.get_text("blocks")
                if blocks:
                    text_parts = []
                    for block in blocks:
                        if len(block) >= 5 and block[4]:  # block[4] is text content
                            text_parts.append(str(block[4]).strip())
                    text = "\n".join(text_parts)
                    if text.strip():
                        return text
            except Exception:
                pass

            # Method 4: Try words method
            try:
                words = page.get_text("words")
                if words:
                    text_parts = []
                    for word in words:
                        if len(word) >= 5 and word[4]:  # word[4] is text content
                            text_parts.append(str(word[4]).strip())
                    text = " ".join(text_parts)
                    if text.strip():
                        return text
            except Exception:
                pass

            # Method 5: Try dictionary method for detailed extraction
            try:
                text_dict = page.get_text("dict")
                if text_dict and "blocks" in text_dict:
                    text_parts = []
                    for block in text_dict["blocks"]:
                        if "lines" in block:
                            for line in block["lines"]:
                                if "spans" in line:
                                    for span in line["spans"]:
                                        if "text" in span and span["text"]:
                                            text_parts.append(span["text"].strip())
                    text = " ".join(text_parts)
                    if text.strip():
                        return text
            except Exception:
                pass

            # Last resort: Generate meaningful fallback content
            page_num: Union[int, str] = "unknown"
            try:
                if hasattr(page, 'number') and isinstance(page.number, int):
                    page_num = page.number + 1
            except (TypeError, AttributeError):
                page_num = "unknown"
            
            logger.warning(f"Standard text extraction failed for page {page_num}, may require OCR")

            # Try to extract at least basic structure information
            page_info = []
            page_info.append(f"Page {page_num}")

            # Get page dimensions and basic info
            try:
                rect = page.rect
                page_info.append(f"Dimensions: {rect.width:.0f}x{rect.height:.0f} pts")
            except Exception:
                page_info.append("Dimensions: Unable to determine")

            # Count images and other elements to give some structure info
            try:
                images = page.get_images()
                if images:
                    page_info.append(f"Contains {len(images)} images/figures")
            except Exception:
                pass

            # Add note about text extraction failure
            page_info.append("Note: Text extraction failed - PDF may have corrupted text streams.")
            page_info.append("This page may contain text that requires OCR for proper extraction.")

            # For section detection, add some common academic paper markers
            # Use special markers that won't be collapsed by clean_text()
            if page_num == 1:
                page_info.append("")  # Empty line for separation
                page_info.append("===SECTION_BREAK===")
                page_info.append("# Abstract")
                page_info.append("[Text extraction failed - may contain abstract]")
                page_info.append("===SECTION_BREAK===")
                page_info.append("# Introduction")
                page_info.append("[Text extraction failed - may contain introduction]")
            elif isinstance(page_num, int) and page_num <= 3:
                page_info.append("")  # Empty line for separation
                page_info.append("===SECTION_BREAK===")
                page_info.append("# Introduction")
                page_info.append("[Text extraction failed - may contain introduction or methodology]")
            else:
                page_info.append("")  # Empty line for separation
                page_info.append("===SECTION_BREAK===")
                page_info.append(f"# Content Page {page_num}")
                page_info.append(f"[Text extraction failed - may contain results, discussion, or references]")

            return "\n".join(page_info)

class ContentExtractor(BaseExtractor):
    """Extracts text content from PDF with basic section detection."""

    def extract(self) -> Dict[str, Any]:
        """Extract text content from PDF.

        Returns:
            Dictionary containing extracted text and metadata
        """
        logger.info("Starting content extraction")
        doc = self._open_document()

        try:
            # Extract basic document metadata
            metadata = {
                "page_count": doc.page_count,
                "title": doc.metadata.get("title", "").strip(),
                "author": doc.metadata.get("author", "").strip(),
                "subject": doc.metadata.get("subject", "").strip(),
                "creator": doc.metadata.get("creator", "").strip(),
                "creation_date": doc.metadata.get("creationDate", ""),
            }

            # Extract text from all pages with fallback methods
            full_text = ""
            pages_text = {}

            for page_num in range(doc.page_count):
                progress_callback(page_num + 1, doc.page_count, f"Extracting page {page_num + 1}")

                page = doc[page_num]
                page_text = self._extract_page_text_robust(page)
                cleaned_text = clean_text(page_text)

                pages_text[page_num + 1] = cleaned_text
                full_text += cleaned_text + "\n\n"

            # Clean full text
            full_text = clean_text(full_text)

            # Basic text statistics
            word_count = len(full_text.split())
            char_count = len(full_text)

            self.extracted_data = {
                "metadata": metadata,
                "full_text": full_text,
                "pages": pages_text,
                "statistics": {
                    "page_count": doc.page_count,
                    "word_count": word_count,
                    "character_count": char_count,
                    "avg_words_per_page": word_count / doc.page_count if doc.page_count > 0 else 0
                }
            }

            logger.info(f"Content extraction completed: {word_count} words, {doc.page_count} pages")
            return self.extracted_data

        finally:
            self._close_document()

class SectionExtractor(BaseExtractor):
    """Extracts and identifies document sections (abstract, introduction, etc.)."""

    # Common section headers to look for (supports both plain text and markdown)
    SECTION_PATTERNS = {
        # Basic patterns (existing)
        'abstract': r'(?i)^#*\s*(abstract|summary)\s*$',
        'introduction': r'(?i)^#*\s*(introduction|intro)\s*$',
        'methods': r'(?i)^#*\s*(methods?|methodology|experimental\s+setup|materials\s+and\s+methods)\s*$',
        'results': r'(?i)^#*\s*(results?|findings|experimental\s+results)\s*$',
        'discussion': r'(?i)^#*\s*(discussion|analysis|discussion\s+and\s+analysis)\s*$',
        'conclusion': r'(?i)^#*\s*(conclusions?|concluding\s+remarks|summary\s+and\s+conclusions?)\s*$',
        'references': r'(?i)^#*\s*(references?|bibliography|works?\s+cited|literature\s+cited|citations?|reference\s+list)\s*$',
        'acknowledgments': r'(?i)^#*\s*(acknowledgments?|acknowledgements?|acknowledgment)\s*$',
        'appendix': r'(?i)^#*\s*(appendix|appendices|supplementary\s+material)\s*$',
        'related_work': r'(?i)^#*\s*(related\s+work|background|literature\s+review|prior\s+work)\s*$',
        'evaluation': r'(?i)^#*\s*(evaluation|experiments?|performance\s+evaluation)\s*$',
        'implementation': r'(?i)^#*\s*(implementation|system\s+design|architecture)\s*$',

        # Roman numeral patterns (I., II., III., etc.) - Fixed patterns
        'roman_introduction': r'(?i)^I\.\s*(introduction|intro)\.?\s*$',
        'roman_preliminaries': r'(?i)^II\.\s*(preliminaries|background|foundation)\.?\s*$',
        'roman_framework': r'(?i)^III\.\s*(framework|generalized\s+framework|methodology|methods?)\.?\s*$',
        'roman_applications': r'(?i)^IV\.\s*(applications?|bridging|specific\s+applications?).*$',
        'roman_correction': r'(?i)^V\.\s*(risk\s+)?correction\.?\s*$',
        'roman_experiment': r'(?i)^VI\.\s*(experiment|experiments?|evaluation)\.?\s*$',
        'roman_conclusion': r'(?i)^VII\.\s*(conclusion|conclusions?)\.?\s*$',
        'roman_references': r'(?i)^VIII\.\s*(references?|bibliography)\.?\s*$',

        # Numbered patterns (1., 2., 3., etc.)
        'numbered_introduction': r'(?i)^1\.\s*(introduction|intro)\.?\s*$',
        'numbered_methods': r'(?i)^2\.\s*(methods?|methodology|approach)\.?\s*$',
        'numbered_results': r'(?i)^3\.\s*(results?|findings|experiments?)\.?\s*$',
        'numbered_discussion': r'(?i)^4\.\s*(discussion|analysis)\.?\s*$',
        'numbered_conclusion': r'(?i)^5\.\s*(conclusion|conclusions?)\.?\s*$',
        'numbered_references': r'(?i)^6\.\s*(references?|bibliography)\.?\s*$',

        # Generic Roman numeral pattern (fallback)
        'roman_section': r'(?i)^([IVX]+)\.\s*(.+?)\.?\s*$',

        # Generic numbered pattern (fallback)
        'numbered_section': r'(?i)^(\d+)\.\s*(.+?)\.?\s*$',

        # Letter subsection patterns (A., B., C., etc.)
        'subsection_letter': r'(?i)^([A-Z])\.\s*(.+?)\.?\s*$'
    }

    def extract(self) -> Dict[str, Any]:
        """Extract document sections.

        Returns:
            Dictionary containing identified sections
        """
        logger.info("Starting section extraction")

        try:
            # Get full text first
            content_extractor = ContentExtractor(self.pdf_content)
            content_data = content_extractor.extract()
            full_text = content_data["full_text"]

            # Handle section detection for text with section breaks
            sections = {}

            if "===SECTION_BREAK===" in full_text:
                # Split by section breaks first
                section_blocks = full_text.split("===SECTION_BREAK===")

                for i, block in enumerate(section_blocks):
                    block = block.strip()
                    if not block:
                        continue

                    lines = block.split('\n')
                    section_header = None
                    section_content = []

                    for line in lines:
                        line = line.strip()
                        if not line:
                            continue

                        # Check if first non-empty line is a section header
                        if section_header is None:
                            section_found = None
                            section_title = None

                            # Debug logging for lines that look like section headers
                            if re.match(r'^[IVX]+\.\s+', line) or re.match(r'^\d+\.\s+', line) or re.match(r'^[A-Z]\.\s+', line):
                                logger.debug(f"Checking potential section header: '{line}'")

                            for section_name, pattern in self.SECTION_PATTERNS.items():
                                match = re.match(pattern, line)
                                if match:
                                    section_found = section_name
                                    section_title = line.strip()
                                    logger.debug(f"MATCHED pattern '{section_name}': '{line}'")
                                    break

                            # Map Roman numeral and numbered sections to standard names
                            if section_found:
                                # Create a mapping for better section organization
                                section_mapping = {
                                    'roman_abstract': 'abstract',
                                    'roman_introduction': 'introduction',
                                    'roman_preliminaries': 'preliminaries',
                                    'roman_framework': 'methodology',
                                    'roman_applications': 'applications',
                                    'roman_correction': 'risk_correction',
                                    'roman_experiment': 'experiments',
                                    'roman_conclusion': 'conclusion',
                                    'roman_references': 'references',
                                    'numbered_introduction': 'introduction',
                                    'numbered_methods': 'methodology',
                                    'numbered_results': 'results',
                                    'numbered_discussion': 'discussion',
                                    'numbered_conclusion': 'conclusion',
                                    'numbered_references': 'references'
                                }

                                # Use mapped name if available, otherwise use original
                                if section_found in section_mapping:
                                    section_header = section_mapping[section_found]
                                elif section_found == 'roman_section':
                                    # Extract section title from generic Roman numeral pattern
                                    match = re.match(r'(?i)^([IVX]+)\.\s*(.+?)\.?\s*$', line)
                                    if match:
                                        roman_num, title = match.groups()
                                        section_header = f"section_{roman_num.lower()}_{title.lower().replace(' ', '_')}"
                                elif section_found == 'numbered_section':
                                    # Extract section title from generic numbered pattern
                                    match = re.match(r'(?i)^(\d+)\.\s*(.+?)\.?\s*$', line)
                                    if match:
                                        num, title = match.groups()
                                        section_header = f"section_{num}_{title.lower().replace(' ', '_')}"
                                elif section_found == 'subsection_letter':
                                    # Extract subsection title from letter pattern
                                    match = re.match(r'(?i)^([A-Z])\.\s*(.+?)\.?\s*$', line)
                                    if match:
                                        letter, title = match.groups()
                                        section_header = f"subsection_{letter.lower()}_{title.lower().replace(' ', '_')}"
                                else:
                                    section_header = section_found

                                logger.debug(f"Found section: {section_found} -> {section_header} ('{section_title}')")
                                # Don't include the header line in content for clean headers
                                if not line.startswith('#') or 'content page' in line.lower():
                                    section_content.append(line)
                            else:
                                section_content.append(line)
                        else:
                            section_content.append(line)

                    # Save the section
                    if section_header:
                        sections[section_header] = '\n'.join(section_content).strip()
                    elif section_content:
                        # Handle blocks without clear headers
                        content_text = '\n'.join(section_content).strip()
                        if i == 0:  # First block might be title/abstract
                            if len(content_text) > 100 and any(word in content_text.lower() for word in ['abstract', 'introduction', 'model', 'method']):
                                sections['abstract'] = content_text
                            else:
                                sections['preliminary'] = content_text
                        else:
                            # Add to preliminary or create generic section
                            if 'preliminary' not in sections:
                                sections['preliminary'] = content_text
                            else:
                                sections['preliminary'] += '\n\n' + content_text

            else:
                # Fallback to original line-by-line detection for regular text
                # First, try to split text on section headers that are embedded in flowing text
                full_text_processed = self._split_on_embedded_section_headers(full_text)
                lines = full_text_processed.split('\n')
                current_section = None
                current_content = []

                for line in lines:
                    line = line.strip()
                    if not line:
                        continue

                    # Check if line matches a section header
                    section_found = None
                    section_title = None

                    # Debug logging for lines that look like section headers
                    if re.match(r'^[IVX]+\.\s+', line) or re.match(r'^\d+\.\s+', line) or re.match(r'^[A-Z]\.\s+', line):
                        logger.debug(f"Checking potential section header: '{line}'")

                    for section_name, pattern in self.SECTION_PATTERNS.items():
                        match = re.match(pattern, line)
                        if match:
                            section_found = section_name
                            section_title = line.strip()
                            logger.debug(f"MATCHED pattern '{section_name}': '{line}'")
                            break

                    if section_found:
                        # Save previous section
                        if current_section and current_content:
                            sections[current_section] = '\n'.join(current_content).strip()

                        # Map section names using the same logic as above
                        section_mapping = {
                            'roman_abstract': 'abstract',
                            'roman_introduction': 'introduction',
                            'roman_preliminaries': 'preliminaries',
                            'roman_framework': 'methodology',
                            'roman_applications': 'applications',
                            'roman_correction': 'risk_correction',
                            'roman_experiment': 'experiments',
                            'roman_conclusion': 'conclusion',
                            'roman_references': 'references',
                            'numbered_introduction': 'introduction',
                            'numbered_methods': 'methodology',
                            'numbered_results': 'results',
                            'numbered_discussion': 'discussion',
                            'numbered_conclusion': 'conclusion',
                            'numbered_references': 'references'
                        }

                        # Use mapped name if available, otherwise use original
                        if section_found in section_mapping:
                            current_section = section_mapping[section_found]
                        elif section_found == 'roman_section':
                            # Extract section title from generic Roman numeral pattern
                            match = re.match(r'(?i)^([IVX]+)\.\s*(.+?)\.?\s*$', line)
                            if match:
                                roman_num, title = match.groups()
                                current_section = f"section_{roman_num.lower()}_{title.lower().replace(' ', '_')}"
                        elif section_found == 'numbered_section':
                            # Extract section title from generic numbered pattern
                            match = re.match(r'(?i)^(\d+)\.\s*(.+?)\.?\s*$', line)
                            if match:
                                num, title = match.groups()
                                current_section = f"section_{num}_{title.lower().replace(' ', '_')}"
                        elif section_found == 'subsection_letter':
                            # Extract subsection title from letter pattern
                            match = re.match(r'(?i)^([A-Z])\.\s*(.+?)\.?\s*$', line)
                            if match:
                                letter, title = match.groups()
                                current_section = f"subsection_{letter.lower()}_{title.lower().replace(' ', '_')}"
                        else:
                            current_section = section_found

                        current_content = []
                        logger.debug(f"Found section: {section_found} -> {current_section} ('{section_title}')")

                    elif current_section:
                        # Add line to current section
                        current_content.append(line)
                    else:
                        # Before any section is found, collect in preliminary content
                        if 'preliminary' not in sections:
                            sections['preliminary'] = []
                        if isinstance(sections['preliminary'], list):
                            sections['preliminary'].append(line)
                        else:
                            sections['preliminary'] += '\n' + line

                # Save the last section
                if current_section and current_content:
                    sections[current_section] = '\n'.join(current_content).strip()

            # Clean up preliminary section
            if 'preliminary' in sections and isinstance(sections['preliminary'], list):
                sections['preliminary'] = clean_text('\n'.join(sections['preliminary']))

            # If only preliminary content exists, rename it to body for clarity
            if len(sections) == 1 and 'preliminary' in sections:
                sections['body'] = sections.pop('preliminary')

            self.extracted_data = {
                "sections": sections,
                "section_count": len(sections),
                "identified_sections": list(sections.keys())
            }

            logger.info(f"Section extraction completed: {len(sections)} sections found")
            return self.extracted_data

        finally:
            self._close_document()

    def _split_on_embedded_section_headers(self, text: str) -> str:
        """Split text on embedded section headers and put each on its own line."""

        # Define patterns for section headers that might be embedded in text
        section_header_patterns = [
            r'(I\.\s+INTRODUCTION)',
            r'(II\.\s+PRELIMINARIES)',
            r'(III\.\s+GENERALIZED\s+FRAMEWORK)',
            r'(IV\.\s+BRIDGING[^.]*?)',
            r'(V\.\s+RISK\s+CORRECTION)',
            r'(VI\.\s+EXPERIMENT)',
            r'(VII\.\s+CONCLUSION)',
            r'(VIII\.\s+REFERENCES)',
            # More specific Roman numeral patterns to avoid over-matching
            r'(\bI\.\s+[A-Z][A-Z\s]+?)(?=\s+[A-Z][a-z])',
            r'(\bII\.\s+[A-Z][A-Z\s]+?)(?=\s+[A-Z][a-z])',
            r'(\bIII\.\s+[A-Z][A-Z\s]+?)(?=\s+[A-Z][a-z])',
            r'(\bIV\.\s+[A-Z][A-Z\s]+?)(?=\s+[A-Z][a-z])',
            r'(\bV\.\s+[A-Z][A-Z\s]+?)(?=\s+[A-Z][a-z])',
            r'(\bVI\.\s+[A-Z][A-Z\s]+?)(?=\s+[A-Z][a-z])',
            r'(\bVII\.\s+[A-Z][A-Z\s]+?)(?=\s+[A-Z][a-z])',
            # Letter subsections
            r'(\b[A-Z]\.\s+[A-Z][a-zA-Z\s]+?)(?=\s+[A-Z][a-z])',
        ]

        # Split text on these patterns, keeping the delimiters
        import re
        for pattern in section_header_patterns:
            # Use replacement to add newlines around section headers
            text = re.sub(pattern, r'\n\1\n', text)

        # Clean up multiple newlines and leading/trailing whitespace
        text = re.sub(r'\n+', '\n', text)
        text = text.strip()

        return text

class FigureExtractor(BaseExtractor):
    """Extracts figures and images from PDF."""

    def extract(self) -> Dict[str, Any]:
        """Extract figures from PDF.

        Returns:
            Dictionary containing figure information and data
        """
        logger.info("Starting figure extraction")
        
        if not FITZ_AVAILABLE or fitz is None:
            logger.warning("PyMuPDF not available - figure extraction skipped")
            return {
                "figures": [],
                "figure_count": 0,
                "total_size_bytes": 0,
                "error": "PyMuPDF not available"
            }
        
        doc = self._open_document()

        try:
            figures = []
            figure_count = 0

            for page_num in range(doc.page_count):
                progress_callback(page_num + 1, doc.page_count, f"Extracting figures from page {page_num + 1}")

                page = doc[page_num]
                with suppress_stderr():
                    image_list = page.get_images(full=True)

                for img_index, img in enumerate(image_list):
                    try:
                        # Get image data
                        xref = img[0]
                        with suppress_stderr():
                            pix = fitz.Pixmap(doc, xref)

                        # Skip images that are too small (likely decorative elements)
                        if pix.width < 50 or pix.height < 50:
                            pix = None
                            continue

                        figure_count += 1

                        # Convert to PNG if not already
                        if pix.n - pix.alpha < 4:  # GRAY or RGB
                            with suppress_stderr():
                                img_data = pix.tobytes("png")
                        else:  # CMYK: convert to RGB first
                            with suppress_stderr():
                                pix_rgb = fitz.Pixmap(fitz.csRGB, pix)
                                img_data = pix_rgb.tobytes("png")
                            pix_rgb = None

                        figures.append({
                            "figure_id": f"figure_{figure_count}",
                            "page": page_num + 1,
                            "width": pix.width,
                            "height": pix.height,
                            "size_bytes": len(img_data),
                            "data": img_data,
                            "format": "png"
                        })

                        pix = None  # Free memory

                    except Exception as e:
                        logger.warning(f"Failed to extract image {img_index} from page {page_num + 1}: {str(e)}")
                        continue

            self.extracted_data = {
                "figures": figures,
                "figure_count": figure_count,
                "total_size_bytes": sum(fig["size_bytes"] for fig in figures)
            }

            logger.info(f"Figure extraction completed: {figure_count} figures found")
            return self.extracted_data

        finally:
            self._close_document()

class TableExtractor(BaseExtractor):
    """Extracts tables from PDF (enhanced implementation)."""

    def extract(self) -> Dict[str, Any]:
        """Extract tables from PDF.

        Returns:
            Dictionary containing enhanced table information

        Note:
            Enhanced implementation with precise detection focused on actual tabular data.
            Prioritizes accuracy over recall to minimize false positives.
        """
        logger.info("Starting precise table extraction")
        doc = self._open_document()

        if doc is None:
            logger.error("Failed to open document")
            return {
                'total_tables': 0,
                'tables': [],
                'extraction_method': 'precise_tabular_detection',
                'error': 'Failed to open document'
            }

        try:
            all_tables = []

            for page_num in range(doc.page_count):
                progress_callback(page_num + 1, doc.page_count, f"Analyzing page {page_num + 1} for tables")
                page = doc[page_num]

                # Use focused detection approach
                page_tables = self._detect_actual_tables(page, page_num)
                all_tables.extend(page_tables)

            return {
                'total_tables': len(all_tables),
                'tables': all_tables,
                'extraction_method': 'precise_tabular_detection'
            }

        finally:
            self._close_document()

    def _detect_actual_tables(self, page, page_num: int) -> List[Dict[str, Any]]:
        """Detect actual tabular data using precise heuristics."""

        page_text = self._extract_page_text_robust(page)
        if not page_text.strip():
            return []

        lines = page_text.split('\n')
        tables = []

        # Method 1: Look for formal table captions followed by structured data
        tables.extend(self._find_captioned_tables(lines, page_num))

        # Method 2: Look for standalone structured data blocks (no caption)
        tables.extend(self._find_standalone_tabular_blocks(lines, page_num))

        # Remove duplicates and validate quality
        tables = self._validate_and_deduplicate_tables(tables)

        return tables

    def _find_captioned_tables(self, lines: List[str], page_num: int) -> List[Dict[str, Any]]:
        """Find tables that have formal captions followed by structured data."""
        tables = []

        # Enhanced pattern to catch various table caption formats
        caption_patterns = [
            r'(?i)Table\s+[IVX\d]+[:\.]?\s*(.+?)(?:\.|$)',  # Table I: caption
            r'(?i)Tab\.\s+[\d]+[:\.]?\s*(.+?)(?:\.|$)',     # Tab. 1: caption
        ]

        for i, line in enumerate(lines):
            line = line.strip()

            # Check if this line contains a table caption
            caption_match = None
            for pattern_idx, pattern in enumerate(caption_patterns):
                caption_match = re.search(pattern, line)
                if caption_match:
                    break

            if caption_match:
                table_title = caption_match.group(1).strip()

                # Look for actual tabular data within next 15 lines
                table_data = self._extract_table_data_after_caption(lines, i, table_title)

                if table_data and len(table_data['rows']) >= 2:  # Need header + at least 1 data row
                    table_dict = {
                        'table_id': f'table_{len(tables) + 1}',
                        'page_number': page_num + 1,
                        'title': table_title,
                        'raw_text': '\n'.join(table_data['rows']),
                        'row_count': len(table_data['rows']),
                        'column_count': table_data['columns'],
                        'detection_method': 'captioned_table',
                        'confidence': table_data['confidence'],
                        'start_line': table_data['start_line'],
                        'end_line': table_data['end_line']
                    }
                    
                    # Enhance with CSV conversion
                    enhanced_table = enhance_table_with_csv(table_dict)
                    tables.append(enhanced_table)

        return tables

    def _extract_table_data_after_caption(self, lines: List[str], caption_line: int, title: str) -> Dict[str, Any]:
        """Extract the actual table data that follows a caption."""

        table_rows = []
        start_line = None
        end_line = None
        max_columns = 0

        # Look ahead for structured data
        for j in range(caption_line + 1, min(caption_line + 20, len(lines))):
            current_line = lines[j].strip()

            if not current_line:
                continue

            # Stop if we hit another section/table
            if self._line_is_section_break(current_line):
                break

            # Check if this line contains actual tabular data
            if self._is_genuine_table_row(current_line):
                if start_line is None:
                    start_line = j
                end_line = j
                table_rows.append(current_line)

                # Estimate column count
                col_count = self._estimate_column_count(current_line)
                max_columns = max(max_columns, col_count)

            elif table_rows and not self._could_be_table_continuation(current_line):
                # If we have some table rows and this line clearly isn't table data, stop
                break

        if not table_rows:
            return {
                'rows': [],
                'columns': 0,
                'confidence': 0.0,
                'start_line': -1,
                'end_line': -1
            }

        # Calculate confidence based on table quality
        confidence = self._calculate_table_confidence(table_rows, max_columns)

        return {
            'rows': table_rows,
            'columns': max_columns,
            'confidence': confidence,
            'start_line': start_line,
            'end_line': end_line
        }

    def _find_standalone_tabular_blocks(self, lines: List[str], page_num: int) -> List[Dict[str, Any]]:
        """Find blocks of structured tabular data without captions."""
        tables = []

        current_block = []
        block_start = None

        for i, line in enumerate(lines):
            line = line.strip()

            if not line:
                # Empty line - check if current block is substantial enough
                if len(current_block) >= 3:  # Need at least 3 rows for standalone table
                    confidence = self._calculate_table_confidence(current_block, self._estimate_max_columns(current_block))

                    if confidence >= 0.5:  # Lowered confidence threshold for standalone tables
                        table_dict = {
                            'table_id': f'table_{len(tables) + 1}',
                            'page_number': page_num + 1,
                            'title': f'Table on page {page_num + 1}',
                            'raw_text': '\n'.join(current_block),
                            'row_count': len(current_block),
                            'column_count': self._estimate_max_columns(current_block),
                            'detection_method': 'standalone_block',
                            'confidence': confidence,
                            'start_line': block_start,
                            'end_line': i - 1
                        }
                        
                        # Enhance with CSV conversion
                        enhanced_table = enhance_table_with_csv(table_dict)
                        tables.append(enhanced_table)

                current_block = []
                block_start = None
                continue

            if self._is_genuine_table_row(line):
                if not current_block:
                    block_start = i
                current_block.append(line)
            else:
                # Not a table row, process current block if substantial
                if len(current_block) >= 3:
                    confidence = self._calculate_table_confidence(current_block, self._estimate_max_columns(current_block))

                    if confidence >= 0.5:  # Lowered confidence threshold
                        tables.append({
                            'table_id': f'table_{len(tables) + 1}',
                            'page_number': page_num + 1,
                            'title': f'Table on page {page_num + 1}',
                            'raw_text': '\n'.join(current_block),
                            'row_count': len(current_block),
                            'column_count': self._estimate_max_columns(current_block),
                            'detection_method': 'standalone_block',
                            'confidence': confidence,
                            'start_line': block_start,
                            'end_line': i - 1
                        })

                current_block = []
                block_start = None

        return tables

    def _could_be_table_continuation(self, line: str) -> bool:
        """Check if a line could be a continuation of table data."""
        if len(line.strip()) < 3:
            return False

        # Empty lines or very short lines are not table continuations
        if not line.strip():
            return False

        # If it looks like a section header, it's not a table continuation
        if self._line_is_section_break(line):
            return False

        # If it has some structure (separators, numbers), it could be table data
        if re.search(r'[\\t|]', line) or re.search(r'\\d', line):
            return True

        # If it has multiple words separated by spaces, could be table data
        words = line.split()
        if len(words) >= 2 and len(words) <= 10:
            return True

        return False

    def _validate_and_deduplicate_tables(self, tables: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Validate and deduplicate tables based on their raw text and position."""
        seen_raw_text_positions = {}
        valid_tables = []

        for table in tables:
            raw_text = table['raw_text']

            # Check if this raw text has been seen at a different position
            if raw_text in seen_raw_text_positions:
                # If it's a duplicate, keep the one with the lower confidence
                if seen_raw_text_positions[raw_text]['confidence'] < table['confidence']:
                    seen_raw_text_positions[raw_text] = table
                continue

            # Check if the table is significantly overlapping with another
            is_overlapping = False
            for existing_table in valid_tables:
                if self._blocks_overlap(existing_table, table):
                    is_overlapping = True
                    break

            if not is_overlapping:
                valid_tables.append(table)
                seen_raw_text_positions[raw_text] = table

        return valid_tables

    def _estimate_column_count(self, line: str) -> int:
        """Estimate the number of columns in a line based on common patterns."""
        # Simple heuristic: count words and assume a reasonable number of columns
        words = line.split()
        return min(len(words), 15)  # Max 15 columns for estimation

    def _estimate_max_columns(self, lines: List[str]) -> int:
        """Estimate the maximum number of columns across all lines in a block."""
        max_cols = 0
        for line in lines:
            max_cols = max(max_cols, self._estimate_column_count(line))
        return max_cols

    def _calculate_table_confidence(self, rows: List[str], max_columns: int) -> float:
        """Calculate confidence score for table detection with enhanced false positive detection."""
        if not rows or max_columns < 2:
            return 0.0

        confidence = 0.3  # Base confidence for having rows

        # ENHANCED FALSE POSITIVE DETECTION
        false_positive_score = self._calculate_false_positive_score(rows)
        if false_positive_score > 0.7:  # High likelihood of false positive
            return max(0.0, confidence - 0.4)  # Significantly reduce confidence

        # Column structure bonus
        if max_columns >= 3:
            confidence += 0.1
        if max_columns >= 4:
            confidence += 0.1

        # Row consistency bonus
        if len(rows) >= 3:
            confidence += 0.1

        # Detect numeric data patterns
        all_text = '\n'.join(rows)
        numeric_patterns = len(re.findall(r'\b\d+\.\d+\\b', all_text))
        if numeric_patterns >= 5:
            confidence += 0.2
        elif numeric_patterns >= 2:
            confidence += 0.1

        # Separators boost
        if '\t' in all_text or '|' in all_text:
            confidence += 0.2

        # ENHANCED POSITIVE INDICATORS
        # Technical/academic terms that indicate genuine table content
        technical_score = self._calculate_technical_content_score(rows)
        confidence += technical_score * 0.2

        # Structural consistency bonus
        structure_score = self._calculate_structural_consistency_score(rows)
        confidence += structure_score * 0.1

        return min(confidence, 1.0)  # Cap at 1.0

    def _calculate_false_positive_score(self, rows: List[str]) -> float:
        """Calculate likelihood that detected table is actually a false positive."""
        if not rows:
            return 0.0

        false_positive_indicators = 0
        total_rows = len(rows)

        for row in rows:
            # Check for figure caption patterns
            if re.search(r'(Figure|Fig\.|Table|Algorithm|Equation)\s+\d+', row, re.IGNORECASE):
                false_positive_indicators += 2  # High weight for captions

            # Check for author affiliations
            if re.search(r'(University|Institute|Department|Email:|@)', row, re.IGNORECASE):
                false_positive_indicators += 1

            # Check for flowing text patterns
            if re.search(r'\b(however|therefore|thus|moreover|furthermore|consequently)\b', row, re.IGNORECASE):
                false_positive_indicators += 1

            # Check for complete sentences
            if row.count('.') >= 2 or (row.endswith('.') and len(row.split()) > 8):
                false_positive_indicators += 1

            # Check for equation patterns
            if re.search(r'\w+\s*=\s*\w+|where\s+\w+', row, re.IGNORECASE):
                false_positive_indicators += 1

        return min(false_positive_indicators / total_rows, 1.0)

    def _calculate_technical_content_score(self, rows: List[str]) -> float:
        """Calculate score for technical/academic content typical in tables."""
        if not rows:
            return 0.0

        technical_terms = [
            'algorithm', 'dataset', 'method', 'baseline', 'accuracy', 'precision', 'recall',
            'error', 'time', 'performance', 'mae', 'rmse', 'mape', 'learning', 'training',
            'validation', 'test', 'score', 'metric', 'result', 'comparison', 'evaluation'
        ]

        technical_indicators = 0
        total_words = 0

        for row in rows:
            words = row.lower().split()
            total_words += len(words)
            for word in words:
                if any(term in word for term in technical_terms):
                    technical_indicators += 1

        return min(technical_indicators / max(total_words, 1) * 5, 1.0)  # Scale appropriately

    def _calculate_structural_consistency_score(self, rows: List[str]) -> float:
        """Calculate score for structural consistency typical in tables."""
        if len(rows) < 2:
            return 0.0

        # Check for consistent column counts
        column_counts = []
        for row in rows:
            # Count potential columns using various delimiters
            col_count = max(
                len(re.split(r'\s{2,}', row)),  # Multiple spaces
                len(row.split('\t')),           # Tabs
                len(row.split('|')),             # Pipes
                len(row.split())                 # Single spaces
            )
            column_counts.append(col_count)

        if not column_counts:
            return 0.0

        # Calculate consistency
        avg_columns = sum(column_counts) / len(column_counts)
        variance = sum((count - avg_columns) ** 2 for count in column_counts) / len(column_counts)
        consistency = 1.0 / (1.0 + variance)  # Higher consistency = lower variance

        return consistency

    def _is_genuine_table_row(self, line: str) -> bool:
        """Check if a line looks like it could be part of a table - balanced for academic content."""
        if len(line.strip()) < 3:
            return False

        # ENHANCED EXCLUSIONS FOR FIGURE CAPTIONS
        # Exclude figure captions and simple lists
        if re.match(r'^\\s*\\([a-f]\\)\\s+', line.strip()):  # (a), (b), (c) patterns
            return False

        # More comprehensive figure caption patterns
        figure_patterns = [
            r'^\\s*(Figure|Fig\\.|Table|Algorithm|Equation|Eq\\.)\\s+\\d+',  # Figure 1, Table 2, etc.
            r'^\\s*(Figure|Fig\\.|Table)\\s+[IVX]+',  # Figure I, Table II, etc.
            r'Caption:|^Caption\\s+\\d+',  # Caption: or Caption 1
            r'^\\s*\\d+\\.\\s+(Figure|Table|Algorithm)',  # 1. Figure caption
        ]
        
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in figure_patterns):
            return False

        # ENHANCED EXCLUSIONS FOR ACADEMIC CONTENT
        # Exclude obviously non-tabular content
        if re.match(r'^\\s*(Figure|Fig\\.|Abstract|Introduction|Conclusion|References|Bibliography)', line.strip(), re.IGNORECASE):
            return False
            
        # Exclude author affiliations (common false positives)
        affiliation_patterns = [
            r'^\\s*\\d+\\s*[A-Z][a-z]+\\s+University',  # 1 Stanford University
            r'^\\s*[A-Z][a-z]+\\s+Institute',  # MIT Institute
            r'^\\s*Department\\s+of',  # Department of Computer Science
            r'^\\s*\\*\\s*[A-Z][a-z]+',  # *Corresponding author
            r'Email:\\s*\\w+@',  # Email addresses
            r'^\\s*[A-Z][a-z]+\\s+[A-Z][a-z]+\\s*,?\\s*[A-Z][a-z]+',  # Full names
        ]
        
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in affiliation_patterns):
            return False
            
        # Exclude equations and mathematical expressions
        equation_patterns = [
            r'^\\s*\\w+\\s*=\\s*\\w+',  # Simple equations x = y
            r'^\\s*where\\s+\\w+',  # "where x is..."
            r'^\\s*[A-Z]\\s*=\\s*',  # Variable definitions
            r'^\\s*Equation\\s+\\d+',  # Equation references
        ]
        
        if any(re.search(pattern, line, re.IGNORECASE) for pattern in equation_patterns):
            return False

        # **STRICT EXCLUSIONS: Flowing text / paragraphs**
        words = line.split()

        # Exclude long flowing sentences (typical paragraph text)
        if len(words) > 12:  # Very long lines are likely paragraphs
            return False

        # Exclude lines with paragraph indicators
        paragraph_indicators = ['compared to', 'however', 'therefore', 'thus', 'moreover', 'furthermore',
                              'in addition', 'consequently', 'as a result', 'on the other hand',
                              'in contrast', 'similarly', 'likewise', 'for example', 'for instance',
                              'such as', 'in particular', 'specifically', 'namely']

        line_lower = line.lower()
        if any(indicator in line_lower for indicator in paragraph_indicators):
            return False

        # Exclude complete sentences (academic tables have shorter, structured entries)
        if line.count('.') >= 2 or (line.endswith('.') and len(words) > 8):
            return False

        # **POSITIVE INDICATORS: Table-like content**

        # 1. VERY SHORT STRUCTURED ENTRIES (high confidence table content)
        if 1 <= len(words) <= 4:
            # Short entries with academic/technical terms
            technical_terms = ['supervision', 'assumption', 'pointwise', 'pairwise', 'task', 'setting',
                             'learning', 'label', 'dataset', 'algorithm', 'method', 'baseline',
                             'accuracy', 'precision', 'recall', 'error', 'time', 'performance']

            if any(term in line_lower for term in technical_terms):
                return True

            # Short entries with parenthetical info (common in tables)
            if '(' in line and ')' in line:
                return True

        # 2. CLEAR COLUMN SEPARATORS
        separator_indicators = ['\\t', '   ', ' | ', '|', '&']  # Multiple spaces, tabs, pipes
        separator_count = sum(line.count(sep) for sep in separator_indicators)

        if separator_count >= 2 and 2 <= len(words) <= 8:  # Clear multi-column structure
            return True

        # 3. NUMERICAL DATA ROWS
        numbers = re.findall(r'\b\d+\.?\d*\b', line)
        if len(numbers) >= 2 and len(words) <= 10:  # Multiple numbers in reasonable length
            return True

        # 4. REFERENCE CITATIONS (but only if short)
        if re.search(r'\\[\\d+\\]', line) and len(words) <= 6:  # [5], [9] etc. in short context
            return True

        # 5. CONSISTENT CAPITALIZATION PATTERNS (headers)
        if len(words) <= 5:
            caps_words = re.findall(r'\b[A-Z]{2,}\b', line)
            if len(caps_words) >= 1:
                return True

            # Title case headers (common in academic tables)
            title_case_words = sum(1 for word in words if word[0].isupper() and len(word) > 1)
            if title_case_words >= 2:
                return True

        return False

    def _line_contains_tabular_data(self, line: str) -> bool:
        """Check if line contains data patterns typical of tables."""
        # Exclude figure captions and references
        if re.match(r'^\s*\([a-f]\)\s+', line.strip()):
            return False
        if re.match(r'^\s*Figure\s+\d+:', line.strip(), re.IGNORECASE):
            return False
        if len(line.strip()) < 15:  # Too short for meaningful table data
            return False

        # Look for clear numerical/tabular patterns
        patterns = [
            r'\d+\.\d+',            # Decimal numbers
            r'\b\d{4}\b',           # Years
            r'\d+%',                # Percentages
            r'\$\d+\.?\d*',         # Money
            r'\d+/\d+',             # Fractions
            r'\d+:\d+',             # Ratios/times
        ]

        # Count numeric/tabular patterns
        pattern_count = 0
        for pattern in patterns:
            pattern_count += len(re.findall(pattern, line))

        # Also check for algorithm/dataset names commonly found in comparison tables
        algorithm_indicators = ['ARIMA', 'Algorithm', 'Dataset', 'MAE', 'RMSE', 'Time', 'Error']
        has_algorithm_terms = any(term in line for term in algorithm_indicators)

        # Must have substantial numerical content OR be clearly a table header
        words = line.split()
        return ((pattern_count >= 3 and len(words) >= 4) or
                (has_algorithm_terms and len(words) >= 3))

    def _line_is_table_data(self, line: str) -> bool:
        """Check if a line contains actual tabular data (structured columns)."""
        if len(line.strip()) < 3:
            return False

        # Look for patterns that indicate tabular data
        # Multiple numbers with consistent spacing
        number_pattern = r'\b\d+\.?\d*\b'
        numbers = re.findall(number_pattern, line)

        # Check for common table separators and structure
        separators = ['\t', '  ', ' | ', '|', '&']  # Including LaTeX & separator

        # Count separators
        separator_count = 0
        for sep in separators:
            separator_count += line.count(sep)

        # Strong indicators of table data:
        # 1. Multiple numbers with separators
        if len(numbers) >= 2 and separator_count >= 1:
            return True

        # 2. Has performance metrics or scientific notation
        if re.search(r'\b\d+\.\d{2,4}\b', line) and separator_count >= 1:  # Decimal numbers like 0.3541
            return True

        # 3. Parenthetical values (often std deviations in tables)
        if re.search(r'\(\d+\.\d+\)', line) and separator_count >= 1:
            return True

        # 4. Scientific data patterns
        if re.search(r'\b[A-Z][A-Z0-9]*\b.*\d', line) and separator_count >= 1:  # Like "FR 0.3445"
            return True

        # 5. Multiple short alphanumeric codes/names with numbers
        codes = re.findall(r'\b[A-Z]{1,4}\b', line)
        if len(codes) >= 2 and len(numbers) >= 1:
            return True

        return False

    def _line_might_be_table_header(self, line: str) -> bool:
        """Check if a line might be a table header."""
        if len(line.strip()) < 3:
            return False

        # Headers often have:
        # 1. Column names separated by spaces/tabs
        words = line.split()
        if len(words) >= 3:  # At least 3 columns
            # Check if words look like column headers
            header_indicators = ['data', 'type', 'method', 'result', 'score', 'value', 'name',
                               'vectorization', 'pd', 'average', 'performance', 'algorithm',
                               'low1', 'nnb', 'ap', 'fr', 'persistence', 'image']

            header_words = sum(1 for word in words if word.lower() in header_indicators)
            if header_words >= 1:
                return True

        # 2. Consistent spacing/formatting
        if '\t' in line or '  ' in line:
            return True

        # 3. All caps words (common in headers)
        caps_words = re.findall(r'\b[A-Z]{2,}\b', line)
        if len(caps_words) >= 2:
            return True

        return False

    def _line_is_section_break(self, line: str) -> bool:
        """Check if a line indicates a section break that would end a table."""
        if len(line.strip()) < 3:
            return False

        # Section headers
        if re.match(r'^\d+\s+[A-Z]', line):  # "4 Results & Discussion"
            return True

        # Figure/Algorithm captions
        if re.match(r'(?i)^(Fig|Figure|Algorithm|Theorem|Lemma|Equation)', line):
            return True

        # Subsection headers
        if re.match(r'^\d+\.\d+', line):  # "4.1 Analysis"
            return True

        # All caps headers
        if len(line.split()) <= 5 and line.isupper():
            return True

        return False

    def _blocks_overlap(self, block1: Dict[str, Any], block2: Dict[str, Any]) -> bool:
        """Check if two table blocks overlap."""
        return not (block1["end_line"] < block2["start_line"] or
                   block2["end_line"] < block1["start_line"])

class CitationExtractor(BaseExtractor):
    """Extracts citations and references from PDF."""

    def extract(self) -> Dict[str, Any]:
        """Extract citations and references.

        Returns:
            Dictionary containing enhanced citation information
        """
        logger.info("Starting enhanced citation extraction")

        try:
            # Get sections first
            section_extractor = SectionExtractor(self.pdf_content)
            section_data = section_extractor.extract()

            # Look for references section with multiple approaches
            references_text = self._find_references_section(section_data)

            citations = []
            if references_text:
                citations = self._parse_references(references_text)
                logger.info(f"Found {len(citations)} references in dedicated section")
            else:
                # Try to find references throughout the document
                content_extractor = ContentExtractor(self.pdf_content)
                content_data = content_extractor.extract()
                full_text = content_data["full_text"]
                citations = self._extract_references_from_full_text(full_text)
                logger.info(f"Extracted {len(citations)} references from full text analysis")

            # Look for in-text citations in the main content
            content_extractor = ContentExtractor(self.pdf_content)
            content_data = content_extractor.extract()
            full_text = content_data["full_text"]

            in_text_citations = self._extract_in_text_citations(full_text)

            self.extracted_data = {
                "reference_list": citations,
                "in_text_citations": in_text_citations,
                "reference_count": len(citations),
                "in_text_count": len(in_text_citations),
                "has_reference_section": bool(references_text),
                "note": "Enhanced citation extraction with multiple detection methods"
            }

            logger.info(f"Enhanced citation extraction completed: {len(citations)} references, {len(in_text_citations)} in-text citations")
            return self.extracted_data

        finally:
            self._close_document()

    def _find_references_section(self, section_data: Dict[str, Any]) -> str:
        """Find the references section using multiple approaches."""
        sections = section_data.get("sections", {})

        # Direct match
        if "references" in sections:
            return sections["references"]

        # Check for variations
        reference_variations = [
            "references", "bibliography", "works_cited", "citations",
            "reference_list", "literature_cited", "references_cited"
        ]

        for key in sections:
            if any(var in key.lower() for var in reference_variations):
                return sections[key]

        # Look for reference-like content in any section
        for key, content in sections.items():
            if self._content_looks_like_references(content):
                logger.info(f"Found reference-like content in section: {key}")
                return content

        return ""

    def _content_looks_like_references(self, content: str) -> bool:
        """Check if content looks like a references section."""
        if not content or len(content) < 100:
            return False

        lines = content.split('\n')
        reference_lines = 0

        for line in lines:
            line = line.strip()
            if not line:
                continue

            # Check for reference-like patterns
            if self._line_looks_like_reference(line):
                reference_lines += 1

        # If more than 30% of lines look like references, consider it a reference section
        non_empty_lines = len([line for line in lines if line.strip()])
        return reference_lines / non_empty_lines > 0.3 if non_empty_lines > 0 else False

    def _line_looks_like_reference(self, line: str) -> bool:
        """Check if a line looks like a reference citation."""
        # Common reference patterns
        patterns = [
            r'^\d+\.\s+',  # Numbered references (1. Author...)
            r'^\[\d+\]\s+',  # Bracketed numbers ([1] Author...)
            r'\(\d{4}\)',  # Year in parentheses
            r'et\s+al\.?',  # "et al."
            r'doi:\s*10\.',  # DOI
            r'https?://',  # URLs
            r'pp?\.\s*\d+',  # Page numbers
            r'vol\.\s*\d+',  # Volume numbers
            r'proceedings',  # Conference proceedings
            r'journal',  # Journal mentions
        ]

        # Must have reasonable length and contain some reference indicators
        if len(line) < 20:
            return False

        pattern_matches = 0
        for pattern in patterns:
            if re.search(pattern, line, re.IGNORECASE):
                pattern_matches += 1

        # Also check for author patterns (Last, First or First Last)
        author_patterns = [
            r'[A-Z][a-z]+,\s+[A-Z]\.?',  # Last, F.
            r'[A-Z]\.\s*[A-Z][a-z]+',    # F. Last
        ]

        for pattern in author_patterns:
            if re.search(pattern, line):
                pattern_matches += 1

        return pattern_matches >= 2

    def _parse_references(self, references_text: str) -> List[Dict[str, Any]]:
        """Parse references from the references section text."""
        citations = []
        lines = references_text.split('\n')

        current_ref = []
        ref_count = 0

        for line in lines:
            line = line.strip()
            if not line:
                if current_ref:
                    ref_count += 1
                    citations.append(self._create_citation_object(current_ref, ref_count))
                    current_ref = []
                continue

            # Check if this is the start of a new reference
            if (re.match(r'^\d+\.\s+', line) or
                re.match(r'^\[\d+\]\s+', line) or
                (not current_ref and self._line_looks_like_reference(line))):

                # Save previous reference if exists
                if current_ref:
                    ref_count += 1
                    citations.append(self._create_citation_object(current_ref, ref_count))

                # Start new reference
                current_ref = [line]
            else:
                # Continue current reference
                if current_ref:
                    current_ref.append(line)
                elif self._line_looks_like_reference(line):
                    # Start new reference even without number
                    current_ref = [line]

        # Save final reference
        if current_ref:
            ref_count += 1
            citations.append(self._create_citation_object(current_ref, ref_count))

        return citations

    def _extract_references_from_full_text(self, full_text: str) -> List[Dict[str, Any]]:
        """Extract references from full text when no dedicated section is found."""
        citations = []
        lines = full_text.split('\n')

        # Look for reference-like lines throughout the document
        ref_count = 0
        for i, line in enumerate(lines):
            line = line.strip()
            if self._line_looks_like_reference(line) and len(line) > 50:
                ref_count += 1
                citations.append(self._create_citation_object([line], ref_count))

        return citations

    def _create_citation_object(self, ref_lines: List[str], ref_id: int) -> Dict[str, Any]:
        """Create a citation object from reference lines."""
        full_text = ' '.join(ref_lines).strip()

        # Extract basic information
        citation = {
            "citation_id": f"citation_{ref_id}",
            "raw_text": full_text,
            "authors": self._extract_authors(full_text),
            "title": self._extract_title(full_text),
            "year": self._extract_year(full_text),
            "doi": self._extract_doi(full_text),
            "url": self._extract_url(full_text)
        }

        return citation

    def _extract_authors(self, text: str) -> List[str]:
        """Extract author names from citation text."""
        authors = []

        # Look for author patterns
        author_patterns = [
            r'([A-Z][a-z]+),\s+([A-Z]\.?\s*)+',  # Last, F. M.
            r'([A-Z]\.?\s*)+\s+([A-Z][a-z]+)',   # F. M. Last
        ]

        for pattern in author_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                authors.append(match.group().strip())

        return authors[:5]  # Limit to first 5 authors

    def _extract_title(self, text: str) -> str:
        """Extract title from citation text."""
        # Look for quoted titles or titles after author and before year
        title_patterns = [
            r'"([^"]+)"',  # Quoted titles
            r'\.([^.]+)\.',  # Between periods
        ]

        for pattern in title_patterns:
            match = re.search(pattern, text)
            if match and len(match.group(1)) > 10:  # Reasonable title length
                return match.group(1).strip()

        return ""

    def _extract_year(self, text: str) -> str:
        """Extract publication year from citation text."""
        year_pattern = r'\b(19|20)\d{2}\b'
        match = re.search(year_pattern, text)
        return match.group() if match else ""

    def _extract_doi(self, text: str) -> str:
        """Extract DOI from citation text."""
        doi_pattern = r'doi:\s*(10\.\S+)'
        match = re.search(doi_pattern, text, re.IGNORECASE)
        return match.group(1) if match else ""

    def _extract_url(self, text: str) -> str:
        """Extract URL from citation text."""
        url_pattern = r'https?://\S+'
        match = re.search(url_pattern, text)
        return match.group() if match else ""

    def _extract_in_text_citations(self, full_text: str) -> List[Dict[str, Any]]:
        """Extract in-text citations with enhanced patterns."""
        in_text_citations = []

        # Enhanced in-text citation patterns
        patterns = [
            (r'\(([A-Z][a-z]+(?:\s+et\s+al\.?)?,?\s+\d{4}[a-z]?)\)', 'author_year'),
            (r'\(([A-Z][a-z]+(?:\s+&\s+[A-Z][a-z]+)?,?\s+\d{4}[a-z]?)\)', 'author_year_ampersand'),
            (r'\[(\d+)\]', 'numbered'),
            (r'\[(\d+[-,\s]*\d*)\]', 'numbered_range'),
            (r'\((\d+)\)', 'numbered_parentheses'),
            (r'([A-Z][a-z]+\s+\(\d{4}\))', 'author_year_inline'),
        ]

        for pattern, citation_type in patterns:
            matches = re.finditer(pattern, full_text)
            for match in matches:
                in_text_citations.append({
                    "citation_text": match.group(1),
                    "full_match": match.group(0),
                    "position": match.start(),
                    "type": citation_type,
                    "context": full_text[max(0, match.start() - 50):match.end() + 50]
                })

        # Remove duplicates and sort by position
        unique_citations = []
        seen_positions = set()

        for citation in in_text_citations:
            if citation["position"] not in seen_positions:
                unique_citations.append(citation)
                seen_positions.add(citation["position"])

        return sorted(unique_citations, key=lambda x: x["position"])

def extract_all_content(pdf_content: bytes, output_format: Optional[str] = None, output_path: Optional[str] = None) -> Dict[str, Any]:
    """Extract all content types from PDF with optional output formatting.

    Args:
        pdf_content: PDF file as bytes
        output_format: Optional output format (html, latex, xml, csv, markdown)
        output_path: Optional path for formatted output

    Returns:
        Combined extraction results
    """
    from datetime import datetime

    logger.info("Starting comprehensive content extraction with plugin support")

    results = {
        "extraction_timestamp": datetime.now().isoformat(),
        "content": {},
        "sections": {},
        "figures": {},
        "tables": {},
        "citations": {},
        "equations": {},
        "metadata": {},
        "citation_networks": {}
    }

    try:
        # Initialize plugin system
        plugin_manager = get_plugin_manager()
        
        # Pre-process document hook
        temp_file_path = None
        try:
            import tempfile
            import os
            
            # Create temporary file for plugin access
            with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                tmp_file.write(pdf_content)
                temp_file_path = tmp_file.name
            
            # Execute pre-processing hooks
            preprocessed_path = execute_hook_until_success(
                "pre_process_document", 
                temp_file_path, 
                {"output_format": output_format, "output_path": output_path}
            )
            
            if preprocessed_path:
                logger.info(f"Document preprocessed by plugin: {preprocessed_path}")
                # Read the preprocessed PDF
                with open(preprocessed_path, 'rb') as f:
                    pdf_content = f.read()
                
                # Clean up preprocessed file if it's different from original
                if preprocessed_path != temp_file_path and os.path.exists(preprocessed_path):
                    os.unlink(preprocessed_path)
            
        except Exception as e:
            logger.warning(f"Plugin pre-processing failed: {e}")
        
        # Document validation hook
        try:
            validation_results = execute_hook(
                "validate_document",
                temp_file_path or "",
                {"format": output_format}
            )
            
            # If any plugin rejects the document, skip processing
            if validation_results and any(not result for result in validation_results if result is not None):
                logger.warning("Document validation failed - skipping processing")
                results["validation_status"] = "failed"
                return results
            
        except Exception as e:
            logger.warning(f"Document validation failed: {e}")
        
                # Content extraction with plugin enhancement
        content_extractor = ContentExtractor(pdf_content)
        results["content"] = content_extractor.extract()
        
        # Enhanced text extraction through plugins
        try:
            enhanced_text = execute_hook_until_success(
                "extract_text",
                temp_file_path or "",
                -1,  # All pages
                {"method": "enhanced"}
            )
            
            if enhanced_text:
                logger.info("Enhanced text extraction successful")
                results["content"]["enhanced_text"] = enhanced_text
        except Exception as e:
            logger.warning(f"Enhanced text extraction failed: {e}")

        # Section extraction with plugin enhancement
        section_extractor = SectionExtractor(pdf_content)
        results["sections"] = section_extractor.extract()
        
        # Enhanced section detection through plugins
        try:
            enhanced_sections = execute_hook_until_success(
                "detect_sections",
                results["content"].get("full_text", ""),
                results["content"].get("pages", []),
                {"method": "enhanced"}
            )
            
            if enhanced_sections:
                logger.info("Enhanced section detection successful")
                results["sections"]["enhanced_sections"] = enhanced_sections
        except Exception as e:
            logger.warning(f"Enhanced section detection failed: {e}")

        # Figure extraction with plugin enhancement
        figure_extractor = FigureExtractor(pdf_content)
        results["figures"] = figure_extractor.extract()
        
        # Enhanced figure extraction through plugins
        try:
            if FITZ_AVAILABLE and fitz is not None:
                doc = fitz.open(stream=pdf_content, filetype="pdf")
                enhanced_figures = execute_hook_until_success(
                    "extract_figures",
                    doc,
                    {"method": "enhanced"}
                )
                
                if enhanced_figures:
                    logger.info("Enhanced figure extraction successful")
                    results["figures"]["enhanced_figures"] = enhanced_figures
                    
                doc.close()
            else:
                logger.warning("Enhanced figure extraction skipped - PyMuPDF not available")
        except Exception as e:
            logger.warning(f"Enhanced figure extraction failed: {e}")

        # Table extraction with plugin enhancement
        table_extractor = TableExtractor(pdf_content)
        results["tables"] = table_extractor.extract()
        
        # Enhanced table processing through plugins
        try:
            if FITZ_AVAILABLE and fitz is not None:
                doc = fitz.open(stream=pdf_content, filetype="pdf")
                enhanced_tables = execute_hook_until_success(
                    "process_tables",
                    doc,
                    results["content"].get("full_text", ""),
                    {"method": "enhanced"}
                )
                
                if enhanced_tables:
                    logger.info("Enhanced table processing successful")
                    results["tables"]["enhanced_tables"] = enhanced_tables
                    
                doc.close()
            else:
                logger.warning("Enhanced table processing skipped - PyMuPDF not available")
        except Exception as e:
            logger.warning(f"Enhanced table processing failed: {e}")

        # Citation extraction
        citation_extractor = CitationExtractor(pdf_content)
        results["citations"] = citation_extractor.extract()

        # Equation extraction (Stage 5 feature)
        try:
            from .equation_processor import process_equations_from_pdf
            results["equations"] = process_equations_from_pdf(pdf_content)
            
            # Enhanced equation processing through plugins
            try:
                enhanced_equations = execute_hook(
                    "process_equations",
                    results["equations"].get("equations", []),
                    {"method": "enhanced"}
                )
                
                if enhanced_equations:
                    logger.info("Enhanced equation processing successful")
                    # Use the best result from plugins
                    for enhanced_result in enhanced_equations:
                        if enhanced_result and isinstance(enhanced_result, list):
                            results["equations"]["enhanced_equations"] = enhanced_result
                            break
            except Exception as e:
                logger.warning(f"Enhanced equation processing failed: {e}")
                
        except ImportError:
            logger.warning("Equation processing not available")
            results["equations"] = {"total_equations": 0, "equations": [], "processing_status": "not_available"}

        # Advanced figure processing (Stage 5 feature)
        try:
            from .advanced_figure_processor import process_advanced_figures
            results["advanced_figures"] = process_advanced_figures(pdf_content)
        except ImportError:
            logger.warning("Advanced figure processing not available")
            results["advanced_figures"] = {"total_figures": 0, "figures": [], "processing_status": "not_available"}

        # Enhanced metadata extraction (Stage 5 feature)
        try:
            from .metadata_extractor import extract_metadata
            
            # Use existing temp file or create new one
            if not temp_file_path:
                import tempfile
                import os
                
                # Create temporary file for metadata extraction
                with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                    tmp_file.write(pdf_content)
                    temp_file_path = tmp_file.name
            
            try:
                metadata = extract_metadata(temp_file_path)
                results["metadata"] = metadata.to_dict()
                
                # Enhanced metadata processing through plugins
                try:
                    enhanced_metadata = execute_hook(
                        "enhance_metadata",
                        results["metadata"],
                        {"method": "enhanced"}
                    )
                    
                    if enhanced_metadata:
                        logger.info("Enhanced metadata processing successful")
                        # Use the best result from plugins
                        for enhanced_result in enhanced_metadata:
                            if enhanced_result and isinstance(enhanced_result, dict):
                                results["metadata"]["enhanced_metadata"] = enhanced_result
                                break
                except Exception as e:
                    logger.warning(f"Enhanced metadata processing failed: {e}")
                    
            finally:
                # Clean up temporary file if we created it
                if temp_file_path and os.path.exists(temp_file_path):
                    os.unlink(temp_file_path)
                    
        except ImportError:
            logger.warning("Enhanced metadata extraction not available")
            results["metadata"] = {"processing_status": "not_available"}
        except Exception as e:
            logger.error(f"Metadata extraction failed: {str(e)}")
            results["metadata"] = {"processing_status": "error", "error": str(e)}

        # Citation network analysis (Stage 5 feature)
        try:
            from .citation_network_analyzer import analyze_citation_networks
            
            # Prepare metadata for network analysis
            papers_metadata = []
            if results["metadata"].get("processing_status") not in ["not_available", "error"]:
                papers_metadata.append(results["metadata"])
            
            # Only perform network analysis if we have metadata
            if papers_metadata:
                results["citation_networks"] = analyze_citation_networks(papers_metadata)
            else:
                results["citation_networks"] = {"processing_status": "insufficient_data", "message": "Network analysis requires metadata"}
        except ImportError:
            logger.warning("Citation network analysis not available")
            results["citation_networks"] = {"processing_status": "not_available"}
        except Exception as e:
            logger.error(f"Citation network analysis failed: {str(e)}")
            results["citation_networks"] = {"processing_status": "error", "error": str(e)}

        # Summary statistics
        results["summary"] = {
            "total_pages": results["content"].get("statistics", {}).get("page_count", 0),
            "total_words": results["content"].get("statistics", {}).get("word_count", 0),
            "sections_found": results["sections"].get("section_count", 0),
            "figures_found": results["figures"].get("figure_count", 0),
            "tables_found": results["tables"].get("total_tables", 0),
            "references_found": results["citations"].get("reference_count", 0),
            "equations_found": results["equations"].get("total_equations", 0),
            "advanced_figures_found": results["advanced_figures"].get("total_figures", 0),
            "captions_found": results["advanced_figures"].get("total_captions", 0),
            "metadata_extracted": results["metadata"].get("processing_status", "unknown") not in ["not_available", "error"],
            "authors_found": len(results["metadata"].get("authors", [])),
            "keywords_found": len(results["metadata"].get("keywords", [])),
            "citations_in_metadata": len(results["metadata"].get("citations", [])),
            "doi_found": bool(results["metadata"].get("doi")),
            "title_confidence": results["metadata"].get("title_confidence", 0.0),
            "abstract_confidence": results["metadata"].get("abstract_confidence", 0.0),
            "author_confidence": results["metadata"].get("author_confidence", 0.0),
            "citation_networks_analyzed": results["citation_networks"].get("processing_status", "unknown") not in ["not_available", "error", "insufficient_data"],
            "total_papers_in_network": results["citation_networks"].get("total_papers_analyzed", 0),
            "network_types_built": len(results["citation_networks"].get("networks", {}))
        }

        # Output formatting (Stage 5 feature)
        if output_format and output_path:
            try:
                from .output_formatters import format_output
                
                # Plugin-enhanced output formatting
                try:
                    custom_output = execute_hook_until_success(
                        "format_output",
                        results,
                        output_format,
                        {"path": output_path, "method": "enhanced"}
                    )
                    
                    if custom_output:
                        logger.info("Custom output formatting successful")
                        # Save custom output
                        with open(output_path, 'w', encoding='utf-8') as f:
                            f.write(custom_output)
                        results["output_formatted"] = {"format": output_format, "path": output_path, "success": True, "method": "plugin"}
                    else:
                        # Fall back to default formatting
                        success = format_output(results, output_path, output_format)
                        if success:
                            logger.info(f"Results formatted and saved to {output_path} in {output_format} format")
                            results["output_formatted"] = {"format": output_format, "path": output_path, "success": True, "method": "default"}
                        else:
                            logger.warning(f"Failed to format results in {output_format} format")
                            results["output_formatted"] = {"format": output_format, "path": output_path, "success": False}
                except Exception as e:
                    logger.warning(f"Plugin output formatting failed: {e}")
                    # Fall back to default formatting
                    success = format_output(results, output_path, output_format)
                    if success:
                        logger.info(f"Results formatted and saved to {output_path} in {output_format} format")
                        results["output_formatted"] = {"format": output_format, "path": output_path, "success": True, "method": "default"}
                    else:
                        logger.warning(f"Failed to format results in {output_format} format")
                        results["output_formatted"] = {"format": output_format, "path": output_path, "success": False}
                        
            except ImportError:
                logger.warning("Output formatting not available")
                results["output_formatted"] = {"error": "Output formatting not available"}
            except Exception as e:
                logger.error(f"Output formatting failed: {str(e)}")
                results["output_formatted"] = {"error": str(e)}

        # Post-processing and validation hooks
        try:
            # Post-process results through plugins
            enhanced_results = execute_hook_until_success(
                "post_process_document",
                temp_file_path or "",
                results,
                {"output_format": output_format, "output_path": output_path}
            )
            
            if enhanced_results:
                logger.info("Post-processing enhancement successful")
                results["post_processed"] = True
                # Merge enhanced results
                if isinstance(enhanced_results, dict):
                    results.update(enhanced_results)
            
            # Validate output quality
            if output_path:
                try:
                    validation_results = execute_hook(
                        "validate_output",
                        output_path,
                        results,
                        {"format": output_format}
                    )
                    
                    if validation_results:
                        logger.info("Output validation completed")
                        results["validation_results"] = [
                            result for result in validation_results 
                            if result is not None
                        ]
                except Exception as e:
                    logger.warning(f"Output validation failed: {e}")
                    
        except Exception as e:
            logger.warning(f"Post-processing failed: {e}")
        
        # Clean up temporary file
        if temp_file_path and os.path.exists(temp_file_path):
            try:
                os.unlink(temp_file_path)
            except Exception as e:
                logger.warning(f"Failed to clean up temporary file: {e}")

        logger.info("Comprehensive content extraction completed successfully with plugin support")
        return results

    except Exception as e:
        logger.error(f"Content extraction failed: {str(e)}")
        raise ProcessingError(f"Failed to extract content: {str(e)}")


def extract_all_content_optimized(pdf_content: bytes, enable_parallel: bool = True) -> Dict[str, Any]:
    """Extract all content types from PDF with Stage 4 performance optimizations.

    Args:
        pdf_content: PDF file as bytes
        enable_parallel: Whether to use parallel processing (default: True)

    Returns:
        Combined extraction results with performance optimizations
    """
    logger.info("Starting optimized content extraction with Stage 4 enhancements")
    
    if enable_parallel:
        # Use parallel extraction with full optimization
        try:
            from .performance import extract_with_full_optimization
            logger.info("Using parallel extraction with caching and monitoring")
            results = extract_with_full_optimization(pdf_content)
            
            # Add equation processing if not already included
            if "equations" not in results:
                try:
                    from .equation_processor import process_equations_from_pdf
                    results["equations"] = process_equations_from_pdf(pdf_content)
                    results["summary"]["equations_found"] = results["equations"].get("total_equations", 0)
                except ImportError:
                    logger.warning("Equation processing not available")
                    results["equations"] = {"total_equations": 0, "equations": [], "processing_status": "not_available"}
                    results["summary"]["equations_found"] = 0
            
            # Add advanced figure processing if not already included
            if "advanced_figures" not in results:
                try:
                    from .advanced_figure_processor import process_advanced_figures
                    results["advanced_figures"] = process_advanced_figures(pdf_content)
                    results["summary"]["advanced_figures_found"] = results["advanced_figures"].get("total_figures", 0)
                    results["summary"]["captions_found"] = results["advanced_figures"].get("total_captions", 0)
                except ImportError:
                    logger.warning("Advanced figure processing not available")
                    results["advanced_figures"] = {"total_figures": 0, "figures": [], "processing_status": "not_available"}
                    results["summary"]["advanced_figures_found"] = 0
                    results["summary"]["captions_found"] = 0
            
            # Add enhanced metadata extraction if not already included
            if "metadata" not in results:
                try:
                    from .metadata_extractor import extract_metadata
                    import tempfile
                    import os
                    
                    # Create temporary file for metadata extraction
                    with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
                        tmp_file.write(pdf_content)
                        tmp_file_path = tmp_file.name
                    
                    try:
                        metadata = extract_metadata(tmp_file_path)
                        results["metadata"] = metadata.to_dict()
                        # Update summary statistics
                        results["summary"]["metadata_extracted"] = True
                        results["summary"]["authors_found"] = len(results["metadata"].get("authors", []))
                        results["summary"]["keywords_found"] = len(results["metadata"].get("keywords", []))
                        results["summary"]["citations_in_metadata"] = len(results["metadata"].get("citations", []))
                        results["summary"]["doi_found"] = bool(results["metadata"].get("doi"))
                        results["summary"]["title_confidence"] = results["metadata"].get("title_confidence", 0.0)
                        results["summary"]["abstract_confidence"] = results["metadata"].get("abstract_confidence", 0.0)
                        results["summary"]["author_confidence"] = results["metadata"].get("author_confidence", 0.0)
                    finally:
                        # Clean up temporary file
                        os.unlink(tmp_file_path)
                except ImportError:
                    logger.warning("Enhanced metadata extraction not available")
                    results["metadata"] = {"processing_status": "not_available"}
                    results["summary"]["metadata_extracted"] = False
                    results["summary"]["authors_found"] = 0
                    results["summary"]["keywords_found"] = 0
                    results["summary"]["citations_in_metadata"] = 0
                    results["summary"]["doi_found"] = False
                    results["summary"]["title_confidence"] = 0.0
                    results["summary"]["abstract_confidence"] = 0.0
                    results["summary"]["author_confidence"] = 0.0
                except Exception as e:
                    logger.error(f"Metadata extraction failed: {str(e)}")
                    results["metadata"] = {"processing_status": "error", "error": str(e)}
                    results["summary"]["metadata_extracted"] = False
                    results["summary"]["authors_found"] = 0
                    results["summary"]["keywords_found"] = 0
                    results["summary"]["citations_in_metadata"] = 0
                    results["summary"]["doi_found"] = False
                    results["summary"]["title_confidence"] = 0.0
                    results["summary"]["abstract_confidence"] = 0.0
                    results["summary"]["author_confidence"] = 0.0
            
            return results
        except ImportError:
            logger.warning("Performance module not available, falling back to sequential extraction")
            return extract_all_content(pdf_content)
    else:
        # Use sequential extraction with memory optimization
        from .performance import memory_optimized
        
        @memory_optimized
        def _extract_sequential():
            return extract_all_content(pdf_content)
        
        return _extract_sequential()

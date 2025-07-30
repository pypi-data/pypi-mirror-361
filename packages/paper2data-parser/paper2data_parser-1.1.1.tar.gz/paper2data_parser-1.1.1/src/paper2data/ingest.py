"""
Input ingestion and validation for Paper2Data.

Handles PDF files, arXiv URLs, DOI resolution, and input sanitization.
"""

import logging
from pathlib import Path
from typing import Union, Optional, Dict, Any, Tuple
from urllib.parse import urlparse
import requests
import fitz  # PyMuPDF
from .utils import get_logger, ValidationError, ProcessingError
from .api_integration import arxiv_client, doi_client

logger = get_logger(__name__)


class BaseIngestor:
    """Base class for all input ingestors."""
    
    def __init__(self, input_source: str) -> None:
        self.input_source = input_source
        self.metadata: Dict[str, Any] = {}
    
    def validate(self) -> bool:
        """Validate the input source."""
        raise NotImplementedError("Subclasses must implement validate method")
    
    def ingest(self) -> bytes:
        """Ingest and return the content as bytes."""
        raise NotImplementedError("Subclasses must implement ingest method")


class PDFIngestor(BaseIngestor):
    """Handles PDF file input validation and loading."""
    
    def validate(self) -> bool:
        """Validate that the PDF file exists and is readable.
        
        Returns:
            True if PDF is valid
            
        Raises:
            ValidationError: If PDF is invalid or cannot be read
        """
        logger.info(f"Validating PDF file: {self.input_source}")
        
        path = Path(self.input_source)
        
        # Basic file validation
        if not path.exists():
            raise ValidationError(f"PDF file not found: {self.input_source}")
        
        if not path.is_file():
            raise ValidationError(f"Path is not a file: {self.input_source}")
        
        # Check file extension
        if path.suffix.lower() != '.pdf':
            raise ValidationError(f"File must be a PDF: {self.input_source}")
        
        # Check file size (max 100MB)
        file_size = path.stat().st_size
        max_size = 100 * 1024 * 1024  # 100MB
        if file_size > max_size:
            raise ValidationError(f"PDF too large: {file_size / (1024*1024):.1f}MB (max: 100MB)")
        
        # Try to open PDF with PyMuPDF to validate structure
        try:
            doc = fitz.open(self.input_source)
            
            if doc.page_count == 0:
                raise ValidationError("PDF has no pages")
            
            # Extract basic metadata
            metadata = doc.metadata
            page_count = doc.page_count  # Get page count before closing
            self.metadata.update({
                "page_count": page_count,
                "title": metadata.get("title", "").strip(),
                "author": metadata.get("author", "").strip(),
                "subject": metadata.get("subject", "").strip(),
                "creator": metadata.get("creator", "").strip(),
                "producer": metadata.get("producer", "").strip(),
                "creation_date": metadata.get("creationDate", ""),
                "modification_date": metadata.get("modDate", ""),
                "file_size": file_size
            })
            
            doc.close()
            logger.info(f"PDF validation successful: {page_count} pages, {file_size / 1024:.1f}KB")
            return True
            
        except Exception as e:
            raise ValidationError(f"Invalid or corrupted PDF: {str(e)}")
    
    def ingest(self) -> bytes:
        """Load PDF file content.
        
        Returns:
            PDF content as bytes
            
        Raises:
            ProcessingError: If PDF cannot be loaded
        """
        logger.info(f"Loading PDF file: {self.input_source}")
        
        try:
            with open(self.input_source, 'rb') as f:
                content = f.read()
            
            logger.info(f"PDF loaded successfully: {len(content)} bytes")
            return content
            
        except Exception as e:
            raise ProcessingError(f"Failed to load PDF file: {str(e)}")


class URLIngestor(BaseIngestor):
    """Handles arXiv URL processing and download with enhanced API integration."""
    
    def validate(self) -> bool:
        """Validate that the URL is a valid arXiv URL or accessible PDF URL.
        
        Returns:
            True if URL is valid
            
        Raises:
            ValidationError: If URL is invalid
        """
        logger.info(f"Validating URL: {self.input_source}")
        
        # Basic URL validation
        if not self.input_source.strip():
            raise ValidationError("URL cannot be empty")
        
        parsed = urlparse(self.input_source)
        
        # Check for supported URL types
        if parsed.scheme not in ('http', 'https'):
            raise ValidationError("URL must use http or https protocol")
        
        # Enhanced arXiv URL pattern validation
        if 'arxiv.org' in parsed.netloc:
            # Extract arXiv ID pattern
            if '/abs/' in parsed.path or '/pdf/' in parsed.path:
                arxiv_id = parsed.path.split('/')[-1].replace('.pdf', '')
                
                try:
                    # Use the enhanced arXiv API client for validation and metadata
                    metadata = arxiv_client.get_paper_metadata(arxiv_id)
                    
                    self.metadata.update({
                        "source_type": "arxiv",
                        "arxiv_id": arxiv_id,
                        "original_url": self.input_source,
                        "enhanced_metadata": metadata
                    })
                    
                    logger.info(f"Valid arXiv URL detected with enhanced metadata: {metadata['title']}")
                    return True
                    
                except Exception as e:
                    raise ValidationError(f"Invalid arXiv ID or API error: {str(e)}")
        
        # For other URLs, just check basic accessibility
        try:
            response = requests.head(self.input_source, timeout=10)
            response.raise_for_status()
            
            content_type = response.headers.get('content-type', '').lower()
            if 'pdf' not in content_type:
                logger.warning("URL does not appear to point to a PDF file")
            
            self.metadata.update({
                "source_type": "url",
                "content_type": content_type,
                "content_length": response.headers.get('content-length'),
                "original_url": self.input_source
            })
            
            logger.info("URL validation successful")
            return True
            
        except requests.RequestException as e:
            raise ValidationError(f"URL not accessible: {str(e)}")
    
    def ingest(self) -> bytes:
        """Download paper from URL using enhanced API integration.
        
        Returns:
            Downloaded PDF content as bytes
            
        Raises:
            ProcessingError: If download fails
        """
        logger.info(f"Downloading from URL: {self.input_source}")
        
        try:
            # Use enhanced arXiv API client for arXiv URLs
            if self.metadata.get("source_type") == "arxiv":
                arxiv_id = self.metadata.get("arxiv_id")
                if arxiv_id:
                    logger.info(f"Using enhanced arXiv API for download: {arxiv_id}")
                    content = arxiv_client.download_paper(arxiv_id)
                    
                    self.metadata.update({
                        "downloaded_size": len(content),
                        "download_method": "arxiv_api"
                    })
                    
                    return content
            
            # For non-arXiv URLs, use standard download
            download_url = self.input_source
            response = requests.get(download_url, timeout=30)
            response.raise_for_status()
            
            # Verify it's actually a PDF
            content = response.content
            if not content.startswith(b'%PDF'):
                raise ProcessingError("Downloaded content is not a valid PDF")
            
            self.metadata.update({
                "downloaded_size": len(content),
                "download_url": download_url,
                "download_method": "direct"
            })
            
            logger.info(f"Download successful: {len(content)} bytes")
            return content
            
        except requests.RequestException as e:
            raise ProcessingError(f"Failed to download from URL: {str(e)}")
        except Exception as e:
            raise ProcessingError(f"Unexpected error during download: {str(e)}")


class DOIIngestor(BaseIngestor):
    """Handles DOI resolution and paper retrieval with enhanced API integration."""
    
    def validate(self) -> bool:
        """Validate DOI and fetch comprehensive metadata.
        
        Returns:
            True if DOI is valid
            
        Raises:
            ValidationError: If DOI is invalid
        """
        logger.info(f"Validating DOI: {self.input_source}")
        
        try:
            # Use the enhanced DOI API client for validation and metadata
            metadata = doi_client.resolve_doi(self.input_source)
            
            self.metadata.update({
                "source_type": "doi",
                "doi": metadata["doi"],
                "original_input": self.input_source,
                "enhanced_metadata": metadata
            })
            
            logger.info(f"DOI validation successful with enhanced metadata: {metadata['title']}")
            return True
            
        except Exception as e:
            raise ValidationError(f"Invalid DOI or API error: {str(e)}")
    
    def ingest(self) -> bytes:
        """Resolve DOI and attempt to download paper using enhanced API integration.
        
        Returns:
            Downloaded PDF content as bytes
            
        Raises:
            ProcessingError: If DOI resolution or download fails
        """
        logger.info(f"Resolving DOI: {self.input_source}")
        
        try:
            # Get enhanced metadata
            enhanced_metadata = self.metadata.get("enhanced_metadata", {})
            
            # Check if PDF URL is available
            pdf_url = enhanced_metadata.get("pdf_url")
            if pdf_url:
                logger.info(f"Found PDF URL in metadata: {pdf_url}")
                
                # Attempt to download PDF
                response = requests.get(pdf_url, timeout=30)
                response.raise_for_status()
                
                content = response.content
                
                # Verify it's actually a PDF
                if not content.startswith(b'%PDF'):
                    raise ProcessingError("Downloaded content is not a valid PDF")
                
                self.metadata.update({
                    "downloaded_size": len(content),
                    "download_url": pdf_url,
                    "download_method": "doi_direct"
                })
                
                logger.info(f"DOI PDF download successful: {len(content)} bytes")
                return content
            
            # If no direct PDF URL, try to find alternative sources
            doi = enhanced_metadata.get("doi", self.input_source)
            
            # Check if this DOI is also in arXiv
            arxiv_id = enhanced_metadata.get("doi")  # Some papers have arXiv IDs in DOI metadata
            if arxiv_id:
                try:
                    logger.info(f"Attempting arXiv download for DOI: {arxiv_id}")
                    content = arxiv_client.download_paper(arxiv_id)
                    
                    self.metadata.update({
                        "downloaded_size": len(content),
                        "download_method": "doi_to_arxiv"
                    })
                    
                    return content
                except Exception as e:
                    logger.warning(f"Failed to download via arXiv: {str(e)}")
            
            # If no direct download is possible, provide informative error
            title = enhanced_metadata.get("title", "Unknown")
            journal = enhanced_metadata.get("journal", "Unknown")
            
            error_msg = (
                f"DOI resolved successfully but PDF download not available. "
                f"Paper: '{title}' from {journal}. "
                f"Please visit the publisher's website or try accessing through institutional access."
            )
            
            raise ProcessingError(error_msg)
            
        except requests.RequestException as e:
            raise ProcessingError(f"Failed to download DOI PDF: {str(e)}")
        except Exception as e:
            raise ProcessingError(f"Unexpected error during DOI resolution: {str(e)}")


def create_ingestor(input_source: str) -> BaseIngestor:
    """Factory function to create appropriate ingestor based on input type.
    
    Args:
        input_source: Input path, URL, or DOI
        
    Returns:
        Appropriate ingestor instance
        
    Raises:
        ValidationError: If input type cannot be determined
    """
    logger.info(f"Creating ingestor for: {input_source}")
    
    # Clean input
    source = input_source.strip()
    
    # Check for DOI
    if (source.startswith('doi:') or 
        source.startswith('10.') or 
        'dx.doi.org' in source or
        'doi.org' in source):
        logger.debug("Detected DOI input")
        return DOIIngestor(source)
    
    # Check for URL
    if source.startswith(('http://', 'https://')):
        logger.debug("Detected URL input")
        return URLIngestor(source)
    
    # Check for arXiv ID (without full URL)
    if source.startswith('arxiv:'):
        arxiv_id = source[6:]
        url = f"https://arxiv.org/abs/{arxiv_id}"
        logger.debug(f"Converting arXiv ID to URL: {url}")
        return URLIngestor(url)
    
    # Default to PDF file
    logger.debug("Assuming PDF file input")
    return PDFIngestor(source) 
"""
API Integration Module for Paper2Data

Handles arXiv API integration, DOI resolution, rate limiting, caching, and batch operations.
"""

import logging
import time
import re
from typing import Dict, Any, Optional, List, Tuple, Union
from pathlib import Path
from datetime import datetime, timedelta
from urllib.parse import urlparse, parse_qs
import json
import hashlib

import requests
import arxiv
import feedparser
from ratelimit import limits, sleep_and_retry
from cachetools import TTLCache
from dateutil.parser import parse as date_parse

from .utils import get_logger, ValidationError, ProcessingError

logger = get_logger(__name__)

# Configuration constants
ARXIV_API_BASE = "http://export.arxiv.org/api/query"
CROSSREF_API_BASE = "https://api.crossref.org/works"
CACHE_TTL = 3600  # 1 hour cache
MAX_CACHE_SIZE = 1000
RATE_LIMIT_CALLS = 10
RATE_LIMIT_PERIOD = 60  # seconds


class APIRateLimiter:
    """Rate limiter for API calls to respect service limits."""
    
    def __init__(self, calls_per_period: int = RATE_LIMIT_CALLS, period: int = RATE_LIMIT_PERIOD):
        self.calls_per_period = calls_per_period
        self.period = period
        self.call_times = []
    
    def __call__(self, func):
        def wrapper(*args, **kwargs):
            now = time.time()
            # Remove old calls outside the period
            self.call_times = [t for t in self.call_times if now - t < self.period]
            
            # Check if we need to wait
            if len(self.call_times) >= self.calls_per_period:
                sleep_time = self.period - (now - self.call_times[0])
                if sleep_time > 0:
                    logger.info(f"Rate limit reached, sleeping for {sleep_time:.2f} seconds")
                    time.sleep(sleep_time)
            
            # Record this call
            self.call_times.append(time.time())
            return func(*args, **kwargs)
        return wrapper


class APICache:
    """Caching system for API responses."""
    
    def __init__(self, ttl: int = CACHE_TTL, maxsize: int = MAX_CACHE_SIZE):
        self.cache = TTLCache(maxsize=maxsize, ttl=ttl)
    
    def get_key(self, method: str, *args, **kwargs) -> str:
        """Generate cache key from method and arguments."""
        key_data = f"{method}:{args}:{sorted(kwargs.items())}"
        return hashlib.md5(key_data.encode()).hexdigest()
    
    def get(self, key: str) -> Optional[Any]:
        """Get cached value."""
        return self.cache.get(key)
    
    def set(self, key: str, value: Any) -> None:
        """Set cached value."""
        self.cache[key] = value
    
    def clear(self) -> None:
        """Clear all cached values."""
        self.cache.clear()


# Global instances
rate_limiter = APIRateLimiter()
api_cache = APICache()


class ArxivAPIClient:
    """Enhanced arXiv API client with comprehensive paper retrieval."""
    
    def __init__(self):
        self.client = arxiv.Client()
    
    @rate_limiter
    def get_paper_metadata(self, arxiv_id: str) -> Dict[str, Any]:
        """Get comprehensive metadata for an arXiv paper.
        
        Args:
            arxiv_id: arXiv identifier (e.g., "2301.00001" or "cs.AI/0601001")
            
        Returns:
            Paper metadata dictionary
            
        Raises:
            ValidationError: If arXiv ID is invalid
            ProcessingError: If API call fails
        """
        cache_key = api_cache.get_key("arxiv_metadata", arxiv_id)
        cached_result = api_cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for arXiv metadata: {arxiv_id}")
            return cached_result
        
        logger.info(f"Fetching arXiv metadata for: {arxiv_id}")
        
        try:
            # Clean arXiv ID
            clean_id = self._clean_arxiv_id(arxiv_id)
            
            # Create search query
            search = arxiv.Search(id_list=[clean_id], max_results=1)
            
            # Get the paper
            papers = list(self.client.results(search))
            
            if not papers:
                raise ValidationError(f"arXiv paper not found: {arxiv_id}")
            
            paper = papers[0]
            
            # Extract comprehensive metadata
            metadata = {
                "arxiv_id": clean_id,
                "title": paper.title,
                "summary": paper.summary,
                "authors": [author.name for author in paper.authors],
                "published": paper.published.isoformat() if paper.published else None,
                "updated": paper.updated.isoformat() if paper.updated else None,
                "categories": paper.categories,
                "primary_category": paper.primary_category,
                "comment": paper.comment,
                "journal_ref": paper.journal_ref,
                "doi": paper.doi,
                "pdf_url": paper.pdf_url,
                "entry_id": paper.entry_id,
                "links": [{"href": link.href, "title": link.title, "rel": link.rel} 
                         for link in paper.links],
                "source_type": "arxiv"
            }
            
            # Cache the result
            api_cache.set(cache_key, metadata)
            
            logger.info(f"arXiv metadata retrieved: {metadata['title']}")
            return metadata
            
        except arxiv.ArxivError as e:
            raise ProcessingError(f"arXiv API error: {str(e)}")
        except Exception as e:
            raise ProcessingError(f"Failed to fetch arXiv metadata: {str(e)}")
    
    @rate_limiter
    def download_paper(self, arxiv_id: str, download_dir: Optional[Path] = None) -> bytes:
        """Download PDF from arXiv.
        
        Args:
            arxiv_id: arXiv identifier
            download_dir: Optional directory to save the PDF
            
        Returns:
            PDF content as bytes
            
        Raises:
            ProcessingError: If download fails
        """
        logger.info(f"Downloading arXiv paper: {arxiv_id}")
        
        try:
            # Get metadata first to get the PDF URL
            metadata = self.get_paper_metadata(arxiv_id)
            pdf_url = metadata["pdf_url"]
            
            # Download PDF
            response = requests.get(pdf_url, timeout=60)
            response.raise_for_status()
            
            content = response.content
            
            # Verify it's a PDF
            if not content.startswith(b'%PDF'):
                raise ProcessingError("Downloaded content is not a valid PDF")
            
            # Optionally save to disk
            if download_dir:
                download_dir = Path(download_dir)
                download_dir.mkdir(exist_ok=True)
                
                filename = f"{arxiv_id.replace('/', '_')}.pdf"
                filepath = download_dir / filename
                
                with open(filepath, 'wb') as f:
                    f.write(content)
                
                logger.info(f"PDF saved to: {filepath}")
            
            logger.info(f"arXiv PDF downloaded: {len(content)} bytes")
            return content
            
        except requests.RequestException as e:
            raise ProcessingError(f"Failed to download arXiv PDF: {str(e)}")
        except Exception as e:
            raise ProcessingError(f"Unexpected error downloading arXiv PDF: {str(e)}")
    
    def _clean_arxiv_id(self, arxiv_id: str) -> str:
        """Clean and validate arXiv ID format.
        
        Args:
            arxiv_id: Raw arXiv identifier
            
        Returns:
            Clean arXiv ID
            
        Raises:
            ValidationError: If ID format is invalid
        """
        # Remove common prefixes
        clean_id = arxiv_id.strip()
        if clean_id.startswith('arxiv:'):
            clean_id = clean_id[6:]
        if clean_id.startswith('arXiv:'):
            clean_id = clean_id[6:]
        
        # Basic format validation
        # New format: YYMM.NNNNN[vN]
        # Old format: subject-class/YYMMnnn
        new_format = re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', clean_id)
        old_format = re.match(r'^[a-z-]+(\.[A-Z]{2})?/\d{7}$', clean_id)
        
        if not (new_format or old_format):
            raise ValidationError(f"Invalid arXiv ID format: {arxiv_id}")
        
        return clean_id
    
    def search_papers(self, query: str, max_results: int = 10) -> List[Dict[str, Any]]:
        """Search for papers on arXiv.
        
        Args:
            query: Search query
            max_results: Maximum number of results to return
            
        Returns:
            List of paper metadata dictionaries
        """
        logger.info(f"Searching arXiv for: {query}")
        
        try:
            search = arxiv.Search(
                query=query,
                max_results=max_results,
                sort_by=arxiv.SortCriterion.SubmittedDate
            )
            
            results = []
            for paper in self.client.results(search):
                results.append({
                    "arxiv_id": paper.get_short_id(),
                    "title": paper.title,
                    "summary": paper.summary[:200] + "..." if len(paper.summary) > 200 else paper.summary,
                    "authors": [author.name for author in paper.authors],
                    "published": paper.published.isoformat() if paper.published else None,
                    "categories": paper.categories,
                    "pdf_url": paper.pdf_url
                })
            
            logger.info(f"Found {len(results)} papers")
            return results
            
        except Exception as e:
            logger.error(f"arXiv search failed: {str(e)}")
            return []


class DOIAPIClient:
    """Enhanced DOI resolution client with publisher API integration."""
    
    def __init__(self):
        self.headers = {
            'User-Agent': 'Paper2Data/1.0 (https://github.com/paper2data/paper2data)'
        }
    
    @rate_limiter
    def resolve_doi(self, doi: str) -> Dict[str, Any]:
        """Resolve DOI and get comprehensive metadata.
        
        Args:
            doi: DOI identifier
            
        Returns:
            Paper metadata dictionary
            
        Raises:
            ValidationError: If DOI is invalid
            ProcessingError: If resolution fails
        """
        cache_key = api_cache.get_key("doi_metadata", doi)
        cached_result = api_cache.get(cache_key)
        if cached_result:
            logger.debug(f"Cache hit for DOI metadata: {doi}")
            return cached_result
        
        logger.info(f"Resolving DOI: {doi}")
        
        try:
            # Clean DOI
            clean_doi = self._clean_doi(doi)
            
            # Get metadata from CrossRef
            url = f"{CROSSREF_API_BASE}/{clean_doi}"
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            
            data = response.json()
            work = data.get('message', {})
            
            # Extract comprehensive metadata
            metadata = {
                "doi": clean_doi,
                "title": work.get('title', [''])[0] if work.get('title') else '',
                "subtitle": work.get('subtitle', [''])[0] if work.get('subtitle') else '',
                "authors": self._extract_authors(work.get('author', [])),
                "published": self._extract_publication_date(work),
                "journal": work.get('container-title', [''])[0] if work.get('container-title') else '',
                "volume": work.get('volume', ''),
                "issue": work.get('issue', ''),
                "pages": work.get('page', ''),
                "publisher": work.get('publisher', ''),
                "type": work.get('type', ''),
                "subject": work.get('subject', []),
                "abstract": work.get('abstract', ''),
                "url": work.get('URL', ''),
                "is_referenced_by_count": work.get('is-referenced-by-count', 0),
                "references_count": work.get('references-count', 0),
                "license": self._extract_license(work.get('license', [])),
                "source_type": "doi"
            }
            
            # Try to find PDF URL
            pdf_url = self._find_pdf_url(work)
            if pdf_url:
                metadata["pdf_url"] = pdf_url
            
            # Cache the result
            api_cache.set(cache_key, metadata)
            
            logger.info(f"DOI resolved: {metadata['title']}")
            return metadata
            
        except requests.RequestException as e:
            raise ProcessingError(f"Failed to resolve DOI: {str(e)}")
        except Exception as e:
            raise ProcessingError(f"Unexpected error resolving DOI: {str(e)}")
    
    def _clean_doi(self, doi: str) -> str:
        """Clean and validate DOI format.
        
        Args:
            doi: Raw DOI identifier
            
        Returns:
            Clean DOI
            
        Raises:
            ValidationError: If DOI format is invalid
        """
        # Remove common prefixes
        clean_doi = doi.strip()
        if clean_doi.startswith('doi:'):
            clean_doi = clean_doi[4:]
        if clean_doi.startswith('http://dx.doi.org/'):
            clean_doi = clean_doi[18:]
        if clean_doi.startswith('https://doi.org/'):
            clean_doi = clean_doi[15:]
        if clean_doi.startswith('https://dx.doi.org/'):
            clean_doi = clean_doi[19:]
        
        # Basic DOI format validation
        if not clean_doi or '/' not in clean_doi:
            raise ValidationError(f"Invalid DOI format: {doi}")
        
        # DOI regex pattern
        doi_pattern = r'^10\.\d{4,}/.+$'
        if not re.match(doi_pattern, clean_doi):
            raise ValidationError(f"Invalid DOI format: {doi}")
        
        return clean_doi
    
    def _extract_authors(self, authors: List[Dict[str, Any]]) -> List[str]:
        """Extract author names from CrossRef author data."""
        result = []
        for author in authors:
            given = author.get('given', '')
            family = author.get('family', '')
            if given and family:
                result.append(f"{given} {family}")
            elif family:
                result.append(family)
        return result
    
    def _extract_publication_date(self, work: Dict[str, Any]) -> Optional[str]:
        """Extract publication date from CrossRef work data."""
        date_fields = ['published-print', 'published-online', 'issued']
        
        for field in date_fields:
            if field in work:
                date_parts = work[field].get('date-parts', [])
                if date_parts and date_parts[0]:
                    parts = date_parts[0]
                    if len(parts) >= 3:
                        return f"{parts[0]}-{parts[1]:02d}-{parts[2]:02d}"
                    elif len(parts) >= 2:
                        return f"{parts[0]}-{parts[1]:02d}"
                    elif len(parts) >= 1:
                        return str(parts[0])
        return None
    
    def _extract_license(self, licenses: List[Dict[str, Any]]) -> Optional[str]:
        """Extract license information from CrossRef license data."""
        if licenses:
            return licenses[0].get('URL', '')
        return None
    
    def _find_pdf_url(self, work: Dict[str, Any]) -> Optional[str]:
        """Try to find PDF URL from CrossRef work data."""
        # Check links
        links = work.get('link', [])
        for link in links:
            if link.get('content-type') == 'application/pdf':
                return link.get('URL')
        
        # Check URL field
        url = work.get('URL', '')
        if url and 'pdf' in url.lower():
            return url
        
        return None


class BatchProcessor:
    """Handle batch operations for multiple papers."""
    
    def __init__(self, arxiv_client: ArxivAPIClient, doi_client: DOIAPIClient):
        self.arxiv_client = arxiv_client
        self.doi_client = doi_client
    
    def process_batch(self, identifiers: List[str], progress_callback=None) -> List[Dict[str, Any]]:
        """Process a batch of paper identifiers.
        
        Args:
            identifiers: List of arXiv IDs, DOIs, or URLs
            progress_callback: Optional callback function for progress updates
            
        Returns:
            List of results with metadata and any errors
        """
        logger.info(f"Processing batch of {len(identifiers)} papers")
        
        results = []
        
        for i, identifier in enumerate(identifiers):
            try:
                # Determine type and get metadata
                if self._is_arxiv_id(identifier):
                    metadata = self.arxiv_client.get_paper_metadata(identifier)
                elif self._is_doi(identifier):
                    metadata = self.doi_client.resolve_doi(identifier)
                else:
                    raise ValidationError(f"Unsupported identifier format: {identifier}")
                
                results.append({
                    "identifier": identifier,
                    "success": True,
                    "metadata": metadata,
                    "error": None
                })
                
            except Exception as e:
                results.append({
                    "identifier": identifier,
                    "success": False,
                    "metadata": None,
                    "error": str(e)
                })
                logger.error(f"Failed to process {identifier}: {str(e)}")
            
            # Progress callback
            if progress_callback:
                progress_callback(i + 1, len(identifiers))
        
        logger.info(f"Batch processing complete: {sum(1 for r in results if r['success'])}/{len(results)} successful")
        return results
    
    def _is_arxiv_id(self, identifier: str) -> bool:
        """Check if identifier is an arXiv ID."""
        clean_id = identifier.strip()
        if clean_id.startswith(('arxiv:', 'arXiv:')):
            return True
        
        # Check patterns
        new_format = re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', clean_id)
        old_format = re.match(r'^[a-z-]+(\.[A-Z]{2})?/\d{7}$', clean_id)
        
        return bool(new_format or old_format)
    
    def _is_doi(self, identifier: str) -> bool:
        """Check if identifier is a DOI."""
        clean_id = identifier.strip()
        if clean_id.startswith(('doi:', '10.', 'http://dx.doi.org/', 'https://doi.org/')):
            return True
        return False


# Global API clients
arxiv_client = ArxivAPIClient()
doi_client = DOIAPIClient()
batch_processor = BatchProcessor(arxiv_client, doi_client) 
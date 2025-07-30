"""
Advanced Bibliographic Parser for Paper2Data Version 1.1

This module provides comprehensive bibliographic data processing including:
- Citation style detection and classification
- Reference parsing and normalization
- Cross-reference validation and resolution
- Citation network analysis
- Bibliographic data quality assessment
"""

import re
import json
import logging
from typing import Dict, List, Any, Optional, Set, Tuple, Union
from dataclasses import dataclass, field, asdict
from enum import Enum
from pathlib import Path
import requests
from urllib.parse import quote
from datetime import datetime

from .utils import get_logger, clean_text, ProcessingError

logger = get_logger(__name__)

class CitationStyle(Enum):
    """Enumeration of citation styles."""
    APA = "apa"
    MLA = "mla"
    IEEE = "ieee"
    CHICAGO = "chicago"
    HARVARD = "harvard"
    VANCOUVER = "vancouver"
    NATURE = "nature"
    SCIENCE = "science"
    ACM = "acm"
    SPRINGER = "springer"
    UNKNOWN = "unknown"

class ReferenceType(Enum):
    """Types of references."""
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    BOOK = "book"
    BOOK_CHAPTER = "book_chapter"
    THESIS = "thesis"
    REPORT = "report"
    WEBSITE = "website"
    PREPRINT = "preprint"
    PATENT = "patent"
    SOFTWARE = "software"
    DATASET = "dataset"
    UNKNOWN = "unknown"

class CitationQuality(Enum):
    """Citation quality levels."""
    EXCELLENT = "excellent"
    GOOD = "good"
    FAIR = "fair"
    POOR = "poor"
    INCOMPLETE = "incomplete"

@dataclass
class BibliographicAuthor:
    """Represents an author in a bibliographic reference."""
    family_name: str
    given_names: List[str] = field(default_factory=list)
    initials: List[str] = field(default_factory=list)
    suffix: Optional[str] = None
    orcid: Optional[str] = None
    normalized_name: str = ""
    
    def __post_init__(self):
        """Post-process author information."""
        if not self.normalized_name:
            self.normalized_name = self._normalize_name()
    
    def _normalize_name(self) -> str:
        """Normalize author name for comparison."""
        name_parts = [self.family_name]
        if self.given_names:
            name_parts.extend(self.given_names)
        elif self.initials:
            name_parts.extend(self.initials)
        
        return " ".join(name_parts).lower().strip()
    
    def get_display_name(self, style: CitationStyle) -> str:
        """Get formatted name according to citation style."""
        if style == CitationStyle.APA:
            if self.given_names:
                initials = [name[0] + "." for name in self.given_names]
                return f"{self.family_name}, {' '.join(initials)}"
            elif self.initials:
                return f"{self.family_name}, {' '.join(self.initials)}"
            else:
                return self.family_name
        elif style == CitationStyle.MLA:
            if self.given_names:
                return f"{self.family_name}, {' '.join(self.given_names)}"
            else:
                return self.family_name
        else:
            # Default format
            if self.given_names:
                return f"{' '.join(self.given_names)} {self.family_name}"
            else:
                return self.family_name

@dataclass
class BibliographicReference:
    """Comprehensive bibliographic reference."""
    # Core identification
    reference_id: str
    raw_text: str
    parsed_text: str = ""
    
    # Reference metadata
    reference_type: ReferenceType = ReferenceType.UNKNOWN
    citation_style: CitationStyle = CitationStyle.UNKNOWN
    quality: CitationQuality = CitationQuality.FAIR
    
    # Authors and editors
    authors: List[BibliographicAuthor] = field(default_factory=list)
    editors: List[BibliographicAuthor] = field(default_factory=list)
    
    # Publication details
    title: str = ""
    journal: str = ""
    conference: str = ""
    book_title: str = ""
    publisher: str = ""
    year: Optional[int] = None
    month: Optional[str] = None
    volume: str = ""
    issue: str = ""
    pages: str = ""
    
    # Identifiers
    doi: str = ""
    isbn: str = ""
    issn: str = ""
    pmid: str = ""
    arxiv_id: str = ""
    url: str = ""
    
    # Additional metadata
    abstract: str = ""
    keywords: List[str] = field(default_factory=list)
    language: str = "en"
    
    # Quality metrics
    completeness_score: float = 0.0
    accuracy_score: float = 0.0
    confidence_score: float = 0.0
    
    # Processing metadata
    extraction_date: datetime = field(default_factory=datetime.now)
    validation_status: str = "pending"
    cross_references: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Post-process reference data."""
        if not self.parsed_text:
            self.parsed_text = self.raw_text
        
        if not self.reference_id:
            self.reference_id = self._generate_reference_id()
        
        # Calculate quality scores
        self._calculate_quality_scores()
    
    def _generate_reference_id(self) -> str:
        """Generate a unique reference ID."""
        import hashlib
        content = f"{self.title}_{self.year}_{len(self.authors)}"
        return hashlib.md5(content.encode()).hexdigest()[:12]
    
    def _calculate_quality_scores(self):
        """Calculate reference quality scores."""
        # Completeness score
        total_fields = 15
        filled_fields = 0
        
        if self.title: filled_fields += 1
        if self.authors: filled_fields += 1
        if self.year: filled_fields += 1
        if self.journal or self.conference or self.book_title: filled_fields += 1
        if self.volume: filled_fields += 1
        if self.issue: filled_fields += 1
        if self.pages: filled_fields += 1
        if self.doi: filled_fields += 1
        if self.publisher: filled_fields += 1
        if self.url: filled_fields += 1
        if self.isbn or self.issn: filled_fields += 1
        if self.abstract: filled_fields += 1
        if self.language: filled_fields += 1
        if self.month: filled_fields += 1
        if self.keywords: filled_fields += 1
        
        self.completeness_score = filled_fields / total_fields
        
        # Accuracy score (based on format validation)
        accuracy_points = 0
        total_points = 10
        
        if self.doi and self._is_valid_doi(self.doi): accuracy_points += 1
        if self.year and 1900 <= self.year <= datetime.now().year: accuracy_points += 1
        if self.authors and all(author.family_name for author in self.authors): accuracy_points += 1
        if self.title and len(self.title) > 5: accuracy_points += 1
        if self.pages and self._is_valid_page_range(self.pages): accuracy_points += 1
        if self.url and self._is_valid_url(self.url): accuracy_points += 1
        if self.isbn and self._is_valid_isbn(self.isbn): accuracy_points += 1
        if self.issn and self._is_valid_issn(self.issn): accuracy_points += 1
        if self.pmid and self.pmid.isdigit(): accuracy_points += 1
        if self.arxiv_id and self._is_valid_arxiv_id(self.arxiv_id): accuracy_points += 1
        
        self.accuracy_score = accuracy_points / total_points
        
        # Overall confidence score
        self.confidence_score = (self.completeness_score + self.accuracy_score) / 2
        
        # Determine quality level
        if self.confidence_score >= 0.9:
            self.quality = CitationQuality.EXCELLENT
        elif self.confidence_score >= 0.7:
            self.quality = CitationQuality.GOOD
        elif self.confidence_score >= 0.5:
            self.quality = CitationQuality.FAIR
        elif self.confidence_score >= 0.3:
            self.quality = CitationQuality.POOR
        else:
            self.quality = CitationQuality.INCOMPLETE
    
    def _is_valid_doi(self, doi: str) -> bool:
        """Validate DOI format."""
        pattern = r'^10\.\d{4,}/[^\s]+$'
        return bool(re.match(pattern, doi.strip()))
    
    def _is_valid_page_range(self, pages: str) -> bool:
        """Validate page range format."""
        patterns = [
            r'^\d+$',  # Single page
            r'^\d+-\d+$',  # Page range
            r'^\d+–\d+$',  # Page range with en-dash
            r'^pp\.\s*\d+-\d+$',  # With pp. prefix
        ]
        return any(re.match(pattern, pages.strip()) for pattern in patterns)
    
    def _is_valid_url(self, url: str) -> bool:
        """Validate URL format."""
        pattern = r'^https?://[^\s]+$'
        return bool(re.match(pattern, url.strip()))
    
    def _is_valid_isbn(self, isbn: str) -> bool:
        """Validate ISBN format."""
        isbn = re.sub(r'[^\d]', '', isbn)  # Remove non-digits
        return len(isbn) in [10, 13]
    
    def _is_valid_issn(self, issn: str) -> bool:
        """Validate ISSN format."""
        pattern = r'^\d{4}-\d{3}[\dX]$'
        return bool(re.match(pattern, issn.strip()))
    
    def _is_valid_arxiv_id(self, arxiv_id: str) -> bool:
        """Validate arXiv ID format."""
        patterns = [
            r'^\d{4}\.\d{4,5}(v\d+)?$',  # New format
            r'^[a-z-]+/\d{7}(v\d+)?$',  # Old format
        ]
        return any(re.match(pattern, arxiv_id.strip()) for pattern in patterns)
    
    def get_formatted_citation(self, style: CitationStyle) -> str:
        """Get formatted citation in specified style."""
        if style == CitationStyle.APA:
            return self._format_apa()
        elif style == CitationStyle.MLA:
            return self._format_mla()
        elif style == CitationStyle.IEEE:
            return self._format_ieee()
        elif style == CitationStyle.CHICAGO:
            return self._format_chicago()
        else:
            return self.parsed_text
    
    def _format_apa(self) -> str:
        """Format citation in APA style."""
        parts = []
        
        # Authors
        if self.authors:
            if len(self.authors) == 1:
                parts.append(self.authors[0].get_display_name(CitationStyle.APA))
            elif len(self.authors) <= 7:
                author_names = [author.get_display_name(CitationStyle.APA) for author in self.authors[:-1]]
                parts.append(", ".join(author_names) + ", & " + self.authors[-1].get_display_name(CitationStyle.APA))
            else:
                # More than 7 authors
                author_names = [author.get_display_name(CitationStyle.APA) for author in self.authors[:6]]
                parts.append(", ".join(author_names) + ", ... " + self.authors[-1].get_display_name(CitationStyle.APA))
        
        # Year
        if self.year:
            parts.append(f"({self.year})")
        
        # Title
        if self.title:
            parts.append(f"{self.title}.")
        
        # Journal/Conference
        if self.journal:
            journal_part = f"*{self.journal}*"
            if self.volume:
                journal_part += f", {self.volume}"
                if self.issue:
                    journal_part += f"({self.issue})"
            if self.pages:
                journal_part += f", {self.pages}"
            parts.append(journal_part + ".")
        elif self.conference:
            parts.append(f"*{self.conference}*.")
        
        # DOI
        if self.doi:
            parts.append(f"https://doi.org/{self.doi}")
        
        return " ".join(parts)
    
    def _format_mla(self) -> str:
        """Format citation in MLA style."""
        parts = []
        
        # Authors
        if self.authors:
            if len(self.authors) == 1:
                parts.append(self.authors[0].get_display_name(CitationStyle.MLA))
            else:
                parts.append(self.authors[0].get_display_name(CitationStyle.MLA) + ", et al.")
        
        # Title
        if self.title:
            if self.journal or self.conference:
                parts.append(f'"{self.title}."')
            else:
                parts.append(f"*{self.title}*.")
        
        # Journal/Conference
        if self.journal:
            journal_part = f"*{self.journal}*"
            if self.volume:
                journal_part += f", vol. {self.volume}"
                if self.issue:
                    journal_part += f", no. {self.issue}"
            if self.year:
                journal_part += f", {self.year}"
            if self.pages:
                journal_part += f", pp. {self.pages}"
            parts.append(journal_part + ".")
        
        return " ".join(parts)
    
    def _format_ieee(self) -> str:
        """Format citation in IEEE style."""
        parts = []
        
        # Authors
        if self.authors:
            if len(self.authors) <= 3:
                author_names = []
                for author in self.authors:
                    if author.given_names:
                        initials = "".join([name[0] + "." for name in author.given_names])
                        author_names.append(f"{initials} {author.family_name}")
                    else:
                        author_names.append(author.family_name)
                parts.append(", ".join(author_names[:-1]) + ", and " + author_names[-1] if len(author_names) > 1 else author_names[0])
            else:
                first_author = self.authors[0]
                if first_author.given_names:
                    initials = "".join([name[0] + "." for name in first_author.given_names])
                    parts.append(f"{initials} {first_author.family_name} et al.")
                else:
                    parts.append(f"{first_author.family_name} et al.")
        
        # Title
        if self.title:
            parts.append(f'"{self.title},"')
        
        # Journal
        if self.journal:
            journal_part = f"*{self.journal}*"
            if self.volume:
                journal_part += f", vol. {self.volume}"
                if self.issue:
                    journal_part += f", no. {self.issue}"
            if self.pages:
                journal_part += f", pp. {self.pages}"
            if self.year:
                journal_part += f", {self.year}"
            parts.append(journal_part + ".")
        
        return " ".join(parts)
    
    def _format_chicago(self) -> str:
        """Format citation in Chicago style."""
        parts = []
        
        # Authors
        if self.authors:
            if len(self.authors) == 1:
                author = self.authors[0]
                if author.given_names:
                    parts.append(f"{author.family_name}, {' '.join(author.given_names)}")
                else:
                    parts.append(author.family_name)
            else:
                first_author = self.authors[0]
                if first_author.given_names:
                    parts.append(f"{first_author.family_name}, {' '.join(first_author.given_names)}, et al.")
                else:
                    parts.append(f"{first_author.family_name} et al.")
        
        # Title
        if self.title:
            if self.journal:
                parts.append(f'"{self.title}."')
            else:
                parts.append(f"*{self.title}*.")
        
        # Journal
        if self.journal:
            journal_part = f"*{self.journal}*"
            if self.volume:
                journal_part += f" {self.volume}"
                if self.issue:
                    journal_part += f", no. {self.issue}"
            if self.year:
                journal_part += f" ({self.year})"
            if self.pages:
                journal_part += f": {self.pages}"
            parts.append(journal_part + ".")
        
        return " ".join(parts)

@dataclass
class BibliographicDatabase:
    """Database of parsed bibliographic references."""
    references: List[BibliographicReference] = field(default_factory=list)
    citation_network: Dict[str, List[str]] = field(default_factory=dict)
    style_distribution: Dict[CitationStyle, int] = field(default_factory=dict)
    quality_metrics: Dict[str, float] = field(default_factory=dict)
    
    def add_reference(self, reference: BibliographicReference):
        """Add a reference to the database."""
        self.references.append(reference)
        self._update_style_distribution(reference.citation_style)
        self._update_quality_metrics()
    
    def _update_style_distribution(self, style: CitationStyle):
        """Update citation style distribution."""
        if style not in self.style_distribution:
            self.style_distribution[style] = 0
        self.style_distribution[style] += 1
    
    def _update_quality_metrics(self):
        """Update overall quality metrics."""
        if not self.references:
            return
        
        total_completeness = sum(ref.completeness_score for ref in self.references)
        total_accuracy = sum(ref.accuracy_score for ref in self.references)
        total_confidence = sum(ref.confidence_score for ref in self.references)
        
        count = len(self.references)
        self.quality_metrics = {
            "average_completeness": total_completeness / count,
            "average_accuracy": total_accuracy / count,
            "average_confidence": total_confidence / count,
            "total_references": count,
            "excellent_quality": len([ref for ref in self.references if ref.quality == CitationQuality.EXCELLENT]),
            "good_quality": len([ref for ref in self.references if ref.quality == CitationQuality.GOOD]),
            "fair_quality": len([ref for ref in self.references if ref.quality == CitationQuality.FAIR]),
            "poor_quality": len([ref for ref in self.references if ref.quality == CitationQuality.POOR]),
            "incomplete_quality": len([ref for ref in self.references if ref.quality == CitationQuality.INCOMPLETE]),
        }
    
    def get_references_by_style(self, style: CitationStyle) -> List[BibliographicReference]:
        """Get references by citation style."""
        return [ref for ref in self.references if ref.citation_style == style]
    
    def get_references_by_quality(self, quality: CitationQuality) -> List[BibliographicReference]:
        """Get references by quality level."""
        return [ref for ref in self.references if ref.quality == quality]
    
    def get_dominant_citation_style(self) -> CitationStyle:
        """Get the most common citation style."""
        if not self.style_distribution:
            return CitationStyle.UNKNOWN
        
        return max(self.style_distribution.items(), key=lambda x: x[1])[0]

class CitationStyleDetector:
    """Detects citation styles from reference text."""
    
    def __init__(self):
        # Citation style patterns
        self.style_patterns = {
            CitationStyle.APA: [
                r'\([12]\d{3}\)',  # Year in parentheses
                r'[A-Z][a-z]+,\s*[A-Z]\.',  # Last, F.
                r'&\s+[A-Z][a-z]+',  # & Author
                r'doi:\s*10\.',  # DOI format
            ],
            CitationStyle.MLA: [
                r'"[^"]+"\.',  # Title in quotes
                r'\*[^*]+\*',  # Italicized journal
                r'vol\.\s*\d+',  # Volume format
                r'pp\.\s*\d+-\d+',  # Page format
            ],
            CitationStyle.IEEE: [
                r'\[\d+\]',  # Numbered citations
                r'et\s+al\.',  # et al.
                r'vol\.\s*\d+,\s*no\.\s*\d+',  # Volume, number format
                r'pp\.\s*\d+-\d+,\s*[12]\d{3}',  # Pages, year
            ],
            CitationStyle.CHICAGO: [
                r'[A-Z][a-z]+,\s*[A-Z][a-z]+',  # Last, First
                r'\([12]\d{3}\):',  # Year with colon
                r'no\.\s*\d+\s*\([12]\d{3}\)',  # Number (year)
            ],
            CitationStyle.NATURE: [
                r'^[A-Z][a-z]+,\s*[A-Z]\.',  # Author format
                r'Nature\s+\d+',  # Nature journal pattern
                r'\(\d{4}\)',  # Year in parentheses
            ],
            CitationStyle.SCIENCE: [
                r'^[A-Z]\.\s*[A-Z][a-z]+',  # F. Last format
                r'Science\s+\d+',  # Science journal pattern
                r'\(\d{4}\)',  # Year format
            ]
        }
    
    def detect_style(self, reference_text: str) -> CitationStyle:
        """Detect citation style from reference text."""
        scores = {}
        
        for style, patterns in self.style_patterns.items():
            score = 0
            for pattern in patterns:
                matches = len(re.findall(pattern, reference_text, re.IGNORECASE))
                score += matches
            scores[style] = score
        
        # Return style with highest score
        if scores:
            max_score = max(scores.values())
            if max_score > 0:
                return max(scores.items(), key=lambda x: x[1])[0]
        
        return CitationStyle.UNKNOWN

class ReferenceParser:
    """Parses bibliographic references into structured data."""
    
    def __init__(self):
        self.style_detector = CitationStyleDetector()
        
        # Author parsing patterns
        self.author_patterns = [
            r'([A-Z][a-z]+),\s*([A-Z]\.?\s*)+',  # Last, F. M.
            r'([A-Z]\.?\s*)+\s+([A-Z][a-z]+)',  # F. M. Last
            r'([A-Z][a-z]+),\s*([A-Z][a-z]+)',  # Last, First
        ]
        
        # Title patterns
        self.title_patterns = [
            r'"([^"]+)"',  # Title in quotes
            r'([A-Z][^.!?]*[.!?])',  # Sentence case title
        ]
        
        # Journal patterns
        self.journal_patterns = [
            r'\*([^*]+)\*',  # Italicized journal
            r'([A-Z][A-Za-z\s&]+)(?:\s+\d+|\s+vol)',  # Journal before volume
        ]
        
        # Year patterns
        self.year_patterns = [
            r'\(([12]\d{3})\)',  # Year in parentheses
            r'\b([12]\d{3})\b',  # Year standalone
        ]
        
        # DOI pattern
        self.doi_pattern = r'(?:doi:|DOI:)?\s*(10\.\d+/[^\s,]+)'
        
        # Volume/Issue/Pages patterns
        self.volume_pattern = r'(?:vol\.?\s*|volume\s*)(\d+)'
        self.issue_pattern = r'(?:no\.?\s*|issue\s*|number\s*)(\d+)'
        self.pages_pattern = r'(?:pp\.?\s*|pages?\s*)(\d+(?:-|–)\d+|\d+)'
    
    def parse_reference(self, reference_text: str, reference_id: str = None) -> BibliographicReference:
        """Parse a reference into structured data."""
        # Clean the reference text
        cleaned_text = self._clean_reference_text(reference_text)
        
        # Detect citation style
        style = self.style_detector.detect_style(cleaned_text)
        
        # Create reference object
        reference = BibliographicReference(
            reference_id=reference_id or "",
            raw_text=reference_text,
            parsed_text=cleaned_text,
            citation_style=style
        )
        
        # Parse components
        reference.authors = self._parse_authors(cleaned_text)
        reference.title = self._parse_title(cleaned_text)
        reference.journal = self._parse_journal(cleaned_text)
        reference.year = self._parse_year(cleaned_text)
        reference.volume = self._parse_volume(cleaned_text)
        reference.issue = self._parse_issue(cleaned_text)
        reference.pages = self._parse_pages(cleaned_text)
        reference.doi = self._parse_doi(cleaned_text)
        reference.url = self._parse_url(cleaned_text)
        
        # Determine reference type
        reference.reference_type = self._determine_reference_type(reference)
        
        return reference
    
    def _clean_reference_text(self, text: str) -> str:
        """Clean and normalize reference text."""
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text.strip())
        
        # Remove numbered prefixes
        text = re.sub(r'^\d+\.\s*', '', text)
        text = re.sub(r'^\[\d+\]\s*', '', text)
        
        return text
    
    def _parse_authors(self, text: str) -> List[BibliographicAuthor]:
        """Parse authors from reference text."""
        authors = []
        
        # Try different author patterns
        for pattern in self.author_patterns:
            matches = re.finditer(pattern, text)
            for match in matches:
                if len(match.groups()) >= 2:
                    family_name = match.group(1).strip()
                    given_part = match.group(2).strip()
                    
                    # Parse given names/initials
                    given_names = []
                    initials = []
                    
                    if '.' in given_part:
                        # Initials
                        initials = re.findall(r'[A-Z]\.?', given_part)
                    else:
                        # Full given names
                        given_names = given_part.split()
                    
                    author = BibliographicAuthor(
                        family_name=family_name,
                        given_names=given_names,
                        initials=initials
                    )
                    authors.append(author)
        
        # Remove duplicates
        unique_authors = []
        seen_names = set()
        for author in authors:
            if author.normalized_name not in seen_names:
                unique_authors.append(author)
                seen_names.add(author.normalized_name)
        
        return unique_authors[:10]  # Limit to reasonable number
    
    def _parse_title(self, text: str) -> str:
        """Parse title from reference text."""
        for pattern in self.title_patterns:
            match = re.search(pattern, text)
            if match:
                title = match.group(1).strip()
                if len(title) > 10:  # Reasonable title length
                    return title.rstrip('.,')
        
        return ""
    
    def _parse_journal(self, text: str) -> str:
        """Parse journal name from reference text."""
        for pattern in self.journal_patterns:
            match = re.search(pattern, text, re.IGNORECASE)
            if match:
                journal = match.group(1).strip()
                if len(journal) > 3:  # Reasonable journal name length
                    return journal
        
        return ""
    
    def _parse_year(self, text: str) -> Optional[int]:
        """Parse publication year from reference text."""
        for pattern in self.year_patterns:
            match = re.search(pattern, text)
            if match:
                try:
                    year = int(match.group(1))
                    if 1900 <= year <= datetime.now().year:
                        return year
                except ValueError:
                    continue
        
        return None
    
    def _parse_volume(self, text: str) -> str:
        """Parse volume from reference text."""
        match = re.search(self.volume_pattern, text, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _parse_issue(self, text: str) -> str:
        """Parse issue from reference text."""
        match = re.search(self.issue_pattern, text, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _parse_pages(self, text: str) -> str:
        """Parse pages from reference text."""
        match = re.search(self.pages_pattern, text, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _parse_doi(self, text: str) -> str:
        """Parse DOI from reference text."""
        match = re.search(self.doi_pattern, text, re.IGNORECASE)
        return match.group(1) if match else ""
    
    def _parse_url(self, text: str) -> str:
        """Parse URL from reference text."""
        url_pattern = r'https?://[^\s,]+'
        match = re.search(url_pattern, text)
        return match.group(0) if match else ""
    
    def _determine_reference_type(self, reference: BibliographicReference) -> ReferenceType:
        """Determine the type of reference."""
        if reference.journal:
            return ReferenceType.JOURNAL_ARTICLE
        elif reference.conference:
            return ReferenceType.CONFERENCE_PAPER
        elif 'thesis' in reference.title.lower() or 'dissertation' in reference.title.lower():
            return ReferenceType.THESIS
        elif reference.url and not reference.journal:
            return ReferenceType.WEBSITE
        elif reference.arxiv_id:
            return ReferenceType.PREPRINT
        elif 'patent' in reference.title.lower():
            return ReferenceType.PATENT
        else:
            return ReferenceType.UNKNOWN

class BibliographicNormalizer:
    """Normalizes bibliographic data across different styles."""
    
    def __init__(self):
        self.journal_aliases = self._load_journal_aliases()
        self.publisher_aliases = self._load_publisher_aliases()
    
    def _load_journal_aliases(self) -> Dict[str, str]:
        """Load journal name aliases for normalization."""
        return {
            "nature": "Nature",
            "science": "Science",
            "cell": "Cell",
            "pnas": "Proceedings of the National Academy of Sciences",
            "jacs": "Journal of the American Chemical Society",
            "angew chem": "Angewandte Chemie International Edition",
            "phys rev lett": "Physical Review Letters",
            "prl": "Physical Review Letters",
            "ieee trans": "IEEE Transactions",
            "acm trans": "ACM Transactions",
        }
    
    def _load_publisher_aliases(self) -> Dict[str, str]:
        """Load publisher aliases for normalization."""
        return {
            "springer": "Springer",
            "elsevier": "Elsevier",
            "wiley": "Wiley",
            "ieee": "IEEE",
            "acm": "ACM",
            "nature": "Nature Publishing Group",
            "science": "American Association for the Advancement of Science",
        }
    
    def normalize_reference(self, reference: BibliographicReference) -> BibliographicReference:
        """Normalize a bibliographic reference."""
        # Normalize journal name
        if reference.journal:
            normalized_journal = self._normalize_journal_name(reference.journal)
            reference.journal = normalized_journal
        
        # Normalize author names
        for author in reference.authors:
            author.normalized_name = author._normalize_name()
        
        # Normalize title
        if reference.title:
            reference.title = self._normalize_title(reference.title)
        
        # Normalize DOI
        if reference.doi:
            reference.doi = self._normalize_doi(reference.doi)
        
        # Normalize pages
        if reference.pages:
            reference.pages = self._normalize_pages(reference.pages)
        
        return reference
    
    def _normalize_journal_name(self, journal: str) -> str:
        """Normalize journal name."""
        journal_lower = journal.lower().strip()
        
        # Check aliases
        for alias, full_name in self.journal_aliases.items():
            if alias in journal_lower:
                return full_name
        
        # Title case normalization
        return journal.title()
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title formatting."""
        # Remove extra punctuation
        title = title.strip('.,;:')
        
        # Ensure proper sentence case
        if title.isupper():
            title = title.title()
        
        return title
    
    def _normalize_doi(self, doi: str) -> str:
        """Normalize DOI format."""
        # Remove common prefixes
        doi = re.sub(r'^(?:doi:|DOI:)?\s*', '', doi)
        
        # Remove URL prefix if present
        doi = re.sub(r'^https?://(?:dx\.)?doi\.org/', '', doi)
        
        return doi.strip()
    
    def _normalize_pages(self, pages: str) -> str:
        """Normalize page format."""
        # Remove 'pp.' prefix
        pages = re.sub(r'^pp\.?\s*', '', pages)
        
        # Normalize dash types
        pages = re.sub(r'[–—]', '-', pages)
        
        return pages.strip()

class BibliographicParser:
    """Main bibliographic parser class."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.reference_parser = ReferenceParser()
        self.normalizer = BibliographicNormalizer()
        self.database = BibliographicDatabase()
        
        # Reference extraction patterns
        self.reference_section_patterns = [
            r'(?i)references?\s*:?\s*\n(.*?)(?:\n\n|\n[A-Z][a-z]+:|\Z)',
            r'(?i)bibliography\s*:?\s*\n(.*?)(?:\n\n|\n[A-Z][a-z]+:|\Z)',
            r'(?i)works?\s+cited\s*:?\s*\n(.*?)(?:\n\n|\n[A-Z][a-z]+:|\Z)',
            r'(?i)literature\s+cited\s*:?\s*\n(.*?)(?:\n\n|\n[A-Z][a-z]+:|\Z)',
        ]
        
        self.reference_patterns = [
            r'^\d+\.\s*(.+?)(?=\n\d+\.|\n\n|\Z)',  # Numbered references
            r'^\[\d+\]\s*(.+?)(?=\n\[\d+\]|\n\n|\Z)',  # Bracketed numbers
            r'^([A-Z][^.]+\.\s*.+?)(?=\n[A-Z][^.]+\.|\n\n|\Z)',  # Author-year
        ]
    
    def parse_bibliography(self, text: str) -> BibliographicDatabase:
        """Parse bibliography from text and return structured database."""
        logger.info("Starting bibliographic parsing")
        
        # Extract reference sections
        reference_sections = self._extract_reference_sections(text)
        
        # Parse individual references
        all_references = []
        for section in reference_sections:
            references = self._parse_reference_section(section)
            all_references.extend(references)
        
        # Normalize references
        normalized_references = []
        for ref in all_references:
            normalized_ref = self.normalizer.normalize_reference(ref)
            normalized_references.append(normalized_ref)
            self.database.add_reference(normalized_ref)
        
        logger.info(f"Bibliographic parsing completed: {len(normalized_references)} references")
        return self.database
    
    def _extract_reference_sections(self, text: str) -> List[str]:
        """Extract reference sections from text."""
        sections = []
        
        for pattern in self.reference_section_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                section_text = match.group(1).strip()
                if section_text and len(section_text) > 50:  # Reasonable section length
                    sections.append(section_text)
        
        return sections
    
    def _parse_reference_section(self, section_text: str) -> List[BibliographicReference]:
        """Parse individual references from a reference section."""
        references = []
        
        # Try different reference patterns
        for pattern in self.reference_patterns:
            matches = re.finditer(pattern, section_text, re.MULTILINE | re.DOTALL)
            for i, match in enumerate(matches):
                ref_text = match.group(1).strip()
                if len(ref_text) > 20:  # Reasonable reference length
                    ref_id = f"ref_{len(references) + 1:03d}"
                    reference = self.reference_parser.parse_reference(ref_text, ref_id)
                    references.append(reference)
        
        # If no structured patterns found, try line-by-line
        if not references:
            lines = section_text.split('\n')
            for i, line in enumerate(lines):
                line = line.strip()
                if len(line) > 20:  # Reasonable reference length
                    ref_id = f"ref_{i + 1:03d}"
                    reference = self.reference_parser.parse_reference(line, ref_id)
                    references.append(reference)
        
        return references
    
    def export_bibliography(self, format: str = "json") -> str:
        """Export bibliography in specified format."""
        if format.lower() == "json":
            return self._export_json()
        elif format.lower() == "bibtex":
            return self._export_bibtex()
        elif format.lower() == "ris":
            return self._export_ris()
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _export_json(self) -> str:
        """Export bibliography as JSON."""
        data = {
            "metadata": {
                "total_references": len(self.database.references),
                "dominant_style": self.database.get_dominant_citation_style().value,
                "quality_metrics": self.database.quality_metrics,
                "export_date": datetime.now().isoformat()
            },
            "references": []
        }
        
        for ref in self.database.references:
            ref_dict = asdict(ref)
            # Convert enums to strings
            ref_dict["citation_style"] = ref.citation_style.value
            ref_dict["reference_type"] = ref.reference_type.value
            ref_dict["quality"] = ref.quality.value
            ref_dict["extraction_date"] = ref.extraction_date.isoformat()
            data["references"].append(ref_dict)
        
        return json.dumps(data, indent=2, ensure_ascii=False)
    
    def _export_bibtex(self) -> str:
        """Export bibliography as BibTeX."""
        bibtex_entries = []
        
        for ref in self.database.references:
            entry_type = self._get_bibtex_entry_type(ref.reference_type)
            cite_key = self._generate_cite_key(ref)
            
            entry = f"@{entry_type}{{{cite_key},\n"
            
            # Add fields
            if ref.title:
                entry += f"  title = {{{ref.title}}},\n"
            if ref.authors:
                author_str = " and ".join([f"{author.family_name}, {' '.join(author.given_names)}" 
                                         for author in ref.authors])
                entry += f"  author = {{{author_str}}},\n"
            if ref.journal:
                entry += f"  journal = {{{ref.journal}}},\n"
            if ref.year:
                entry += f"  year = {{{ref.year}}},\n"
            if ref.volume:
                entry += f"  volume = {{{ref.volume}}},\n"
            if ref.issue:
                entry += f"  number = {{{ref.issue}}},\n"
            if ref.pages:
                entry += f"  pages = {{{ref.pages}}},\n"
            if ref.doi:
                entry += f"  doi = {{{ref.doi}}},\n"
            if ref.url:
                entry += f"  url = {{{ref.url}}},\n"
            
            entry = entry.rstrip(',\n') + "\n}\n\n"
            bibtex_entries.append(entry)
        
        return "".join(bibtex_entries)
    
    def _export_ris(self) -> str:
        """Export bibliography as RIS format."""
        ris_entries = []
        
        for ref in self.database.references:
            entry = f"TY  - {self._get_ris_type(ref.reference_type)}\n"
            
            if ref.title:
                entry += f"TI  - {ref.title}\n"
            
            for author in ref.authors:
                if author.given_names:
                    entry += f"AU  - {author.family_name}, {' '.join(author.given_names)}\n"
                else:
                    entry += f"AU  - {author.family_name}\n"
            
            if ref.journal:
                entry += f"JO  - {ref.journal}\n"
            if ref.year:
                entry += f"PY  - {ref.year}\n"
            if ref.volume:
                entry += f"VL  - {ref.volume}\n"
            if ref.issue:
                entry += f"IS  - {ref.issue}\n"
            if ref.pages:
                entry += f"SP  - {ref.pages}\n"
            if ref.doi:
                entry += f"DO  - {ref.doi}\n"
            if ref.url:
                entry += f"UR  - {ref.url}\n"
            
            entry += "ER  - \n\n"
            ris_entries.append(entry)
        
        return "".join(ris_entries)
    
    def _get_bibtex_entry_type(self, ref_type: ReferenceType) -> str:
        """Get BibTeX entry type for reference type."""
        mapping = {
            ReferenceType.JOURNAL_ARTICLE: "article",
            ReferenceType.CONFERENCE_PAPER: "inproceedings",
            ReferenceType.BOOK: "book",
            ReferenceType.BOOK_CHAPTER: "incollection",
            ReferenceType.THESIS: "phdthesis",
            ReferenceType.REPORT: "techreport",
            ReferenceType.WEBSITE: "misc",
            ReferenceType.PREPRINT: "misc",
        }
        return mapping.get(ref_type, "misc")
    
    def _get_ris_type(self, ref_type: ReferenceType) -> str:
        """Get RIS type for reference type."""
        mapping = {
            ReferenceType.JOURNAL_ARTICLE: "JOUR",
            ReferenceType.CONFERENCE_PAPER: "CONF",
            ReferenceType.BOOK: "BOOK",
            ReferenceType.BOOK_CHAPTER: "CHAP",
            ReferenceType.THESIS: "THES",
            ReferenceType.REPORT: "RPRT",
            ReferenceType.WEBSITE: "ELEC",
            ReferenceType.PREPRINT: "UNPB",
        }
        return mapping.get(ref_type, "GEN")
    
    def _generate_cite_key(self, ref: BibliographicReference) -> str:
        """Generate citation key for BibTeX."""
        if ref.authors:
            first_author = ref.authors[0].family_name.lower()
        else:
            first_author = "unknown"
        
        year = str(ref.year) if ref.year else "unknown"
        
        # Clean title words
        if ref.title:
            title_words = re.findall(r'\b[A-Za-z]+\b', ref.title.lower())
            title_part = title_words[0] if title_words else "unknown"
        else:
            title_part = "unknown"
        
        return f"{first_author}{year}{title_part}"
    
    def get_parsing_summary(self) -> Dict[str, Any]:
        """Get summary of parsing results."""
        return {
            "total_references": len(self.database.references),
            "citation_styles": {style.value: count for style, count in self.database.style_distribution.items()},
            "dominant_style": self.database.get_dominant_citation_style().value,
            "quality_distribution": {
                "excellent": len(self.database.get_references_by_quality(CitationQuality.EXCELLENT)),
                "good": len(self.database.get_references_by_quality(CitationQuality.GOOD)),
                "fair": len(self.database.get_references_by_quality(CitationQuality.FAIR)),
                "poor": len(self.database.get_references_by_quality(CitationQuality.POOR)),
                "incomplete": len(self.database.get_references_by_quality(CitationQuality.INCOMPLETE)),
            },
            "reference_types": {
                ref_type.value: len([ref for ref in self.database.references if ref.reference_type == ref_type])
                for ref_type in ReferenceType
            },
            "quality_metrics": self.database.quality_metrics,
        }

# Factory functions
def create_bibliographic_parser(config: Optional[Dict[str, Any]] = None) -> BibliographicParser:
    """Create a bibliographic parser with optional configuration."""
    return BibliographicParser(config)

def integrate_with_enhanced_metadata(enhanced_metadata_result: Dict[str, Any], 
                                   config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Integrate bibliographic parsing with enhanced metadata results."""
    logger.info("Integrating bibliographic parsing with enhanced metadata")
    
    try:
        # Create parser
        parser = create_bibliographic_parser(config)
        
        # Get text content
        full_text = enhanced_metadata_result.get("full_text", "")
        
        # Parse bibliography
        bibliography = parser.parse_bibliography(full_text)
        
        # Create integration result
        result = enhanced_metadata_result.copy()
        result["bibliography"] = {
            "references": [asdict(ref) for ref in bibliography.references],
            "summary": parser.get_parsing_summary(),
            "citation_network": bibliography.citation_network,
        }
        
        # Convert enums to strings for JSON serialization
        for ref_dict in result["bibliography"]["references"]:
            ref_dict["citation_style"] = bibliography.references[0].citation_style.value if bibliography.references else "unknown"
            ref_dict["reference_type"] = bibliography.references[0].reference_type.value if bibliography.references else "unknown"
            ref_dict["quality"] = bibliography.references[0].quality.value if bibliography.references else "unknown"
            if "extraction_date" in ref_dict:
                ref_dict["extraction_date"] = ref_dict["extraction_date"].isoformat() if hasattr(ref_dict["extraction_date"], 'isoformat') else str(ref_dict["extraction_date"])
        
        logger.info("Bibliographic parsing integration completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Bibliographic parsing integration failed: {str(e)}")
        # Return original result if enhancement fails
        result = enhanced_metadata_result.copy()
        result["bibliography_error"] = str(e)
        return result 
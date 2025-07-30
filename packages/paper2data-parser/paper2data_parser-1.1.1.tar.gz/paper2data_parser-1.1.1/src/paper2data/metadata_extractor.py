"""
Enhanced Metadata Extraction for Paper2Data

This module provides comprehensive metadata extraction capabilities for academic papers,
including title, authors, abstract, keywords, publication information, DOI, references,
affiliations, and other bibliographic data.
"""

import re
import json
import logging
from typing import Dict, List, Optional, Any, Tuple, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
import fitz  # PyMuPDF

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class PaperType(Enum):
    """Types of academic papers"""
    JOURNAL_ARTICLE = "journal_article"
    CONFERENCE_PAPER = "conference_paper"
    THESIS = "thesis"
    BOOK_CHAPTER = "book_chapter"
    PREPRINT = "preprint"
    TECHNICAL_REPORT = "technical_report"
    UNKNOWN = "unknown"

class PublicationStatus(Enum):
    """Publication status types"""
    PUBLISHED = "published"
    ACCEPTED = "accepted"
    SUBMITTED = "submitted"
    PREPRINT = "preprint"
    DRAFT = "draft"
    UNKNOWN = "unknown"

@dataclass
class Author:
    """Represents an author of a paper"""
    name: str
    affiliations: List[str] = field(default_factory=list)
    orcid: Optional[str] = None
    email: Optional[str] = None
    position: Optional[int] = None
    is_corresponding: bool = False
    
    def __post_init__(self):
        """Clean and validate author data"""
        self.name = self.name.strip()
        self.affiliations = [aff.strip() for aff in self.affiliations if aff.strip()]
        if self.orcid:
            self.orcid = self.orcid.strip()
        if self.email:
            self.email = self.email.strip().lower()

@dataclass
class PublicationInfo:
    """Publication information"""
    journal: Optional[str] = None
    conference: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    year: Optional[int] = None
    month: Optional[str] = None
    publisher: Optional[str] = None
    isbn: Optional[str] = None
    issn: Optional[str] = None
    
    def __post_init__(self):
        """Clean and validate publication info"""
        if self.journal:
            self.journal = self.journal.strip()
        if self.conference:
            self.conference = self.conference.strip()
        if self.publisher:
            self.publisher = self.publisher.strip()

@dataclass
class Citation:
    """Represents a citation/reference"""
    text: str
    authors: List[str] = field(default_factory=list)
    title: Optional[str] = None
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    url: Optional[str] = None
    position: Optional[int] = None
    
    def __post_init__(self):
        """Clean citation data"""
        self.text = self.text.strip()
        self.authors = [author.strip() for author in self.authors if author.strip()]
        if self.title:
            self.title = self.title.strip()
        if self.journal:
            self.journal = self.journal.strip()

@dataclass
class EnhancedMetadata:
    """Comprehensive metadata for academic papers"""
    # Basic information
    title: str
    abstract: str
    authors: List[Author] = field(default_factory=list)
    keywords: List[str] = field(default_factory=list)
    
    # Publication information
    publication_info: PublicationInfo = field(default_factory=PublicationInfo)
    paper_type: PaperType = PaperType.UNKNOWN
    publication_status: PublicationStatus = PublicationStatus.UNKNOWN
    
    # Identifiers
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    pmid: Optional[str] = None
    pmc_id: Optional[str] = None
    
    # Citations and references
    citations: List[Citation] = field(default_factory=list)
    citation_count: int = 0
    
    # Academic categories
    subject_categories: List[str] = field(default_factory=list)
    acm_categories: List[str] = field(default_factory=list)
    
    # Document properties
    page_count: int = 0
    word_count: int = 0
    language: str = "en"
    
    # Timestamps
    created_date: Optional[datetime] = None
    modified_date: Optional[datetime] = None
    extraction_date: datetime = field(default_factory=datetime.now)
    
    # Confidence scores
    title_confidence: float = 0.0
    abstract_confidence: float = 0.0
    author_confidence: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization"""
        data = asdict(self)
        # Convert datetime objects to ISO format strings
        if data.get('created_date'):
            data['created_date'] = data['created_date'].isoformat()
        if data.get('modified_date'):
            data['modified_date'] = data['modified_date'].isoformat()
        if data.get('extraction_date'):
            data['extraction_date'] = data['extraction_date'].isoformat()
        return data

class MetadataExtractor:
    """Enhanced metadata extraction from academic papers"""
    
    def __init__(self):
        """Initialize the metadata extractor"""
        self.title_patterns = [
            r'^(.+?)(?=\n\n|\n[A-Z][a-z]|\nabstract|\nABSTRACT)',
            r'^(.+?)(?=\n\s*\n)',
            r'^(.{10,200}?)(?=\n)',
            r'Title:\s*(.+)',
            r'TITLE:\s*(.+)',
        ]
        
        self.author_patterns = [
            r'(?:Authors?|By):\s*(.+?)(?=\n\n|\nabstract|\nABSTRACT)',
            r'^(.+?)(?=\n(?:Abstract|ABSTRACT))',
            r'([A-Z][a-z]+ [A-Z][a-z]+(?:,\s*[A-Z][a-z]+ [A-Z][a-z]+)*)',
            r'([A-Z]\. [A-Z][a-z]+(?:,\s*[A-Z]\. [A-Z][a-z]+)*)',
        ]
        
        self.abstract_patterns = [
            r'(?:Abstract|ABSTRACT):\s*(.+?)(?=\n\n|\n(?:Keywords|KEYWORDS|Introduction|INTRODUCTION))',
            r'(?:Abstract|ABSTRACT)\s*(.+?)(?=\n\n|\n(?:Keywords|KEYWORDS|Introduction|INTRODUCTION))',
            r'(?:Abstract|ABSTRACT)[:\s]*(.+?)(?=\n(?:[A-Z][a-z]+:|[0-9]+\.))',
        ]
        
        self.keywords_patterns = [
            r'(?:Keywords|KEYWORDS):\s*(.+?)(?=\n\n|\n[A-Z])',
            r'(?:Keywords|KEYWORDS)[:\s]*(.+?)(?=\n\n|\n[A-Z])',
            r'(?:Key words|KEY WORDS):\s*(.+?)(?=\n\n|\n[A-Z])',
        ]
        
        self.doi_patterns = [
            r'(?:DOI|doi):\s*([0-9]{2}\.[0-9]{4}/[^\s]+)',
            r'doi\.org/([0-9]{2}\.[0-9]{4}/[^\s]+)',
            r'(?:DOI|doi):\s*([0-9]{2}\.[0-9]{4}/[^\s,\n]+)',
            r'([0-9]{2}\.[0-9]{4}/[^\s,\n]+)',
        ]
        
        self.arxiv_patterns = [
            r'arXiv:([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?)',
            r'arxiv\.org/abs/([0-9]{4}\.[0-9]{4,5}(?:v[0-9]+)?)',
        ]
        
        self.email_patterns = [
            r'([a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,})',
        ]
        
        self.orcid_patterns = [
            r'ORCID[:\s]*([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X])',
            r'orcid\.org/([0-9]{4}-[0-9]{4}-[0-9]{4}-[0-9]{3}[0-9X])',
        ]
        
        self.journal_patterns = [
            r'(?:Journal|JOURNAL):\s*(.+?)(?=\n|,|\.|;)',
            r'(?:Published in|In):\s*(.+?)(?=\n|,|\.|;)',
            r'([A-Z][a-z]+ (?:Journal|Review|Proceedings|Conference))',
        ]
        
        self.year_patterns = [
            r'(?:19|20)([0-9]{2})',
            r'(?:Copyright|©)\s*(?:19|20)([0-9]{2})',
        ]
        
        self.citation_patterns = [
            r'\[([0-9]+)\]',
            r'\(([0-9]+)\)',
            r'(?:References|REFERENCES)\s*\n(.+?)(?=\n\n|\Z)',
        ]
        
        self.subject_categories = [
            'Computer Science', 'Mathematics', 'Physics', 'Biology', 'Chemistry',
            'Engineering', 'Medicine', 'Economics', 'Psychology', 'Statistics',
            'Machine Learning', 'Artificial Intelligence', 'Data Science',
            'Computational Biology', 'Bioinformatics', 'Quantum Computing',
            'Robotics', 'Natural Language Processing', 'Computer Vision',
            'Cybersecurity', 'Software Engineering', 'Human-Computer Interaction'
        ]
        
    def extract_metadata(self, pdf_path: str) -> EnhancedMetadata:
        """Extract comprehensive metadata from a PDF file"""
        logger.info(f"Extracting metadata from: {pdf_path}")
        
        try:
            # Open PDF document
            doc = fitz.open(pdf_path)
            
            # Extract text from all pages
            full_text = ""
            for page_num in range(len(doc)):
                page = doc[page_num]
                full_text += page.get_text()
            
            # Extract basic document properties
            metadata = EnhancedMetadata(
                title="",
                abstract="",
                page_count=len(doc),
                word_count=len(full_text.split()),
                extraction_date=datetime.now()
            )
            
            # Extract individual components
            metadata.title = self._extract_title(full_text)
            metadata.abstract = self._extract_abstract(full_text)
            metadata.authors = self._extract_authors(full_text)
            metadata.keywords = self._extract_keywords(full_text)
            metadata.doi = self._extract_doi(full_text)
            metadata.arxiv_id = self._extract_arxiv_id(full_text)
            metadata.publication_info = self._extract_publication_info(full_text)
            metadata.citations = self._extract_citations(full_text)
            metadata.subject_categories = self._extract_subject_categories(full_text)
            metadata.paper_type = self._determine_paper_type(full_text, metadata)
            
            # Calculate confidence scores
            metadata.title_confidence = self._calculate_title_confidence(metadata.title)
            metadata.abstract_confidence = self._calculate_abstract_confidence(metadata.abstract)
            metadata.author_confidence = self._calculate_author_confidence(metadata.authors)
            
            # Extract PDF metadata
            pdf_metadata = doc.metadata
            if pdf_metadata:
                if pdf_metadata.get('title') and not metadata.title:
                    metadata.title = pdf_metadata['title']
                if pdf_metadata.get('author') and not metadata.authors:
                    metadata.authors = self._parse_pdf_authors(pdf_metadata['author'])
                if pdf_metadata.get('creationDate'):
                    metadata.created_date = self._parse_pdf_date(pdf_metadata['creationDate'])
                if pdf_metadata.get('modDate'):
                    metadata.modified_date = self._parse_pdf_date(pdf_metadata['modDate'])
            
            doc.close()
            
            logger.info(f"Successfully extracted metadata: {len(metadata.authors)} authors, "
                       f"{len(metadata.keywords)} keywords, {len(metadata.citations)} citations")
            
            return metadata
            
        except Exception as e:
            logger.error(f"Error extracting metadata: {str(e)}")
            return EnhancedMetadata(title="", abstract="", extraction_date=datetime.now())
    
    def _extract_title(self, text: str) -> str:
        """Extract paper title from text"""
        # Clean text first
        lines = text.split('\n')
        clean_lines = [line.strip() for line in lines if line.strip()]
        
        if not clean_lines:
            return ""
        
        # Try patterns in order of preference
        for pattern in self.title_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                title = matches[0].strip()
                if len(title) > 10 and len(title) < 200:
                    return self._clean_title(title)
        
        # Fallback: use first non-empty line if it looks like a title
        first_line = clean_lines[0]
        if len(first_line) > 10 and len(first_line) < 200 and not first_line.lower().startswith(('page', 'abstract', 'introduction')):
            return self._clean_title(first_line)
        
        return ""
    
    def _clean_title(self, title: str) -> str:
        """Clean and normalize title text"""
        # Remove extra whitespace
        title = re.sub(r'\s+', ' ', title)
        # Remove trailing punctuation except periods
        title = re.sub(r'[,;:]+$', '', title)
        # Remove leading/trailing quotes
        title = title.strip('"\'')
        return title.strip()
    
    def _extract_abstract(self, text: str) -> str:
        """Extract abstract from text"""
        for pattern in self.abstract_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                abstract = matches[0].strip()
                if len(abstract) > 50 and len(abstract) < 2000:
                    return self._clean_abstract(abstract)
        
        return ""
    
    def _clean_abstract(self, abstract: str) -> str:
        """Clean and normalize abstract text"""
        # Remove extra whitespace
        abstract = re.sub(r'\s+', ' ', abstract)
        # Remove line breaks within sentences
        abstract = re.sub(r'(?<=[a-z])\n(?=[a-z])', ' ', abstract)
        return abstract.strip()
    
    def _extract_authors(self, text: str) -> List[Author]:
        """Extract authors from text"""
        authors = []
        
        # Try to find author section
        for pattern in self.author_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                author_text = matches[0].strip()
                authors = self._parse_authors(author_text)
                if authors:
                    break
        
        # Extract additional info
        for author in authors:
            author.email = self._find_author_email(text, author.name)
            author.orcid = self._find_author_orcid(text, author.name)
            author.affiliations = self._find_author_affiliations(text, author.name)
        
        return authors
    
    def _parse_authors(self, author_text: str) -> List[Author]:
        """Parse author names from text"""
        authors = []
        
        # Split by common delimiters
        parts = re.split(r'[,;]\s*(?=and\s+|&\s+|[A-Z])', author_text)
        
        for i, part in enumerate(parts):
            part = part.strip()
            if not part:
                continue
            
            # Remove common prefixes/suffixes
            part = re.sub(r'^(?:and\s+|&\s+)', '', part, flags=re.IGNORECASE)
            part = re.sub(r'(?:\s+et\s+al\.?|\s+and\s+others)$', '', part, flags=re.IGNORECASE)
            
            # Extract name
            name_match = re.search(r'([A-Z][a-z]+(?:\s+[A-Z]\.?)?\s+[A-Z][a-z]+)', part)
            if name_match:
                name = name_match.group(1).strip()
                authors.append(Author(name=name, position=i+1))
        
        return authors
    
    def _find_author_email(self, text: str, author_name: str) -> Optional[str]:
        """Find email for a specific author"""
        # Look for email near author name
        author_context = self._get_context_around_name(text, author_name)
        if author_context:
            for pattern in self.email_patterns:
                matches = re.findall(pattern, author_context, re.IGNORECASE)
                if matches:
                    return matches[0]
        return None
    
    def _find_author_orcid(self, text: str, author_name: str) -> Optional[str]:
        """Find ORCID for a specific author"""
        author_context = self._get_context_around_name(text, author_name)
        if author_context:
            for pattern in self.orcid_patterns:
                matches = re.findall(pattern, author_context, re.IGNORECASE)
                if matches:
                    return matches[0]
        return None
    
    def _find_author_affiliations(self, text: str, author_name: str) -> List[str]:
        """Find affiliations for a specific author"""
        affiliations = []
        author_context = self._get_context_around_name(text, author_name)
        if author_context:
            # Look for common affiliation patterns
            affiliation_patterns = [
                r'([A-Z][a-z]+ University)',
                r'([A-Z][a-z]+ Institute)',
                r'([A-Z][a-z]+ Laboratory)',
                r'([A-Z][a-z]+ College)',
                r'([A-Z][a-z]+ Research Center)',
            ]
            
            for pattern in affiliation_patterns:
                matches = re.findall(pattern, author_context)
                affiliations.extend(matches)
        
        return list(set(affiliations))  # Remove duplicates
    
    def _get_context_around_name(self, text: str, name: str, window: int = 200) -> str:
        """Get text context around a name"""
        name_pos = text.find(name)
        if name_pos == -1:
            return ""
        
        start = max(0, name_pos - window)
        end = min(len(text), name_pos + len(name) + window)
        return text[start:end]
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text"""
        keywords = []
        
        for pattern in self.keywords_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE | re.DOTALL)
            if matches:
                keyword_text = matches[0].strip()
                # Split by common delimiters
                parts = re.split(r'[,;]\s*', keyword_text)
                keywords = [part.strip() for part in parts if part.strip()]
                break
        
        return keywords
    
    def _extract_doi(self, text: str) -> Optional[str]:
        """Extract DOI from text"""
        for pattern in self.doi_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        return None
    
    def _extract_arxiv_id(self, text: str) -> Optional[str]:
        """Extract arXiv ID from text"""
        for pattern in self.arxiv_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                return matches[0]
        return None
    
    def _extract_publication_info(self, text: str) -> PublicationInfo:
        """Extract publication information"""
        pub_info = PublicationInfo()
        
        # Extract journal
        for pattern in self.journal_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                pub_info.journal = matches[0].strip()
                break
        
        # Extract year
        for pattern in self.year_patterns:
            matches = re.findall(pattern, text)
            if matches:
                try:
                    pub_info.year = int("20" + matches[0] if len(matches[0]) == 2 else matches[0])
                    break
                except ValueError:
                    continue
        
        return pub_info
    
    def _extract_citations(self, text: str) -> List[Citation]:
        """Extract citations from references section"""
        citations = []
        
        # Find references section
        ref_match = re.search(r'(?:References|REFERENCES|Bibliography|BIBLIOGRAPHY)\s*\n(.+?)(?=\n\n|\Z)', text, re.DOTALL | re.IGNORECASE)
        if ref_match:
            ref_text = ref_match.group(1)
            
            # Split into individual citations
            citation_lines = re.split(r'\n(?=\[?\d+\]?\.?\s)', ref_text)
            
            for i, line in enumerate(citation_lines):
                if line.strip():
                    citation = self._parse_citation(line.strip(), i+1)
                    if citation:
                        citations.append(citation)
        
        return citations
    
    def _parse_citation(self, text: str, position: int) -> Optional[Citation]:
        """Parse a single citation"""
        if len(text) < 20:  # Too short to be a valid citation
            return None
        
        citation = Citation(text=text, position=position)
        
        # Extract authors
        author_match = re.search(r'^([A-Z][a-z]+(?:,\s*[A-Z]\.?)*(?:,\s*[A-Z][a-z]+)*)', text)
        if author_match:
            author_text = author_match.group(1)
            citation.authors = [name.strip() for name in author_text.split(',')]
        
        # Extract title (usually in quotes)
        title_match = re.search(r'["\'](.+?)["\']', text)
        if title_match:
            citation.title = title_match.group(1)
        
        # Extract year
        year_match = re.search(r'\((\d{4})\)', text)
        if year_match:
            citation.year = int(year_match.group(1))
        
        # Extract DOI
        doi_match = re.search(r'doi:?\s*([0-9]{2}\.[0-9]{4}/[^\s,]+)', text, re.IGNORECASE)
        if doi_match:
            citation.doi = doi_match.group(1)
        
        return citation
    
    def _extract_subject_categories(self, text: str) -> List[str]:
        """Extract subject categories based on content"""
        categories = []
        text_lower = text.lower()
        
        for category in self.subject_categories:
            if category.lower() in text_lower:
                categories.append(category)
        
        return categories
    
    def _determine_paper_type(self, text: str, metadata: EnhancedMetadata) -> PaperType:
        """Determine the type of paper"""
        text_lower = text.lower()
        
        if 'conference' in text_lower or 'proceedings' in text_lower:
            return PaperType.CONFERENCE_PAPER
        elif 'journal' in text_lower or metadata.publication_info.journal:
            return PaperType.JOURNAL_ARTICLE
        elif 'thesis' in text_lower or 'dissertation' in text_lower:
            return PaperType.THESIS
        elif 'arxiv' in text_lower or metadata.arxiv_id:
            return PaperType.PREPRINT
        elif 'technical report' in text_lower or 'tech report' in text_lower:
            return PaperType.TECHNICAL_REPORT
        elif 'chapter' in text_lower:
            return PaperType.BOOK_CHAPTER
        else:
            return PaperType.UNKNOWN
    
    def _calculate_title_confidence(self, title: str) -> float:
        """Calculate confidence score for title extraction"""
        if not title:
            return 0.0
        
        score = 0.0
        
        # Length check
        if 10 <= len(title) <= 200:
            score += 0.3
        
        # Capitalization check
        if title[0].isupper():
            score += 0.2
        
        # No weird characters
        if not re.search(r'[^\w\s\-:,\.\(\)\'"]', title):
            score += 0.2
        
        # Reasonable word count
        word_count = len(title.split())
        if 3 <= word_count <= 20:
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_abstract_confidence(self, abstract: str) -> float:
        """Calculate confidence score for abstract extraction"""
        if not abstract:
            return 0.0
        
        score = 0.0
        
        # Length check
        if 50 <= len(abstract) <= 2000:
            score += 0.4
        
        # Sentence structure
        sentence_count = len(re.findall(r'[.!?]+', abstract))
        if sentence_count >= 3:
            score += 0.3
        
        # No weird formatting
        if not re.search(r'[^\w\s\-:,\.\(\)\'"\[\]%]', abstract):
            score += 0.3
        
        return min(score, 1.0)
    
    def _calculate_author_confidence(self, authors: List[Author]) -> float:
        """Calculate confidence score for author extraction"""
        if not authors:
            return 0.0
        
        score = 0.0
        
        # Reasonable number of authors
        if 1 <= len(authors) <= 20:
            score += 0.4
        
        # Names look reasonable
        valid_names = sum(1 for author in authors if len(author.name.split()) >= 2)
        if valid_names == len(authors):
            score += 0.3
        
        # Additional info available
        authors_with_info = sum(1 for author in authors if author.email or author.orcid or author.affiliations)
        if authors_with_info > 0:
            score += 0.3
        
        return min(score, 1.0)
    
    def _parse_pdf_authors(self, author_string: str) -> List[Author]:
        """Parse authors from PDF metadata"""
        authors = []
        if author_string:
            # Split by common delimiters
            names = re.split(r'[,;]\s*', author_string)
            for i, name in enumerate(names):
                if name.strip():
                    authors.append(Author(name=name.strip(), position=i+1))
        return authors
    
    def _parse_pdf_date(self, date_string: str) -> Optional[datetime]:
        """Parse date from PDF metadata"""
        try:
            # PDF date format: D:YYYYMMDDHHmmSSOHH'mm'
            if date_string.startswith('D:'):
                date_string = date_string[2:]
            
            # Extract year, month, day
            if len(date_string) >= 8:
                year = int(date_string[:4])
                month = int(date_string[4:6])
                day = int(date_string[6:8])
                return datetime(year, month, day)
        except (ValueError, IndexError):
            pass
        
        return None

# Global instance for easy access
metadata_extractor = MetadataExtractor()

def extract_metadata(pdf_path: str) -> EnhancedMetadata:
    """Extract metadata from a PDF file using the global instance"""
    return metadata_extractor.extract_metadata(pdf_path)

def export_metadata(metadata: EnhancedMetadata, output_path: str, format: str = 'json') -> bool:
    """Export metadata to file"""
    try:
        if format.lower() == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(metadata.to_dict(), f, indent=2, ensure_ascii=False)
        else:
            raise ValueError(f"Unsupported format: {format}")
        
        logger.info(f"Metadata exported to: {output_path}")
        return True
    except Exception as e:
        logger.error(f"Error exporting metadata: {str(e)}")
        return False 
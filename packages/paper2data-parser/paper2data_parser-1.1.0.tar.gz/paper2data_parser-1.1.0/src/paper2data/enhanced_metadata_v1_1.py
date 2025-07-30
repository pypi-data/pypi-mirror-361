"""
Enhanced Metadata Extraction for Paper2Data Version 1.1

This module provides advanced metadata extraction capabilities including:
- Author disambiguation and normalization
- Institution detection and affiliation mapping
- Funding information extraction
- Enhanced bibliographic metadata processing
- Cross-reference with external databases
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

from .utils import get_logger, clean_text, ProcessingError

logger = get_logger(__name__)

class AuthorNameFormat(Enum):
    """Enumeration of author name formats."""
    FIRST_LAST = "first_last"
    LAST_FIRST = "last_first"
    LAST_COMMA_FIRST = "last_comma_first"
    INITIALS_LAST = "initials_last"
    UNKNOWN = "unknown"

class InstitutionType(Enum):
    """Enumeration of institution types."""
    UNIVERSITY = "university"
    RESEARCH_INSTITUTE = "research_institute"
    COMPANY = "company"
    GOVERNMENT = "government"
    HOSPITAL = "hospital"
    NON_PROFIT = "non_profit"
    UNKNOWN = "unknown"

class FundingSourceType(Enum):
    """Enumeration of funding source types."""
    GOVERNMENT = "government"
    FOUNDATION = "foundation"
    INDUSTRY = "industry"
    UNIVERSITY = "university"
    INTERNATIONAL = "international"
    UNKNOWN = "unknown"

@dataclass
class AuthorIdentifier:
    """Represents author identifiers from external systems."""
    orcid: Optional[str] = None
    scopus_id: Optional[str] = None
    google_scholar_id: Optional[str] = None
    researchgate_id: Optional[str] = None
    semantic_scholar_id: Optional[str] = None
    confidence: float = 0.0
    
    def __post_init__(self):
        """Validate identifiers."""
        if self.orcid and not self._is_valid_orcid(self.orcid):
            self.orcid = None
        
    def _is_valid_orcid(self, orcid: str) -> bool:
        """Validate ORCID format."""
        # ORCID format: 0000-0000-0000-000X
        pattern = r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$'
        return bool(re.match(pattern, orcid))

@dataclass
class Institution:
    """Represents an academic or research institution."""
    name: str
    normalized_name: str
    type: InstitutionType
    country: Optional[str] = None
    city: Optional[str] = None
    department: Optional[str] = None
    ror_id: Optional[str] = None  # Research Organization Registry ID
    grid_id: Optional[str] = None  # Global Research Identifier Database ID
    confidence: float = 0.0
    aliases: List[str] = field(default_factory=list)
    
    def __post_init__(self):
        """Normalize institution name."""
        if not self.normalized_name:
            self.normalized_name = self._normalize_name(self.name)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize institution name for comparison."""
        # Remove common prefixes/suffixes
        name = re.sub(r'\b(University of|College of|Institute of|School of)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b(University|College|Institute|School|Lab|Laboratory)\b', '', name, flags=re.IGNORECASE)
        
        # Remove punctuation and normalize spaces
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip().lower()
        
        return name

@dataclass
class EnhancedAuthor:
    """Represents an author with enhanced metadata."""
    name: str
    normalized_name: str
    name_format: AuthorNameFormat
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    middle_names: List[str] = field(default_factory=list)
    initials: Optional[str] = None
    email: Optional[str] = None
    affiliations: List[Institution] = field(default_factory=list)
    identifiers: AuthorIdentifier = field(default_factory=AuthorIdentifier)
    is_corresponding: bool = False
    position_in_paper: int = 0
    confidence: float = 0.0
    
    def __post_init__(self):
        """Post-process author information."""
        if not self.normalized_name:
            self.normalized_name = self._normalize_name(self.name)
        
        if not self.first_name or not self.last_name:
            self._parse_name()
    
    def _normalize_name(self, name: str) -> str:
        """Normalize author name for comparison."""
        # Remove titles and suffixes
        name = re.sub(r'\b(Dr|Prof|Professor|PhD|Ph\.D|MD|M\.D)\b\.?', '', name, flags=re.IGNORECASE)
        name = re.sub(r'\b(Jr|Sr|III|IV|V)\b\.?', '', name, flags=re.IGNORECASE)
        
        # Normalize spaces and case
        name = re.sub(r'\s+', ' ', name).strip().lower()
        return name
    
    def _parse_name(self):
        """Parse author name into components."""
        name = self.name.strip()
        
        # Check for "Last, First" format
        if ',' in name:
            parts = name.split(',')
            self.last_name = parts[0].strip()
            rest = parts[1].strip()
            if rest:
                name_parts = rest.split()
                self.first_name = name_parts[0]
                self.middle_names = name_parts[1:]
            self.name_format = AuthorNameFormat.LAST_COMMA_FIRST
        else:
            # "First Last" or "F. Last" format
            parts = name.split()
            if len(parts) >= 2:
                if '.' in parts[0]:  # Initials format
                    self.initials = parts[0]
                    self.last_name = ' '.join(parts[1:])
                    self.name_format = AuthorNameFormat.INITIALS_LAST
                else:  # First Last format
                    self.first_name = parts[0]
                    self.last_name = parts[-1]
                    self.middle_names = parts[1:-1]
                    self.name_format = AuthorNameFormat.FIRST_LAST
            else:
                self.name_format = AuthorNameFormat.UNKNOWN

@dataclass
class FundingSource:
    """Represents a funding source."""
    name: str
    normalized_name: str
    type: FundingSourceType
    country: Optional[str] = None
    grant_number: Optional[str] = None
    award_id: Optional[str] = None
    amount: Optional[str] = None
    confidence: float = 0.0
    
    def __post_init__(self):
        """Normalize funding source name."""
        if not self.normalized_name:
            self.normalized_name = self._normalize_name(self.name)
    
    def _normalize_name(self, name: str) -> str:
        """Normalize funding source name."""
        # Remove common patterns
        name = re.sub(r'\b(Foundation|Fund|Agency|Council|Institute|Organization)\b', '', name, flags=re.IGNORECASE)
        name = re.sub(r'[^\w\s]', '', name)
        name = re.sub(r'\s+', ' ', name).strip().lower()
        return name

@dataclass
class EnhancedMetadata:
    """Comprehensive metadata for academic papers."""
    # Basic metadata
    title: str
    normalized_title: str
    authors: List[EnhancedAuthor] = field(default_factory=list)
    
    # Publication information
    journal: Optional[str] = None
    conference: Optional[str] = None
    volume: Optional[str] = None
    issue: Optional[str] = None
    pages: Optional[str] = None
    year: Optional[int] = None
    publication_date: Optional[str] = None
    
    # Identifiers
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    pmid: Optional[str] = None
    isbn: Optional[str] = None
    
    # Subject classification
    keywords: List[str] = field(default_factory=list)
    subjects: List[str] = field(default_factory=list)
    categories: List[str] = field(default_factory=list)
    
    # Funding information
    funding_sources: List[FundingSource] = field(default_factory=list)
    
    # Abstract and summary
    abstract: Optional[str] = None
    summary: Optional[str] = None
    
    # Technical metadata
    language: str = "en"
    page_count: int = 0
    word_count: int = 0
    
    # Quality metrics
    extraction_confidence: float = 0.0
    completeness_score: float = 0.0
    
    def __post_init__(self):
        """Post-process metadata."""
        if not self.normalized_title:
            self.normalized_title = self._normalize_title(self.title)
    
    def _normalize_title(self, title: str) -> str:
        """Normalize title for comparison."""
        # Remove common patterns and normalize
        title = re.sub(r'[^\w\s]', ' ', title)
        title = re.sub(r'\s+', ' ', title).strip().lower()
        return title

class InstitutionDatabase:
    """Database of known institutions for normalization."""
    
    def __init__(self):
        self.institutions: Dict[str, Institution] = {}
        self.aliases: Dict[str, str] = {}
        self._load_common_institutions()
    
    def _load_common_institutions(self):
        """Load common institution names and aliases."""
        common_institutions = [
            ("MIT", "Massachusetts Institute of Technology", InstitutionType.UNIVERSITY, "US"),
            ("Stanford", "Stanford University", InstitutionType.UNIVERSITY, "US"),
            ("Harvard", "Harvard University", InstitutionType.UNIVERSITY, "US"),
            ("Cambridge", "University of Cambridge", InstitutionType.UNIVERSITY, "UK"),
            ("Oxford", "University of Oxford", InstitutionType.UNIVERSITY, "UK"),
            ("UC Berkeley", "University of California, Berkeley", InstitutionType.UNIVERSITY, "US"),
            ("CMU", "Carnegie Mellon University", InstitutionType.UNIVERSITY, "US"),
            ("Google", "Google Inc.", InstitutionType.COMPANY, "US"),
            ("Microsoft", "Microsoft Corporation", InstitutionType.COMPANY, "US"),
            ("IBM", "International Business Machines Corporation", InstitutionType.COMPANY, "US"),
            ("CERN", "European Organization for Nuclear Research", InstitutionType.RESEARCH_INSTITUTE, "CH"),
            ("NIH", "National Institutes of Health", InstitutionType.GOVERNMENT, "US"),
            ("NSF", "National Science Foundation", InstitutionType.GOVERNMENT, "US"),
        ]
        
        for alias, full_name, inst_type, country in common_institutions:
            inst = Institution(
                name=full_name,
                normalized_name=full_name.lower(),
                type=inst_type,
                country=country,
                confidence=0.9
            )
            self.institutions[full_name.lower()] = inst
            self.aliases[alias.lower()] = full_name.lower()
    
    def normalize_institution(self, name: str) -> Optional[Institution]:
        """Normalize institution name using database."""
        name_lower = name.lower()
        
        # Direct match
        if name_lower in self.institutions:
            return self.institutions[name_lower]
        
        # Alias match
        if name_lower in self.aliases:
            return self.institutions[self.aliases[name_lower]]
        
        # Fuzzy matching
        for known_name, institution in self.institutions.items():
            if self._fuzzy_match(name_lower, known_name):
                return institution
        
        return None
    
    def _fuzzy_match(self, name1: str, name2: str, threshold: float = 0.8) -> bool:
        """Simple fuzzy matching for institution names."""
        # Simple Jaccard similarity
        words1 = set(name1.split())
        words2 = set(name2.split())
        
        if not words1 or not words2:
            return False
        
        intersection = words1 & words2
        union = words1 | words2
        
        similarity = len(intersection) / len(union)
        return similarity >= threshold

class FundingDatabase:
    """Database of known funding sources."""
    
    def __init__(self):
        self.funding_sources: Dict[str, FundingSource] = {}
        self._load_common_funding_sources()
    
    def _load_common_funding_sources(self):
        """Load common funding source names."""
        common_sources = [
            ("NSF", "National Science Foundation", FundingSourceType.GOVERNMENT, "US"),
            ("NIH", "National Institutes of Health", FundingSourceType.GOVERNMENT, "US"),
            ("NASA", "National Aeronautics and Space Administration", FundingSourceType.GOVERNMENT, "US"),
            ("DOE", "Department of Energy", FundingSourceType.GOVERNMENT, "US"),
            ("Gates Foundation", "Bill & Melinda Gates Foundation", FundingSourceType.FOUNDATION, "US"),
            ("Ford Foundation", "Ford Foundation", FundingSourceType.FOUNDATION, "US"),
            ("Sloan Foundation", "Alfred P. Sloan Foundation", FundingSourceType.FOUNDATION, "US"),
            ("ERC", "European Research Council", FundingSourceType.INTERNATIONAL, "EU"),
            ("Marie Curie", "Marie Skłodowska-Curie Actions", FundingSourceType.INTERNATIONAL, "EU"),
            ("Horizon 2020", "Horizon 2020", FundingSourceType.INTERNATIONAL, "EU"),
            ("DARPA", "Defense Advanced Research Projects Agency", FundingSourceType.GOVERNMENT, "US"),
            ("ONR", "Office of Naval Research", FundingSourceType.GOVERNMENT, "US"),
            ("AFOSR", "Air Force Office of Scientific Research", FundingSourceType.GOVERNMENT, "US"),
        ]
        
        for alias, full_name, source_type, country in common_sources:
            source = FundingSource(
                name=full_name,
                normalized_name=full_name.lower(),
                type=source_type,
                country=country,
                confidence=0.9
            )
            self.funding_sources[full_name.lower()] = source

class EnhancedMetadataExtractor:
    """Main class for enhanced metadata extraction."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.institution_db = InstitutionDatabase()
        self.funding_db = FundingDatabase()
        
        # Improved extraction patterns
        self.author_patterns = [
            r'(?:Authors?|By):\s*(.+?)(?:\n\s*\n|\nabstract|\nABSTRACT|$)',
            r'(?:^|\n)([A-Z][a-z]+ [A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+ [A-Z][a-z]+)*)\s*(?:\n|$)',
            r'(?:^|\n)([A-Z]\.\s*[A-Z][a-z]+(?:\s*,\s*[A-Z]\.\s*[A-Z][a-z]+)*)\s*(?:\n|$)',
        ]
        
        self.institution_patterns = [
            r'\b((?:University of|College of|Institute of|School of)\s+[A-Z][a-zA-Z\s]{3,30})\b',
            r'\b([A-Z][a-zA-Z\s]{3,30})\s+(?:University|College|Institute|School)\b',
            r'\b(?:Department of|Dept\.?\s+of)\s+([A-Z][a-zA-Z\s]{3,30})\b',
            r'\b([A-Z][a-zA-Z\s]{3,30})\s+(?:Research|Laboratory|Lab|Center)\b',
        ]
        
        self.funding_patterns = [
            r'(?:funded|supported|grant|award)\s+(?:by|from|under)\s+([A-Z][a-zA-Z\s,]+?)(?:\s+grant|\s+award|\s+contract|\.|$)',
            r'(?:Grant|Award|Contract)\s+(?:Number|No\.?|#)\s*([A-Z0-9-]+)',
            r'(?:NSF|NIH|NASA|DOE|DARPA|ONR|AFOSR)\s+(?:Grant|Award|Contract)?\s*(?:Number|No\.?|#)?\s*([A-Z0-9-]+)',
        ]
        
        self.email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        
    def extract_metadata(self, text: str, existing_metadata: Optional[Dict[str, Any]] = None) -> EnhancedMetadata:
        """Extract enhanced metadata from paper text."""
        logger.info("Starting enhanced metadata extraction")
        
        # Initialize with existing metadata if available
        metadata = self._initialize_metadata(existing_metadata)
        
        # Extract authors with enhanced processing
        authors = self._extract_authors(text)
        metadata.authors = authors
        
        # Extract funding information
        funding_sources = self._extract_funding_sources(text)
        metadata.funding_sources = funding_sources
        
        # Extract additional metadata
        metadata.abstract = self._extract_abstract(text)
        metadata.keywords = self._extract_keywords(text)
        metadata.subjects = self._extract_subjects(text)
        
        # Calculate quality metrics
        metadata.extraction_confidence = self._calculate_confidence(metadata)
        metadata.completeness_score = self._calculate_completeness(metadata)
        
        # Word count
        metadata.word_count = len(text.split())
        
        logger.info(f"Enhanced metadata extraction completed: {len(authors)} authors, {len(funding_sources)} funding sources")
        return metadata
    
    def _initialize_metadata(self, existing_metadata: Optional[Dict[str, Any]]) -> EnhancedMetadata:
        """Initialize metadata structure with existing data."""
        if not existing_metadata:
            return EnhancedMetadata(title="", normalized_title="")
        
        # Extract basic information
        title = existing_metadata.get("title", "")
        
        metadata = EnhancedMetadata(
            title=title,
            normalized_title="",
            journal=existing_metadata.get("journal"),
            year=existing_metadata.get("year"),
            doi=existing_metadata.get("doi"),
            arxiv_id=existing_metadata.get("arxiv_id"),
            page_count=existing_metadata.get("page_count", 0),
            publication_date=existing_metadata.get("publication_date"),
            volume=existing_metadata.get("volume"),
            issue=existing_metadata.get("issue"),
            pages=existing_metadata.get("pages"),
        )
        
        # Process basic author information if available
        if "author" in existing_metadata and existing_metadata["author"]:
            basic_authors = existing_metadata["author"].split(";")
            for i, author_name in enumerate(basic_authors):
                author_name = author_name.strip()
                if author_name:
                    enhanced_author = EnhancedAuthor(
                        name=author_name,
                        normalized_name="",
                        name_format=AuthorNameFormat.UNKNOWN,
                        position_in_paper=i,
                        confidence=0.7
                    )
                    metadata.authors.append(enhanced_author)
        
        return metadata
    
    def _extract_authors(self, text: str) -> List[EnhancedAuthor]:
        """Extract and enhance author information."""
        authors = []
        
        # Try multiple extraction methods
        author_strings = self._find_author_strings(text)
        
        for i, author_str in enumerate(author_strings):
            parsed_authors = self._process_author_string(author_str, i)
            authors.extend(parsed_authors)
        
        # Enhance with institutions and additional information
        for author in authors:
            self._enhance_author_with_institutions(author, text)
            self._enhance_author_with_contact_info(author, text)
        
        return authors
    
    def _find_author_strings(self, text: str) -> List[str]:
        """Find author strings in the text using multiple patterns."""
        author_strings = set()
        
        # Look for explicit author sections first
        author_sections = [
            r'(?i)authors?\s*:\s*([^\n]+?)(?:\n\s*\n|\nabstract|\nABSTRACT|$)',
            r'(?i)by\s+([^\n]+?)(?:\n\s*\n|\nabstract|\nABSTRACT|$)',
        ]
        
        for pattern in author_sections:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                author_text = match.group(1).strip()
                if author_text and 10 <= len(author_text) <= 200:  # Reasonable author section length
                    author_strings.add(author_text)
        
        # If no explicit sections found, look for author patterns in first few lines
        if not author_strings:
            lines = text.split('\n')[:10]  # First 10 lines
            for line in lines:
                line = line.strip()
                # Look for lines with multiple names
                if self._looks_like_author_line(line):
                    author_strings.add(line)
        
        return list(author_strings)
    
    def _looks_like_author_line(self, line: str) -> bool:
        """Check if a line looks like it contains author names."""
        if not line or len(line) < 5 or len(line) > 150:
            return False
        
        # Skip lines that are clearly not authors
        skip_words = ['abstract', 'introduction', 'conclusion', 'keywords', 'email', 'university', 'institute', 'department', 'school', 'college']
        if any(word in line.lower() for word in skip_words):
            return False
        
        # Look for author name patterns
        author_patterns = [
            r'[A-Z][a-z]+ [A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+ [A-Z][a-z]+)+',  # Multiple "First Last" names
            r'[A-Z][a-z]+,\s*[A-Z][a-z]+(?:\s*,\s*[A-Z][a-z]+,\s*[A-Z][a-z]+)+',  # Multiple "Last, First" names
            r'[A-Z]\.\s*[A-Z][a-z]+(?:\s*,\s*[A-Z]\.\s*[A-Z][a-z]+)+',  # Multiple "F. Last" names
        ]
        
        for pattern in author_patterns:
            if re.search(pattern, line):
                return True
        
        return False
    
    def _process_author_string(self, author_str: str, position: int) -> List[EnhancedAuthor]:
        """Process a single author string into EnhancedAuthor objects."""
        author_str = author_str.strip()
        if not author_str or len(author_str) < 2:
            return []
        
        # Remove common prefixes/suffixes
        author_str = re.sub(r'^(?:by|author|authors):\s*', '', author_str, flags=re.IGNORECASE)
        author_str = re.sub(r'\s*\([^)]+\)\s*$', '', author_str)  # Remove trailing affiliations
        
        # Split authors by commas or 'and'
        author_parts = re.split(r',\s*(?=and\s+|[A-Z])|,\s*and\s+|\s+and\s+', author_str)
        
        authors = []
        for i, part in enumerate(author_parts):
            part = part.strip()
            if part and len(part) > 2:
                # Check if this looks like a name
                if self._looks_like_single_name(part):
                    author = EnhancedAuthor(
                        name=part,
                        normalized_name="",
                        name_format=AuthorNameFormat.UNKNOWN,
                        position_in_paper=position + i,
                        confidence=0.8
                    )
                    authors.append(author)
        
        return authors
    
    def _looks_like_single_name(self, name: str) -> bool:
        """Check if a string looks like a single person's name."""
        if not name or len(name) < 3 or len(name) > 50:
            return False
        
        # Should contain letters and limited punctuation
        if not re.match(r'^[A-Za-z\s\.\-\']+$', name):
            return False
        
        # Should have at least one space (first and last name)
        if ' ' not in name and ',' not in name:
            return False
        
        # Check for common name patterns
        name_patterns = [
            r'^[A-Z][a-z]+ [A-Z][a-z]+$',  # First Last
            r'^[A-Z][a-z]+,\s*[A-Z][a-z]+$',  # Last, First
            r'^[A-Z]\.\s*[A-Z][a-z]+$',  # F. Last
            r'^[A-Z][a-z]+ [A-Z]\. [A-Z][a-z]+$',  # First M. Last
        ]
        
        for pattern in name_patterns:
            if re.match(pattern, name):
                return True
        
        return False
    
    def _enhance_author_with_institutions(self, author: EnhancedAuthor, text: str):
        """Enhance author with institutional affiliations."""
        # Look for institutions near the author's name
        author_context = self._find_author_context(author.name, text)
        
        institution_matches = []
        for pattern in self.institution_patterns:
            matches = re.finditer(pattern, author_context, re.IGNORECASE)
            for match in matches:
                inst_name = match.group(1).strip()
                if inst_name and 3 <= len(inst_name) <= 50:
                    institution_matches.append(inst_name)
        
        # Process and normalize institutions
        for inst_name in institution_matches:
            institution = self._process_institution(inst_name)
            if institution:
                author.affiliations.append(institution)
        
        # Limit to reasonable number of affiliations
        author.affiliations = author.affiliations[:5]
    
    def _find_author_context(self, author_name: str, text: str, context_size: int = 500) -> str:
        """Find text context around author name."""
        # Find author name in text
        name_pattern = re.escape(author_name)
        match = re.search(name_pattern, text, re.IGNORECASE)
        
        if match:
            start = max(0, match.start() - context_size)
            end = min(len(text), match.end() + context_size)
            return text[start:end]
        
        return ""
    
    def _process_institution(self, inst_name: str) -> Optional[Institution]:
        """Process and normalize institution name."""
        inst_name = inst_name.strip()
        if not inst_name:
            return None
        
        # Try database normalization first
        normalized_inst = self.institution_db.normalize_institution(inst_name)
        if normalized_inst:
            return normalized_inst
        
        # Create new institution
        inst_type = self._classify_institution(inst_name)
        return Institution(
            name=inst_name,
            normalized_name="",
            type=inst_type,
            confidence=0.6
        )
    
    def _classify_institution(self, inst_name: str) -> InstitutionType:
        """Classify institution type based on name."""
        inst_lower = inst_name.lower()
        
        if any(word in inst_lower for word in ['university', 'college', 'school']):
            return InstitutionType.UNIVERSITY
        elif any(word in inst_lower for word in ['institute', 'research', 'laboratory', 'lab', 'center']):
            return InstitutionType.RESEARCH_INSTITUTE
        elif any(word in inst_lower for word in ['corp', 'inc', 'ltd', 'company', 'technologies']):
            return InstitutionType.COMPANY
        elif any(word in inst_lower for word in ['hospital', 'medical', 'health']):
            return InstitutionType.HOSPITAL
        elif any(word in inst_lower for word in ['government', 'agency', 'department', 'ministry']):
            return InstitutionType.GOVERNMENT
        else:
            return InstitutionType.UNKNOWN
    
    def _enhance_author_with_contact_info(self, author: EnhancedAuthor, text: str):
        """Enhance author with contact information."""
        # Look for email addresses near author name
        author_context = self._find_author_context(author.name, text)
        
        email_matches = re.finditer(self.email_pattern, author_context)
        for match in email_matches:
            email = match.group(0)
            if self._is_likely_author_email(email, author.name):
                author.email = email
                break
    
    def _is_likely_author_email(self, email: str, author_name: str) -> bool:
        """Check if email is likely to belong to the author."""
        email_local = email.split('@')[0].lower()
        
        # Check if email contains parts of author name
        if hasattr(author, 'last_name') and author.last_name:
            if author.last_name.lower() in email_local:
                return True
        
        if hasattr(author, 'first_name') and author.first_name:
            if author.first_name.lower() in email_local:
                return True
        
        return False
    
    def _extract_funding_sources(self, text: str) -> List[FundingSource]:
        """Extract funding information from text."""
        funding_sources = []
        
        # Look for acknowledgments or funding sections
        funding_sections = self._find_funding_sections(text)
        
        for section in funding_sections:
            sources = self._parse_funding_section(section)
            funding_sources.extend(sources)
        
        return funding_sources
    
    def _find_funding_sections(self, text: str) -> List[str]:
        """Find funding-related sections in the text."""
        funding_sections = []
        
        # Look for acknowledgments sections
        ack_patterns = [
            r'(?i)acknowledgments?(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)funding(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)grants?(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)support(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in ack_patterns:
            matches = re.finditer(pattern, text, re.MULTILINE | re.DOTALL)
            for match in matches:
                section_text = match.group(1).strip()
                if section_text and len(section_text) < 1000:  # Reasonable section length
                    funding_sections.append(section_text)
        
        return funding_sections
    
    def _parse_funding_section(self, section: str) -> List[FundingSource]:
        """Parse funding sources from a funding section."""
        sources = []
        
        for pattern in self.funding_patterns:
            matches = re.finditer(pattern, section, re.IGNORECASE)
            for match in matches:
                source_text = match.group(1).strip()
                if source_text:
                    source = self._process_funding_source(source_text)
                    if source:
                        sources.append(source)
        
        return sources
    
    def _process_funding_source(self, source_text: str) -> Optional[FundingSource]:
        """Process a funding source string."""
        source_text = source_text.strip()
        if not source_text or len(source_text) < 2:
            return None
        
        # Check if it's a grant number
        if re.match(r'^[A-Z0-9-]+$', source_text):
            return FundingSource(
                name=source_text,
                normalized_name=source_text.lower(),
                type=FundingSourceType.UNKNOWN,
                grant_number=source_text,
                confidence=0.7
            )
        
        # Try to match against known funding sources
        for known_source in self.funding_db.funding_sources.values():
            if self._fuzzy_match_funding(source_text, known_source.name):
                return FundingSource(
                    name=known_source.name,
                    normalized_name=known_source.normalized_name,
                    type=known_source.type,
                    country=known_source.country,
                    confidence=0.8
                )
        
        # Create new funding source
        source_type = self._classify_funding_source(source_text)
        return FundingSource(
            name=source_text,
            normalized_name="",
            type=source_type,
            confidence=0.5
        )
    
    def _fuzzy_match_funding(self, text: str, known_name: str) -> bool:
        """Fuzzy match funding source names."""
        text_lower = text.lower()
        known_lower = known_name.lower()
        
        # Check for substring matches
        if known_lower in text_lower or text_lower in known_lower:
            return True
        
        # Check for word overlap
        text_words = set(text_lower.split())
        known_words = set(known_lower.split())
        
        if len(text_words & known_words) >= 2:
            return True
        
        return False
    
    def _classify_funding_source(self, source_text: str) -> FundingSourceType:
        """Classify funding source type."""
        source_lower = source_text.lower()
        
        if any(word in source_lower for word in ['nsf', 'nih', 'nasa', 'doe', 'darpa', 'government', 'agency']):
            return FundingSourceType.GOVERNMENT
        elif any(word in source_lower for word in ['foundation', 'fund']):
            return FundingSourceType.FOUNDATION
        elif any(word in source_lower for word in ['corp', 'inc', 'company', 'industries']):
            return FundingSourceType.INDUSTRY
        elif any(word in source_lower for word in ['university', 'college', 'school']):
            return FundingSourceType.UNIVERSITY
        elif any(word in source_lower for word in ['european', 'international', 'erc', 'horizon']):
            return FundingSourceType.INTERNATIONAL
        else:
            return FundingSourceType.UNKNOWN
    
    def _extract_abstract(self, text: str) -> Optional[str]:
        """Extract abstract from text."""
        abstract_patterns = [
            r'(?i)abstract(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)summary(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in abstract_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
            if match:
                abstract_text = match.group(1).strip()
                if abstract_text and len(abstract_text) > 50:  # Reasonable abstract length
                    return abstract_text
        
        return None
    
    def _extract_keywords(self, text: str) -> List[str]:
        """Extract keywords from text."""
        keywords = []
        
        keyword_patterns = [
            r'(?i)keywords?(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)index\s+terms?(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in keyword_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
            if match:
                keyword_text = match.group(1).strip()
                # Split by common separators
                keyword_list = re.split(r'[,;]', keyword_text)
                for keyword in keyword_list:
                    keyword = keyword.strip()
                    if keyword and len(keyword) > 2:
                        keywords.append(keyword)
        
        return keywords
    
    def _extract_subjects(self, text: str) -> List[str]:
        """Extract subject classifications from text."""
        subjects = []
        
        subject_patterns = [
            r'(?i)subject\s+classification(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)categories?(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
            r'(?i)MSC\s+(?:2020|2010)?(?:\s*:|\s*\n)([^.]+?)(?:\n\n|\n[A-Z]|$)',
        ]
        
        for pattern in subject_patterns:
            match = re.search(pattern, text, re.MULTILINE | re.DOTALL)
            if match:
                subject_text = match.group(1).strip()
                # Split by common separators
                subject_list = re.split(r'[,;]', subject_text)
                for subject in subject_list:
                    subject = subject.strip()
                    if subject and len(subject) > 2:
                        subjects.append(subject)
        
        return subjects
    
    def _calculate_confidence(self, metadata: EnhancedMetadata) -> float:
        """Calculate overall extraction confidence."""
        scores = []
        
        # Title confidence
        if metadata.title:
            scores.append(0.9)
        
        # Author confidence
        if metadata.authors:
            author_scores = [author.confidence for author in metadata.authors]
            scores.append(sum(author_scores) / len(author_scores))
        
        # Abstract confidence
        if metadata.abstract:
            scores.append(0.8)
        
        # Funding confidence
        if metadata.funding_sources:
            funding_scores = [source.confidence for source in metadata.funding_sources]
            scores.append(sum(funding_scores) / len(funding_scores))
        
        return sum(scores) / len(scores) if scores else 0.0
    
    def _calculate_completeness(self, metadata: EnhancedMetadata) -> float:
        """Calculate metadata completeness score."""
        total_fields = 15
        filled_fields = 0
        
        # Check required fields
        if metadata.title: filled_fields += 1
        if metadata.authors: filled_fields += 1
        if metadata.abstract: filled_fields += 1
        if metadata.year: filled_fields += 1
        if metadata.doi: filled_fields += 1
        if metadata.journal: filled_fields += 1
        if metadata.keywords: filled_fields += 1
        if metadata.subjects: filled_fields += 1
        if metadata.funding_sources: filled_fields += 1
        
        # Check author completeness
        if metadata.authors:
            for author in metadata.authors:
                if author.affiliations: filled_fields += 1
                if author.email: filled_fields += 1
                break  # Count once for any author having these fields
        
        # Check additional fields
        if metadata.volume: filled_fields += 1
        if metadata.issue: filled_fields += 1
        if metadata.pages: filled_fields += 1
        if metadata.publication_date: filled_fields += 1
        
        return filled_fields / total_fields
    
    def export_metadata(self, metadata: EnhancedMetadata, format: str = "json") -> str:
        """Export metadata in specified format."""
        if format.lower() == "json":
            # Convert metadata to dict and handle enum serialization
            metadata_dict = asdict(metadata)
            metadata_dict = self._convert_enums_to_strings(metadata_dict)
            return json.dumps(metadata_dict, indent=2, ensure_ascii=False)
        elif format.lower() == "yaml":
            try:
                import yaml
                metadata_dict = asdict(metadata)
                metadata_dict = self._convert_enums_to_strings(metadata_dict)
                return yaml.dump(metadata_dict, default_flow_style=False, allow_unicode=True)
            except ImportError:
                logger.warning("PyYAML not available, falling back to JSON")
                return self.export_metadata(metadata, "json")
        else:
            raise ValueError(f"Unsupported export format: {format}")
    
    def _convert_enums_to_strings(self, obj: Any) -> Any:
        """Convert enum values to strings for JSON serialization."""
        if isinstance(obj, dict):
            return {key: self._convert_enums_to_strings(value) for key, value in obj.items()}
        elif isinstance(obj, list):
            return [self._convert_enums_to_strings(item) for item in obj]
        elif hasattr(obj, 'value'):  # Enum
            return obj.value
        else:
            return obj
    
    def get_extraction_summary(self, metadata: EnhancedMetadata) -> Dict[str, Any]:
        """Get a summary of extraction results."""
        return {
            "title": metadata.title,
            "author_count": len(metadata.authors),
            "institution_count": sum(len(author.affiliations) for author in metadata.authors),
            "funding_source_count": len(metadata.funding_sources),
            "has_abstract": bool(metadata.abstract),
            "keyword_count": len(metadata.keywords),
            "subject_count": len(metadata.subjects),
            "extraction_confidence": metadata.extraction_confidence,
            "completeness_score": metadata.completeness_score,
            "language": metadata.language,
            "word_count": metadata.word_count,
        }

# Factory function for easy instantiation
def create_enhanced_metadata_extractor(config: Optional[Dict[str, Any]] = None) -> EnhancedMetadataExtractor:
    """Create an enhanced metadata extractor with optional configuration."""
    return EnhancedMetadataExtractor(config)

# Integration function for existing pipeline
def integrate_with_content_extractor(content_extractor_result: Dict[str, Any], 
                                   config: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Integrate enhanced metadata extraction with existing content extractor results."""
    logger.info("Integrating enhanced metadata extraction with content extractor")
    
    try:
        # Create extractor
        extractor = create_enhanced_metadata_extractor(config)
        
        # Get text content
        full_text = content_extractor_result.get("full_text", "")
        existing_metadata = content_extractor_result.get("metadata", {})
        
        # Extract enhanced metadata
        enhanced_metadata = extractor.extract_metadata(full_text, existing_metadata)
        
        # Create integration result
        result = content_extractor_result.copy()
        result["enhanced_metadata"] = asdict(enhanced_metadata)
        result["enhanced_metadata"] = extractor._convert_enums_to_strings(result["enhanced_metadata"])
        result["metadata_summary"] = extractor.get_extraction_summary(enhanced_metadata)
        
        logger.info("Enhanced metadata integration completed successfully")
        return result
        
    except Exception as e:
        logger.error(f"Enhanced metadata integration failed: {str(e)}")
        # Return original result if enhancement fails
        result = content_extractor_result.copy()
        result["enhanced_metadata_error"] = str(e)
        return result 
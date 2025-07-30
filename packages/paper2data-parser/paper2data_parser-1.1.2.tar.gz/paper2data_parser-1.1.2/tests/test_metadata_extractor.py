"""
Comprehensive tests for enhanced metadata extraction functionality.
"""

import unittest
import tempfile
import os
from datetime import datetime
from unittest.mock import patch, MagicMock

from paper2data.metadata_extractor import (
    MetadataExtractor, EnhancedMetadata, Author, PublicationInfo, Citation,
    PaperType, PublicationStatus, extract_metadata, export_metadata
)


class TestAuthor(unittest.TestCase):
    """Test Author dataclass"""
    
    def test_author_creation(self):
        """Test basic author creation"""
        author = Author(
            name="John Doe",
            affiliations=["MIT", "Harvard"],
            email="john@example.com",
            orcid="0000-0000-0000-0000"
        )
        
        self.assertEqual(author.name, "John Doe")
        self.assertEqual(author.affiliations, ["MIT", "Harvard"])
        self.assertEqual(author.email, "john@example.com")
        self.assertEqual(author.orcid, "0000-0000-0000-0000")
    
    def test_author_post_init_cleaning(self):
        """Test author data cleaning"""
        author = Author(
            name="  John Doe  ",
            affiliations=["  MIT  ", "", "  Harvard  "],
            email="  John@Example.COM  ",
            orcid="  0000-0000-0000-0000  "
        )
        
        self.assertEqual(author.name, "John Doe")
        self.assertEqual(author.affiliations, ["MIT", "Harvard"])
        self.assertEqual(author.email, "john@example.com")
        self.assertEqual(author.orcid, "0000-0000-0000-0000")


class TestPublicationInfo(unittest.TestCase):
    """Test PublicationInfo dataclass"""
    
    def test_publication_info_creation(self):
        """Test basic publication info creation"""
        pub_info = PublicationInfo(
            journal="Nature",
            year=2023,
            volume="123",
            pages="1-10"
        )
        
        self.assertEqual(pub_info.journal, "Nature")
        self.assertEqual(pub_info.year, 2023)
        self.assertEqual(pub_info.volume, "123")
        self.assertEqual(pub_info.pages, "1-10")
    
    def test_publication_info_cleaning(self):
        """Test publication info data cleaning"""
        pub_info = PublicationInfo(
            journal="  Nature  ",
            conference="  ICML  ",
            publisher="  Springer  "
        )
        
        self.assertEqual(pub_info.journal, "Nature")
        self.assertEqual(pub_info.conference, "ICML")
        self.assertEqual(pub_info.publisher, "Springer")


class TestCitation(unittest.TestCase):
    """Test Citation dataclass"""
    
    def test_citation_creation(self):
        """Test basic citation creation"""
        citation = Citation(
            text="Smith, J. (2020). Machine Learning Basics. Journal of AI, 15(3), 25-40.",
            authors=["J. Smith"],
            title="Machine Learning Basics",
            year=2020,
            journal="Journal of AI"
        )
        
        self.assertEqual(citation.authors, ["J. Smith"])
        self.assertEqual(citation.title, "Machine Learning Basics")
        self.assertEqual(citation.year, 2020)
        self.assertEqual(citation.journal, "Journal of AI")
    
    def test_citation_cleaning(self):
        """Test citation data cleaning"""
        citation = Citation(
            text="  Some citation text  ",
            authors=["  J. Smith  ", "", "  M. Johnson  "],
            title="  Some Title  ",
            journal="  Some Journal  "
        )
        
        self.assertEqual(citation.authors, ["J. Smith", "M. Johnson"])
        self.assertEqual(citation.title, "Some Title")
        self.assertEqual(citation.journal, "Some Journal")


class TestEnhancedMetadata(unittest.TestCase):
    """Test EnhancedMetadata dataclass"""
    
    def test_metadata_creation(self):
        """Test basic metadata creation"""
        metadata = EnhancedMetadata(
            title="Test Paper",
            abstract="This is a test abstract",
            authors=[Author(name="John Doe")],
            keywords=["test", "paper"],
            doi="10.1234/test.doi"
        )
        
        self.assertEqual(metadata.title, "Test Paper")
        self.assertEqual(metadata.abstract, "This is a test abstract")
        self.assertEqual(len(metadata.authors), 1)
        self.assertEqual(metadata.authors[0].name, "John Doe")
        self.assertEqual(metadata.keywords, ["test", "paper"])
        self.assertEqual(metadata.doi, "10.1234/test.doi")
    
    def test_metadata_to_dict(self):
        """Test metadata to dictionary conversion"""
        metadata = EnhancedMetadata(
            title="Test Paper",
            abstract="Test abstract",
            extraction_date=datetime(2023, 1, 1)
        )
        
        data = metadata.to_dict()
        
        self.assertEqual(data["title"], "Test Paper")
        self.assertEqual(data["abstract"], "Test abstract")
        self.assertEqual(data["extraction_date"], "2023-01-01T00:00:00")


class TestMetadataExtractor(unittest.TestCase):
    """Test MetadataExtractor class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.extractor = MetadataExtractor()
    
    def test_clean_title(self):
        """Test title cleaning"""
        title = "  Machine Learning: A Comprehensive Survey  "
        cleaned = self.extractor._clean_title(title)
        self.assertEqual(cleaned, "Machine Learning: A Comprehensive Survey")
        
        title_with_quotes = '"Machine Learning Survey"'
        cleaned = self.extractor._clean_title(title_with_quotes)
        self.assertEqual(cleaned, "Machine Learning Survey")
    
    def test_clean_abstract(self):
        """Test abstract cleaning"""
        abstract = "This is a test\nabstract with\nline breaks."
        cleaned = self.extractor._clean_abstract(abstract)
        self.assertEqual(cleaned, "This is a test abstract with line breaks.")
    
    def test_parse_authors(self):
        """Test author parsing"""
        author_text = "John Doe, Jane Smith, and Michael Johnson"
        authors = self.extractor._parse_authors(author_text)
        
        self.assertEqual(len(authors), 3)
        self.assertEqual(authors[0].name, "John Doe")
        self.assertEqual(authors[1].name, "Jane Smith")
        self.assertEqual(authors[2].name, "Michael Johnson")
    
    def test_extract_title_patterns(self):
        """Test title extraction patterns"""
        # Test with simple title
        text = "Machine Learning in Healthcare\n\nAbstract: This paper discusses..."
        title = self.extractor._extract_title(text)
        self.assertEqual(title, "Machine Learning in Healthcare")
        
        # Test with title: format
        text = "Title: Advanced Neural Networks\n\nContent follows..."
        title = self.extractor._extract_title(text)
        self.assertEqual(title, "Advanced Neural Networks")
    
    def test_extract_abstract_patterns(self):
        """Test abstract extraction patterns"""
        text = "Title\n\nAbstract: This is the abstract text. It contains multiple sentences.\n\nIntroduction:"
        abstract = self.extractor._extract_abstract(text)
        self.assertEqual(abstract, "This is the abstract text. It contains multiple sentences.")
        
        text = "Title\n\nABSTRACT\nThis is the abstract text.\n\nKeywords:"
        abstract = self.extractor._extract_abstract(text)
        self.assertEqual(abstract, "This is the abstract text.")
    
    def test_extract_keywords_patterns(self):
        """Test keyword extraction patterns"""
        text = "Abstract text here.\n\nKeywords: machine learning, neural networks, deep learning\n\nIntroduction:"
        keywords = self.extractor._extract_keywords(text)
        self.assertEqual(keywords, ["machine learning", "neural networks", "deep learning"])
        
        text = "Abstract text here.\n\nKEYWORDS: AI, ML, DL\n\nIntroduction:"
        keywords = self.extractor._extract_keywords(text)
        self.assertEqual(keywords, ["AI", "ML", "DL"])
    
    def test_extract_doi_patterns(self):
        """Test DOI extraction patterns"""
        text = "This paper has DOI: 10.1234/journal.2023.001"
        doi = self.extractor._extract_doi(text)
        self.assertEqual(doi, "10.1234/journal.2023.001")
        
        text = "Available at https://doi.org/10.1234/journal.2023.001"
        doi = self.extractor._extract_doi(text)
        self.assertEqual(doi, "10.1234/journal.2023.001")
    
    def test_extract_arxiv_id_patterns(self):
        """Test arXiv ID extraction patterns"""
        text = "This paper is available at arXiv:2023.12345v1"
        arxiv_id = self.extractor._extract_arxiv_id(text)
        self.assertEqual(arxiv_id, "2023.12345v1")
        
        text = "Available at https://arxiv.org/abs/2023.12345"
        arxiv_id = self.extractor._extract_arxiv_id(text)
        self.assertEqual(arxiv_id, "2023.12345")
    
    def test_extract_publication_info(self):
        """Test publication information extraction"""
        text = "Published in Nature Journal, 2023. Volume 15, Issue 3."
        pub_info = self.extractor._extract_publication_info(text)
        
        # Should extract journal name and year
        self.assertIsNotNone(pub_info.journal)
        self.assertIsNotNone(pub_info.year)
    
    def test_parse_citation(self):
        """Test citation parsing"""
        citation_text = "Smith, J. (2020). \"Machine Learning Basics\". Journal of AI, 15(3), 25-40. doi:10.1234/jai.2020.001"
        citation = self.extractor._parse_citation(citation_text, 1)
        
        self.assertIsNotNone(citation)
        self.assertEqual(citation.position, 1)
        self.assertIn("Smith", citation.authors)
        self.assertEqual(citation.title, "Machine Learning Basics")
        self.assertEqual(citation.year, 2020)
        self.assertEqual(citation.doi, "10.1234/jai.2020.001")
    
    def test_extract_subject_categories(self):
        """Test subject category extraction"""
        text = "This paper focuses on Machine Learning and Computer Vision applications in Medicine."
        categories = self.extractor._extract_subject_categories(text)
        
        self.assertIn("Machine Learning", categories)
        self.assertIn("Computer Vision", categories)
        self.assertIn("Medicine", categories)
    
    def test_determine_paper_type(self):
        """Test paper type determination"""
        # Test conference paper
        text = "Proceedings of the International Conference on Machine Learning"
        metadata = EnhancedMetadata(title="Test", abstract="Test")
        paper_type = self.extractor._determine_paper_type(text, metadata)
        self.assertEqual(paper_type, PaperType.CONFERENCE_PAPER)
        
        # Test journal article
        text = "Published in Nature Journal"
        metadata = EnhancedMetadata(title="Test", abstract="Test")
        metadata.publication_info = PublicationInfo(journal="Nature")
        paper_type = self.extractor._determine_paper_type(text, metadata)
        self.assertEqual(paper_type, PaperType.JOURNAL_ARTICLE)
        
        # Test preprint
        text = "Available on arXiv"
        metadata = EnhancedMetadata(title="Test", abstract="Test", arxiv_id="2023.12345")
        paper_type = self.extractor._determine_paper_type(text, metadata)
        self.assertEqual(paper_type, PaperType.PREPRINT)
    
    def test_calculate_confidence_scores(self):
        """Test confidence score calculations"""
        # Test title confidence
        good_title = "Machine Learning Applications in Healthcare"
        confidence = self.extractor._calculate_title_confidence(good_title)
        self.assertGreater(confidence, 0.5)
        
        # Test abstract confidence
        good_abstract = "This paper presents a comprehensive survey of machine learning techniques. We analyze various approaches and their applications. The results demonstrate significant improvements in accuracy."
        confidence = self.extractor._calculate_abstract_confidence(good_abstract)
        self.assertGreater(confidence, 0.5)
        
        # Test author confidence
        good_authors = [
            Author(name="John Doe", email="john@example.com"),
            Author(name="Jane Smith", orcid="0000-0000-0000-0000")
        ]
        confidence = self.extractor._calculate_author_confidence(good_authors)
        self.assertGreater(confidence, 0.5)
    
    def test_get_context_around_name(self):
        """Test context extraction around names"""
        text = "John Doe is a researcher at MIT. He works on machine learning. Contact: john@mit.edu"
        context = self.extractor._get_context_around_name(text, "John Doe", 20)
        
        self.assertIn("John Doe", context)
        self.assertIn("MIT", context)
    
    def test_find_author_email(self):
        """Test email finding for authors"""
        text = "John Doe (john@example.com) is the lead author."
        email = self.extractor._find_author_email(text, "John Doe")
        self.assertEqual(email, "john@example.com")
    
    def test_find_author_orcid(self):
        """Test ORCID finding for authors"""
        text = "John Doe ORCID: 0000-0000-0000-0000 is a researcher."
        orcid = self.extractor._find_author_orcid(text, "John Doe")
        self.assertEqual(orcid, "0000-0000-0000-0000")
    
    def test_find_author_affiliations(self):
        """Test affiliation finding for authors"""
        text = "John Doe from MIT and Harvard University conducted this research."
        affiliations = self.extractor._find_author_affiliations(text, "John Doe")
        
        # Should find at least one affiliation
        self.assertGreater(len(affiliations), 0)
    
    def test_parse_pdf_authors(self):
        """Test PDF metadata author parsing"""
        author_string = "John Doe, Jane Smith, Michael Johnson"
        authors = self.extractor._parse_pdf_authors(author_string)
        
        self.assertEqual(len(authors), 3)
        self.assertEqual(authors[0].name, "John Doe")
        self.assertEqual(authors[1].name, "Jane Smith")
        self.assertEqual(authors[2].name, "Michael Johnson")
    
    def test_parse_pdf_date(self):
        """Test PDF date parsing"""
        # Test standard PDF date format
        date_string = "D:20230101120000Z"
        date = self.extractor._parse_pdf_date(date_string)
        
        self.assertIsNotNone(date)
        self.assertEqual(date.year, 2023)
        self.assertEqual(date.month, 1)
        self.assertEqual(date.day, 1)
        
        # Test simple date format
        date_string = "20230101120000"
        date = self.extractor._parse_pdf_date(date_string)
        
        self.assertIsNotNone(date)
        self.assertEqual(date.year, 2023)
    
    @patch('paper2data.metadata_extractor.fitz.open')
    def test_extract_metadata_with_mock(self, mock_open):
        """Test metadata extraction with mocked PDF"""
        # Mock PDF document
        mock_doc = MagicMock()
        mock_doc.page_count = 10
        mock_doc.metadata = {
            'title': 'Test Paper',
            'author': 'John Doe',
            'creationDate': 'D:20230101120000Z'
        }
        
        # Mock page
        mock_page = MagicMock()
        mock_page.get_text.return_value = """
        Machine Learning in Healthcare
        
        John Doe, Jane Smith
        MIT, Harvard University
        john@mit.edu
        
        Abstract: This paper presents a comprehensive survey of machine learning techniques in healthcare applications.
        
        Keywords: machine learning, healthcare, artificial intelligence
        
        DOI: 10.1234/journal.2023.001
        
        1. Introduction
        This section introduces the topic.
        
        References
        [1] Smith, J. (2020). "AI in Medicine". Nature, 15(3), 25-40.
        """
        
        mock_doc.__getitem__.return_value = mock_page
        mock_doc.__len__.return_value = 10
        mock_doc.__iter__.return_value = [mock_page] * 10
        mock_open.return_value = mock_doc
        
        # Test extraction
        metadata = self.extractor.extract_metadata("test.pdf")
        
        # Verify results
        self.assertEqual(metadata.title, "Machine Learning in Healthcare")
        self.assertIn("machine learning", metadata.abstract.lower())
        self.assertGreater(len(metadata.authors), 0)
        self.assertIn("machine learning", metadata.keywords)
        self.assertEqual(metadata.doi, "10.1234/journal.2023.001")
        self.assertEqual(metadata.page_count, 10)
        self.assertGreater(metadata.title_confidence, 0.5)
        self.assertGreater(metadata.abstract_confidence, 0.5)


class TestGlobalFunctions(unittest.TestCase):
    """Test global functions"""
    
    @patch('paper2data.metadata_extractor.metadata_extractor.extract_metadata')
    def test_extract_metadata_function(self, mock_extract):
        """Test global extract_metadata function"""
        mock_metadata = EnhancedMetadata(title="Test", abstract="Test")
        mock_extract.return_value = mock_metadata
        
        result = extract_metadata("test.pdf")
        
        self.assertEqual(result.title, "Test")
        mock_extract.assert_called_once_with("test.pdf")
    
    def test_export_metadata_json(self):
        """Test metadata export to JSON"""
        metadata = EnhancedMetadata(
            title="Test Paper",
            abstract="Test abstract",
            keywords=["test", "paper"]
        )
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_path = f.name
        
        try:
            success = export_metadata(metadata, output_path, 'json')
            self.assertTrue(success)
            
            # Verify file was created
            self.assertTrue(os.path.exists(output_path))
            
            # Verify file content
            with open(output_path, 'r') as f:
                content = f.read()
                self.assertIn("Test Paper", content)
                self.assertIn("Test abstract", content)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)
    
    def test_export_metadata_unsupported_format(self):
        """Test metadata export with unsupported format"""
        metadata = EnhancedMetadata(title="Test", abstract="Test")
        
        with tempfile.NamedTemporaryFile(mode='w', suffix='.xml', delete=False) as f:
            output_path = f.name
        
        try:
            success = export_metadata(metadata, output_path, 'xml')
            self.assertFalse(success)
        finally:
            if os.path.exists(output_path):
                os.unlink(output_path)


class TestEnumTypes(unittest.TestCase):
    """Test enum types"""
    
    def test_paper_type_enum(self):
        """Test PaperType enum"""
        self.assertEqual(PaperType.JOURNAL_ARTICLE.value, "journal_article")
        self.assertEqual(PaperType.CONFERENCE_PAPER.value, "conference_paper")
        self.assertEqual(PaperType.PREPRINT.value, "preprint")
    
    def test_publication_status_enum(self):
        """Test PublicationStatus enum"""
        self.assertEqual(PublicationStatus.PUBLISHED.value, "published")
        self.assertEqual(PublicationStatus.ACCEPTED.value, "accepted")
        self.assertEqual(PublicationStatus.PREPRINT.value, "preprint")


if __name__ == '__main__':
    unittest.main() 
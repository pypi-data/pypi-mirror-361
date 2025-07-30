"""
NLP Processing Plugin for Paper2Data

This plugin provides advanced natural language processing capabilities
for academic paper analysis, including keyword extraction, content
classification, and text enhancement features.

Features:
- Keyword extraction using TF-IDF and domain-specific methods
- Content classification (subject area, document type)
- Text quality assessment
- Academic phrase detection
- Language detection and processing
- Sentiment analysis for research content

Author: Paper2Data Team
Version: 1.0.0
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union, Set, Tuple
from dataclasses import dataclass, field
from collections import Counter, defaultdict
import json
import math
from pathlib import Path

from ..plugin_manager import BasePlugin, PluginMetadata, plugin_hook, HookPriority
from ..plugin_hooks import HookCategory


logger = logging.getLogger(__name__)


@dataclass
class KeywordResult:
    """Represents extracted keywords with metadata"""
    keywords: List[str]
    scores: Dict[str, float]
    categories: Dict[str, List[str]]
    confidence: float
    method: str
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "keywords": self.keywords,
            "scores": self.scores,
            "categories": self.categories,
            "confidence": self.confidence,
            "method": self.method
        }


@dataclass
class ContentClassification:
    """Represents content classification results"""
    subject_areas: List[str]
    document_type: str
    confidence: float
    academic_level: str
    research_domains: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "subject_areas": self.subject_areas,
            "document_type": self.document_type,
            "confidence": self.confidence,
            "academic_level": self.academic_level,
            "research_domains": self.research_domains
        }


@dataclass
class TextQuality:
    """Represents text quality assessment"""
    readability_score: float
    academic_writing_score: float
    complexity_level: str
    issues: List[str]
    recommendations: List[str]
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "readability_score": self.readability_score,
            "academic_writing_score": self.academic_writing_score,
            "complexity_level": self.complexity_level,
            "issues": self.issues,
            "recommendations": self.recommendations
        }


class NLPProcessor:
    """Core NLP processing functionality"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("NLPProcessor")
        
        # Academic keywords by domain
        self.academic_domains = {
            "computer_science": [
                "algorithm", "machine learning", "artificial intelligence", "neural network",
                "deep learning", "computer vision", "natural language processing", "data mining",
                "software engineering", "distributed systems", "cybersecurity", "blockchain",
                "optimization", "computational complexity", "programming", "database"
            ],
            "mathematics": [
                "theorem", "proof", "lemma", "corollary", "axiom", "conjecture", "analysis",
                "algebra", "geometry", "topology", "calculus", "probability", "statistics",
                "differential equation", "linear algebra", "number theory", "combinatorics"
            ],
            "physics": [
                "quantum", "relativity", "thermodynamics", "electromagnetic", "mechanics",
                "particle physics", "condensed matter", "optics", "plasma", "astrophysics",
                "cosmology", "nuclear physics", "atomic physics", "molecular physics"
            ],
            "biology": [
                "genome", "protein", "DNA", "RNA", "cell", "molecular", "genetics", "evolution",
                "ecology", "biochemistry", "neuroscience", "immunology", "microbiology",
                "bioinformatics", "phylogenetics", "metabolism", "enzyme", "chromosome"
            ],
            "chemistry": [
                "molecule", "reaction", "synthesis", "catalyst", "organic", "inorganic",
                "physical chemistry", "analytical chemistry", "spectroscopy", "crystallography",
                "thermochemistry", "electrochemistry", "polymer", "nanomaterial"
            ],
            "medicine": [
                "clinical", "patient", "diagnosis", "treatment", "therapy", "disease",
                "pathology", "pharmacology", "epidemiology", "biomarker", "clinical trial",
                "medical imaging", "surgery", "oncology", "cardiology", "neurology"
            ]
        }
        
        # Academic writing indicators
        self.academic_phrases = [
            "in this paper", "we propose", "our approach", "experimental results",
            "related work", "previous studies", "furthermore", "moreover", "however",
            "consequently", "in conclusion", "to summarize", "based on", "according to",
            "as shown in", "it can be seen that", "this demonstrates", "evidence suggests"
        ]
        
        # Document type indicators
        self.document_types = {
            "research_paper": ["abstract", "introduction", "methodology", "results", "conclusion"],
            "review_paper": ["survey", "review", "overview", "state of the art", "literature"],
            "conference_paper": ["conference", "proceedings", "workshop", "symposium"],
            "journal_article": ["journal", "volume", "issue", "pages", "doi"],
            "thesis": ["thesis", "dissertation", "advisor", "committee", "chapter"],
            "technical_report": ["report", "technical", "documentation", "manual"]
        }
        
        # Stop words for keyword extraction
        self.stop_words = {
            "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of",
            "with", "by", "from", "up", "about", "into", "through", "during", "before",
            "after", "above", "below", "between", "among", "within", "without", "against",
            "this", "that", "these", "those", "i", "me", "my", "myself", "we", "our",
            "ours", "ourselves", "you", "your", "yours", "yourself", "yourselves", "he",
            "him", "his", "himself", "she", "her", "hers", "herself", "it", "its",
            "itself", "they", "them", "their", "theirs", "themselves", "what", "which",
            "who", "whom", "whose", "this", "that", "these", "those", "am", "is", "are",
            "was", "were", "be", "been", "being", "have", "has", "had", "having", "do",
            "does", "did", "doing", "will", "would", "should", "could", "can", "may",
            "might", "must", "shall", "will", "would"
        }
    
    def extract_keywords(self, text: str, metadata: Dict[str, Any]) -> KeywordResult:
        """
        Extract keywords from text using multiple methods
        
        Args:
            text: Input text
            metadata: Document metadata
            
        Returns:
            KeywordResult: Extracted keywords with scores
        """
        try:
            # Clean and preprocess text
            clean_text = self._preprocess_text(text)
            
            # Extract keywords using different methods
            tfidf_keywords = self._extract_tfidf_keywords(clean_text)
            domain_keywords = self._extract_domain_keywords(clean_text)
            phrase_keywords = self._extract_phrase_keywords(clean_text)
            
            # Combine and score keywords
            combined_keywords = self._combine_keywords(
                tfidf_keywords, domain_keywords, phrase_keywords
            )
            
            # Categorize keywords
            categories = self._categorize_keywords(combined_keywords)
            
            # Calculate confidence
            confidence = self._calculate_keyword_confidence(
                combined_keywords, categories, text
            )
            
            return KeywordResult(
                keywords=list(combined_keywords.keys())[:50],  # Top 50 keywords
                scores=combined_keywords,
                categories=categories,
                confidence=confidence,
                method="hybrid_tfidf_domain"
            )
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {e}")
            return KeywordResult(
                keywords=[],
                scores={},
                categories={},
                confidence=0.0,
                method="error"
            )
    
    def _preprocess_text(self, text: str) -> str:
        """Preprocess text for keyword extraction"""
        # Convert to lowercase
        text = text.lower()
        
        # Remove special characters but keep spaces and letters
        text = re.sub(r'[^a-zA-Z\s]', ' ', text)
        
        # Remove extra whitespace
        text = re.sub(r'\s+', ' ', text)
        
        return text.strip()
    
    def _extract_tfidf_keywords(self, text: str) -> Dict[str, float]:
        """Extract keywords using TF-IDF method"""
        words = text.split()
        
        # Calculate term frequency
        tf = Counter(words)
        total_words = len(words)
        
        # Simple TF-IDF implementation
        tfidf_scores = {}
        for word, freq in tf.items():
            if word not in self.stop_words and len(word) > 2:
                # Simple TF calculation
                tf_score = freq / total_words
                
                # Simple IDF approximation (inverse document frequency)
                # In practice, you'd use a corpus for proper IDF calculation
                idf_score = math.log(1000 / (freq + 1))  # Simplified IDF
                
                tfidf_scores[word] = tf_score * idf_score
        
        return tfidf_scores
    
    def _extract_domain_keywords(self, text: str) -> Dict[str, float]:
        """Extract domain-specific keywords"""
        domain_scores = {}
        
        for domain, keywords in self.academic_domains.items():
            for keyword in keywords:
                if keyword.lower() in text:
                    # Count occurrences
                    count = text.lower().count(keyword.lower())
                    # Score based on frequency and keyword importance
                    score = count * 2.0  # Domain keywords get higher weight
                    domain_scores[keyword] = score
        
        return domain_scores
    
    def _extract_phrase_keywords(self, text: str) -> Dict[str, float]:
        """Extract multi-word phrases as keywords"""
        phrases = {}
        
        # Extract n-grams (2-4 words)
        words = text.split()
        
        for n in range(2, 5):  # 2-gram to 4-gram
            for i in range(len(words) - n + 1):
                phrase = ' '.join(words[i:i+n])
                
                # Filter out phrases with stop words
                if not any(word in self.stop_words for word in phrase.split()):
                    if phrase not in phrases:
                        phrases[phrase] = 0
                    phrases[phrase] += 1
        
        # Score phrases based on frequency
        max_freq = max(phrases.values()) if phrases else 1
        phrase_scores = {
            phrase: freq / max_freq 
            for phrase, freq in phrases.items() 
            if freq > 1  # Only keep phrases that appear more than once
        }
        
        return phrase_scores
    
    def _combine_keywords(self, *keyword_dicts: Dict[str, float]) -> Dict[str, float]:
        """Combine keywords from multiple extraction methods"""
        combined = defaultdict(float)
        
        for keyword_dict in keyword_dicts:
            for keyword, score in keyword_dict.items():
                combined[keyword] += score
        
        # Sort by score and return as regular dict
        sorted_keywords = sorted(combined.items(), key=lambda x: x[1], reverse=True)
        return dict(sorted_keywords)
    
    def _categorize_keywords(self, keywords: Dict[str, float]) -> Dict[str, List[str]]:
        """Categorize keywords by domain"""
        categories = defaultdict(list)
        
        for keyword in keywords:
            categorized = False
            
            # Check domain categories
            for domain, domain_keywords in self.academic_domains.items():
                if keyword.lower() in [dk.lower() for dk in domain_keywords]:
                    categories[domain].append(keyword)
                    categorized = True
                    break
            
            # Check for general academic terms
            if not categorized:
                if any(phrase in keyword.lower() for phrase in self.academic_phrases):
                    categories["academic_writing"].append(keyword)
                elif len(keyword.split()) > 1:
                    categories["multi_word_terms"].append(keyword)
                else:
                    categories["general_terms"].append(keyword)
        
        return dict(categories)
    
    def _calculate_keyword_confidence(self, keywords: Dict[str, float], 
                                    categories: Dict[str, List[str]], 
                                    text: str) -> float:
        """Calculate confidence score for keyword extraction"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for domain-specific keywords
        domain_keywords = sum(len(kw_list) for domain, kw_list in categories.items() 
                            if domain in self.academic_domains)
        confidence += min(domain_keywords * 0.05, 0.3)
        
        # Boost confidence for academic phrases
        academic_keywords = len(categories.get("academic_writing", []))
        confidence += min(academic_keywords * 0.03, 0.2)
        
        # Boost confidence for multi-word terms
        multi_word_keywords = len(categories.get("multi_word_terms", []))
        confidence += min(multi_word_keywords * 0.02, 0.1)
        
        return min(confidence, 1.0)
    
    def classify_content(self, text: str, metadata: Dict[str, Any]) -> ContentClassification:
        """
        Classify document content
        
        Args:
            text: Document text
            metadata: Document metadata
            
        Returns:
            ContentClassification: Classification results
        """
        try:
            # Detect subject areas
            subject_areas = self._detect_subject_areas(text)
            
            # Detect document type
            document_type = self._detect_document_type(text, metadata)
            
            # Assess academic level
            academic_level = self._assess_academic_level(text)
            
            # Identify research domains
            research_domains = self._identify_research_domains(text)
            
            # Calculate classification confidence
            confidence = self._calculate_classification_confidence(
                subject_areas, document_type, academic_level, research_domains
            )
            
            return ContentClassification(
                subject_areas=subject_areas,
                document_type=document_type,
                confidence=confidence,
                academic_level=academic_level,
                research_domains=research_domains
            )
            
        except Exception as e:
            self.logger.error(f"Content classification failed: {e}")
            return ContentClassification(
                subject_areas=[],
                document_type="unknown",
                confidence=0.0,
                academic_level="unknown",
                research_domains=[]
            )
    
    def _detect_subject_areas(self, text: str) -> List[str]:
        """Detect subject areas based on domain keywords"""
        text_lower = text.lower()
        subject_scores = {}
        
        for domain, keywords in self.academic_domains.items():
            score = 0
            for keyword in keywords:
                if keyword.lower() in text_lower:
                    score += text_lower.count(keyword.lower())
            
            if score > 0:
                subject_scores[domain] = score
        
        # Return domains with significant presence
        threshold = max(subject_scores.values()) * 0.3 if subject_scores else 0
        return [domain for domain, score in subject_scores.items() if score >= threshold]
    
    def _detect_document_type(self, text: str, metadata: Dict[str, Any]) -> str:
        """Detect document type based on content and metadata"""
        text_lower = text.lower()
        type_scores = {}
        
        for doc_type, indicators in self.document_types.items():
            score = 0
            for indicator in indicators:
                if indicator.lower() in text_lower:
                    score += text_lower.count(indicator.lower())
            type_scores[doc_type] = score
        
        # Return type with highest score
        if type_scores:
            return max(type_scores.items(), key=lambda x: x[1])[0]
        else:
            return "unknown"
    
    def _assess_academic_level(self, text: str) -> str:
        """Assess academic level based on writing complexity"""
        # Simple heuristic based on sentence length and vocabulary
        sentences = text.split('.')
        avg_sentence_length = sum(len(s.split()) for s in sentences) / len(sentences)
        
        # Count complex words (more than 6 characters)
        words = text.split()
        complex_words = sum(1 for word in words if len(word) > 6)
        complex_ratio = complex_words / len(words) if words else 0
        
        if avg_sentence_length > 25 and complex_ratio > 0.4:
            return "advanced"
        elif avg_sentence_length > 15 and complex_ratio > 0.25:
            return "intermediate"
        else:
            return "basic"
    
    def _identify_research_domains(self, text: str) -> List[str]:
        """Identify specific research domains"""
        domains = []
        text_lower = text.lower()
        
        # Look for research methodology terms
        if any(term in text_lower for term in ["experiment", "survey", "case study", "analysis"]):
            domains.append("empirical_research")
        
        if any(term in text_lower for term in ["theorem", "proof", "mathematical", "formal"]):
            domains.append("theoretical_research")
        
        if any(term in text_lower for term in ["application", "implementation", "system", "tool"]):
            domains.append("applied_research")
        
        if any(term in text_lower for term in ["review", "survey", "literature", "meta-analysis"]):
            domains.append("literature_review")
        
        return domains
    
    def _calculate_classification_confidence(self, subject_areas: List[str], 
                                           document_type: str, academic_level: str,
                                           research_domains: List[str]) -> float:
        """Calculate classification confidence"""
        confidence = 0.3  # Base confidence
        
        # Boost confidence for detected subject areas
        confidence += min(len(subject_areas) * 0.15, 0.4)
        
        # Boost confidence for document type detection
        if document_type != "unknown":
            confidence += 0.2
        
        # Boost confidence for academic level assessment
        if academic_level != "unknown":
            confidence += 0.1
        
        # Boost confidence for research domains
        confidence += min(len(research_domains) * 0.05, 0.15)
        
        return min(confidence, 1.0)
    
    def assess_text_quality(self, text: str) -> TextQuality:
        """
        Assess text quality for academic writing
        
        Args:
            text: Input text
            
        Returns:
            TextQuality: Quality assessment results
        """
        try:
            # Calculate readability score (simplified Flesch-Kincaid)
            readability = self._calculate_readability(text)
            
            # Assess academic writing quality
            academic_score = self._assess_academic_writing(text)
            
            # Determine complexity level
            complexity = self._determine_complexity(text)
            
            # Identify issues
            issues = self._identify_issues(text)
            
            # Generate recommendations
            recommendations = self._generate_recommendations(
                readability, academic_score, complexity, issues
            )
            
            return TextQuality(
                readability_score=readability,
                academic_writing_score=academic_score,
                complexity_level=complexity,
                issues=issues,
                recommendations=recommendations
            )
            
        except Exception as e:
            self.logger.error(f"Text quality assessment failed: {e}")
            return TextQuality(
                readability_score=0.0,
                academic_writing_score=0.0,
                complexity_level="unknown",
                issues=["Assessment failed"],
                recommendations=[]
            )
    
    def _calculate_readability(self, text: str) -> float:
        """Calculate readability score (simplified)"""
        sentences = text.split('.')
        words = text.split()
        
        if not sentences or not words:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        
        # Count syllables (simplified - count vowels)
        syllables = sum(sum(1 for char in word if char.lower() in 'aeiou') 
                       for word in words)
        avg_syllables = syllables / len(words) if words else 0
        
        # Simplified Flesch Reading Ease score
        readability = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        
        # Normalize to 0-1 range
        return max(0.0, min(1.0, readability / 100.0))
    
    def _assess_academic_writing(self, text: str) -> float:
        """Assess academic writing quality"""
        text_lower = text.lower()
        score = 0.0
        
        # Check for academic phrases
        academic_phrase_count = sum(1 for phrase in self.academic_phrases 
                                  if phrase in text_lower)
        score += min(academic_phrase_count * 0.05, 0.3)
        
        # Check for formal language indicators
        formal_indicators = ["therefore", "furthermore", "moreover", "however", 
                           "consequently", "nevertheless", "accordingly"]
        formal_count = sum(1 for indicator in formal_indicators 
                         if indicator in text_lower)
        score += min(formal_count * 0.03, 0.2)
        
        # Check for passive voice (simplified)
        passive_indicators = ["was", "were", "been", "being"]
        passive_count = sum(text_lower.count(indicator) for indicator in passive_indicators)
        passive_ratio = passive_count / len(text.split()) if text.split() else 0
        score += min(passive_ratio * 0.5, 0.1)
        
        # Check for technical terminology
        technical_words = sum(1 for word in text.split() if len(word) > 8)
        technical_ratio = technical_words / len(text.split()) if text.split() else 0
        score += min(technical_ratio * 0.3, 0.15)
        
        return min(score, 1.0)
    
    def _determine_complexity(self, text: str) -> str:
        """Determine text complexity level"""
        words = text.split()
        
        if not words:
            return "unknown"
        
        # Calculate complexity metrics
        avg_word_length = sum(len(word) for word in words) / len(words)
        long_words = sum(1 for word in words if len(word) > 6)
        long_word_ratio = long_words / len(words)
        
        if avg_word_length > 6 and long_word_ratio > 0.4:
            return "high"
        elif avg_word_length > 4.5 and long_word_ratio > 0.25:
            return "medium"
        else:
            return "low"
    
    def _identify_issues(self, text: str) -> List[str]:
        """Identify potential issues in text"""
        issues = []
        
        # Check for very long sentences
        sentences = text.split('.')
        long_sentences = sum(1 for s in sentences if len(s.split()) > 40)
        if long_sentences > len(sentences) * 0.2:
            issues.append("Many sentences are too long")
        
        # Check for repetitive words
        words = text.lower().split()
        word_counts = Counter(words)
        repetitive_words = [word for word, count in word_counts.items() 
                          if count > len(words) * 0.05 and word not in self.stop_words]
        if repetitive_words:
            issues.append(f"Repetitive words: {', '.join(repetitive_words[:3])}")
        
        # Check for lack of transitions
        transitions = ["however", "therefore", "furthermore", "moreover", "consequently"]
        transition_count = sum(1 for t in transitions if t in text.lower())
        if transition_count < len(sentences) * 0.1:
            issues.append("Limited use of transition words")
        
        return issues
    
    def _generate_recommendations(self, readability: float, academic_score: float,
                                complexity: str, issues: List[str]) -> List[str]:
        """Generate writing recommendations"""
        recommendations = []
        
        if readability < 0.3:
            recommendations.append("Consider simplifying sentence structure for better readability")
        
        if academic_score < 0.5:
            recommendations.append("Include more academic phrases and formal language")
        
        if complexity == "low":
            recommendations.append("Consider using more sophisticated vocabulary")
        elif complexity == "high":
            recommendations.append("Balance complex terms with clear explanations")
        
        if "Many sentences are too long" in issues:
            recommendations.append("Break down long sentences into shorter, clearer ones")
        
        if "Limited use of transition words" in issues:
            recommendations.append("Use more transition words to improve flow")
        
        return recommendations


class NLPPlugin(BasePlugin):
    """NLP processing plugin for Paper2Data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.processor = NLPProcessor(self.config)
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            name="nlp_processor",
            version="1.0.0",
            description="Advanced NLP processing for academic papers including keyword extraction and content classification",
            author="Paper2Data Team",
            license="MIT",
            website="https://github.com/paper2data/plugins",
            dependencies=["re", "logging", "collections"],
            paper2data_version=">=1.0.0",
            hooks=["extract_keywords", "classify_content", "enhance_metadata", "analyze_structure"],
            config_schema={
                "type": "object",
                "properties": {
                    "max_keywords": {
                        "type": "integer",
                        "minimum": 1,
                        "maximum": 100,
                        "default": 50,
                        "description": "Maximum number of keywords to extract"
                    },
                    "keyword_method": {
                        "type": "string",
                        "enum": ["tfidf", "domain", "hybrid"],
                        "default": "hybrid",
                        "description": "Method for keyword extraction"
                    },
                    "enable_classification": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable content classification"
                    },
                    "quality_assessment": {
                        "type": "boolean",
                        "default": True,
                        "description": "Enable text quality assessment"
                    },
                    "min_confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.3,
                        "description": "Minimum confidence threshold for results"
                    }
                }
            },
            tags=["nlp", "keywords", "classification", "text-analysis"],
            experimental=False
        )
    
    def setup(self) -> bool:
        """Set up the plugin"""
        try:
            self.logger.info("Setting up NLP Plugin")
            
            # Validate configuration
            if not self.validate_config(self.config):
                self.logger.error("Invalid configuration for NLP Plugin")
                return False
            
            # Initialize processor
            self.processor = NLPProcessor(self.config)
            
            self.logger.info("NLP Plugin setup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"NLP Plugin setup failed: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Clean up plugin resources"""
        try:
            self.logger.info("Cleaning up NLP Plugin")
            return True
            
        except Exception as e:
            self.logger.error(f"NLP Plugin cleanup failed: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        try:
            max_keywords = config.get('max_keywords', 50)
            if not isinstance(max_keywords, int) or not (1 <= max_keywords <= 100):
                return False
            
            keyword_method = config.get('keyword_method', 'hybrid')
            if keyword_method not in ['tfidf', 'domain', 'hybrid']:
                return False
            
            min_confidence = config.get('min_confidence', 0.3)
            if not isinstance(min_confidence, (int, float)) or not (0.0 <= min_confidence <= 1.0):
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    @plugin_hook("extract_keywords", HookPriority.HIGH, 
                "Extract keywords using NLP techniques")
    def extract_keywords_hook(self, text: str, metadata: Dict[str, Any], 
                             config: Dict[str, Any]) -> Optional[List[str]]:
        """
        Extract keywords from text
        
        Args:
            text: Document text
            metadata: Document metadata
            config: Extraction configuration
            
        Returns:
            Optional[List[str]]: Extracted keywords
        """
        if not self.is_enabled():
            return None
        
        try:
            self.logger.info("Extracting keywords using NLP plugin")
            
            # Extract keywords
            keyword_result = self.processor.extract_keywords(text, metadata)
            
            # Filter by confidence
            min_confidence = self.config.get('min_confidence', 0.3)
            if keyword_result.confidence < min_confidence:
                self.logger.warning(f"Keyword extraction confidence {keyword_result.confidence} "
                                  f"below threshold {min_confidence}")
                return None
            
            # Limit number of keywords
            max_keywords = self.config.get('max_keywords', 50)
            keywords = keyword_result.keywords[:max_keywords]
            
            self.logger.info(f"Extracted {len(keywords)} keywords with confidence "
                           f"{keyword_result.confidence:.2f}")
            
            return keywords
            
        except Exception as e:
            self.logger.error(f"Keyword extraction failed: {e}")
            return None
    
    @plugin_hook("classify_content", HookPriority.HIGH, 
                "Classify document content using NLP")
    def classify_content_hook(self, text: str, metadata: Dict[str, Any], 
                             config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Classify document content
        
        Args:
            text: Document text
            metadata: Document metadata
            config: Classification configuration
            
        Returns:
            Optional[Dict[str, Any]]: Classification results
        """
        if not self.is_enabled() or not self.config.get('enable_classification', True):
            return None
        
        try:
            self.logger.info("Classifying content using NLP plugin")
            
            # Classify content
            classification = self.processor.classify_content(text, metadata)
            
            # Check confidence threshold
            min_confidence = self.config.get('min_confidence', 0.3)
            if classification.confidence < min_confidence:
                self.logger.warning(f"Classification confidence {classification.confidence} "
                                  f"below threshold {min_confidence}")
                return None
            
            self.logger.info(f"Content classified as {classification.document_type} "
                           f"with confidence {classification.confidence:.2f}")
            
            return classification.to_dict()
            
        except Exception as e:
            self.logger.error(f"Content classification failed: {e}")
            return None
    
    @plugin_hook("enhance_metadata", HookPriority.NORMAL, 
                "Enhance metadata with NLP analysis")
    def enhance_metadata_hook(self, metadata: Dict[str, Any], 
                             config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Enhance metadata with NLP analysis
        
        Args:
            metadata: Original metadata
            config: Enhancement configuration
            
        Returns:
            Optional[Dict[str, Any]]: Enhanced metadata
        """
        if not self.is_enabled():
            return None
        
        try:
            # Get text from metadata
            text = metadata.get('text', '')
            if not text:
                return None
            
            self.logger.info("Enhancing metadata with NLP analysis")
            
            enhanced_metadata = metadata.copy()
            
            # Add keyword extraction
            keywords = self.extract_keywords_hook(text, metadata, config)
            if keywords:
                enhanced_metadata['nlp_keywords'] = keywords
            
            # Add content classification
            classification = self.classify_content_hook(text, metadata, config)
            if classification:
                enhanced_metadata['nlp_classification'] = classification
            
            # Add text quality assessment
            if self.config.get('quality_assessment', True):
                quality = self.processor.assess_text_quality(text)
                enhanced_metadata['text_quality'] = quality.to_dict()
            
            self.logger.info("Metadata enhanced with NLP analysis")
            return enhanced_metadata
            
        except Exception as e:
            self.logger.error(f"Metadata enhancement failed: {e}")
            return None
    
    @plugin_hook("analyze_structure", HookPriority.NORMAL, 
                "Analyze document structure using NLP")
    def analyze_structure_hook(self, sections: List[Dict[str, Any]], 
                              figures: List[Dict[str, Any]], 
                              tables: List[Dict[str, Any]], 
                              config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Analyze document structure
        
        Args:
            sections: Document sections
            figures: Document figures
            tables: Document tables
            config: Analysis configuration
            
        Returns:
            Optional[Dict[str, Any]]: Structure analysis results
        """
        if not self.is_enabled():
            return None
        
        try:
            self.logger.info("Analyzing document structure using NLP")
            
            # Analyze section content
            section_analysis = {}
            for i, section in enumerate(sections):
                section_text = section.get('text', '')
                if section_text:
                    # Extract keywords for this section
                    keywords = self.processor.extract_keywords(section_text, {})
                    section_analysis[f'section_{i}'] = {
                        'keywords': keywords.keywords[:10],  # Top 10 keywords
                        'complexity': self.processor.assess_text_quality(section_text).complexity_level,
                        'word_count': len(section_text.split())
                    }
            
            # Overall structure analysis
            total_words = sum(len(s.get('text', '').split()) for s in sections)
            
            structure_analysis = {
                'total_sections': len(sections),
                'total_figures': len(figures),
                'total_tables': len(tables),
                'total_words': total_words,
                'section_analysis': section_analysis,
                'document_structure_score': self._calculate_structure_score(
                    sections, figures, tables
                )
            }
            
            self.logger.info("Document structure analysis completed")
            return structure_analysis
            
        except Exception as e:
            self.logger.error(f"Structure analysis failed: {e}")
            return None
    
    def _calculate_structure_score(self, sections: List[Dict[str, Any]], 
                                 figures: List[Dict[str, Any]], 
                                 tables: List[Dict[str, Any]]) -> float:
        """Calculate document structure quality score"""
        score = 0.0
        
        # Score based on section count
        section_count = len(sections)
        if 3 <= section_count <= 10:
            score += 0.3
        elif section_count > 10:
            score += 0.2
        
        # Score based on figure/table balance
        content_count = len(figures) + len(tables)
        if content_count > 0:
            score += min(content_count * 0.05, 0.3)
        
        # Score based on section length balance
        if sections:
            word_counts = [len(s.get('text', '').split()) for s in sections]
            if word_counts:
                avg_length = sum(word_counts) / len(word_counts)
                variance = sum((count - avg_length) ** 2 for count in word_counts) / len(word_counts)
                if variance < avg_length:  # Low variance indicates balanced sections
                    score += 0.2
        
        return min(score, 1.0)


# Plugin instance for loading
plugin_instance = NLPPlugin 
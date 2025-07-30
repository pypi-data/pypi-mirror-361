"""
Comprehensive tests for citation network analysis functionality.
"""

import unittest
import tempfile
import os
import json
from unittest.mock import patch, MagicMock
from datetime import datetime

from paper2data.citation_network_analyzer import (
    CitationNetworkAnalyzer, NetworkNode, NetworkEdge, NetworkMetrics,
    AuthorMetrics, CitationInfluence, NetworkType, CentralityMetric,
    build_citation_network, analyze_citation_networks
)


class TestNetworkNode(unittest.TestCase):
    """Test NetworkNode dataclass"""
    
    def test_network_node_creation(self):
        """Test basic network node creation"""
        node = NetworkNode(
            node_id="paper_1",
            node_type="paper",
            title="Test Paper",
            authors=["John Doe", "Jane Smith"],
            year=2023,
            journal="Test Journal",
            doi="10.1234/test",
            keywords=["test", "paper"]
        )
        
        self.assertEqual(node.node_id, "paper_1")
        self.assertEqual(node.node_type, "paper")
        self.assertEqual(node.title, "Test Paper")
        self.assertEqual(node.authors, ["John Doe", "Jane Smith"])
        self.assertEqual(node.year, 2023)
        self.assertEqual(node.journal, "Test Journal")
        self.assertEqual(node.doi, "10.1234/test")
        self.assertEqual(node.keywords, ["test", "paper"])
    
    def test_network_node_to_dict(self):
        """Test network node to dictionary conversion"""
        node = NetworkNode(
            node_id="paper_1",
            node_type="paper",
            title="Test Paper"
        )
        
        data = node.to_dict()
        self.assertEqual(data["node_id"], "paper_1")
        self.assertEqual(data["node_type"], "paper")
        self.assertEqual(data["title"], "Test Paper")


class TestNetworkEdge(unittest.TestCase):
    """Test NetworkEdge dataclass"""
    
    def test_network_edge_creation(self):
        """Test basic network edge creation"""
        edge = NetworkEdge(
            source="paper_1",
            target="paper_2",
            edge_type="citation",
            weight=1.0,
            year=2023,
            context="This paper cites..."
        )
        
        self.assertEqual(edge.source, "paper_1")
        self.assertEqual(edge.target, "paper_2")
        self.assertEqual(edge.edge_type, "citation")
        self.assertEqual(edge.weight, 1.0)
        self.assertEqual(edge.year, 2023)
        self.assertEqual(edge.context, "This paper cites...")
    
    def test_network_edge_to_dict(self):
        """Test network edge to dictionary conversion"""
        edge = NetworkEdge(
            source="paper_1",
            target="paper_2",
            edge_type="citation"
        )
        
        data = edge.to_dict()
        self.assertEqual(data["source"], "paper_1")
        self.assertEqual(data["target"], "paper_2")
        self.assertEqual(data["edge_type"], "citation")


class TestNetworkMetrics(unittest.TestCase):
    """Test NetworkMetrics dataclass"""
    
    def test_network_metrics_creation(self):
        """Test basic network metrics creation"""
        metrics = NetworkMetrics(
            num_nodes=10,
            num_edges=15,
            density=0.3,
            is_connected=True,
            num_components=1
        )
        
        self.assertEqual(metrics.num_nodes, 10)
        self.assertEqual(metrics.num_edges, 15)
        self.assertEqual(metrics.density, 0.3)
        self.assertTrue(metrics.is_connected)
        self.assertEqual(metrics.num_components, 1)
    
    def test_network_metrics_to_dict(self):
        """Test network metrics to dictionary conversion"""
        metrics = NetworkMetrics(
            num_nodes=5,
            num_edges=8,
            density=0.4
        )
        
        data = metrics.to_dict()
        self.assertEqual(data["num_nodes"], 5)
        self.assertEqual(data["num_edges"], 8)
        self.assertEqual(data["density"], 0.4)


class TestAuthorMetrics(unittest.TestCase):
    """Test AuthorMetrics dataclass"""
    
    def test_author_metrics_creation(self):
        """Test basic author metrics creation"""
        metrics = AuthorMetrics(
            author_name="John Doe",
            paper_count=5,
            total_citations=25,
            h_index=3,
            collaboration_count=8,
            unique_coauthors={"Jane Smith", "Mike Johnson"}
        )
        
        self.assertEqual(metrics.author_name, "John Doe")
        self.assertEqual(metrics.paper_count, 5)
        self.assertEqual(metrics.total_citations, 25)
        self.assertEqual(metrics.h_index, 3)
        self.assertEqual(metrics.collaboration_count, 8)
        self.assertEqual(len(metrics.unique_coauthors), 2)
    
    def test_author_metrics_to_dict(self):
        """Test author metrics to dictionary conversion"""
        metrics = AuthorMetrics(
            author_name="John Doe",
            unique_coauthors={"Jane Smith", "Mike Johnson"}
        )
        
        data = metrics.to_dict()
        self.assertEqual(data["author_name"], "John Doe")
        self.assertIsInstance(data["unique_coauthors"], list)
        self.assertEqual(len(data["unique_coauthors"]), 2)


class TestCitationInfluence(unittest.TestCase):
    """Test CitationInfluence dataclass"""
    
    def test_citation_influence_creation(self):
        """Test basic citation influence creation"""
        influence = CitationInfluence(
            paper_id="paper_1",
            direct_citations=5,
            indirect_citations=12,
            influence_score=8.5,
            citation_generations={1: 5, 2: 7, 3: 3}
        )
        
        self.assertEqual(influence.paper_id, "paper_1")
        self.assertEqual(influence.direct_citations, 5)
        self.assertEqual(influence.indirect_citations, 12)
        self.assertEqual(influence.influence_score, 8.5)
        self.assertEqual(len(influence.citation_generations), 3)
    
    def test_citation_influence_to_dict(self):
        """Test citation influence to dictionary conversion"""
        influence = CitationInfluence(
            paper_id="paper_1",
            direct_citations=3
        )
        
        data = influence.to_dict()
        self.assertEqual(data["paper_id"], "paper_1")
        self.assertEqual(data["direct_citations"], 3)


class TestCitationNetworkAnalyzer(unittest.TestCase):
    """Test CitationNetworkAnalyzer class"""
    
    def setUp(self):
        """Set up test fixtures"""
        self.analyzer = CitationNetworkAnalyzer()
        
        # Create sample papers metadata
        self.sample_papers = [
            {
                "title": "Machine Learning Fundamentals",
                "authors": [{"name": "John Doe"}, {"name": "Jane Smith"}],
                "publication_info": {"year": 2020, "journal": "AI Review"},
                "doi": "10.1234/ml.fundamentals",
                "keywords": ["machine learning", "AI"],
                "citations": [
                    {
                        "text": "Neural Networks by Smith (2018)",
                        "title": "Neural Networks",
                        "authors": ["Smith"],
                        "year": 2018,
                        "doi": "10.1234/nn.2018"
                    }
                ]
            },
            {
                "title": "Deep Learning Applications",
                "authors": [{"name": "Mike Johnson"}, {"name": "John Doe"}],
                "publication_info": {"year": 2021, "journal": "ML Journal"},
                "doi": "10.1234/dl.applications",
                "keywords": ["deep learning", "applications"],
                "citations": [
                    {
                        "text": "Machine Learning Fundamentals by Doe (2020)",
                        "title": "Machine Learning Fundamentals",
                        "authors": ["Doe"],
                        "year": 2020,
                        "doi": "10.1234/ml.fundamentals"
                    }
                ]
            },
            {
                "title": "Neural Networks",
                "authors": [{"name": "Smith"}],
                "publication_info": {"year": 2018, "journal": "Neural Computing"},
                "doi": "10.1234/nn.2018",
                "keywords": ["neural networks", "deep learning"],
                "citations": []
            }
        ]
    
    def test_analyzer_initialization(self):
        """Test analyzer initialization"""
        self.assertIsInstance(self.analyzer.networks, dict)
        self.assertIsInstance(self.analyzer.metadata_cache, dict)
        self.assertIsInstance(self.analyzer.analysis_cache, dict)
        self.assertEqual(self.analyzer.cocitation_threshold, 2)
        self.assertEqual(self.analyzer.coupling_threshold, 2)
        self.assertEqual(self.analyzer.collaboration_threshold, 1)
    
    def test_generate_paper_id(self):
        """Test paper ID generation"""
        paper = {
            "title": "Test Paper",
            "authors": [{"name": "John Doe"}],
            "publication_info": {"year": 2023},
            "doi": "10.1234/test"
        }
        
        paper_id = self.analyzer._generate_paper_id(paper)
        self.assertTrue(paper_id.startswith("doi:"))
        self.assertIn("10.1234/test", paper_id)
        
        # Test without DOI
        paper_no_doi = {
            "title": "Test Paper",
            "authors": [{"name": "John Doe"}],
            "publication_info": {"year": 2023}
        }
        
        paper_id_no_doi = self.analyzer._generate_paper_id(paper_no_doi)
        self.assertTrue(paper_id_no_doi.startswith("paper:"))
    
    def test_extract_author_names(self):
        """Test author name extraction"""
        # Test with dictionaries
        authors_dict = [{"name": "John Doe"}, {"name": "Jane Smith"}]
        names = self.analyzer._extract_author_names(authors_dict)
        self.assertEqual(names, ["John Doe", "Jane Smith"])
        
        # Test with strings
        authors_str = ["John Doe", "Jane Smith"]
        names = self.analyzer._extract_author_names(authors_str)
        self.assertEqual(names, ["John Doe", "Jane Smith"])
        
        # Test with mixed types
        authors_mixed = [{"name": "John Doe"}, "Jane Smith", 123]
        names = self.analyzer._extract_author_names(authors_mixed)
        self.assertEqual(names, ["John Doe", "Jane Smith", "123"])
    
    def test_find_cited_paper_id(self):
        """Test cited paper ID finding"""
        citation = {
            "title": "Machine Learning Fundamentals",
            "authors": ["Doe"],
            "year": 2020,
            "doi": "10.1234/ml.fundamentals"
        }
        
        cited_id = self.analyzer._find_cited_paper_id(citation, self.sample_papers)
        self.assertIsNotNone(cited_id)
        self.assertTrue("10.1234/ml.fundamentals" in cited_id)
    
    def test_build_citation_network(self):
        """Test citation network construction"""
        network = self.analyzer.build_citation_network(self.sample_papers)
        
        # Check network properties
        self.assertEqual(network.number_of_nodes(), 3)
        self.assertTrue(network.is_directed())
        self.assertGreater(network.number_of_edges(), 0)
        
        # Check network is stored
        self.assertIn(NetworkType.CITATION, self.analyzer.networks)
        
        # Check node attributes
        for node_id, data in network.nodes(data=True):
            self.assertIn("node_type", data)
            self.assertEqual(data["node_type"], "paper")
            self.assertIn("title", data)
    
    def test_build_cocitation_network(self):
        """Test co-citation network construction"""
        # First build citation network
        citation_network = self.analyzer.build_citation_network(self.sample_papers)
        
        # Build co-citation network
        cocitation_network = self.analyzer.build_cocitation_network(citation_network)
        
        # Check network properties
        self.assertFalse(cocitation_network.is_directed())
        self.assertEqual(cocitation_network.number_of_nodes(), citation_network.number_of_nodes())
        
        # Check network is stored
        self.assertIn(NetworkType.COCITATION, self.analyzer.networks)
    
    def test_build_bibliographic_coupling_network(self):
        """Test bibliographic coupling network construction"""
        # First build citation network
        citation_network = self.analyzer.build_citation_network(self.sample_papers)
        
        # Build bibliographic coupling network
        coupling_network = self.analyzer.build_bibliographic_coupling_network(citation_network)
        
        # Check network properties
        self.assertFalse(coupling_network.is_directed())
        self.assertEqual(coupling_network.number_of_nodes(), citation_network.number_of_nodes())
        
        # Check network is stored
        self.assertIn(NetworkType.BIBLIOGRAPHIC_COUPLING, self.analyzer.networks)
    
    def test_build_author_collaboration_network(self):
        """Test author collaboration network construction"""
        network = self.analyzer.build_author_collaboration_network(self.sample_papers)
        
        # Check network properties
        self.assertFalse(network.is_directed())
        self.assertGreater(network.number_of_nodes(), 0)
        
        # Check network is stored
        self.assertIn(NetworkType.AUTHOR_COLLABORATION, self.analyzer.networks)
        
        # Check node attributes
        for node_id, data in network.nodes(data=True):
            self.assertIn("node_type", data)
            self.assertEqual(data["node_type"], "author")
    
    def test_build_keyword_cooccurrence_network(self):
        """Test keyword co-occurrence network construction"""
        network = self.analyzer.build_keyword_cooccurrence_network(self.sample_papers)
        
        # Check network properties
        self.assertFalse(network.is_directed())
        self.assertGreater(network.number_of_nodes(), 0)
        
        # Check network is stored
        self.assertIn(NetworkType.KEYWORD_COOCCURRENCE, self.analyzer.networks)
        
        # Check node attributes
        for node_id, data in network.nodes(data=True):
            self.assertIn("node_type", data)
            self.assertEqual(data["node_type"], "keyword")
    
    def test_calculate_network_metrics(self):
        """Test network metrics calculation"""
        network = self.analyzer.build_citation_network(self.sample_papers)
        metrics = self.analyzer.calculate_network_metrics(network, NetworkType.CITATION)
        
        # Check basic metrics
        self.assertEqual(metrics.num_nodes, network.number_of_nodes())
        self.assertEqual(metrics.num_edges, network.number_of_edges())
        self.assertGreaterEqual(metrics.density, 0.0)
        self.assertLessEqual(metrics.density, 1.0)
        self.assertIsInstance(metrics.is_connected, bool)
        self.assertGreaterEqual(metrics.num_components, 1)
    
    def test_calculate_centrality_metrics(self):
        """Test centrality metrics calculation"""
        network = self.analyzer.build_citation_network(self.sample_papers)
        
        # Test with default metrics
        centrality = self.analyzer.calculate_centrality_metrics(network)
        
        # Check that some metrics are calculated
        self.assertIn("degree", centrality)
        self.assertIn("pagerank", centrality)
        
        # Check that all nodes have scores
        for metric, scores in centrality.items():
            self.assertEqual(len(scores), network.number_of_nodes())
            for node_id, score in scores.items():
                self.assertIsInstance(score, (int, float))
    
    def test_analyze_author_metrics(self):
        """Test author metrics analysis"""
        author_metrics = self.analyzer.analyze_author_metrics(self.sample_papers)
        
        # Check that metrics are calculated for each author
        self.assertGreater(len(author_metrics), 0)
        
        for author_name, metrics in author_metrics.items():
            self.assertIsInstance(metrics, AuthorMetrics)
            self.assertEqual(metrics.author_name, author_name)
            self.assertGreaterEqual(metrics.paper_count, 0)
            self.assertGreaterEqual(metrics.total_citations, 0)
            self.assertGreaterEqual(metrics.h_index, 0)
    
    def test_analyze_citation_influence(self):
        """Test citation influence analysis"""
        network = self.analyzer.build_citation_network(self.sample_papers)
        influence_data = self.analyzer.analyze_citation_influence(network)
        
        # Check that influence is calculated for each paper
        self.assertEqual(len(influence_data), network.number_of_nodes())
        
        for paper_id, influence in influence_data.items():
            self.assertIsInstance(influence, CitationInfluence)
            self.assertEqual(influence.paper_id, paper_id)
            self.assertGreaterEqual(influence.direct_citations, 0)
            self.assertGreaterEqual(influence.influence_score, 0.0)
    
    def test_export_network(self):
        """Test network export functionality"""
        network = self.analyzer.build_citation_network(self.sample_papers)
        
        # Test JSON export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name
        
        try:
            success = self.analyzer.export_network(NetworkType.CITATION, json_path, 'json')
            self.assertTrue(success)
            self.assertTrue(os.path.exists(json_path))
            
            # Verify file content
            with open(json_path, 'r') as f:
                data = json.load(f)
                self.assertIn("nodes", data)
                self.assertIn("links", data)
        finally:
            if os.path.exists(json_path):
                os.unlink(json_path)
    
    def test_generate_network_summary(self):
        """Test network summary generation"""
        network = self.analyzer.build_citation_network(self.sample_papers)
        summary = self.analyzer.generate_network_summary(NetworkType.CITATION)
        
        # Check summary structure
        self.assertIn("network_type", summary)
        self.assertEqual(summary["network_type"], "citation")
        self.assertIn("timestamp", summary)
        self.assertIn("basic_metrics", summary)
        self.assertIn("centrality_metrics", summary)
        self.assertIn("top_nodes", summary)
        self.assertIn("network_structure", summary)
        self.assertIn("recommendations", summary)
    
    def test_error_handling(self):
        """Test error handling with invalid data"""
        # Test with empty papers list
        empty_network = self.analyzer.build_citation_network([])
        self.assertEqual(empty_network.number_of_nodes(), 0)
        self.assertEqual(empty_network.number_of_edges(), 0)
        
        # Test with malformed paper data
        malformed_papers = [{"invalid": "data"}]
        malformed_network = self.analyzer.build_citation_network(malformed_papers)
        self.assertEqual(malformed_network.number_of_nodes(), 1)  # Should still create node
    
    def test_thresholds_configuration(self):
        """Test configurable thresholds"""
        # Test changing thresholds
        self.analyzer.cocitation_threshold = 1
        self.analyzer.coupling_threshold = 1
        self.analyzer.collaboration_threshold = 2
        
        self.assertEqual(self.analyzer.cocitation_threshold, 1)
        self.assertEqual(self.analyzer.coupling_threshold, 1)
        self.assertEqual(self.analyzer.collaboration_threshold, 2)


class TestGlobalFunctions(unittest.TestCase):
    """Test global functions"""
    
    def test_build_citation_network_function(self):
        """Test global build_citation_network function"""
        papers = [
            {
                "title": "Test Paper",
                "authors": [{"name": "John Doe"}],
                "publication_info": {"year": 2023},
                "citations": []
            }
        ]
        
        network = build_citation_network(papers)
        self.assertEqual(network.number_of_nodes(), 1)
        self.assertTrue(network.is_directed())
    
    def test_analyze_citation_networks_function(self):
        """Test global analyze_citation_networks function"""
        papers = [
            {
                "title": "Test Paper",
                "authors": [{"name": "John Doe"}],
                "publication_info": {"year": 2023},
                "keywords": ["test"],
                "citations": []
            }
        ]
        
        results = analyze_citation_networks(papers)
        
        # Check results structure
        self.assertIn("networks", results)
        self.assertIn("author_analysis", results)
        self.assertIn("influence_analysis", results)
        self.assertIn("analysis_timestamp", results)
        self.assertIn("total_papers_analyzed", results)
        self.assertEqual(results["total_papers_analyzed"], 1)


class TestEnumTypes(unittest.TestCase):
    """Test enum types"""
    
    def test_network_type_enum(self):
        """Test NetworkType enum"""
        self.assertEqual(NetworkType.CITATION.value, "citation")
        self.assertEqual(NetworkType.COCITATION.value, "cocitation")
        self.assertEqual(NetworkType.BIBLIOGRAPHIC_COUPLING.value, "bibliographic_coupling")
        self.assertEqual(NetworkType.AUTHOR_COLLABORATION.value, "author_collaboration")
        self.assertEqual(NetworkType.KEYWORD_COOCCURRENCE.value, "keyword_cooccurrence")
    
    def test_centrality_metric_enum(self):
        """Test CentralityMetric enum"""
        self.assertEqual(CentralityMetric.DEGREE.value, "degree")
        self.assertEqual(CentralityMetric.BETWEENNESS.value, "betweenness")
        self.assertEqual(CentralityMetric.CLOSENESS.value, "closeness")
        self.assertEqual(CentralityMetric.EIGENVECTOR.value, "eigenvector")
        self.assertEqual(CentralityMetric.PAGERANK.value, "pagerank")
        self.assertEqual(CentralityMetric.KATZ.value, "katz")


if __name__ == '__main__':
    unittest.main() 
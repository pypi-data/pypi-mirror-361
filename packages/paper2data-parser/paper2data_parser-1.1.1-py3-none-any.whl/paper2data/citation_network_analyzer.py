"""
Citation Network Analysis for Paper2Data

This module provides comprehensive citation network analysis capabilities including
network construction, graph metrics, bibliometric analysis, citation influence
measurement, and network visualization.
"""

import re
import json
import logging
import networkx as nx
import numpy as np
from typing import Dict, List, Any, Optional, Tuple, Set, Union
from dataclasses import dataclass, field, asdict
from datetime import datetime
from enum import Enum
from collections import defaultdict, Counter
import tempfile
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class NetworkType(Enum):
    """Types of citation networks"""
    CITATION = "citation"  # Direct citation relationships
    COCITATION = "cocitation"  # Papers cited together
    BIBLIOGRAPHIC_COUPLING = "bibliographic_coupling"  # Papers citing same sources
    AUTHOR_COLLABORATION = "author_collaboration"  # Author collaboration network
    KEYWORD_COOCCURRENCE = "keyword_cooccurrence"  # Keyword co-occurrence network

class CentralityMetric(Enum):
    """Centrality metrics for network analysis"""
    DEGREE = "degree"
    BETWEENNESS = "betweenness"
    CLOSENESS = "closeness"
    EIGENVECTOR = "eigenvector"
    PAGERANK = "pagerank"
    KATZ = "katz"

@dataclass
class NetworkNode:
    """Represents a node in the citation network"""
    node_id: str
    node_type: str  # paper, author, keyword, etc.
    title: Optional[str] = None
    authors: List[str] = field(default_factory=list)
    year: Optional[int] = None
    journal: Optional[str] = None
    doi: Optional[str] = None
    keywords: List[str] = field(default_factory=list)
    
    # Network metrics
    degree: int = 0
    in_degree: int = 0
    out_degree: int = 0
    betweenness_centrality: float = 0.0
    closeness_centrality: float = 0.0
    eigenvector_centrality: float = 0.0
    pagerank: float = 0.0
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

@dataclass
class NetworkEdge:
    """Represents an edge in the citation network"""
    source: str
    target: str
    edge_type: str  # citation, cocitation, collaboration, etc.
    weight: float = 1.0
    year: Optional[int] = None
    context: Optional[str] = None  # Citation context
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

@dataclass
class NetworkMetrics:
    """Comprehensive network analysis metrics"""
    # Basic network properties
    num_nodes: int = 0
    num_edges: int = 0
    density: float = 0.0
    is_connected: bool = False
    num_components: int = 0
    
    # Clustering metrics
    average_clustering: float = 0.0
    global_clustering: float = 0.0
    
    # Path metrics
    average_shortest_path: Optional[float] = None
    diameter: Optional[int] = None
    radius: Optional[int] = None
    
    # Centralization metrics
    degree_centralization: float = 0.0
    betweenness_centralization: float = 0.0
    closeness_centralization: float = 0.0
    
    # Community metrics
    num_communities: int = 0
    modularity: float = 0.0
    
    # Citation-specific metrics
    average_citations_per_paper: float = 0.0
    most_cited_papers: List[str] = field(default_factory=list)
    citation_distribution: Dict[str, int] = field(default_factory=dict)
    
    # Temporal metrics
    network_age: Optional[int] = None  # Years from oldest to newest paper
    citation_velocity: float = 0.0  # Citations per year
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

@dataclass
class AuthorMetrics:
    """Author-specific metrics in citation network"""
    author_name: str
    paper_count: int = 0
    total_citations: int = 0
    h_index: int = 0
    average_citations_per_paper: float = 0.0
    collaboration_count: int = 0
    unique_coauthors: Set[str] = field(default_factory=set)
    publication_years: List[int] = field(default_factory=list)
    research_areas: List[str] = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['unique_coauthors'] = list(self.unique_coauthors)
        return data

@dataclass
class CitationInfluence:
    """Citation influence analysis"""
    paper_id: str
    direct_citations: int = 0
    indirect_citations: int = 0  # Citations to papers that cite this paper
    citation_generations: Dict[int, int] = field(default_factory=dict)  # Generation -> count
    influence_score: float = 0.0
    temporal_influence: Dict[int, int] = field(default_factory=dict)  # Year -> citations
    field_influence: Dict[str, int] = field(default_factory=dict)  # Research area -> citations
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization"""
        return asdict(self)

class CitationNetworkAnalyzer:
    """Comprehensive citation network analysis"""
    
    def __init__(self):
        """Initialize the citation network analyzer"""
        self.networks = {}  # Store different types of networks
        self.metadata_cache = {}  # Cache paper metadata
        self.analysis_cache = {}  # Cache analysis results
        
        # Analysis parameters
        self.cocitation_threshold = 2  # Minimum co-citations for edge
        self.coupling_threshold = 2  # Minimum shared references for edge
        self.collaboration_threshold = 1  # Minimum collaborations for edge
        
    def build_citation_network(self, papers_metadata: List[Dict[str, Any]]) -> nx.DiGraph:
        """Build directed citation network from papers metadata"""
        logger.info(f"Building citation network from {len(papers_metadata)} papers")
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Cache metadata for quick lookup
        for paper in papers_metadata:
            paper_id = self._generate_paper_id(paper)
            self.metadata_cache[paper_id] = paper
        
        # Add nodes for all papers
        for paper in papers_metadata:
            paper_id = self._generate_paper_id(paper)
            
            # Create node with metadata
            node = NetworkNode(
                node_id=paper_id,
                node_type="paper",
                title=paper.get('title', ''),
                authors=paper.get('authors', []),
                year=paper.get('publication_info', {}).get('year'),
                journal=paper.get('publication_info', {}).get('journal'),
                doi=paper.get('doi'),
                keywords=paper.get('keywords', [])
            )
            
            G.add_node(paper_id, **node.to_dict())
        
        # Add citation edges
        citation_count = 0
        for paper in papers_metadata:
            paper_id = self._generate_paper_id(paper)
            citations = paper.get('citations', [])
            
            for citation in citations:
                cited_paper_id = self._find_cited_paper_id(citation, papers_metadata)
                if cited_paper_id and cited_paper_id in G.nodes:
                    # Create citation edge
                    edge = NetworkEdge(
                        source=paper_id,
                        target=cited_paper_id,
                        edge_type="citation",
                        year=citation.get('year'),
                        context=citation.get('text', '')[:200]  # First 200 chars
                    )
                    
                    G.add_edge(paper_id, cited_paper_id, **edge.to_dict())
                    citation_count += 1
        
        logger.info(f"Built citation network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Store network
        self.networks[NetworkType.CITATION] = G
        return G
    
    def build_cocitation_network(self, citation_network: Optional[nx.DiGraph] = None) -> nx.Graph:
        """Build co-citation network (papers cited together)"""
        if citation_network is None:
            citation_network = self.networks.get(NetworkType.CITATION)
            if citation_network is None:
                raise ValueError("No citation network available. Build citation network first.")
        
        logger.info("Building co-citation network")
        
        # Create undirected graph
        G = nx.Graph()
        
        # Add all nodes from citation network
        for node_id, data in citation_network.nodes(data=True):
            G.add_node(node_id, **data)
        
        # Find co-citations
        cocitation_counts = defaultdict(int)
        
        # For each paper, find what it cites
        for citing_paper in citation_network.nodes():
            cited_papers = list(citation_network.successors(citing_paper))
            
            # Create co-citation edges between cited papers
            for i, paper1 in enumerate(cited_papers):
                for paper2 in cited_papers[i+1:]:
                    pair = tuple(sorted([paper1, paper2]))
                    cocitation_counts[pair] += 1
        
        # Add edges above threshold
        edge_count = 0
        for (paper1, paper2), count in cocitation_counts.items():
            if count >= self.cocitation_threshold:
                edge = NetworkEdge(
                    source=paper1,
                    target=paper2,
                    edge_type="cocitation",
                    weight=count
                )
                G.add_edge(paper1, paper2, **edge.to_dict())
                edge_count += 1
        
        logger.info(f"Built co-citation network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Store network
        self.networks[NetworkType.COCITATION] = G
        return G
    
    def build_bibliographic_coupling_network(self, citation_network: Optional[nx.DiGraph] = None) -> nx.Graph:
        """Build bibliographic coupling network (papers citing same sources)"""
        if citation_network is None:
            citation_network = self.networks.get(NetworkType.CITATION)
            if citation_network is None:
                raise ValueError("No citation network available. Build citation network first.")
        
        logger.info("Building bibliographic coupling network")
        
        # Create undirected graph
        G = nx.Graph()
        
        # Add all nodes from citation network
        for node_id, data in citation_network.nodes(data=True):
            G.add_node(node_id, **data)
        
        # Find bibliographic coupling
        coupling_counts = defaultdict(int)
        
        # For each pair of papers, count shared references
        papers = list(citation_network.nodes())
        for i, paper1 in enumerate(papers):
            cited_by_paper1 = set(citation_network.successors(paper1))
            
            for paper2 in papers[i+1:]:
                cited_by_paper2 = set(citation_network.successors(paper2))
                
                # Count shared references
                shared_references = len(cited_by_paper1.intersection(cited_by_paper2))
                if shared_references >= self.coupling_threshold:
                    coupling_counts[(paper1, paper2)] = shared_references
        
        # Add edges above threshold
        edge_count = 0
        for (paper1, paper2), count in coupling_counts.items():
            edge = NetworkEdge(
                source=paper1,
                target=paper2,
                edge_type="bibliographic_coupling",
                weight=count
            )
            G.add_edge(paper1, paper2, **edge.to_dict())
            edge_count += 1
        
        logger.info(f"Built bibliographic coupling network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Store network
        self.networks[NetworkType.BIBLIOGRAPHIC_COUPLING] = G
        return G
    
    def build_author_collaboration_network(self, papers_metadata: List[Dict[str, Any]]) -> nx.Graph:
        """Build author collaboration network"""
        logger.info("Building author collaboration network")
        
        # Create undirected graph
        G = nx.Graph()
        
        # Track author collaborations
        collaboration_counts = defaultdict(int)
        author_papers = defaultdict(list)
        author_years = defaultdict(list)
        
        # Process each paper
        for paper in papers_metadata:
            authors = self._extract_author_names(paper.get('authors', []))
            year = paper.get('publication_info', {}).get('year')
            paper_id = self._generate_paper_id(paper)
            
            # Track author-paper relationships
            for author in authors:
                author_papers[author].append(paper_id)
                if year:
                    author_years[author].append(year)
            
            # Create collaboration edges
            for i, author1 in enumerate(authors):
                for author2 in authors[i+1:]:
                    pair = tuple(sorted([author1, author2]))
                    collaboration_counts[pair] += 1
        
        # Add author nodes
        for author in author_papers.keys():
            node = NetworkNode(
                node_id=author,
                node_type="author",
                title=author  # Use author name as title
            )
            G.add_node(author, **node.to_dict())
        
        # Add collaboration edges
        edge_count = 0
        for (author1, author2), count in collaboration_counts.items():
            if count >= self.collaboration_threshold:
                edge = NetworkEdge(
                    source=author1,
                    target=author2,
                    edge_type="collaboration",
                    weight=count
                )
                G.add_edge(author1, author2, **edge.to_dict())
                edge_count += 1
        
        logger.info(f"Built author collaboration network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Store network
        self.networks[NetworkType.AUTHOR_COLLABORATION] = G
        return G
    
    def build_keyword_cooccurrence_network(self, papers_metadata: List[Dict[str, Any]]) -> nx.Graph:
        """Build keyword co-occurrence network"""
        logger.info("Building keyword co-occurrence network")
        
        # Create undirected graph
        G = nx.Graph()
        
        # Track keyword co-occurrences
        cooccurrence_counts = defaultdict(int)
        keyword_papers = defaultdict(list)
        
        # Process each paper
        for paper in papers_metadata:
            keywords = paper.get('keywords', [])
            paper_id = self._generate_paper_id(paper)
            
            # Clean and normalize keywords
            normalized_keywords = []
            for keyword in keywords:
                if isinstance(keyword, str):
                    normalized = keyword.lower().strip()
                    if len(normalized) > 2:  # Filter very short keywords
                        normalized_keywords.append(normalized)
                        keyword_papers[normalized].append(paper_id)
            
            # Create co-occurrence edges
            for i, kw1 in enumerate(normalized_keywords):
                for kw2 in normalized_keywords[i+1:]:
                    pair = tuple(sorted([kw1, kw2]))
                    cooccurrence_counts[pair] += 1
        
        # Add keyword nodes
        for keyword in keyword_papers.keys():
            node = NetworkNode(
                node_id=keyword,
                node_type="keyword",
                title=keyword
            )
            G.add_node(keyword, **node.to_dict())
        
        # Add co-occurrence edges (minimum 2 co-occurrences)
        edge_count = 0
        for (kw1, kw2), count in cooccurrence_counts.items():
            if count >= 2:
                edge = NetworkEdge(
                    source=kw1,
                    target=kw2,
                    edge_type="cooccurrence",
                    weight=count
                )
                G.add_edge(kw1, kw2, **edge.to_dict())
                edge_count += 1
        
        logger.info(f"Built keyword co-occurrence network: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges")
        
        # Store network
        self.networks[NetworkType.KEYWORD_COOCCURRENCE] = G
        return G
    
    def calculate_network_metrics(self, network: nx.Graph, network_type: NetworkType) -> NetworkMetrics:
        """Calculate comprehensive network metrics"""
        logger.info(f"Calculating metrics for {network_type.value} network")
        
        metrics = NetworkMetrics()
        
        # Basic properties
        metrics.num_nodes = network.number_of_nodes()
        metrics.num_edges = network.number_of_edges()
        
        if metrics.num_nodes > 1:
            metrics.density = nx.density(network)
            metrics.is_connected = nx.is_connected(network) if not network.is_directed() else nx.is_weakly_connected(network)
            metrics.num_components = nx.number_connected_components(network) if not network.is_directed() else nx.number_weakly_connected_components(network)
        
        # Clustering metrics (for undirected networks)
        if not network.is_directed() and metrics.num_nodes > 2:
            try:
                metrics.average_clustering = nx.average_clustering(network)
                metrics.global_clustering = nx.transitivity(network)
            except:
                pass
        
        # Path metrics (only for connected networks)
        if metrics.is_connected and metrics.num_nodes > 1:
            try:
                if network.is_directed():
                    # Use weakly connected component
                    largest_cc = max(nx.weakly_connected_components(network), key=len)
                    subgraph = network.subgraph(largest_cc)
                else:
                    largest_cc = max(nx.connected_components(network), key=len)
                    subgraph = network.subgraph(largest_cc)
                
                if len(largest_cc) > 1:
                    if not network.is_directed():
                        metrics.average_shortest_path = nx.average_shortest_path_length(subgraph)
                        metrics.diameter = nx.diameter(subgraph)
                        metrics.radius = nx.radius(subgraph)
            except:
                pass
        
        # Centralization metrics
        if metrics.num_nodes > 2:
            try:
                # Degree centralization
                degrees = dict(network.degree())
                max_degree = max(degrees.values()) if degrees else 0
                degree_sum = sum(max_degree - d for d in degrees.values())
                max_possible = (metrics.num_nodes - 1) * (metrics.num_nodes - 2)
                if max_possible > 0:
                    metrics.degree_centralization = degree_sum / max_possible
                
                # Betweenness centralization
                if not network.is_directed():
                    betweenness = nx.betweenness_centrality(network)
                    max_betweenness = max(betweenness.values()) if betweenness else 0
                    betweenness_sum = sum(max_betweenness - b for b in betweenness.values())
                    max_possible_betweenness = (metrics.num_nodes - 1) * (metrics.num_nodes - 2) / 2
                    if max_possible_betweenness > 0:
                        metrics.betweenness_centralization = betweenness_sum / max_possible_betweenness
            except:
                pass
        
        # Community detection
        if not network.is_directed() and metrics.num_edges > 0:
            try:
                import networkx.algorithms.community as nx_comm
                communities = list(nx_comm.greedy_modularity_communities(network))
                metrics.num_communities = len(communities)
                metrics.modularity = nx_comm.modularity(network, communities)
            except:
                pass
        
        # Citation-specific metrics
        if network_type == NetworkType.CITATION:
            self._calculate_citation_metrics(network, metrics)
        
        # Temporal metrics
        self._calculate_temporal_metrics(network, metrics)
        
        return metrics
    
    def calculate_centrality_metrics(self, network: nx.Graph, 
                                   metrics: List[CentralityMetric] = None) -> Dict[str, Dict[str, float]]:
        """Calculate centrality metrics for all nodes"""
        if metrics is None:
            metrics = [CentralityMetric.DEGREE, CentralityMetric.BETWEENNESS, 
                      CentralityMetric.CLOSENESS, CentralityMetric.PAGERANK]
        
        logger.info(f"Calculating centrality metrics: {[m.value for m in metrics]}")
        
        results = {}
        
        try:
            if CentralityMetric.DEGREE in metrics:
                if network.is_directed():
                    results['in_degree'] = dict(network.in_degree())
                    results['out_degree'] = dict(network.out_degree())
                results['degree'] = dict(network.degree())
            
            if CentralityMetric.BETWEENNESS in metrics:
                results['betweenness'] = nx.betweenness_centrality(network)
            
            if CentralityMetric.CLOSENESS in metrics:
                if nx.is_connected(network) or (network.is_directed() and nx.is_weakly_connected(network)):
                    results['closeness'] = nx.closeness_centrality(network)
            
            if CentralityMetric.EIGENVECTOR in metrics and not network.is_directed():
                try:
                    results['eigenvector'] = nx.eigenvector_centrality(network)
                except:
                    pass
            
            if CentralityMetric.PAGERANK in metrics:
                results['pagerank'] = nx.pagerank(network)
            
            if CentralityMetric.KATZ in metrics and not network.is_directed():
                try:
                    results['katz'] = nx.katz_centrality(network)
                except:
                    pass
        
        except Exception as e:
            logger.warning(f"Error calculating centrality metrics: {e}")
        
        return results
    
    def analyze_author_metrics(self, papers_metadata: List[Dict[str, Any]]) -> Dict[str, AuthorMetrics]:
        """Analyze author-specific metrics"""
        logger.info("Analyzing author metrics")
        
        author_data = defaultdict(lambda: {
            'papers': [],
            'citations': [],
            'coauthors': set(),
            'years': [],
            'keywords': []
        })
        
        # Collect author data
        for paper in papers_metadata:
            authors = self._extract_author_names(paper.get('authors', []))
            year = paper.get('publication_info', {}).get('year')
            keywords = paper.get('keywords', [])
            paper_citations = len(paper.get('citations', []))
            paper_id = self._generate_paper_id(paper)
            
            for author in authors:
                author_data[author]['papers'].append(paper_id)
                author_data[author]['citations'].append(paper_citations)
                author_data[author]['coauthors'].update(authors)
                if year:
                    author_data[author]['years'].append(year)
                author_data[author]['keywords'].extend(keywords)
        
        # Calculate metrics for each author
        author_metrics = {}
        for author, data in author_data.items():
            metrics = AuthorMetrics(author_name=author)
            
            metrics.paper_count = len(data['papers'])
            metrics.total_citations = sum(data['citations'])
            metrics.average_citations_per_paper = metrics.total_citations / metrics.paper_count if metrics.paper_count > 0 else 0
            
            # H-index calculation
            citations_sorted = sorted(data['citations'], reverse=True)
            h_index = 0
            for i, citations in enumerate(citations_sorted):
                if citations >= i + 1:
                    h_index = i + 1
                else:
                    break
            metrics.h_index = h_index
            
            # Collaboration metrics
            metrics.unique_coauthors = data['coauthors'] - {author}  # Remove self
            metrics.collaboration_count = len(metrics.unique_coauthors)
            
            # Temporal metrics
            metrics.publication_years = sorted(data['years'])
            
            # Research areas (most common keywords)
            keyword_counts = Counter(data['keywords'])
            metrics.research_areas = [kw for kw, count in keyword_counts.most_common(5)]
            
            author_metrics[author] = metrics
        
        return author_metrics
    
    def analyze_citation_influence(self, citation_network: nx.DiGraph, 
                                 max_generations: int = 3) -> Dict[str, CitationInfluence]:
        """Analyze citation influence with multi-generational impact"""
        logger.info("Analyzing citation influence")
        
        influence_data = {}
        
        for paper_id in citation_network.nodes():
            influence = CitationInfluence(paper_id=paper_id)
            
            # Direct citations (papers citing this paper)
            direct_citers = list(citation_network.predecessors(paper_id))
            influence.direct_citations = len(direct_citers)
            
            # Multi-generational citations
            current_generation = {paper_id}
            total_influence = 0
            
            for generation in range(1, max_generations + 1):
                next_generation = set()
                for paper in current_generation:
                    citers = set(citation_network.predecessors(paper))
                    next_generation.update(citers)
                
                # Remove papers from previous generations
                next_generation -= current_generation
                if generation > 1:
                    for prev_gen in range(1, generation):
                        if prev_gen in influence.citation_generations:
                            prev_papers = set()  # This would need to be tracked properly
                            next_generation -= prev_papers
                
                influence.citation_generations[generation] = len(next_generation)
                total_influence += len(next_generation) * (1.0 / generation)  # Decay with distance
                current_generation = next_generation
                
                if not next_generation:
                    break
            
            # Calculate influence score
            influence.influence_score = total_influence
            
            # Temporal influence analysis
            paper_data = self.metadata_cache.get(paper_id, {})
            paper_year = paper_data.get('publication_info', {}).get('year')
            
            if paper_year:
                # Analyze citations over time
                for citing_paper_id in direct_citers:
                    citing_paper_data = self.metadata_cache.get(citing_paper_id, {})
                    citing_year = citing_paper_data.get('publication_info', {}).get('year')
                    if citing_year:
                        influence.temporal_influence[citing_year] = influence.temporal_influence.get(citing_year, 0) + 1
            
            influence_data[paper_id] = influence
        
        return influence_data
    
    def export_network(self, network_type: NetworkType, output_path: str, 
                      format: str = 'gexf') -> bool:
        """Export network to various formats"""
        if network_type not in self.networks:
            logger.error(f"Network type {network_type.value} not found")
            return False
        
        network = self.networks[network_type]
        
        try:
            if format.lower() == 'gexf':
                nx.write_gexf(network, output_path)
            elif format.lower() == 'graphml':
                nx.write_graphml(network, output_path)
            elif format.lower() == 'gml':
                nx.write_gml(network, output_path)
            elif format.lower() == 'json':
                data = nx.node_link_data(network)
                with open(output_path, 'w', encoding='utf-8') as f:
                    json.dump(data, f, indent=2, ensure_ascii=False)
            elif format.lower() == 'csv_nodes':
                self._export_nodes_csv(network, output_path)
            elif format.lower() == 'csv_edges':
                self._export_edges_csv(network, output_path)
            else:
                raise ValueError(f"Unsupported format: {format}")
            
            logger.info(f"Network exported to {output_path} in {format} format")
            return True
        
        except Exception as e:
            logger.error(f"Failed to export network: {e}")
            return False
    
    def generate_network_summary(self, network_type: NetworkType) -> Dict[str, Any]:
        """Generate comprehensive network summary"""
        if network_type not in self.networks:
            return {"error": f"Network type {network_type.value} not found"}
        
        network = self.networks[network_type]
        metrics = self.calculate_network_metrics(network, network_type)
        centrality = self.calculate_centrality_metrics(network)
        
        summary = {
            "network_type": network_type.value,
            "timestamp": datetime.now().isoformat(),
            "basic_metrics": metrics.to_dict(),
            "centrality_metrics": centrality,
            "top_nodes": self._get_top_nodes(network, centrality),
            "network_structure": self._analyze_network_structure(network),
            "recommendations": self._generate_recommendations(network, metrics)
        }
        
        return summary
    
    def _generate_paper_id(self, paper: Dict[str, Any]) -> str:
        """Generate unique paper ID from metadata"""
        # Use DOI if available
        if paper.get('doi'):
            return f"doi:{paper['doi']}"
        
        # Use title + first author + year
        title = paper.get('title', '').strip()
        authors = paper.get('authors', [])
        year = paper.get('publication_info', {}).get('year', '')
        
        if title and authors:
            first_author = self._extract_author_names(authors)[0] if authors else ''
            # Create hash-like ID
            import hashlib
            content = f"{title}_{first_author}_{year}".lower()
            return f"paper:{hashlib.md5(content.encode()).hexdigest()[:12]}"
        
        # Fallback to hash of full paper content
        import hashlib
        content = str(paper)
        return f"paper:{hashlib.md5(content.encode()).hexdigest()[:12]}"
    
    def _find_cited_paper_id(self, citation: Dict[str, Any], papers: List[Dict[str, Any]]) -> Optional[str]:
        """Find paper ID for a citation"""
        citation_doi = citation.get('doi')
        citation_title = citation.get('title', '').lower().strip()
        citation_authors = citation.get('authors', [])
        citation_year = citation.get('year')
        
        # Try DOI match first
        if citation_doi:
            for paper in papers:
                if paper.get('doi') == citation_doi:
                    return self._generate_paper_id(paper)
        
        # Try title + author match
        if citation_title and citation_authors:
            for paper in papers:
                paper_title = paper.get('title', '').lower().strip()
                paper_authors = self._extract_author_names(paper.get('authors', []))
                paper_year = paper.get('publication_info', {}).get('year')
                
                # Fuzzy title match
                if (citation_title in paper_title or paper_title in citation_title) and paper_title:
                    # Check author overlap
                    citation_author_names = [str(a).strip().lower() for a in citation_authors if str(a).strip()]
                    paper_author_names = [a.strip().lower() for a in paper_authors]
                    
                    if any(ca in pa for ca in citation_author_names for pa in paper_author_names):
                        # Check year if available
                        if not citation_year or not paper_year or abs(citation_year - paper_year) <= 1:
                            return self._generate_paper_id(paper)
        
        return None
    
    def _extract_author_names(self, authors: List[Any]) -> List[str]:
        """Extract author names from various formats"""
        names = []
        for author in authors:
            if isinstance(author, dict):
                name = author.get('name', '')
            elif isinstance(author, str):
                name = author
            else:
                name = str(author)
            
            if name.strip():
                names.append(name.strip())
        
        return names
    
    def _calculate_citation_metrics(self, network: nx.DiGraph, metrics: NetworkMetrics):
        """Calculate citation-specific metrics"""
        if not network.is_directed():
            return
        
        # Citations per paper
        in_degrees = dict(network.in_degree())
        if in_degrees:
            metrics.average_citations_per_paper = np.mean(list(in_degrees.values()))
        
        # Most cited papers
        sorted_papers = sorted(in_degrees.items(), key=lambda x: x[1], reverse=True)
        metrics.most_cited_papers = [paper_id for paper_id, citations in sorted_papers[:10]]
        
        # Citation distribution
        citation_counts = Counter(in_degrees.values())
        metrics.citation_distribution = dict(citation_counts)
    
    def _calculate_temporal_metrics(self, network: nx.Graph, metrics: NetworkMetrics):
        """Calculate temporal network metrics"""
        years = []
        for node_id, data in network.nodes(data=True):
            year = data.get('year')
            if year:
                years.append(year)
        
        if years:
            metrics.network_age = max(years) - min(years)
            # Simple citation velocity calculation
            total_citations = network.number_of_edges()
            metrics.citation_velocity = total_citations / max(1, metrics.network_age)
    
    def _get_top_nodes(self, network: nx.Graph, centrality: Dict[str, Dict[str, float]]) -> Dict[str, List[Dict[str, Any]]]:
        """Get top nodes by various centrality measures"""
        top_nodes = {}
        
        for metric_name, values in centrality.items():
            if values:
                sorted_nodes = sorted(values.items(), key=lambda x: x[1], reverse=True)
                top_nodes[metric_name] = []
                
                for node_id, score in sorted_nodes[:10]:
                    node_data = network.nodes[node_id].copy()
                    node_data['score'] = score
                    top_nodes[metric_name].append(node_data)
        
        return top_nodes
    
    def _analyze_network_structure(self, network: nx.Graph) -> Dict[str, Any]:
        """Analyze network structure"""
        structure = {}
        
        # Degree distribution
        degrees = dict(network.degree())
        if degrees:
            structure['degree_distribution'] = {
                'mean': np.mean(list(degrees.values())),
                'std': np.std(list(degrees.values())),
                'min': min(degrees.values()),
                'max': max(degrees.values())
            }
        
        # Component analysis
        if not network.is_directed():
            components = list(nx.connected_components(network))
            structure['components'] = {
                'count': len(components),
                'largest_size': len(max(components, key=len)) if components else 0,
                'sizes': [len(c) for c in components]
            }
        
        return structure
    
    def _generate_recommendations(self, network: nx.Graph, metrics: NetworkMetrics) -> List[str]:
        """Generate analysis recommendations"""
        recommendations = []
        
        if metrics.density < 0.01:
            recommendations.append("Network is very sparse - consider expanding citation search")
        
        if metrics.num_components > metrics.num_nodes * 0.1:
            recommendations.append("Many disconnected components - network may need consolidation")
        
        if not metrics.is_connected:
            recommendations.append("Network is disconnected - analyze largest component separately")
        
        if metrics.average_clustering < 0.1:
            recommendations.append("Low clustering - papers may be from diverse research areas")
        
        return recommendations
    
    def _export_nodes_csv(self, network: nx.Graph, output_path: str):
        """Export nodes to CSV format"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if network.nodes():
                # Get all possible node attributes
                all_attrs = set()
                for _, data in network.nodes(data=True):
                    all_attrs.update(data.keys())
                
                fieldnames = ['node_id'] + sorted(all_attrs)
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for node_id, data in network.nodes(data=True):
                    row = {'node_id': node_id}
                    row.update(data)
                    writer.writerow(row)
    
    def _export_edges_csv(self, network: nx.Graph, output_path: str):
        """Export edges to CSV format"""
        import csv
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            if network.edges():
                # Get all possible edge attributes
                all_attrs = set()
                for _, _, data in network.edges(data=True):
                    all_attrs.update(data.keys())
                
                fieldnames = ['source', 'target'] + sorted(all_attrs)
                writer = csv.DictWriter(f, fieldnames=fieldnames)
                writer.writeheader()
                
                for source, target, data in network.edges(data=True):
                    row = {'source': source, 'target': target}
                    row.update(data)
                    writer.writerow(row)

# Global instance for easy access
citation_network_analyzer = CitationNetworkAnalyzer()

def build_citation_network(papers_metadata: List[Dict[str, Any]]) -> nx.DiGraph:
    """Build citation network using the global instance"""
    return citation_network_analyzer.build_citation_network(papers_metadata)

def analyze_citation_networks(papers_metadata: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Comprehensive citation network analysis"""
    analyzer = CitationNetworkAnalyzer()
    
    # Build all network types
    citation_net = analyzer.build_citation_network(papers_metadata)
    cocitation_net = analyzer.build_cocitation_network(citation_net)
    coupling_net = analyzer.build_bibliographic_coupling_network(citation_net)
    author_net = analyzer.build_author_collaboration_network(papers_metadata)
    keyword_net = analyzer.build_keyword_cooccurrence_network(papers_metadata)
    
    # Analyze metrics
    citation_metrics = analyzer.calculate_network_metrics(citation_net, NetworkType.CITATION)
    author_metrics = analyzer.analyze_author_metrics(papers_metadata)
    influence_analysis = analyzer.analyze_citation_influence(citation_net)
    
    # Generate summaries
    results = {
        "networks": {
            "citation": analyzer.generate_network_summary(NetworkType.CITATION),
            "cocitation": analyzer.generate_network_summary(NetworkType.COCITATION),
            "bibliographic_coupling": analyzer.generate_network_summary(NetworkType.BIBLIOGRAPHIC_COUPLING),
            "author_collaboration": analyzer.generate_network_summary(NetworkType.AUTHOR_COLLABORATION),
            "keyword_cooccurrence": analyzer.generate_network_summary(NetworkType.KEYWORD_COOCCURRENCE)
        },
        "author_analysis": {name: metrics.to_dict() for name, metrics in author_metrics.items()},
        "influence_analysis": {paper_id: influence.to_dict() for paper_id, influence in influence_analysis.items()},
        "analysis_timestamp": datetime.now().isoformat(),
        "total_papers_analyzed": len(papers_metadata)
    }
    
    return results 
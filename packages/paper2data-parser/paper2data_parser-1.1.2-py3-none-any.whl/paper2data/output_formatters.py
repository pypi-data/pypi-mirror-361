"""
Output Formatters for Paper2Data

This module provides comprehensive output formatting capabilities for Paper2Data
extraction results, supporting multiple formats including HTML, LaTeX, Word,
XML, CSV, and Markdown.
"""

import os
import json
import csv
import tempfile
import logging
from typing import Dict, Any, List, Optional, Union, TextIO
from datetime import datetime
from abc import ABC, abstractmethod
from dataclasses import dataclass
from enum import Enum
import xml.etree.ElementTree as ET
from xml.dom import minidom
import base64

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OutputFormat(Enum):
    """Supported output formats"""
    JSON = "json"
    HTML = "html"
    LATEX = "latex"
    XML = "xml"
    CSV = "csv"
    MARKDOWN = "markdown"
    DOCX = "docx"
    PDF = "pdf"

@dataclass
class FormatConfig:
    """Configuration for output formatting"""
    include_metadata: bool = True
    include_figures: bool = True
    include_tables: bool = True
    include_equations: bool = True
    include_citations: bool = True
    include_networks: bool = True
    include_statistics: bool = True
    
    # Format-specific options
    html_include_css: bool = True
    html_embed_images: bool = False
    latex_document_class: str = "article"
    latex_packages: List[str] = None
    csv_delimiter: str = ","
    xml_pretty_print: bool = True
    markdown_include_toc: bool = True
    
    def __post_init__(self):
        if self.latex_packages is None:
            self.latex_packages = ["amsmath", "graphicx", "hyperref", "booktabs"]

class BaseFormatter(ABC):
    """Base class for all output formatters"""
    
    def __init__(self, config: FormatConfig = None):
        """Initialize formatter with configuration"""
        self.config = config or FormatConfig()
        self.output_format = None
    
    @abstractmethod
    def format(self, data: Dict[str, Any], output_path: str) -> bool:
        """Format and save data to specified output path"""
        pass
    
    def _validate_data(self, data: Dict[str, Any]) -> bool:
        """Validate input data structure"""
        required_keys = ["extraction_timestamp"]
        return all(key in data for key in required_keys)
    
    def _get_title(self, data: Dict[str, Any]) -> str:
        """Extract document title from data"""
        # Try metadata first
        if "metadata" in data and isinstance(data["metadata"], dict):
            title = data["metadata"].get("title")
            if title:
                return str(title)
        
        # Try content extraction
        if "content" in data and isinstance(data["content"], dict):
            title = data["content"].get("title")
            if title:
                return str(title)
        
        return "Document Analysis Results"
    
    def _format_timestamp(self, timestamp: str) -> str:
        """Format timestamp for display"""
        try:
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M:%S")
        except:
            return timestamp

class JSONFormatter(BaseFormatter):
    """JSON output formatter"""
    
    def __init__(self, config: FormatConfig = None):
        super().__init__(config)
        self.output_format = OutputFormat.JSON
    
    def format(self, data: Dict[str, Any], output_path: str) -> bool:
        """Format data as JSON"""
        try:
            # Filter data based on config
            filtered_data = self._filter_data(data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(filtered_data, f, indent=2, ensure_ascii=False, default=str)
            
            logger.info(f"JSON output saved to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to format JSON: {e}")
            return False
    
    def _filter_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Filter data based on configuration"""
        filtered = {"extraction_timestamp": data.get("extraction_timestamp")}
        
        if self.config.include_metadata and "metadata" in data:
            filtered["metadata"] = data["metadata"]
        
        if self.config.include_figures and "figures" in data:
            filtered["figures"] = data["figures"]
        
        if self.config.include_tables and "tables" in data:
            filtered["tables"] = data["tables"]
        
        if self.config.include_equations and "equations" in data:
            filtered["equations"] = data["equations"]
        
        if self.config.include_citations and "citations" in data:
            filtered["citations"] = data["citations"]
        
        if self.config.include_networks and "citation_networks" in data:
            filtered["citation_networks"] = data["citation_networks"]
        
        if self.config.include_statistics and "summary" in data:
            filtered["summary"] = data["summary"]
        
        # Always include content
        if "content" in data:
            filtered["content"] = data["content"]
        
        if "sections" in data:
            filtered["sections"] = data["sections"]
        
        return filtered

class HTMLFormatter(BaseFormatter):
    """HTML output formatter with rich styling"""
    
    def __init__(self, config: FormatConfig = None):
        super().__init__(config)
        self.output_format = OutputFormat.HTML
    
    def format(self, data: Dict[str, Any], output_path: str) -> bool:
        """Format data as HTML"""
        try:
            title = self._get_title(data)
            timestamp = self._format_timestamp(data.get("extraction_timestamp", ""))
            
            html_content = self._generate_html(data, title, timestamp)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            logger.info(f"HTML output saved to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to format HTML: {e}")
            return False
    
    def _generate_html(self, data: Dict[str, Any], title: str, timestamp: str) -> str:
        """Generate complete HTML document"""
        html_parts = []
        
        # HTML header
        html_parts.append(self._get_html_header(title))
        
        # Title and metadata
        html_parts.append(f'<div class="header">')
        html_parts.append(f'<h1>{title}</h1>')
        html_parts.append(f'<p class="timestamp">Extracted: {timestamp}</p>')
        html_parts.append('</div>')
        
        # Table of contents
        html_parts.append(self._generate_toc(data))
        
        # Content sections
        if self.config.include_metadata:
            html_parts.append(self._format_metadata_html(data.get("metadata", {})))
        
        html_parts.append(self._format_content_html(data.get("content", {})))
        html_parts.append(self._format_sections_html(data.get("sections", {})))
        
        if self.config.include_figures:
            html_parts.append(self._format_figures_html(data.get("figures", {})))
        
        if self.config.include_tables:
            html_parts.append(self._format_tables_html(data.get("tables", {})))
        
        if self.config.include_equations:
            html_parts.append(self._format_equations_html(data.get("equations", {})))
        
        if self.config.include_citations:
            html_parts.append(self._format_citations_html(data.get("citations", {})))
        
        if self.config.include_networks:
            html_parts.append(self._format_networks_html(data.get("citation_networks", {})))
        
        if self.config.include_statistics:
            html_parts.append(self._format_statistics_html(data.get("summary", {})))
        
        # HTML footer
        html_parts.append(self._get_html_footer())
        
        return '\n'.join(html_parts)
    
    def _get_html_header(self, title: str) -> str:
        """Generate HTML document header"""
        css = self._get_css() if self.config.html_include_css else ""
        
        return f'''<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title} - Paper2Data Analysis</title>
    {css}
</head>
<body>
<div class="container">'''
    
    def _get_html_footer(self) -> str:
        """Generate HTML document footer"""
        return '''</div>
<footer>
    <p>Generated by Paper2Data - Academic Document Analysis System</p>
</footer>
</body>
</html>'''
    
    def _get_css(self) -> str:
        """Generate CSS styles for HTML output"""
        return '''<style>
body {
    font-family: 'Georgia', 'Times New Roman', serif;
    line-height: 1.6;
    margin: 0;
    padding: 0;
    background-color: #f9f9f9;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 20px;
    background-color: white;
    box-shadow: 0 0 10px rgba(0,0,0,0.1);
}

.header {
    text-align: center;
    border-bottom: 3px solid #2c3e50;
    padding-bottom: 20px;
    margin-bottom: 30px;
}

h1 {
    color: #2c3e50;
    font-size: 2.5em;
    margin-bottom: 10px;
}

h2 {
    color: #34495e;
    border-bottom: 2px solid #ecf0f1;
    padding-bottom: 5px;
    margin-top: 30px;
}

h3 {
    color: #7f8c8d;
    margin-top: 25px;
}

.timestamp {
    color: #7f8c8d;
    font-style: italic;
    font-size: 0.9em;
}

.toc {
    background-color: #ecf0f1;
    padding: 20px;
    border-radius: 5px;
    margin: 20px 0;
}

.toc ul {
    list-style-type: none;
    padding-left: 0;
}

.toc li {
    margin: 5px 0;
}

.toc a {
    color: #3498db;
    text-decoration: none;
}

.toc a:hover {
    text-decoration: underline;
}

.section {
    margin: 30px 0;
    padding: 20px;
    border-left: 4px solid #3498db;
    background-color: #fafafa;
}

table {
    width: 100%;
    border-collapse: collapse;
    margin: 20px 0;
    background-color: white;
}

th, td {
    border: 1px solid #ddd;
    padding: 12px;
    text-align: left;
}

th {
    background-color: #34495e;
    color: white;
    font-weight: bold;
}

tr:nth-child(even) {
    background-color: #f8f9fa;
}

.figure-container {
    text-align: center;
    margin: 20px 0;
    padding: 15px;
    border: 1px solid #ddd;
    border-radius: 5px;
}

.figure-caption {
    font-style: italic;
    color: #666;
    margin-top: 10px;
}

.equation {
    text-align: center;
    margin: 20px 0;
    padding: 15px;
    background-color: #f8f9fa;
    border-left: 4px solid #e74c3c;
    font-family: 'Courier New', monospace;
}

.metadata-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 20px;
    margin: 20px 0;
}

.metadata-item {
    padding: 15px;
    background-color: #f8f9fa;
    border-radius: 5px;
    border-left: 4px solid #3498db;
}

.statistics {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.stat-card {
    text-align: center;
    padding: 20px;
    background-color: #3498db;
    color: white;
    border-radius: 5px;
}

.stat-number {
    font-size: 2em;
    font-weight: bold;
    display: block;
}

.stat-label {
    font-size: 0.9em;
    opacity: 0.9;
}

.citation {
    margin: 10px 0;
    padding: 10px;
    background-color: #fff;
    border-left: 3px solid #95a5a6;
    font-size: 0.9em;
}

.network-summary {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 15px;
    margin: 20px 0;
}

.network-card {
    padding: 15px;
    background-color: #f1c40f;
    color: #2c3e50;
    border-radius: 5px;
    text-align: center;
}

footer {
    text-align: center;
    padding: 20px;
    background-color: #2c3e50;
    color: white;
    margin-top: 40px;
}

.alert {
    padding: 15px;
    margin: 20px 0;
    border-radius: 5px;
}

.alert-info {
    background-color: #d1ecf1;
    border-left: 4px solid #bee5eb;
    color: #0c5460;
}

.alert-warning {
    background-color: #fff3cd;
    border-left: 4px solid #ffeaa7;
    color: #856404;
}

@media (max-width: 768px) {
    .container {
        padding: 10px;
    }
    
    h1 {
        font-size: 2em;
    }
    
    .metadata-grid, .statistics, .network-summary {
        grid-template-columns: 1fr;
    }
}
</style>'''
    
    def _generate_toc(self, data: Dict[str, Any]) -> str:
        """Generate table of contents"""
        toc_items = []
        
        if self.config.include_metadata and data.get("metadata"):
            toc_items.append('<li><a href="#metadata">Document Metadata</a></li>')
        
        toc_items.append('<li><a href="#content">Document Content</a></li>')
        toc_items.append('<li><a href="#sections">Document Sections</a></li>')
        
        if self.config.include_figures and data.get("figures"):
            toc_items.append('<li><a href="#figures">Figures & Images</a></li>')
        
        if self.config.include_tables and data.get("tables"):
            toc_items.append('<li><a href="#tables">Tables</a></li>')
        
        if self.config.include_equations and data.get("equations"):
            toc_items.append('<li><a href="#equations">Equations</a></li>')
        
        if self.config.include_citations and data.get("citations"):
            toc_items.append('<li><a href="#citations">Citations & References</a></li>')
        
        if self.config.include_networks and data.get("citation_networks"):
            toc_items.append('<li><a href="#networks">Citation Networks</a></li>')
        
        if self.config.include_statistics and data.get("summary"):
            toc_items.append('<li><a href="#statistics">Analysis Statistics</a></li>')
        
        return f'''<div class="toc">
<h2>Table of Contents</h2>
<ul>
{chr(10).join(toc_items)}
</ul>
</div>'''
    
    def _format_metadata_html(self, metadata: Dict[str, Any]) -> str:
        """Format metadata section as HTML"""
        if not metadata:
            return ""
        
        html_parts = ['<div class="section" id="metadata">', '<h2>Document Metadata</h2>']
        
        # Basic metadata
        basic_items = []
        if metadata.get("title"):
            basic_items.append(f'<div class="metadata-item"><strong>Title:</strong> {metadata["title"]}</div>')
        
        if metadata.get("authors"):
            authors = metadata["authors"]
            if isinstance(authors, list):
                author_list = ", ".join([str(a.get("name", a) if isinstance(a, dict) else a) for a in authors])
                basic_items.append(f'<div class="metadata-item"><strong>Authors:</strong> {author_list}</div>')
        
        if metadata.get("publication_info"):
            pub_info = metadata["publication_info"]
            if isinstance(pub_info, dict):
                pub_details = []
                if pub_info.get("journal"):
                    pub_details.append(f"Journal: {pub_info['journal']}")
                if pub_info.get("year"):
                    pub_details.append(f"Year: {pub_info['year']}")
                if pub_info.get("volume"):
                    pub_details.append(f"Volume: {pub_info['volume']}")
                if pub_details:
                    basic_items.append(f'<div class="metadata-item"><strong>Publication:</strong> {", ".join(pub_details)}</div>')
        
        if metadata.get("doi"):
            basic_items.append(f'<div class="metadata-item"><strong>DOI:</strong> <a href="https://doi.org/{metadata["doi"]}">{metadata["doi"]}</a></div>')
        
        if metadata.get("keywords"):
            keywords = metadata["keywords"]
            if isinstance(keywords, list):
                keyword_list = ", ".join([str(k) for k in keywords])
                basic_items.append(f'<div class="metadata-item"><strong>Keywords:</strong> {keyword_list}</div>')
        
        if basic_items:
            html_parts.append('<div class="metadata-grid">')
            html_parts.extend(basic_items)
            html_parts.append('</div>')
        
        # Abstract
        if metadata.get("abstract"):
            html_parts.append('<h3>Abstract</h3>')
            html_parts.append(f'<div class="section">{metadata["abstract"]}</div>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_content_html(self, content: Dict[str, Any]) -> str:
        """Format content section as HTML"""
        html_parts = ['<div class="section" id="content">', '<h2>Document Content</h2>']
        
        # Full text
        if content.get("full_text"):
            html_parts.append('<h3>Full Text</h3>')
            text = content["full_text"]
            # Simple paragraph formatting
            paragraphs = text.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    html_parts.append(f'<p>{para.strip()}</p>')
        
        # Statistics
        if content.get("statistics"):
            stats = content["statistics"]
            html_parts.append('<h3>Content Statistics</h3>')
            html_parts.append('<div class="statistics">')
            
            if stats.get("page_count"):
                html_parts.append('<div class="stat-card"><span class="stat-number">{}</span><span class="stat-label">Pages</span></div>'.format(stats["page_count"]))
            
            if stats.get("word_count"):
                html_parts.append('<div class="stat-card"><span class="stat-number">{}</span><span class="stat-label">Words</span></div>'.format(stats["word_count"]))
            
            if stats.get("character_count"):
                html_parts.append('<div class="stat-card"><span class="stat-number">{}</span><span class="stat-label">Characters</span></div>'.format(stats["character_count"]))
            
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_sections_html(self, sections: Dict[str, Any]) -> str:
        """Format sections as HTML"""
        html_parts = ['<div class="section" id="sections">', '<h2>Document Sections</h2>']
        
        if sections.get("sections"):
            for section in sections["sections"]:
                if isinstance(section, dict):
                    title = section.get("title", "Untitled Section")
                    content = section.get("content", "")
                    
                    html_parts.append(f'<h3>{title}</h3>')
                    if content:
                        # Simple paragraph formatting
                        paragraphs = content.split('\n\n')
                        for para in paragraphs:
                            if para.strip():
                                html_parts.append(f'<p>{para.strip()}</p>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_figures_html(self, figures: Dict[str, Any]) -> str:
        """Format figures section as HTML"""
        if not figures or not figures.get("figures"):
            return ""
        
        html_parts = ['<div class="section" id="figures">', '<h2>Figures & Images</h2>']
        
        for i, figure in enumerate(figures["figures"], 1):
            if isinstance(figure, dict):
                html_parts.append('<div class="figure-container">')
                
                # Figure title
                caption = figure.get("caption", f"Figure {i}")
                html_parts.append(f'<h4>Figure {i}</h4>')
                
                # Image placeholder or base64 if embedded
                if self.config.html_embed_images and figure.get("image_data"):
                    html_parts.append(f'<img src="data:image/png;base64,{figure["image_data"]}" alt="{caption}" style="max-width: 100%; height: auto;">')
                else:
                    html_parts.append('<div style="border: 2px dashed #ccc; padding: 50px; text-align: center; color: #666;">Image Not Embedded</div>')
                
                # Caption
                if caption:
                    html_parts.append(f'<div class="figure-caption">{caption}</div>')
                
                # Additional info
                if figure.get("page"):
                    html_parts.append(f'<p><small>Page: {figure["page"]}</small></p>')
                
                html_parts.append('</div>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_tables_html(self, tables: Dict[str, Any]) -> str:
        """Format tables section as HTML"""
        if not tables or not tables.get("tables"):
            return ""
        
        html_parts = ['<div class="section" id="tables">', '<h2>Tables</h2>']
        
        for i, table in enumerate(tables["tables"], 1):
            if isinstance(table, dict):
                html_parts.append(f'<h3>Table {i}</h3>')
                
                # Table caption
                if table.get("caption"):
                    html_parts.append(f'<p><strong>{table["caption"]}</strong></p>')
                
                # Table data
                if table.get("data"):
                    html_parts.append('<table>')
                    
                    # Header row if available
                    if table.get("headers"):
                        html_parts.append('<thead><tr>')
                        for header in table["headers"]:
                            html_parts.append(f'<th>{header}</th>')
                        html_parts.append('</tr></thead>')
                    
                    # Data rows
                    html_parts.append('<tbody>')
                    for row in table["data"]:
                        html_parts.append('<tr>')
                        if isinstance(row, list):
                            for cell in row:
                                html_parts.append(f'<td>{cell}</td>')
                        html_parts.append('</tr>')
                    html_parts.append('</tbody>')
                    
                    html_parts.append('</table>')
                
                # Additional info
                if table.get("page"):
                    html_parts.append(f'<p><small>Page: {table["page"]}</small></p>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_equations_html(self, equations: Dict[str, Any]) -> str:
        """Format equations section as HTML"""
        if not equations or not equations.get("equations"):
            return ""
        
        html_parts = ['<div class="section" id="equations">', '<h2>Mathematical Equations</h2>']
        
        for i, equation in enumerate(equations["equations"], 1):
            if isinstance(equation, dict):
                html_parts.append('<div class="equation">')
                html_parts.append(f'<h4>Equation {i}</h4>')
                
                # LaTeX code
                if equation.get("latex"):
                    html_parts.append(f'<pre>{equation["latex"]}</pre>')
                
                # Original text
                if equation.get("text"):
                    html_parts.append(f'<p><strong>Original:</strong> {equation["text"]}</p>')
                
                # Additional info
                if equation.get("page"):
                    html_parts.append(f'<p><small>Page: {equation["page"]}</small></p>')
                
                html_parts.append('</div>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_citations_html(self, citations: Dict[str, Any]) -> str:
        """Format citations section as HTML"""
        if not citations:
            return ""
        
        html_parts = ['<div class="section" id="citations">', '<h2>Citations & References</h2>']
        
        # References
        if citations.get("references"):
            html_parts.append('<h3>References</h3>')
            for i, ref in enumerate(citations["references"], 1):
                if isinstance(ref, dict):
                    html_parts.append('<div class="citation">')
                    
                    # Citation text
                    if ref.get("text"):
                        html_parts.append(f'<p>{i}. {ref["text"]}</p>')
                    
                    # Structured information
                    details = []
                    if ref.get("authors"):
                        authors = ref["authors"]
                        if isinstance(authors, list):
                            details.append(f"Authors: {', '.join(authors)}")
                    
                    if ref.get("title"):
                        details.append(f"Title: {ref['title']}")
                    
                    if ref.get("year"):
                        details.append(f"Year: {ref['year']}")
                    
                    if ref.get("doi"):
                        details.append(f'DOI: <a href="https://doi.org/{ref["doi"]}">{ref["doi"]}</a>')
                    
                    if details:
                        html_parts.append(f'<p><small>{" | ".join(details)}</small></p>')
                    
                    html_parts.append('</div>')
        
        # In-text citations
        if citations.get("in_text_citations"):
            html_parts.append('<h3>In-text Citations</h3>')
            html_parts.append(f'<p>Found {len(citations["in_text_citations"])} in-text citations throughout the document.</p>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_networks_html(self, networks: Dict[str, Any]) -> str:
        """Format citation networks section as HTML"""
        if not networks or not networks.get("networks"):
            return ""
        
        html_parts = ['<div class="section" id="networks">', '<h2>Citation Networks</h2>']
        
        html_parts.append('<div class="network-summary">')
        for network_name, network_data in networks["networks"].items():
            if isinstance(network_data, dict) and "basic_metrics" in network_data:
                metrics = network_data["basic_metrics"]
                
                html_parts.append('<div class="network-card">')
                html_parts.append(f'<h4>{network_name.replace("_", " ").title()}</h4>')
                html_parts.append(f'<p><strong>Nodes:</strong> {metrics.get("num_nodes", 0)}</p>')
                html_parts.append(f'<p><strong>Edges:</strong> {metrics.get("num_edges", 0)}</p>')
                html_parts.append(f'<p><strong>Density:</strong> {metrics.get("density", 0):.3f}</p>')
                html_parts.append('</div>')
        
        html_parts.append('</div>')
        
        # Author analysis
        if networks.get("author_analysis"):
            html_parts.append('<h3>Author Analysis</h3>')
            author_count = len(networks["author_analysis"])
            html_parts.append(f'<p>Analyzed {author_count} authors and their collaboration patterns.</p>')
        
        # Influence analysis
        if networks.get("influence_analysis"):
            html_parts.append('<h3>Citation Influence</h3>')
            influence_count = len(networks["influence_analysis"])
            html_parts.append(f'<p>Calculated influence scores for {influence_count} papers.</p>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)
    
    def _format_statistics_html(self, summary: Dict[str, Any]) -> str:
        """Format statistics section as HTML"""
        if not summary:
            return ""
        
        html_parts = ['<div class="section" id="statistics">', '<h2>Analysis Statistics</h2>']
        
        html_parts.append('<div class="statistics">')
        
        # Core statistics
        stats_items = [
            ("total_pages", "Pages"),
            ("total_words", "Words"),
            ("sections_found", "Sections"),
            ("figures_found", "Figures"),
            ("tables_found", "Tables"),
            ("references_found", "References"),
            ("equations_found", "Equations"),
            ("authors_found", "Authors"),
            ("keywords_found", "Keywords")
        ]
        
        for key, label in stats_items:
            if key in summary:
                html_parts.append(f'<div class="stat-card"><span class="stat-number">{summary[key]}</span><span class="stat-label">{label}</span></div>')
        
        html_parts.append('</div>')
        
        # Quality indicators
        quality_items = []
        if summary.get("metadata_extracted"):
            quality_items.append("✓ Metadata Extracted")
        if summary.get("citation_networks_analyzed"):
            quality_items.append("✓ Networks Analyzed")
        if summary.get("doi_found"):
            quality_items.append("✓ DOI Found")
        
        if quality_items:
            html_parts.append('<div class="alert alert-info">')
            html_parts.append('<h4>Quality Indicators</h4>')
            html_parts.append('<ul>')
            for item in quality_items:
                html_parts.append(f'<li>{item}</li>')
            html_parts.append('</ul>')
            html_parts.append('</div>')
        
        html_parts.append('</div>')
        return '\n'.join(html_parts)

class LaTeXFormatter(BaseFormatter):
    """LaTeX output formatter for academic documents"""
    
    def __init__(self, config: FormatConfig = None):
        super().__init__(config)
        self.output_format = OutputFormat.LATEX
    
    def format(self, data: Dict[str, Any], output_path: str) -> bool:
        """Format data as LaTeX"""
        try:
            latex_content = self._generate_latex(data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(latex_content)
            
            logger.info(f"LaTeX output saved to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to format LaTeX: {e}")
            return False
    
    def _generate_latex(self, data: Dict[str, Any]) -> str:
        """Generate complete LaTeX document"""
        title = self._get_title(data)
        timestamp = self._format_timestamp(data.get("extraction_timestamp", ""))
        
        latex_parts = []
        
        # Document header
        latex_parts.append(self._get_latex_header(title))
        
        # Title page
        latex_parts.append("\\begin{document}")
        latex_parts.append("\\maketitle")
        latex_parts.append(f"\\begin{{center}}\\textit{{Analysis performed: {timestamp}}}\\end{{center}}")
        latex_parts.append("\\newpage")
        
        # Table of contents
        latex_parts.append("\\tableofcontents")
        latex_parts.append("\\newpage")
        
        # Content sections
        if self.config.include_metadata:
            latex_parts.append(self._format_metadata_latex(data.get("metadata", {})))
        
        latex_parts.append(self._format_content_latex(data.get("content", {})))
        latex_parts.append(self._format_sections_latex(data.get("sections", {})))
        
        if self.config.include_figures:
            latex_parts.append(self._format_figures_latex(data.get("figures", {})))
        
        if self.config.include_tables:
            latex_parts.append(self._format_tables_latex(data.get("tables", {})))
        
        if self.config.include_equations:
            latex_parts.append(self._format_equations_latex(data.get("equations", {})))
        
        if self.config.include_citations:
            latex_parts.append(self._format_citations_latex(data.get("citations", {})))
        
        if self.config.include_statistics:
            latex_parts.append(self._format_statistics_latex(data.get("summary", {})))
        
        latex_parts.append("\\end{document}")
        
        return '\n'.join(latex_parts)
    
    def _get_latex_header(self, title: str) -> str:
        """Generate LaTeX document header"""
        packages = ''.join([f"\\usepackage{{{pkg}}}\n" for pkg in self.config.latex_packages])
        
        return f"""\\documentclass[12pt]{{{self.config.latex_document_class}}}
{packages}
\\usepackage[utf8]{{inputenc}}
\\usepackage[T1]{{fontenc}}
\\usepackage{{geometry}}
\\geometry{{margin=1in}}

\\title{{{title}}}
\\author{{Paper2Data Analysis System}}
\\date{{\\today}}"""
    
    def _escape_latex(self, text: str) -> str:
        """Escape special LaTeX characters"""
        if not isinstance(text, str):
            text = str(text)
        
        # Basic LaTeX escaping
        replacements = {
            '\\': '\\textbackslash{}',
            '{': '\\{',
            '}': '\\}',
            '$': '\\$',
            '&': '\\&',
            '%': '\\%',
            '#': '\\#',
            '^': '\\textasciicircum{}',
            '_': '\\_',
            '~': '\\textasciitilde{}',
        }
        
        for char, replacement in replacements.items():
            text = text.replace(char, replacement)
        
        return text
    
    def _format_metadata_latex(self, metadata: Dict[str, Any]) -> str:
        """Format metadata section as LaTeX"""
        if not metadata:
            return ""
        
        latex_parts = ["\\section{Document Metadata}"]
        
        # Basic metadata table
        latex_parts.append("\\begin{tabular}{ll}")
        latex_parts.append("\\toprule")
        latex_parts.append("\\textbf{Field} & \\textbf{Value} \\\\")
        latex_parts.append("\\midrule")
        
        if metadata.get("title"):
            latex_parts.append(f"Title & {self._escape_latex(metadata['title'])} \\\\")
        
        if metadata.get("authors"):
            authors = metadata["authors"]
            if isinstance(authors, list):
                author_list = ", ".join([str(a.get("name", a) if isinstance(a, dict) else a) for a in authors])
                latex_parts.append(f"Authors & {self._escape_latex(author_list)} \\\\")
        
        if metadata.get("doi"):
            latex_parts.append(f"DOI & \\url{{{metadata['doi']}}} \\\\")
        
        latex_parts.append("\\bottomrule")
        latex_parts.append("\\end{tabular}")
        
        # Abstract
        if metadata.get("abstract"):
            latex_parts.append("\\subsection{Abstract}")
            latex_parts.append(self._escape_latex(metadata["abstract"]))
        
        return '\n'.join(latex_parts)
    
    def _format_content_latex(self, content: Dict[str, Any]) -> str:
        """Format content section as LaTeX"""
        latex_parts = ["\\section{Document Content}"]
        
        if content.get("full_text"):
            latex_parts.append("\\subsection{Full Text}")
            text = self._escape_latex(content["full_text"])
            # Convert double newlines to paragraph breaks
            text = text.replace('\n\n', '\n\n\\par\n')
            latex_parts.append(text)
        
        return '\n'.join(latex_parts)
    
    def _format_sections_latex(self, sections: Dict[str, Any]) -> str:
        """Format sections as LaTeX"""
        latex_parts = ["\\section{Document Sections}"]
        
        if sections.get("sections"):
            for section in sections["sections"]:
                if isinstance(section, dict):
                    title = section.get("title", "Untitled Section")
                    content = section.get("content", "")
                    
                    latex_parts.append(f"\\subsection{{{self._escape_latex(title)}}}")
                    if content:
                        latex_parts.append(self._escape_latex(content))
        
        return '\n'.join(latex_parts)
    
    def _format_figures_latex(self, figures: Dict[str, Any]) -> str:
        """Format figures section as LaTeX"""
        if not figures or not figures.get("figures"):
            return ""
        
        latex_parts = ["\\section{Figures \\& Images}"]
        
        for i, figure in enumerate(figures["figures"], 1):
            if isinstance(figure, dict):
                caption = figure.get("caption", f"Figure {i}")
                
                latex_parts.append("\\begin{figure}[h]")
                latex_parts.append("\\centering")
                latex_parts.append("\\fbox{Image Not Embedded}")  # Placeholder
                latex_parts.append(f"\\caption{{{self._escape_latex(caption)}}}")
                latex_parts.append(f"\\label{{fig:{i}}}")
                latex_parts.append("\\end{figure}")
        
        return '\n'.join(latex_parts)
    
    def _format_tables_latex(self, tables: Dict[str, Any]) -> str:
        """Format tables section as LaTeX"""
        if not tables or not tables.get("tables"):
            return ""
        
        latex_parts = ["\\section{Tables}"]
        
        for i, table in enumerate(tables["tables"], 1):
            if isinstance(table, dict):
                caption = table.get("caption", f"Table {i}")
                
                if table.get("data"):
                    # Determine column count
                    max_cols = 1
                    if table.get("headers"):
                        max_cols = len(table["headers"])
                    elif table["data"]:
                        max_cols = max(len(row) if isinstance(row, list) else 1 for row in table["data"])
                    
                    col_spec = "l" * max_cols
                    
                    latex_parts.append("\\begin{table}[h]")
                    latex_parts.append("\\centering")
                    latex_parts.append(f"\\begin{{tabular}}{{{col_spec}}}")
                    latex_parts.append("\\toprule")
                    
                    # Headers
                    if table.get("headers"):
                        header_row = " & ".join([self._escape_latex(str(h)) for h in table["headers"]])
                        latex_parts.append(f"{header_row} \\\\")
                        latex_parts.append("\\midrule")
                    
                    # Data rows
                    for row in table["data"]:
                        if isinstance(row, list):
                            escaped_row = [self._escape_latex(str(cell)) for cell in row]
                            latex_parts.append(f"{' & '.join(escaped_row)} \\\\")
                    
                    latex_parts.append("\\bottomrule")
                    latex_parts.append("\\end{tabular}")
                    latex_parts.append(f"\\caption{{{self._escape_latex(caption)}}}")
                    latex_parts.append(f"\\label{{tab:{i}}}")
                    latex_parts.append("\\end{table}")
        
        return '\n'.join(latex_parts)
    
    def _format_equations_latex(self, equations: Dict[str, Any]) -> str:
        """Format equations section as LaTeX"""
        if not equations or not equations.get("equations"):
            return ""
        
        latex_parts = ["\\section{Mathematical Equations}"]
        
        for i, equation in enumerate(equations["equations"], 1):
            if isinstance(equation, dict):
                latex_parts.append(f"\\subsection{{Equation {i}}}")
                
                # LaTeX equation
                if equation.get("latex"):
                    latex_parts.append("\\begin{equation}")
                    latex_parts.append(equation["latex"])
                    latex_parts.append("\\end{equation}")
                
                # Original text
                if equation.get("text"):
                    latex_parts.append(f"\\textbf{{Original:}} {self._escape_latex(equation['text'])}")
        
        return '\n'.join(latex_parts)
    
    def _format_citations_latex(self, citations: Dict[str, Any]) -> str:
        """Format citations section as LaTeX"""
        if not citations:
            return ""
        
        latex_parts = ["\\section{Citations \\& References}"]
        
        if citations.get("references"):
            latex_parts.append("\\subsection{References}")
            latex_parts.append("\\begin{enumerate}")
            
            for ref in citations["references"]:
                if isinstance(ref, dict) and ref.get("text"):
                    latex_parts.append(f"\\item {self._escape_latex(ref['text'])}")
            
            latex_parts.append("\\end{enumerate}")
        
        return '\n'.join(latex_parts)
    
    def _format_statistics_latex(self, summary: Dict[str, Any]) -> str:
        """Format statistics section as LaTeX"""
        if not summary:
            return ""
        
        latex_parts = ["\\section{Analysis Statistics}"]
        
        # Statistics table
        latex_parts.append("\\begin{tabular}{ll}")
        latex_parts.append("\\toprule")
        latex_parts.append("\\textbf{Metric} & \\textbf{Count} \\\\")
        latex_parts.append("\\midrule")
        
        stats_items = [
            ("total_pages", "Pages"),
            ("total_words", "Words"),
            ("sections_found", "Sections"),
            ("figures_found", "Figures"),
            ("tables_found", "Tables"),
            ("references_found", "References"),
            ("equations_found", "Equations")
        ]
        
        for key, label in stats_items:
            if key in summary:
                latex_parts.append(f"{label} & {summary[key]} \\\\")
        
        latex_parts.append("\\bottomrule")
        latex_parts.append("\\end{tabular}")
        
        return '\n'.join(latex_parts)

class XMLFormatter(BaseFormatter):
    """XML output formatter"""
    
    def __init__(self, config: FormatConfig = None):
        super().__init__(config)
        self.output_format = OutputFormat.XML
    
    def format(self, data: Dict[str, Any], output_path: str) -> bool:
        """Format data as XML"""
        try:
            root = self._create_xml_tree(data)
            
            # Pretty print if configured
            if self.config.xml_pretty_print:
                xml_str = self._prettify_xml(root)
            else:
                xml_str = ET.tostring(root, encoding='unicode')
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write(xml_str)
            
            logger.info(f"XML output saved to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to format XML: {e}")
            return False
    
    def _create_xml_tree(self, data: Dict[str, Any]) -> ET.Element:
        """Create XML tree from data"""
        root = ET.Element("paper2data_analysis")
        root.set("timestamp", data.get("extraction_timestamp", ""))
        
        # Document metadata
        if self.config.include_metadata and data.get("metadata"):
            metadata_elem = ET.SubElement(root, "metadata")
            self._add_dict_to_xml(metadata_elem, data["metadata"])
        
        # Content
        if data.get("content"):
            content_elem = ET.SubElement(root, "content")
            self._add_dict_to_xml(content_elem, data["content"])
        
        # Sections
        if data.get("sections"):
            sections_elem = ET.SubElement(root, "sections")
            self._add_dict_to_xml(sections_elem, data["sections"])
        
        # Figures
        if self.config.include_figures and data.get("figures"):
            figures_elem = ET.SubElement(root, "figures")
            self._add_dict_to_xml(figures_elem, data["figures"])
        
        # Tables
        if self.config.include_tables and data.get("tables"):
            tables_elem = ET.SubElement(root, "tables")
            self._add_dict_to_xml(tables_elem, data["tables"])
        
        # Equations
        if self.config.include_equations and data.get("equations"):
            equations_elem = ET.SubElement(root, "equations")
            self._add_dict_to_xml(equations_elem, data["equations"])
        
        # Citations
        if self.config.include_citations and data.get("citations"):
            citations_elem = ET.SubElement(root, "citations")
            self._add_dict_to_xml(citations_elem, data["citations"])
        
        # Networks
        if self.config.include_networks and data.get("citation_networks"):
            networks_elem = ET.SubElement(root, "citation_networks")
            self._add_dict_to_xml(networks_elem, data["citation_networks"])
        
        # Statistics
        if self.config.include_statistics and data.get("summary"):
            summary_elem = ET.SubElement(root, "summary")
            self._add_dict_to_xml(summary_elem, data["summary"])
        
        return root
    
    def _add_dict_to_xml(self, parent: ET.Element, data: Any, key_name: str = None):
        """Recursively add dictionary data to XML element"""
        if isinstance(data, dict):
            for key, value in data.items():
                child = ET.SubElement(parent, self._sanitize_xml_tag(str(key)))
                self._add_dict_to_xml(child, value, key)
        elif isinstance(data, list):
            for i, item in enumerate(data):
                item_elem = ET.SubElement(parent, "item")
                item_elem.set("index", str(i))
                self._add_dict_to_xml(item_elem, item)
        else:
            # Simple value
            parent.text = str(data) if data is not None else ""
    
    def _sanitize_xml_tag(self, tag: str) -> str:
        """Sanitize string to be valid XML tag"""
        # Replace invalid characters with underscores
        import re
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', tag)
        # Ensure it starts with a letter or underscore
        if sanitized and not sanitized[0].isalpha() and sanitized[0] != '_':
            sanitized = '_' + sanitized
        return sanitized or 'element'
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        """Return pretty-printed XML string"""
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")[23:]  # Remove XML declaration

class CSVFormatter(BaseFormatter):
    """CSV output formatter for tabular data"""
    
    def __init__(self, config: FormatConfig = None):
        super().__init__(config)
        self.output_format = OutputFormat.CSV
    
    def format(self, data: Dict[str, Any], output_path: str) -> bool:
        """Format data as CSV (creates multiple files)"""
        try:
            base_path = output_path.rsplit('.', 1)[0] if '.' in output_path else output_path
            
            # Create separate CSV files for different data types
            files_created = []
            
            # Summary statistics
            if self.config.include_statistics and data.get("summary"):
                stats_path = f"{base_path}_statistics.csv"
                if self._create_statistics_csv(data["summary"], stats_path):
                    files_created.append(stats_path)
            
            # Metadata
            if self.config.include_metadata and data.get("metadata"):
                metadata_path = f"{base_path}_metadata.csv"
                if self._create_metadata_csv(data["metadata"], metadata_path):
                    files_created.append(metadata_path)
            
            # Tables
            if self.config.include_tables and data.get("tables", {}).get("tables"):
                tables_path = f"{base_path}_tables.csv"
                if self._create_tables_csv(data["tables"]["tables"], tables_path):
                    files_created.append(tables_path)
            
            # Citations
            if self.config.include_citations and data.get("citations", {}).get("references"):
                citations_path = f"{base_path}_citations.csv"
                if self._create_citations_csv(data["citations"]["references"], citations_path):
                    files_created.append(citations_path)
            
            # Equations
            if self.config.include_equations and data.get("equations", {}).get("equations"):
                equations_path = f"{base_path}_equations.csv"
                if self._create_equations_csv(data["equations"]["equations"], equations_path):
                    files_created.append(equations_path)
            
            # Figures
            if self.config.include_figures and data.get("figures", {}).get("figures"):
                figures_path = f"{base_path}_figures.csv"
                if self._create_figures_csv(data["figures"]["figures"], figures_path):
                    files_created.append(figures_path)
            
            logger.info(f"CSV files created: {', '.join(files_created)}")
            return len(files_created) > 0
        
        except Exception as e:
            logger.error(f"Failed to format CSV: {e}")
            return False
    
    def _create_statistics_csv(self, summary: Dict[str, Any], output_path: str) -> bool:
        """Create statistics CSV file"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=self.config.csv_delimiter)
                writer.writerow(["Metric", "Value"])
                
                for key, value in summary.items():
                    if isinstance(value, (str, int, float, bool)):
                        writer.writerow([key, value])
            
            return True
        except Exception as e:
            logger.error(f"Failed to create statistics CSV: {e}")
            return False
    
    def _create_metadata_csv(self, metadata: Dict[str, Any], output_path: str) -> bool:
        """Create metadata CSV file"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=self.config.csv_delimiter)
                writer.writerow(["Field", "Value"])
                
                # Flatten metadata for CSV
                flattened = self._flatten_dict(metadata)
                for key, value in flattened.items():
                    writer.writerow([key, value])
            
            return True
        except Exception as e:
            logger.error(f"Failed to create metadata CSV: {e}")
            return False
    
    def _create_tables_csv(self, tables: List[Dict[str, Any]], output_path: str) -> bool:
        """Create tables CSV file"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=self.config.csv_delimiter)
                writer.writerow(["Table_ID", "Caption", "Page", "Row_Index", "Data"])
                
                for table_idx, table in enumerate(tables):
                    caption = table.get("caption", f"Table {table_idx + 1}")
                    page = table.get("page", "")
                    
                    if table.get("data"):
                        for row_idx, row in enumerate(table["data"]):
                            if isinstance(row, list):
                                row_data = self.config.csv_delimiter.join([str(cell) for cell in row])
                            else:
                                row_data = str(row)
                            
                            writer.writerow([table_idx + 1, caption, page, row_idx + 1, row_data])
            
            return True
        except Exception as e:
            logger.error(f"Failed to create tables CSV: {e}")
            return False
    
    def _create_citations_csv(self, citations: List[Dict[str, Any]], output_path: str) -> bool:
        """Create citations CSV file"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=self.config.csv_delimiter)
                writer.writerow(["Citation_ID", "Text", "Authors", "Title", "Year", "DOI", "URL"])
                
                for idx, citation in enumerate(citations):
                    authors = ""
                    if citation.get("authors"):
                        if isinstance(citation["authors"], list):
                            authors = "; ".join([str(a) for a in citation["authors"]])
                        else:
                            authors = str(citation["authors"])
                    
                    writer.writerow([
                        idx + 1,
                        citation.get("text", ""),
                        authors,
                        citation.get("title", ""),
                        citation.get("year", ""),
                        citation.get("doi", ""),
                        citation.get("url", "")
                    ])
            
            return True
        except Exception as e:
            logger.error(f"Failed to create citations CSV: {e}")
            return False
    
    def _create_equations_csv(self, equations: List[Dict[str, Any]], output_path: str) -> bool:
        """Create equations CSV file"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=self.config.csv_delimiter)
                writer.writerow(["Equation_ID", "Text", "LaTeX", "Page", "Confidence"])
                
                for idx, equation in enumerate(equations):
                    writer.writerow([
                        idx + 1,
                        equation.get("text", ""),
                        equation.get("latex", ""),
                        equation.get("page", ""),
                        equation.get("confidence", "")
                    ])
            
            return True
        except Exception as e:
            logger.error(f"Failed to create equations CSV: {e}")
            return False
    
    def _create_figures_csv(self, figures: List[Dict[str, Any]], output_path: str) -> bool:
        """Create figures CSV file"""
        try:
            with open(output_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f, delimiter=self.config.csv_delimiter)
                writer.writerow(["Figure_ID", "Caption", "Page", "Width", "Height", "Type"])
                
                for idx, figure in enumerate(figures):
                    writer.writerow([
                        idx + 1,
                        figure.get("caption", ""),
                        figure.get("page", ""),
                        figure.get("width", ""),
                        figure.get("height", ""),
                        figure.get("type", "")
                    ])
            
            return True
        except Exception as e:
            logger.error(f"Failed to create figures CSV: {e}")
            return False
    
    def _flatten_dict(self, d: Dict[str, Any], parent_key: str = '', sep: str = '.') -> Dict[str, str]:
        """Flatten nested dictionary for CSV output"""
        items = []
        for k, v in d.items():
            new_key = f"{parent_key}{sep}{k}" if parent_key else k
            if isinstance(v, dict):
                items.extend(self._flatten_dict(v, new_key, sep=sep).items())
            elif isinstance(v, list):
                # Convert lists to semicolon-separated strings
                if v and all(isinstance(item, (str, int, float)) for item in v):
                    items.append((new_key, "; ".join([str(item) for item in v])))
                else:
                    items.append((new_key, f"[{len(v)} items]"))
            else:
                items.append((new_key, str(v) if v is not None else ""))
        return dict(items)

class MarkdownFormatter(BaseFormatter):
    """Markdown output formatter"""
    
    def __init__(self, config: FormatConfig = None):
        super().__init__(config)
        self.output_format = OutputFormat.MARKDOWN
    
    def format(self, data: Dict[str, Any], output_path: str) -> bool:
        """Format data as Markdown"""
        try:
            markdown_content = self._generate_markdown(data)
            
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(markdown_content)
            
            logger.info(f"Markdown output saved to {output_path}")
            return True
        
        except Exception as e:
            logger.error(f"Failed to format Markdown: {e}")
            return False
    
    def _generate_markdown(self, data: Dict[str, Any]) -> str:
        """Generate complete Markdown document"""
        title = self._get_title(data)
        timestamp = self._format_timestamp(data.get("extraction_timestamp", ""))
        
        md_parts = []
        
        # Title and metadata
        md_parts.append(f"# {title}")
        md_parts.append(f"*Analysis performed: {timestamp}*")
        md_parts.append("")
        
        # Table of contents
        if self.config.markdown_include_toc:
            md_parts.append(self._generate_toc_markdown(data))
        
        # Content sections
        if self.config.include_metadata:
            md_parts.append(self._format_metadata_markdown(data.get("metadata", {})))
        
        md_parts.append(self._format_content_markdown(data.get("content", {})))
        md_parts.append(self._format_sections_markdown(data.get("sections", {})))
        
        if self.config.include_figures:
            md_parts.append(self._format_figures_markdown(data.get("figures", {})))
        
        if self.config.include_tables:
            md_parts.append(self._format_tables_markdown(data.get("tables", {})))
        
        if self.config.include_equations:
            md_parts.append(self._format_equations_markdown(data.get("equations", {})))
        
        if self.config.include_citations:
            md_parts.append(self._format_citations_markdown(data.get("citations", {})))
        
        if self.config.include_networks:
            md_parts.append(self._format_networks_markdown(data.get("citation_networks", {})))
        
        if self.config.include_statistics:
            md_parts.append(self._format_statistics_markdown(data.get("summary", {})))
        
        # Footer
        md_parts.append("---")
        md_parts.append("*Generated by Paper2Data - Academic Document Analysis System*")
        
        return '\n'.join(md_parts)
    
    def _generate_toc_markdown(self, data: Dict[str, Any]) -> str:
        """Generate table of contents in Markdown"""
        toc_items = ["## Table of Contents", ""]
        
        if self.config.include_metadata and data.get("metadata"):
            toc_items.append("- [Document Metadata](#document-metadata)")
        
        toc_items.append("- [Document Content](#document-content)")
        toc_items.append("- [Document Sections](#document-sections)")
        
        if self.config.include_figures and data.get("figures"):
            toc_items.append("- [Figures & Images](#figures--images)")
        
        if self.config.include_tables and data.get("tables"):
            toc_items.append("- [Tables](#tables)")
        
        if self.config.include_equations and data.get("equations"):
            toc_items.append("- [Mathematical Equations](#mathematical-equations)")
        
        if self.config.include_citations and data.get("citations"):
            toc_items.append("- [Citations & References](#citations--references)")
        
        if self.config.include_networks and data.get("citation_networks"):
            toc_items.append("- [Citation Networks](#citation-networks)")
        
        if self.config.include_statistics and data.get("summary"):
            toc_items.append("- [Analysis Statistics](#analysis-statistics)")
        
        toc_items.append("")
        return '\n'.join(toc_items)
    
    def _format_metadata_markdown(self, metadata: Dict[str, Any]) -> str:
        """Format metadata section as Markdown"""
        if not metadata:
            return ""
        
        md_parts = ["## Document Metadata", ""]
        
        # Basic metadata
        if metadata.get("title"):
            md_parts.append(f"**Title:** {metadata['title']}")
        
        if metadata.get("authors"):
            authors = metadata["authors"]
            if isinstance(authors, list):
                author_list = ", ".join([str(a.get("name", a) if isinstance(a, dict) else a) for a in authors])
                md_parts.append(f"**Authors:** {author_list}")
        
        if metadata.get("publication_info"):
            pub_info = metadata["publication_info"]
            if isinstance(pub_info, dict):
                pub_details = []
                if pub_info.get("journal"):
                    pub_details.append(f"Journal: {pub_info['journal']}")
                if pub_info.get("year"):
                    pub_details.append(f"Year: {pub_info['year']}")
                if pub_info.get("volume"):
                    pub_details.append(f"Volume: {pub_info['volume']}")
                if pub_details:
                    md_parts.append(f"**Publication:** {', '.join(pub_details)}")
        
        if metadata.get("doi"):
            md_parts.append(f"**DOI:** [{metadata['doi']}](https://doi.org/{metadata['doi']})")
        
        if metadata.get("keywords"):
            keywords = metadata["keywords"]
            if isinstance(keywords, list):
                keyword_list = ", ".join([f"`{k}`" for k in keywords])
                md_parts.append(f"**Keywords:** {keyword_list}")
        
        # Abstract
        if metadata.get("abstract"):
            md_parts.append("")
            md_parts.append("### Abstract")
            md_parts.append("")
            md_parts.append(metadata["abstract"])
        
        md_parts.append("")
        return '\n'.join(md_parts)
    
    def _format_content_markdown(self, content: Dict[str, Any]) -> str:
        """Format content section as Markdown"""
        md_parts = ["## Document Content", ""]
        
        # Statistics
        if content.get("statistics"):
            stats = content["statistics"]
            md_parts.append("### Content Statistics")
            md_parts.append("")
            
            stats_items = []
            if stats.get("page_count"):
                stats_items.append(f"📄 **Pages:** {stats['page_count']}")
            if stats.get("word_count"):
                stats_items.append(f"📝 **Words:** {stats['word_count']}")
            if stats.get("character_count"):
                stats_items.append(f"🔤 **Characters:** {stats['character_count']}")
            
            md_parts.extend(stats_items)
            md_parts.append("")
        
        # Full text (truncated for readability)
        if content.get("full_text"):
            md_parts.append("### Full Text")
            md_parts.append("")
            text = content["full_text"]
            # Truncate if very long
            if len(text) > 2000:
                text = text[:2000] + "... [truncated]"
            md_parts.append(text)
            md_parts.append("")
        
        return '\n'.join(md_parts)
    
    def _format_sections_markdown(self, sections: Dict[str, Any]) -> str:
        """Format sections as Markdown"""
        md_parts = ["## Document Sections", ""]
        
        if sections.get("sections"):
            for i, section in enumerate(sections["sections"], 1):
                if isinstance(section, dict):
                    title = section.get("title", f"Section {i}")
                    content = section.get("content", "")
                    
                    md_parts.append(f"### {title}")
                    md_parts.append("")
                    if content:
                        # Truncate long sections
                        if len(content) > 1000:
                            content = content[:1000] + "... [truncated]"
                        md_parts.append(content)
                    md_parts.append("")
        
        return '\n'.join(md_parts)
    
    def _format_figures_markdown(self, figures: Dict[str, Any]) -> str:
        """Format figures section as Markdown"""
        if not figures or not figures.get("figures"):
            return ""
        
        md_parts = ["## Figures & Images", ""]
        
        for i, figure in enumerate(figures["figures"], 1):
            if isinstance(figure, dict):
                caption = figure.get("caption", f"Figure {i}")
                
                md_parts.append(f"### Figure {i}")
                md_parts.append("")
                md_parts.append("![Image Not Embedded]()")  # Placeholder
                md_parts.append(f"*{caption}*")
                
                if figure.get("page"):
                    md_parts.append(f"**Page:** {figure['page']}")
                
                md_parts.append("")
        
        return '\n'.join(md_parts)
    
    def _format_tables_markdown(self, tables: Dict[str, Any]) -> str:
        """Format tables section as Markdown"""
        if not tables or not tables.get("tables"):
            return ""
        
        md_parts = ["## Tables", ""]
        
        for i, table in enumerate(tables["tables"], 1):
            if isinstance(table, dict):
                md_parts.append(f"### Table {i}")
                
                if table.get("caption"):
                    md_parts.append(f"*{table['caption']}*")
                
                md_parts.append("")
                
                # Markdown table
                if table.get("data"):
                    # Headers
                    if table.get("headers"):
                        header_row = "| " + " | ".join([str(h) for h in table["headers"]]) + " |"
                        separator = "| " + " | ".join(["---"] * len(table["headers"])) + " |"
                        md_parts.append(header_row)
                        md_parts.append(separator)
                    
                    # Data rows
                    for row in table["data"]:
                        if isinstance(row, list):
                            row_text = "| " + " | ".join([str(cell) for cell in row]) + " |"
                            md_parts.append(row_text)
                
                if table.get("page"):
                    md_parts.append(f"**Page:** {table['page']}")
                
                md_parts.append("")
        
        return '\n'.join(md_parts)
    
    def _format_equations_markdown(self, equations: Dict[str, Any]) -> str:
        """Format equations section as Markdown"""
        if not equations or not equations.get("equations"):
            return ""
        
        md_parts = ["## Mathematical Equations", ""]
        
        for i, equation in enumerate(equations["equations"], 1):
            if isinstance(equation, dict):
                md_parts.append(f"### Equation {i}")
                md_parts.append("")
                
                # LaTeX code block
                if equation.get("latex"):
                    md_parts.append("```latex")
                    md_parts.append(equation["latex"])
                    md_parts.append("```")
                
                # Original text
                if equation.get("text"):
                    md_parts.append(f"**Original:** {equation['text']}")
                
                if equation.get("page"):
                    md_parts.append(f"**Page:** {equation['page']}")
                
                md_parts.append("")
        
        return '\n'.join(md_parts)
    
    def _format_citations_markdown(self, citations: Dict[str, Any]) -> str:
        """Format citations section as Markdown"""
        if not citations:
            return ""
        
        md_parts = ["## Citations & References", ""]
        
        # References
        if citations.get("references"):
            md_parts.append("### References")
            md_parts.append("")
            
            for i, ref in enumerate(citations["references"], 1):
                if isinstance(ref, dict):
                    md_parts.append(f"{i}. {ref.get('text', 'No text available')}")
                    
                    # Additional details
                    details = []
                    if ref.get("authors"):
                        authors = ref["authors"]
                        if isinstance(authors, list):
                            details.append(f"**Authors:** {', '.join(authors)}")
                    
                    if ref.get("year"):
                        details.append(f"**Year:** {ref['year']}")
                    
                    if ref.get("doi"):
                        details.append(f"**DOI:** [{ref['doi']}](https://doi.org/{ref['doi']})")
                    
                    if details:
                        md_parts.append(f"   {' | '.join(details)}")
                    
                    md_parts.append("")
        
        # In-text citations
        if citations.get("in_text_citations"):
            md_parts.append("### In-text Citations")
            md_parts.append("")
            md_parts.append(f"Found **{len(citations['in_text_citations'])}** in-text citations throughout the document.")
            md_parts.append("")
        
        return '\n'.join(md_parts)
    
    def _format_networks_markdown(self, networks: Dict[str, Any]) -> str:
        """Format citation networks section as Markdown"""
        if not networks or not networks.get("networks"):
            return ""
        
        md_parts = ["## Citation Networks", ""]
        
        # Network summary
        md_parts.append("### Network Summary")
        md_parts.append("")
        
        for network_name, network_data in networks["networks"].items():
            if isinstance(network_data, dict) and "basic_metrics" in network_data:
                metrics = network_data["basic_metrics"]
                
                md_parts.append(f"#### {network_name.replace('_', ' ').title()}")
                md_parts.append(f"- **Nodes:** {metrics.get('num_nodes', 0)}")
                md_parts.append(f"- **Edges:** {metrics.get('num_edges', 0)}")
                md_parts.append(f"- **Density:** {metrics.get('density', 0):.3f}")
                md_parts.append("")
        
        # Author analysis
        if networks.get("author_analysis"):
            md_parts.append("### Author Analysis")
            md_parts.append("")
            author_count = len(networks["author_analysis"])
            md_parts.append(f"Analyzed **{author_count}** authors and their collaboration patterns.")
            md_parts.append("")
        
        # Influence analysis
        if networks.get("influence_analysis"):
            md_parts.append("### Citation Influence")
            md_parts.append("")
            influence_count = len(networks["influence_analysis"])
            md_parts.append(f"Calculated influence scores for **{influence_count}** papers.")
            md_parts.append("")
        
        return '\n'.join(md_parts)
    
    def _format_statistics_markdown(self, summary: Dict[str, Any]) -> str:
        """Format statistics section as Markdown"""
        if not summary:
            return ""
        
        md_parts = ["## Analysis Statistics", ""]
        
        # Create statistics table
        md_parts.append("| Metric | Count |")
        md_parts.append("|--------|-------|")
        
        stats_items = [
            ("total_pages", "Pages"),
            ("total_words", "Words"),
            ("sections_found", "Sections"),
            ("figures_found", "Figures"),
            ("tables_found", "Tables"),
            ("references_found", "References"),
            ("equations_found", "Equations"),
            ("authors_found", "Authors"),
            ("keywords_found", "Keywords")
        ]
        
        for key, label in stats_items:
            if key in summary:
                md_parts.append(f"| {label} | {summary[key]} |")
        
        md_parts.append("")
        
        # Quality indicators
        quality_items = []
        if summary.get("metadata_extracted"):
            quality_items.append("✅ Metadata Extracted")
        if summary.get("citation_networks_analyzed"):
            quality_items.append("✅ Networks Analyzed")
        if summary.get("doi_found"):
            quality_items.append("✅ DOI Found")
        
        if quality_items:
            md_parts.append("### Quality Indicators")
            md_parts.append("")
            for item in quality_items:
                md_parts.append(f"- {item}")
            md_parts.append("")
        
        return '\n'.join(md_parts)

# Document (DOCX) formatter placeholder - requires python-docx
class DOCXFormatter(BaseFormatter):
    """Microsoft Word (DOCX) output formatter"""
    
    def __init__(self, config: FormatConfig = None):
        super().__init__(config)
        self.output_format = OutputFormat.DOCX
    
    def format(self, data: Dict[str, Any], output_path: str) -> bool:
        """Format data as DOCX (requires python-docx)"""
        try:
            # This would require python-docx package
            logger.warning("DOCX formatting requires python-docx package (not implemented)")
            return False
        
        except Exception as e:
            logger.error(f"Failed to format DOCX: {e}")
            return False

class FormatterFactory:
    """Factory class for creating output formatters"""
    
    _formatters = {
        OutputFormat.JSON: JSONFormatter,
        OutputFormat.HTML: HTMLFormatter,
        OutputFormat.LATEX: LaTeXFormatter,
        OutputFormat.XML: XMLFormatter,
        OutputFormat.CSV: CSVFormatter,
        OutputFormat.MARKDOWN: MarkdownFormatter,
        OutputFormat.DOCX: DOCXFormatter,
    }
    
    @classmethod
    def create_formatter(cls, output_format: OutputFormat, config: FormatConfig = None) -> BaseFormatter:
        """Create formatter instance for specified format"""
        if output_format not in cls._formatters:
            raise ValueError(f"Unsupported output format: {output_format}")
        
        formatter_class = cls._formatters[output_format]
        return formatter_class(config)
    
    @classmethod
    def get_supported_formats(cls) -> List[OutputFormat]:
        """Get list of supported output formats"""
        return list(cls._formatters.keys())

def format_output(data: Dict[str, Any], output_path: str, 
                 output_format: Union[OutputFormat, str], 
                 config: FormatConfig = None) -> bool:
    """
    Format extraction results to specified output format
    
    Args:
        data: Paper2Data extraction results
        output_path: Path where to save formatted output
        output_format: Target format (OutputFormat enum or string)
        config: Formatting configuration
    
    Returns:
        True if formatting successful, False otherwise
    """
    try:
        # Convert string to enum if needed
        if isinstance(output_format, str):
            output_format = OutputFormat(output_format.lower())
        
        # Create formatter
        formatter = FormatterFactory.create_formatter(output_format, config)
        
        # Format and save
        return formatter.format(data, output_path)
    
    except Exception as e:
        logger.error(f"Failed to format output: {e}")
        return False

def batch_format(data: Dict[str, Any], base_output_path: str, 
                formats: List[Union[OutputFormat, str]], 
                config: FormatConfig = None) -> Dict[str, bool]:
    """
    Format extraction results to multiple output formats
    
    Args:
        data: Paper2Data extraction results
        base_output_path: Base path for output files (extension will be added)
        formats: List of target formats
        config: Formatting configuration
    
    Returns:
        Dictionary mapping format names to success status
    """
    results = {}
    base_name = base_output_path.rsplit('.', 1)[0] if '.' in base_output_path else base_output_path
    
    for fmt in formats:
        try:
            # Convert string to enum if needed
            if isinstance(fmt, str):
                fmt_enum = OutputFormat(fmt.lower())
            else:
                fmt_enum = fmt
            
            # Generate output path with appropriate extension
            output_path = f"{base_name}.{fmt_enum.value}"
            
            # Format output
            success = format_output(data, output_path, fmt_enum, config)
            results[fmt_enum.value] = success
            
        except Exception as e:
            logger.error(f"Failed to format {fmt}: {e}")
            results[str(fmt)] = False
    
    return results

# Global instance for easy access
default_config = FormatConfig()

def export_to_html(data: Dict[str, Any], output_path: str, config: FormatConfig = None) -> bool:
    """Export data to HTML format"""
    return format_output(data, output_path, OutputFormat.HTML, config or default_config)

def export_to_latex(data: Dict[str, Any], output_path: str, config: FormatConfig = None) -> bool:
    """Export data to LaTeX format"""
    return format_output(data, output_path, OutputFormat.LATEX, config or default_config)

def export_to_xml(data: Dict[str, Any], output_path: str, config: FormatConfig = None) -> bool:
    """Export data to XML format"""
    return format_output(data, output_path, OutputFormat.XML, config or default_config)

def export_to_csv(data: Dict[str, Any], output_path: str, config: FormatConfig = None) -> bool:
    """Export data to CSV format"""
    return format_output(data, output_path, OutputFormat.CSV, config or default_config)

def export_to_markdown(data: Dict[str, Any], output_path: str, config: FormatConfig = None) -> bool:
    """Export data to Markdown format"""
    return format_output(data, output_path, OutputFormat.MARKDOWN, config or default_config)

def export_all_formats(data: Dict[str, Any], base_output_path: str, config: FormatConfig = None) -> Dict[str, bool]:
    """Export data to all supported formats"""
    supported_formats = [OutputFormat.JSON, OutputFormat.HTML, OutputFormat.LATEX, 
                        OutputFormat.XML, OutputFormat.CSV, OutputFormat.MARKDOWN]
    return batch_format(data, base_output_path, supported_formats, config or default_config) 
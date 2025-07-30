"""
Multi-Format Output System for Paper2Data V1.1

Provides template-based export capabilities for extracted academic paper content
to multiple formats: HTML, LaTeX, Word (DOCX), and EPUB.
"""

import os
import json
import yaml
import shutil
from pathlib import Path
from typing import Dict, Any, List, Optional, Union, Tuple
from datetime import datetime
from dataclasses import dataclass, field
from enum import Enum
import tempfile
import zipfile
import re
import base64
from urllib.parse import quote

from .utils import get_logger, ProcessingError, ensure_directory, save_json
from .enhanced_metadata_v1_1 import EnhancedMetadataExtractor
from .bibliographic_parser import BibliographicParser


class OutputFormat(Enum):
    """Supported output formats."""
    HTML = "html"
    LATEX = "latex"
    WORD = "word"
    EPUB = "epub"
    MARKDOWN = "markdown"
    PDF = "pdf"  # Generated from LaTeX


class TemplateTheme(Enum):
    """Available template themes."""
    ACADEMIC = "academic"
    MODERN = "modern"
    MINIMAL = "minimal"
    JOURNAL = "journal"
    CONFERENCE = "conference"


@dataclass
class ExportConfiguration:
    """Configuration for multi-format export."""
    format: OutputFormat
    theme: TemplateTheme = TemplateTheme.ACADEMIC
    include_figures: bool = True
    include_tables: bool = True
    include_equations: bool = True
    include_bibliography: bool = True
    include_metadata: bool = True
    interactive_elements: bool = True  # For HTML format
    generate_toc: bool = True
    custom_css: Optional[str] = None
    custom_template: Optional[str] = None
    output_filename: Optional[str] = None
    embed_media: bool = True
    quality_settings: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExportedDocument:
    """Result of document export."""
    format: OutputFormat
    file_path: Path
    file_size: int
    creation_time: datetime
    metadata: Dict[str, Any]
    assets: List[Path] = field(default_factory=list)
    warnings: List[str] = field(default_factory=list)
    errors: List[str] = field(default_factory=list)


class MultiFormatExporter:
    """Main class for exporting Paper2Data content to multiple formats."""
    
    def __init__(self, extraction_results: Dict[str, Any], output_dir: Path = None):
        """Initialize the multi-format exporter.
        
        Args:
            extraction_results: Complete extraction results from Paper2Data
            output_dir: Base directory for output files
        """
        self.logger = get_logger(__name__)
        self.extraction_results = extraction_results
        self.output_dir = output_dir or Path("./paper2data_export")
        self.templates_dir = Path(__file__).parent / "templates"
        
        # Create output directory
        ensure_directory(self.output_dir)
        
        # Initialize format-specific exporters
        self.html_exporter = HTMLExporter(self)
        self.latex_exporter = LaTeXExporter(self)
        self.word_exporter = WordExporter(self)
        self.epub_exporter = EPUBExporter(self)
        self.markdown_exporter = MarkdownExporter(self)
        
        self.logger.info(f"Multi-format exporter initialized with output directory: {self.output_dir}")
    
    def export_single_format(self, config: ExportConfiguration) -> ExportedDocument:
        """Export to a single format.
        
        Args:
            config: Export configuration
            
        Returns:
            ExportedDocument with results
        """
        self.logger.info(f"Starting export to {config.format.value} format")
        
        try:
            if config.format == OutputFormat.HTML:
                return self.html_exporter.export(config)
            elif config.format == OutputFormat.LATEX:
                return self.latex_exporter.export(config)
            elif config.format == OutputFormat.WORD:
                return self.word_exporter.export(config)
            elif config.format == OutputFormat.EPUB:
                return self.epub_exporter.export(config)
            elif config.format == OutputFormat.MARKDOWN:
                return self.markdown_exporter.export(config)
            else:
                raise ProcessingError(f"Unsupported format: {config.format}")
                
        except Exception as e:
            self.logger.error(f"Export failed for format {config.format.value}: {str(e)}")
            raise ProcessingError(f"Export failed: {str(e)}")
    
    def export_multiple_formats(self, configs: List[ExportConfiguration]) -> Dict[OutputFormat, ExportedDocument]:
        """Export to multiple formats.
        
        Args:
            configs: List of export configurations
            
        Returns:
            Dictionary mapping formats to exported documents
        """
        results = {}
        
        for config in configs:
            try:
                result = self.export_single_format(config)
                results[config.format] = result
                self.logger.info(f"Successfully exported to {config.format.value}")
            except Exception as e:
                self.logger.error(f"Failed to export to {config.format.value}: {str(e)}")
                # Continue with other formats
        
        return results
    
    def create_export_package(self, formats: List[OutputFormat], 
                            theme: TemplateTheme = TemplateTheme.ACADEMIC) -> Path:
        """Create a complete export package with multiple formats.
        
        Args:
            formats: List of formats to export
            theme: Template theme to use
            
        Returns:
            Path to the created package (ZIP file)
        """
        package_dir = self.output_dir / "export_package"
        ensure_directory(package_dir)
        
        # Create configurations for each format
        configs = []
        for format_type in formats:
            config = ExportConfiguration(
                format=format_type,
                theme=theme,
                include_figures=True,
                include_tables=True,
                include_equations=True,
                include_bibliography=True,
                include_metadata=True,
                interactive_elements=True,
                generate_toc=True
            )
            configs.append(config)
        
        # Export to all formats
        results = self.export_multiple_formats(configs)
        
        # Create package manifest
        manifest = {
            "package_created": datetime.now().isoformat(),
            "source_paper": self.extraction_results.get("content", {}).get("metadata", {}),
            "formats": [],
            "theme": theme.value,
            "total_files": 0
        }
        
        for format_type, result in results.items():
            manifest["formats"].append({
                "format": format_type.value,
                "file_path": str(result.file_path.relative_to(self.output_dir)),
                "file_size": result.file_size,
                "creation_time": result.creation_time.isoformat(),
                "assets": [str(asset.relative_to(self.output_dir)) for asset in result.assets]
            })
            manifest["total_files"] += 1 + len(result.assets)
        
        # Save manifest
        manifest_path = package_dir / "manifest.json"
        save_json(manifest, manifest_path)
        
        # Create ZIP package
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        paper_title = self.extraction_results.get("content", {}).get("metadata", {}).get("title", "paper")
        safe_title = re.sub(r'[^\w\s-]', '', paper_title).strip()[:50]
        zip_path = self.output_dir / f"{safe_title}_{timestamp}.zip"
        
        with zipfile.ZipFile(zip_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
            for root, dirs, files in os.walk(self.output_dir):
                for file in files:
                    if file.endswith('.zip'):
                        continue  # Don't include other zip files
                    file_path = Path(root) / file
                    arcname = file_path.relative_to(self.output_dir)
                    zipf.write(file_path, arcname)
        
        self.logger.info(f"Created export package: {zip_path}")
        return zip_path
    
    def get_template_path(self, format_type: OutputFormat, theme: TemplateTheme, 
                         template_name: str) -> Path:
        """Get path to a template file.
        
        Args:
            format_type: Output format
            theme: Template theme
            template_name: Name of the template file
            
        Returns:
            Path to template file
        """
        template_path = self.templates_dir / format_type.value / theme.value / template_name
        
        if not template_path.exists():
            # Fall back to default theme
            template_path = self.templates_dir / format_type.value / "academic" / template_name
        
        if not template_path.exists():
            raise ProcessingError(f"Template not found: {template_path}")
        
        return template_path
    
    def prepare_content_for_export(self, config: ExportConfiguration) -> Dict[str, Any]:
        """Prepare and sanitize content for export.
        
        Args:
            config: Export configuration
            
        Returns:
            Prepared content dictionary
        """
        content = {
            "metadata": {},
            "sections": {},
            "figures": [],
            "tables": [],
            "equations": [],
            "bibliography": [],
            "toc": []
        }
        
        # Extract metadata
        if config.include_metadata:
            content["metadata"] = self.extraction_results.get("content", {}).get("metadata", {})
        
        # Extract sections
        sections = self.extraction_results.get("sections", {}).get("sections", {})
        for section_name, section_content in sections.items():
            if section_content and section_content.strip():
                content["sections"][section_name] = self._sanitize_content(section_content, config.format)
        
        # Extract figures
        if config.include_figures:
            figures = self.extraction_results.get("figures", {}).get("figures", [])
            for figure in figures:
                content["figures"].append(self._prepare_figure(figure, config))
        
        # Extract tables
        if config.include_tables:
            tables = self.extraction_results.get("tables", {}).get("tables", [])
            for table in tables:
                content["tables"].append(self._prepare_table(table, config))
        
        # Extract equations
        if config.include_equations:
            equations = self.extraction_results.get("equations", {}).get("equations", [])
            for equation in equations:
                content["equations"].append(self._prepare_equation(equation, config))
        
        # Extract bibliography
        if config.include_bibliography:
            citations = self.extraction_results.get("citations", {}).get("references", [])
            content["bibliography"] = self._prepare_bibliography(citations, config)
        
        # Generate table of contents
        if config.generate_toc:
            content["toc"] = self._generate_toc(content["sections"])
        
        return content
    
    def _sanitize_content(self, content: str, format_type: OutputFormat) -> str:
        """Sanitize content for specific output format.
        
        Args:
            content: Raw content string
            format_type: Target output format
            
        Returns:
            Sanitized content string
        """
        if format_type == OutputFormat.HTML:
            # Escape HTML special characters
            content = content.replace('&', '&amp;')
            content = content.replace('<', '&lt;')
            content = content.replace('>', '&gt;')
            content = content.replace('"', '&quot;')
            content = content.replace("'", '&#39;')
        
        elif format_type == OutputFormat.LATEX:
            # Escape LaTeX special characters
            latex_chars = {
                '&': r'\&',
                '%': r'\%',
                '$': r'\$',
                '#': r'\#',
                '^': r'\textasciicircum{}',
                '_': r'\_',
                '{': r'\{',
                '}': r'\}',
                '~': r'\textasciitilde{}',
                '\\': r'\textbackslash{}'
            }
            for char, replacement in latex_chars.items():
                content = content.replace(char, replacement)
        
        elif format_type == OutputFormat.WORD:
            # Basic XML escaping for Word
            content = content.replace('&', '&amp;')
            content = content.replace('<', '&lt;')
            content = content.replace('>', '&gt;')
        
        return content
    
    def _prepare_figure(self, figure: Dict[str, Any], config: ExportConfiguration) -> Dict[str, Any]:
        """Prepare figure data for export.
        
        Args:
            figure: Figure data
            config: Export configuration
            
        Returns:
            Prepared figure data
        """
        prepared = {
            "id": figure.get("figure_id", "unknown"),
            "caption": figure.get("caption", ""),
            "data": None,
            "format": figure.get("format", "png"),
            "size": figure.get("size", {}),
            "alt_text": figure.get("alt_text", "")
        }
        
        if config.embed_media and "data" in figure:
            if config.format == OutputFormat.HTML:
                # Base64 encode for HTML
                img_data = base64.b64encode(figure["data"]).decode('utf-8')
                prepared["data"] = f"data:image/png;base64,{img_data}"
            else:
                prepared["data"] = figure["data"]
        
        return prepared
    
    def _prepare_table(self, table: Dict[str, Any], config: ExportConfiguration) -> Dict[str, Any]:
        """Prepare table data for export.
        
        Args:
            table: Table data
            config: Export configuration
            
        Returns:
            Prepared table data
        """
        prepared = {
            "id": table.get("table_id", "unknown"),
            "caption": table.get("caption", ""),
            "data": table.get("csv_content", table.get("raw_text", "")),
            "format": "csv" if "csv_content" in table else "text",
            "rows": table.get("rows", []),
            "columns": table.get("columns", [])
        }
        
        return prepared
    
    def _prepare_equation(self, equation: Dict[str, Any], config: ExportConfiguration) -> Dict[str, Any]:
        """Prepare equation data for export.
        
        Args:
            equation: Equation data
            config: Export configuration
            
        Returns:
            Prepared equation data
        """
        prepared = {
            "id": equation.get("equation_id", "unknown"),
            "latex": equation.get("latex", ""),
            "mathml": equation.get("mathml", ""),
            "image": equation.get("image", None),
            "context": equation.get("context", "")
        }
        
        return prepared
    
    def _prepare_bibliography(self, citations: List[Dict[str, Any]], 
                            config: ExportConfiguration) -> List[Dict[str, Any]]:
        """Prepare bibliography data for export.
        
        Args:
            citations: List of citations
            config: Export configuration
            
        Returns:
            Prepared bibliography data
        """
        prepared = []
        
        for citation in citations:
            prepared_citation = {
                "id": citation.get("citation_id", "unknown"),
                "formatted": citation.get("formatted", ""),
                "authors": citation.get("authors", []),
                "title": citation.get("title", ""),
                "year": citation.get("year", ""),
                "journal": citation.get("journal", ""),
                "doi": citation.get("doi", ""),
                "url": citation.get("url", "")
            }
            prepared.append(prepared_citation)
        
        return prepared
    
    def _generate_toc(self, sections: Dict[str, str]) -> List[Dict[str, Any]]:
        """Generate table of contents from sections.
        
        Args:
            sections: Dictionary of sections
            
        Returns:
            Table of contents structure
        """
        toc = []
        
        for section_name, section_content in sections.items():
            toc_entry = {
                "id": section_name,
                "title": section_name.replace("_", " ").title(),
                "level": 1,
                "page": None,  # Will be set during rendering
                "anchor": f"section_{section_name}"
            }
            toc.append(toc_entry)
        
        return toc


class BaseFormatExporter:
    """Base class for format-specific exporters."""
    
    def __init__(self, main_exporter: MultiFormatExporter):
        """Initialize base exporter.
        
        Args:
            main_exporter: Main multi-format exporter instance
        """
        self.main_exporter = main_exporter
        self.logger = get_logger(f"{__name__}.{self.__class__.__name__}")
    
    def export(self, config: ExportConfiguration) -> ExportedDocument:
        """Export to specific format.
        
        Args:
            config: Export configuration
            
        Returns:
            ExportedDocument with results
        """
        raise NotImplementedError("Subclasses must implement export method")
    
    def load_template(self, template_name: str, config: ExportConfiguration) -> str:
        """Load template content.
        
        Args:
            template_name: Template file name
            config: Export configuration
            
        Returns:
            Template content as string
        """
        template_path = self.main_exporter.get_template_path(
            config.format, config.theme, template_name
        )
        
        with open(template_path, 'r', encoding='utf-8') as f:
            return f.read()
    
    def render_template(self, template_content: str, context: Dict[str, Any]) -> str:
        """Render template with context data.
        
        Args:
            template_content: Template content string
            context: Context data for rendering
            
        Returns:
            Rendered template content
        """
        # Simple template rendering (can be enhanced with Jinja2 or similar)
        rendered = template_content
        
        for key, value in context.items():
            placeholder = f"{{{{{key}}}}}"
            rendered = rendered.replace(placeholder, str(value))
        
        return rendered


class HTMLExporter(BaseFormatExporter):
    """HTML format exporter with interactive features."""
    
    def export(self, config: ExportConfiguration) -> ExportedDocument:
        """Export to HTML format.
        
        Args:
            config: Export configuration
            
        Returns:
            ExportedDocument with HTML results
        """
        self.logger.info("Starting HTML export")
        
        # Prepare content
        content = self.main_exporter.prepare_content_for_export(config)
        
        # Create HTML-specific output directory
        html_dir = self.main_exporter.output_dir / "html"
        ensure_directory(html_dir)
        
        # Create assets directory
        assets_dir = html_dir / "assets"
        ensure_directory(assets_dir)
        
        # Load and render main template
        template_content = self.load_template("main.html", config)
        
        # Prepare context
        context = {
            "title": content["metadata"].get("title", "Academic Paper"),
            "authors": content["metadata"].get("authors", ""),
            "abstract": content["sections"].get("abstract", ""),
            "content": self._render_html_content(content),
            "toc": self._render_html_toc(content["toc"]),
            "bibliography": self._render_html_bibliography(content["bibliography"]),
            "css_styles": self._get_css_styles(config),
            "js_scripts": self._get_js_scripts(config),
            "creation_date": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        
        # Render template
        rendered_html = self.render_template(template_content, context)
        
        # Save HTML file
        output_filename = config.output_filename or "paper.html"
        html_file = html_dir / output_filename
        
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(rendered_html)
        
        # Copy assets
        assets = self._copy_html_assets(assets_dir, content, config)
        
        # Create result
        result = ExportedDocument(
            format=OutputFormat.HTML,
            file_path=html_file,
            file_size=html_file.stat().st_size,
            creation_time=datetime.now(),
            metadata=content["metadata"],
            assets=assets
        )
        
        self.logger.info(f"HTML export completed: {html_file}")
        return result
    
    def _render_html_content(self, content: Dict[str, Any]) -> str:
        """Render HTML content sections.
        
        Args:
            content: Prepared content
            
        Returns:
            Rendered HTML content
        """
        html_parts = []
        
        # Render sections
        for section_name, section_content in content["sections"].items():
            if section_content and section_content.strip():
                html_parts.append(f'<section id="section_{section_name}">')
                html_parts.append(f'<h2>{section_name.replace("_", " ").title()}</h2>')
                html_parts.append(f'<div class="section-content">{section_content}</div>')
                html_parts.append('</section>')
        
        # Render figures
        if content["figures"]:
            html_parts.append('<section id="figures">')
            html_parts.append('<h2>Figures</h2>')
            for figure in content["figures"]:
                html_parts.append(self._render_html_figure(figure))
            html_parts.append('</section>')
        
        # Render tables
        if content["tables"]:
            html_parts.append('<section id="tables">')
            html_parts.append('<h2>Tables</h2>')
            for table in content["tables"]:
                html_parts.append(self._render_html_table(table))
            html_parts.append('</section>')
        
        return '\n'.join(html_parts)
    
    def _render_html_figure(self, figure: Dict[str, Any]) -> str:
        """Render HTML figure.
        
        Args:
            figure: Figure data
            
        Returns:
            Rendered HTML figure
        """
        html = f'<figure id="figure_{figure["id"]}" class="paper-figure">'
        
        if figure["data"]:
            html += f'<img src="{figure["data"]}" alt="{figure["alt_text"]}" />'
        
        if figure["caption"]:
            html += f'<figcaption>{figure["caption"]}</figcaption>'
        
        html += '</figure>'
        return html
    
    def _render_html_table(self, table: Dict[str, Any]) -> str:
        """Render HTML table.
        
        Args:
            table: Table data
            
        Returns:
            Rendered HTML table
        """
        html = f'<div id="table_{table["id"]}" class="paper-table">'
        
        if table["caption"]:
            html += f'<h3>{table["caption"]}</h3>'
        
        if table["format"] == "csv" and table["data"]:
            # Convert CSV to HTML table
            lines = table["data"].split('\n')
            if lines:
                html += '<table>'
                # Header row
                header_cells = lines[0].split(',')
                html += '<thead><tr>'
                for cell in header_cells:
                    html += f'<th>{cell.strip()}</th>'
                html += '</tr></thead>'
                
                # Data rows
                html += '<tbody>'
                for line in lines[1:]:
                    if line.strip():
                        cells = line.split(',')
                        html += '<tr>'
                        for cell in cells:
                            html += f'<td>{cell.strip()}</td>'
                        html += '</tr>'
                html += '</tbody></table>'
        else:
            html += f'<pre>{table["data"]}</pre>'
        
        html += '</div>'
        return html
    
    def _render_html_toc(self, toc: List[Dict[str, Any]]) -> str:
        """Render HTML table of contents.
        
        Args:
            toc: Table of contents data
            
        Returns:
            Rendered HTML TOC
        """
        if not toc:
            return ""
        
        html = '<nav id="table-of-contents"><h2>Table of Contents</h2><ul>'
        
        for entry in toc:
            html += f'<li><a href="#{entry["anchor"]}">{entry["title"]}</a></li>'
        
        html += '</ul></nav>'
        return html
    
    def _render_html_bibliography(self, bibliography: List[Dict[str, Any]]) -> str:
        """Render HTML bibliography.
        
        Args:
            bibliography: Bibliography data
            
        Returns:
            Rendered HTML bibliography
        """
        if not bibliography:
            return ""
        
        html = '<section id="bibliography"><h2>References</h2><ol>'
        
        for citation in bibliography:
            html += f'<li id="citation_{citation["id"]}">'
            html += citation["formatted"]
            html += '</li>'
        
        html += '</ol></section>'
        return html
    
    def _get_css_styles(self, config: ExportConfiguration) -> str:
        """Get CSS styles for HTML export.
        
        Args:
            config: Export configuration
            
        Returns:
            CSS styles string
        """
        try:
            css_template = self.load_template("styles.css", config)
            return css_template
        except Exception:
            # Return default styles if template not found
            return """
            body { font-family: Georgia, serif; line-height: 1.6; margin: 40px; }
            h1, h2, h3 { color: #333; }
            .paper-figure { margin: 20px 0; text-align: center; }
            .paper-table { margin: 20px 0; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            #table-of-contents { margin: 20px 0; }
            """
    
    def _get_js_scripts(self, config: ExportConfiguration) -> str:
        """Get JavaScript scripts for HTML export.
        
        Args:
            config: Export configuration
            
        Returns:
            JavaScript code string
        """
        if not config.interactive_elements:
            return ""
        
        try:
            js_template = self.load_template("scripts.js", config)
            return js_template
        except Exception:
            return ""
    
    def _copy_html_assets(self, assets_dir: Path, content: Dict[str, Any], 
                         config: ExportConfiguration) -> List[Path]:
        """Copy HTML assets to output directory.
        
        Args:
            assets_dir: Assets directory
            content: Content data
            config: Export configuration
            
        Returns:
            List of copied asset paths
        """
        assets = []
        
        # Copy CSS files
        try:
            css_path = self.main_exporter.get_template_path(config.format, config.theme, "styles.css")
            dest_css = assets_dir / "styles.css"
            shutil.copy2(css_path, dest_css)
            assets.append(dest_css)
        except Exception:
            pass
        
        # Copy JS files
        if config.interactive_elements:
            try:
                js_path = self.main_exporter.get_template_path(config.format, config.theme, "scripts.js")
                dest_js = assets_dir / "scripts.js"
                shutil.copy2(js_path, dest_js)
                assets.append(dest_js)
            except Exception:
                pass
        
        return assets


class LaTeXExporter(BaseFormatExporter):
    """LaTeX format exporter for academic paper reconstruction."""
    
    def export(self, config: ExportConfiguration) -> ExportedDocument:
        """Export to LaTeX format.
        
        Args:
            config: Export configuration
            
        Returns:
            ExportedDocument with LaTeX results
        """
        self.logger.info("Starting LaTeX export")
        
        # Prepare content
        content = self.main_exporter.prepare_content_for_export(config)
        
        # Create LaTeX-specific output directory
        latex_dir = self.main_exporter.output_dir / "latex"
        ensure_directory(latex_dir)
        
        # Load and render main template
        template_content = self.load_template("main.tex", config)
        
        # Prepare context
        context = {
            "title": content["metadata"].get("title", "Academic Paper"),
            "authors": self._format_latex_authors(content["metadata"].get("authors", "")),
            "abstract": content["sections"].get("abstract", ""),
            "content": self._render_latex_content(content),
            "bibliography": self._render_latex_bibliography(content["bibliography"]),
            "packages": self._get_latex_packages(config),
            "creation_date": datetime.now().strftime("%Y-%m-%d")
        }
        
        # Render template
        rendered_latex = self.render_template(template_content, context)
        
        # Save LaTeX file
        output_filename = config.output_filename or "paper.tex"
        latex_file = latex_dir / output_filename
        
        with open(latex_file, 'w', encoding='utf-8') as f:
            f.write(rendered_latex)
        
        # Copy assets
        assets = self._copy_latex_assets(latex_dir, content, config)
        
        # Create result
        result = ExportedDocument(
            format=OutputFormat.LATEX,
            file_path=latex_file,
            file_size=latex_file.stat().st_size,
            creation_time=datetime.now(),
            metadata=content["metadata"],
            assets=assets
        )
        
        self.logger.info(f"LaTeX export completed: {latex_file}")
        return result
    
    def _format_latex_authors(self, authors: str) -> str:
        """Format authors for LaTeX.
        
        Args:
            authors: Authors string
            
        Returns:
            LaTeX-formatted authors
        """
        if not authors:
            return ""
        
        # Split by common separators and format for LaTeX
        author_list = re.split(r'[,;]', authors)
        formatted_authors = []
        
        for author in author_list:
            author = author.strip()
            if author:
                formatted_authors.append(f"\\author{{{author}}}")
        
        return '\n'.join(formatted_authors)
    
    def _render_latex_content(self, content: Dict[str, Any]) -> str:
        """Render LaTeX content sections.
        
        Args:
            content: Prepared content
            
        Returns:
            Rendered LaTeX content
        """
        latex_parts = []
        
        # Render sections
        for section_name, section_content in content["sections"].items():
            if section_content and section_content.strip():
                latex_parts.append(f'\\section{{{section_name.replace("_", " ").title()}}}')
                latex_parts.append(f'\\label{{sec:{section_name}}}')
                latex_parts.append(section_content)
                latex_parts.append('')
        
        # Render figures
        if content["figures"]:
            for figure in content["figures"]:
                latex_parts.append(self._render_latex_figure(figure))
        
        # Render tables
        if content["tables"]:
            for table in content["tables"]:
                latex_parts.append(self._render_latex_table(table))
        
        return '\n'.join(latex_parts)
    
    def _render_latex_figure(self, figure: Dict[str, Any]) -> str:
        """Render LaTeX figure.
        
        Args:
            figure: Figure data
            
        Returns:
            Rendered LaTeX figure
        """
        latex = '\\begin{figure}[htbp]\n'
        latex += '\\centering\n'
        
        if figure["data"]:
            # Save figure data to file
            figure_file = f"figure_{figure['id']}.png"
            latex += f'\\includegraphics[width=0.8\\textwidth]{{{figure_file}}}\n'
        
        if figure["caption"]:
            latex += f'\\caption{{{figure["caption"]}}}\n'
        
        latex += f'\\label{{fig:{figure["id"]}}}\n'
        latex += '\\end{figure}\n'
        
        return latex
    
    def _render_latex_table(self, table: Dict[str, Any]) -> str:
        """Render LaTeX table.
        
        Args:
            table: Table data
            
        Returns:
            Rendered LaTeX table
        """
        latex = '\\begin{table}[htbp]\n'
        latex += '\\centering\n'
        
        if table["caption"]:
            latex += f'\\caption{{{table["caption"]}}}\n'
        
        latex += f'\\label{{tab:{table["id"]}}}\n'
        
        if table["format"] == "csv" and table["data"]:
            # Convert CSV to LaTeX table
            lines = table["data"].split('\n')
            if lines:
                # Determine column count
                col_count = len(lines[0].split(','))
                latex += f'\\begin{{tabular}}{{|{"l|" * col_count}}}\n'
                latex += '\\hline\n'
                
                # Header row
                header_cells = lines[0].split(',')
                latex += ' & '.join(cell.strip() for cell in header_cells) + ' \\\\\n'
                latex += '\\hline\n'
                
                # Data rows
                for line in lines[1:]:
                    if line.strip():
                        cells = line.split(',')
                        latex += ' & '.join(cell.strip() for cell in cells) + ' \\\\\n'
                        latex += '\\hline\n'
                
                latex += '\\end{tabular}\n'
        else:
            latex += '\\begin{verbatim}\n'
            latex += table["data"]
            latex += '\\end{verbatim}\n'
        
        latex += '\\end{table}\n'
        
        return latex
    
    def _render_latex_bibliography(self, bibliography: List[Dict[str, Any]]) -> str:
        """Render LaTeX bibliography.
        
        Args:
            bibliography: Bibliography data
            
        Returns:
            Rendered LaTeX bibliography
        """
        if not bibliography:
            return ""
        
        latex = '\\begin{thebibliography}{99}\n'
        
        for citation in bibliography:
            latex += f'\\bibitem{{{citation["id"]}}}\n'
            latex += citation["formatted"] + '\n\n'
        
        latex += '\\end{thebibliography}\n'
        
        return latex
    
    def _get_latex_packages(self, config: ExportConfiguration) -> str:
        """Get LaTeX packages for export.
        
        Args:
            config: Export configuration
            
        Returns:
            LaTeX packages string
        """
        packages = [
            "\\usepackage[utf8]{inputenc}",
            "\\usepackage{amsmath}",
            "\\usepackage{amsfonts}",
            "\\usepackage{amssymb}",
            "\\usepackage{graphicx}",
            "\\usepackage{float}",
            "\\usepackage{hyperref}",
            "\\usepackage{geometry}",
            "\\usepackage{fancyhdr}",
            "\\usepackage{booktabs}",
            "\\usepackage{caption}",
            "\\usepackage{subcaption}"
        ]
        
        return '\n'.join(packages)
    
    def _copy_latex_assets(self, latex_dir: Path, content: Dict[str, Any], 
                          config: ExportConfiguration) -> List[Path]:
        """Copy LaTeX assets to output directory.
        
        Args:
            latex_dir: LaTeX output directory
            content: Content data
            config: Export configuration
            
        Returns:
            List of copied asset paths
        """
        assets = []
        
        # Copy figure files
        for figure in content["figures"]:
            if figure["data"]:
                figure_file = latex_dir / f"figure_{figure['id']}.png"
                if isinstance(figure["data"], bytes):
                    with open(figure_file, 'wb') as f:
                        f.write(figure["data"])
                    assets.append(figure_file)
        
        # Copy style files
        try:
            style_path = self.main_exporter.get_template_path(config.format, config.theme, "style.sty")
            dest_style = latex_dir / "paper_style.sty"
            shutil.copy2(style_path, dest_style)
            assets.append(dest_style)
        except Exception:
            pass
        
        return assets


class WordExporter(BaseFormatExporter):
    """Word document exporter with preserved formatting."""
    
    def export(self, config: ExportConfiguration) -> ExportedDocument:
        """Export to Word format.
        
        Args:
            config: Export configuration
            
        Returns:
            ExportedDocument with Word results
        """
        self.logger.info("Starting Word export")
        
        # Note: This is a simplified implementation
        # For full Word export, consider using python-docx library
        
        # Prepare content
        content = self.main_exporter.prepare_content_for_export(config)
        
        # Create Word-specific output directory
        word_dir = self.main_exporter.output_dir / "word"
        ensure_directory(word_dir)
        
        # For now, create a rich text format file
        output_filename = config.output_filename or "paper.rtf"
        word_file = word_dir / output_filename
        
        # Generate RTF content
        rtf_content = self._generate_rtf_content(content)
        
        with open(word_file, 'w', encoding='utf-8') as f:
            f.write(rtf_content)
        
        # Create result
        result = ExportedDocument(
            format=OutputFormat.WORD,
            file_path=word_file,
            file_size=word_file.stat().st_size,
            creation_time=datetime.now(),
            metadata=content["metadata"],
            assets=[]
        )
        
        self.logger.info(f"Word export completed: {word_file}")
        return result
    
    def _generate_rtf_content(self, content: Dict[str, Any]) -> str:
        """Generate RTF content for Word compatibility.
        
        Args:
            content: Prepared content
            
        Returns:
            RTF content string
        """
        rtf = "{\\rtf1\\ansi\\deff0 {\\fonttbl {\\f0 Times New Roman;}}\\f0\\fs24 "
        
        # Title
        title = content["metadata"].get("title", "Academic Paper")
        rtf += f"\\b\\fs28 {title}\\b0\\fs24\\par\\par "
        
        # Authors
        authors = content["metadata"].get("authors", "")
        if authors:
            rtf += f"\\i {authors}\\i0\\par\\par "
        
        # Abstract
        if "abstract" in content["sections"]:
            rtf += "\\b Abstract\\b0\\par "
            rtf += content["sections"]["abstract"] + "\\par\\par "
        
        # Sections
        for section_name, section_content in content["sections"].items():
            if section_name != "abstract" and section_content and section_content.strip():
                rtf += f"\\b {section_name.replace('_', ' ').title()}\\b0\\par "
                rtf += section_content + "\\par\\par "
        
        # Bibliography
        if content["bibliography"]:
            rtf += "\\b References\\b0\\par "
            for citation in content["bibliography"]:
                rtf += citation["formatted"] + "\\par "
        
        rtf += "}"
        
        return rtf


class EPUBExporter(BaseFormatExporter):
    """EPUB format exporter for e-book compatibility."""
    
    def export(self, config: ExportConfiguration) -> ExportedDocument:
        """Export to EPUB format.
        
        Args:
            config: Export configuration
            
        Returns:
            ExportedDocument with EPUB results
        """
        self.logger.info("Starting EPUB export")
        
        # Prepare content
        content = self.main_exporter.prepare_content_for_export(config)
        
        # Create EPUB-specific output directory
        epub_dir = self.main_exporter.output_dir / "epub"
        ensure_directory(epub_dir)
        
        # Create EPUB structure
        self._create_epub_structure(epub_dir, content, config)
        
        # Create EPUB file
        output_filename = config.output_filename or "paper.epub"
        epub_file = epub_dir / output_filename
        
        self._create_epub_file(epub_dir, epub_file, content)
        
        # Create result
        result = ExportedDocument(
            format=OutputFormat.EPUB,
            file_path=epub_file,
            file_size=epub_file.stat().st_size,
            creation_time=datetime.now(),
            metadata=content["metadata"],
            assets=[]
        )
        
        self.logger.info(f"EPUB export completed: {epub_file}")
        return result
    
    def _create_epub_structure(self, epub_dir: Path, content: Dict[str, Any], 
                              config: ExportConfiguration) -> None:
        """Create EPUB directory structure.
        
        Args:
            epub_dir: EPUB output directory
            content: Content data
            config: Export configuration
        """
        # Create EPUB directories
        meta_inf = epub_dir / "META-INF"
        oebps = epub_dir / "OEBPS"
        ensure_directory(meta_inf)
        ensure_directory(oebps)
        
        # Create container.xml
        container_xml = """<?xml version="1.0"?>
<container version="1.0" xmlns="urn:oasis:names:tc:opendocument:xmlns:container">
    <rootfiles>
        <rootfile full-path="OEBPS/content.opf" media-type="application/oebps-package+xml"/>
    </rootfiles>
</container>"""
        
        with open(meta_inf / "container.xml", 'w', encoding='utf-8') as f:
            f.write(container_xml)
        
        # Create content.opf
        content_opf = self._generate_epub_content_opf(content)
        with open(oebps / "content.opf", 'w', encoding='utf-8') as f:
            f.write(content_opf)
        
        # Create toc.ncx
        toc_ncx = self._generate_epub_toc_ncx(content)
        with open(oebps / "toc.ncx", 'w', encoding='utf-8') as f:
            f.write(toc_ncx)
        
        # Create HTML chapters
        self._create_epub_chapters(oebps, content)
    
    def _generate_epub_content_opf(self, content: Dict[str, Any]) -> str:
        """Generate EPUB content.opf file.
        
        Args:
            content: Content data
            
        Returns:
            content.opf XML string
        """
        title = content["metadata"].get("title", "Academic Paper")
        authors = content["metadata"].get("authors", "Unknown")
        
        opf = f"""<?xml version="1.0" encoding="UTF-8"?>
<package xmlns="http://www.idpf.org/2007/opf" unique-identifier="bookid" version="2.0">
    <metadata xmlns:dc="http://purl.org/dc/elements/1.1/">
        <dc:title>{title}</dc:title>
        <dc:creator>{authors}</dc:creator>
        <dc:language>en</dc:language>
        <dc:identifier id="bookid">paper2data-{datetime.now().strftime('%Y%m%d%H%M%S')}</dc:identifier>
        <dc:date>{datetime.now().strftime('%Y-%m-%d')}</dc:date>
        <dc:subject>Academic Paper</dc:subject>
    </metadata>
    
    <manifest>
        <item id="ncx" href="toc.ncx" media-type="application/x-dtbncx+xml"/>
        <item id="cover" href="cover.html" media-type="application/xhtml+xml"/>
        <item id="content" href="content.html" media-type="application/xhtml+xml"/>
        <item id="css" href="styles.css" media-type="text/css"/>
    </manifest>
    
    <spine toc="ncx">
        <itemref idref="cover"/>
        <itemref idref="content"/>
    </spine>
</package>"""
        
        return opf
    
    def _generate_epub_toc_ncx(self, content: Dict[str, Any]) -> str:
        """Generate EPUB toc.ncx file.
        
        Args:
            content: Content data
            
        Returns:
            toc.ncx XML string
        """
        title = content["metadata"].get("title", "Academic Paper")
        
        ncx = f"""<?xml version="1.0" encoding="UTF-8"?>
<ncx xmlns="http://www.daisy.org/z3986/2005/ncx/" version="2005-1">
    <head>
        <meta name="dtb:uid" content="paper2data-{datetime.now().strftime('%Y%m%d%H%M%S')}"/>
        <meta name="dtb:depth" content="2"/>
        <meta name="dtb:totalPageCount" content="0"/>
        <meta name="dtb:maxPageNumber" content="0"/>
    </head>
    
    <docTitle>
        <text>{title}</text>
    </docTitle>
    
    <navMap>
        <navPoint id="cover" playOrder="1">
            <navLabel><text>Cover</text></navLabel>
            <content src="cover.html"/>
        </navPoint>
        <navPoint id="content" playOrder="2">
            <navLabel><text>Content</text></navLabel>
            <content src="content.html"/>
        </navPoint>
    </navMap>
</ncx>"""
        
        return ncx
    
    def _create_epub_chapters(self, oebps_dir: Path, content: Dict[str, Any]) -> None:
        """Create EPUB chapter HTML files.
        
        Args:
            oebps_dir: OEBPS directory
            content: Content data
        """
        # Create cover page
        title = content["metadata"].get("title", "Academic Paper")
        authors = content["metadata"].get("authors", "Unknown")
        
        cover_html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <div class="cover">
        <h1>{title}</h1>
        <p class="authors">{authors}</p>
        <p class="date">{datetime.now().strftime('%Y-%m-%d')}</p>
    </div>
</body>
</html>"""
        
        with open(oebps_dir / "cover.html", 'w', encoding='utf-8') as f:
            f.write(cover_html)
        
        # Create content page
        content_html = f"""<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.1//EN" "http://www.w3.org/TR/xhtml11/DTD/xhtml11.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
<head>
    <title>{title}</title>
    <link rel="stylesheet" type="text/css" href="styles.css"/>
</head>
<body>
    <div class="content">
        {self._render_epub_content(content)}
    </div>
</body>
</html>"""
        
        with open(oebps_dir / "content.html", 'w', encoding='utf-8') as f:
            f.write(content_html)
        
        # Create CSS
        css_content = """
        body { font-family: Georgia, serif; line-height: 1.6; margin: 20px; }
        .cover { text-align: center; padding: 50px; }
        .cover h1 { font-size: 2em; margin-bottom: 20px; }
        .authors { font-style: italic; font-size: 1.2em; }
        .date { color: #666; }
        h1, h2, h3 { color: #333; }
        .section { margin: 20px 0; }
        """
        
        with open(oebps_dir / "styles.css", 'w', encoding='utf-8') as f:
            f.write(css_content)
    
    def _render_epub_content(self, content: Dict[str, Any]) -> str:
        """Render EPUB content.
        
        Args:
            content: Content data
            
        Returns:
            Rendered HTML content for EPUB
        """
        html_parts = []
        
        # Render sections
        for section_name, section_content in content["sections"].items():
            if section_content and section_content.strip():
                html_parts.append(f'<div class="section">')
                html_parts.append(f'<h2>{section_name.replace("_", " ").title()}</h2>')
                html_parts.append(f'<p>{section_content}</p>')
                html_parts.append('</div>')
        
        # Render bibliography
        if content["bibliography"]:
            html_parts.append('<div class="section">')
            html_parts.append('<h2>References</h2>')
            html_parts.append('<ol>')
            for citation in content["bibliography"]:
                html_parts.append(f'<li>{citation["formatted"]}</li>')
            html_parts.append('</ol>')
            html_parts.append('</div>')
        
        return '\n'.join(html_parts)
    
    def _create_epub_file(self, epub_dir: Path, epub_file: Path, content: Dict[str, Any]) -> None:
        """Create final EPUB file.
        
        Args:
            epub_dir: EPUB directory with structure
            epub_file: Output EPUB file path
            content: Content data
        """
        with zipfile.ZipFile(epub_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # Add mimetype first (uncompressed)
            zipf.writestr("mimetype", "application/epub+zip", compress_type=zipfile.ZIP_STORED)
            
            # Add all other files
            for root, dirs, files in os.walk(epub_dir):
                for file in files:
                    file_path = Path(root) / file
                    if file_path != epub_file:  # Don't include the epub file itself
                        arcname = file_path.relative_to(epub_dir)
                        zipf.write(file_path, arcname) 


class MarkdownExporter(BaseFormatExporter):
    """Markdown format exporter for readable text output."""
    
    def export(self, config: ExportConfiguration) -> ExportedDocument:
        """Export to Markdown format.
        
        Args:
            config: Export configuration
            
        Returns:
            ExportedDocument with Markdown results
        """
        self.logger.info("Starting Markdown export")
        
        # Prepare content
        content = self.main_exporter.prepare_content_for_export(config)
        
        # Create Markdown-specific output directory
        markdown_dir = self.main_exporter.output_dir / "markdown"
        ensure_directory(markdown_dir)
        
        # Generate Markdown content
        markdown_content = self._generate_markdown_content(content)
        
        # Save Markdown file
        output_filename = config.output_filename or "paper.md"
        markdown_file = markdown_dir / output_filename
        
        with open(markdown_file, 'w', encoding='utf-8') as f:
            f.write(markdown_content)
        
        # Create result
        result = ExportedDocument(
            format=OutputFormat.MARKDOWN,
            file_path=markdown_file,
            file_size=markdown_file.stat().st_size,
            creation_time=datetime.now(),
            metadata=content["metadata"],
            assets=[]
        )
        
        self.logger.info(f"Markdown export completed: {markdown_file}")
        return result
    
    def _generate_markdown_content(self, content: Dict[str, Any]) -> str:
        """Generate Markdown content from prepared data.
        
        Args:
            content: Prepared content data
            
        Returns:
            Markdown content string
        """
        markdown_parts = []
        
        # Title and metadata
        title = content["metadata"].get("title", "Academic Paper")
        authors = content["metadata"].get("authors", "")
        
        markdown_parts.append(f"# {title}")
        markdown_parts.append("")
        
        if authors:
            markdown_parts.append(f"**Authors:** {authors}")
            markdown_parts.append("")
        
        # Generation info
        markdown_parts.append(f"*Generated by Paper2Data v1.1 on {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}*")
        markdown_parts.append("")
        markdown_parts.append("---")
        markdown_parts.append("")
        
        # Table of contents
        if content["toc"]:
            markdown_parts.append("## Table of Contents")
            markdown_parts.append("")
            for entry in content["toc"]:
                markdown_parts.append(f"- [{entry['title']}](#{entry['anchor']})")
            markdown_parts.append("")
            markdown_parts.append("---")
            markdown_parts.append("")
        
        # Sections
        for section_name, section_content in content["sections"].items():
            if section_content and section_content.strip():
                # Format section title
                section_title = section_name.replace("_", " ").title()
                markdown_parts.append(f"## {section_title}")
                markdown_parts.append("")
                
                # Add section content
                formatted_content = self._format_markdown_content(section_content)
                markdown_parts.append(formatted_content)
                markdown_parts.append("")
        
        # Figures
        if content["figures"]:
            markdown_parts.append("## Figures")
            markdown_parts.append("")
            
            for figure in content["figures"]:
                markdown_parts.append(f"### Figure {figure['id']}")
                markdown_parts.append("")
                
                # Add image (if data URL is available)
                if figure.get("data"):
                    if isinstance(figure["data"], str) and figure["data"].startswith("data:"):
                        markdown_parts.append(f"![{figure.get('alt_text', 'Figure')}]({figure['data']})")
                    else:
                        markdown_parts.append(f"*[Figure {figure['id']}: Image not embedded - binary data]*")
                else:
                    markdown_parts.append(f"*[Figure {figure['id']}: Image not available]*")
                
                markdown_parts.append("")
                
                # Add caption
                if figure.get("caption"):
                    markdown_parts.append(f"**Caption:** {figure['caption']}")
                    markdown_parts.append("")
        
        # Tables
        if content["tables"]:
            markdown_parts.append("## Tables")
            markdown_parts.append("")
            
            for table in content["tables"]:
                markdown_parts.append(f"### Table {table['id']}")
                markdown_parts.append("")
                
                # Add caption
                if table.get("caption"):
                    markdown_parts.append(f"**Caption:** {table['caption']}")
                    markdown_parts.append("")
                
                # Add table content
                if table["format"] == "csv" and table["data"]:
                    markdown_table = self._convert_csv_to_markdown_table(table["data"])
                    markdown_parts.append(markdown_table)
                else:
                    markdown_parts.append("```")
                    markdown_parts.append(table["data"])
                    markdown_parts.append("```")
                
                markdown_parts.append("")
        
        # Equations
        if content["equations"]:
            markdown_parts.append("## Equations")
            markdown_parts.append("")
            
            for equation in content["equations"]:
                markdown_parts.append(f"### Equation {equation['id']}")
                markdown_parts.append("")
                
                # LaTeX math
                if equation.get("latex"):
                    markdown_parts.append(f"$$")
                    markdown_parts.append(equation["latex"])
                    markdown_parts.append("$$")
                
                markdown_parts.append("")
                
                # Context
                if equation.get("context"):
                    markdown_parts.append(f"*Context: {equation['context']}*")
                    markdown_parts.append("")
        
        # Bibliography
        if content["bibliography"]:
            markdown_parts.append("## References")
            markdown_parts.append("")
            
            for i, citation in enumerate(content["bibliography"], 1):
                markdown_parts.append(f"{i}. {citation['formatted']}")
                markdown_parts.append("")
        
        # Footer
        markdown_parts.append("---")
        markdown_parts.append("")
        markdown_parts.append("*This document was generated using Paper2Data v1.1*")
        markdown_parts.append("")
        markdown_parts.append("*Original paper content has been extracted and formatted for markdown viewing*")
        
        return "\n".join(markdown_parts)
    
    def _format_markdown_content(self, content: str) -> str:
        """Format content for Markdown output.
        
        Args:
            content: Raw content string
            
        Returns:
            Formatted Markdown content
        """
        # Basic formatting - convert line breaks to proper paragraphs
        paragraphs = content.split('\n\n')
        formatted_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if paragraph:
                # Handle lists
                if paragraph.startswith('- ') or paragraph.startswith('* '):
                    formatted_paragraphs.append(paragraph)
                elif paragraph.startswith('1. ') or paragraph.startswith('2. '):
                    formatted_paragraphs.append(paragraph)
                else:
                    # Regular paragraph
                    formatted_paragraphs.append(paragraph)
        
        return "\n\n".join(formatted_paragraphs)
    
    def _convert_csv_to_markdown_table(self, csv_data: str) -> str:
        """Convert CSV data to Markdown table format.
        
        Args:
            csv_data: CSV content string
            
        Returns:
            Markdown table string
        """
        lines = csv_data.strip().split('\n')
        if not lines:
            return ""
        
        # Parse CSV (simple implementation)
        rows = []
        for line in lines:
            cells = [cell.strip() for cell in line.split(',')]
            rows.append(cells)
        
        if not rows:
            return ""
        
        # Generate Markdown table
        markdown_table = []
        
        # Header row
        header = rows[0]
        markdown_table.append("| " + " | ".join(header) + " |")
        
        # Separator row
        separator = "| " + " | ".join(["---"] * len(header)) + " |"
        markdown_table.append(separator)
        
        # Data rows
        for row in rows[1:]:
            # Ensure row has same number of columns as header
            while len(row) < len(header):
                row.append("")
            
            markdown_table.append("| " + " | ".join(row[:len(header)]) + " |")
        
        return "\n".join(markdown_table) 
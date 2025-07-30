#!/usr/bin/env python3
"""
Paper2Data CLI Help System

Comprehensive help system with detailed command descriptions, usage examples,
and troubleshooting information.
"""

import sys
import os
import platform
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


@dataclass
class HelpSection:
    """Represents a help section with title, content, and formatting."""
    title: str
    content: str
    examples: List[str] = None
    subsections: Dict[str, str] = None
    
    def __post_init__(self):
        if self.examples is None:
            self.examples = []
        if self.subsections is None:
            self.subsections = {}


class HelpFormatter:
    """Handles formatting of help text with colors and structure."""
    
    def __init__(self, use_colors: bool = None):
        """Initialize formatter with color support detection."""
        if use_colors is None:
            # Auto-detect color support
            self.use_colors = (
                sys.stdout.isatty() and 
                platform.system() != "Windows" or 
                "COLORTERM" in os.environ
            )
        else:
            self.use_colors = use_colors
    
    def format_title(self, text: str) -> str:
        """Format a title with color and emphasis."""
        if self.use_colors:
            return f"\033[1;36m{text}\033[0m"  # Bold cyan
        return f"=== {text} ==="
    
    def format_subtitle(self, text: str) -> str:
        """Format a subtitle with color."""
        if self.use_colors:
            return f"\033[1;33m{text}\033[0m"  # Bold yellow
        return f"--- {text} ---"
    
    def format_command(self, text: str) -> str:
        """Format a command with color."""
        if self.use_colors:
            return f"\033[1;32m{text}\033[0m"  # Bold green
        return f"`{text}`"
    
    def format_arg(self, text: str) -> str:
        """Format an argument with color."""
        if self.use_colors:
            return f"\033[1;35m{text}\033[0m"  # Bold magenta
        return f"<{text}>"
    
    def format_success(self, text: str) -> str:
        """Format success message."""
        if self.use_colors:
            return f"\033[1;32m✅ {text}\033[0m"
        return f"✅ {text}"
    
    def format_warning(self, text: str) -> str:
        """Format warning message."""
        if self.use_colors:
            return f"\033[1;33m⚠️  {text}\033[0m"
        return f"⚠️  {text}"
    
    def format_error(self, text: str) -> str:
        """Format error message."""
        if self.use_colors:
            return f"\033[1;31m❌ {text}\033[0m"
        return f"❌ {text}"
    
    def format_info(self, text: str) -> str:
        """Format info message."""
        if self.use_colors:
            return f"\033[1;34mℹ️  {text}\033[0m"
        return f"ℹ️  {text}"


class Paper2DataHelpSystem:
    """Comprehensive help system for Paper2Data CLI."""
    
    def __init__(self):
        self.formatter = HelpFormatter()
        self._init_help_sections()
    
    def _init_help_sections(self):
        """Initialize all help sections."""
        self.sections = {
            "overview": self._create_overview_section(),
            "commands": self._create_commands_section(),
            "examples": self._create_examples_section(),
            "configuration": self._create_configuration_section(),
            "troubleshooting": self._create_troubleshooting_section(),
            "advanced": self._create_advanced_section(),
        }
    
    def _create_overview_section(self) -> HelpSection:
        """Create the overview help section."""
        content = """
Paper2Data is a powerful tool for extracting structured data from academic papers.
It can process PDF files, download papers from arXiv, and resolve DOIs to extract:

• Text content organized by sections
• Figures and images with captions
• Tables converted to CSV format
• Citations and references
• Metadata and bibliographic information

The tool supports multiple input formats and provides flexible output options
for integration with research workflows.
"""
        
        return HelpSection(
            title="Overview",
            content=content.strip(),
            examples=[
                "# Quick start - process a local PDF",
                "paper2data convert my_paper.pdf",
                "",
                "# Download and process from arXiv",
                "paper2data convert https://arxiv.org/abs/2301.00001",
                "",
                "# Process using DOI",
                "paper2data convert 10.1038/nature12373"
            ]
        )
    
    def _create_commands_section(self) -> HelpSection:
        """Create the commands help section."""
        content = """
Paper2Data provides four main commands for different operations:
"""
        
        subsections = {
            "convert": """
Extract content from papers and save to structured output directory.
This is the main command for processing papers.

Usage: paper2data convert INPUT [OPTIONS]

INPUT can be:
• Local PDF file path
• arXiv URL (https://arxiv.org/abs/PAPER_ID)
• DOI (Digital Object Identifier)

The convert command creates a structured output directory with:
• extracted_text.md - Full text content
• figures/ - Extracted images as PNG files
• tables/ - Tables converted to CSV format
• metadata.json - Paper metadata and statistics
• citations.json - Extracted references
""",
            
            "validate": """
Validate input sources without processing them.
Useful for checking if a paper is accessible and processable.

Usage: paper2data validate INPUT [OPTIONS]

Returns validation status and basic metadata about the paper.
""",
            
            "info": """
Get detailed information about a paper without full processing.
Shows metadata, estimated processing time, and available operations.

Usage: paper2data info INPUT [OPTIONS]

Provides quick insights into paper structure and content.
""",
            
            "config": """
Manage Paper2Data configuration files and settings.
Supports creating, validating, and fixing configuration files.

Usage: paper2data config [OPTIONS]

Configuration actions:
• create  - Create new configuration file
• validate - Check existing configuration
• fix     - Attempt to fix configuration issues
• status  - Show current configuration status
• help    - Show configuration help
"""
        }
        
        return HelpSection(
            title="Commands",
            content=content.strip(),
            subsections=subsections
        )
    
    def _create_examples_section(self) -> HelpSection:
        """Create the examples help section."""
        content = """
Comprehensive examples for different use cases and scenarios:
"""
        
        examples = [
            "# Basic PDF processing",
            "paper2data convert research_paper.pdf",
            "",
            "# Specify output directory",
            "paper2data convert paper.pdf --output ./my_output",
            "",
            "# Process with custom configuration",
            "paper2data convert paper.pdf --config ./my_config.yml",
            "",
            "# Skip certain extraction types",
            "paper2data convert paper.pdf --no-figures --no-tables",
            "",
            "# Download from arXiv (various formats)",
            "paper2data convert https://arxiv.org/abs/2301.00001",
            "paper2data convert https://arxiv.org/pdf/2301.00001.pdf",
            "paper2data convert 2301.00001",
            "",
            "# Process using DOI",
            "paper2data convert 10.1038/nature12373",
            "paper2data convert doi:10.1038/nature12373",
            "",
            "# Batch processing (using shell)",
            "for pdf in *.pdf; do paper2data convert \"$pdf\"; done",
            "",
            "# Get paper info before processing",
            "paper2data info https://arxiv.org/abs/2301.00001",
            "",
            "# Validate multiple sources",
            "paper2data validate paper1.pdf",
            "paper2data validate https://arxiv.org/abs/2301.00001",
            "",
            "# Configuration management",
            "paper2data config --config-action create --profile research",
            "paper2data config --config-action validate",
            "paper2data config --config-action status",
            "",
            "# Different output formats",
            "paper2data convert paper.pdf --format yaml",
            "paper2data convert paper.pdf --format markdown",
            "",
            "# Debug mode with detailed logging",
            "paper2data convert paper.pdf --log-level DEBUG --log-file debug.log",
            "",
            "# JSON output for scripting",
            "paper2data convert paper.pdf --json-output > result.json",
            "",
            "# Dry run (validation only)",
            "paper2data convert paper.pdf --dry-run"
        ]
        
        return HelpSection(
            title="Examples",
            content=content.strip(),
            examples=examples
        )
    
    def _create_configuration_section(self) -> HelpSection:
        """Create the configuration help section."""
        content = """
Paper2Data supports flexible configuration through YAML files.
Configuration files allow you to customize processing behavior,
output formats, and system resource usage.
"""
        
        subsections = {
            "profiles": """
Pre-configured profiles for different use cases:

• fast     - Quick processing with minimal resource usage
• balanced - Good balance of speed and quality (default)
• thorough - Comprehensive extraction with maximum quality
• research - Optimized for academic research workflows

Create a profile:
  paper2data config --config-action create --profile research
""",
            
            "locations": """
Configuration file locations (in order of priority):

1. Specified with --config option
2. ./paper2data.yml (current directory)
3. ./paper2data.yaml (current directory)
4. ~/.paper2data.yml (user home directory)
5. ~/.config/paper2data/config.yml (user config directory)

The first configuration file found will be used.
""",
            
            "interactive": """
Interactive configuration setup:

  paper2data config --config-action create --interactive

This will guide you through:
• System capability detection
• Use case selection
• Performance preferences
• Output format preferences
• Resource allocation settings
""",
            
            "validation": """
Configuration validation and fixing:

  paper2data config --config-action validate
  paper2data config --config-action fix
  paper2data config --config-action status

These commands help ensure your configuration is:
• Syntactically valid
• Compatible with your system
• Optimized for your use case
• Free of conflicting settings
"""
        }
        
        return HelpSection(
            title="Configuration",
            content=content.strip(),
            subsections=subsections
        )
    
    def _create_troubleshooting_section(self) -> HelpSection:
        """Create the troubleshooting help section."""
        content = """
Common issues and solutions for Paper2Data usage:
"""
        
        subsections = {
            "common_errors": """
Common Error Messages and Solutions:

❌ "Input is required for this command"
   Solution: Provide input file/URL after the command
   Example: paper2data convert paper.pdf

❌ "Failed to download from arXiv"
   Solutions:
   • Check internet connection
   • Verify arXiv URL format
   • Try alternative URL format: https://arxiv.org/pdf/PAPER_ID.pdf

❌ "Invalid DOI format"
   Solutions:
   • Ensure DOI is complete (e.g., 10.1038/nature12373)
   • Remove any prefixes except "doi:" if used
   • Check DOI validity on doi.org

❌ "Configuration file not found"
   Solutions:
   • Create configuration: paper2data config --config-action create
   • Specify config file: --config path/to/config.yml
   • Check configuration status: paper2data config --config-action status

❌ "PDF processing failed"
   Solutions:
   • Check if PDF is password-protected
   • Verify file is not corrupted
   • Try with --log-level DEBUG for detailed error info
   • Some PDFs may have restricted access or unusual formatting
""",
            
            "performance": """
Performance Issues and Solutions:

🐌 Slow processing:
   • Use --profile fast for quicker processing
   • Skip unnecessary extractions: --no-figures, --no-tables
   • Check system resources with: paper2data config --config-action status
   • Consider smaller batch sizes for multiple files

💾 High memory usage:
   • Use balanced or fast profile
   • Process files one at a time instead of batches
   • Close other applications while processing large files
   • Check available memory with system info

🔧 Configuration issues:
   • Validate configuration: paper2data config --config-action validate
   • Reset to defaults: paper2data config --config-action create --profile balanced
   • Check system compatibility: paper2data config --config-action status
""",
            
            "debugging": """
Debugging Tips:

🔍 Enable debug logging:
   paper2data convert paper.pdf --log-level DEBUG --log-file debug.log

📊 Get detailed info:
   paper2data info paper.pdf

🧪 Test without processing:
   paper2data validate paper.pdf
   paper2data convert paper.pdf --dry-run

📈 JSON output for analysis:
   paper2data convert paper.pdf --json-output > result.json

🔧 System diagnostics:
   paper2data config --config-action status
   paper2data config --config-action help
"""
        }
        
        return HelpSection(
            title="Troubleshooting",
            content=content.strip(),
            subsections=subsections
        )
    
    def _create_advanced_section(self) -> HelpSection:
        """Create the advanced usage help section."""
        content = """
Advanced usage patterns and integration examples:
"""
        
        subsections = {
            "scripting": """
Using Paper2Data in Scripts:

Shell script example:
#!/bin/bash
for paper in papers/*.pdf; do
    echo "Processing: $paper"
    paper2data convert "$paper" --json-output > "results/$(basename "$paper" .pdf).json"
done

Python integration:
import subprocess
import json

def process_paper(pdf_path):
    result = subprocess.run([
        'paper2data', 'convert', pdf_path, '--json-output'
    ], capture_output=True, text=True)
    return json.loads(result.stdout)

# Process paper and get results
results = process_paper('paper.pdf')
print(f"Extracted {results['summary']['sections_found']} sections")
""",
            
            "batch_processing": """
Batch Processing Strategies:

Sequential processing:
  for pdf in *.pdf; do 
    paper2data convert "$pdf" --output "output/$(basename "$pdf" .pdf)"
  done

Parallel processing (GNU parallel):
  parallel paper2data convert {} --output output/{/.} ::: *.pdf

With error handling:
  for pdf in *.pdf; do
    if paper2data validate "$pdf"; then
      paper2data convert "$pdf" --output "output/$(basename "$pdf" .pdf)"
    else
      echo "Skipping invalid PDF: $pdf"
    fi
  done
""",
            
            "integration": """
Integration with Other Tools:

With Jupyter notebooks:
  !paper2data convert paper.pdf --json-output > paper_data.json
  import json
  with open('paper_data.json') as f:
      data = json.load(f)

With research workflows:
  # Extract papers from bibliography
  cat bibliography.txt | while read doi; do
    paper2data convert "$doi" --output "papers/$(echo "$doi" | tr '/' '_')"
  done

With version control:
  # Add extracted data to git
  paper2data convert paper.pdf --output paper_data/
  git add paper_data/
  git commit -m "Add extracted data for $(basename paper.pdf)"
""",
            
            "customization": """
Customization Options:

Environment variables:
  export PAPER2DATA_CONFIG=~/.paper2data.yml
  export PAPER2DATA_OUTPUT_DIR=~/paper_extracts
  export PAPER2DATA_LOG_LEVEL=DEBUG

Custom output structure:
  # Configuration file can customize:
  # - Output directory structure
  # - File naming conventions
  # - Processing parameters
  # - Resource allocation

API-style usage:
  # For programmatic access, use JSON output
  paper2data convert paper.pdf --json-output --log-level ERROR

Plugin development:
  # Configuration supports plugin loading
  # See documentation for plugin architecture
  # Custom extractors can be registered
"""
        }
        
        return HelpSection(
            title="Advanced Usage",
            content=content.strip(),
            subsections=subsections
        )
    
    def show_section(self, section_name: str) -> str:
        """Show a specific help section."""
        if section_name not in self.sections:
            return f"Unknown help section: {section_name}"
        
        section = self.sections[section_name]
        output = []
        
        # Title
        output.append(self.formatter.format_title(section.title))
        output.append("")
        
        # Content
        output.append(section.content)
        output.append("")
        
        # Subsections
        if section.subsections:
            for subtitle, content in section.subsections.items():
                output.append(self.formatter.format_subtitle(subtitle.replace("_", " ").title()))
                output.append("")
                output.append(content.strip())
                output.append("")
        
        # Examples
        if section.examples:
            output.append(self.formatter.format_subtitle("Examples"))
            output.append("")
            for example in section.examples:
                if example.startswith("#"):
                    output.append(self.formatter.format_info(example))
                elif example.strip():
                    output.append(self.formatter.format_command(example))
                else:
                    output.append("")
        
        return "\n".join(output)
    
    def show_all_help(self) -> str:
        """Show comprehensive help for all sections."""
        output = []
        
        # Header
        output.append(self.formatter.format_title("Paper2Data - Comprehensive Help"))
        output.append("")
        output.append("Extract structured data from academic papers with ease.")
        output.append("")
        
        # Table of contents
        output.append(self.formatter.format_subtitle("Available Help Sections"))
        output.append("")
        for section_name, section in self.sections.items():
            output.append(f"• {section_name} - {section.title}")
        output.append("")
        output.append("Use 'paper2data help <section>' for detailed information.")
        output.append("")
        
        # Quick start
        output.append(self.formatter.format_subtitle("Quick Start"))
        output.append("")
        output.append(self.formatter.format_command("paper2data convert paper.pdf"))
        output.append(self.formatter.format_command("paper2data convert https://arxiv.org/abs/2301.00001"))
        output.append(self.formatter.format_command("paper2data config --config-action create --profile balanced"))
        output.append("")
        
        return "\n".join(output)
    
    def show_command_help(self, command: str) -> str:
        """Show help for a specific command."""
        if command == "convert":
            return self._show_convert_help()
        elif command == "validate":
            return self._show_validate_help()
        elif command == "info":
            return self._show_info_help()
        elif command == "config":
            return self._show_config_help()
        else:
            return f"Unknown command: {command}"
    
    def _show_convert_help(self) -> str:
        """Show detailed help for convert command."""
        output = []
        output.append(self.formatter.format_title("Convert Command Help"))
        output.append("")
        output.append("Extract content from papers and save to structured output directory.")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Usage"))
        output.append("")
        output.append(self.formatter.format_command("paper2data convert INPUT [OPTIONS]"))
        output.append("")
        
        output.append(self.formatter.format_subtitle("Input Types"))
        output.append("")
        output.append("• PDF file path: paper.pdf, /path/to/paper.pdf")
        output.append("• arXiv URL: https://arxiv.org/abs/2301.00001")
        output.append("• arXiv PDF: https://arxiv.org/pdf/2301.00001.pdf")
        output.append("• arXiv ID: 2301.00001")
        output.append("• DOI: 10.1038/nature12373")
        output.append("• DOI with prefix: doi:10.1038/nature12373")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Common Options"))
        output.append("")
        output.append("  -o, --output DIR     Output directory")
        output.append("  -f, --format FORMAT  Output format (json, yaml, markdown)")
        output.append("  --config FILE        Configuration file")
        output.append("  --log-level LEVEL    Logging level (DEBUG, INFO, WARNING, ERROR)")
        output.append("  --no-figures         Skip figure extraction")
        output.append("  --no-tables          Skip table extraction")
        output.append("  --no-citations       Skip citation extraction")
        output.append("  --dry-run            Validate without processing")
        output.append("  --json-output        Output JSON to stdout")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Examples"))
        output.append("")
        output.append(self.formatter.format_command("paper2data convert paper.pdf"))
        output.append(self.formatter.format_command("paper2data convert https://arxiv.org/abs/2301.00001 --output ./results"))
        output.append(self.formatter.format_command("paper2data convert 10.1038/nature12373 --no-figures --format yaml"))
        output.append("")
        
        return "\n".join(output)
    
    def _show_validate_help(self) -> str:
        """Show detailed help for validate command."""
        output = []
        output.append(self.formatter.format_title("Validate Command Help"))
        output.append("")
        output.append("Validate input sources without processing them.")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Usage"))
        output.append("")
        output.append(self.formatter.format_command("paper2data validate INPUT [OPTIONS]"))
        output.append("")
        
        output.append(self.formatter.format_subtitle("What it checks"))
        output.append("")
        output.append("• File existence and readability")
        output.append("• arXiv URL accessibility")
        output.append("• DOI validity and resolution")
        output.append("• Basic PDF structure")
        output.append("• Estimated processing requirements")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Examples"))
        output.append("")
        output.append(self.formatter.format_command("paper2data validate paper.pdf"))
        output.append(self.formatter.format_command("paper2data validate https://arxiv.org/abs/2301.00001"))
        output.append(self.formatter.format_command("paper2data validate 10.1038/nature12373"))
        output.append("")
        
        return "\n".join(output)
    
    def _show_info_help(self) -> str:
        """Show detailed help for info command."""
        output = []
        output.append(self.formatter.format_title("Info Command Help"))
        output.append("")
        output.append("Get detailed information about a paper without full processing.")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Usage"))
        output.append("")
        output.append(self.formatter.format_command("paper2data info INPUT [OPTIONS]"))
        output.append("")
        
        output.append(self.formatter.format_subtitle("Information provided"))
        output.append("")
        output.append("• Paper metadata (title, authors, etc.)")
        output.append("• File size and page count")
        output.append("• Estimated processing time")
        output.append("• Available extraction operations")
        output.append("• System compatibility")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Examples"))
        output.append("")
        output.append(self.formatter.format_command("paper2data info paper.pdf"))
        output.append(self.formatter.format_command("paper2data info https://arxiv.org/abs/2301.00001"))
        output.append("")
        
        return "\n".join(output)
    
    def _show_config_help(self) -> str:
        """Show detailed help for config command."""
        output = []
        output.append(self.formatter.format_title("Config Command Help"))
        output.append("")
        output.append("Manage Paper2Data configuration files and settings.")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Usage"))
        output.append("")
        output.append(self.formatter.format_command("paper2data config [OPTIONS]"))
        output.append("")
        
        output.append(self.formatter.format_subtitle("Configuration Actions"))
        output.append("")
        output.append("  --config-action create     Create new configuration file")
        output.append("  --config-action validate   Validate existing configuration")
        output.append("  --config-action fix        Fix configuration issues")
        output.append("  --config-action status     Show configuration status")
        output.append("  --config-action help       Show detailed configuration help")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Additional Options"))
        output.append("")
        output.append("  --profile PROFILE      Use configuration profile")
        output.append("  --interactive          Interactive setup")
        output.append("  --config FILE          Specify configuration file")
        output.append("")
        
        output.append(self.formatter.format_subtitle("Examples"))
        output.append("")
        output.append(self.formatter.format_command("paper2data config --config-action create --profile research"))
        output.append(self.formatter.format_command("paper2data config --config-action validate"))
        output.append(self.formatter.format_command("paper2data config --config-action create --interactive"))
        output.append("")
        
        return "\n".join(output)
    
    def get_system_info(self) -> str:
        """Get system information for help context."""
        output = []
        output.append(self.formatter.format_subtitle("System Information"))
        output.append("")
        
        try:
            import platform
            import os
            
            output.append(f"Platform: {platform.system()} {platform.release()}")
            output.append(f"Python: {platform.python_version()}")
            output.append(f"Architecture: {platform.machine()}")
            
            # Memory info (if available)
            try:
                import psutil
                memory = psutil.virtual_memory()
                output.append(f"Memory: {memory.total // (1024**3)} GB total, {memory.available // (1024**3)} GB available")
            except ImportError:
                output.append("Memory: psutil not available for memory info")
            
            # CPU info
            try:
                import multiprocessing
                output.append(f"CPU cores: {multiprocessing.cpu_count()}")
            except:
                output.append("CPU cores: Unable to detect")
            
            # Current directory
            output.append(f"Current directory: {os.getcwd()}")
            
        except Exception as e:
            output.append(f"System info error: {str(e)}")
        
        return "\n".join(output)

    def get_contextual_help(self, context: Optional[Dict[str, Any]] = None) -> str:
        """Get contextual help based on current system state and user context."""
        output = []
        
        output.append(self.formatter.format_title("Contextual Help"))
        output.append("")
        
        # System state detection
        try:
            from .config_manager import get_configuration_status
            config_status = get_configuration_status()
            
            if not config_status.has_config:
                output.append(self.formatter.format_warning("No configuration file found"))
                output.append("Recommendation: Create a configuration file to customize processing:")
                output.append(self.formatter.format_command("paper2data config --config-action create --profile balanced"))
                output.append("")
            elif not config_status.is_valid:
                output.append(self.formatter.format_error("Configuration file has issues"))
                output.append("Recommendation: Fix your configuration:")
                output.append(self.formatter.format_command("paper2data config --config-action fix"))
                output.append("")
            else:
                output.append(self.formatter.format_success(f"Configuration is valid (Profile: {config_status.profile or 'default'})"))
                output.append("")
        except Exception as e:
            output.append(self.formatter.format_info("Configuration status could not be determined"))
            output.append("")
        
        # System resource recommendations
        try:
            import psutil
            memory = psutil.virtual_memory()
            available_gb = memory.available // (1024**3)
            
            if available_gb < 2:
                output.append(self.formatter.format_warning("Low memory detected"))
                output.append("Recommendations for low memory systems:")
                output.append("• Use --profile fast for minimal resource usage")
                output.append("• Process files one at a time")
                output.append("• Skip unnecessary extractions with --no-figures or --no-tables")
                output.append("")
            elif available_gb > 8:
                output.append(self.formatter.format_success("High memory available"))
                output.append("Recommendations for high-memory systems:")
                output.append("• Use --profile thorough for maximum quality")
                output.append("• Process multiple files in batch")
                output.append("• Enable all extraction types")
                output.append("")
        except ImportError:
            output.append(self.formatter.format_info("Install psutil for system resource monitoring"))
            output.append("")
        
        # Current directory context
        import os
        current_dir = Path(os.getcwd())
        pdf_files = list(current_dir.glob("*.pdf"))
        
        if pdf_files:
            output.append(self.formatter.format_info(f"Found {len(pdf_files)} PDF files in current directory"))
            output.append("Quick actions:")
            if len(pdf_files) == 1:
                output.append(self.formatter.format_command(f"paper2data convert {pdf_files[0].name}"))
            else:
                output.append(self.formatter.format_command("# Process all PDFs"))
                output.append(self.formatter.format_command("for pdf in *.pdf; do paper2data convert \"$pdf\"; done"))
            output.append("")
        
        # Common next steps
        output.append(self.formatter.format_subtitle("Common Next Steps"))
        output.append("")
        output.append("1. First time using Paper2Data?")
        output.append("   " + self.formatter.format_command("paper2data help --help-section overview"))
        output.append("")
        output.append("2. Need to process a paper?")
        output.append("   " + self.formatter.format_command("paper2data convert <input>"))
        output.append("")
        output.append("3. Want to see examples?")
        output.append("   " + self.formatter.format_command("paper2data help --help-section examples"))
        output.append("")
        output.append("4. Having issues?")
        output.append("   " + self.formatter.format_command("paper2data help --help-section troubleshooting"))
        output.append("")
        output.append("5. Want to optimize performance?")
        output.append("   " + self.formatter.format_command("paper2data config --config-action status"))
        output.append("")
        
        return "\n".join(output)
    
    def get_error_specific_help(self, error_message: str) -> str:
        """Get help specific to an error message."""
        output = []
        
        output.append(self.formatter.format_title("Error-Specific Help"))
        output.append("")
        output.append(f"Error: {error_message}")
        output.append("")
        
        # Match common error patterns
        error_lower = error_message.lower()
        
        if "input is required" in error_lower:
            output.append(self.formatter.format_subtitle("Solution"))
            output.append("You need to provide an input source after the command.")
            output.append("")
            output.append("Examples:")
            output.append(self.formatter.format_command("paper2data convert paper.pdf"))
            output.append(self.formatter.format_command("paper2data convert https://arxiv.org/abs/2301.00001"))
            output.append(self.formatter.format_command("paper2data convert 10.1038/nature12373"))
            
        elif "failed to download" in error_lower and "arxiv" in error_lower:
            output.append(self.formatter.format_subtitle("Solution"))
            output.append("arXiv download failed. Try these solutions:")
            output.append("• Check your internet connection")
            output.append("• Verify the arXiv URL format")
            output.append("• Try the PDF URL instead:")
            output.append(self.formatter.format_command("paper2data convert https://arxiv.org/pdf/2301.00001.pdf"))
            
        elif "invalid doi" in error_lower:
            output.append(self.formatter.format_subtitle("Solution"))
            output.append("DOI format is invalid. Try these fixes:")
            output.append("• Ensure DOI is complete (e.g., 10.1038/nature12373)")
            output.append("• Remove any prefixes except 'doi:' if used")
            output.append("• Verify DOI exists on doi.org")
            
        elif "configuration" in error_lower:
            output.append(self.formatter.format_subtitle("Solution"))
            output.append("Configuration issue detected. Try these fixes:")
            output.append(self.formatter.format_command("paper2data config --config-action validate"))
            output.append(self.formatter.format_command("paper2data config --config-action fix"))
            output.append(self.formatter.format_command("paper2data config --config-action create --profile balanced"))
            
        elif "pdf processing failed" in error_lower:
            output.append(self.formatter.format_subtitle("Solution"))
            output.append("PDF processing failed. Try these solutions:")
            output.append("• Check if PDF is password-protected")
            output.append("• Verify file is not corrupted")
            output.append("• Try with debug logging:")
            output.append(self.formatter.format_command("paper2data convert paper.pdf --log-level DEBUG"))
            
        elif "memory" in error_lower or "out of memory" in error_lower:
            output.append(self.formatter.format_subtitle("Solution"))
            output.append("Memory issue detected. Try these solutions:")
            output.append("• Use fast profile: --profile fast")
            output.append("• Skip extractions: --no-figures --no-tables")
            output.append("• Process files one at a time")
            output.append("• Close other applications")
            
        else:
            output.append(self.formatter.format_subtitle("General Solutions"))
            output.append("For unexpected errors, try:")
            output.append("• Enable debug logging: --log-level DEBUG")
            output.append("• Check system status: paper2data config --config-action status")
            output.append("• Validate input: paper2data validate <input>")
            output.append("• See troubleshooting: paper2data help --help-section troubleshooting")
        
        output.append("")
        output.append(self.formatter.format_subtitle("Need More Help?"))
        output.append("• Run: paper2data help --help-section troubleshooting")
        output.append("• Run: paper2data help --system-info")
        output.append("• Check configuration: paper2data config --config-action status")
        
        return "\n".join(output)
    
    def get_usage_recommendations(self) -> str:
        """Get usage recommendations based on system capabilities."""
        output = []
        
        output.append(self.formatter.format_title("Usage Recommendations"))
        output.append("")
        
        try:
            # System analysis
            import multiprocessing
            import psutil
            
            cpu_count = multiprocessing.cpu_count()
            memory = psutil.virtual_memory()
            memory_gb = memory.total // (1024**3)
            
            output.append(self.formatter.format_subtitle("System Analysis"))
            output.append(f"CPU cores: {cpu_count}")
            output.append(f"Memory: {memory_gb} GB")
            output.append("")
            
            # Recommendations based on system
            if cpu_count >= 8 and memory_gb >= 16:
                output.append(self.formatter.format_success("High-performance system detected"))
                output.append("Recommendations:")
                output.append("• Use --profile thorough for maximum quality")
                output.append("• Process multiple files simultaneously")
                output.append("• Enable all extraction types")
                output.append("• Use batch processing for large datasets")
                profile = "thorough"
            elif cpu_count >= 4 and memory_gb >= 8:
                output.append(self.formatter.format_success("Good performance system"))
                output.append("Recommendations:")
                output.append("• Use --profile balanced (default)")
                output.append("• Process files individually or in small batches")
                output.append("• All extraction types should work well")
                profile = "balanced"
            else:
                output.append(self.formatter.format_warning("Limited resources detected"))
                output.append("Recommendations:")
                output.append("• Use --profile fast for better performance")
                output.append("• Process files one at a time")
                output.append("• Consider skipping resource-intensive extractions")
                output.append("• Close other applications while processing")
                profile = "fast"
            
            output.append("")
            output.append(self.formatter.format_subtitle("Recommended Configuration"))
            output.append(f"Create optimized configuration:")
            output.append(self.formatter.format_command(f"paper2data config --config-action create --profile {profile}"))
            
        except Exception as e:
            output.append(self.formatter.format_warning("Could not analyze system capabilities"))
            output.append("Default recommendation: Use balanced profile")
            output.append(self.formatter.format_command("paper2data config --config-action create --profile balanced"))
        
        return "\n".join(output)

    def get_configuration_detailed_help(self) -> str:
        """Get detailed configuration help with current system context."""
        output = []
        
        output.append(self.formatter.format_title("Configuration Detailed Help"))
        output.append("")
        
        # Current configuration status
        try:
            from .config_manager import get_configuration_status
            config_status = get_configuration_status()
            
            output.append(self.formatter.format_subtitle("Current Configuration Status"))
            output.append("")
            
            if config_status.has_config:
                output.append(self.formatter.format_success(f"Configuration file found: {config_status.config_path}"))
                output.append(f"Profile: {config_status.profile or 'default'}")
                if config_status.is_valid:
                    output.append(self.formatter.format_success("Configuration is valid"))
                else:
                    output.append(self.formatter.format_error("Configuration has issues"))
                    if config_status.errors:
                        output.append("Errors:")
                        for error in config_status.errors:
                            output.append(f"  • {error}")
                    if config_status.warnings:
                        output.append("Warnings:")
                        for warning in config_status.warnings:
                            output.append(f"  • {warning}")
            else:
                output.append(self.formatter.format_warning("No configuration file found"))
                output.append("Paper2Data will use default settings.")
            
            output.append("")
            
        except Exception as e:
            output.append(self.formatter.format_warning(f"Could not determine configuration status: {str(e)}"))
            output.append("")
        
        # Configuration file structure
        output.append(self.formatter.format_subtitle("Configuration File Structure"))
        output.append("")
        output.append("A complete configuration file includes these sections:")
        output.append("")
        output.append("```yaml")
        output.append("# Output configuration")
        output.append("output:")
        output.append("  directory: ./paper2data_output")
        output.append("  format: json")
        output.append("  create_structure: true")
        output.append("")
        output.append("# Processing configuration")
        output.append("processing:")
        output.append("  mode: balanced")
        output.append("  extract_figures: true")
        output.append("  extract_tables: true")
        output.append("  extract_citations: true")
        output.append("  parallel_processing: true")
        output.append("  max_workers: 4")
        output.append("")
        output.append("# Logging configuration")
        output.append("logging:")
        output.append("  level: INFO")
        output.append("  file: paper2data.log")
        output.append("  console: true")
        output.append("```")
        output.append("")
        
        # Profile explanations
        output.append(self.formatter.format_subtitle("Profile Explanations"))
        output.append("")
        output.append("• **fast**: Minimal resource usage, basic extraction")
        output.append("  - Best for: Quick processing, limited resources")
        output.append("  - Trade-offs: Lower quality, fewer features")
        output.append("")
        output.append("• **balanced**: Good balance of speed and quality")
        output.append("  - Best for: Most users, typical use cases")
        output.append("  - Trade-offs: Reasonable processing time")
        output.append("")
        output.append("• **thorough**: High quality extraction")
        output.append("  - Best for: Important documents, research")
        output.append("  - Trade-offs: Slower processing, more resources")
        output.append("")
        output.append("• **research**: Maximum quality for research")
        output.append("  - Best for: Academic research, detailed analysis")
        output.append("  - Trade-offs: Longest processing time")
        output.append("")
        
        # Configuration troubleshooting
        output.append(self.formatter.format_subtitle("Configuration Troubleshooting"))
        output.append("")
        output.append("Common configuration issues and solutions:")
        output.append("")
        output.append("**Configuration file not found:**")
        output.append("  " + self.formatter.format_command("paper2data config --config-action create"))
        output.append("")
        output.append("**Configuration has errors:**")
        output.append("  " + self.formatter.format_command("paper2data config --config-action validate"))
        output.append("  " + self.formatter.format_command("paper2data config --config-action fix"))
        output.append("")
        output.append("**Want to start fresh:**")
        output.append("  " + self.formatter.format_command("paper2data config --config-action create --profile balanced"))
        output.append("")
        output.append("**Interactive setup:**")
        output.append("  " + self.formatter.format_command("paper2data config --config-action create --interactive"))
        output.append("")
        
        return "\n".join(output)
    
    def get_performance_tuning_help(self) -> str:
        """Get help for performance tuning based on system capabilities."""
        output = []
        
        output.append(self.formatter.format_title("Performance Tuning Help"))
        output.append("")
        
        try:
            import psutil
            import multiprocessing
            
            # System analysis
            cpu_count = multiprocessing.cpu_count()
            memory = psutil.virtual_memory()
            memory_gb = memory.total // (1024**3)
            available_gb = memory.available // (1024**3)
            
            output.append(self.formatter.format_subtitle("System Analysis"))
            output.append("")
            output.append(f"CPU Cores: {cpu_count}")
            output.append(f"Total Memory: {memory_gb} GB")
            output.append(f"Available Memory: {available_gb} GB")
            output.append(f"Memory Usage: {memory.percent:.1f}%")
            output.append("")
            
            # Performance recommendations
            output.append(self.formatter.format_subtitle("Performance Recommendations"))
            output.append("")
            
            if available_gb < 2:
                output.append(self.formatter.format_warning("Low memory detected"))
                output.append("Memory optimization recommendations:")
                output.append("• Use --profile fast")
                output.append("• Process files individually")
                output.append("• Skip resource-intensive extractions:")
                output.append("  " + self.formatter.format_command("paper2data convert input.pdf --no-figures --no-tables"))
                output.append("• Close other applications")
                output.append("• Consider upgrading system memory")
            elif available_gb < 4:
                output.append(self.formatter.format_info("Moderate memory available"))
                output.append("Balanced performance recommendations:")
                output.append("• Use --profile balanced (default)")
                output.append("• Process files individually or in small batches")
                output.append("• Monitor memory usage during processing")
            else:
                output.append(self.formatter.format_success("Sufficient memory available"))
                output.append("High performance recommendations:")
                output.append("• Use --profile thorough for maximum quality")
                output.append("• Enable parallel processing")
                output.append("• Process multiple files simultaneously")
            
            output.append("")
            
            # CPU-specific recommendations
            output.append(self.formatter.format_subtitle("CPU Optimization"))
            output.append("")
            
            if cpu_count >= 8:
                output.append(self.formatter.format_success("Multi-core system detected"))
                output.append("CPU optimization recommendations:")
                output.append("• Enable parallel processing in configuration")
                output.append("• Use multiple worker processes")
                output.append("• Consider batch processing for multiple files")
            elif cpu_count >= 4:
                output.append(self.formatter.format_info("Good CPU available"))
                output.append("CPU optimization recommendations:")
                output.append("• Use parallel processing for large files")
                output.append("• Process files individually for best results")
            else:
                output.append(self.formatter.format_warning("Limited CPU cores"))
                output.append("CPU optimization recommendations:")
                output.append("• Use --profile fast for better performance")
                output.append("• Avoid parallel processing overhead")
                output.append("• Process files one at a time")
            
            output.append("")
            
            # Configuration recommendations
            output.append(self.formatter.format_subtitle("Recommended Configuration"))
            output.append("")
            
            if available_gb >= 8 and cpu_count >= 8:
                profile = "thorough"
                output.append("High-performance system configuration:")
            elif available_gb >= 4 and cpu_count >= 4:
                profile = "balanced"
                output.append("Balanced system configuration:")
            else:
                profile = "fast"
                output.append("Resource-constrained system configuration:")
            
            output.append(self.formatter.format_command(f"paper2data config --config-action create --profile {profile}"))
            
        except ImportError:
            output.append(self.formatter.format_warning("Install psutil for detailed system analysis"))
            output.append("")
            output.append("Basic performance tips:")
            output.append("• Use --profile fast for better performance")
            output.append("• Process files individually")
            output.append("• Skip unnecessary extractions if needed")
            output.append("• Monitor system resources during processing")
        
        return "\n".join(output)


# Global help system instance
help_system = Paper2DataHelpSystem() 
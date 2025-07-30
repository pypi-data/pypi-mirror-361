#!/usr/bin/env python3
"""
Paper2Data Parser - Command Line Interface

Main entry point for the Python parser that can be called from the Node.js CLI.
"""

import sys
import json
import argparse
from pathlib import Path
from typing import Dict, Any, Optional
import logging

from . import (
    create_ingestor, 
    extract_all_content,
    setup_logging, 
    get_logger,
    load_config,
    save_json,
    create_output_structure,
    format_output,
    ValidationError,
    ProcessingError,
    ConfigurationError
)
from .help_system import help_system


def setup_argument_parser() -> argparse.ArgumentParser:
    """Set up command line argument parser."""
    parser = argparse.ArgumentParser(
        description="Paper2Data Parser - Extract content from academic papers",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=help_system.show_section("overview")
    )
    
    parser.add_argument(
        "command",
        choices=["convert", "validate", "info", "config", "help"],
        help="Command to execute"
    )
    
    parser.add_argument(
        "input",
        nargs="?",
        help="Input source: PDF file path, arXiv URL, or DOI (not required for config/help commands)"
    )
    
    parser.add_argument(
        "-o", "--output",
        type=Path,
        help="Output directory (default: ./paper2data_output)"
    )
    
    parser.add_argument(
        "-f", "--format",
        choices=["json", "yaml", "markdown"],
        default="json",
        help="Output format for metadata (default: json)"
    )
    
    parser.add_argument(
        "--config",
        type=Path,
        help="Configuration file path"
    )
    
    parser.add_argument(
        "--log-level",
        choices=["DEBUG", "INFO", "WARNING", "ERROR"],
        default="INFO",
        help="Logging level (default: INFO)"
    )
    
    parser.add_argument(
        "--log-file",
        type=Path,
        help="Log file path"
    )
    
    parser.add_argument(
        "--no-figures",
        action="store_true",
        help="Skip figure extraction"
    )
    
    parser.add_argument(
        "--no-tables",
        action="store_true", 
        help="Skip table extraction"
    )
    
    parser.add_argument(
        "--no-citations",
        action="store_true",
        help="Skip citation extraction"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Validate input without processing"
    )
    
    parser.add_argument(
        "--json-output",
        action="store_true",
        help="Output results as JSON to stdout (for CLI integration)"
    )
    
    # Configuration-specific arguments
    parser.add_argument(
        "--config-action",
        choices=["create", "validate", "fix", "status", "help"],
        default="help",
        help="Configuration action to perform (default: help)"
    )
    
    parser.add_argument(
        "--profile",
        choices=["fast", "balanced", "thorough", "research"],
        help="Configuration profile to use"
    )
    
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Interactive configuration setup"
    )
    
    # Help-specific arguments
    parser.add_argument(
        "--help-section",
        choices=["overview", "commands", "examples", "configuration", "troubleshooting", "advanced"],
        help="Show specific help section"
    )
    
    parser.add_argument(
        "--help-command",
        choices=["convert", "validate", "info", "config"],
        help="Show detailed help for specific command"
    )
    
    parser.add_argument(
        "--system-info",
        action="store_true",
        help="Show system information"
    )
    
    parser.add_argument(
        "--contextual-help",
        action="store_true",
        help="Show contextual help based on current system state"
    )
    
    parser.add_argument(
        "--error-help",
        type=str,
        help="Get help for a specific error message"
    )
    
    parser.add_argument(
        "--usage-recommendations",
        action="store_true",
        help="Get usage recommendations based on system capabilities"
    )
    
    parser.add_argument(
        "--config-help",
        action="store_true",
        help="Show detailed configuration help with current system context"
    )
    
    parser.add_argument(
        "--performance-help",
        action="store_true",
        help="Show performance tuning help based on system capabilities"
    )
    
    return parser


def validate_input_command(input_source: str, args: argparse.Namespace) -> Dict[str, Any]:
    """Validate input source and return validation results."""
    logger = get_logger()
    
    try:
        ingestor = create_ingestor(input_source)
        is_valid = ingestor.validate()
        
        result = {
            "valid": is_valid,
            "input_source": input_source,
            "metadata": ingestor.metadata,
            "message": "Input validation successful"
        }
        
        logger.info(f"Validation successful for: {input_source}")
        return result
        
    except (ValidationError, ProcessingError) as e:
        result = {
            "valid": False,
            "input_source": input_source,
            "error": str(e),
            "message": "Input validation failed"
        }
        
        logger.error(f"Validation failed: {str(e)}")
        return result


def info_command(input_source: str, args: argparse.Namespace) -> Dict[str, Any]:
    """Get information about input source without full processing."""
    logger = get_logger()
    
    try:
        # Validate first
        validation_result = validate_input_command(input_source, args)
        if not validation_result["valid"]:
            return validation_result
        
        # For PDF files, get basic info
        ingestor = create_ingestor(input_source)
        ingestor.validate()  # This populates metadata
        
        result = {
            "input_source": input_source,
            "metadata": ingestor.metadata,
            "estimated_processing_time": "1-5 minutes (depends on document size)",
            "supported_operations": ["text extraction", "section detection", "figure extraction", "table detection", "citation extraction"]
        }
        
        logger.info(f"Info retrieved for: {input_source}")
        return result
        
    except Exception as e:
        logger.error(f"Failed to get info: {str(e)}")
        return {
            "error": str(e),
            "message": "Failed to retrieve information"
        }


def convert_command(input_source: str, args: argparse.Namespace, config: Dict[str, Any]) -> Dict[str, Any]:
    """Convert paper to structured data."""
    logger = get_logger()
    
    try:
        # Create ingestor and validate
        logger.info(f"Starting conversion of: {input_source}")
        ingestor = create_ingestor(input_source)
        ingestor.validate()
        
        if args.dry_run:
            return {
                "success": True,
                "input_source": input_source,
                "message": "Dry run completed - input is valid",
                "metadata": ingestor.metadata
            }
        
        # Ingest content
        logger.info("Ingesting content...")
        pdf_content = ingestor.ingest()
        
        # Extract all content
        logger.info("Extracting content...")
        extraction_results = extract_all_content(pdf_content)
        
        # Determine output directory
        if args.output:
            output_dir = args.output
        else:
            output_dir = Path(config.get("output", {}).get("directory", "./paper2data_output"))
        
        # Create output structure
        paper_title = extraction_results.get("content", {}).get("metadata", {}).get("title", "unknown")
        if not paper_title or paper_title == "unknown":
            # Try to get title from filename or URL
            if input_source.endswith('.pdf'):
                paper_title = Path(input_source).stem
            else:
                paper_title = "unknown_paper"
        
        output_structure = create_output_structure(output_dir, paper_title)
        
        # Save extracted content
        logger.info("Saving extracted content...")
        
        # Save metadata
        metadata_file = output_structure["metadata"] / "document_info.json"
        save_json(extraction_results.get("content", {}).get("metadata", {}), metadata_file)
        
        # Save sections
        sections = extraction_results.get("sections", {}).get("sections", {})
        for section_name, section_content in sections.items():
            if section_content:
                section_file = output_structure["sections"] / f"{section_name}.md"
                with open(section_file, 'w', encoding='utf-8') as f:
                    f.write(f"# {section_name.title()}\n\n{section_content}")
        
        # Save figures (if enabled)
        if not args.no_figures and config.get("processing", {}).get("extract_figures", True):
            figures = extraction_results.get("figures", {}).get("figures", [])
            for figure in figures:
                figure_file = output_structure["figures"] / f"{figure['figure_id']}.png"
                with open(figure_file, 'wb') as f:
                    f.write(figure["data"])
        
        # Save tables (if enabled)
        if not args.no_tables and config.get("processing", {}).get("extract_tables", True):
            tables = extraction_results.get("tables", {}).get("tables", [])
            for table in tables:
                # Use CSV format if available, otherwise fall back to raw text
                if 'csv_content' in table and table['csv_content']:
                    table_file = output_structure["tables"] / f"{table['table_id']}.csv"
                    with open(table_file, 'w', encoding='utf-8', newline='') as f:
                        f.write(table["csv_content"])
                else:
                    # Fallback to raw text format
                    table_file = output_structure["tables"] / f"{table['table_id']}.txt"
                    with open(table_file, 'w', encoding='utf-8') as f:
                        f.write(table["raw_text"])
        
        # Save citations (if enabled)
        if not args.no_citations and config.get("processing", {}).get("extract_citations", True):
            citations = extraction_results.get("citations", {}).get("reference_list", [])
            if citations:
                citations_file = output_structure["metadata"] / "citations.json"
                save_json({"references": citations}, citations_file)
        
        # Save comprehensive results (excluding binary data)
        results_file = output_structure["root"] / "extraction_results.json"
        json_safe_results = {
            "content": extraction_results.get("content", {}),
            "sections": extraction_results.get("sections", {}),
            "tables": extraction_results.get("tables", {}),
            "citations": extraction_results.get("citations", {}),
            "summary": extraction_results.get("summary", {}),
            "extraction_timestamp": extraction_results.get("extraction_timestamp", ""),
            # Note: Figure binary data is saved separately as PNG files
            "figures": {
                "summary": extraction_results.get("figures", {}).get("summary", {}),
                "figure_count": len(extraction_results.get("figures", {}).get("figures", []))
            }
        }
        save_json(json_safe_results, results_file)
        
        # Create README
        readme_file = output_structure["root"] / "README.md"
        with open(readme_file, 'w', encoding='utf-8') as f:
            f.write(f"""# {paper_title}

## Extraction Summary

- **Pages**: {extraction_results.get('summary', {}).get('total_pages', 'Unknown')}
- **Words**: {extraction_results.get('summary', {}).get('total_words', 'Unknown')}
- **Sections**: {extraction_results.get('summary', {}).get('sections_found', 0)}
- **Figures**: {extraction_results.get('summary', {}).get('figures_found', 0)}
- **Tables**: {extraction_results.get('summary', {}).get('tables_found', 0)}
- **References**: {extraction_results.get('summary', {}).get('references_found', 0)}

## Directory Structure

- `sections/` - Document sections in Markdown format
- `figures/` - Extracted figures as PNG files
- `tables/` - Extracted tables as CSV files (structured data) or text files (fallback)
- `metadata/` - Document metadata and citations
- `extraction_results.json` - Complete extraction results

## Source

Original source: {input_source}
Processed on: {extraction_results.get('extraction_timestamp', 'Unknown')}
""")
        
        result = {
            "success": True,
            "input_source": input_source,
            "output_directory": str(output_structure["root"]),
            "summary": extraction_results.get("summary", {}),
            "files_created": {
                "sections": len(sections),
                "figures": len(extraction_results.get("figures", {}).get("figures", [])),
                "tables": len(extraction_results.get("tables", {}).get("tables", [])),
                "metadata_files": 2  # document_info.json + citations.json
            }
        }
        
        logger.info(f"Conversion completed successfully: {output_structure['root']}")
        return result
        
    except Exception as e:
        logger.error(f"Conversion failed: {str(e)}")
        return {
            "success": False,
            "input_source": input_source,
            "error": str(e),
            "message": "Conversion failed"
        }


def config_command(args: argparse.Namespace) -> Dict[str, Any]:
    """Handle configuration commands."""
    logger = get_logger()
    
    try:
        from .config_manager import (
            get_configuration_status,
            create_config_interactive,
            fix_configuration,
            get_config_help
        )
        from .config_validator import get_validation_report
        from .smart_defaults import get_config_profiles
        
        action = args.config_action
        
        if action == "help":
            help_text = get_config_help()
            print(help_text)
            return {
                "success": True,
                "action": "help",
                "message": "Configuration help displayed"
            }
        
        elif action == "status":
            status = get_configuration_status()
            print("\n📊 Configuration Status")
            print("=" * 25)
            print(f"Has config file: {'✅' if status.has_config else '❌'}")
            if status.config_path:
                print(f"Config path: {status.config_path}")
            print(f"Configuration valid: {'✅' if status.is_valid else '❌'}")
            print(f"Profile: {status.profile or 'default'}")
            print(f"System optimal: {'✅' if status.system_optimal else '⚠️'}")
            
            if status.errors:
                print("\nErrors:")
                for error in status.errors:
                    print(f"  ❌ {error}")
            
            if status.warnings:
                print("\nWarnings:")
                for warning in status.warnings:
                    print(f"  ⚠️  {warning}")
            
            return {
                "success": True,
                "action": "status",
                "status": status.__dict__
            }
        
        elif action == "validate":
            config_path = args.config or None
            if config_path:
                report = get_validation_report(config_path)
            else:
                status = get_configuration_status()
                if status.config_path:
                    report = get_validation_report(status.config_path)
                else:
                    report = "No configuration file found to validate"
            
            print(report)
            return {
                "success": True,
                "action": "validate",
                "message": "Validation report displayed"
            }
        
        elif action == "fix":
            config_path = args.config or None
            success = fix_configuration(config_path)
            
            if success:
                print("✅ Configuration fixed successfully")
                return {
                    "success": True,
                    "action": "fix",
                    "message": "Configuration fixed"
                }
            else:
                print("❌ Could not fix configuration automatically")
                return {
                    "success": False,
                    "action": "fix",
                    "message": "Configuration could not be fixed"
                }
        
        elif action == "create":
            if args.interactive:
                config_path = create_config_interactive(args.config)
                return {
                    "success": True,
                    "action": "create",
                    "config_path": str(config_path),
                    "message": "Configuration created interactively"
                }
            else:
                # Non-interactive creation
                profile = args.profile or "balanced"
                config_path = Path(args.config) if args.config else Path.cwd() / "paper2data.yml"
                
                from .smart_defaults import create_config_file
                create_config_file(config_path, use_case=profile)
                
                print(f"✅ Configuration created: {config_path}")
                print(f"📋 Profile: {profile}")
                return {
                    "success": True,
                    "action": "create",
                    "config_path": str(config_path),
                    "profile": profile,
                    "message": "Configuration created"
                }
        
        else:
            return {
                "success": False,
                "action": action,
                "message": f"Unknown configuration action: {action}"
            }
    
    except Exception as e:
        logger.error(f"Configuration command failed: {str(e)}")
        return {
            "success": False,
            "action": args.config_action,
            "error": str(e),
            "message": "Configuration command failed"
        }


def help_command(args: argparse.Namespace) -> Dict[str, Any]:
    """Handle help command with comprehensive help system."""
    try:
        if args.help_section:
            # Show specific help section
            help_text = help_system.show_section(args.help_section)
            print(help_text)
            return {
                "success": True,
                "action": "help",
                "section": args.help_section,
                "message": f"Help section '{args.help_section}' displayed"
            }
        
        elif args.help_command:
            # Show help for specific command
            help_text = help_system.show_command_help(args.help_command)
            print(help_text)
            return {
                "success": True,
                "action": "help",
                "command": args.help_command,
                "message": f"Help for '{args.help_command}' command displayed"
            }
        
        elif args.system_info:
            # Show system information
            system_info = help_system.get_system_info()
            print(system_info)
            return {
                "success": True,
                "action": "help",
                "info": "system",
                "message": "System information displayed"
            }
        
        elif args.contextual_help:
            # Show contextual help based on current state
            contextual_help = help_system.get_contextual_help()
            print(contextual_help)
            return {
                "success": True,
                "action": "help",
                "type": "contextual",
                "message": "Contextual help displayed"
            }
        
        elif args.error_help:
            # Show help for specific error
            error_help = help_system.get_error_specific_help(args.error_help)
            print(error_help)
            return {
                "success": True,
                "action": "help",
                "type": "error",
                "error": args.error_help,
                "message": "Error-specific help displayed"
            }
        
        elif args.usage_recommendations:
            # Show usage recommendations
            recommendations = help_system.get_usage_recommendations()
            print(recommendations)
            return {
                "success": True,
                "action": "help",
                "type": "recommendations",
                "message": "Usage recommendations displayed"
            }
        
        elif args.config_help:
            # Show detailed configuration help
            config_help = help_system.get_configuration_detailed_help()
            print(config_help)
            return {
                "success": True,
                "action": "help",
                "type": "config",
                "message": "Configuration help displayed"
            }
        
        elif args.performance_help:
            # Show performance tuning help
            performance_help = help_system.get_performance_tuning_help()
            print(performance_help)
            return {
                "success": True,
                "action": "help",
                "type": "performance",
                "message": "Performance tuning help displayed"
            }
        
        else:
            # Show comprehensive help
            help_text = help_system.show_all_help()
            print(help_text)
            return {
                "success": True,
                "action": "help",
                "message": "Comprehensive help displayed"
            }
    
    except Exception as e:
        return {
            "success": False,
            "action": "help",
            "error": str(e),
            "message": "Help command failed"
        }


def main() -> int:
    """Main entry point."""
    parser = setup_argument_parser()
    args = parser.parse_args()
    
    try:
        # Handle help command early
        if args.command == "help":
            # Set up minimal logging for help command
            setup_logging(level="ERROR")  # Suppress most logs for help
            result = help_command(args)
            
            if args.json_output:
                print(json.dumps(result, indent=2))
            
            return 0 if result.get("success", False) else 1
        
        # Handle config command early (doesn't need input validation)
        if args.command == "config":
            # Set up basic logging for config command
            setup_logging(level=args.log_level or "INFO", log_file=args.log_file)
            logger = get_logger()
            logger.info(f"Starting Paper2Data parser - Command: {args.command}")
            
            result = config_command(args)
            
            # Output results
            if args.json_output:
                print(json.dumps(result, indent=2))
            
            return 0 if result.get("success", False) else 1
        
        # For other commands, validate input is provided
        if not args.input:
            print("❌ Input is required for this command")
            print("Use 'paper2data help' for usage examples")
            return 1
        
        # Load configuration
        config = load_config(args.config)
        
        # Set up logging - use stderr when JSON output is requested
        log_level = args.log_level or config.get("logging", {}).get("level", "INFO")
        log_file = args.log_file or config.get("logging", {}).get("file")
        
        # Use stderr for logging when JSON output is requested to keep stdout clean
        if args.json_output:
            import sys
            console_handler = logging.StreamHandler(sys.stderr)
            console_handler.setLevel(getattr(logging, log_level.upper()))
            formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            console_handler.setFormatter(formatter)
            
            logger = logging.getLogger("paper2data.parser")
            logger.setLevel(getattr(logging, log_level.upper()))
            logger.handlers.clear()
            logger.addHandler(console_handler)
            
            if log_file:
                file_handler = logging.FileHandler(log_file)
                file_handler.setLevel(getattr(logging, log_level.upper()))
                file_handler.setFormatter(formatter)
                logger.addHandler(file_handler)
        else:
            setup_logging(level=log_level, log_file=log_file)
        
        logger = get_logger()
        logger.info(f"Starting Paper2Data parser - Command: {args.command}")
        
        # Execute command
        if args.command == "validate":
            result = validate_input_command(args.input, args)
        elif args.command == "info":
            result = info_command(args.input, args)
        elif args.command == "convert":
            result = convert_command(args.input, args, config)
        else:
            result = {"error": f"Unknown command: {args.command}"}
        
        # Output results
        if args.json_output:
            print(json.dumps(result, indent=2))
        else:
            if result.get("success", False) or result.get("valid", False):
                print("✅ Operation completed successfully")
                if "output_directory" in result:
                    print(f"📂 Output: {result['output_directory']}")
                if "summary" in result:
                    summary = result["summary"]
                    print(f"📄 {summary.get('total_pages', 0)} pages, {summary.get('total_words', 0)} words")
                    print(f"📊 {summary.get('sections_found', 0)} sections, {summary.get('figures_found', 0)} figures, {summary.get('tables_found', 0)} tables")
            else:
                print("❌ Operation failed")
                if "error" in result:
                    print(f"Error: {result['error']}")
                print("Use 'paper2data help' for usage examples")
        
        return 0 if result.get("success", result.get("valid", False)) else 1
        
    except Exception as e:
        if args.json_output:
            print(json.dumps({"error": str(e), "success": False}, indent=2))
        else:
            print(f"❌ Fatal error: {str(e)}")
            print("Use 'paper2data help troubleshooting' for common solutions")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 
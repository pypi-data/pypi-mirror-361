"""
Paper2Data Plugin Hook System

This module defines all the hook points where plugins can integrate with
Paper2Data's processing pipeline. Hooks provide a clean interface for
extending functionality without modifying core code.

Available Hook Categories:
- Document Processing: PDF parsing, text extraction, preprocessing
- Content Analysis: Section detection, figure extraction, table processing
- Data Enhancement: Metadata enrichment, citation analysis, equation processing
- Output Generation: Format conversion, post-processing, validation
- System Integration: Configuration, logging, monitoring

Example Usage:
    ```python
    from paper2data.plugin_hooks import register_hook, execute_hook
    
    # Register a hook
    @register_hook('process_equations')
    def my_equation_processor(equations_data):
        # Process equations
        return processed_equations
    
    # Execute hooks
    results = execute_hook('process_equations', equation_data)
    ```

Author: Paper2Data Team
Version: 1.0.0
"""

from typing import Dict, List, Any, Optional, Callable, Union
from dataclasses import dataclass
from enum import Enum
import logging

logger = logging.getLogger(__name__)


class HookCategory(Enum):
    """Hook categories for organization"""
    DOCUMENT = "document"
    CONTENT = "content"
    ANALYSIS = "analysis"
    OUTPUT = "output"
    SYSTEM = "system"


@dataclass
class HookDefinition:
    """Definition of a hook point"""
    name: str
    category: HookCategory
    description: str
    parameters: Dict[str, str]
    return_type: str
    example: str
    version_added: str = "1.0.0"


# Document Processing Hooks
DOCUMENT_HOOKS = {
    "pre_process_document": HookDefinition(
        name="pre_process_document",
        category=HookCategory.DOCUMENT,
        description="Called before processing a document. Allows preprocessing of PDF files.",
        parameters={
            "file_path": "str - Path to the PDF file",
            "config": "Dict[str, Any] - Processing configuration"
        },
        return_type="Optional[str] - Modified file path or None to use original",
        example="Decrypt password-protected PDFs, fix corrupted files"
    ),
    
    "post_process_document": HookDefinition(
        name="post_process_document",
        category=HookCategory.DOCUMENT,
        description="Called after processing a document. Allows post-processing of results.",
        parameters={
            "file_path": "str - Path to the processed PDF file",
            "results": "Dict[str, Any] - Processing results",
            "config": "Dict[str, Any] - Processing configuration"
        },
        return_type="Optional[Dict[str, Any]] - Modified results or None to use original",
        example="Add custom metadata, generate summaries, create thumbnails"
    ),
    
    "extract_text": HookDefinition(
        name="extract_text",
        category=HookCategory.DOCUMENT,
        description="Alternative text extraction methods. Called when default extraction fails.",
        parameters={
            "file_path": "str - Path to the PDF file",
            "page_num": "int - Page number to extract (or -1 for all pages)",
            "config": "Dict[str, Any] - Extraction configuration"
        },
        return_type="Optional[str] - Extracted text or None if failed",
        example="OCR for scanned documents, specialized parsers for specific formats"
    ),
    
    "validate_document": HookDefinition(
        name="validate_document",
        category=HookCategory.DOCUMENT,
        description="Validate document before processing. Can reject invalid documents.",
        parameters={
            "file_path": "str - Path to the PDF file",
            "metadata": "Dict[str, Any] - Document metadata"
        },
        return_type="bool - True if document is valid, False to skip processing",
        example="Check file integrity, validate academic format, filter by content type"
    )
}

# Content Analysis Hooks
CONTENT_HOOKS = {
    "detect_sections": HookDefinition(
        name="detect_sections",
        category=HookCategory.CONTENT,
        description="Enhanced section detection. Can provide alternative section detection methods.",
        parameters={
            "text": "str - Document text",
            "pages": "List[Dict[str, Any]] - Page information",
            "config": "Dict[str, Any] - Detection configuration"
        },
        return_type="Optional[List[Dict[str, Any]]] - Detected sections or None",
        example="AI-powered section detection, domain-specific section patterns"
    ),
    
    "extract_figures": HookDefinition(
        name="extract_figures",
        category=HookCategory.CONTENT,
        description="Enhanced figure extraction. Can provide alternative extraction methods.",
        parameters={
            "document": "fitz.Document - PyMuPDF document object",
            "config": "Dict[str, Any] - Extraction configuration"
        },
        return_type="Optional[List[Dict[str, Any]]] - Extracted figures or None",
        example="AI-powered figure detection, caption extraction, figure classification"
    ),
    
    "process_tables": HookDefinition(
        name="process_tables",
        category=HookCategory.CONTENT,
        description="Enhanced table processing. Can provide alternative table extraction methods.",
        parameters={
            "document": "fitz.Document - PyMuPDF document object",
            "text": "str - Document text",
            "config": "Dict[str, Any] - Processing configuration"
        },
        return_type="Optional[List[Dict[str, Any]]] - Processed tables or None",
        example="ML-based table detection, complex table parsing, table structure analysis"
    ),
    
    "analyze_layout": HookDefinition(
        name="analyze_layout",
        category=HookCategory.CONTENT,
        description="Document layout analysis. Can provide document structure insights.",
        parameters={
            "document": "fitz.Document - PyMuPDF document object",
            "config": "Dict[str, Any] - Analysis configuration"
        },
        return_type="Optional[Dict[str, Any]] - Layout analysis results or None",
        example="Column detection, reading order analysis, document structure classification"
    ),
    
    "extract_images": HookDefinition(
        name="extract_images",
        category=HookCategory.CONTENT,
        description="Enhanced image extraction with analysis capabilities.",
        parameters={
            "document": "fitz.Document - PyMuPDF document object",
            "config": "Dict[str, Any] - Extraction configuration"
        },
        return_type="Optional[List[Dict[str, Any]]] - Extracted images with metadata or None",
        example="Image quality assessment, duplicate detection, image classification"
    )
}

# Data Enhancement Hooks
ANALYSIS_HOOKS = {
    "process_equations": HookDefinition(
        name="process_equations",
        category=HookCategory.ANALYSIS,
        description="Mathematical equation processing and conversion.",
        parameters={
            "equations": "List[Dict[str, Any]] - Detected equations",
            "config": "Dict[str, Any] - Processing configuration"
        },
        return_type="Optional[List[Dict[str, Any]]] - Processed equations or None",
        example="LaTeX conversion, MathML generation, equation parsing"
    ),
    
    "enhance_metadata": HookDefinition(
        name="enhance_metadata",
        category=HookCategory.ANALYSIS,
        description="Metadata enrichment from external sources.",
        parameters={
            "metadata": "Dict[str, Any] - Extracted metadata",
            "config": "Dict[str, Any] - Enhancement configuration"
        },
        return_type="Optional[Dict[str, Any]] - Enhanced metadata or None",
        example="DOI resolution, author disambiguation, citation enrichment"
    ),
    
    "analyze_citations": HookDefinition(
        name="analyze_citations",
        category=HookCategory.ANALYSIS,
        description="Citation analysis and network building.",
        parameters={
            "citations": "List[Dict[str, Any]] - Extracted citations",
            "metadata": "Dict[str, Any] - Document metadata",
            "config": "Dict[str, Any] - Analysis configuration"
        },
        return_type="Optional[Dict[str, Any]] - Citation analysis results or None",
        example="Citation network construction, impact analysis, duplicate detection"
    ),
    
    "extract_keywords": HookDefinition(
        name="extract_keywords",
        category=HookCategory.ANALYSIS,
        description="Keyword and topic extraction from document content.",
        parameters={
            "text": "str - Document text",
            "metadata": "Dict[str, Any] - Document metadata",
            "config": "Dict[str, Any] - Extraction configuration"
        },
        return_type="Optional[List[str]] - Extracted keywords or None",
        example="NLP-based keyword extraction, domain-specific term identification"
    ),
    
    "classify_content": HookDefinition(
        name="classify_content",
        category=HookCategory.ANALYSIS,
        description="Document content classification and categorization.",
        parameters={
            "text": "str - Document text",
            "metadata": "Dict[str, Any] - Document metadata",
            "config": "Dict[str, Any] - Classification configuration"
        },
        return_type="Optional[Dict[str, Any]] - Classification results or None",
        example="Subject classification, document type detection, quality assessment"
    ),
    
    "analyze_structure": HookDefinition(
        name="analyze_structure",
        category=HookCategory.ANALYSIS,
        description="Advanced document structure analysis.",
        parameters={
            "sections": "List[Dict[str, Any]] - Document sections",
            "figures": "List[Dict[str, Any]] - Document figures",
            "tables": "List[Dict[str, Any]] - Document tables",
            "config": "Dict[str, Any] - Analysis configuration"
        },
        return_type="Optional[Dict[str, Any]] - Structure analysis results or None",
        example="Logical structure mapping, cross-reference analysis, content hierarchy"
    )
}

# Output Generation Hooks
OUTPUT_HOOKS = {
    "format_output": HookDefinition(
        name="format_output",
        category=HookCategory.OUTPUT,
        description="Custom output formatting for specific formats.",
        parameters={
            "data": "Dict[str, Any] - Processing results",
            "format": "str - Output format name",
            "config": "Dict[str, Any] - Formatting configuration"
        },
        return_type="Optional[str] - Formatted output or None",
        example="Custom HTML templates, specialized XML formats, API-specific formats"
    ),
    
    "post_process_output": HookDefinition(
        name="post_process_output",
        category=HookCategory.OUTPUT,
        description="Post-processing of generated output files.",
        parameters={
            "output_path": "str - Path to output directory",
            "files": "List[str] - List of generated files",
            "config": "Dict[str, Any] - Post-processing configuration"
        },
        return_type="Optional[List[str]] - Modified file list or None",
        example="Compression, encryption, upload to cloud storage, notification"
    ),
    
    "validate_output": HookDefinition(
        name="validate_output",
        category=HookCategory.OUTPUT,
        description="Validation of generated output for quality assurance.",
        parameters={
            "output_path": "str - Path to output directory",
            "data": "Dict[str, Any] - Processing results",
            "config": "Dict[str, Any] - Validation configuration"
        },
        return_type="Optional[Dict[str, Any]] - Validation results or None",
        example="Quality metrics calculation, completeness checking, format validation"
    ),
    
    "generate_report": HookDefinition(
        name="generate_report",
        category=HookCategory.OUTPUT,
        description="Generation of processing reports and summaries.",
        parameters={
            "data": "Dict[str, Any] - Processing results",
            "statistics": "Dict[str, Any] - Processing statistics",
            "config": "Dict[str, Any] - Report configuration"
        },
        return_type="Optional[str] - Generated report or None",
        example="Quality reports, processing summaries, statistical analysis"
    )
}

# System Integration Hooks
SYSTEM_HOOKS = {
    "configure_processing": HookDefinition(
        name="configure_processing",
        category=HookCategory.SYSTEM,
        description="Dynamic configuration of processing parameters.",
        parameters={
            "config": "Dict[str, Any] - Current configuration",
            "document_info": "Dict[str, Any] - Document information",
            "context": "Dict[str, Any] - Processing context"
        },
        return_type="Optional[Dict[str, Any]] - Modified configuration or None",
        example="Document-specific settings, adaptive processing parameters"
    ),
    
    "log_processing": HookDefinition(
        name="log_processing",
        category=HookCategory.SYSTEM,
        description="Custom logging and monitoring of processing events.",
        parameters={
            "event": "str - Event type",
            "data": "Dict[str, Any] - Event data",
            "context": "Dict[str, Any] - Processing context"
        },
        return_type="None",
        example="External logging services, metrics collection, monitoring dashboards"
    ),
    
    "handle_error": HookDefinition(
        name="handle_error",
        category=HookCategory.SYSTEM,
        description="Custom error handling and recovery strategies.",
        parameters={
            "error": "Exception - The error that occurred",
            "context": "Dict[str, Any] - Processing context",
            "config": "Dict[str, Any] - Error handling configuration"
        },
        return_type="Optional[bool] - True if error was handled, False to re-raise",
        example="Error notification, fallback processing, automatic retry"
    ),
    
    "monitor_performance": HookDefinition(
        name="monitor_performance",
        category=HookCategory.SYSTEM,
        description="Performance monitoring and optimization.",
        parameters={
            "metrics": "Dict[str, Any] - Performance metrics",
            "context": "Dict[str, Any] - Processing context"
        },
        return_type="Optional[Dict[str, Any]] - Performance recommendations or None",
        example="Resource usage monitoring, performance optimization suggestions"
    )
}

# All hooks registry
ALL_HOOKS = {
    **DOCUMENT_HOOKS,
    **CONTENT_HOOKS,
    **ANALYSIS_HOOKS,
    **OUTPUT_HOOKS,
    **SYSTEM_HOOKS
}


def get_hook_definition(hook_name: str) -> Optional[HookDefinition]:
    """
    Get the definition of a specific hook
    
    Args:
        hook_name: Name of the hook
        
    Returns:
        Optional[HookDefinition]: Hook definition or None if not found
    """
    return ALL_HOOKS.get(hook_name)


def list_hooks_by_category(category: HookCategory) -> Dict[str, HookDefinition]:
    """
    List all hooks in a specific category
    
    Args:
        category: Hook category
        
    Returns:
        Dict[str, HookDefinition]: Dictionary of hooks in the category
    """
    return {
        name: hook_def 
        for name, hook_def in ALL_HOOKS.items() 
        if hook_def.category == category
    }


def get_all_hook_names() -> List[str]:
    """
    Get list of all available hook names
    
    Returns:
        List[str]: List of hook names
    """
    return list(ALL_HOOKS.keys())


def validate_hook_name(hook_name: str) -> bool:
    """
    Validate if a hook name is valid
    
    Args:
        hook_name: Hook name to validate
        
    Returns:
        bool: True if valid, False otherwise
    """
    return hook_name in ALL_HOOKS


def get_hook_documentation() -> Dict[str, Dict[str, Any]]:
    """
    Get complete documentation for all hooks
    
    Returns:
        Dict[str, Dict[str, Any]]: Complete hook documentation
    """
    doc = {}
    
    for category in HookCategory:
        category_hooks = list_hooks_by_category(category)
        doc[category.value] = {
            "description": f"Hooks for {category.value} processing",
            "hooks": {
                name: {
                    "description": hook_def.description,
                    "parameters": hook_def.parameters,
                    "return_type": hook_def.return_type,
                    "example": hook_def.example,
                    "version_added": hook_def.version_added
                }
                for name, hook_def in category_hooks.items()
            }
        }
    
    return doc


# Hook execution utilities
def execute_hook(hook_name: str, *args, **kwargs) -> List[Any]:
    """
    Execute a hook using the global plugin manager
    
    Args:
        hook_name: Name of hook to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        List[Any]: Results from hook execution
    """
    from .plugin_manager import get_plugin_manager
    
    if not validate_hook_name(hook_name):
        logger.warning(f"Unknown hook name: {hook_name}")
        return []
    
    manager = get_plugin_manager()
    return manager.execute_hook(hook_name, *args, **kwargs)


def execute_hook_until_success(hook_name: str, *args, **kwargs) -> Any:
    """
    Execute hook until one succeeds
    
    Args:
        hook_name: Name of hook to execute
        *args: Positional arguments
        **kwargs: Keyword arguments
        
    Returns:
        Any: First successful result
    """
    from .plugin_manager import get_plugin_manager
    
    if not validate_hook_name(hook_name):
        logger.warning(f"Unknown hook name: {hook_name}")
        return None
    
    manager = get_plugin_manager()
    return manager.execute_hook_until_success(hook_name, *args, **kwargs)


def register_hook(hook_name: str, priority: 'HookPriority' = None):
    """
    Decorator for registering hook functions
    
    Args:
        hook_name: Name of the hook
        priority: Execution priority
        
    Returns:
        Decorator function
    """
    from .plugin_manager import plugin_hook, HookPriority
    
    if priority is None:
        priority = HookPriority.NORMAL
    
    if not validate_hook_name(hook_name):
        logger.warning(f"Unknown hook name: {hook_name}")
    
    return plugin_hook(hook_name, priority)


# Hook categories for easy access
HOOK_CATEGORIES = {
    "document": DOCUMENT_HOOKS,
    "content": CONTENT_HOOKS,
    "analysis": ANALYSIS_HOOKS,
    "output": OUTPUT_HOOKS,
    "system": SYSTEM_HOOKS
} 
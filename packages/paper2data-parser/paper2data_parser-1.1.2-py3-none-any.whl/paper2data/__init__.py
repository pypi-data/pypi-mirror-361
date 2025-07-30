"""
Paper2Data Parser Package

A Python package for extracting and parsing content from academic papers.
Supports PDF files, arXiv URLs, and DOI resolution.
"""

__version__ = "1.1.2"
__author__ = "Paper2Data Team"
__email__ = "team@paper2data.dev"

# Main API exports
from .ingest import PDFIngestor, URLIngestor, DOIIngestor, create_ingestor
from .config_manager import (
    ConfigManager,
    ConfigurationStatus,
    load_config,
    save_config,
    create_config_interactive,
    get_configuration_status,
    fix_configuration,
    get_config_help,
    config_manager
)
from .config_schema import Paper2DataConfig, CONFIG_PROFILES
from .smart_defaults import (
    get_smart_config,
    get_system_info,
    create_config_file,
    get_config_profiles,
    smart_defaults
)
from .config_validator import (
    validate_config,
    validate_config_file,
    get_validation_report,
    fix_config_issues,
    config_validator
)
from .extractor import (
    ContentExtractor, 
    SectionExtractor, 
    FigureExtractor, 
    TableExtractor, 
    CitationExtractor,
    extract_all_content,
    extract_all_content_optimized
)
from .api_integration import (
    ArxivAPIClient,
    DOIAPIClient,
    BatchProcessor,
    arxiv_client,
    doi_client,
    batch_processor,
    api_cache
)
from .performance import (
    ResourceMonitor,
    PerformanceCache,
    ParallelExtractor,
    BatchProcessor as PerformanceBatchProcessor,
    StreamingProcessor,
    ProgressPersistence,
    get_performance_cache,
    get_resource_monitor,
    get_parallel_extractor,
    extract_with_full_optimization,
    get_system_recommendations,
    clear_all_caches,
    memory_optimized,
    with_performance_monitoring
)
from .equation_processor import (
    EquationProcessor,
    EquationRegion,
    EquationExtractionResult,
    MathematicalPatternDetector,
    LaTeXConverter,
    MathMLGenerator,
    create_equation_processor,
    process_equations_from_pdf,
    integrate_with_extractor
)
from .advanced_figure_processor import (
    AdvancedFigureProcessor,
    CaptionDetector,
    ImageAnalyzer,
    FigureClassifier,
    AdvancedFigure,
    FigureCaption,
    ImageAnalysis,
    FigureType,
    ImageQuality,
    CaptionPosition,
    get_advanced_figure_processor,
    process_advanced_figures
)
from .metadata_extractor import (
    MetadataExtractor,
    EnhancedMetadata,
    Author,
    PublicationInfo,
    Citation,
    PaperType,
    PublicationStatus,
    extract_metadata,
    export_metadata,
    metadata_extractor
)
from .enhanced_metadata_v1_1 import (
    EnhancedMetadataExtractor,
    EnhancedMetadata as EnhancedMetadataV1_1,
    EnhancedAuthor,
    Institution,
    FundingSource,
    AuthorIdentifier,
    AuthorNameFormat,
    InstitutionType,
    FundingSourceType,
    InstitutionDatabase,
    FundingDatabase,
    create_enhanced_metadata_extractor,
    integrate_with_content_extractor
)
from .bibliographic_parser import (
    BibliographicParser,
    BibliographicReference,
    BibliographicAuthor,
    BibliographicDatabase,
    BibliographicNormalizer,
    CitationStyleDetector,
    ReferenceParser,
    CitationStyle,
    ReferenceType,
    CitationQuality,
    create_bibliographic_parser,
    integrate_with_enhanced_metadata
)
from .citation_network_analyzer import (
    CitationNetworkAnalyzer,
    NetworkNode,
    NetworkEdge,
    NetworkMetrics,
    AuthorMetrics,
    CitationInfluence,
    NetworkType,
    CentralityMetric,
    build_citation_network,
    analyze_citation_networks,
    citation_network_analyzer
)
from .output_formatters import (
    OutputFormat,
    FormatConfig,
    BaseFormatter,
    JSONFormatter,
    HTMLFormatter,
    LaTeXFormatter,
    XMLFormatter,
    CSVFormatter,
    MarkdownFormatter,
    DOCXFormatter,
    FormatterFactory,
    format_output,
    batch_format,
    export_to_html,
    export_to_latex,
    export_to_xml,
    export_to_csv,
    export_to_markdown,
    export_all_formats,
    default_config
)
from .plugin_manager import (
    PluginManager,
    BasePlugin,
    PluginMetadata,
    PluginInfo,
    PluginStatus,
    HookPriority,
    HookRegistration,
    plugin_hook,
    get_plugin_manager,
    initialize_plugin_system
)
from .plugin_hooks import (
    HookCategory,
    HookDefinition,
    execute_hook,
    execute_hook_until_success,
    register_hook,
    get_hook_definition,
    list_hooks_by_category,
    get_all_hook_names,
    validate_hook_name,
    get_hook_documentation,
    ALL_HOOKS,
    HOOK_CATEGORIES
)
from .utils import (
    setup_logging, 
    get_logger,
    validate_input, 
    format_output, 
    clean_text,
    load_config,
    save_json,
    ensure_directory,
    create_output_structure,
    progress_callback,
    suppress_stderr,
    normalize_url,
    normalize_arxiv_url,
    normalize_doi,
    validate_arxiv_id,
    validate_doi,
    extract_identifiers_from_text,
    validate_url_accessibility,
    ProcessingError,
    ValidationError,
    ConfigurationError
)

# Help system
from .help_system import help_system

# Multi-format output system
from .multi_format_exporter import (
    MultiFormatExporter,
    ExportConfiguration,
    ExportedDocument,
    OutputFormat,
    TemplateTheme,
    HTMLExporter,
    LaTeXExporter,
    WordExporter,
    EPUBExporter,
    MarkdownExporter,
    BaseFormatExporter
)

# Enhanced Plugin System v1.1
from .plugin_dependency_manager import (
    DependencyManager,
    VersionConstraint,
    DependencyType,
    ConflictResolution,
    DependencyNode,
    DependencyConflict,
    DependencyResolution
)
from .plugin_marketplace import (
    PluginMarketplace,
    PluginListing,
    PluginCategory,
    SecurityStatus,
    PluginCompatibility,
    PluginReview,
    PluginStatistics,
    SearchFilter,
    get_plugin_marketplace,
    marketplace_client
)
from .plugin_system_enhanced import (
    EnhancedPluginSystem,
    PluginHealth,
    SystemMetrics,
    PluginConfiguration,
    initialize_enhanced_plugin_system,
    get_enhanced_plugin_system
)

# All exports for comprehensive API access
__all__ = [
    # Version information
    "__version__",
    "__author__",
    "__email__",
    
    # Core ingest functionality
    "PDFIngestor",
    "URLIngestor", 
    "DOIIngestor",
    "create_ingestor",
    
    # Configuration management
    "ConfigManager",
    "ConfigurationStatus",
    "load_config",
    "save_config",
    "create_config_interactive",
    "get_configuration_status",
    "fix_configuration",
    "get_config_help",
    "config_manager",
    "Paper2DataConfig",
    "CONFIG_PROFILES",
    
    # Smart defaults and validation
    "get_smart_config",
    "get_system_info",
    "create_config_file",
    "get_config_profiles",
    "smart_defaults",
    "validate_config",
    "validate_config_file",
    "get_validation_report",
    "fix_config_issues",
    "config_validator",
    
    # Content extraction
    "ContentExtractor",
    "SectionExtractor",
    "FigureExtractor",
    "TableExtractor",
    "CitationExtractor",
    "extract_all_content",
    "extract_all_content_optimized",
    
    # API integration
    "ArxivAPIClient",
    "DOIAPIClient",
    "BatchProcessor",
    "arxiv_client",
    "doi_client",
    "batch_processor",
    "api_cache",
    
    # Performance optimization
    "ResourceMonitor",
    "PerformanceCache",
    "ParallelExtractor",
    "PerformanceBatchProcessor",
    "StreamingProcessor",
    "ProgressPersistence",
    "get_performance_cache",
    "get_resource_monitor",
    "get_parallel_extractor",
    "extract_with_full_optimization",
    "get_system_recommendations",
    "clear_all_caches",
    "memory_optimized",
    "with_performance_monitoring",
    
    # Equation processing
    "EquationProcessor",
    "EquationRegion",
    "EquationExtractionResult",
    "MathematicalPatternDetector",
    "LaTeXConverter",
    "MathMLGenerator",
    "create_equation_processor",
    "process_equations_from_pdf",
    "integrate_with_extractor",
    
    # Advanced figure processing
    "AdvancedFigureProcessor",
    "CaptionDetector",
    "ImageAnalyzer",
    "FigureClassifier",
    "AdvancedFigure",
    "FigureCaption",
    "ImageAnalysis",
    "FigureType",
    "ImageQuality",
    "CaptionPosition",
    "get_advanced_figure_processor",
    "process_advanced_figures",
    
    # Metadata extraction
    "MetadataExtractor",
    "EnhancedMetadata",
    "Author",
    "PublicationInfo",
    "Citation",
    "PaperType",
    "PublicationStatus",
    "extract_metadata",
    "export_metadata",
    "metadata_extractor",
    
    # Enhanced metadata v1.1
    "EnhancedMetadataExtractor",
    "EnhancedMetadataV1_1",
    "EnhancedAuthor",
    "Institution",
    "FundingSource",
    "AuthorIdentifier",
    "AuthorNameFormat",
    "InstitutionType",
    "FundingSourceType",
    "InstitutionDatabase",
    "FundingDatabase",
    "create_enhanced_metadata_extractor",
    "integrate_with_content_extractor",
    
    # Bibliographic processing
    "BibliographicParser",
    "BibliographicReference",
    "BibliographicAuthor",
    "BibliographicDatabase",
    "BibliographicNormalizer",
    "CitationStyleDetector",
    "ReferenceParser",
    "CitationStyle",
    "ReferenceType",
    "CitationQuality",
    "create_bibliographic_parser",
    "integrate_with_enhanced_metadata",
    
    # Citation network analysis
    "CitationNetworkAnalyzer",
    "NetworkNode",
    "NetworkEdge",
    "NetworkMetrics",
    "AuthorMetrics",
    "CitationInfluence",
    "NetworkType",
    "CentralityMetric",
    "build_citation_network",
    "analyze_citation_networks",
    "citation_network_analyzer",
    
    # Output formatting
    "OutputFormat",
    "FormatConfig",
    "BaseFormatter",
    "JSONFormatter",
    "HTMLFormatter",
    "LaTeXFormatter",
    "XMLFormatter",
    "CSVFormatter",
    "MarkdownFormatter",
    "DOCXFormatter",
    "FormatterFactory",
    "format_output",
    "batch_format",
    "export_to_html",
    "export_to_latex",
    "export_to_xml",
    "export_to_csv",
    "export_to_markdown",
    "export_all_formats",
    "default_config",
    
    # Plugin system
    "PluginManager",
    "BasePlugin",
    "PluginMetadata",
    "PluginInfo",
    "PluginStatus",
    "HookPriority",
    "HookRegistration",
    "plugin_hook",
    "get_plugin_manager",
    "initialize_plugin_system",
    
    # Plugin hooks
    "HookCategory",
    "HookDefinition",
    "execute_hook",
    "execute_hook_until_success",
    "register_hook",
    "get_hook_definition",
    "list_hooks_by_category",
    "get_all_hook_names",
    "validate_hook_name",
    "get_hook_documentation",
    "ALL_HOOKS",
    "HOOK_CATEGORIES",
    
    # Multi-format export
    "MultiFormatExporter",
    "ExportConfiguration",
    "ExportedDocument",
    "TemplateTheme",
    "HTMLExporter",
    "LaTeXExporter",
    "WordExporter",
    "EPUBExporter",
    "MarkdownExporter",
    "BaseFormatExporter",
    
    # Enhanced Plugin System v1.1
    "DependencyManager",
    "VersionConstraint",
    "DependencyType",
    "ConflictResolution",
    "DependencyNode",
    "DependencyConflict",
    "DependencyResolution",
    "PluginMarketplace",
    "PluginListing",
    "PluginCategory",
    "SecurityStatus",
    "PluginCompatibility",
    "PluginReview",
    "PluginStatistics",
    "SearchFilter",
    "get_plugin_marketplace",
    "marketplace_client",
    "EnhancedPluginSystem",
    "PluginHealth",
    "SystemMetrics",
    "PluginConfiguration",
    "initialize_enhanced_plugin_system",
    "get_enhanced_plugin_system",
    
    # Utilities
    "setup_logging",
    "get_logger",
    "validate_input",
    "clean_text",
    "save_json",
    "ensure_directory",
    "create_output_structure",
    "progress_callback",
    "suppress_stderr",
    "normalize_url",
    "normalize_arxiv_url",
    "normalize_doi",
    "validate_arxiv_id",
    "validate_doi",
    "extract_identifiers_from_text",
    "validate_url_accessibility",
    "ProcessingError",
    "ValidationError",
    "ConfigurationError",
    
    # Help system
    "help_system",
]

# Package metadata
SUPPORTED_FORMATS = ["pdf"]
SUPPORTED_SOURCES = ["file", "url", "arxiv", "doi"]
DEFAULT_CONFIG = {
    "output": {
        "format": "json",
        "directory": "./paper2data_output",
        "preserve_structure": True
    },
    "processing": {
        "extract_figures": True,
        "extract_tables": True,
        "extract_citations": True,
        "max_file_size_mb": 100
    },
    "logging": {
        "level": "INFO",
        "file": None
    }
} 
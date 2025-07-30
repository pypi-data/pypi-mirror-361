"""
Utility functions for Paper2Data parser.

Provides common functionality for file operations, logging, configuration,
and data processing across the application.
"""

import os
import sys
import json
import yaml
import logging
import re
from pathlib import Path
from typing import Dict, Any, Optional, Union, List, Tuple
from contextlib import contextmanager
from urllib.parse import urlparse, urlunparse
import tempfile


@contextmanager
def suppress_stderr():
    """Context manager to suppress stderr output (like MuPDF errors)."""
    # Save the original stderr file descriptor
    old_stderr_fd = os.dup(2)
    try:
        # Redirect stderr to devnull
        devnull_fd = os.open(os.devnull, os.O_WRONLY)
        os.dup2(devnull_fd, 2)
        os.close(devnull_fd)
        yield
    finally:
        # Restore stderr
        os.dup2(old_stderr_fd, 2)
        os.close(old_stderr_fd)


def setup_logging(
    level: str = "INFO",
    log_file: Optional[Path] = None,
    format_string: Optional[str] = None
) -> logging.Logger:
    """Set up logging configuration for the parser.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional file path to write logs to
        format_string: Custom format string for log messages
    
    Returns:
        Configured logger instance
        
    Raises:
        ValueError: If invalid logging level is provided
    """
    # Validate logging level
    numeric_level = getattr(logging, level.upper(), None)
    if not isinstance(numeric_level, int):
        raise ValueError(f'Invalid log level: {level}')
    
    # Create logger
    logger = logging.getLogger("paper2data.parser")
    logger.setLevel(numeric_level)
    
    # Clear any existing handlers
    logger.handlers.clear()
    
    # Default format string
    if format_string is None:
        format_string = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    formatter = logging.Formatter(format_string)
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(numeric_level)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File handler (optional)
    if log_file:
        log_file = Path(log_file)
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(numeric_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
        logger.info(f"Logging to file: {log_file}")
    
    logger.info(f"Logging configured at {level} level")
    return logger


def get_logger(name: str = "paper2data.parser") -> logging.Logger:
    """Get a logger instance with the specified name.
    
    Args:
        name: Logger name
        
    Returns:
        Logger instance
    """
    return logging.getLogger(name)


def format_output(
    data: Dict[str, Any],
    output_format: str = "json"
) -> Union[str, bytes]:
    """Format extracted data for output.
    
    Args:
        data: Data dictionary to format
        output_format: Output format ('json', 'yaml', 'markdown')
        
    Returns:
        Formatted data as string or bytes
        
    Raises:
        ValueError: If unsupported output format is specified
    """
    logger = get_logger()
    logger.debug(f"Formatting output as {output_format}")
    
    if output_format.lower() == "json":
        return json.dumps(data, indent=2, ensure_ascii=False)
    elif output_format.lower() == "yaml":
        return yaml.dump(data, default_flow_style=False, allow_unicode=True)
    elif output_format.lower() == "markdown":
        # Basic markdown formatting for metadata
        lines = ["# Document Metadata\n"]
        for key, value in data.items():
            if isinstance(value, dict):
                lines.append(f"## {key.title()}\n")
                for subkey, subvalue in value.items():
                    lines.append(f"- **{subkey}**: {subvalue}")
            else:
                lines.append(f"- **{key}**: {value}")
        return "\n".join(lines)
    else:
        raise ValueError(f"Unsupported output format: {output_format}")


def clean_text(text: str) -> str:
    """Clean and normalize extracted text.
    
    Args:
        text: Raw text to clean
        
    Returns:
        Cleaned text string
    """
    logger = get_logger()
    logger.debug("Cleaning extracted text")
    
    # Preserve section break markers before cleaning
    has_section_breaks = "===SECTION_BREAK===" in text
    
    if has_section_breaks:
        # Split by section breaks and clean each part separately
        parts = text.split("===SECTION_BREAK===")
        cleaned_parts = []
        
        for part in parts:
            # Clean each part but preserve structure
            cleaned_part = part.strip()
            
            # Remove common PDF artifacts
            cleaned_part = cleaned_part.replace("\x00", "")  # Null bytes
            cleaned_part = cleaned_part.replace("\ufeff", "")  # BOM
            cleaned_part = cleaned_part.replace("\u200b", "")  # Zero-width space
            
            # Normalize line breaks but don't collapse all whitespace
            cleaned_part = cleaned_part.replace("\r\n", "\n").replace("\r", "\n")
            
            # Remove excessive line breaks but preserve paragraph structure
            while "\n\n\n" in cleaned_part:
                cleaned_part = cleaned_part.replace("\n\n\n", "\n\n")
            
            if cleaned_part:
                cleaned_parts.append(cleaned_part)
        
        # Rejoin with section breaks but add newlines for proper parsing
        return "\n===SECTION_BREAK===\n".join(cleaned_parts)
    
    else:
        # Standard cleaning for regular text
        # Remove extra whitespace
        text = " ".join(text.split())
        
        # Remove common PDF artifacts
        text = text.replace("\x00", "")  # Null bytes
        text = text.replace("\ufeff", "")  # BOM
        text = text.replace("\u200b", "")  # Zero-width space
        
        # Normalize line breaks
        text = text.replace("\r\n", "\n").replace("\r", "\n")
        
        # Remove excessive line breaks
        while "\n\n\n" in text:
            text = text.replace("\n\n\n", "\n\n")
        
        return text.strip()


def extract_filename_from_url(url: str) -> str:
    """Extract a reasonable filename from a URL."""
    # TODO: Implement filename extraction
    logging.info(f"Extracting filename from URL: {url}")
    raise NotImplementedError("Filename extraction not yet implemented")


def ensure_directory(path: Path) -> Path:
    """Ensure directory exists, create if it doesn't.
    
    Args:
        path: Directory path to ensure
        
    Returns:
        Path object of the created/existing directory
        
    Raises:
        OSError: If directory cannot be created
    """
    logger = get_logger()
    logger.debug(f"Ensuring directory exists: {path}")
    
    try:
        path.mkdir(parents=True, exist_ok=True)
        logger.debug(f"Directory ready: {path}")
        return path
    except OSError as e:
        logger.error(f"Failed to create directory {path}: {e}")
        raise


def save_json(data: Dict[str, Any], filepath: Path) -> None:
    """Save data as JSON file.
    
    Args:
        data: Data to save
        filepath: Target file path
        
    Raises:
        OSError: If file cannot be written
    """
    logger = get_logger()
    logger.debug(f"Saving JSON to: {filepath}")
    
    try:
        ensure_directory(filepath.parent)
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        logger.info(f"JSON saved successfully: {filepath}")
    except OSError as e:
        logger.error(f"Failed to save JSON to {filepath}: {e}")
        raise


def load_config(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Load configuration from YAML file.
    
    DEPRECATED: Use config_manager.load_config() for new code.
    This function is maintained for backward compatibility.
    
    Args:
        config_path: Path to configuration file. If None, uses default locations.
        
    Returns:
        Configuration dictionary
        
    Raises:
        ConfigurationError: If configuration cannot be loaded or is invalid
    """
    logger = get_logger()
    
    try:
        # Use the new configuration system
        from .config_manager import load_config as new_load_config
        config = new_load_config(config_path=config_path)
        
        # Convert to dictionary for backward compatibility
        config_dict = config.dict(exclude_none=True)
        
        logger.info("Configuration loaded successfully using new system")
        return config_dict
        
    except Exception as e:
        logger.warning(f"New configuration system failed: {e}")
        logger.info("Falling back to legacy configuration loading")
        
        # Fallback to old system
        return _load_config_legacy(config_path)


def _load_config_legacy(config_path: Optional[Path] = None) -> Dict[str, Any]:
    """Legacy configuration loading (fallback)."""
    logger = get_logger()
    
    # Default configuration
    default_config = {
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
    
    if config_path is None:
        # Try default locations
        possible_paths = [
            Path.cwd() / "paper2data.yml",
            Path.cwd() / "paper2data.yaml", 
            Path.home() / ".paper2data" / "config.yml",
            Path.home() / ".paper2data" / "config.yaml"
        ]
        
        for path in possible_paths:
            if path.exists():
                config_path = path
                break
        
        if config_path is None:
            logger.info("No configuration file found, using defaults")
            return default_config
    
    logger.info(f"Loading configuration from: {config_path}")
    
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = yaml.safe_load(f)
        
        if not isinstance(config, dict):
            raise ConfigurationError("Configuration file must contain a dictionary")
        
        # Merge with defaults
        merged_config = default_config.copy()
        for key, value in config.items():
            if key in merged_config and isinstance(merged_config[key], dict) and isinstance(value, dict):
                merged_config[key].update(value)
            else:
                merged_config[key] = value
        
        logger.info("Configuration loaded successfully")
        return merged_config
        
    except yaml.YAMLError as e:
        raise ConfigurationError(f"Invalid YAML in configuration file: {e}")
    except OSError as e:
        raise ConfigurationError(f"Cannot read configuration file: {e}")


def get_file_hash(filepath: Path) -> str:
    """Generate hash for file content."""
    # TODO: Implement file hashing
    logging.info(f"Generating hash for: {filepath}")
    raise NotImplementedError("File hashing not yet implemented")


def progress_callback(current: int, total: int, message: str = "") -> None:
    """Callback function for progress tracking.
    
    Args:
        current: Current progress value
        total: Total progress value
        message: Optional progress message
    """
    logger = get_logger()
    percentage = (current / total * 100) if total > 0 else 0
    
    if message:
        logger.info(f"Progress: {current}/{total} ({percentage:.1f}%) - {message}")
    else:
        logger.info(f"Progress: {current}/{total} ({percentage:.1f}%)")


def create_output_structure(base_path: Path, paper_title: str = "unknown") -> Dict[str, Path]:
    """Create standardized output directory structure.
    
    Args:
        base_path: Base output directory
        paper_title: Title of the paper for naming
        
    Returns:
        Dictionary mapping structure names to paths
    """
    logger = get_logger()
    logger.info(f"Creating output structure at: {base_path}")
    
    # Sanitize paper title for directory name
    safe_title = "".join(c for c in paper_title if c.isalnum() or c in (' ', '-', '_')).strip()
    safe_title = safe_title.replace(' ', '_').lower()[:50]  # Limit length
    
    if not safe_title:
        safe_title = "unknown_paper"
    
    # Create directory structure
    structure = {
        "root": base_path / safe_title,
        "sections": base_path / safe_title / "sections",
        "figures": base_path / safe_title / "figures", 
        "tables": base_path / safe_title / "tables",
        "metadata": base_path / safe_title / "metadata"
    }
    
    # Create all directories
    for name, path in structure.items():
        ensure_directory(path)
    
    logger.info(f"Output structure created: {structure['root']}")
    return structure


class ProcessingError(Exception):
    """Raised when PDF processing fails."""
    pass


class ValidationError(Exception):
    """Raised when input validation fails."""
    pass


class ConfigurationError(Exception):
    """Raised when configuration is invalid or missing."""
    pass


def validate_input(input_path: str) -> bool:
    """Validate input file or URL.
    
    Args:
        input_path: Path to file or URL to validate
        
    Returns:
        True if input is valid
        
    Raises:
        ValidationError: If input is invalid
    """
    logger = get_logger()
    logger.debug(f"Validating input: {input_path}")
    
    # Check if it's a URL
    if input_path.startswith(('http://', 'https://', 'arxiv:', 'doi:')):
        logger.debug("Input detected as URL")
        # Basic URL validation
        if len(input_path.strip()) == 0:
            raise ValidationError("URL cannot be empty")
        return True
    
    # Check if it's a file path
    path = Path(input_path)
    if not path.exists():
        raise ValidationError(f"File not found: {input_path}")
    
    if not path.is_file():
        raise ValidationError(f"Path is not a file: {input_path}")
    
    if path.suffix.lower() != '.pdf':
        raise ValidationError(f"File must be a PDF: {input_path}")
    
    # Check file size (max 100MB)
    file_size = path.stat().st_size
    max_size = 100 * 1024 * 1024  # 100MB
    if file_size > max_size:
        raise ValidationError(f"File too large: {file_size / (1024*1024):.1f}MB (max: 100MB)")
    
    logger.info(f"Input validation successful: {input_path}")
    return True


def normalize_url(url: str) -> str:
    """Normalize and clean URL for consistent processing.
    
    Args:
        url: Raw URL string
        
    Returns:
        Normalized URL string
        
    Raises:
        ValueError: If URL is invalid
    """
    logger = get_logger()
    logger.debug(f"Normalizing URL: {url}")
    
    # Clean the URL
    url = url.strip()
    
    # Add protocol if missing
    if not url.startswith(('http://', 'https://')):
        if url.startswith('//'):
            url = 'https:' + url
        else:
            url = 'https://' + url
    
    # Parse URL
    try:
        parsed = urlparse(url)
    except Exception as e:
        raise ValueError(f"Invalid URL format: {url}")
    
    # Normalize components
    scheme = parsed.scheme.lower()
    netloc = parsed.netloc.lower()
    path = parsed.path
    
    # Remove default ports
    if ':80' in netloc and scheme == 'http':
        netloc = netloc.replace(':80', '')
    elif ':443' in netloc and scheme == 'https':
        netloc = netloc.replace(':443', '')
    
    # Normalize path
    if not path:
        path = '/'
    
    # Reconstruct URL
    normalized = urlunparse((scheme, netloc, path, parsed.params, parsed.query, parsed.fragment))
    
    logger.debug(f"Normalized URL: {normalized}")
    return normalized


def normalize_arxiv_url(url: str) -> Tuple[str, str]:
    """Normalize arXiv URL and extract arXiv ID.
    
    Args:
        url: arXiv URL or arXiv ID
        
    Returns:
        Tuple of (normalized_url, arxiv_id)
        
    Raises:
        ValueError: If not a valid arXiv URL/ID
    """
    logger = get_logger()
    logger.debug(f"Normalizing arXiv URL: {url}")
    
    # Clean input
    url = url.strip()
    
    # Remove common prefixes
    if url.startswith('arxiv:'):
        url = url[6:]
    elif url.startswith('arXiv:'):
        url = url[6:]
    
    # Extract arXiv ID from URL
    if url.startswith(('http://', 'https://')):
        if 'arxiv.org' not in url:
            raise ValueError(f"Not an arXiv URL: {url}")
        
        # Extract ID from URL path
        if '/abs/' in url:
            arxiv_id = url.split('/abs/')[-1]
        elif '/pdf/' in url:
            arxiv_id = url.split('/pdf/')[-1].replace('.pdf', '')
        else:
            raise ValueError(f"Cannot extract arXiv ID from URL: {url}")
    else:
        # Assume it's already an arXiv ID
        arxiv_id = url
    
    # Validate arXiv ID format
    if not validate_arxiv_id(arxiv_id):
        raise ValueError(f"Invalid arXiv ID format: {arxiv_id}")
    
    # Construct normalized URL
    normalized_url = f"https://arxiv.org/abs/{arxiv_id}"
    
    logger.debug(f"Normalized arXiv URL: {normalized_url}, ID: {arxiv_id}")
    return normalized_url, arxiv_id


def normalize_doi(doi: str) -> str:
    """Normalize DOI to standard format.
    
    Args:
        doi: Raw DOI string
        
    Returns:
        Normalized DOI string
        
    Raises:
        ValueError: If DOI format is invalid
    """
    logger = get_logger()
    logger.debug(f"Normalizing DOI: {doi}")
    
    # Clean input
    doi = doi.strip()
    
    # Remove common prefixes
    if doi.startswith('doi:'):
        doi = doi[4:].strip()
    elif doi.startswith('http://dx.doi.org/'):
        doi = doi[18:].strip()
    elif doi.startswith('https://doi.org/'):
        doi = doi[15:].strip()
    elif doi.startswith('https://dx.doi.org/'):
        doi = doi[19:].strip()
    
    # Remove any leading slash
    if doi.startswith('/'):
        doi = doi[1:]
    
    # Validate DOI format
    if not validate_doi(doi):
        raise ValueError(f"Invalid DOI format: {doi}")
    
    logger.debug(f"Normalized DOI: {doi}")
    return doi


def validate_arxiv_id(arxiv_id: str) -> bool:
    """Validate arXiv ID format.
    
    Args:
        arxiv_id: arXiv identifier
        
    Returns:
        True if valid arXiv ID format
    """
    # New format: YYMM.NNNNN[vN]
    new_format = re.match(r'^\d{4}\.\d{4,5}(v\d+)?$', arxiv_id)
    
    # Old format: subject-class/YYMMnnn
    old_format = re.match(r'^[a-z-]+(\.[A-Z]{2})?/\d{7}$', arxiv_id)
    
    return bool(new_format or old_format)


def validate_doi(doi: str) -> bool:
    """Validate DOI format.
    
    Args:
        doi: DOI identifier
        
    Returns:
        True if valid DOI format
    """
    # Basic DOI format: 10.XXXX/YYYY
    doi_pattern = r'^10\.\d{4,}/.+$'
    return bool(re.match(doi_pattern, doi))


def extract_identifiers_from_text(text: str) -> Dict[str, List[str]]:
    """Extract paper identifiers (DOIs, arXiv IDs) from text.
    
    Args:
        text: Text to search for identifiers
        
    Returns:
        Dictionary with 'dois' and 'arxiv_ids' lists
    """
    logger = get_logger()
    logger.debug("Extracting identifiers from text")
    
    identifiers = {
        'dois': [],
        'arxiv_ids': []
    }
    
    # DOI patterns
    doi_patterns = [
        r'10\.\d{4,}/[^\s,;]+',
        r'doi:\s*(10\.\d{4,}/[^\s,;]+)',
        r'DOI:\s*(10\.\d{4,}/[^\s,;]+)',
        r'https?://(?:dx\.)?doi\.org/(10\.\d{4,}/[^\s,;]+)',
        r'https?://doi\.org/(10\.\d{4,}/[^\s,;]+)'
    ]
    
    for pattern in doi_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                # Handle captured groups (URL patterns return tuples)
                if isinstance(match, tuple):
                    match = match[0] if match[0] else match
                
                # Clean up trailing punctuation
                match = re.sub(r'[.,:;]+$', '', match)
                
                normalized_doi = normalize_doi(match)
                if normalized_doi not in identifiers['dois']:
                    identifiers['dois'].append(normalized_doi)
            except ValueError:
                continue
    
    # arXiv patterns
    arxiv_patterns = [
        r'arXiv:\s*\d{4}\.\d{4,5}(?:v\d+)?',
        r'arxiv:\s*\d{4}\.\d{4,5}(?:v\d+)?',
        r'arXiv:\s*[a-z-]+(?:\.[A-Z]{2})?/\d{7}',
        r'arxiv:\s*[a-z-]+(?:\.[A-Z]{2})?/\d{7}',
        r'https?://arxiv\.org/abs/\d{4}\.\d{4,5}(?:v\d+)?',
        r'https?://arxiv\.org/abs/[a-z-]+(?:\.[A-Z]{2})?/\d{7}'
    ]
    
    for pattern in arxiv_patterns:
        matches = re.findall(pattern, text, re.IGNORECASE)
        for match in matches:
            try:
                _, arxiv_id = normalize_arxiv_url(match)
                if arxiv_id not in identifiers['arxiv_ids']:
                    identifiers['arxiv_ids'].append(arxiv_id)
            except ValueError:
                continue
    
    logger.debug(f"Found {len(identifiers['dois'])} DOIs and {len(identifiers['arxiv_ids'])} arXiv IDs")
    return identifiers


def validate_url_accessibility(url: str, timeout: int = 10) -> Tuple[bool, Optional[str]]:
    """Check if URL is accessible.
    
    Args:
        url: URL to check
        timeout: Timeout in seconds
        
    Returns:
        Tuple of (is_accessible, error_message)
    """
    logger = get_logger()
    logger.debug(f"Checking URL accessibility: {url}")
    
    try:
        import requests
        response = requests.head(url, timeout=timeout)
        response.raise_for_status()
        return True, None
    except requests.RequestException as e:
        error_msg = f"URL not accessible: {str(e)}"
        logger.warning(error_msg)
        return False, error_msg
    except Exception as e:
        error_msg = f"Unexpected error checking URL: {str(e)}"
        logger.error(error_msg)
        return False, error_msg 
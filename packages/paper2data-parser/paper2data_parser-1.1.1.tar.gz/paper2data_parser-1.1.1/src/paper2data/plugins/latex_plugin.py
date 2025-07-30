"""
LaTeX Processing Plugin for Paper2Data

This plugin provides enhanced LaTeX equation processing capabilities,
including equation detection, LaTeX conversion, and mathematical
notation handling.

Features:
- Enhanced equation detection in PDF documents
- LaTeX to MathML conversion
- Mathematical symbol recognition
- Equation validation and formatting
- Integration with existing equation processing pipeline

Author: Paper2Data Team
Version: 1.0.0
"""

import re
import logging
from typing import Dict, List, Any, Optional, Union
from dataclasses import dataclass
from pathlib import Path
import json

from ..plugin_manager import BasePlugin, PluginMetadata, plugin_hook, HookPriority
from ..plugin_hooks import HookCategory


logger = logging.getLogger(__name__)


@dataclass
class LaTeXEquation:
    """Represents a LaTeX equation with metadata"""
    content: str
    equation_type: str  # 'inline' or 'display'
    page_number: int
    position: Dict[str, float]
    confidence: float
    symbols: List[str]
    complexity: str  # 'simple', 'medium', 'complex'
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary representation"""
        return {
            "content": self.content,
            "equation_type": self.equation_type,
            "page_number": self.page_number,
            "position": self.position,
            "confidence": self.confidence,
            "symbols": self.symbols,
            "complexity": self.complexity
        }


class LaTeXProcessor:
    """Core LaTeX processing functionality"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger("LaTeXProcessor")
        
        # Common LaTeX patterns
        self.inline_patterns = [
            r'\$([^$\n]+)\$',  # $equation$
            r'\\begin\{math\}(.*?)\\end\{math\}',  # \begin{math}...\end{math}
            r'\\[(.*?)\\]',  # \[equation\]
        ]
        
        self.display_patterns = [
            r'\$\$([^$\n]+)\$\$',  # $$equation$$
            r'\\begin\{equation\}(.*?)\\end\{equation\}',  # equation environment
            r'\\begin\{align\}(.*?)\\end\{align\}',  # align environment
            r'\\begin\{gather\}(.*?)\\end\{gather\}',  # gather environment
            r'\\begin\{multline\}(.*?)\\end\{multline\}',  # multline environment
        ]
        
        # Mathematical symbols for complexity analysis
        self.simple_symbols = {
            '+', '-', '*', '/', '=', '<', '>', '(', ')', '[', ']', '{', '}',
            'x', 'y', 'z', 'a', 'b', 'c', 'n', 'm', 'k', 'i', 'j'
        }
        
        self.complex_symbols = {
            '\\int', '\\sum', '\\prod', '\\lim', '\\frac', '\\sqrt', '\\partial',
            '\\nabla', '\\infty', '\\alpha', '\\beta', '\\gamma', '\\delta',
            '\\epsilon', '\\theta', '\\lambda', '\\mu', '\\pi', '\\sigma',
            '\\phi', '\\psi', '\\omega', '\\rightarrow', '\\leftarrow',
            '\\Rightarrow', '\\Leftarrow', '\\forall', '\\exists', '\\in',
            '\\subset', '\\supset', '\\cup', '\\cap', '\\bigcup', '\\bigcap'
        }
    
    def detect_equations(self, text: str, page_num: int = 0) -> List[LaTeXEquation]:
        """
        Detect LaTeX equations in text
        
        Args:
            text: Text to analyze
            page_num: Page number for context
            
        Returns:
            List[LaTeXEquation]: Detected equations
        """
        equations = []
        
        # Detect inline equations
        for pattern in self.inline_patterns:
            for match in re.finditer(pattern, text, re.DOTALL):
                equation_content = match.group(1).strip()
                if equation_content:
                    equation = self._create_equation(
                        equation_content,
                        'inline',
                        page_num,
                        match.start(),
                        match.end()
                    )
                    equations.append(equation)
        
        # Detect display equations
        for pattern in self.display_patterns:
            for match in re.finditer(pattern, text, re.DOTALL):
                equation_content = match.group(1).strip()
                if equation_content:
                    equation = self._create_equation(
                        equation_content,
                        'display',
                        page_num,
                        match.start(),
                        match.end()
                    )
                    equations.append(equation)
        
        return equations
    
    def _create_equation(self, content: str, eq_type: str, page_num: int, 
                        start_pos: int, end_pos: int) -> LaTeXEquation:
        """Create LaTeXEquation object with analysis"""
        symbols = self._extract_symbols(content)
        complexity = self._analyze_complexity(symbols)
        confidence = self._calculate_confidence(content, symbols)
        
        return LaTeXEquation(
            content=content,
            equation_type=eq_type,
            page_number=page_num,
            position={"start": start_pos, "end": end_pos},
            confidence=confidence,
            symbols=symbols,
            complexity=complexity
        )
    
    def _extract_symbols(self, content: str) -> List[str]:
        """Extract mathematical symbols from equation content"""
        symbols = []
        
        # Find LaTeX commands
        latex_commands = re.findall(r'\\[a-zA-Z]+', content)
        symbols.extend(latex_commands)
        
        # Find single character symbols
        for char in content:
            if char in self.simple_symbols or char in self.complex_symbols:
                if char not in symbols:
                    symbols.append(char)
        
        return symbols
    
    def _analyze_complexity(self, symbols: List[str]) -> str:
        """Analyze equation complexity based on symbols"""
        complex_count = sum(1 for symbol in symbols if symbol in self.complex_symbols)
        
        if complex_count == 0:
            return "simple"
        elif complex_count <= 3:
            return "medium"
        else:
            return "complex"
    
    def _calculate_confidence(self, content: str, symbols: List[str]) -> float:
        """Calculate confidence score for equation detection"""
        confidence = 0.5  # Base confidence
        
        # Boost confidence for LaTeX commands
        latex_commands = [s for s in symbols if s.startswith('\\')]
        confidence += min(len(latex_commands) * 0.1, 0.3)
        
        # Boost confidence for mathematical symbols
        math_symbols = [s for s in symbols if s in self.complex_symbols]
        confidence += min(len(math_symbols) * 0.05, 0.2)
        
        # Penalty for very short content
        if len(content.strip()) < 3:
            confidence -= 0.2
        
        return min(max(confidence, 0.0), 1.0)
    
    def convert_to_mathml(self, equation: LaTeXEquation) -> Optional[str]:
        """
        Convert LaTeX equation to MathML
        
        Args:
            equation: LaTeX equation to convert
            
        Returns:
            Optional[str]: MathML representation or None if conversion fails
        """
        try:
            # This is a simplified conversion - in practice, you'd use
            # a library like latex2mathml or sympy
            latex_content = equation.content
            
            # Basic conversions
            mathml = self._basic_latex_to_mathml(latex_content)
            
            return mathml
            
        except Exception as e:
            self.logger.error(f"Failed to convert LaTeX to MathML: {e}")
            return None
    
    def _basic_latex_to_mathml(self, latex: str) -> str:
        """Basic LaTeX to MathML conversion"""
        # This is a simplified implementation
        # In practice, you'd use a proper LaTeX parser
        
        mathml = f'<math xmlns="http://www.w3.org/1998/Math/MathML">'
        
        # Handle fractions
        latex = re.sub(r'\\frac\{([^}]+)\}\{([^}]+)\}', 
                      r'<mfrac><mi>\1</mi><mi>\2</mi></mfrac>', latex)
        
        # Handle square roots
        latex = re.sub(r'\\sqrt\{([^}]+)\}', 
                      r'<msqrt><mi>\1</mi></msqrt>', latex)
        
        # Handle superscripts
        latex = re.sub(r'\^([^{}]+|\{[^}]+\})', 
                      r'<msup><mi></mi><mi>\1</mi></msup>', latex)
        
        # Handle subscripts
        latex = re.sub(r'_([^{}]+|\{[^}]+\})', 
                      r'<msub><mi></mi><mi>\1</mi></msub>', latex)
        
        # Simple text conversion
        latex = re.sub(r'([a-zA-Z]+)', r'<mi>\1</mi>', latex)
        latex = re.sub(r'([0-9]+)', r'<mn>\1</mn>', latex)
        
        mathml += latex + '</math>'
        
        return mathml
    
    def validate_equation(self, equation: LaTeXEquation) -> bool:
        """
        Validate a LaTeX equation
        
        Args:
            equation: Equation to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        try:
            # Check for balanced braces
            if not self._check_balanced_braces(equation.content):
                return False
            
            # Check for valid LaTeX syntax
            if not self._check_latex_syntax(equation.content):
                return False
            
            # Check minimum confidence threshold
            min_confidence = self.config.get('min_confidence', 0.3)
            if equation.confidence < min_confidence:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Equation validation failed: {e}")
            return False
    
    def _check_balanced_braces(self, content: str) -> bool:
        """Check if braces are balanced in LaTeX content"""
        stack = []
        brace_pairs = {'(': ')', '[': ']', '{': '}'}
        
        for char in content:
            if char in brace_pairs:
                stack.append(char)
            elif char in brace_pairs.values():
                if not stack:
                    return False
                last_open = stack.pop()
                if brace_pairs[last_open] != char:
                    return False
        
        return len(stack) == 0
    
    def _check_latex_syntax(self, content: str) -> bool:
        """Basic LaTeX syntax validation"""
        # Check for common LaTeX command patterns
        if re.search(r'\\[a-zA-Z]+', content):
            # Has LaTeX commands, check for proper structure
            if re.search(r'\\begin\{[^}]+\}', content):
                # Has begin environment, check for matching end
                begin_matches = re.findall(r'\\begin\{([^}]+)\}', content)
                end_matches = re.findall(r'\\end\{([^}]+)\}', content)
                if len(begin_matches) != len(end_matches):
                    return False
                if sorted(begin_matches) != sorted(end_matches):
                    return False
        
        return True


class LaTeXPlugin(BasePlugin):
    """LaTeX processing plugin for Paper2Data"""
    
    def __init__(self, config: Dict[str, Any] = None):
        super().__init__(config)
        self.processor = LaTeXProcessor(self.config)
    
    def get_metadata(self) -> PluginMetadata:
        """Return plugin metadata"""
        return PluginMetadata(
            name="latex_processor",
            version="1.0.0",
            description="Advanced LaTeX equation processing and conversion",
            author="Paper2Data Team",
            license="MIT",
            website="https://github.com/paper2data/plugins",
            dependencies=["re", "logging"],
            paper2data_version=">=1.0.0",
            hooks=["process_equations", "extract_text", "validate_output"],
            config_schema={
                "type": "object",
                "properties": {
                    "min_confidence": {
                        "type": "number",
                        "minimum": 0.0,
                        "maximum": 1.0,
                        "default": 0.3,
                        "description": "Minimum confidence threshold for equation detection"
                    },
                    "output_format": {
                        "type": "string",
                        "enum": ["latex", "mathml", "both"],
                        "default": "both",
                        "description": "Output format for processed equations"
                    },
                    "include_complexity": {
                        "type": "boolean",
                        "default": True,
                        "description": "Include complexity analysis in output"
                    },
                    "max_equations": {
                        "type": "integer",
                        "minimum": 1,
                        "default": 1000,
                        "description": "Maximum number of equations to process"
                    }
                }
            },
            tags=["latex", "equations", "mathematics", "conversion"],
            experimental=False
        )
    
    def setup(self) -> bool:
        """Set up the plugin"""
        try:
            self.logger.info("Setting up LaTeX Plugin")
            
            # Validate configuration
            if not self.validate_config(self.config):
                self.logger.error("Invalid configuration for LaTeX Plugin")
                return False
            
            # Initialize processor with config
            self.processor = LaTeXProcessor(self.config)
            
            self.logger.info("LaTeX Plugin setup completed successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"LaTeX Plugin setup failed: {e}")
            return False
    
    def cleanup(self) -> bool:
        """Clean up plugin resources"""
        try:
            self.logger.info("Cleaning up LaTeX Plugin")
            # No specific cleanup needed for this plugin
            return True
            
        except Exception as e:
            self.logger.error(f"LaTeX Plugin cleanup failed: {e}")
            return False
    
    def validate_config(self, config: Dict[str, Any]) -> bool:
        """Validate plugin configuration"""
        try:
            # Check required configuration values
            min_confidence = config.get('min_confidence', 0.3)
            if not isinstance(min_confidence, (int, float)) or not (0.0 <= min_confidence <= 1.0):
                return False
            
            output_format = config.get('output_format', 'both')
            if output_format not in ['latex', 'mathml', 'both']:
                return False
            
            max_equations = config.get('max_equations', 1000)
            if not isinstance(max_equations, int) or max_equations < 1:
                return False
            
            return True
            
        except Exception as e:
            self.logger.error(f"Configuration validation failed: {e}")
            return False
    
    @plugin_hook("process_equations", HookPriority.HIGH, 
                "Enhanced LaTeX equation processing with validation and conversion")
    def process_equations_hook(self, equations: List[Dict[str, Any]], 
                              config: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Process equations with LaTeX capabilities
        
        Args:
            equations: List of equation data
            config: Processing configuration
            
        Returns:
            List[Dict[str, Any]]: Processed equations with LaTeX enhancements
        """
        if not self.is_enabled():
            return equations
        
        try:
            self.logger.info(f"Processing {len(equations)} equations with LaTeX plugin")
            
            processed_equations = []
            max_equations = min(len(equations), self.config.get('max_equations', 1000))
            
            for i, eq_data in enumerate(equations[:max_equations]):
                try:
                    # Convert to LaTeXEquation object
                    latex_eq = LaTeXEquation(
                        content=eq_data.get('content', ''),
                        equation_type=eq_data.get('type', 'inline'),
                        page_number=eq_data.get('page_number', 0),
                        position=eq_data.get('position', {}),
                        confidence=eq_data.get('confidence', 0.5),
                        symbols=eq_data.get('symbols', []),
                        complexity=eq_data.get('complexity', 'simple')
                    )
                    
                    # Validate equation
                    if not self.processor.validate_equation(latex_eq):
                        self.logger.warning(f"Equation {i} failed validation, skipping")
                        continue
                    
                    # Convert to MathML if requested
                    mathml = None
                    output_format = self.config.get('output_format', 'both')
                    if output_format in ['mathml', 'both']:
                        mathml = self.processor.convert_to_mathml(latex_eq)
                    
                    # Create enhanced equation data
                    enhanced_eq = eq_data.copy()
                    enhanced_eq.update({
                        'latex_content': latex_eq.content,
                        'symbols': latex_eq.symbols,
                        'complexity': latex_eq.complexity,
                        'confidence': latex_eq.confidence,
                        'validated': True
                    })
                    
                    if mathml:
                        enhanced_eq['mathml'] = mathml
                    
                    processed_equations.append(enhanced_eq)
                    
                except Exception as e:
                    self.logger.error(f"Failed to process equation {i}: {e}")
                    # Include original equation data
                    processed_equations.append(eq_data)
            
            self.logger.info(f"Successfully processed {len(processed_equations)} equations")
            return processed_equations
            
        except Exception as e:
            self.logger.error(f"LaTeX equation processing failed: {e}")
            return equations
    
    @plugin_hook("extract_text", HookPriority.LOW, 
                "Extract LaTeX equations from text content")
    def extract_text_hook(self, file_path: str, page_num: int, 
                         config: Dict[str, Any]) -> Optional[str]:
        """
        Extract text with LaTeX equation detection
        
        Args:
            file_path: Path to the PDF file
            page_num: Page number to extract
            config: Extraction configuration
            
        Returns:
            Optional[str]: Extracted text with LaTeX annotations
        """
        if not self.is_enabled():
            return None
        
        # This hook is called when default text extraction fails
        # For LaTeX plugin, we don't provide alternative text extraction
        # but we could enhance text with equation markup
        return None
    
    @plugin_hook("validate_output", HookPriority.NORMAL, 
                "Validate LaTeX equations in output")
    def validate_output_hook(self, output_path: str, data: Dict[str, Any], 
                           config: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Validate LaTeX equations in output
        
        Args:
            output_path: Path to output directory
            data: Processing results
            config: Validation configuration
            
        Returns:
            Optional[Dict[str, Any]]: Validation results
        """
        if not self.is_enabled():
            return None
        
        try:
            validation_results = {
                'plugin': 'latex_processor',
                'validated_equations': 0,
                'failed_equations': 0,
                'validation_errors': []
            }
            
            # Check if equations exist in data
            equations = data.get('equations', [])
            if not equations:
                return validation_results
            
            self.logger.info(f"Validating {len(equations)} equations")
            
            for i, eq_data in enumerate(equations):
                try:
                    # Create LaTeXEquation object
                    latex_eq = LaTeXEquation(
                        content=eq_data.get('content', ''),
                        equation_type=eq_data.get('type', 'inline'),
                        page_number=eq_data.get('page_number', 0),
                        position=eq_data.get('position', {}),
                        confidence=eq_data.get('confidence', 0.5),
                        symbols=eq_data.get('symbols', []),
                        complexity=eq_data.get('complexity', 'simple')
                    )
                    
                    # Validate equation
                    if self.processor.validate_equation(latex_eq):
                        validation_results['validated_equations'] += 1
                    else:
                        validation_results['failed_equations'] += 1
                        validation_results['validation_errors'].append({
                            'equation_index': i,
                            'content': eq_data.get('content', ''),
                            'error': 'Failed LaTeX validation'
                        })
                        
                except Exception as e:
                    validation_results['failed_equations'] += 1
                    validation_results['validation_errors'].append({
                        'equation_index': i,
                        'content': eq_data.get('content', ''),
                        'error': str(e)
                    })
            
            self.logger.info(f"LaTeX validation complete: {validation_results['validated_equations']} "
                           f"valid, {validation_results['failed_equations']} failed")
            
            return validation_results
            
        except Exception as e:
            self.logger.error(f"LaTeX output validation failed: {e}")
            return {
                'plugin': 'latex_processor',
                'error': str(e),
                'validated_equations': 0,
                'failed_equations': 0
            }


# Plugin instance for loading
plugin_instance = LaTeXPlugin 
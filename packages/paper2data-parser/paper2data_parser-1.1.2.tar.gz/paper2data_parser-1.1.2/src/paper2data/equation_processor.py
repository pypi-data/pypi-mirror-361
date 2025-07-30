"""
Mathematical Equation Detection and LaTeX Conversion System
Version 1.1 Feature - Advanced Academic Processing

This module provides comprehensive mathematical equation detection,
LaTeX conversion, and MathML generation capabilities for academic papers.
"""

import re
import logging
import json
from typing import List, Dict, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from pathlib import Path
import base64

try:
    import fitz  # PyMuPDF
    FITZ_AVAILABLE = True
except ImportError:
    FITZ_AVAILABLE = False

try:
    import sympy
    from sympy import latex, sympify
    from sympy.parsing.latex import parse_latex
    SYMPY_AVAILABLE = True
except ImportError:
    SYMPY_AVAILABLE = False

try:
    import cv2
    import numpy as np
    OPENCV_AVAILABLE = True
except ImportError:
    OPENCV_AVAILABLE = False

logger = logging.getLogger(__name__)


@dataclass
class EquationRegion:
    """Represents a detected mathematical equation region."""
    equation_id: str
    page_number: int
    bbox: Tuple[float, float, float, float]  # x0, y0, x1, y1
    text_content: str
    confidence: float
    equation_type: str  # 'inline', 'display', 'numbered'
    latex_code: Optional[str] = None
    mathml_code: Optional[str] = None
    symbols: List[str] = None
    complexity_score: float = 0.0
    
    def __post_init__(self):
        if self.symbols is None:
            self.symbols = []


@dataclass
class EquationExtractionResult:
    """Complete equation extraction results for a document."""
    total_equations: int
    inline_equations: int
    display_equations: int
    numbered_equations: int
    equations: List[EquationRegion]
    average_confidence: float
    processing_time: float
    latex_symbols_used: List[str]
    mathml_available: bool


class MathematicalPatternDetector:
    """Advanced mathematical pattern detection and classification."""
    
    def __init__(self):
        self.inline_patterns = [
            r'\$[^$]+\$',  # Single dollar signs
            r'\\begin\{math\}.*?\\end\{math\}',  # Math environment
            r'\\(.*?\\)',  # Parentheses delimiters
            r'[a-zA-Z]_\{[^}]+\}',  # Subscripts
            r'[a-zA-Z]\^\{[^}]+\}',  # Superscripts
            r'\\[a-zA-Z]+\{[^}]*\}',  # LaTeX commands
            r'[a-zA-Z]+\s*[=≠<>≤≥≈∝∞∫∑∏]\s*[a-zA-Z0-9]+',  # Mathematical relations
            r'[α-ωΑ-Ω]',  # Greek letters
            r'[∂∇∆∫∑∏√∞±×÷≤≥≠≈∝∈∉⊂⊃∪∩∧∨¬∀∃]',  # Mathematical symbols
        ]
        
        self.display_patterns = [
            r'\$\$.*?\$\$',  # Double dollar signs
            r'\\begin\{equation\}.*?\\end\{equation\}',  # Equation environment
            r'\\begin\{align\}.*?\\end\{align\}',  # Align environment
            r'\\begin\{eqnarray\}.*?\\end\{eqnarray\}',  # Eqnarray environment
            r'\\begin\{displaymath\}.*?\\end\{displaymath\}',  # Display math
            r'\\begin\{gather\}.*?\\end\{gather\}',  # Gather environment
            r'\\begin\{multline\}.*?\\end\{multline\}',  # Multline environment
        ]
        
        self.numbered_patterns = [
            r'\\begin\{equation\}.*?\\end\{equation\}',
            r'\\begin\{align\}.*?\\end\{align\}',
            r'\\begin\{eqnarray\}.*?\\end\{eqnarray\}',
            r'\([0-9]+\)\s*$',  # Equation numbers
            r'\([0-9]+\.[0-9]+\)\s*$',  # Numbered equations
        ]
        
        self.latex_symbols = [
            'alpha', 'beta', 'gamma', 'delta', 'epsilon', 'zeta', 'eta', 'theta',
            'iota', 'kappa', 'lambda', 'mu', 'nu', 'xi', 'omicron', 'pi',
            'rho', 'sigma', 'tau', 'upsilon', 'phi', 'chi', 'psi', 'omega',
            'Gamma', 'Delta', 'Theta', 'Lambda', 'Xi', 'Pi', 'Sigma', 'Upsilon',
            'Phi', 'Psi', 'Omega', 'sum', 'prod', 'int', 'oint', 'partial',
            'nabla', 'infty', 'pm', 'mp', 'times', 'div', 'cdot', 'ast',
            'star', 'circ', 'bullet', 'cap', 'cup', 'uplus', 'sqcap', 'sqcup',
            'vee', 'wedge', 'setminus', 'wr', 'diamond', 'bigtriangleup',
            'bigtriangledown', 'triangleleft', 'triangleright', 'lhd', 'rhd',
            'unlhd', 'unrhd', 'oplus', 'ominus', 'otimes', 'oslash', 'odot',
            'bigcirc', 'dagger', 'ddagger', 'amalg', 'leq', 'geq', 'equiv',
            'models', 'prec', 'succ', 'sim', 'perp', 'preceq', 'succeq',
            'simeq', 'll', 'gg', 'asymp', 'parallel', 'subset', 'supset',
            'approx', 'bowtie', 'subseteq', 'supseteq', 'cong', 'neq',
            'smile', 'sqsubseteq', 'sqsupseteq', 'doteq', 'frown', 'in',
            'ni', 'propto', 'vdash', 'dashv', 'sqrt', 'frac', 'sum', 'int'
        ]
        
        # Compile patterns for performance
        self.compiled_inline = [re.compile(pattern, re.DOTALL) for pattern in self.inline_patterns]
        self.compiled_display = [re.compile(pattern, re.DOTALL) for pattern in self.display_patterns]
        self.compiled_numbered = [re.compile(pattern, re.DOTALL) for pattern in self.numbered_patterns]


class LaTeXConverter:
    """Advanced LaTeX conversion and validation system."""
    
    def __init__(self):
        self.symbol_mapping = {
            '≤': r'\leq',
            '≥': r'\geq',
            '≠': r'\neq',
            '≈': r'\approx',
            '∝': r'\propto',
            '∞': r'\infty',
            '∫': r'\int',
            '∑': r'\sum',
            '∏': r'\prod',
            '√': r'\sqrt',
            '±': r'\pm',
            '×': r'\times',
            '÷': r'\div',
            '∂': r'\partial',
            '∇': r'\nabla',
            '∆': r'\Delta',
            '∈': r'\in',
            '∉': r'\notin',
            '⊂': r'\subset',
            '⊃': r'\supset',
            '∪': r'\cup',
            '∩': r'\cap',
            '∧': r'\wedge',
            '∨': r'\vee',
            '¬': r'\neg',
            '∀': r'\forall',
            '∃': r'\exists',
            # Greek letters
            'α': r'\alpha', 'β': r'\beta', 'γ': r'\gamma', 'δ': r'\delta',
            'ε': r'\epsilon', 'ζ': r'\zeta', 'η': r'\eta', 'θ': r'\theta',
            'ι': r'\iota', 'κ': r'\kappa', 'λ': r'\lambda', 'μ': r'\mu',
            'ν': r'\nu', 'ξ': r'\xi', 'ο': r'\omicron', 'π': r'\pi',
            'ρ': r'\rho', 'σ': r'\sigma', 'τ': r'\tau', 'υ': r'\upsilon',
            'φ': r'\phi', 'χ': r'\chi', 'ψ': r'\psi', 'ω': r'\omega',
            'Α': r'\Alpha', 'Β': r'\Beta', 'Γ': r'\Gamma', 'Δ': r'\Delta',
            'Ε': r'\Epsilon', 'Ζ': r'\Zeta', 'Η': r'\Eta', 'Θ': r'\Theta',
            'Ι': r'\Iota', 'Κ': r'\Kappa', 'Λ': r'\Lambda', 'Μ': r'\Mu',
            'Ν': r'\Nu', 'Ξ': r'\Xi', 'Ο': r'\Omicron', 'Π': r'\Pi',
            'Ρ': r'\Rho', 'Σ': r'\Sigma', 'Τ': r'\Tau', 'Υ': r'\Upsilon',
            'Φ': r'\Phi', 'Χ': r'\Chi', 'Ψ': r'\Psi', 'Ω': r'\Omega',
        }
        
        self.environment_patterns = {
            'fraction': r'(\d+|\w+)/(\d+|\w+)',
            'power': r'(\w+)\^(\{[^}]+\}|\w+)',
            'subscript': r'(\w+)_(\{[^}]+\}|\w+)',
            'integral': r'∫([^∫]+)d(\w+)',
            'summation': r'∑([^∑]+)',
            'product': r'∏([^∏]+)',
            'square_root': r'√([^√]+)',
            'absolute': r'\|([^|]+)\|',
            'parentheses': r'\(([^)]+)\)',
            'brackets': r'\[([^\]]+)\]',
            'braces': r'\{([^}]+)\}',
        }
    
    def convert_to_latex(self, text: str) -> str:
        """Convert mathematical text to LaTeX format."""
        latex_text = text
        
        # Replace Unicode mathematical symbols
        for symbol, latex_symbol in self.symbol_mapping.items():
            latex_text = latex_text.replace(symbol, latex_symbol)
        
        # Convert common mathematical expressions
        for pattern_name, pattern in self.environment_patterns.items():
            latex_text = self._apply_pattern_conversion(latex_text, pattern, pattern_name)
        
        # Clean up and validate
        latex_text = self._clean_latex(latex_text)
        
        return latex_text
    
    def _apply_pattern_conversion(self, text: str, pattern: str, pattern_type: str) -> str:
        """Apply specific pattern conversions based on type."""
        if pattern_type == 'fraction':
            text = re.sub(pattern, r'\\frac{\1}{\2}', text)
        elif pattern_type == 'power':
            text = re.sub(pattern, r'\1^{\2}', text)
        elif pattern_type == 'subscript':
            text = re.sub(pattern, r'\1_{\2}', text)
        elif pattern_type == 'integral':
            text = re.sub(pattern, r'\\int \1 d\2', text)
        elif pattern_type == 'summation':
            text = re.sub(pattern, r'\\sum \1', text)
        elif pattern_type == 'product':
            text = re.sub(pattern, r'\\prod \1', text)
        elif pattern_type == 'square_root':
            text = re.sub(pattern, r'\\sqrt{\1}', text)
        
        return text
    
    def _clean_latex(self, latex_text: str) -> str:
        """Clean and validate LaTeX code."""
        # Remove extra spaces
        latex_text = re.sub(r'\s+', ' ', latex_text)
        
        # Fix common LaTeX issues
        latex_text = latex_text.replace('{ }', '{}')
        latex_text = latex_text.replace('\\\\', '\\')
        
        # Ensure proper bracing
        latex_text = self._fix_bracing(latex_text)
        
        return latex_text.strip()
    
    def _fix_bracing(self, latex_text: str) -> str:
        """Fix LaTeX bracing issues."""
        # This is a simplified implementation
        # In a full implementation, we'd use a proper LaTeX parser
        open_braces = latex_text.count('{')
        close_braces = latex_text.count('}')
        
        if open_braces > close_braces:
            latex_text += '}' * (open_braces - close_braces)
        elif close_braces > open_braces:
            latex_text = '{' * (close_braces - open_braces) + latex_text
        
        return latex_text
    
    def validate_latex(self, latex_code: str) -> Tuple[bool, str]:
        """Validate LaTeX code syntax."""
        try:
            if SYMPY_AVAILABLE:
                # Try to parse with SymPy
                parsed = parse_latex(latex_code)
                return True, "Valid LaTeX syntax"
            else:
                # Basic validation without SymPy
                if self._basic_latex_validation(latex_code):
                    return True, "Valid LaTeX syntax (basic validation)"
                else:
                    return False, "Invalid LaTeX syntax"
        except Exception as e:
            return False, f"LaTeX validation error: {str(e)}"
    
    def _basic_latex_validation(self, latex_code: str) -> bool:
        """Basic LaTeX validation without external libraries."""
        # Check for balanced braces
        if latex_code.count('{') != latex_code.count('}'):
            return False
        
        # Check for balanced parentheses
        if latex_code.count('(') != latex_code.count(')'):
            return False
        
        # Check for balanced brackets
        if latex_code.count('[') != latex_code.count(']'):
            return False
        
        # Check for basic LaTeX command structure
        if '\\' in latex_code and not re.search(r'\\[a-zA-Z]+', latex_code):
            return False
        
        return True


class MathMLGenerator:
    """Generate MathML from LaTeX equations."""
    
    def __init__(self):
        self.latex_to_mathml_map = {
            r'\\frac\{([^}]+)\}\{([^}]+)\}': r'<mfrac><mi>\1</mi><mi>\2</mi></mfrac>',
            r'\\sqrt\{([^}]+)\}': r'<msqrt><mi>\1</mi></msqrt>',
            r'\\sum': r'<mo>∑</mo>',
            r'\\int': r'<mo>∫</mo>',
            r'\\prod': r'<mo>∏</mo>',
            r'\\infty': r'<mi>∞</mi>',
            r'\\alpha': r'<mi>α</mi>',
            r'\\beta': r'<mi>β</mi>',
            r'\\gamma': r'<mi>γ</mi>',
            r'\\delta': r'<mi>δ</mi>',
            r'\\epsilon': r'<mi>ε</mi>',
            r'\\theta': r'<mi>θ</mi>',
            r'\\lambda': r'<mi>λ</mi>',
            r'\\mu': r'<mi>μ</mi>',
            r'\\pi': r'<mi>π</mi>',
            r'\\sigma': r'<mi>σ</mi>',
            r'\\phi': r'<mi>φ</mi>',
            r'\\omega': r'<mi>ω</mi>',
        }
    
    def convert_to_mathml(self, latex_code: str) -> str:
        """Convert LaTeX to MathML."""
        mathml = latex_code
        
        # Apply conversions
        for latex_pattern, mathml_replacement in self.latex_to_mathml_map.items():
            mathml = re.sub(latex_pattern, mathml_replacement, mathml)
        
        # Wrap in MathML structure
        mathml = f'<math xmlns="http://www.w3.org/1998/Math/MathML">{mathml}</math>'
        
        return mathml


class EquationProcessor:
    """Main equation processing engine for Paper2Data Version 1.1."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        self.config = config or {}
        self.pattern_detector = MathematicalPatternDetector()
        self.latex_converter = LaTeXConverter()
        self.mathml_generator = MathMLGenerator()
        
        # Configuration parameters
        self.min_confidence_threshold = self.config.get('min_confidence_threshold', 0.7)
        self.extract_inline_equations = self.config.get('extract_inline_equations', True)
        self.extract_display_equations = self.config.get('extract_display_equations', True)
        self.extract_numbered_equations = self.config.get('extract_numbered_equations', True)
        self.generate_latex = self.config.get('generate_latex', True)
        self.generate_mathml = self.config.get('generate_mathml', True)
        
        logger.info("Equation processor initialized with advanced mathematical processing")
    
    def process_document(self, doc_path: str) -> EquationExtractionResult:
        """Process a PDF document for mathematical equations."""
        import time
        start_time = time.time()
        
        logger.info(f"Starting equation processing for: {doc_path}")
        
        if not FITZ_AVAILABLE:
            logger.error("PyMuPDF not available for equation processing")
            return EquationExtractionResult(
                total_equations=0,
                inline_equations=0,
                display_equations=0,
                numbered_equations=0,
                equations=[],
                average_confidence=0.0,
                processing_time=0.0,
                latex_symbols_used=[],
                mathml_available=False
            )
        
        try:
            doc = fitz.open(doc_path)
            all_equations = []
            
            for page_num in range(len(doc)):
                page = doc[page_num]
                page_equations = self._process_page(page, page_num)
                all_equations.extend(page_equations)
            
            doc.close()
            
            # Calculate statistics
            inline_count = sum(1 for eq in all_equations if eq.equation_type == 'inline')
            display_count = sum(1 for eq in all_equations if eq.equation_type == 'display')
            numbered_count = sum(1 for eq in all_equations if eq.equation_type == 'numbered')
            
            avg_confidence = sum(eq.confidence for eq in all_equations) / len(all_equations) if all_equations else 0.0
            
            # Extract unique LaTeX symbols
            latex_symbols = set()
            for eq in all_equations:
                if eq.symbols:
                    latex_symbols.update(eq.symbols)
            
            processing_time = time.time() - start_time
            
            result = EquationExtractionResult(
                total_equations=len(all_equations),
                inline_equations=inline_count,
                display_equations=display_count,
                numbered_equations=numbered_count,
                equations=all_equations,
                average_confidence=avg_confidence,
                processing_time=processing_time,
                latex_symbols_used=list(latex_symbols),
                mathml_available=self.generate_mathml
            )
            
            logger.info(f"Equation processing completed: {len(all_equations)} equations found in {processing_time:.2f}s")
            return result
            
        except Exception as e:
            logger.error(f"Error processing document for equations: {str(e)}")
            return EquationExtractionResult(
                total_equations=0,
                inline_equations=0,
                display_equations=0,
                numbered_equations=0,
                equations=[],
                average_confidence=0.0,
                processing_time=time.time() - start_time,
                latex_symbols_used=[],
                mathml_available=False
            )
    
    def _process_page(self, page, page_num: int) -> List[EquationRegion]:
        """Process a single page for mathematical equations."""
        page_equations = []
        
        # Extract text and analyze for equations
        text = page.get_text()
        
        # Detect inline equations
        if self.extract_inline_equations:
            inline_equations = self._detect_inline_equations(text, page_num)
            page_equations.extend(inline_equations)
        
        # Detect display equations
        if self.extract_display_equations:
            display_equations = self._detect_display_equations(text, page_num)
            page_equations.extend(display_equations)
        
        # Detect numbered equations
        if self.extract_numbered_equations:
            numbered_equations = self._detect_numbered_equations(text, page_num)
            page_equations.extend(numbered_equations)
        
        # Process each equation
        for equation in page_equations:
            self._enhance_equation(equation)
        
        return page_equations
    
    def _detect_inline_equations(self, text: str, page_num: int) -> List[EquationRegion]:
        """Detect inline mathematical equations."""
        equations = []
        
        for pattern in self.pattern_detector.compiled_inline:
            matches = pattern.finditer(text)
            for match in matches:
                equation_text = match.group(0)
                confidence = self._calculate_confidence(equation_text, 'inline')
                
                if confidence >= self.min_confidence_threshold:
                    equation = EquationRegion(
                        equation_id=f"inline_{page_num}_{len(equations)}",
                        page_number=page_num,
                        bbox=(0, 0, 0, 0),  # Would need OCR/layout analysis for precise location
                        text_content=equation_text,
                        confidence=confidence,
                        equation_type='inline'
                    )
                    equations.append(equation)
        
        return equations
    
    def _detect_display_equations(self, text: str, page_num: int) -> List[EquationRegion]:
        """Detect display mathematical equations."""
        equations = []
        
        for pattern in self.pattern_detector.compiled_display:
            matches = pattern.finditer(text)
            for match in matches:
                equation_text = match.group(0)
                confidence = self._calculate_confidence(equation_text, 'display')
                
                if confidence >= self.min_confidence_threshold:
                    equation = EquationRegion(
                        equation_id=f"display_{page_num}_{len(equations)}",
                        page_number=page_num,
                        bbox=(0, 0, 0, 0),
                        text_content=equation_text,
                        confidence=confidence,
                        equation_type='display'
                    )
                    equations.append(equation)
        
        return equations
    
    def _detect_numbered_equations(self, text: str, page_num: int) -> List[EquationRegion]:
        """Detect numbered mathematical equations."""
        equations = []
        
        for pattern in self.pattern_detector.compiled_numbered:
            matches = pattern.finditer(text)
            for match in matches:
                equation_text = match.group(0)
                confidence = self._calculate_confidence(equation_text, 'numbered')
                
                if confidence >= self.min_confidence_threshold:
                    equation = EquationRegion(
                        equation_id=f"numbered_{page_num}_{len(equations)}",
                        page_number=page_num,
                        bbox=(0, 0, 0, 0),
                        text_content=equation_text,
                        confidence=confidence,
                        equation_type='numbered'
                    )
                    equations.append(equation)
        
        return equations
    
    def _calculate_confidence(self, text: str, equation_type: str) -> float:
        """Calculate confidence score for equation detection."""
        confidence = 0.0
        
        # Base confidence by type
        type_confidence = {
            'inline': 0.6,
            'display': 0.8,
            'numbered': 0.9
        }
        confidence += type_confidence.get(equation_type, 0.5)
        
        # Bonus for mathematical symbols
        math_symbols = sum(1 for symbol in self.pattern_detector.latex_symbols 
                          if symbol in text.lower())
        confidence += min(math_symbols * 0.1, 0.3)
        
        # Bonus for LaTeX commands
        latex_commands = len(re.findall(r'\\[a-zA-Z]+', text))
        confidence += min(latex_commands * 0.05, 0.2)
        
        # Bonus for mathematical operators
        operators = len(re.findall(r'[=≠<>≤≥≈∝∞∫∑∏±×÷]', text))
        confidence += min(operators * 0.1, 0.2)
        
        return min(confidence, 1.0)
    
    def _enhance_equation(self, equation: EquationRegion):
        """Enhance equation with LaTeX and MathML conversion."""
        # Generate LaTeX
        if self.generate_latex:
            try:
                latex_code = self.latex_converter.convert_to_latex(equation.text_content)
                is_valid, validation_message = self.latex_converter.validate_latex(latex_code)
                
                if is_valid:
                    equation.latex_code = latex_code
                else:
                    logger.warning(f"Invalid LaTeX generated for equation {equation.equation_id}: {validation_message}")
                    equation.latex_code = equation.text_content  # Fallback to original
                
            except Exception as e:
                logger.error(f"Error generating LaTeX for equation {equation.equation_id}: {str(e)}")
                equation.latex_code = equation.text_content
        
        # Generate MathML
        if self.generate_mathml and equation.latex_code:
            try:
                mathml_code = self.mathml_generator.convert_to_mathml(equation.latex_code)
                equation.mathml_code = mathml_code
            except Exception as e:
                logger.error(f"Error generating MathML for equation {equation.equation_id}: {str(e)}")
        
        # Extract symbols
        equation.symbols = self._extract_symbols(equation.text_content)
        
        # Calculate complexity score
        equation.complexity_score = self._calculate_complexity(equation.text_content)
    
    def _extract_symbols(self, text: str) -> List[str]:
        """Extract mathematical symbols from equation text."""
        symbols = set()
        
        for symbol in self.pattern_detector.latex_symbols:
            if symbol in text.lower():
                symbols.add(symbol)
        
        # Add Unicode mathematical symbols
        for symbol in self.latex_converter.symbol_mapping.keys():
            if symbol in text:
                symbols.add(symbol)
        
        return list(symbols)
    
    def _calculate_complexity(self, text: str) -> float:
        """Calculate equation complexity score."""
        complexity = 0.0
        
        # Base complexity by length
        complexity += len(text) * 0.01
        
        # Bonus for nested structures
        nested_structures = text.count('{') + text.count('(') + text.count('[')
        complexity += nested_structures * 0.1
        
        # Bonus for integrals, sums, products
        advanced_operators = len(re.findall(r'[∫∑∏]', text))
        complexity += advanced_operators * 0.3
        
        # Bonus for fractions
        fractions = len(re.findall(r'\\frac|/', text))
        complexity += fractions * 0.2
        
        # Bonus for powers and subscripts
        powers = len(re.findall(r'[\^_]', text))
        complexity += powers * 0.1
        
        return min(complexity, 10.0)  # Cap at 10.0
    
    def export_equations(self, result: EquationExtractionResult, output_path: str, format: str = 'json'):
        """Export equation extraction results to file."""
        output_path = Path(output_path)
        
        if format == 'json':
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(asdict(result), f, indent=2, ensure_ascii=False)
        
        elif format == 'latex':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write("% Mathematical Equations Extracted by Paper2Data\n")
                f.write("% Version 1.1 - Advanced Academic Processing\n\n")
                
                for equation in result.equations:
                    f.write(f"% Equation {equation.equation_id} (Page {equation.page_number})\n")
                    f.write(f"% Type: {equation.equation_type}, Confidence: {equation.confidence:.2f}\n")
                    if equation.latex_code:
                        f.write(f"{equation.latex_code}\n\n")
                    else:
                        f.write(f"% Original text: {equation.text_content}\n\n")
        
        elif format == 'mathml':
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write('<?xml version="1.0" encoding="UTF-8"?>\n')
                f.write('<equations>\n')
                
                for equation in result.equations:
                    f.write(f'  <equation id="{equation.equation_id}" page="{equation.page_number}" type="{equation.equation_type}">\n')
                    if equation.mathml_code:
                        f.write(f'    {equation.mathml_code}\n')
                    f.write('  </equation>\n')
                
                f.write('</equations>\n')
        
        logger.info(f"Equations exported to {output_path} in {format} format")


def create_equation_processor(config: Optional[Dict[str, Any]] = None) -> EquationProcessor:
    """Factory function to create an equation processor instance."""
    return EquationProcessor(config)


def process_equations_from_pdf(pdf_content: bytes) -> Dict[str, Any]:
    """Helper function to process equations from PDF content for integration with main extractor."""
    import tempfile
    import os
    
    logger.info("Starting equation processing from PDF content")
    
    try:
        # Create temporary file for processing
        with tempfile.NamedTemporaryFile(suffix='.pdf', delete=False) as tmp_file:
            tmp_file.write(pdf_content)
            temp_file_path = tmp_file.name
        
        # Create equation processor
        processor = EquationProcessor({
            'min_confidence_threshold': 0.6,
            'extract_inline_equations': True,
            'extract_display_equations': True,
            'extract_numbered_equations': True,
            'generate_latex': True,
            'generate_mathml': True
        })
        
        # Process the document
        result = processor.process_document(temp_file_path)
        
        # Clean up temporary file
        os.unlink(temp_file_path)
        
        # Convert result to dictionary format for integration
        equations_dict = {
            "total_equations": result.total_equations,
            "inline_equations": result.inline_equations,
            "display_equations": result.display_equations,
            "numbered_equations": result.numbered_equations,
            "equations": [
                {
                    "equation_id": eq.equation_id,
                    "page_number": eq.page_number,
                    "equation_type": eq.equation_type,
                    "text_content": eq.text_content,
                    "confidence": eq.confidence,
                    "latex_code": eq.latex_code,
                    "mathml_code": eq.mathml_code,
                    "symbols": eq.symbols,
                    "complexity_score": eq.complexity_score
                }
                for eq in result.equations
            ],
            "average_confidence": result.average_confidence,
            "processing_time": result.processing_time,
            "latex_symbols_used": result.latex_symbols_used,
            "mathml_available": result.mathml_available,
            "processing_status": "successful"
        }
        
        logger.info(f"Equation processing completed: {result.total_equations} equations found")
        return equations_dict
        
    except Exception as e:
        logger.error(f"Error processing equations from PDF: {str(e)}")
        return {
            "total_equations": 0,
            "inline_equations": 0,
            "display_equations": 0,
            "numbered_equations": 0,
            "equations": [],
            "average_confidence": 0.0,
            "processing_time": 0.0,
            "latex_symbols_used": [],
            "mathml_available": False,
            "processing_status": "failed",
            "error": str(e)
        }


# Version 1.1 Feature Integration
def integrate_with_extractor():
    """Integration point for the main extractor module."""
    logger.info("Mathematical equation processing integrated with Paper2Data Version 1.1")
    return True


if __name__ == "__main__":
    # Example usage
    processor = create_equation_processor({
        'min_confidence_threshold': 0.7,
        'extract_inline_equations': True,
        'extract_display_equations': True,
        'extract_numbered_equations': True,
        'generate_latex': True,
        'generate_mathml': True
    })
    
    # This would be called from the main extractor
    print("Paper2Data Version 1.1 - Mathematical Equation Processing System")
    print("Advanced equation detection and LaTeX conversion capabilities")
    print("Ready for integration with academic paper processing pipeline") 
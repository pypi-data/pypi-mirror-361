"""
Comprehensive tests for equation processing functionality.

Tests the mathematical equation detection and LaTeX/MathML conversion
capabilities implemented in Stage 5.
"""

import pytest
import tempfile
from pathlib import Path
from unittest.mock import patch, Mock

from paper2data.equation_processor import (
    EquationProcessor,
    EquationDetector,
    MathematicalEquation,
    EquationType,
    EquationComplexity,
    get_equation_processor,
    process_equations_from_pdf,
    export_equations_to_latex,
    export_equations_to_mathml
)


class TestEquationDetector:
    """Test equation detection functionality."""
    
    def test_equation_detector_creation(self):
        """Test EquationDetector instantiation."""
        detector = EquationDetector()
        assert detector is not None
        assert detector.equation_patterns is not None
        assert detector.latex_symbols is not None
        assert detector.greek_letters is not None
        assert detector.mathematical_operators is not None
    
    def test_latex_symbols_loading(self):
        """Test LaTeX symbols mapping."""
        detector = EquationDetector()
        latex_symbols = detector.latex_symbols
        
        # Test Greek letters
        assert latex_symbols['α'] == r'\alpha'
        assert latex_symbols['β'] == r'\beta'
        assert latex_symbols['π'] == r'\pi'
        assert latex_symbols['Ω'] == r'\Omega'
        
        # Test mathematical symbols
        assert latex_symbols['∫'] == r'\int'
        assert latex_symbols['∑'] == r'\sum'
        assert latex_symbols['∞'] == r'\infty'
        assert latex_symbols['≠'] == r'\neq'
    
    def test_greek_letters_loading(self):
        """Test Greek letters list."""
        detector = EquationDetector()
        greek_letters = detector.greek_letters
        
        assert 'α' in greek_letters
        assert 'β' in greek_letters
        assert 'π' in greek_letters
        assert 'Ω' in greek_letters
        assert len(greek_letters) == 48  # 24 lowercase + 24 uppercase
    
    def test_mathematical_operators_loading(self):
        """Test mathematical operators list."""
        detector = EquationDetector()
        operators = detector.mathematical_operators
        
        assert '+' in operators
        assert '-' in operators
        assert '=' in operators
        assert '≠' in operators
        assert '∫' in operators
        assert '∑' in operators
    
    def test_simple_equation_detection(self):
        """Test detection of simple equations."""
        detector = EquationDetector()
        
        # Test simple equation
        text = "The equation is x = 5"
        equations = detector.detect_equations(text, 1)
        
        assert len(equations) > 0
        equation = equations[0]
        assert equation.equation_type == EquationType.INLINE
        assert equation.page_number == 1
        assert equation.confidence > 0.5
    
    def test_display_equation_detection(self):
        """Test detection of display equations."""
        detector = EquationDetector()
        
        # Test display equation
        text = """Some text here.
        
        E = mc²
        
        More text here."""
        
        equations = detector.detect_equations(text, 1)
        
        # Should find equations
        assert len(equations) > 0
        
        # Check for display equation
        display_equations = [eq for eq in equations if eq.equation_type == EquationType.DISPLAY]
        assert len(display_equations) > 0
    
    def test_numbered_equation_detection(self):
        """Test detection of numbered equations."""
        detector = EquationDetector()
        
        # Test numbered equation
        text = "The fundamental equation is F = ma (1)"
        equations = detector.detect_equations(text, 1)
        
        numbered_equations = [eq for eq in equations if eq.equation_type == EquationType.NUMBERED]
        if numbered_equations:
            equation = numbered_equations[0]
            assert equation.equation_number == "1"
    
    def test_greek_letter_detection(self):
        """Test detection of Greek letters in equations."""
        detector = EquationDetector()
        
        # Test Greek letters
        text = "The angle α is related to β by the equation α = β + π"
        equations = detector.detect_equations(text, 1)
        
        assert len(equations) > 0
        
        # Check variables extraction - Greek letters should be detected as variables
        greek_variables_found = False
        for equation in equations:
            if 'α' in equation.variables or 'β' in equation.variables or 'π' in equation.variables:
                greek_variables_found = True
                break
        assert greek_variables_found, "No Greek letter variables found in equations"
    
    def test_fraction_detection(self):
        """Test detection of fractions."""
        detector = EquationDetector()
        
        # Test fraction
        text = "The ratio is a/b = c/d"
        equations = detector.detect_equations(text, 1)
        
        fraction_equations = [eq for eq in equations if eq.equation_type == EquationType.FRACTION]
        assert len(fraction_equations) > 0
    
    def test_integral_detection(self):
        """Test detection of integrals."""
        detector = EquationDetector()
        
        # Test integral
        text = "The integral ∫f(x)dx represents the area under the curve"
        equations = detector.detect_equations(text, 1)
        
        integral_equations = [eq for eq in equations if eq.equation_type == EquationType.INTEGRAL]
        assert len(integral_equations) > 0
    
    def test_summation_detection(self):
        """Test detection of summations."""
        detector = EquationDetector()
        
        # Test summation
        text = "The sum ∑i=1 to n of ai equals the total"
        equations = detector.detect_equations(text, 1)
        
        summation_equations = [eq for eq in equations if eq.equation_type == EquationType.SUMMATION]
        assert len(summation_equations) > 0
    
    def test_subscript_superscript_detection(self):
        """Test detection of subscripts and superscripts."""
        detector = EquationDetector()
        
        # Test subscript/superscript
        text = "The variables x_1 and y^2 are related"
        equations = detector.detect_equations(text, 1)
        
        sub_super_equations = [eq for eq in equations if eq.equation_type == EquationType.SUBSCRIPT_SUPERSCRIPT]
        assert len(sub_super_equations) > 0
    
    def test_latex_generation(self):
        """Test LaTeX code generation."""
        detector = EquationDetector()
        
        # Test LaTeX generation for different equation types
        inline_latex = detector._generate_latex("x = 5", EquationType.INLINE)
        assert inline_latex == "$x = 5$"
        
        display_latex = detector._generate_latex("E = mc²", EquationType.DISPLAY)
        assert display_latex == "\\[\nE = mc²\n\\]"
        
        numbered_latex = detector._generate_latex("F = ma", EquationType.NUMBERED)
        assert numbered_latex == "\\begin{equation}\nF = ma\n\\end{equation}"
    
    def test_mathml_generation(self):
        """Test MathML code generation."""
        detector = EquationDetector()
        
        # Test MathML generation
        inline_mathml = detector._generate_mathml("x = 5", EquationType.INLINE)
        assert '<math><mrow>x = 5</mrow></math>' in inline_mathml
        
        display_mathml = detector._generate_mathml("E = mc²", EquationType.DISPLAY)
        assert '<math display="block"><mrow>E = mc²</mrow></math>' in display_mathml
    
    def test_complexity_assessment(self):
        """Test equation complexity assessment."""
        detector = EquationDetector()
        
        # Simple equation
        simple_complexity = detector._assess_complexity("x = 5")
        assert simple_complexity == EquationComplexity.SIMPLE
        
        # Complex equation with Greek letters and operators
        complex_complexity = detector._assess_complexity("∫α^β + ∑γ_i * δ/ε")
        assert complex_complexity in [EquationComplexity.COMPLEX, EquationComplexity.VERY_COMPLEX]
    
    def test_variable_extraction(self):
        """Test variable extraction from equations."""
        detector = EquationDetector()
        
        # Test variable extraction
        variables = detector._extract_variables("x = a + b_1 + α")
        assert 'x' in variables
        assert 'a' in variables
        assert 'b_1' in variables
        assert 'α' in variables
    
    def test_operator_extraction(self):
        """Test operator extraction from equations."""
        detector = EquationDetector()
        
        # Test operator extraction
        operators = detector._extract_operators("x = a + b - c * d / e")
        assert '=' in operators
        assert '+' in operators
        assert '-' in operators
        assert '*' in operators
        assert '/' in operators
    
    def test_confidence_calculation(self):
        """Test confidence score calculation."""
        detector = EquationDetector()
        
        # Test confidence for different equation types
        simple_confidence = detector._calculate_confidence("x = 5", EquationType.INLINE)
        assert 0.5 <= simple_confidence <= 1.0
        
        complex_confidence = detector._calculate_confidence("∫α^β = ∑γ_i", EquationType.NUMBERED)
        assert complex_confidence > simple_confidence


class TestEquationProcessor:
    """Test equation processor functionality."""
    
    def test_equation_processor_creation(self):
        """Test EquationProcessor instantiation."""
        processor = EquationProcessor()
        assert processor is not None
        assert processor.detector is not None
        assert processor.equation_refs is not None
    
    def test_equation_processing_with_mock_pdf(self):
        """Test equation processing with mock PDF content."""
        processor = EquationProcessor()
        
        # Mock PDF content
        mock_pdf_content = b"mock pdf content"
        
        # Mock fitz document
        with patch('paper2data.equation_processor.fitz.open') as mock_open:
            mock_doc = Mock()
            mock_page = Mock()
            mock_page.get_text.return_value = "The equation is E = mc² (1)"
            mock_doc.page_count = 1
            mock_doc.__getitem__ = Mock(return_value=mock_page)
            mock_doc.close = Mock()
            mock_open.return_value = mock_doc
            
            # Process equations
            results = processor.process_equations(mock_pdf_content)
            
            # Verify results
            assert "total_equations" in results
            assert "equations" in results
            assert "equation_references" in results
            assert "statistics" in results
            assert results["processing_status"] == "completed"
    
    def test_equation_reference_finding(self):
        """Test finding equation references in text."""
        processor = EquationProcessor()
        
        # Test reference finding
        text = "As shown in Equation (1), the result follows from Eq. 2"
        references = processor._find_equation_references(text, 1)
        
        assert len(references) >= 1
        assert any(ref["equation_number"] == "1" for ref in references)
    
    def test_equation_reference_linking(self):
        """Test linking equations with their references."""
        processor = EquationProcessor()
        
        # Create mock equations
        equations = [
            MathematicalEquation(
                equation_id="eq_1",
                equation_type=EquationType.NUMBERED,
                complexity=EquationComplexity.SIMPLE,
                raw_text="E = mc²",
                latex_code="$E = mc²$",
                mathml_code="<math><mrow>E = mc²</mrow></math>",
                position={"x": 0, "y": 0, "width": 10, "height": 1},
                page_number=1,
                confidence=0.8,
                context_before="",
                context_after="",
                equation_number="1"
            )
        ]
        
        # Create mock references
        references = [
            {
                "reference_text": "Equation (1)",
                "equation_number": "1",
                "page_number": 1,
                "position": 50
            }
        ]
        
        # Link equations and references
        processor._link_equation_references(equations, references)
        
        # Verify linking
        assert len(equations[0].referenced_by) > 0
        assert "Equation (1)" in equations[0].referenced_by
    
    def test_equation_statistics_generation(self):
        """Test generation of equation statistics."""
        processor = EquationProcessor()
        
        # Create mock equations
        equations = [
            MathematicalEquation(
                equation_id="eq_1",
                equation_type=EquationType.INLINE,
                complexity=EquationComplexity.SIMPLE,
                raw_text="x = 5",
                latex_code="$x = 5$",
                mathml_code="<math><mrow>x = 5</mrow></math>",
                position={"x": 0, "y": 0, "width": 10, "height": 1},
                page_number=1,
                confidence=0.8,
                context_before="",
                context_after="",
                variables=["x"],
                operators=["="]
            ),
            MathematicalEquation(
                equation_id="eq_2",
                equation_type=EquationType.DISPLAY,
                complexity=EquationComplexity.COMPLEX,
                raw_text="E = mc²",
                latex_code="\\[E = mc²\\]",
                mathml_code="<math display='block'><mrow>E = mc²</mrow></math>",
                position={"x": 0, "y": 5, "width": 15, "height": 1},
                page_number=1,
                confidence=0.9,
                context_before="",
                context_after="",
                variables=["E", "m", "c"],
                operators=["="]
            )
        ]
        
        # Generate statistics
        stats = processor._generate_equation_statistics(equations)
        
        # Verify statistics
        assert stats["total_equations"] == 2
        assert stats["equations_by_type"]["inline"] == 1
        assert stats["equations_by_type"]["display"] == 1
        assert stats["equations_by_complexity"]["simple"] == 1
        assert stats["equations_by_complexity"]["complex"] == 1
        assert stats["unique_variables"] == 4  # x, E, m, c
        assert stats["unique_operators"] == 1  # =


class TestMathematicalEquation:
    """Test MathematicalEquation dataclass."""
    
    def test_equation_creation(self):
        """Test equation object creation."""
        equation = MathematicalEquation(
            equation_id="eq_1",
            equation_type=EquationType.INLINE,
            complexity=EquationComplexity.SIMPLE,
            raw_text="x = 5",
            latex_code="$x = 5$",
            mathml_code="<math><mrow>x = 5</mrow></math>",
            position={"x": 0, "y": 0, "width": 10, "height": 1},
            page_number=1,
            confidence=0.8,
            context_before="",
            context_after=""
        )
        
        assert equation.equation_id == "eq_1"
        assert equation.equation_type == EquationType.INLINE
        assert equation.complexity == EquationComplexity.SIMPLE
        assert equation.raw_text == "x = 5"
        assert equation.page_number == 1
        assert equation.confidence == 0.8
        assert equation.referenced_by == []
        assert equation.variables == []
        assert equation.operators == []
    
    def test_equation_serialization(self):
        """Test equation serialization to dictionary."""
        equation = MathematicalEquation(
            equation_id="eq_1",
            equation_type=EquationType.INLINE,
            complexity=EquationComplexity.SIMPLE,
            raw_text="x = 5",
            latex_code="$x = 5$",
            mathml_code="<math><mrow>x = 5</mrow></math>",
            position={"x": 0, "y": 0, "width": 10, "height": 1},
            page_number=1,
            confidence=0.8,
            context_before="",
            context_after=""
        )
        
        # Serialize to dictionary
        equation_dict = equation.to_dict()
        
        # Verify serialization
        assert equation_dict["equation_id"] == "eq_1"
        assert equation_dict["equation_type"] == "inline"
        assert equation_dict["complexity"] == "simple"
        assert equation_dict["raw_text"] == "x = 5"
        assert equation_dict["page_number"] == 1
        assert equation_dict["confidence"] == 0.8


class TestGlobalFunctions:
    """Test global functions and instances."""
    
    def test_global_equation_processor_instance(self):
        """Test global equation processor instance."""
        processor1 = get_equation_processor()
        processor2 = get_equation_processor()
        
        # Should be the same instance
        assert processor1 is processor2
    
    def test_process_equations_from_pdf(self):
        """Test global equation processing function."""
        mock_pdf_content = b"mock pdf content"
        
        # Mock the equation processor
        with patch('paper2data.equation_processor.EquationProcessor') as mock_processor_class:
            mock_processor = Mock()
            mock_processor.process_equations.return_value = {
                "total_equations": 1,
                "equations": [],
                "processing_status": "completed"
            }
            mock_processor_class.return_value = mock_processor
            
            # Process equations
            results = process_equations_from_pdf(mock_pdf_content)
            
            # Verify results
            assert "total_equations" in results
            assert "equations" in results
            assert "processing_status" in results


class TestEquationExport:
    """Test equation export functionality."""
    
    def test_latex_export(self):
        """Test LaTeX export functionality."""
        # Create mock equations
        equations = [
            MathematicalEquation(
                equation_id="eq_1",
                equation_type=EquationType.INLINE,
                complexity=EquationComplexity.SIMPLE,
                raw_text="x = 5",
                latex_code="$x = 5$",
                mathml_code="<math><mrow>x = 5</mrow></math>",
                position={"x": 0, "y": 0, "width": 10, "height": 1},
                page_number=1,
                confidence=0.8,
                context_before="",
                context_after=""
            )
        ]
        
        # Test LaTeX export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.tex', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            export_equations_to_latex(equations, output_path)
            
            # Verify file was created
            assert output_path.exists()
            
            # Verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert "\\documentclass{article}" in content
                assert "\\usepackage{amsmath}" in content
                assert "$x = 5$" in content
                assert "\\end{document}" in content
        finally:
            output_path.unlink(missing_ok=True)
    
    def test_mathml_export(self):
        """Test MathML export functionality."""
        # Create mock equations
        equations = [
            MathematicalEquation(
                equation_id="eq_1",
                equation_type=EquationType.INLINE,
                complexity=EquationComplexity.SIMPLE,
                raw_text="x = 5",
                latex_code="$x = 5$",
                mathml_code="<math><mrow>x = 5</mrow></math>",
                position={"x": 0, "y": 0, "width": 10, "height": 1},
                page_number=1,
                confidence=0.8,
                context_before="",
                context_after=""
            )
        ]
        
        # Test MathML export
        with tempfile.NamedTemporaryFile(mode='w', suffix='.html', delete=False) as f:
            output_path = Path(f.name)
        
        try:
            export_equations_to_mathml(equations, output_path)
            
            # Verify file was created
            assert output_path.exists()
            
            # Verify content
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                assert '<?xml version="1.0" encoding="UTF-8"?>' in content
                assert '<html xmlns="http://www.w3.org/1999/xhtml">' in content
                assert '<math><mrow>x = 5</mrow></math>' in content
                assert '</html>' in content
        finally:
            output_path.unlink(missing_ok=True)


if __name__ == "__main__":
    pytest.main([__file__, "-v"]) 
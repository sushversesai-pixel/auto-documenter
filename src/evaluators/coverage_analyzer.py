"""
Coverage Analyzer for Documentation Assessment

Analyzes code coverage and documentation completeness
to provide quantitative metrics about documentation quality.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from pathlib import Path

from models.code_elements import CodeFunction, CodeClass, CodeModule


@dataclass
class CoverageMetrics:
    """Container for documentation coverage metrics."""
    total_elements: int
    documented_elements: int
    coverage_percentage: float
    missing_docstrings: int
    missing_parameters: int
    missing_returns: int
    missing_examples: int
    function_coverage: float
    class_coverage: float
    module_coverage: float


class CoverageAnalyzer:
    """Analyzer for documentation coverage metrics."""
    
    def analyze_coverage(self, elements: List[Any], generated_docs: Dict[str, Any]) -> CoverageMetrics:
        """
        Analyze documentation coverage for a set of code elements.
        
        Args:
            elements: List of parsed code elements
            generated_docs: Generated documentation data
            
        Returns:
            CoverageMetrics object with coverage analysis
        """
        total_elements = len(elements)
        
        # Categorize elements
        functions = [e for e in elements if e.type == 'function']
        classes = [e for e in elements if e.type == 'class']
        modules = [e for e in elements if e.type == 'module']
        
        # Count documented elements
        documented_elements = 0
        missing_docstrings = 0
        missing_parameters = 0
        missing_returns = 0
        missing_examples = 0
        
        for element in elements:
            element_key = f"{element.name}_{element.line_number}"
            doc = generated_docs.get(element_key, {})
            
            is_documented = False
            
            # Check if element has documentation
            if doc.get('summary') and doc.get('summary') != f"{element.type.title()} {element.name}":
                is_documented = True
                documented_elements += 1
            else:
                missing_docstrings += 1
            
            # Check specific documentation aspects
            if element.type == 'function':
                if hasattr(element, 'parameters') and element.parameters:
                    if not doc.get('parameters'):
                        missing_parameters += 1
                
                if hasattr(element, 'return_type') and element.return_type:
                    if not doc.get('returns'):
                        missing_returns += 1
                
                if not doc.get('examples'):
                    missing_examples += 1
        
        # Calculate coverage percentages
        coverage_percentage = (documented_elements / total_elements * 100) if total_elements > 0 else 0
        
        function_coverage = self._calculate_type_coverage(functions, generated_docs)
        class_coverage = self._calculate_type_coverage(classes, generated_docs)
        module_coverage = self._calculate_type_coverage(modules, generated_docs)
        
        return CoverageMetrics(
            total_elements=total_elements,
            documented_elements=documented_elements,
            coverage_percentage=coverage_percentage,
            missing_docstrings=missing_docstrings,
            missing_parameters=missing_parameters,
            missing_returns=missing_returns,
            missing_examples=missing_examples,
            function_coverage=function_coverage,
            class_coverage=class_coverage,
            module_coverage=module_coverage
        )
    
    def _calculate_type_coverage(self, elements: List[Any], generated_docs: Dict[str, Any]) -> float:
        """Calculate coverage percentage for a specific element type."""
        if not elements:
            return 100.0
        
        documented = 0
        for element in elements:
            element_key = f"{element.name}_{element.line_number}"
            doc = generated_docs.get(element_key, {})
            
            if doc.get('summary') and doc.get('summary') != f"{element.type.title()} {element.name}":
                documented += 1
        
        return (documented / len(elements)) * 100
    
    def generate_coverage_report(self, metrics: CoverageMetrics, output_path: str) -> str:
        """
        Generate a detailed coverage report.
        
        Args:
            metrics: Coverage metrics to report
            output_path: Path where report will be saved
            
        Returns:
            Path to generated report file
        """
        report_content = f"""# Documentation Coverage Report

## Overall Coverage
- **Total Elements**: {metrics.total_elements}
- **Documented Elements**: {metrics.documented_elements}
- **Coverage Percentage**: {metrics.coverage_percentage:.1f}%

## Coverage by Type
- **Functions**: {metrics.function_coverage:.1f}%
- **Classes**: {metrics.class_coverage:.1f}%  
- **Modules**: {metrics.module_coverage:.1f}%

## Missing Documentation
- **Missing Docstrings**: {metrics.missing_docstrings}
- **Missing Parameter Docs**: {metrics.missing_parameters}
- **Missing Return Docs**: {metrics.missing_returns}
- **Missing Examples**: {metrics.missing_examples}

## Quality Assessment
{'✅ Excellent' if metrics.coverage_percentage >= 90 else '⚠️ Good' if metrics.coverage_percentage >= 70 else '❌ Needs Improvement'} - {metrics.coverage_percentage:.1f}% coverage

## Recommendations
"""
        
        if metrics.coverage_percentage < 70:
            report_content += "- Focus on adding basic docstrings to undocumented functions and classes\n"
        
        if metrics.missing_parameters > 0:
            report_content += "- Add parameter descriptions to improve function documentation\n"
        
        if metrics.missing_returns > 0:
            report_content += "- Document return values for better API understanding\n"
        
        if metrics.missing_examples > 0:
            report_content += "- Include usage examples to improve user experience\n"
        
        # Save report
        report_path = Path(output_path) / "coverage_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(report_content)
        
        return str(report_path)
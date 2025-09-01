"""
Hallucination Detection for AI-Generated Documentation

Detects potential hallucinations, inconsistencies, and errors
in AI-generated documentation content.
"""

import re
import ast
from typing import Dict, List, Any, Optional, Set
from dataclasses import dataclass
from pathlib import Path


@dataclass
class HallucinationCheck:
    """Container for hallucination detection results."""
    element_name: str
    check_type: str
    severity: str  # 'high', 'medium', 'low'
    message: str
    confidence: float


@dataclass
class HallucinationReport:
    """Container for comprehensive hallucination analysis."""
    total_checks: int
    issues_found: int
    high_severity: int
    medium_severity: int
    low_severity: int
    confidence_score: float
    issues: List[HallucinationCheck]


class HallucinationDetector:
    """Detector for AI hallucinations in generated documentation."""
    
    def __init__(self):
        self.common_hallucination_patterns = [
            r'(?i)this function (never|always) (returns?|raises?)',
            r'(?i)(guaranteed|ensures?|promises?) to',
            r'(?i)(perfectly|completely|absolutely) (safe|secure)',
            r'(?i)will (never|always) fail',
            r'(?i)(impossible|cannot) to (break|fail)',
        ]
        
        self.suspicious_claims = [
            r'(?i)(100%|completely|perfectly) (accurate|correct|safe)',
            r'(?i)(never|always) (works?|fails?)',
            r'(?i)(impossible|guaranteed) (to|that)',
            r'(?i)(instantly|immediately) (solves?|fixes?)',
        ]
    
    def detect_hallucinations(self, elements: List[Any], generated_docs: Dict[str, Any], 
                            original_code: Optional[str] = None) -> HallucinationReport:
        """
        Detect potential hallucinations in generated documentation.
        
        Args:
            elements: List of code elements
            generated_docs: AI-generated documentation
            original_code: Original source code for validation
            
        Returns:
            HallucinationReport with detected issues
        """
        issues = []
        total_checks = 0
        
        for element in elements:
            element_key = f"{element.name}_{element.line_number}"
            doc = generated_docs.get(element_key, {})
            
            if not doc:
                continue
            
            # Check for various hallucination types
            issues.extend(self._check_overly_confident_claims(element.name, doc))
            issues.extend(self._check_parameter_consistency(element, doc))
            issues.extend(self._check_return_type_consistency(element, doc))
            issues.extend(self._check_code_example_validity(element.name, doc))
            
            total_checks += 4
        
        # Calculate summary metrics
        high_severity = len([i for i in issues if i.severity == 'high'])
        medium_severity = len([i for i in issues if i.severity == 'medium'])
        low_severity = len([i for i in issues if i.severity == 'low'])
        
        confidence_score = max(0, 100 - (high_severity * 20 + medium_severity * 10 + low_severity * 5))
        
        return HallucinationReport(
            total_checks=total_checks,
            issues_found=len(issues),
            high_severity=high_severity,
            medium_severity=medium_severity,
            low_severity=low_severity,
            confidence_score=confidence_score,
            issues=issues
        )
    
    def _check_overly_confident_claims(self, element_name: str, doc: Dict[str, Any]) -> List[HallucinationCheck]:
        """Check for overly confident or absolute claims."""
        issues = []
        text = str(doc.get('description', '')) + str(doc.get('summary', ''))
        
        for pattern in self.common_hallucination_patterns:
            if re.search(pattern, text):
                issues.append(HallucinationCheck(
                    element_name=element_name,
                    check_type='overconfident_claim',
                    severity='high',
                    message=f"Contains overconfident claim that may not be accurate",
                    confidence=0.8
                ))
        
        for pattern in self.suspicious_claims:
            if re.search(pattern, text):
                issues.append(HallucinationCheck(
                    element_name=element_name,
                    check_type='suspicious_claim',
                    severity='medium',
                    message=f"Contains suspicious absolute claim",
                    confidence=0.6
                ))
        
        return issues
    
    def _check_parameter_consistency(self, element: Any, doc: Dict[str, Any]) -> List[HallucinationCheck]:
        """Check if documented parameters match actual function parameters."""
        issues = []
        
        if not hasattr(element, 'parameters') or element.type != 'function':
            return issues
        
        actual_params = {p.name for p in element.parameters}
        documented_params = set()
        
        if doc.get('parameters'):
            documented_params = {p.get('name', '') for p in doc['parameters']}
        
        # Check for extra documented parameters
        extra_params = documented_params - actual_params
        if extra_params:
            issues.append(HallucinationCheck(
                element_name=element.name,
                check_type='parameter_hallucination',
                severity='high',
                message=f"Documents non-existent parameters: {', '.join(extra_params)}",
                confidence=0.9
            ))
        
        # Check for missing parameter documentation
        missing_params = actual_params - documented_params
        if missing_params and len(missing_params) > len(actual_params) * 0.5:
            issues.append(HallucinationCheck(
                element_name=element.name,
                check_type='incomplete_parameters',
                severity='medium',
                message=f"Missing documentation for parameters: {', '.join(missing_params)}",
                confidence=0.7
            ))
        
        return issues
    
    def _check_return_type_consistency(self, element: Any, doc: Dict[str, Any]) -> List[HallucinationCheck]:
        """Check if documented return type matches actual return type annotation."""
        issues = []
        
        if not hasattr(element, 'return_type') or element.type != 'function':
            return issues
        
        actual_return = element.return_type
        documented_return = doc.get('returns', {}).get('type', '')
        
        if actual_return and documented_return:
            # Simple check for major inconsistencies
            if (actual_return.lower() in ['str', 'string'] and 
                documented_return.lower() in ['int', 'integer', 'float', 'number']):
                issues.append(HallucinationCheck(
                    element_name=element.name,
                    check_type='return_type_mismatch',
                    severity='high',
                    message=f"Return type mismatch: actual '{actual_return}' vs documented '{documented_return}'",
                    confidence=0.8
                ))
        
        return issues
    
    def _check_code_example_validity(self, element_name: str, doc: Dict[str, Any]) -> List[HallucinationCheck]:
        """Check if code examples are syntactically valid."""
        issues = []
        
        examples = doc.get('examples', [])
        for i, example in enumerate(examples):
            code = example.get('code', '')
            if not code:
                continue
            
            try:
                # Try to parse Python code examples
                if 'def ' in code or 'import ' in code or '=' in code:
                    ast.parse(code)
            except SyntaxError:
                issues.append(HallucinationCheck(
                    element_name=element_name,
                    check_type='invalid_code_example',
                    severity='medium',
                    message=f"Example {i+1} contains invalid Python syntax",
                    confidence=0.9
                ))
        
        return issues
    
    def generate_hallucination_report(self, report: HallucinationReport, output_path: str) -> str:
        """
        Generate a detailed hallucination detection report.
        
        Args:
            report: Hallucination analysis results
            output_path: Path where report will be saved
            
        Returns:
            Path to generated report file
        """
        content = f"""# Hallucination Detection Report

## Summary
- **Total Checks**: {report.total_checks}
- **Issues Found**: {report.issues_found}
- **Confidence Score**: {report.confidence_score:.1f}%

## Issue Breakdown
- **High Severity**: {report.high_severity} issues
- **Medium Severity**: {report.medium_severity} issues  
- **Low Severity**: {report.low_severity} issues

## Quality Assessment
{'✅ High Confidence' if report.confidence_score >= 80 else '⚠️ Medium Confidence' if report.confidence_score >= 60 else '❌ Low Confidence'} - {report.confidence_score:.1f}% confidence in documentation accuracy

"""
        
        if report.issues:
            content += "## Detected Issues\n\n"
            for issue in sorted(report.issues, key=lambda x: {'high': 3, 'medium': 2, 'low': 1}[x.severity], reverse=True):
                severity_icon = {'high': '🔴', 'medium': '🟡', 'low': '🟢'}[issue.severity]
                content += f"### {severity_icon} {issue.element_name}\n"
                content += f"**Type**: {issue.check_type.replace('_', ' ').title()}\n"
                content += f"**Message**: {issue.message}\n"
                content += f"**Confidence**: {issue.confidence:.1f}\n\n"
        else:
            content += "## ✅ No Issues Detected\n\nAll documentation appears to be consistent and accurate.\n"
        
        # Save report
        report_path = Path(output_path) / "hallucination_report.md"
        with open(report_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return str(report_path)
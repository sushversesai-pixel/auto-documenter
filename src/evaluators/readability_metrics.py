"""
Readability Metrics for Documentation Quality Assessment

Analyzes generated documentation to provide readability scores
and quality metrics based on various criteria.
"""

import re
import math
from typing import Dict, List, Any, Optional
from dataclasses import dataclass


@dataclass
class ReadabilityMetrics:
    """Container for readability assessment results."""
    flesch_score: float
    clarity_score: float
    completeness_score: float
    consistency_score: float
    overall_score: float
    word_count: int
    sentence_count: int
    avg_sentence_length: float
    technical_terms_ratio: float


class ReadabilityAnalyzer:
    """Analyzer for documentation readability and quality."""
    
    def __init__(self):
        self.technical_terms = {
            'python': ['function', 'class', 'method', 'parameter', 'return', 'exception', 
                      'module', 'import', 'decorator', 'async', 'await', 'yield'],
            'javascript': ['function', 'class', 'method', 'parameter', 'return', 'callback',
                          'promise', 'async', 'await', 'export', 'import', 'const', 'var']
        }
    
    def analyze_documentation(self, documentation: str, language: str = 'python') -> ReadabilityMetrics:
        """
        Analyze documentation text for readability metrics.
        
        Args:
            documentation: Generated documentation text
            language: Programming language context
            
        Returns:
            ReadabilityMetrics object with analysis results
        """
        # Basic text analysis
        words = self._extract_words(documentation)
        sentences = self._extract_sentences(documentation)
        
        word_count = len(words)
        sentence_count = len(sentences) if sentences else 1
        avg_sentence_length = word_count / sentence_count
        
        # Calculate metrics
        flesch_score = self._calculate_flesch_score(words, sentences)
        clarity_score = self._calculate_clarity_score(documentation, language)
        completeness_score = self._calculate_completeness_score(documentation)
        consistency_score = self._calculate_consistency_score(documentation)
        technical_terms_ratio = self._calculate_technical_terms_ratio(words, language)
        
        # Overall score (weighted average)
        overall_score = (
            flesch_score * 0.3 +
            clarity_score * 0.25 +
            completeness_score * 0.25 +
            consistency_score * 0.2
        )
        
        return ReadabilityMetrics(
            flesch_score=flesch_score,
            clarity_score=clarity_score,
            completeness_score=completeness_score,
            consistency_score=consistency_score,
            overall_score=overall_score,
            word_count=word_count,
            sentence_count=sentence_count,
            avg_sentence_length=avg_sentence_length,
            technical_terms_ratio=technical_terms_ratio
        )
    
    def _extract_words(self, text: str) -> List[str]:
        """Extract words from text, excluding code blocks."""
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        text = re.sub(r'`.*?`', '', text)
        
        # Extract words (alphabetic characters only)
        words = re.findall(r'\b[a-zA-Z]+\b', text.lower())
        return words
    
    def _extract_sentences(self, text: str) -> List[str]:
        """Extract sentences from text."""
        # Remove code blocks
        text = re.sub(r'```.*?```', '', text, flags=re.DOTALL)
        
        # Split on sentence endings
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        return sentences
    
    def _calculate_flesch_score(self, words: List[str], sentences: List[str]) -> float:
        """Calculate Flesch Reading Ease score (0-100, higher is better)."""
        if not words or not sentences:
            return 0.0
        
        avg_sentence_length = len(words) / len(sentences)
        avg_syllables = sum(self._count_syllables(word) for word in words) / len(words)
        
        # Flesch formula
        score = 206.835 - (1.015 * avg_sentence_length) - (84.6 * avg_syllables)
        return max(0, min(100, score))
    
    def _count_syllables(self, word: str) -> int:
        """Estimate syllable count for a word."""
        word = word.lower()
        vowels = 'aeiouy'
        count = 0
        prev_was_vowel = False
        
        for char in word:
            is_vowel = char in vowels
            if is_vowel and not prev_was_vowel:
                count += 1
            prev_was_vowel = is_vowel
        
        # Handle silent e
        if word.endswith('e') and count > 1:
            count -= 1
        
        return max(1, count)
    
    def _calculate_clarity_score(self, text: str, language: str) -> float:
        """Calculate clarity score based on structure and formatting."""
        score = 100.0
        
        # Check for proper section headers
        if not re.search(r'^#+\s+', text, re.MULTILINE):
            score -= 20
        
        # Check for parameter documentation
        if 'Parameters:' not in text and 'Args:' not in text:
            score -= 25
        
        # Check for return value documentation
        if 'Returns:' not in text and 'Return:' not in text:
            score -= 15
        
        # Check for examples
        if 'Examples:' not in text and 'Example:' not in text:
            score -= 20
        
        # Check for code blocks
        if '```' not in text:
            score -= 10
        
        return max(0, score)
    
    def _calculate_completeness_score(self, text: str) -> float:
        """Calculate completeness score based on documentation sections."""
        score = 0.0
        max_score = 100.0
        
        # Essential sections (20 points each)
        if re.search(r'(description|summary)', text, re.IGNORECASE):
            score += 20
        
        if re.search(r'(parameters?|args?)', text, re.IGNORECASE):
            score += 20
        
        if re.search(r'returns?', text, re.IGNORECASE):
            score += 20
        
        if re.search(r'examples?', text, re.IGNORECASE):
            score += 20
        
        # Additional sections (10 points each)
        if re.search(r'(raises?|exceptions?)', text, re.IGNORECASE):
            score += 10
        
        if re.search(r'(notes?|remarks?)', text, re.IGNORECASE):
            score += 10
        
        return min(max_score, score)
    
    def _calculate_consistency_score(self, text: str) -> float:
        """Calculate consistency score based on formatting patterns."""
        score = 100.0
        
        # Check for consistent parameter formatting
        param_patterns = [
            r'- `\w+`:', r'\*\*\w+\*\*:', r':\w+:', r'@param'
        ]
        param_matches = sum(len(re.findall(pattern, text)) for pattern in param_patterns)
        
        if param_matches == 0:
            score -= 30
        
        # Check for consistent code block formatting
        code_blocks = re.findall(r'```\w*\n.*?\n```', text, re.DOTALL)
        inline_code = re.findall(r'`[^`]+`', text)
        
        if len(code_blocks) == 0 and len(inline_code) == 0:
            score -= 20
        
        return max(0, score)
    
    def _calculate_technical_terms_ratio(self, words: List[str], language: str) -> float:
        """Calculate ratio of technical terms to total words."""
        if not words:
            return 0.0
        
        tech_terms = self.technical_terms.get(language, [])
        tech_word_count = sum(1 for word in words if word in tech_terms)
        
        return tech_word_count / len(words)
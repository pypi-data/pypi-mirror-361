"""
Result parsing and processing for OCR output.

This module provides utilities for parsing and processing OCR results
from various sources into a standardized format.
"""

import json
import logging
import re
from typing import Any, Dict, List, Optional, Tuple, Union

from .models import OCRResult, TextBlock, BoundingBox
from ..utils.logging_utils import setup_logger

class ResultParser:
    """Parser for OCR results from different sources."""
    
    def __init__(self, language: str = "polish", min_confidence: float = 0.5):
        """Initialize the result parser.
        
        Args:
            language: Default language for OCR results
            min_confidence: Minimum confidence threshold for text blocks
        """
        self.logger = setup_logger('result_parser')
        self.language = language
        self.min_confidence = min_confidence
    
    def parse_ollama_output(self, output: Union[str, Dict], language: Optional[str] = None) -> OCRResult:
        """Parse the output from Ollama into an OCRResult.
        
        Args:
            output: Raw output from Ollama (can be string or dict)
            language: Language of the text (overrides default if provided)
            
        Returns:
            Parsed OCRResult
            
        Raises:
            ValueError: If the output cannot be parsed
        """
        if isinstance(output, str):
            try:
                # Try to parse as JSON
                output = self._extract_json(output)
            except json.JSONDecodeError as e:
                raise ValueError("Failed to parse Ollama output as JSON") from e
        
        if not isinstance(output, dict):
            raise ValueError(f"Expected dict output from Ollama, got {type(output)}")
        
        # Create base result
        result = OCRResult(
            text=output.get("text", ""),
            language=language or self.language,
            model=output.get("model", "ollama"),
            confidence=float(output.get("confidence", 0.0)),
            metadata={
                "source": "ollama",
                **output.get("metadata", {})
            }
        )
        
        # Parse text blocks
        blocks = output.get("blocks", [])
        if not blocks and "text" in output:
            # If no blocks but we have text, create a single block
            blocks = [{"text": output["text"], "x": 0, "y": 0, "width": 0, "height": 0}]
        
        for block in blocks:
            try:
                confidence = float(block.get("confidence", 1.0))
                if confidence < self.min_confidence:
                    continue
                    
                text_block = TextBlock(
                    text=block.get("text", ""),
                    x=float(block.get("x", 0)),
                    y=float(block.get("y", 0)),
                    width=float(block.get("width", 0)),
                    height=float(block.get("height", 0)),
                    confidence=confidence,
                    language=block.get("language", language or self.language),
                    metadata=block.get("metadata", {})
                )
                result.blocks.append(text_block)
                
            except (ValueError, TypeError) as e:
                self.logger.warning(f"Failed to parse text block: {block}", exc_info=True)
        
        return result
    
    def _extract_json(self, text: str) -> Dict:
        """Extract a JSON object from a string.
        
        Args:
            text: Text potentially containing JSON
            
        Returns:
            Parsed JSON as a dictionary
            
        Raises:
            json.JSONDecodeError: If no valid JSON is found
        """
        # Try to find JSON in the text
        json_match = re.search(r'\{.*\}', text, re.DOTALL)
        if json_match:
            return json.loads(json_match.group(0))
        
        # If no match, try to parse the whole text as JSON
        return json.loads(text)
    
    def merge_results(self, results: List[OCRResult]) -> OCRResult:
        """Merge multiple OCR results into a single result.
        
        Args:
            results: List of OCRResult objects to merge
            
        Returns:
            Single merged OCRResult
        """
        if not results:
            return OCRResult()
        
        # Use the first result as the base
        merged = OCRResult(
            text="\n\n".join(r.text for r in results if r.text),
            language=results[0].language,
            model=f"merged_{len(results)}_results",
            confidence=sum(r.confidence for r in results) / len(results) if results else 0.0,
            metadata={
                "merged_from": [r.model for r in results],
                "merged_at": len(results)
            }
        )
        
        # Merge all blocks
        for result in results:
            merged.blocks.extend(result.blocks)
        
        return merged

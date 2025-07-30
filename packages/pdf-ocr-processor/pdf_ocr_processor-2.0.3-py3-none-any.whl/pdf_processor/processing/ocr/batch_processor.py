"""
Batch processing for OCR tasks.

This module provides functionality for processing multiple images in batch,
with support for parallel processing and progress tracking.
"""

import json
import logging
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Callable, Iterable

from tqdm import tqdm

from ..models.retry_config import RetryConfig
from ..utils.logging_utils import setup_logger, log_execution_time
from ..utils.validation_utils import validate_image_file

from .models import OCRResult
from .ollama_client import OllamaClient
from .result_parser import ResultParser

class BatchProcessor:
    """Process multiple images in batch with OCR."""
    
    def __init__(
        self,
        model: str = "llava:7b",
        language: str = "polish",
        max_workers: int = 4,
        retry_config: Optional[RetryConfig] = None,
        progress_callback: Optional[Callable[[int, int], None]] = None
    ) -> None:
        """Initialize the batch processor.
        
        Args:
            model: Name of the OCR model to use
            language: Language of the text in the images
            max_workers: Maximum number of parallel workers
            retry_config: Configuration for retrying failed operations
            progress_callback: Callback for progress updates (current, total)
        """
        self.logger = setup_logger('batch_processor')
        self.model = model
        self.language = language
        self.max_workers = max_workers
        self.retry_config = retry_config or RetryConfig()
        self.progress_callback = progress_callback
        
        # Initialize components
        self.ollama_client = OllamaClient(
            model=model,
            retry_config=retry_config
        )
        self.parser = ResultParser(language=language)
    
    @log_execution_time(setup_logger('batch_processor'))
    def process_batch(
        self,
        image_paths: List[Union[str, Path]],
        output_dir: Optional[Union[str, Path]] = None,
        save_intermediate: bool = True,
        **kwargs
    ) -> Dict[Path, OCRResult]:
        """Process multiple images in batch.
        
        Args:
            image_paths: List of paths to input images
            output_dir: Directory to save results (if save_intermediate is True)
            save_intermediate: Whether to save intermediate results
            **kwargs: Additional arguments to pass to the OCR processor
            
        Returns:
            Dictionary mapping input paths to OCRResult objects
        """
        results = {}
        total = len(image_paths)
        
        # Create output directory if needed
        if save_intermediate and output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(parents=True, exist_ok=True)
        
        # Process images in parallel
        with ThreadPoolExecutor(max_workers=self.max_workers) as executor:
            # Submit all tasks
            future_to_path = {
                executor.submit(self._process_single, path, output_dir, save_intermediate, **kwargs): Path(path)
                for path in image_paths
            }
            
            # Process results as they complete
            completed = 0
            with tqdm(total=total, desc="Processing images") as pbar:
                for future in as_completed(future_to_path):
                    path = future_to_path[future]
                    try:
                        result = future.result()
                        results[path] = result
                        
                        # Save intermediate result
                        if save_intermediate and output_dir:
                            self._save_result(result, output_dir / f"{path.stem}_result.json")
                            
                    except Exception as e:
                        self.logger.error(f"Error processing {path}: {str(e)}", exc_info=True)
                    
                    # Update progress
                    completed += 1
                    pbar.update(1)
                    if self.progress_callback:
                        self.progress_callback(completed, total)
        
        return results
    
    def _process_single(
        self,
        image_path: Union[str, Path],
        output_dir: Optional[Path] = None,
        save_intermediate: bool = True,
        **kwargs
    ) -> OCRResult:
        """Process a single image with retries.
        
        Args:
            image_path: Path to the input image
            output_dir: Directory to save results (if save_intermediate is True)
            save_intermediate: Whether to save intermediate results
            **kwargs: Additional arguments to pass to the OCR processor
            
        Returns:
            OCRResult for the processed image
            
        Raises:
            Exception: If processing fails after all retries
        """
        image_path = Path(image_path)
        validate_image_file(image_path)
        
        last_error = None
        delay = self.retry_config.initial_delay
        
        for attempt in range(self.retry_config.max_retries + 1):
            try:
                # Process the image
                result = self.ollama_client.extract_text(
                    image_path=image_path,
                    language=self.language,
                    **kwargs
                )
                
                # Parse the result
                return self.parser.parse_ollama_output(result, language=self.language)
                
            except Exception as e:
                last_error = e
                if attempt < self.retry_config.max_retries:
                    # Calculate next delay with exponential backoff
                    wait_time = min(
                        delay * (2 ** attempt),
                        self.retry_config.max_delay
                    )
                    self.logger.warning(
                        f"Attempt {attempt + 1} failed for {image_path}. "
                        f"Retrying in {wait_time:.1f}s... Error: {str(e)}"
                    )
                    time.sleep(wait_time)
        
        # If we get here, all retries failed
        self.logger.error(
            f"Failed to process {image_path} after {self.retry_config.max_retries} "
            f"attempts. Last error: {str(last_error)}"
        )
        raise last_error or RuntimeError(f"Failed to process {image_path}")
    
    def _save_result(self, result: OCRResult, output_path: Path) -> None:
        """Save an OCR result to a file.
        
        Args:
            result: The OCR result to save
            output_path: Path where to save the result
        """
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(result.to_dict(), f, ensure_ascii=False, indent=2)
            self.logger.debug(f"Saved result to {output_path}")
        except Exception as e:
            self.logger.error(f"Failed to save result to {output_path}: {str(e)}", exc_info=True)

"""Parser module for loading and normalizing test execution JSON."""

import json
import logging
from pathlib import Path
from typing import Dict, Any, List, Optional

from .schemas import TestExecution, Step, Selector

logger = logging.getLogger(__name__)


class TestExecutionParser:
    """Parser for test execution JSON files."""

    def __init__(self, file_path: str):
        """Initialize parser with file path.
        
        Args:
            file_path: Path to the test execution JSON file
        """
        self.file_path = Path(file_path)
        self.test_execution: Optional[TestExecution] = None

    def load(self) -> TestExecution:
        """Load and validate the test execution JSON.
        
        Returns:
            Validated TestExecution object
            
        Raises:
            FileNotFoundError: If file doesn't exist
            ValueError: If JSON is invalid or doesn't match schema
        """
        if not self.file_path.exists():
            raise FileNotFoundError(f"File not found: {self.file_path}")

        logger.info(f"Loading test execution from {self.file_path}")

        try:
            with open(self.file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON: {e}")

        try:
            self.test_execution = TestExecution(**data)
            logger.info(f"Successfully loaded {len(self.test_execution.steps)} steps")
            return self.test_execution
        except Exception as e:
            raise ValueError(f"Invalid test execution schema: {e}")

    def get_metadata(self) -> Dict[str, Any]:
        """Extract metadata from the test execution.
        
        Returns:
            Dictionary with metadata fields
        """
        if not self.test_execution:
            raise ValueError("Test execution not loaded. Call load() first.")

        return {
            "feature_name": self.test_execution.featureName,
            "scenario_name": self.test_execution.scenarioName,
            "step_count": len(self.test_execution.steps),
        }

    def get_starting_url(self) -> Optional[str]:
        """Get the starting URL from the first navigation step.
        
        Returns:
            Starting URL or None if not found
        """
        if not self.test_execution:
            raise ValueError("Test execution not loaded. Call load() first.")

        for step in self.test_execution.steps:
            if step.type == "navigate" and step.output and step.output.url:
                return step.output.url

        return None

    def normalize_step(self, step: Step) -> Dict[str, Any]:
        """Normalize a step into a standardized format.
        
        Args:
            step: Step object to normalize
            
        Returns:
            Dictionary with normalized step data
        """
        normalized = {
            "description": step.description,
            "type": step.type,
            "timestamp": step.timestamp,
        }

        # Add element information if available
        if step.elementText:
            normalized["element_text"] = step.elementText
        if step.elementTag:
            normalized["element_tag"] = step.elementTag
        if step.attributes:
            normalized["attributes"] = step.attributes.model_dump(by_alias=True)

        # Add selectors with normalized priority
        if step.selector:
            normalized["selectors"] = self.normalize_selectors(step.selector)

        # Add output data if available
        if step.output:
            normalized["output"] = step.output.model_dump(exclude_none=True)

        return normalized

    def normalize_selectors(self, selectors: List[Selector]) -> List[Dict[str, Any]]:
        """Normalize and prioritize selectors.
        
        Args:
            selectors: List of selector objects
            
        Returns:
            List of normalized selector dictionaries sorted by priority
        """
        normalized_selectors = []
        
        for selector in selectors:
            # Convert priority to integer
            try:
                priority = int(selector.priority)
            except (ValueError, TypeError):
                priority = 999  # Default low priority for invalid values

            normalized_selectors.append({
                "type": selector.type,
                "value": selector.value,
                "priority": priority,
            })

        # Sort by priority (lower is better)
        normalized_selectors.sort(key=lambda x: x["priority"])

        return normalized_selectors

    def get_step_summary(self) -> List[Dict[str, str]]:
        """Get a summary of all steps.
        
        Returns:
            List of step summaries with type and description
        """
        if not self.test_execution:
            raise ValueError("Test execution not loaded. Call load() first.")

        return [
            {
                "type": step.type,
                "description": step.description,
                "element": step.elementText or "N/A",
            }
            for step in self.test_execution.steps
        ]


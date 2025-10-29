"""OpenAI client wrapper for LLM interactions."""

import os
import logging
import json
from typing import Optional, Dict, Any
import time
from dotenv import load_dotenv

from openai import OpenAI
from openai import OpenAIError

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with OpenAI API."""
    
    # Default configuration
    DEFAULT_MODEL = "gpt-4.1-nano"
    DEFAULT_TEMPERATURE = 0.3

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize LLM client.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY from .env)
            model_name: Model name to use (defaults to gpt-4o)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY in .env file.")

        self.client = OpenAI(api_key=self.api_key)
        self.model_name = model_name or self.DEFAULT_MODEL
        self.temperature = self.DEFAULT_TEMPERATURE

    def _call_api(self, prompt: str, max_retries: int = 3) -> str:
        """Call OpenAI API with retry logic.
        
        Args:
            prompt: Prompt to send to the API
            max_retries: Maximum number of retries
            
        Returns:
            Response text from the API
            
        Raises:
            OpenAIError: If API call fails after retries
        """
        for attempt in range(max_retries):
            try:
                response = self.client.chat.completions.create(
                    model=self.model_name,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a helpful assistant that analyzes test automation steps and provides structured, concise responses.",
                        },
                        {"role": "user", "content": prompt},
                    ],
                    temperature=self.temperature,
                )

                return response.choices[0].message.content.strip()

            except OpenAIError as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise

        raise OpenAIError("API call failed after all retries")

    def categorize_step(self, step_data: Dict[str, Any]) -> str:
        """Categorize a step using LLM.
        
        Args:
            step_data: Normalized step data
            
        Returns:
            Category (navigation, interaction, or validation)
        """
        from .prompts import PromptTemplates

        prompt = PromptTemplates.categorize_step(step_data)
        response = self._call_api(prompt)
        
        # Normalize response
        category = response.lower().strip()
        valid_categories = ["navigation", "interaction", "validation"]
        
        if category not in valid_categories:
            logger.warning(f"Invalid category '{category}', defaulting to 'interaction'")
            category = "interaction"

        logger.debug(f"Categorized step as: {category}")
        return category

    def generate_description(self, step_data: Dict[str, Any], category: str) -> str:
        """Generate human-readable description for a step.
        
        Args:
            step_data: Normalized step data
            category: Step category
            
        Returns:
            Human-readable description
        """
        from .prompts import PromptTemplates

        prompt = PromptTemplates.generate_description(step_data, category)
        description = self._call_api(prompt)
        
        logger.debug(f"Generated description: {description[:100]}...")
        return description

    def determine_action(self, step_data: Dict[str, Any]) -> str:
        """Determine the specific action being performed.
        
        Args:
            step_data: Normalized step data
            
        Returns:
            Action verb
        """
        from .prompts import PromptTemplates

        prompt = PromptTemplates.determine_action(step_data)
        action = self._call_api(prompt).lower().strip()
        
        logger.debug(f"Determined action: {action}")
        return action

    def generate_workflow_summary(
        self,
        feature_name: str,
        scenario_name: str,
        steps_summary: list,
    ) -> str:
        """Generate overall workflow summary.
        
        Args:
            feature_name: Feature name
            scenario_name: Scenario name
            steps_summary: List of step summaries
            
        Returns:
            Workflow summary
        """
        from .prompts import PromptTemplates

        prompt = PromptTemplates.generate_workflow_summary(
            feature_name, scenario_name, steps_summary
        )
        summary = self._call_api(prompt)
        
        logger.info(f"Generated workflow summary: {summary[:100]}...")
        return summary

    def generate_input_schema(
        self,
        feature_name: str,
        scenario_name: str,
        step_descriptions: list,
        execution_data: dict,
    ) -> list:
        """Generate input schema from placeholders in test workflow.
        
        Args:
            feature_name: Feature name
            scenario_name: Scenario name
            step_descriptions: List of step descriptions
            execution_data: Execution data with actual values
            
        Returns:
            List of input schema fields
        """
        from .prompts import PromptTemplates

        prompt = PromptTemplates.generate_input_schema(
            feature_name, scenario_name, step_descriptions, execution_data
        )
        response = self._call_api(prompt)
        
        try:
            # Parse JSON response
            schema = json.loads(response)
            if not isinstance(schema, list):
                logger.warning("Input schema response is not a list, returning empty list")
                return []
            logger.info(f"Generated input schema with {len(schema)} parameters")
            return schema
        except json.JSONDecodeError as e:
            logger.warning(f"Failed to parse input schema JSON: {e}")
            return []


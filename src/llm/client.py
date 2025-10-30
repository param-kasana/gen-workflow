"""OpenAI client wrapper for LLM interactions."""

import os
import logging
import json
from typing import Optional, Dict, Any
import time
from dotenv import load_dotenv

from langchain_openai import ChatOpenAI
from langchain.output_parsers import PydanticOutputParser, OutputFixingParser
from langchain.schema import HumanMessage, SystemMessage

# Load environment variables from .env file
load_dotenv()

logger = logging.getLogger(__name__)


class LLMClient:
    """Client for interacting with OpenAI via LangChain."""
    
    # Default configuration
    DEFAULT_MODEL = "gpt-4.1-nano"
    DEFAULT_TEMPERATURE = 0.3

    def __init__(self, api_key: Optional[str] = None, model_name: Optional[str] = None):
        """Initialize LLM client with LangChain ChatOpenAI.
        
        Args:
            api_key: OpenAI API key (defaults to OPENAI_API_KEY from .env)
            model_name: Model name to use (defaults to gpt-4o)
        """
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        if not self.api_key:
            raise ValueError("OpenAI API key not provided. Set OPENAI_API_KEY in .env file.")

        self.model_name = model_name or self.DEFAULT_MODEL
        self.temperature = self.DEFAULT_TEMPERATURE
        
        # Create LangChain ChatOpenAI instance
        self.llm = ChatOpenAI(
            model=self.model_name,
            temperature=self.temperature,
            api_key=self.api_key,
        )

    def _call_api(self, prompt: str, max_retries: int = 3) -> str:
        """Call OpenAI API via LangChain with retry logic.
        
        Args:
            prompt: Prompt to send to the API
            max_retries: Maximum number of retries
            
        Returns:
            Response text from the API
            
        Raises:
            Exception: If API call fails after retries
        """
        system_msg = SystemMessage(
            content="You are a helpful assistant that analyzes test automation steps and provides structured, concise responses."
        )
        human_msg = HumanMessage(content=prompt)
        
        for attempt in range(max_retries):
            try:
                response = self.llm.invoke([system_msg, human_msg])
                return response.content.strip()
                
            except Exception as e:
                logger.warning(f"API call failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)  # Exponential backoff
                else:
                    raise
        
        raise Exception("API call failed after all retries")

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



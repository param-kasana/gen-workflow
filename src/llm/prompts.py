"""Prompt templates for LLM interactions."""

import json
from typing import Dict, Any, List


class PromptTemplates:
    """Collection of prompt templates for various LLM tasks."""

    @staticmethod
    def categorize_step(step_data: Dict[str, Any]) -> str:
        """Generate prompt for step categorization.
        
        Args:
            step_data: Normalized step data
            
        Returns:
            Prompt string
        """
        prompt = f"""Analyze the following test step and categorize it into one of these categories:
- navigation: Steps that navigate to URLs or change pages
- interaction: Steps that interact with UI elements (clicks, typing, selections)
- validation: Steps that validate or verify something (though these might be implicit)

Step Data:
- Type: {step_data.get('type', 'unknown')}
- Description: {step_data.get('description', 'N/A')}
- Element: {step_data.get('element_text', 'N/A')}
- Element Tag: {step_data.get('element_tag', 'N/A')}

Respond with ONLY the category name (navigation, interaction, or validation)."""
        return prompt

    @staticmethod
    def generate_description(step_data: Dict[str, Any], category: str) -> str:
        """Generate prompt for human-readable description.
        
        Args:
            step_data: Normalized step data
            category: Step category
            
        Returns:
            Prompt string
        """
        prompt = f"""Generate a clear, human-readable description for this test step.
The description should be concise (1-2 sentences) and explain what action is being performed.

Step Information:
- Category: {category}
- Type: {step_data.get('type', 'unknown')}
- Original Description: {step_data.get('description', 'N/A')}
- Element Text: {step_data.get('element_text', 'N/A')}
- Element Tag: {step_data.get('element_tag', 'N/A')}

Output Data:
{step_data.get('output', {})}

Provide ONLY the description, no additional text or explanation."""
        return prompt

    @staticmethod
    def generate_workflow_summary(
        feature_name: str,
        scenario_name: str,
        steps_summary: List[Dict[str, str]],
    ) -> str:
        """Generate prompt for workflow summary.
        
        Args:
            feature_name: Feature name
            scenario_name: Scenario name
            steps_summary: List of step summaries
            
        Returns:
            Prompt string
        """
        steps_text = "\n".join([
            f"{i+1}. {step['description']} (Type: {step['type']}, Element: {step.get('element', 'N/A')})"
            for i, step in enumerate(steps_summary)
        ])

        prompt = f"""Generate a comprehensive summary of this test workflow.
The summary should:
1. Explain the overall purpose of the test
2. Describe the main actions performed
3. Mention key validations or checkpoints
4. Be 2-4 sentences long

Feature: {feature_name}
Scenario: {scenario_name}

Steps:
{steps_text}

Provide ONLY the summary, no additional text or headings."""
        return prompt

    @staticmethod
    def generate_input_schema(
        feature_name: str,
        scenario_name: str,
        step_descriptions: List[str],
        execution_data: Dict[str, Any],
    ) -> str:
        """Generate prompt for input schema extraction.
        
        Args:
            feature_name: Feature name
            scenario_name: Scenario name
            step_descriptions: List of step descriptions
            execution_data: Actual execution data with values
            
        Returns:
            Prompt string
        """
        steps_text = "\n".join([f"- {desc}" for desc in step_descriptions])
        
        prompt = f"""Analyze this test workflow and generate an input schema for parameterized values.

Feature: {feature_name}
Scenario: {scenario_name}

Step Descriptions:
{steps_text}

Execution Data (for extracting example values):
{json.dumps(execution_data, indent=2)}

Instructions:
1. Identify parameterizable values in two ways:
   a) Placeholders in angle brackets: <placeholder>, <url>, <phone>, <button>
   b) Quoted values in descriptions: "Explore iPhone 17 Pro", "https://example.com"
   
2. Analyze the context and determine what should be parameterized:
   - URLs, phone models, product names, search queries
   - Button text, link text, element text that varies per test
   - User inputs, form data, credentials
   - Skip generic terms like "button", "link", "click" unless they're specific identifiers

3. For each unique parameter, create a schema entry with:
   - name: meaningful parameter name (e.g., "phone_model", "url", "product_name", "button_text")
   - type: inferred type (string, number, boolean, etc.) - default to "string" if unsure
   - required: true (assume all parameters are required)
   - example: extract actual value from execution data if available
   - description: brief description of what this parameter represents and where it's used

4. Merge similar parameters (e.g., if "iPhone 17 Pro" appears in multiple places, create one "phone_model" parameter)

Return ONLY a valid JSON array of objects. Each object must have: name, type, required, example, description.
If no parameterizable values are found, return an empty array: []

Example output format:
[
  {{
    "name": "url",
    "type": "string",
    "required": true,
    "example": "https://www.telstra.com.au/mobile-phones",
    "description": "URL to navigate to at the start"
  }},
  {{
    "name": "phone_model",
    "type": "string",
    "required": true,
    "example": "iPhone 17 Pro",
    "description": "Phone model to explore"
  }}
]

Respond with ONLY valid JSON array, no additional text."""
        return prompt

    @staticmethod
    def determine_action(step_data: Dict[str, Any]) -> str:
        """Generate prompt to determine the specific action.
        
        Args:
            step_data: Normalized step data
            
        Returns:
            Prompt string
        """
        prompt = f"""Determine the specific action being performed in this step.
Return a single action verb from this list:
- navigate, click, type, select, hover, scroll, wait, verify, check, submit, open, close

If none fit perfectly, choose the closest match.

Step Data:
- Type: {step_data.get('type', 'unknown')}
- Description: {step_data.get('description', 'N/A')}
- Element Text: {step_data.get('element_text', 'N/A')}

Respond with ONLY the action verb, no additional text."""
        return prompt


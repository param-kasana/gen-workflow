"""Prompt templates for LLM interactions."""

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


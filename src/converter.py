"""Main conversion logic for transforming test execution to workflow."""

import logging
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from .parser import TestExecutionParser
from .llm import LLMClient
from .schemas import (
    Workflow,
    WorkflowMetadata,
    InputSchemaField,
    CategorizedStep,
    SelectorInfo,
    ValidationRule,
)

logger = logging.getLogger(__name__)


class TestExecutionConverter:
    """Converter for transforming test execution JSON to workflow JSON."""

    def __init__(
        self,
        llm_client: Optional[LLMClient] = None,
        model_name: Optional[str] = None,
    ):
        """Initialize converter.
        
        Args:
            llm_client: LLM client instance (will create default if not provided)
            model_name: Model name to use (if creating default client)
        """
        if llm_client:
            self.llm_client = llm_client
        else:
            self.llm_client = LLMClient(model_name=model_name)

    def convert(
        self,
        input_file: str,
        verbose: bool = False,
    ) -> Workflow:
        """Convert test execution JSON to workflow.
        
        Args:
            input_file: Path to input test execution JSON
            verbose: Whether to show verbose output
            
        Returns:
            Workflow object
        """
        if verbose:
            logging.basicConfig(level=logging.DEBUG)
        else:
            logging.basicConfig(level=logging.INFO)

        logger.info(f"Starting conversion of {input_file}")

        # Parse input file
        parser = TestExecutionParser(input_file)
        test_execution = parser.load()

        # Extract metadata
        metadata_dict = parser.get_metadata()

        # Process each step
        logger.info(f"Processing {len(test_execution.steps)} steps...")
        categorized_steps = []
        
        for idx, step in enumerate(test_execution.steps, start=1):
            logger.info(f"Processing step {idx}/{len(test_execution.steps)}")
            categorized_step = self._process_step(step, idx, parser)
            categorized_steps.append(categorized_step)

        # Generate workflow summary
        logger.info("Generating workflow summary...")
        steps_summary = parser.get_step_summary()
        summary = self.llm_client.generate_workflow_summary(
            metadata_dict["feature_name"],
            metadata_dict["scenario_name"],
            steps_summary,
        )

        # Generate input schema from placeholders (extract <variables> only)
        logger.info("Extracting input schema from placeholders...")
        input_schema = self._extract_input_schema(test_execution)

        # Create workflow metadata with summary and input schema
        metadata = WorkflowMetadata(
            featureName=metadata_dict["feature_name"],
            scenarioName=metadata_dict["scenario_name"],
            source=Path(input_file).name,
            created_at=datetime.now().isoformat(),
            summary=summary,
            input_schema=input_schema,
        )

        # Create workflow
        workflow = Workflow(
            metadata=metadata,
            steps=categorized_steps,
        )

        logger.info("Conversion complete.")

        return workflow

    def _process_step(
        self,
        step: Any,
        step_id: int,
        parser: TestExecutionParser,
    ) -> CategorizedStep:
        """Process a single step.
        
        Args:
            step: Step object
            step_id: Step ID
            parser: Parser instance
            
        Returns:
            CategorizedStep object
        """
        # Convert selectors
        selectors = None
        if step.selector:
            selectors = [
                SelectorInfo(
                    type=sel.type,
                    value=sel.value,
                    priority=int(sel.priority) if sel.priority else 999,
                )
                for sel in step.selector
            ]

        # Create categorized step keeping original structure
        categorized_step = CategorizedStep(
            id=step_id,
            description=step.description,
            timestamp=step.timestamp,
            output=step.output.model_dump(exclude_none=True) if step.output else None,
            tabId=step.tabId,
            type=step.type,
            force_new_tab=step.force_new_tab,
            elementText=step.elementText,
            elementTag=step.elementTag,
            attributes=step.attributes.model_dump(by_alias=True) if step.attributes else None,
            selector=selectors,
        )

        return categorized_step

    def _extract_input_schema(self, test_execution: Any) -> List[InputSchemaField]:
        """Extract input schema by finding <placeholders> in test execution.
        
        Args:
            test_execution: TestExecution object
            
        Returns:
            List of InputSchemaField objects
        """
        import re
        
        placeholders = {}
        
        # Search for <placeholder> patterns in all text fields
        texts_to_search = [
            test_execution.featureName,
            test_execution.scenarioName,
        ]
        
        # Add step descriptions
        for step in test_execution.steps:
            texts_to_search.append(step.description)
        
        # Pattern to match <variable>
        pattern = r'<([^>]+)>'
        
        # Find all placeholders
        for text in texts_to_search:
            if text:
                matches = re.findall(pattern, text)
                for match in matches:
                    if match not in placeholders:
                        placeholders[match] = {
                            "name": match,
                            "found_in": text
                        }
        
        # Create schema fields by matching with actual data
        schema_fields = []
        
        for placeholder_name, info in placeholders.items():
            example_value = self._find_example_value(
                placeholder_name, 
                test_execution
            )
            
            # Infer type from example value
            param_type = "string"
            if isinstance(example_value, bool):
                param_type = "boolean"
            elif isinstance(example_value, int):
                param_type = "number"
            elif isinstance(example_value, float):
                param_type = "number"
            
            schema_fields.append(
                InputSchemaField(
                    name=placeholder_name,
                    type=param_type,
                    required=True,
                    example=example_value,
                    description=f"Parameter for {placeholder_name}"
                )
            )
        
        logger.info(f"Extracted {len(schema_fields)} parameters from placeholders")
        return schema_fields

    def _find_example_value(self, placeholder_name: str, test_execution: Any) -> Any:
        """Find example value for a placeholder by matching with execution data.
        
        Args:
            placeholder_name: Name of the placeholder (without brackets)
            test_execution: TestExecution object
            
        Returns:
            Example value for the placeholder
        """
        # Map common placeholder names to data
        placeholder_lower = placeholder_name.lower()
        
        # Check for URL
        if placeholder_lower in ['url', 'link', 'website']:
            for step in test_execution.steps:
                if step.output and step.output.url:
                    return step.output.url
        
        # Check for phone/product in element text
        if placeholder_lower in ['phone', 'product', 'model', 'item']:
            for step in test_execution.steps:
                if step.elementText and any(keyword in step.elementText.lower() for keyword in ['iphone', 'samsung', 'pixel']):
                    return step.elementText
        
        # Check for button text
        if placeholder_lower in ['button', 'link', 'text']:
            for step in test_execution.steps:
                if step.elementText:
                    return step.elementText
        
        # Default: return placeholder name as example
        return f"example_{placeholder_name}"

    def save_workflow(self, workflow: Workflow, output_file: str) -> None:
        """Save workflow to JSON file.
        
        Args:
            workflow: Workflow object
            output_file: Path to output file
        """
        import json

        output_path = Path(output_file)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(
                workflow.model_dump(exclude_none=True),
                f,
                indent=2,
                ensure_ascii=False,
            )

        logger.info(f"Workflow saved to {output_file}")


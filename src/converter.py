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

        # Generate input schema from placeholders
        logger.info("Generating input schema...")
        step_descriptions = [step.description for step in test_execution.steps]
        step_descriptions.insert(0, test_execution.featureName)
        step_descriptions.insert(1, test_execution.scenarioName)
        
        # Prepare execution data for example extraction
        execution_data = {
            "feature": test_execution.featureName,
            "scenario": test_execution.scenarioName,
            "steps": [
                {
                    "description": step.description,
                    "elementText": step.elementText,
                    "output": step.output.model_dump(exclude_none=True) if step.output else None,
                }
                for step in test_execution.steps
            ]
        }
        
        input_schema_data = self.llm_client.generate_input_schema(
            metadata_dict["feature_name"],
            metadata_dict["scenario_name"],
            step_descriptions,
            execution_data,
        )
        
        # Convert to InputSchemaField objects
        input_schema = [
            InputSchemaField(**field) for field in input_schema_data
        ] if input_schema_data else []

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


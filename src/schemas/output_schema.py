"""Output schema for workflow JSON files."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field


class InputSchemaField(BaseModel):
    """Input schema field definition."""

    name: str = Field(..., description="Parameter name")
    type: str = Field(..., description="Parameter type (string, number, boolean, etc.)")
    required: bool = Field(..., description="Whether this parameter is required")
    example: Any = Field(..., description="Example value for this parameter")
    description: Optional[str] = Field(None, description="Description of the parameter")


class InputSchemaList(BaseModel):
    """Wrapper for list of input schema fields."""
    
    parameters: List[InputSchemaField] = Field(
        default_factory=list, 
        description="List of input parameters extracted from the workflow"
    )


class WorkflowMetadata(BaseModel):
    """Metadata about the workflow."""

    featureName: str = Field(..., description="Feature name")
    scenarioName: str = Field(..., description="Scenario name")
    source: str = Field(..., description="Source file name")
    created_at: str = Field(..., description="Workflow creation timestamp")
    summary: str = Field(..., description="LLM-generated workflow summary")
    input_schema: List[InputSchemaField] = Field(default_factory=list, description="Input schema for parameterized values")


class SelectorInfo(BaseModel):
    """Selector information with priority."""

    type: str = Field(..., description="Selector type")
    value: str = Field(..., description="Selector value")
    priority: int = Field(..., description="Priority (lower is better)")


class ValidationRule(BaseModel):
    """Validation rule for a step."""

    rule_type: str = Field(..., description="Type of validation (url, status, element, etc.)")
    expected_value: Any = Field(..., description="Expected value")
    actual_value: Optional[Any] = Field(None, description="Actual value observed")
    passed: Optional[bool] = Field(None, description="Whether validation passed")


class CategorizedStep(BaseModel):
    """A workflow step with original test execution data."""

    id: int = Field(..., description="Step ID")
    description: str = Field(..., description="Step description")
    timestamp: float = Field(..., description="Execution timestamp")
    output: Optional[Dict[str, Any]] = Field(None, description="Output from step execution")
    tabId: Optional[str] = Field(None, description="Browser tab ID")
    type: str = Field(..., description="Step type")
    force_new_tab: Optional[bool] = Field(None, description="Whether to force a new tab")
    elementText: Optional[str] = Field(None, description="Text content of the element")
    elementTag: Optional[str] = Field(None, description="HTML tag of the element")
    attributes: Optional[Dict[str, Any]] = Field(None, description="Element attributes")
    selector: Optional[List[SelectorInfo]] = Field(None, description="List of selectors for the element")


class Workflow(BaseModel):
    """Complete workflow schema."""

    metadata: WorkflowMetadata = Field(..., description="Workflow metadata")
    steps: List[CategorizedStep] = Field(..., description="List of categorized steps")


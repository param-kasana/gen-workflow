"""Schema definitions for input and output JSON structures."""

from .input_schema import TestExecution, Step, StepOutput, Selector, StepAttributes
from .output_schema import (
    Workflow,
    WorkflowMetadata,
    InputSchemaField,
    InputSchemaList,
    CategorizedStep,
    SelectorInfo,
    ValidationRule,
)

__all__ = [
    "TestExecution",
    "Step",
    "StepOutput",
    "Selector",
    "StepAttributes",
    "Workflow",
    "WorkflowMetadata",
    "InputSchemaField",
    "InputSchemaList",
    "CategorizedStep",
    "SelectorInfo",
    "ValidationRule",
]


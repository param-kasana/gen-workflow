"""Input schema for test execution JSON files."""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field


class StepOutput(BaseModel):
    """Output data from a navigation step."""

    url: Optional[str] = None
    final_url: Optional[str] = None
    title: Optional[str] = None
    status_code: Optional[int] = None
    ok: Optional[bool] = None


class Selector(BaseModel):
    """Selector information for an element."""

    type: str = Field(..., description="Type of selector (cssSelector, xpath, textSelector, etc.)")
    value: str = Field(..., description="Selector value")
    priority: str = Field(..., description="Priority of this selector")


class StepAttributes(BaseModel):
    """Attributes of an element."""

    class_: Optional[str] = Field(None, alias="class")
    href: Optional[str] = None
    tag: Optional[str] = None
    
    class Config:
        populate_by_name = True


class Step(BaseModel):
    """A single step in the test execution."""

    description: str = Field(..., description="Step description from the test")
    output: Optional[StepOutput] = Field(None, description="Output from step execution")
    timestamp: float = Field(..., description="Unix timestamp of step execution")
    tabId: Optional[str] = Field(None, description="Browser tab ID")
    type: str = Field(..., description="Step type (navigate, select_option, etc.)")
    force_new_tab: Optional[bool] = Field(None, description="Whether to force a new tab")
    
    # Element-specific fields
    elementText: Optional[str] = Field(None, description="Text content of the element")
    elementTag: Optional[str] = Field(None, description="HTML tag of the element")
    attributes: Optional[StepAttributes] = Field(None, description="Element attributes")
    selector: Optional[List[Selector]] = Field(None, description="List of selectors for the element")


class TestExecution(BaseModel):
    """Root schema for test execution JSON."""

    featureName: str = Field(..., description="Name of the feature being tested")
    scenarioName: str = Field(..., description="Name of the test scenario")
    steps: List[Step] = Field(..., description="List of execution steps")


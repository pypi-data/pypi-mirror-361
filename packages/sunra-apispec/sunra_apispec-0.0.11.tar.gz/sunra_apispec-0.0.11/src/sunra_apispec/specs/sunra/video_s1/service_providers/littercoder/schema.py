from typing import Optional, Literal
from pydantic import BaseModel, Field


class LittercoderBaseInput(BaseModel):
    """Base input model for Littercoder API."""
    mode: Optional[str] = Field(
        default="RELAX",
        description="RELAX for slow mode, FAST for fast mode"
    )
    notifyHook: Optional[str] = Field(
        default=None,
        description="Callback URL for notifications"
    )
    state: Optional[str] = Field(
        default=None,
        description="Custom state parameter"
    )


class LittercoderVideoInput(LittercoderBaseInput):
    """Input model for Littercoder video generation endpoint."""
    prompt: str = Field(
        ...,
        description="Text prompt for video generation"
    )
    motion: Literal["low", "high"] = Field(
        ...,
        description="Motion level: low or high"
    )
    base64: str = Field(
        ...,
        description="Base64 encoded first frame image data"
    )


class LittercoderOutput(BaseModel):
    """Output model for Littercoder API responses."""
    code: int = Field(
        ...,
        description="Status code: 1 for success, 22 for queuing, 23 for queue full, 24 for sensitive content, others for errors"
    )
    description: str = Field(
        ...,
        description="Response description"
    )
    result: str = Field(
        ...,
        description="Task ID for the submitted job"
    )

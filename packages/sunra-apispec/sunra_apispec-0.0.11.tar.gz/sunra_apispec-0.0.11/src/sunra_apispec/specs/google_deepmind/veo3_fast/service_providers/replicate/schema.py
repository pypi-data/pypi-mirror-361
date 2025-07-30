from pydantic import BaseModel, Field
from typing import Optional


class Veo3FastInput(BaseModel):
    """Input schema for Veo3-Fast model on Replicate."""
    prompt: str = Field(
        ...,
        description="Text prompt for video generation"
    )
    seed: Optional[int] = Field(
        None,
        description="Random seed. Omit for random generations"
    )


class Veo3FastOutput(BaseModel):
    """Output schema for Veo3-Fast model on Replicate."""
    output: Optional[str] = Field(
        None,
        description="Generated video URL"
    )

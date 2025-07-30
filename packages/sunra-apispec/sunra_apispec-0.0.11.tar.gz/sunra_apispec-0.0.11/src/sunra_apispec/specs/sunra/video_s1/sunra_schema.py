from typing import List, Literal
from pydantic import BaseModel, Field, HttpUrl


class ImageToVideoInput(BaseModel):
    """Input model for image-to-video generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="The text prompt for video generation"
    )

    start_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="URL of the image to use as the first frame"
    )
    
    motion: Literal["low", "high"] = Field(
        default="low",
        json_schema_extra={"x-sr-order": 302},
        description="Motion level: low for low motion, high for high motion"
    )
    
    mode: Literal["slow", "fast"] = Field(
        default="fast",
        json_schema_extra={"x-sr-order": 101},
        description="Generation mode: slow for higher quality, fast for quicker results"
    )

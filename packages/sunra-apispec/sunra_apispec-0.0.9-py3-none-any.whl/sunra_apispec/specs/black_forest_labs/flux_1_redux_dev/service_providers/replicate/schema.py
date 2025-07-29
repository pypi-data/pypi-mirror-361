from typing import Literal, Optional, List
from pydantic import BaseModel, Field
from enum import Enum


class MegapixelsEnum(str, Enum):
    """Enum for megapixels options."""
    ONE = "1"
    QUARTER = "0.25"


class OutputFormatEnum(str, Enum):
    """Enum for output format options."""
    WEBP = "webp"
    JPG = "jpg"
    PNG = "png"


class ReplicateInput(BaseModel):
    """Input model for Replicate FLUX.1-Redux-Dev API."""
    redux_image: str = Field(
        ...,
        description="Input image to condition your output on. This replaces prompt for FLUX.1 Redux models"
    )
    aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21", "3:2", "2:3", "4:5", "5:4", "3:4", "4:3"] = Field(
        "1:1",
        description="Aspect ratio for the generated image"
    )
    num_outputs: int = Field(
        default=1,
        ge=1,
        le=4,
        description="Number of outputs to generate"
    )
    num_inference_steps: int = Field(
        default=28,
        ge=1,
        le=50,
        description="Number of denoising steps. Recommended range is 28-50"
    )
    guidance: float = Field(
        default=3,
        ge=0,
        le=10,
        description="Guidance for generated image"
    )
    seed: Optional[int] = Field(
        default=None,
        description="Random seed. Set for reproducible generation"
    )
    output_format: OutputFormatEnum = Field(
        default=OutputFormatEnum.WEBP,
        description="Format of the output images"
    )
    output_quality: int = Field(
        default=80,
        ge=0,
        le=100,
        description="Quality when saving the output images, from 0 to 100. 100 is best quality, 0 is lowest quality. Not relevant for .png outputs"
    )
    disable_safety_checker: bool = Field(
        default=False,
        description="Disable safety checker for generated images."
    )
    megapixels: MegapixelsEnum = Field(
        default=MegapixelsEnum.ONE,
        description="Approximate number of megapixels for generated image"
    )


class ReplicateOutput(BaseModel):
    """Output model for Replicate FLUX.1-Redux-Dev API."""
    output: List[str] = Field(
        ...,
        description="List of generated image URLs"
    )
    
# Schema for Text-to-Image generation
from pydantic import BaseModel, Field, HttpUrl
from typing import Literal


class BaseInput(BaseModel):
    """Input model for text-to-image generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 200},
        description="Text prompt for image generation.",
    )
    prompt_enhancer: bool = Field(
        default=False,
        json_schema_extra={"x-sr-order": 201},
        description="Whether to perform enhancer on the prompt. If active, automatically modifies the prompt for more creative generation."
    )
    seed: int = Field(
        default=None,
        ge=0,
        le=2147483647,
        json_schema_extra={"x-sr-order": 202},
        description="Seed for reproducibility.",
    )
    # aspect_ratio: Literal["1:1", "16:9", "9:16", "4:3", "3:4", "21:9", "9:21", "custom"] = Field(
    #     default="16:9",
    #     json_schema_extra={"x-sr-order": 401},
    #     description="Aspect ratio of the image between 21:9 and 9:21. If 'custom', you must specify width and height."
    # )
    width: int = Field(
        default=1024,
        ge=256,
        le=1440,
        multiple_of=32,
        json_schema_extra={"x-sr-order": 402},
        description="Width of the generated image in pixels. Must be a multiple of 32."
    )
    height: int = Field(
        default=768,
        ge=256,
        le=1440,
        multiple_of=32,
        json_schema_extra={"x-sr-order": 403},
        description="Height of the generated image in pixels. Must be a multiple of 32."
    )
    output_format: Literal["jpeg", "png"] = Field(
        default="jpeg",
        json_schema_extra={"x-sr-order": 404},
        description="Output format for the generated image. Can be 'jpeg' or 'png'."
    )
    safety_tolerance: int = Field(
        default=40,
        ge=0,
        le=100,
        multiple_of=1,
        json_schema_extra={"x-sr-order": 500},
        description="Tolerance level for input and output moderation. Between 0 and 100, 0 being most strict, 100 being no moderation.",
    )


class TextToImageInput(BaseInput):
    """Input model for text-to-image generation."""
    pass


class ImageToImageInput(BaseInput):
    """Input model for image-to-image generation."""
    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Image URL to use with Flux Redux."
    )

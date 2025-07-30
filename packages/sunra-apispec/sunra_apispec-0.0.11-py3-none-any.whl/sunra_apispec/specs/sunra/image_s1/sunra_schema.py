from typing import List, Literal
from pydantic import BaseModel, Field, HttpUrl
from sunra_apispec.base.output_schema import SunraFile


class TextToImageInput(BaseModel):
    """Input model for text-to-image generation."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="The text prompt for image generation"
    )
    
    mode: Literal["slow", "fast"] = Field(
        default="fast",
        json_schema_extra={"x-sr-order": 101},
        description="Generation mode: slow for higher quality, fast for quicker results"
    )


class ImageBlendingInput(BaseModel):
    """Input model for image blending."""
    images: List[HttpUrl | str] = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Array of image URLs to blend together"
    )
    
    mode: Literal["slow", "fast"] = Field(
        default="fast",
        json_schema_extra={"x-sr-order": 101},
        description="Generation mode: slow for higher quality, fast for quicker results"
    )
    
    aspect_ratio: Literal["2:3", "3:2", "1:1"] = Field(
        default="1:1",
        json_schema_extra={"x-sr-order": 401},
        description="Aspect ratio for the blended image"
    )


class FaceSwapInput(BaseModel):
    """Input model for face swap."""
    face_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Source face image URL"
    )
    
    target_image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 302},
        description="Target image URL where the face will be swapped"
    )
    


class ImageEditingInput(BaseModel):
    """Input model for image editing."""
    prompt: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 201},
        description="Text prompt describing the desired edits"
    )
    
    image: HttpUrl | str = Field(
        ...,
        json_schema_extra={"x-sr-order": 301},
        description="Source image URL to be edited"
    )
    
    mode: Literal["slow", "fast"] = Field(
        default="fast",
        json_schema_extra={"x-sr-order": 101},
        description="Generation mode: slow for higher quality, fast for quicker results"
    )
    
    mask_image: HttpUrl | str = Field(
        default=None,
        json_schema_extra={"x-sr-order": 302},
        description="Optional mask image URL for selective editing"
    )


class ImageActionInput(BaseModel):
    task_id: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 101},
        description="Task ID from the last image generation result which needs to be processed"
    )
    custom_id: str = Field(
        ...,
        json_schema_extra={"x-sr-order": 102},
        description="The custom ID of the action to be performed on the image"
    )


class ImageS1OutputActionItem(BaseModel):
    task_id: str
    custom_id: str
    label: str
    

class ImageS1ImageOutputItem(SunraFile):
    actions: List[ImageS1OutputActionItem]


class ImageS1Output(BaseModel):
    images: List[ImageS1ImageOutputItem]

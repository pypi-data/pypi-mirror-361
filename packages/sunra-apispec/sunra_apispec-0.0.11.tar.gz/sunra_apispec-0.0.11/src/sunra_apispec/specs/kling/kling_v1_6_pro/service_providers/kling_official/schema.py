"""
Schema definitions for Kling v1.6 Pro Official API.
"""

from typing import Optional, Literal, List, Dict, Any
from pydantic import BaseModel, Field


class KlingTextToVideoInput(BaseModel):
    """Input schema for Kling v1.6 Pro Text-to-Video generation."""
    
    model_name: Optional[str] = Field(
        "kling-v1-6", 
        description="Model name"
    )
    prompt: str = Field(
        ..., 
        max_length=2500,
        description="Positive text prompt"
    )
    negative_prompt: Optional[str] = Field(
        None, 
        max_length=2500,
        description="Negative text prompt"
    )
    cfg_scale: Optional[float] = Field(
        0.5, 
        ge=0.0, 
        le=1.0,
        description="CFG scale for guidance"
    )
    mode: Optional[Literal["std", "pro"]] = Field(
        "pro", 
        description="Video generation mode"
    )
    aspect_ratio: Optional[Literal["16:9", "9:16", "1:1"]] = Field(
        "16:9", 
        description="Aspect ratio of the generated video"
    )
    duration: Optional[Literal["5", "10"]] = Field(
        "5", 
        description="Video duration in seconds"
    )
    callback_url: Optional[str] = Field(
        None, 
        description="Callback URL for task completion notification"
    )
    external_task_id: Optional[str] = Field(
        None, 
        description="External task ID for tracking"
    )


class KlingImageToVideoInput(BaseModel):
    """Input schema for Kling v1.6 Pro Image-to-Video generation."""
    
    model_name: Optional[str] = Field(
        "kling-v1-6", 
        description="Model name"
    )
    image: str = Field(
        ..., 
        description="Reference image URL or base64 encoded image"
    )
    image_tail: Optional[str] = Field(
        None, 
        description="Reference image for end frame control"
    )
    prompt: Optional[str] = Field(
        None, 
        max_length=2500,
        description="Positive text prompt"
    )
    negative_prompt: Optional[str] = Field(
        None, 
        max_length=2500,
        description="Negative text prompt"
    )
    cfg_scale: Optional[float] = Field(
        0.5, 
        ge=0.0, 
        le=1.0,
        description="CFG scale for guidance"
    )
    mode: Optional[Literal["std", "pro"]] = Field(
        "pro", 
        description="Video generation mode"
    )
    duration: Optional[Literal["5", "10"]] = Field(
        "5", 
        description="Video duration in seconds"
    )
    callback_url: Optional[str] = Field(
        None, 
        description="Callback URL for task completion notification"
    )
    external_task_id: Optional[str] = Field(
        None, 
        description="External task ID for tracking"
    )


class KlingReferenceImagesToVideoInput(BaseModel):
    """Input schema for Kling v1.6 Pro Reference Images-to-Video generation."""
    
    model_name: Optional[str] = Field(
        "kling-v1-6", 
        description="Model name"
    )
    image_list: List[Dict[str, str]] = Field(
        ..., 
        min_length=1,
        max_length=4,
        description="Reference image list (up to 4 images)"
    )
    prompt: Optional[str] = Field(
        None, 
        max_length=2500,
        description="Positive text prompt"
    )
    negative_prompt: Optional[str] = Field(
        None, 
        max_length=2500,
        description="Negative text prompt"
    )
    mode: Optional[Literal["std", "pro"]] = Field(
        "pro", 
        description="Video generation mode"
    )
    duration: Optional[Literal["5", "10"]] = Field(
        "5", 
        description="Video duration in seconds"
    )
    aspect_ratio: Optional[Literal["16:9", "9:16", "1:1"]] = Field(
        "16:9", 
        description="Aspect ratio of the generated video"
    )
    callback_url: Optional[str] = Field(
        None, 
        description="Callback URL for task completion notification"
    )
    external_task_id: Optional[str] = Field(
        None, 
        description="External task ID for tracking"
    )


class KlingVideoOutput(BaseModel):
    """Output schema for Kling video generation."""
    
    id: str = Field(..., description="Generated video ID")
    url: str = Field(..., description="URL for the generated video")
    duration: str = Field(..., description="Total video duration in seconds")


class KlingTaskResult(BaseModel):
    """Task result schema for Kling API response."""
    
    videos: List[KlingVideoOutput] = Field(..., description="List of generated videos")


class KlingApiResponse(BaseModel):
    """Complete API response schema for Kling."""
    
    code: int = Field(..., description="Response code")
    message: str = Field(..., description="Response message")
    request_id: str = Field(..., description="Request ID")
    data: Dict[str, Any] = Field(..., description="Response data") 
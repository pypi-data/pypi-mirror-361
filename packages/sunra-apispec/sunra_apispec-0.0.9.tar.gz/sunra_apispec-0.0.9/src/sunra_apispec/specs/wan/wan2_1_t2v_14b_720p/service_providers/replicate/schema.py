from typing import Literal, Optional
from pydantic import BaseModel, Field


class ReplicateInput(BaseModel):
    """Input model for Replicate Wan 2.1 T2V 14B 720p API."""
    
    prompt: str = Field(
        ...,
        description="Prompt for video generation"
    )
    
    seed: Optional[int] = Field(
        default=None,
        description="Random seed. Leave blank for random"
    )
    
    fast_mode: Literal["Off", "Balanced", "Fast"] = Field(
        default="Balanced",
        description="Speed up generation with different levels of acceleration. Faster modes may degrade quality somewhat."
    )
    
    lora_scale: float = Field(
        default=1,
        description="Determines how strongly the main LoRA should be applied."
    )
    
    num_frames: int = Field(
        default=81,
        ge=81,
        le=100,
        description="Number of video frames. 81 frames give the best results"
    )
    
    aspect_ratio: Literal["16:9", "9:16", "1:1"] = Field(
        default="16:9",
        description="Aspect ratio of video. 16:9 corresponds to 1280x720px, 9:16 is 720x1280px, and 1:1 is 1024x1024px"
    )
    
    lora_weights: Optional[str] = Field(
        default=None,
        description="Load LoRA weights. Supports Replicate models, HuggingFace URLs, CivitAI URLs, or arbitrary .safetensors URLs."
    )
    
    sample_shift: float = Field(
        default=5,
        ge=1,
        le=10,
        description="Sample shift factor"
    )
    
    sample_steps: int = Field(
        default=30,
        ge=1,
        le=40,
        description="Number of generation steps. Fewer steps means faster generation, at the expensive of output quality."
    )
    
    frames_per_second: int = Field(
        default=16,
        ge=5,
        le=24,
        description="Frames per second. Note that the pricing of this model is based on the video duration at 16 fps"
    )
    
    sample_guide_scale: float = Field(
        default=5,
        ge=0,
        le=10,
        description="Higher guide scale makes prompt adherence better, but can reduce variation"
    )

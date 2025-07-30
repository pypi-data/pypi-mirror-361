from pydantic import BaseModel, Field

class TextToVideoInput(BaseModel):
    """Input model for text-to-video generation."""
    prompt: str = Field(...,
        json_schema_extra={"x-sr-order": 201},
        description='Text prompt for video generation'
    )

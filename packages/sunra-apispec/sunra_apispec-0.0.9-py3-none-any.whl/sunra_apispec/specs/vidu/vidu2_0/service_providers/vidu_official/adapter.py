"""
Adapter for Vidu Official Vidu2.0 API service provider.
Converts Sunra schema to Vidu Official API format.
"""

from typing import Callable
from sunra_apispec.base.adapter_interface import IViduAdapter
from sunra_apispec.base.output_schema import VideoOutput, SunraFile
from ...sunra_schema import ImageToVideoInput, ReferenceImagesToVideoInput
from .schema import (
    ViduImageToVideoInput, 
    ViduReferenceImagesToVideoInput,
    ViduStartEndToVideoInput,
    ModelEnum,
)


class ViduImageToVideoAdapter(IViduAdapter):
    """Adapter for image-to-video generation using Vidu Official API."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ImageToVideoInput to Vidu Official ImageToVideoInput or StartEndToVideoInput format."""
        input_model = ImageToVideoInput.model_validate(data)
            
        # Check if both start_image and end_image are provided
        if input_model.start_image and input_model.end_image:
            # Use StartEndToVideoInput format
            vidu_input = ViduStartEndToVideoInput(
                model=ModelEnum.VIDU2_0.value,
                prompt=input_model.prompt,
                images=[input_model.start_image, input_model.end_image],
                duration=input_model.duration,
                resolution=input_model.resolution,
                movement_amplitude=input_model.movement_amplitude,
                seed=input_model.seed,
            )
            self.request_mode = "start_end_to_video"
        else:
            # Use ImageToVideoInput format
            vidu_input = ViduImageToVideoInput(
                model=ModelEnum.VIDU2_0.value,
                prompt=input_model.prompt,
                images=[input_model.start_image],
                duration=input_model.duration,
                resolution=input_model.resolution,
                movement_amplitude=input_model.movement_amplitude,
                seed=input_model.seed,
            )
            self.request_mode = "image_to_video"

        return vidu_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Get the Vidu Official API endpoint URL for image-to-video."""
        if self.request_mode == "start_end_to_video":
            return "https://api.vidu.com/ent/v2/start-end2video"
        elif self.request_mode == "image_to_video":
            return "https://api.vidu.com/ent/v2/img2video"
        else:
            raise ValueError(f"Invalid request mode: {self.request_mode}")

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Vidu output to Sunra VideoOutput format."""
        video_url = data["creations"][0]["url"]
        sunra_file = processURLMiddleware(video_url)
        return VideoOutput(video=sunra_file).model_dump(exclude_none=True, by_alias=True)
    

class ViduReferenceImagesToVideoAdapter(IViduAdapter):
    """Adapter for reference-images-to-video generation using Vidu Official API."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ReferenceImagesToVideoInput to Vidu Official ReferenceImagesToVideoInput format."""
        input_model = ReferenceImagesToVideoInput.model_validate(data)
            
        vidu_input = ViduReferenceImagesToVideoInput(
            model=ModelEnum.VIDU2_0.value,
            prompt=input_model.prompt,
            images=[img for img in input_model.reference_images],
            aspect_ratio=input_model.aspect_ratio,
            resolution="720p",
            duration=4,
            movement_amplitude=input_model.movement_amplitude,
            seed=input_model.seed,
        )
        
        return vidu_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_request_url(self) -> str:
        """Get the Vidu Official API endpoint URL for reference-images-to-video."""
        return "https://api.vidu.com/ent/v2/reference2video" 

    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Vidu output to Sunra VideoOutput format."""
        video_url = data["creations"][0]["url"]
        sunra_file = processURLMiddleware(video_url)
        return VideoOutput(video=sunra_file).model_dump(exclude_none=True, by_alias=True)

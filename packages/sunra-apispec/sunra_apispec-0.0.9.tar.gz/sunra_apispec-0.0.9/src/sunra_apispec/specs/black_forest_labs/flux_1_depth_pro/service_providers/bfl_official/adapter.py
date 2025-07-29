"""
Adapter for Black Forest Labs Official FLUX 1.0 Depth Pro API service provider.
Converts Sunra schema to BFL Official API format.
"""

import base64
from typing import Callable
import requests
from sunra_apispec.base.adapter_interface import IBlackForestLabsAdapter
from sunra_apispec.base.output_schema import ImagesOutput, SunraFile
from ...sunra_schema import ImageToImageInput
from .schema import BFLFluxV1DepthProInput, OutputFormat


def map_safety_tolerance(sunra_tolerance: int) -> int:
    """
    Map Sunra safety_tolerance (0-100) to BFL API safety_tolerance (0-6).
    
    Args:
        sunra_tolerance: Safety tolerance value from Sunra schema (0-100)
        
    Returns:
        Mapped safety tolerance value for BFL API (0-6)
    """
    # Linear mapping from 0-100 to 0-6
    # 0-16 -> 0, 17-33 -> 1, 34-50 -> 2, 51-66 -> 3, 67-83 -> 4, 84-100 -> 5, 100 -> 6
    if sunra_tolerance == 100:
        return 6
    return min(int(sunra_tolerance * 6 / 100), 6)


class BFLFluxV1DepthProImageToImageAdapter(IBlackForestLabsAdapter):
    """Adapter for FLUX 1.0 Depth Pro image-to-image generation using BFL Official API."""
    
    def convert_input(self, data) -> dict:
        """Convert Sunra ImageToImageInput to BFL Official BFLFluxV1DepthProInput format."""
        input_model = ImageToImageInput.model_validate(data)
        
        bfl_input = BFLFluxV1DepthProInput(
            prompt=input_model.prompt,
            control_image=self._convert_image_to_base64(input_model.control_image),
            preprocessed_image=self._convert_image_to_base64(input_model.preprocessed_image) if input_model.preprocessed_image else None,
            prompt_upsampling=input_model.prompt_enhancer,
            seed=input_model.seed,
            steps=input_model.number_of_steps,
            output_format=OutputFormat.JPEG if input_model.output_format == "jpeg" else OutputFormat.PNG,
            guidance=input_model.guidance_scale,
            safety_tolerance=map_safety_tolerance(input_model.safety_tolerance),
        )
        
        return bfl_input.model_dump(exclude_none=True, by_alias=True)
    
    def get_bfl_model(self) -> str:
        """Get the BFL model identifier for FLUX 1.0 Depth Pro."""
        return "flux-pro-1.0-depth" 
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert BFL Official output to Sunra output format."""
        sunra_file = processURLMiddleware(data["result"]["sample"])
        return ImagesOutput(
            images=[sunra_file]
        ).model_dump(exclude_none=True, by_alias=True)
    
    def _convert_image_to_base64(self, image: str) -> str:
        """Convert image URL or base64 string to base64 encoded string.
        
        Args:
            image: Either a HTTP URL or base64 encoded string
        
        Returns:
            Base64 encoded string of the image
        
        Raises:
            ValueError: If input is invalid or image cannot be fetched
        """
        if isinstance(image, str) and image.startswith(('http')):
            try:
                # Fetch image from URL
                response = requests.get(image)
                response.raise_for_status()

                # Encode binary data to base64
                base64_data = base64.b64encode(response.content).decode('utf-8')
                return base64_data
            except Exception as e:
                raise ValueError(f"Failed to fetch image from URL: {e}")
        elif isinstance(image, str) and image.startswith(('data:image')):
            return image.split(',')[1]
        else: 
            raise ValueError("Input must be either HttpUrl or base64 string")

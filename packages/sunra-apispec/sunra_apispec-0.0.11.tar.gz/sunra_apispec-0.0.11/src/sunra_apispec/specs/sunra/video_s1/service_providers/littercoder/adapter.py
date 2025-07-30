import base64
import requests
from typing import Callable
from sunra_apispec.base.adapter_interface import ILittercoderAdapter
from sunra_apispec.base.output_schema import VideosOutput, SunraFile
from ...sunra_schema import ImageToVideoInput
from .schema import LittercoderVideoInput


class LittercoderImageToVideoAdapter(ILittercoderAdapter):
    """Adapter for image-to-video generation using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra ImageToVideoInput to Littercoder format."""
        input_model = ImageToVideoInput.model_validate(data)
        
        # Convert image URL to base64
        image_base64 = convert_image_to_base64_with_header(str(input_model.start_image))
        
        littercoder_input = LittercoderVideoInput(
            mode=map_mode(input_model.mode),
            prompt=input_model.prompt,
            motion=input_model.motion,
            base64=image_base64
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for video generation."""
        return "/video-s1/submit/video"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for video generation status."""
        return f"/video-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra VideoOutput format."""
        video_urls = data.get("videoUrls")  # Littercoder return videoUrls
        
        # Process the video URL through the middleware
        video_files = [processURLMiddleware(video_url["url"]) for video_url in video_urls]
        
        return VideosOutput(videos=video_files).model_dump(exclude_none=True)


def convert_image_to_base64_with_header(image: str) -> str:
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
            
            content_type = response.headers.get('content-type', 'image/jpeg')

            # Encode binary data to base64
            base64_data = base64.b64encode(response.content).decode('utf-8')
            
            return f"data:{content_type};base64,{base64_data}"
        except Exception as e:
            raise ValueError(f"Failed to fetch image from URL: {e}")
    elif isinstance(image, str) and image.startswith(('data:image')):
        return image
    else: 
        raise ValueError("Input must be either HttpUrl or base64 string")


def map_mode(sunra_mode: str) -> str:
    """Map Sunra mode to Littercoder mode."""
    mode_mapping = {
        "slow": "RELAX",
        "fast": "FAST"
    }
    return mode_mapping.get(sunra_mode, "FAST") 



def get_littercoder_headers() -> dict:
    """Get headers for Littercoder API request."""
    return {
       "Host": "cdn.midjourney.com",
        "User-Agent": (
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
            "(KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36"
        ),
        "Referer": "https://www.midjourney.com/",
        "Origin": "https://www.midjourney.com",
    }
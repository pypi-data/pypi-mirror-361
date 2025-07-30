import base64
import json
import requests
from typing import Callable, List
import io
from sunra_apispec.base.adapter_interface import ILittercoderAdapter
from sunra_apispec.base.output_schema import SunraFile
from ...sunra_schema import (
  TextToImageInput, 
  ImageBlendingInput, 
  FaceSwapInput, 
  ImageEditingInput, 
  ImageS1Output, 
  ImageS1ImageOutputItem,
  ImageS1OutputActionItem,
  ImageActionInput,
)
from .schema import (
    LittercoderImagineInput, 
    LittercoderBlendInput, 
    LittercoderFaceSwapInput, 
    LittercoderEditInput,
    LittercoderActionInput,
)


class LittercoderTextToImageAdapter(ILittercoderAdapter):
    """Adapter for text-to-image generation using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra TextToImageInput to Littercoder format."""
        input_model = TextToImageInput.model_validate(data)
        
        littercoder_input = LittercoderImagineInput(
            mode=map_mode(input_model.mode),
            prompt=input_model.prompt
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for text-to-image."""
        return "/image-s1/submit/imagine"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for text-to-image status."""
        return f"/image-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra ImagesOutput format."""
        return process_image_output_data(data, processURLMiddleware)


class LittercoderImageBlendingAdapter(ILittercoderAdapter):
    """Adapter for image blending using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra ImageBlendingInput to Littercoder format."""
        input_model = ImageBlendingInput.model_validate(data)
        
        # Convert image URLs to base64
        base64_images = [convert_image_to_base64_with_header(str(img)) for img in input_model.images]
        
        # Map aspect ratio
        dimensions_mapping = {
            "2:3": "PORTRAIT",
            "1:1": "SQUARE", 
            "3:2": "LANDSCAPE"
        }
        dimensions = dimensions_mapping.get(input_model.aspect_ratio, "SQUARE")
        
        littercoder_input = LittercoderBlendInput(
            mode=map_mode(input_model.mode),
            base64Array=base64_images,
            dimensions=dimensions
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for image blending."""
        return "/image-s1/submit/blend"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for image blending status."""
        return f"/image-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra ImagesOutput format."""
        return process_image_output_data(data, processURLMiddleware)


class LittercoderFaceSwapAdapter(ILittercoderAdapter):
    """Adapter for face swap using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra FaceSwapInput to Littercoder format."""
        input_model = FaceSwapInput.model_validate(data)
        
        # Convert image URLs to base64
        source_base64 = convert_image_to_base64_with_header(str(input_model.face_image))
        target_base64 = convert_image_to_base64_with_header(str(input_model.target_image))
        
        littercoder_input = LittercoderFaceSwapInput(
            mode="FAST", # Littercoder only supports fast mode for face swap
            sourceBase64=source_base64,
            targetBase64=target_base64
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for face swap."""
        return "/image-s1/insight-face/swap"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for face swap status."""
        return f"/image-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra ImageS1Output format."""
        return process_face_swap_output_data(data, processURLMiddleware)


class LittercoderImageEditingAdapter(ILittercoderAdapter):
    """Adapter for image editing using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra ImageEditingInput to Littercoder format."""
        input_model = ImageEditingInput.model_validate(data)
        
        # Convert image URLs to base64
        image_base64 = convert_image_to_base64_with_header(str(input_model.image))
        mask_base64 = None
        if input_model.mask_image:
            mask_base64 = convert_image_to_base64_with_header(str(input_model.mask_image))
        
        littercoder_input = LittercoderEditInput(
            mode=map_mode(input_model.mode),
            prompt=input_model.prompt,
            imageBase64=image_base64,
            maskBase64=mask_base64
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for image editing."""
        return "/image-s1/submit/edit"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for image editing status."""
        return f"/image-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra ImagesOutput format."""
        return process_image_editing_output_data(data, processURLMiddleware)
    

class LittercoderImageActionAdapter(ILittercoderAdapter):
    """Adapter for image action using Littercoder."""
    
    def convert_input(self, data) -> dict:
        """Convert from Sunra ImageActionInput to Littercoder format."""
        input_model = ImageActionInput.model_validate(data)
        
        littercoder_input = LittercoderActionInput(
            customId=input_model.custom_id,
            taskId=input_model.task_id,
        )
        
        return littercoder_input.model_dump(exclude_none=True)
    
    def get_request_endpoint(self) -> str:
        """Return the Littercoder endpoint for image action."""
        return "/image-s1/submit/action"
    
    def get_status_endpoint(self, task_id: str) -> str:
        """Return the Littercoder endpoint for image action status."""
        return f"/image-s1/task/{task_id}/fetch"
    
    def convert_output(self, data, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
        """Convert Littercoder output to Sunra ImagesOutput format."""
        return process_action_output_data(data, processURLMiddleware)


def split_image_into_quadrants(image_url: str) -> List[str]:
    """Split an image from URL into four quadrants and return base64 encoded images.
    
    Args:
        image_url: URL of the image to split
        
    Returns:
        List of base64 encoded images (4 quadrants)
        
    Raises:
        ValueError: If image cannot be fetched or processed
    """
    from PIL import Image

    try:
        # Download the image
        response = requests.get(image_url)
        response.raise_for_status()
        
        # Open image with PIL
        img = Image.open(io.BytesIO(response.content))
        
        # Get image dimensions
        width, height = img.size
        
        # Calculate quadrant dimensions
        half_width = width // 2
        half_height = height // 2
        
        # Split into 4 quadrants
        quadrants = []
        
        # Top-left quadrant
        quadrant_1 = img.crop((0, 0, half_width, half_height))
        
        # Top-right quadrant
        quadrant_2 = img.crop((half_width, 0, width, half_height))
        
        # Bottom-left quadrant
        quadrant_3 = img.crop((0, half_height, half_width, height))
        
        # Bottom-right quadrant
        quadrant_4 = img.crop((half_width, half_height, width, height))
        
        # Convert each quadrant to base64
        for i, quadrant in enumerate([quadrant_1, quadrant_2, quadrant_3, quadrant_4], 1):
            # Convert to bytes
            img_byte_arr = io.BytesIO()
            quadrant.save(img_byte_arr, format='JPEG')
            img_byte_arr.seek(0)
            
            # Encode to base64
            quadrant_base64 = base64.b64encode(img_byte_arr.getvalue()).decode('utf-8')
            quadrants.append(f"data:image/jpeg;base64,{quadrant_base64}")
        
        return quadrants
        
    except Exception as e:
        raise ValueError(f"Failed to split image into quadrants: {str(e)}")


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
    return mode_mapping.get(sunra_mode, "RELAX")



def process_image_output_data(data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
    image_url = data.get("imageUrl")
    task_id: str = data.get("id")
    buttons = data.get("buttons", [])

    action_maps = [[], [], [], []] # Initialize action maps for each quadrant
    split_images = split_image_into_quadrants(image_url)
    image_files = [processURLMiddleware(image) for image in split_images]

    for button in buttons:
        custom_id: str = button.get("customId")
        label: str = button.get("label")

        if label.startswith("U") and len(label) == 2:  # U1, U2, U3, U4
            quadrant_num = int(label[1])
            action_maps[quadrant_num - 1].append(
                ImageS1OutputActionItem(
                    task_id=task_id,
                    custom_id=custom_id,
                    label="Upsample"
                )
            )
        elif label.startswith("V") and len(label) == 2:  # V1, V2, V3, V4
            quadrant_num = int(label[1])
            action_maps[quadrant_num - 1].append(
                ImageS1OutputActionItem(
                    task_id=task_id,
                    custom_id=custom_id,
                    label="Variation"
                )
            )
        elif "reroll" in custom_id.lower():
            for i in range(4):
                action_maps[i].append(
                    ImageS1OutputActionItem(
                        task_id=task_id,
                        custom_id=custom_id,
                        label="Reroll"
                    )
                )

    images = []
    for image_file, actions in zip(image_files, action_maps):
        image_item = ImageS1ImageOutputItem(
            **image_file.model_dump(exclude_none=True),
            actions=actions
        )
        images.append(image_item)
    
    return ImageS1Output(images=images).model_dump(exclude_none=True)


def process_face_swap_output_data(data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
    """Process face swap output data and convert to Sunra format.
    
    Args:
        data: Raw output data from Littercoder API containing image info and buttons
        processURLMiddleware: Function to convert URL to SunraFile
        
    Returns:
        Dict in ImageS1Output format
    """
    image_url = data.get("imageUrl")
    image_file = processURLMiddleware(image_url)
    
    image_item = ImageS1ImageOutputItem(
        **image_file.model_dump(exclude_none=True),
        actions=[]
    )
    
    return ImageS1Output(images=[image_item]).model_dump(exclude_none=True)


def process_image_editing_output_data(data: dict, processURLMiddleware: Callable[[str], SunraFile]) -> dict:
    """Process image editing output data and convert to Sunra format.
    
    Args:
        data: Raw output data from Littercoder API containing image info and buttons
        processURLMiddleware: Function to convert URL to SunraFile
        
    Returns:
        Dict in ImageS1Output format
    """
    image_url = data.get("imageUrl")

    split_images = split_image_into_quadrants(image_url)
    image_files = [processURLMiddleware(image) for image in split_images]

    images = []
    for image_file in image_files:
        image_item = ImageS1ImageOutputItem(
            **image_file.model_dump(exclude_none=True),
            actions=[]
        )
        images.append(image_item)
    
    return ImageS1Output(images=images).model_dump(exclude_none=True)


def process_action_output_data(data: dict, processURLMiddleware: Callable[[str], SunraFile], split_image: bool = False) -> dict:
    """Process image generation output data and convert to Sunra format.
    
    Args:
        data: Raw output data from Littercoder API containing image info and buttons
        processURLMiddleware: Function to convert URL to SunraFile
        
    Returns:
        Dict in ImageS1Output format
    """
    # Process the main image URL
    image_url = data.get("imageUrl")
    task_id: str = data.get("id")
    buttons = data.get("buttons", [])

    if buttons == []:
        image_file = processURLMiddleware(image_url)
        
        image_item = ImageS1ImageOutputItem(
            **image_file.model_dump(exclude_none=True),
            actions=[]
        )
        
        return ImageS1Output(images=[image_item]).model_dump(exclude_none=True)
    
    elif "U1" in json.dumps(buttons) and "V1" in json.dumps(buttons):
        return process_image_output_data(data, processURLMiddleware)
    else:
        actions = []
        for button in buttons:
            custom_id: str = button.get("customId")
            if "bookmark" in custom_id.lower():
                continue

            label: str = button.get("label", "")
            if label == "":
                label = button.get("emoji", "")
            
            if custom_id and label:
                actions.append(ImageS1OutputActionItem(
                    task_id=task_id,
                    custom_id=custom_id,
                    label=label
                ))

        image_file = processURLMiddleware(image_url)
        image_item = ImageS1ImageOutputItem(
            **image_file.model_dump(exclude_none=True),
            actions=actions
        )
        
        return ImageS1Output(images=[image_item]).model_dump(exclude_none=True)

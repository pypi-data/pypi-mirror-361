import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ImagesOutput
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from .sunra_schema import TextToImageInput, ImageToImageInput
from .service_providers.fal.adapter import FalTextToImageAdapter, FalImageToImageAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Recraft V3 API",
    description="API for Recraft V3 image generation model - A high-quality text-to-image and image-to-image generation model with various artistic styles and customization options.",
    version="1.0.0",
    output_schema=ImagesOutput,
)

@service.app.post(
    f"/{model_path}/text-to-image",
    response_model=SubmitResponse,
    description="Generate image from text prompts",
)
def text_to_image(body: TextToImageInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/image-to-image",
    response_model=SubmitResponse,
    description="Generate image from input image and text prompts",
)
def image_to_image(body: ImageToImageInput) -> SubmitResponse:
    pass

# Register adapters for service providers
registry_items = {
    f"{model_path}/text-to-image": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalTextToImageAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/image-to-image": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalImageToImageAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
} 

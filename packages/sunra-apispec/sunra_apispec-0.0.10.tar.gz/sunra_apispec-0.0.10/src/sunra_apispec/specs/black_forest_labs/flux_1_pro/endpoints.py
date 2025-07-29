import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ImagesOutput
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from sunra_apispec.model_mapping import model_mapping
from .sunra_schema import ImageToImageInput, TextToImageInput
from .service_providers.bfl_official.adapter import BFLFluxV1ProTextToImageAdapter, BFLFluxV1ProImageToImageAdapter
from .service_providers.littercoder.adapter import LittercoderFluxV1ProTextToImageAdapter, LittercoderFluxV1ProImageToImageAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Black Forest Labs API",
    description="API for Black Forest Labs FLUX-1.0-Pro image generation model",
    version="1.0.0",
    output_schema=ImagesOutput,
)

@service.app.post(
    f"/{model_path}/text-to-image",
    response_model=SubmitResponse,
    description="Generate images from text prompts",
)
def text_to_image(body: TextToImageInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/image-to-image",
    response_model=SubmitResponse,
    description="Generate images from image prompt",
)
def image_to_image(body: ImageToImageInput) -> SubmitResponse:
    pass

registry_items = {
    f"{model_path}/text-to-image": [
        {
            "service_provider": ServiceProviderEnum.BLACK_FOREST_LABS.value,
            "adapter": BFLFluxV1ProTextToImageAdapter,
            "request_type": RequestType.ASYNC,
        },
        {
            "service_provider": ServiceProviderEnum.LITTERCODER.value,
            "adapter": LittercoderFluxV1ProTextToImageAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/image-to-image": [
        {
            "service_provider": ServiceProviderEnum.BLACK_FOREST_LABS.value,
            "adapter": BFLFluxV1ProImageToImageAdapter,
            "request_type": RequestType.ASYNC,
        },
        {
            "service_provider": ServiceProviderEnum.LITTERCODER.value,
            "adapter": LittercoderFluxV1ProImageToImageAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
} 

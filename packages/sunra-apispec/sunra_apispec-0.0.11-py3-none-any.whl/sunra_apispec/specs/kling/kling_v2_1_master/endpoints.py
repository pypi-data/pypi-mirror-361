import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import VideoOutput
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from .sunra_schema import TextToVideoInput, ImageToVideoInput
from .service_providers.fal.adapter import FalTextToVideoAdapter, FalImageToVideoAdapter
from .service_providers.kling_official.adapter import KlingTextToVideoAdapter, KlingImageToVideoAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Kling v2.1-master API",
    description="Kling 2.1 Master: The premium endpoint for Kling 2.1, designed for top-tier text-to-video generation with unparalleled motion fluidity, cinematic visuals, and exceptional prompt precision.",
    version="1.0.0",
    output_schema=VideoOutput,
)

@service.app.post(
    f"/{model_path}/text-to-video",
    response_model=SubmitResponse,
    description="Generate video from text prompts",
)
def text_to_video(body: TextToVideoInput) -> SubmitResponse:
    pass

@service.app.post(
    f"/{model_path}/image-to-video",
    response_model=SubmitResponse,
    description="Generate video from image",
)
def image_to_video(body: ImageToVideoInput) -> SubmitResponse:
    pass

registry_items = {
    f"{model_path}/text-to-video": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalTextToVideoAdapter,
            "request_type": RequestType.ASYNC,
        },
        {
            "service_provider": ServiceProviderEnum.KLING.value,
            "adapter": KlingTextToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ],
    f"{model_path}/image-to-video": [
        {
            "service_provider": ServiceProviderEnum.FAL.value,
            "adapter": FalImageToVideoAdapter,
            "request_type": RequestType.ASYNC,
        },
        {
            "service_provider": ServiceProviderEnum.KLING.value,
            "adapter": KlingImageToVideoAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}

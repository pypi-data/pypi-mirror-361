import os
from sunra_apispec.base.base_api_service import BaseAPIService, SubmitResponse
from sunra_apispec.base.common import RequestType
from sunra_apispec.base.output_schema import ImagesOutput
from sunra_apispec.model_mapping import model_mapping
from sunra_apispec.base.adapter_interface import ServiceProviderEnum
from .sunra_schema import TextToImageInput
from .service_providers.replicate.adapter import ReplicateTextToImageAdapter


model_name = os.path.basename(os.path.dirname(__file__))
model_provider = os.path.basename(os.path.dirname(os.path.dirname(__file__)))
model_path = model_mapping[f"{model_provider}/{model_name}"]


service = BaseAPIService(
    title="Luma Photon API",
    description="API for Luma Photon high-quality image generation model - Optimized for creative professional workflows and ultra-high fidelity outputs.",
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

# Register adapters for service providers
registry_items = {
    f"{model_path}/text-to-image": [
        {
            "service_provider": ServiceProviderEnum.REPLICATE.value,
            "adapter": ReplicateTextToImageAdapter,
            "request_type": RequestType.ASYNC,
        }
    ]
}

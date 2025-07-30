import logging
import time
from typing import Dict, Any

from fastapi import FastAPI
from ray import serve
from starlette.requests import Request
from starlette.responses import JSONResponse, StreamingResponse
from vllm import AsyncEngineArgs, AsyncLLMEngine
from vllm.entrypoints.openai.protocol import ChatCompletionRequest, ErrorResponse, ChatCompletionResponse
from vllm.entrypoints.openai.serving_chat import OpenAIServingChat
from vllm.entrypoints.openai.serving_models import OpenAIServingModels, BaseModelPath

web_api = FastAPI(title=f"Ray vLLM OpenAI-compatible API")


@serve.deployment(
    ray_actor_options={"num_gpus": 1},
    autoscaling_config={
        "target_ongoing_requests": 2,
        "min_replicas": 0,
        "initial_replicas": 1,
        "max_replicas": 1,
    }
)
@serve.ingress(web_api)
class VLLMModel:
    def __init__(self, engine_args: Dict[str, Any]):
        logging.basicConfig(level=logging.INFO)
        self.logger = logging.getLogger(__name__)
        self.engine_args = AsyncEngineArgs(**engine_args)
        self.logger.info(f"Initializing Async vLLM engine with args: {self.engine_args}")
        self.engine = AsyncLLMEngine.from_engine_args(self.engine_args)
        self.openai_chat_engine = None
        self.available_models = [
            {"id": self.engine_args.served_model_name[0],
             "object": "model",
             "created": int(time.time()),
             "owned_by": "openai",
             "permission": []}
        ]
        self.logger.info(f"Successfully initialized vLLM engine")

    async def __ensure_openai_chat_engine(self):
        if self.openai_chat_engine is None:
            model_config = await self.engine.get_model_config()
            base_model_paths = [BaseModelPath(name=self.engine_args.served_model_name[0], model_path=self.engine_args.model)]
            openai_serving_models = OpenAIServingModels(self.engine, model_config=model_config, base_model_paths=base_model_paths)
            self.logger.info(f"Initializing vLLM OpenAI Chat engine")
            self.openai_chat_engine = OpenAIServingChat(self.engine,
                                                        model_config=model_config,
                                                        models=openai_serving_models,
                                                        response_role="assistant",
                                                        chat_template_content_format="auto",
                                                        request_logger=None,
                                                        chat_template=None
                                                      )
            self.logger.info(f"Successfully initialized vLLM OpenAI Chat engine")

    @web_api.post("/v1/chat/completions")
    async def create_chat_completion(self, request: ChatCompletionRequest, raw_request: Request):
        await self.__ensure_openai_chat_engine()
        generator = await self.openai_chat_engine.create_chat_completion(request, raw_request)
        if isinstance(generator, ErrorResponse):
            return JSONResponse(content=generator.model_dump(), status_code=generator.code)
        if request.stream:
            return StreamingResponse(content=generator, media_type="text/event-stream")
        else:
            assert isinstance(generator, ChatCompletionResponse)
            return JSONResponse(content=generator.model_dump())

    @web_api.get("/v1/models")
    async def list_models(self):
        """Returns the list of available models in OpenAI-compatible format."""
        return {"object": "list", "data": self.available_models}

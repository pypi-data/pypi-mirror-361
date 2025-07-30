import os
from typing import Dict, Any

from ray.serve import Application

from ray_vllm.vllm_model import VLLMModel


def deploy_model(args: Dict[str, Any]) -> Application:
    assert args
    deployment_name = args.pop("deployment", None)
    assert deployment_name

    model: str = args.pop("model", "")
    assert model
    served_model_name = args.pop("served_model_name", os.path.basename(model))
    assert served_model_name
    if not isinstance(served_model_name, list):
        served_model_name = [served_model_name]

    multimodal = args.pop("multimodal", False)
    trust_remote_code = args.pop("trust_remote_code", False)
    enforce_eager = args.pop("enforce_eager", True)
    tensor_parallel_size = args.pop("tensor_parallel_size", 1)
    max_model_len = args.pop("max_model_len", 4096)
    max_num_seqs = args.pop("max_num_seqs", None)
    gpu_memory_utilization = args.pop("gpu_memory_utilization", 0.9)
    swap_space = args.pop("swap_space", 2)
    enable_chunked_prefill = args.pop("enable_chunked_prefill", False)
    limit_mm_per_prompt = args.pop("limit_mm_per_prompt", {})
    assert isinstance(limit_mm_per_prompt, dict)

    engine_args = dict(model=model,
                       served_model_name=served_model_name,
                       trust_remote_code=trust_remote_code,
                       enforce_eager=enforce_eager,
                       tensor_parallel_size=tensor_parallel_size,
                       max_model_len=max_model_len,
                       max_num_seqs=max_num_seqs,
                       gpu_memory_utilization=gpu_memory_utilization,
                       swap_space=swap_space,
                       enable_chunked_prefill=enable_chunked_prefill
                       )

    if multimodal:
        if limit_mm_per_prompt is None:
            limit_mm_per_prompt = {'image': 1, 'video': 0}
        engine_args["limit_mm_per_prompt"] = limit_mm_per_prompt

    if args:
        # If there are any leftover args, copy them over
        engine_args.update(args)

    deployment = VLLMModel.options(name=deployment_name).bind(engine_args)
    return deployment

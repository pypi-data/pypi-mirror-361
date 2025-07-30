import json
from typing import Callable, Dict, List, Optional

import torch
from tqdm import tqdm
import gc
import multiprocessing
import atexit
import openai

import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

from data.inference.Utility import append_inference, get_saved_inference_index
from data.utility.utility import MyTimer, chunking
from concurrent.futures import ThreadPoolExecutor
import sglang as sgl
from sglang import Engine

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

def cleanup_resources():
    """Clean up any dangling multiprocessing resources"""
    # Force garbage collection
    gc.collect()
    # Try to clean up any multiprocessing resources
    try:
        multiprocessing.resource_tracker._resource_tracker.clear()
    except (AttributeError, Exception) as e:
        print(f"Warning: Could not clear resource tracker: {e}")

def sgl_inference(
    huggingface_model_path: str,
    dataset_name: str,
    local_model_name: str,
    prompts: List[str] = None,
    input_token_ids: List = None,
    chunk_size: int = 200,
    sampling_params: Dict = None,
    trust_remote_code: bool = False,
    seperate_tokenizer_path: Optional[str] = None,
    additional_engine_param: Optional[Dict] = None,
) -> None:
    """Make inference on provided prompts using sglang, will use chunking and save inferenced answer locally.

    | Parameter:
        | huggingface_model_path: the model path copied from Hugging Face, ex: "deepseek-ai/deepseek-math-7b-base"
        | dataset_name: a string representing the dataset, this string will be part of a filename
        | prompts: a list of string, each is the prompt
        | local_model_name: a string indicating the model, this string will be used as a filename
        | input_token_ids: alternatively, you can pass in a List of input_token_ids that have already
            been tokenized by a tokenizer.
        | post_process_func: a function that will be used to process the output answer
        | chunk_size: the program will store every chunk_size inferenced prompts, the default 200 works well
            with one shot model inference for 7B models. You should decrease this number if you are inferencing
            on larger models / doing best of n inferences.
        | sampling_params: the sampling parameter passed for inferencing model, if given none then we will use
            {"max_tokens"=1024}
        | trust_remote_code: the same as the one defined in huggingface transformers
        | seperate_tokenizer_path: if you have a path that links to a tokenizer that you would like to use
        | additional_engine_param: additional parameter for the sglang engine
    """
    # Register cleanup handler to run at exit
    atexit.register(cleanup_resources)
    
    starting_idx = get_saved_inference_index(dataset_name, local_model_name)
    if prompts:
        input_length = len(prompts)
    elif input_token_ids:
        input_length = len(input_token_ids)
    else:
        raise Exception("Both prompts and input token ids are None")
    if starting_idx >= input_length:
        print(
            f"Inference for {dataset_name} using {local_model_name} is already complete"
        )
        return
    print(
        f"starting sglang inferencing for {dataset_name} using {local_model_name} with starting index {starting_idx}"
    )
    timer = MyTimer()
    if prompts:
        prompts = prompts[starting_idx:]
        inputs_to_chunk = prompts
    elif input_token_ids:
        input_token_ids = input_token_ids[starting_idx:]
        inputs_to_chunk = input_token_ids
    if sampling_params is None:
        sampling_params = {"max_new_tokens": 1024, "temperature": 0.8}
    elif "max_tokens" in sampling_params:
        tmp_val = sampling_params.pop("max_tokens")
        sampling_params["max_new_tokens"] = tmp_val
    elif "max_new_tokens" not in sampling_params:
        # default max new tokens
        sampling_params["max_new_tokens"] = 1024

    engine_params = {}
    if additional_engine_param:
        engine_params.update(additional_engine_param)

    if seperate_tokenizer_path:
        engine_params["tokenizer_path"] = seperate_tokenizer_path

    engine_params["trust_remote_code"] = trust_remote_code
    engine_params["disable_cuda_graph"] = True
    engine_params["mem_fraction_static"] = 0.7

    print(f"Initializing sglang Engine with model: {huggingface_model_path}")
    llm = None
    try:
        # Initialize sglang engine
        llm = sgl.Engine(
            model_path=huggingface_model_path,
            tp_size=torch.cuda.device_count() if torch.cuda.is_available() else 1,
            **engine_params
        )
        
        # Set the backend for sglang
        sgl.set_default_backend(llm)
        
        inputs = chunking(inputs_to_chunk, chunk_size)

        for i, chunk_prompts in enumerate(tqdm(inputs, leave=True)):
            batch_results = []
            
            # Process batches using sglang
            for idx, prompt in enumerate(chunk_prompts):
                try:
                    # Use sglang's generate function
                    with sgl.system():
                        sgl.gen("response", prompt, **sampling_params)
                    
                    state = sgl.run()
                    output_text = state["response"]
                    
                    batch_results.append(json.dumps({
                        "id": i * chunk_size + idx + starting_idx,
                        "response": output_text,
                    }))
                except Exception as e:
                    print(f"Error processing prompt {idx}: {e}")
                    batch_results.append(json.dumps({
                        "id": i * chunk_size + idx + starting_idx,
                        "response": "",
                        "error": str(e)
                    }))
            
            append_inference(dataset_name, local_model_name, batch_results)
            
            # Force garbage collection periodically to help clean up resources
            if i % 5 == 0:
                gc.collect()
                
    except Exception as e:
        print(f"Error during inference: {e}")
        raise
    finally:
        # Clean up the engine resources
        if llm is not None:
            try:
                llm.shutdown()
            except Exception as cleanup_error:
                print(f"Warning: Error during Engine cleanup: {cleanup_error}")
        
        # Additional cleanup
        gc.collect()
        cleanup_resources()

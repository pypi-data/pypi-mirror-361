from typing import List
from .gpt import GPTModel
from .az import AzureModel
# from ..SemanticEntropy.modules.pretrained_models.huggingface_models import HuggingfaceModel

def init_model(model_name: str, api_key: str = None, endpoint: str = None):
  # if 'llama' in model_name.lower() or 'falcon' in model_name or 'mistral' in model_name.lower():
  #   model = HuggingfaceModel(
  #     model_name, stop_sequences='default',
  #     max_new_tokens=500
  #   )
  # if 'gpt' in model_name.lower():
  #   model = GPTModel(api_key, model_name)
  # else:
  #   raise ValueError(f'Unknown model_name `{model_name}`.')
  if 'gpt' not in model_name.lower() and 'deepseek' not in model_name.lower():
    raise ValueError(f'Unknown model_name `{model_name}`.')
  
  model = AzureModel(azure_endpoint=endpoint, api_key=api_key, model_name=model_name)
  return model
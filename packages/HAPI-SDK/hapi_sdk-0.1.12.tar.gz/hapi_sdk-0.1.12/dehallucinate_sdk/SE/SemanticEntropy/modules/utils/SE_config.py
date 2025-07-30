from typing import Union, Tuple, Dict, Any, Optional
import os
import json
from collections import OrderedDict
import torch


class SEConfig:
  def __init__(self):
    self.api_key = "your_api_key_here"
    self.api_url = "https://api.example.com"
    self.use_all_generations = True
    self.num_generations = 3
    self.use_num_generations = 1
    self.entailment_model = "gpt-4o"
    self.strict_entailment = False
    self.model_max_new_tokens = 500
    self.max_tokens = 25
    self.compute_context_entails_response = False
    # if entropy is above the threshold, then the response is hallucinated
    self.entropy_threshold = 0.63
    # if entropy is below the threshold, and sampled responses contradict the generated response, then the response is hallucinated
    self.contradiction_threshold = 0.25
    self.contradiction_num_samples = 1


  def display(self):
    config_vars = vars(self)
    for key, value in config_vars.items():
      print(f"{key}: {value}")
  

# class PretrainedConfig(object):
#   model_type: str = ""
#   is_composition: bool = False

#   def __init__(self, **kwargs):
#     # Is decoder is used in encoder-decoder models to differentiate encoder from decoder
#     self.is_encoder_decoder = kwargs.pop("is_encoder_decoder", False)
#     self.is_decoder = kwargs.pop("is_decoder", False)
#     self.add_cross_attention = kwargs.pop("add_cross_attention", False)
#     self.tie_encoder_decoder = kwargs.pop("tie_encoder_decoder", False)

#     # Parameters for sequence generation
#     self.max_length = kwargs.pop("max_length", 20)
#     self.min_length = kwargs.pop("min_length", 0)
#     self.temperature = kwargs.pop("temperature", 1.0)
#     self.top_k = kwargs.pop("top_k", 50)
#     self.top_p = kwargs.pop("top_p", 1.0)
#     self.repetition_penalty = kwargs.pop("repetition_penalty", 1.0)
#     self.length_penalty = kwargs.pop("length_penalty", 1.0)

#     # Fine-tuning task arguments
#     self.architectures = kwargs.pop("architectures", None)
#     self.finetuning_task = kwargs.pop("finetuning_task", None)
#     self.id2label = kwargs.pop("id2label", None)
#     self.label2id = kwargs.pop("label2id", None)
#     if self.id2label is not None:
#       kwargs.pop("num_labels", None)
#       self.id2label = dict((int(key), value) for key, value in self.id2label.items())
#       # Keys are always strings in JSON so convert ids to int here.
#     else:
#       self.num_labels = kwargs.pop("num_labels", 2)

#     # Tokenizer arguments
#     self.tokenizer_class = kwargs.pop("tokenizer_class", None)
#     self.prefix = kwargs.pop("prefix", None)
#     self.bos_token_id = kwargs.pop("bos_token_id", None)
#     self.pad_token_id = kwargs.pop("pad_token_id", None)
#     self.eos_token_id = kwargs.pop("eos_token_id", None)
#     self.sep_token_id = kwargs.pop("sep_token_id", None)

#     self.decoder_start_token_id = kwargs.pop("decoder_start_token_id", None)

#     # task specific arguments
#     self.task_specific_params = kwargs.pop("task_specific_params", None)

#     # TPU arguments
#     self.xla_device = kwargs.pop("xla_device", None)

#     # Name or path to the pretrained checkpoint
#     self._name_or_path = str(kwargs.pop("name_or_path", ""))

#     # Drop the transformers version info
#     kwargs.pop("transformers_version", None)

#     # Additional attributes without default values
#     for key, value in kwargs.items():
#       try:
#         setattr(self, key, value)
#       except AttributeError as err:
#         raise err

#   @classmethod
#   def from_pretrained(cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs) -> "PretrainedConfig":
#     config_dict, kwargs = cls.get_config_dict(pretrained_model_name_or_path, **kwargs)
#     return cls.from_dict(config_dict, **kwargs)

#   @classmethod
#   def _dict_from_json_file(cls, json_file: Union[str, os.PathLike]):
#     with open(json_file, "r", encoding="utf-8") as reader:
#       text = reader.read()
#     return json.loads(text)

#   @classmethod
#   def from_dict(cls, config_dict: Dict[str, Any], **kwargs) -> "PretrainedConfig":
#     return_unused_kwargs = kwargs.pop("return_unused_kwargs", False)

#     config = cls(**config_dict)

#     if hasattr(config, "pruned_heads"):
#       config.pruned_heads = dict((int(key), value) for key, value in config.pruned_heads.items())

#     # Update config with kwargs if needed
#     to_remove = []
#     for key, value in kwargs.items():
#       if hasattr(config, key):
#         setattr(config, key, value)
#         to_remove.append(key)
#     for key in to_remove:
#       kwargs.pop(key, None)

#     if return_unused_kwargs:
#       return config, kwargs
#     else:
#       return config

#   @classmethod
#   def get_config_dict(
#     cls, pretrained_model_name_or_path: Union[str, os.PathLike], **kwargs
#   ) -> Tuple[Dict[str, Any], Dict[str, Any]]:
#     cache_dir = kwargs.pop("cache_dir", None)
#     force_download = kwargs.pop("force_download", False)
#     resume_download = kwargs.pop("resume_download", False)
#     proxies = kwargs.pop("proxies", None)
#     use_auth_token = kwargs.pop("use_auth_token", None)
#     local_files_only = kwargs.pop("local_files_only", False)
#     revision = kwargs.pop("revision", None)

#     pretrained_model_name_or_path = str(pretrained_model_name_or_path)
#     if os.path.isdir(pretrained_model_name_or_path):
#       config_file = os.path.join(pretrained_model_name_or_path, CONFIG_NAME)
#     elif os.path.isfile(pretrained_model_name_or_path) or is_remote_url(pretrained_model_name_or_path):
#       config_file = pretrained_model_name_or_path
#     else:
#       config_file = hf_bucket_url(
#         pretrained_model_name_or_path, filename=CONFIG_NAME, revision=revision, mirror=None
#       )

#     try:
#       # Load from URL or cache if already cached
#       resolved_config_file = cached_path(
#         config_file,
#         cache_dir=cache_dir,
#         force_download=force_download,
#         proxies=proxies,
#         resume_download=resume_download,
#         local_files_only=local_files_only,
#         use_auth_token=use_auth_token,
#       )
#       # Load config dict
#       config_dict = cls._dict_from_json_file(resolved_config_file)

#     except EnvironmentError as err:
#       msg = (
#         f"Can't load config for '{pretrained_model_name_or_path}'. Make sure that:\n\n"
#         f"- '{pretrained_model_name_or_path}' is a correct model identifier listed on 'https://huggingface.co/models'\n\n"
#         f"- or '{pretrained_model_name_or_path}' is the correct path to a directory containing a {CONFIG_NAME} file\n\n"
#       )
#       raise EnvironmentError(msg)

#     except json.JSONDecodeError:
#       msg = (
#         "Couldn't reach server at '{}' to download configuration file or "
#         "configuration file is not a valid JSON file. "
#         "Please check network or file content here: {}.".format(config_file, resolved_config_file)
#       )
#       raise EnvironmentError(msg)

#     return config_dict, kwargs

# class LlamaConfig(PretrainedConfig):
#   model_type = "llama"
#   def __init__(
#     self,
#     vocab_size: int = 32000,
#     dim: int = 512,
#     dropout: int = 0.0,
#     n_layers: int = 8,
#     n_heads: int = 8,
#     n_kv_heads: Optional[int] = 8,
#     max_seq_len: int = 1024,
#     layer_norm_eps: float = 1e-5,
#     multiple_of: int = 32,
#     hidden_dim: Optional[int] = None,
#     position_embedding_type: str = "rotary",
#     use_cache: bool = True,
#     **kwargs
#   ):
#     super().__init__(**kwargs)

#     self.vocab_size = vocab_size
#     self.dim = dim
#     self.dropout = dropout
#     self.n_layers = n_layers
#     self.n_heads = n_heads
#     self.max_seq_len = max_seq_len
#     self.n_kv_heads = n_kv_heads
#     self.layer_norm_eps = layer_norm_eps
#     self.multiple_of = multiple_of
#     self.hidden_dim = hidden_dim
#     self.position_embedding_type = position_embedding_type
#     self.use_cache = use_cache
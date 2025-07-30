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
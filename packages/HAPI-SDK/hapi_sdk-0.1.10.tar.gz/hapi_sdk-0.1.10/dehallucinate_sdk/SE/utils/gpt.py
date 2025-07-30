import os
import hashlib
from tenacity import retry, wait_random_exponential, retry_if_not_exception_type

from openai import OpenAI


class KeyError(Exception):
    """OpenAIKey not provided in environment variable."""
    pass


# @retry(retry=retry_if_not_exception_type(KeyError), wait=wait_random_exponential(min=10, max=20))
def predict(client, prompt, temperature=1.0, model='gpt-4o', logprobs=True, max_tokens=100):
    """Predict with GPT models."""

    if not client.api_key:
        raise KeyError('Need to provide OpenAI API key in environment variable `OPENAI_API_KEY`.')

    if isinstance(prompt, str):
        messages = [
            {'role': 'user', 'content': prompt},
        ]
    else:
        messages = prompt
        
    if model == 'gpt-4':
        model = 'gpt-4-0613'
    elif model == 'gpt-3.5':
        model = 'gpt-3.5-turbo-1106'

    output = client.chat.completions.create(
        model=model,
        messages=messages,
        logprobs=logprobs,
        top_logprobs=1,
        temperature=temperature,
        max_completion_tokens=max_tokens
    )
    response = output.choices[0].message.content
    
    if logprobs:
        logits = [token_info.logprob for token_info in output.choices[0].logprobs.content]
        tokens = [token_info.token for token_info in output.choices[0].logprobs.content]
        return response, logits, tokens
    else:
        return response, None, None


# @retry(retry=retry_if_not_exception_type(KeyError), wait=wait_random_exponential(min=1, max=10))
# def sample_predict(prompt, num_samples, model='gpt-4', temperature=1.0, logprobs=0, config: SEConfig=None):
    

class GPTModel:
    def __init__(self, api_key=None, model_name='gpt-4'):
        self.model_name = model_name
        if not api_key:
            KeyError('Need to provide OpenAI API key in environment variable `OPENAI_API_KEY`.')
        self.client = OpenAI(api_key=api_key)

    def predict(self, prompt, temperature=1.0, max_tokens=100):
        return predict(self.client, prompt, temperature, model=self.model_name, max_tokens=max_tokens)


def md5hash(string):
    return int(hashlib.md5(string.encode('utf-8')).hexdigest(), 16)

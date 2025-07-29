import os
from azure.identity import DefaultAzureCredential, get_bearer_token_provider
from azure.ai.inference import ChatCompletionsClient
from azure.ai.inference.models import UserMessage, SystemMessage
from azure.core.credentials import AzureKeyCredential

# manually set environment variables

def predict(client, prompt, temperature=1.0, model='gpt-4o', logprobs=True, max_tokens=100):
    """Predict with Azure OpenAI models."""
    
    # Convert to proper message objects
    if isinstance(prompt, str):
        messages = [UserMessage(prompt)]
    elif isinstance(prompt, list) and all(isinstance(m, dict) for m in prompt):
        # Convert dict messages to proper message objects
        messages = []
        for m in prompt:
            if m.get('role') == 'system':
                messages.append(SystemMessage(m.get('content', '')))
            elif m.get('role') == 'user':
                messages.append(UserMessage(m.get('content', '')))
            # Add other message types as needed
    else:
        # Assuming prompt is already a list of proper message objects
        messages = prompt
    
    # Azure OpenAI API call
    model_extras = None
    if logprobs:
        # Note: This assumes the model supports logprobs and top_logprobs
        model_extras = {"logprobs": True}
    
    output = client.complete(
        model=model,
        messages=messages,
        temperature=temperature,
        max_tokens=max_tokens,
        model_extras=model_extras
    )

    response = output.choices[0].message.content
    print(output.choices[0])
    # Add this after receiving the response

    if logprobs and output.choices[0]['logprobs']:
        logprobs_content = output.choices[0]["logprobs"]["content"]
        logits = [entry["logprob"] for entry in logprobs_content]
        tokens = [entry["token"] for entry in logprobs_content]
        # print("Logits:", logits)
        # print("Tokens:", tokens)
        return response, logits, tokens
    else:
        return response, None, None


class AzureModel:
    def __init__(self, azure_endpoint=None, api_key=None, model_name='gpt-4o'):
        """Initialize Azure OpenAI model.
        
        Args:
            azure_endpoint: Azure OpenAI endpoint URL
            api_key: Azure OpenAI API key
            model_name: The deployment name of your model in Azure
        """
        self.model_name = model_name
        
        # Get endpoint from parameter or environment variable
        if not azure_endpoint:
            azure_endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
            if not azure_endpoint:
                raise ValueError('Need to provide Azure OpenAI endpoint via parameter or AZURE_OPENAI_ENDPOINT environment variable')
        
        # Get API key from parameter or environment variable
        if not api_key:
            api_key = os.environ.get("AZURE_OPENAI_API_KEY")
            if not api_key:
                raise ValueError('Need to provide Azure OpenAI API key via parameter or AZURE_OPENAI_API_KEY environment variable')
        
        # Clean up the endpoint URL to ensure it's properly formatted
        # Remove any quotes and ensure it ends with a trailing slash
        azure_endpoint = azure_endpoint.strip('"\'')
        if not azure_endpoint.endswith('/'):
            azure_endpoint += '/'
            
        print(f"Using endpoint: {azure_endpoint}")
        
        self.client = ChatCompletionsClient(
            endpoint=azure_endpoint,
            credential=AzureKeyCredential(api_key)
        )

    def predict(self, prompt, temperature=1.0, max_tokens=100):
        return predict(self.client, prompt, temperature, model=self.model_name, max_tokens=max_tokens)


# Example usage with environment variables
def get_default_azure_client():
    """Get an Azure client using environment variables."""
    endpoint = os.environ.get("AZURE_OPENAI_ENDPOINT")
    api_key = os.environ.get("AZURE_OPENAI_API_KEY")
    
    if not endpoint or not api_key:
        raise ValueError("AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY must be set as environment variables")
        
    return AzureModel(azure_endpoint=endpoint, api_key=api_key,)

# # Create a default client if environment variables are set
# client = None
# try:
#     client = get_default_azure_client()
# except ValueError:
#     print("Warning: Azure OpenAI environment variables not set. Set AZURE_OPENAI_ENDPOINT and AZURE_OPENAI_API_KEY to use the default client.")



# print(client.predict("What is the capital of France?", temperature=0.5, max_tokens=50))



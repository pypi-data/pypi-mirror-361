# HAPI SDK

A plug-and-play SDK for detecting and reducing hallucinations in Large Language Model outputs using semantic entropy analysis and trained classifiers.

## Features

- **Hallucination Detection**: Uses trained classifiers to detect hallucinations in LLM outputs
- **Semantic Entropy Analysis**: Advanced semantic analysis to identify uncertain or inconsistent outputs
- **Easy Integration**: Simple API that works with any Hugging Face model
- **Multiple Detection Methods**: Combines classifier-based and semantic entropy-based approaches
- **Real-time Analysis**: Generate and analyze outputs in real-time

## Installation

```bash
pip install HAPI-SDK
```

## Quick Start

```python
from dehallucinate_sdk import DeHallucinationClient

# Initialize the client
client = DeHallucinationClient(
    model_id="meta-llama/Llama-2-7b-chat-hf",
    license_key="your-license-key"
)

# Generate and analyze output
prompt = "Explain quantum entanglement in simple terms."
output, flagged_sentences = client.generate_output(prompt)

print("Generated Output:", output)
print("Flagged Sentences:", flagged_sentences)
```

## Available Methods

The `DeHallucinationClient` exposes the following main methods:

### 1. `generate_output(prompt, max_tokens=512)`
Generates a response and performs hallucination analysis in one step.

```python
output, flagged_sentences = client.generate_output(
    "What is the capital of France?", 
    max_tokens=100
)
```

### 2. `semantic_entropy_check(prompt, num_generations=5)`
Analyzes semantic entropy to detect potential hallucinations.

```python
entropy_score, is_hallucinated = client.semantic_entropy_check(
    "Tell me about the history of artificial intelligence"
)
```

### 3. `sentence_contains_hallucination(sentence, context="")`
Checks if a specific sentence contains hallucinations.

```python
is_hallucinated = client.sentence_contains_hallucination(
    "The capital of France is Berlin.",
    context="Geography facts"
)
```

### 4. `generate(prompt, max_tokens=512)`
Simple text generation without hallucination analysis.

```python
output = client.generate("Write a story about space exploration", max_tokens=200)
```

### 5. `generate_sentence(prompt)`
Generates a single sentence response.

```python
sentence = client.generate_sentence("Complete this: The best way to learn programming is")
```

## Supported Models

- Llama-2-7b-chat (meta-llama/Llama-2-7b-chat-hf)
- Falcon-40b (tiiuae/falcon-40b)  
- Llama-2-7b (meta-llama/Llama-2-7b-hf)
- MPT-7b (mosaicml/mpt-7b)
- More models coming soon!

## Configuration

### Environment Variables

```bash
export OPENAI_API_KEY="your_openai_api_key"
export HUGGINGFACE_API_KEY="your_hf_token"
```

### Advanced Usage

```python
# Configure with custom parameters
client = DeHallucinationClient(
    model_id="meta-llama/Llama-2-7b-chat-hf",
    license_key="your-license-key",
    device="cuda",  # or "cpu"
    temperature=0.7,
    use_semantic_entropy=True,
    confidence_threshold=0.8
)

# Batch processing
prompts = [
    "What causes climate change?",
    "How do vaccines work?", 
    "Explain machine learning basics"
]

results = []
for prompt in prompts:
    output, flagged = client.generate_output(prompt)
    results.append({"prompt": prompt, "output": output, "flagged": flagged})
```

## Error Handling

```python
try:
    output, flagged = client.generate_output("Your prompt here")
except Exception as e:
    print(f"Error during generation: {e}")
```

## Contributing

We welcome contributions! Please see our [GitHub repository](https://github.com/cyprienn967/HAPI_SDK) for more information.

## License

MIT License - see LICENSE file for details.

## Support

For questions, suggestions, or issues, please contact us or open an issue on GitHub.



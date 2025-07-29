## Overview

HAPI is a plug-and-play SDK to dehallucinate your LLM generation in real time

- Hallucination Detection: Identifies and flags AI-generated misinformation.
- Confidence Filtering: Evaluates reliability of generated content.
- Easy Integration: Will support any open-source model soon

## Supported models - more coming soon!

- Llama-2-7b-chat (meta-llama/Llama-2-7b-chat)
- Falcon40b (tiiuae/falcon-40b)
- Llama-2-7b (meta-llama/Llama-2-7b-hf)
- MPT7B (mosaicml/mpt-7b)

## Installation

pip install HAPI_SDK

## Quick Start

from hapi_sdk import DeHallucinationClient

client = DeHallucinationClient(model_id="meta-llama/Llama-2-7b-chat-hf", license_key="your-license-key")

prompt = "Explain quantum entanglement in simple terms."

output, flagged_sentences = client.dehallucinate1(prompt)

print("Filtered Output:", output)

print("Flagged Sentences:", flagged_sentences)

## Contact with any suggestions!



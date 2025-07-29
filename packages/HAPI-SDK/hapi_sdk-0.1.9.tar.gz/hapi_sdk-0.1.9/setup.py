from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="HAPI_SDK",
    version="0.1.9",
    description="A plug-and-play SDK for de-hallucinating outputs from LLMs",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="True",
    author_email="cyprienseydoux@gmail.com",
    url="https://github.com/cyprienn967/HAPI_SDK",
    packages=find_packages(),
    install_requires=[
        "torch",
        "transformers",
        "accelerate",
        "pyarrow >=14.0.0",
        "flask",
        "numpy",
        "evaluate",
        "datasets",
        "pandas",
        "tqdm",
        "tokenizers",
        "openai",
        "tiktoken",
        "nltk",
        "tenacity",
        "safetensors",
        "azure-identity",
        "azure-keyvault-secrets",
        "azure-ai-textanalytics",
        "requests",
        "werkzeug",
        "aws-wsgi",
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)

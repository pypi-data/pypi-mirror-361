from setuptools import setup, find_packages
import os

# Read the README file
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements from requirements.txt
def read_requirements():
    with open("requirements.txt", "r", encoding="utf-8") as f:
        return [line.strip() for line in f if line.strip() and not line.startswith("#")]

setup(
    name="HAPI-SDK",
    version="0.2.17",
    description="A plug-and-play SDK for de-hallucinating outputs from LLMs using semantic entropy and trained classifiers",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="True",
    author_email="cyprienseydoux@gmail.com",
    url="https://github.com/cyprienn967/HAPI_SDK",
    packages=find_packages(include=['dehallucinate_sdk', 'dehallucinate_sdk.*']),
    install_requires=read_requirements(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Software Development :: Libraries :: Python Modules",
    ],
    python_requires=">=3.7",
    keywords="llm hallucination detection ai nlp semantic-entropy machine-learning",
    include_package_data=True,
    package_data={
        'dehallucinate_sdk': [
            'models/*.pt',
            'SE/**/*.py',
            'SE/**/*.yaml', 
            'SE/**/*.txt',
        ],
    },
    project_urls={
        "Bug Reports": "https://github.com/cyprienn967/HAPI_SDK/issues",
        "Source": "https://github.com/cyprienn967/HAPI_SDK",
    },
)

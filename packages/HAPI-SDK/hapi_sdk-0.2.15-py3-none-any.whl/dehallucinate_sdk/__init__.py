"""
HAPI SDK - A plug-and-play SDK for de-hallucinating outputs from LLMs

This package provides tools to detect and reduce hallucinations in Large Language Model outputs
using semantic entropy analysis and trained classifiers.
"""

from .client import DeHallucinationClient

__version__ = "0.2.15"
__author__ = "True"
__email__ = "cyprienseydoux@gmail.com"

# Expose the main class for easy import
__all__ = ["DeHallucinationClient"]


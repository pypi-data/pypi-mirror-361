#!/usr/bin/env python3
"""
FactCheckr - AI-powered fact-checking tool using free Hack Club AI.

A simple, free, and powerful fact-checking library that requires no API keys.
"""

from .core import CompleteFactCheckr

__version__ = "1.0.0"
__author__ = "Geno"
__email__ = "mohamedr7825@gmail.com"
__description__ = "AI-powered fact-checking tool using free Hack Club AI"

# Make the main class available at package level
__all__ = ["CompleteFactCheckr"]

# Convenience alias
FactCheckr = CompleteFactCheckr
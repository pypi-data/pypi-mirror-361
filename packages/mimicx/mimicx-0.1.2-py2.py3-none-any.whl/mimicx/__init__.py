"""
MimicX AI
Human-like AI for everyone.
"""

from .refine_grammar import MimicText
from .MimicText.classifiers.industry.module import MLIndustryClassifier

__version__ = "0.1.2"
__author__ = 'MimicX'
__credits__ = 'AI Researcher at MimicX'

__all__ = ['MimicText', 'MLIndustryClassifier']
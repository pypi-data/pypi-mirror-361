"""
MimicX AI
Human-like AI for everyone.
"""

from .MimicText.refine_grammar import MimicText
from .MimicText.industry_classifier import MLIndustryClassifier

__version__ = "0.1.0"
__author__ = 'Hamadi Camara'
__credits__ = 'AI Researcher at MimicX'

__all__ = ['MimicText', 'MLIndustryClassifier']
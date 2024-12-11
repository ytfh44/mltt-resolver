"""
Core functionality for type checking and evaluation
"""

from .evaluator import Evaluator
from .normalizer import Normalizer
from .checker import TypeChecker

__all__ = ['Evaluator', 'Normalizer', 'TypeChecker']

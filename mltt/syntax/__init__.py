"""
Martin-Löf Type Theory syntax module.
"""

from .terms import Var, Universe, Pi, Lambda, App, Term

__all__ = ['Var', 'Universe', 'Pi', 'Lambda', 'App', 'Term'] 
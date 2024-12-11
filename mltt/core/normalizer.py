from ..syntax.terms import Term
from ..syntax.values import Value
from .evaluator import Evaluator

class Normalizer:
    """规范化器，用于将项规范化为值"""
    
    def __init__(self, evaluator: Evaluator):
        self.evaluator = evaluator
        
    def normalize(self, term: Term) -> Value:
        """将项规范化为值"""
        return self.evaluator.eval(term)
        
    def fresh_name(self, base: str) -> str:
        """生成新的变量名"""
        return f"{base}'"

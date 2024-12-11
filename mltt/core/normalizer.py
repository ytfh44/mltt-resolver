from ..syntax.terms import *
from ..syntax.values import *
from .evaluator import Evaluator

class Normalizer:
    def __init__(self):
        self.evaluator = Evaluator()

    def normalize(self, term: Term) -> Term:
        """将项规约到范式"""
        value = self.evaluator.eval(term)
        return self.read_back(value)
        
    def read_back(self, value: Value) -> Term:
        """将值转回项"""
        if isinstance(value, VarValue):
            return Var(value.name)
            
        elif isinstance(value, UniverseValue):
            return Universe(value.level)
            
        elif isinstance(value, ClosureValue):
            # 生成新的变量名
            fresh_name = self.fresh_name(value.param_name)
            # 应用闭包到新变量
            with self.evaluator.in_env({fresh_name: VarValue(fresh_name)}):
                body_val = self.evaluator.eval(value.body)
                body_term = self.read_back(body_val)
                return Lambda(fresh_name, None, body_term)  # 类型标注暂时忽略
                
        elif isinstance(value, NeutralValue):
            head = self.read_back_neutral(value.head)
            args = [self.read_back(arg) for arg in value.args]
            result = head
            for arg in args:
                result = Apply(result, arg)
            return result
            
        raise ValueError(f"Cannot read back value: {value}")
        
    def read_back_neutral(self, term: Term) -> Term:
        """将中性项转回普通项"""
        if isinstance(term, Var):
            return term
        elif isinstance(term, Apply):
            return Apply(
                self.read_back_neutral(term.func),
                self.read_back_neutral(term.arg)
            )
        raise ValueError(f"Invalid neutral term: {term}")
        
    def fresh_name(self, base: str) -> str:
        """生成新的变量名"""
        # 简单实现，实际应该更复杂
        return f"{base}'"

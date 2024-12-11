from ..syntax.terms import *
from ..syntax.values import *

class Evaluator:
    def __init__(self):
        self.env = {}

    def eval(self, term: Term) -> Value:
        """求值一个项"""
        if isinstance(term, Var):
            return self.env.get(term.name, VarValue(term.name))
            
        elif isinstance(term, Universe):
            return UniverseValue(term.level)
            
        elif isinstance(term, Lambda):
            return ClosureValue(self.env.copy(), term.param_name, term.body)
            
        elif isinstance(term, Apply):
            func_val = self.eval(term.func)
            arg_val = self.eval(term.arg)
            
            if isinstance(func_val, ClosureValue):
                # 应用闭包
                new_env = func_val.env.copy()
                new_env[func_val.param_name] = arg_val
                with self.in_env(new_env):
                    return self.eval(func_val.body)
            else:
                # 构建中性值
                return NeutralValue(term, [arg_val])
                
        return NeutralValue(term, [])

    def in_env(self, new_env):
        """环境管理器"""
        class EnvManager:
            def __init__(self, evaluator, env):
                self.evaluator = evaluator
                self.new_env = env
                self.old_env = None
                
            def __enter__(self):
                self.old_env = self.evaluator.env
                self.evaluator.env = self.new_env
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.evaluator.env = self.old_env
                
        return EnvManager(self, new_env) 
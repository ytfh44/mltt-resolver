from .syntax import *
from .context import Context

class TypeChecker:
    def __init__(self):
        self.context = Context()
    
    def check(self, term: Term, expected_type: Term) -> bool:
        """检查term是否具有expected_type类型"""
        actual_type = self.infer(term)
        return self.is_equal(actual_type, expected_type)
    
    def infer(self, term: Term) -> Term:
        """推导term的类型"""
        if isinstance(term, Var):
            type_ = self.context.lookup(term.name)
            if type_ is None:
                raise TypeError(f"Unbound variable: {term.name}")
            return type_
            
        elif isinstance(term, Universe):
            # Type_n : Type_{n+1}
            return Universe(term.level + 1)
            
        elif isinstance(term, Pi):
            # 检查参数类型
            param_type_type = self.infer(term.param_type)
            if not isinstance(param_type_type, Universe):
                raise TypeError("Parameter type must be a type")
                
            # 在扩展的上下文中检查返回类型
            extended_ctx = self.context.extend(term.param_name, term.param_type)
            with self.in_context(extended_ctx):
                return_type_type = self.infer(term.return_type)
                if not isinstance(return_type_type, Universe):
                    raise TypeError("Return type must be a type")
                    
            # Pi类型的类型是参数类型和返回类型的最大universe level
            return Universe(max(param_type_type.level, return_type_type.level))
            
        elif isinstance(term, Lambda):
            # 检查参数类型
            param_type_type = self.infer(term.param_type)
            if not isinstance(param_type_type, Universe):
                raise TypeError("Parameter type must be a type")
                
            # 在扩展的上下文中检查函数体
            extended_ctx = self.context.extend(term.param_name, term.param_type)
            with self.in_context(extended_ctx):
                body_type = self.infer(term.body)
                
            # Lambda的类型是对应的Pi类型
            return Pi(term.param_name, term.param_type, body_type)
            
        elif isinstance(term, Apply):
            func_type = self.infer(term.func)
            if not isinstance(func_type, Pi):
                raise TypeError("Cannot apply non-function")
                
            # 检查参数类型匹配
            if not self.check(term.arg, func_type.param_type):
                raise TypeError("Argument type mismatch")
                
            # 替换返回类型中的变量
            return self.substitute(
                func_type.return_type,
                func_type.param_name,
                term.arg
            )
            
        raise TypeError(f"Cannot infer type of: {term}")

    def is_equal(self, t1: Term, t2: Term) -> bool:
        """检查两个项是否相等（包括alpha等价性）"""
        # 简单实现，实际应该处理alpha等价
        return t1 == t2
    
    def substitute(self, term: Term, var_name: str, replacement: Term) -> Term:
        """在term中将名为var_name的变量替换为replacement"""
        if isinstance(term, Var):
            if term.name == var_name:
                return replacement
            return term
            
        elif isinstance(term, (Universe, Pi, Lambda)):
            # 递归替换
            if isinstance(term, Pi):
                return Pi(
                    term.param_name,
                    self.substitute(term.param_type, var_name, replacement),
                    self.substitute(term.return_type, var_name, replacement)
                )
            elif isinstance(term, Lambda):
                return Lambda(
                    term.param_name,
                    self.substitute(term.param_type, var_name, replacement),
                    self.substitute(term.body, var_name, replacement)
                )
            return term
            
        elif isinstance(term, Apply):
            return Apply(
                self.substitute(term.func, var_name, replacement),
                self.substitute(term.arg, var_name, replacement)
            )
            
        return term
    
    def in_context(self, ctx: Context):
        """上下文管理器，用于临时切换类型检查的上下文"""
        class ContextManager:
            def __init__(self, checker, new_ctx):
                self.checker = checker
                self.new_ctx = new_ctx
                self.old_ctx = None
                
            def __enter__(self):
                self.old_ctx = self.checker.context
                self.checker.context = self.new_ctx
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.checker.context = self.old_ctx
                
        return ContextManager(self, ctx) 
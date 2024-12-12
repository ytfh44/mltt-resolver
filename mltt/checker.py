from contextlib import contextmanager
from typing import Optional, Union
from .syntax.terms import Term, Var, Universe, Pi, Lambda, App
from .context import Context

class TypeError(Exception):
    """类型错误"""
    pass

class TypeChecker:
    """类型检查器"""
    
    def __init__(self):
        self.context = Context()
    
    def check(self, term: Term, expected_type: Term) -> bool:
        """检查项的类型是否符合预期"""
        try:
            actual_type = self.infer(term)
            return self.is_equal(actual_type, expected_type)
        except TypeError:
            return False
    
    def infer(self, term: Term) -> Term:
        """推导项的类型"""
        if isinstance(term, Var):
            # 变量类型推导
            type_ = self.context.get_var_type(term.name)
            if type_ is None:
                raise TypeError(f"Unbound variable: {term.name}")
            return type_
            
        elif isinstance(term, Universe):
            # Universe类型推导
            return Universe(term.level + 1)
            
        elif isinstance(term, Pi):
            # Pi类型推导
            # 检查参数类型
            param_type = self.infer(term.var_type)
            if not isinstance(param_type, Universe):
                raise TypeError(f"Parameter type must be a universe, got {param_type}")
                
            # 在扩展的上下文中检查返回类型
            with self.in_context(self.context.extend(term.var_name, term.var_type)):
                return_type = self.infer(term.body)
                if not isinstance(return_type, Universe):
                    raise TypeError(f"Return type must be a universe, got {return_type}")
                    
            # Pi类型的类型是两个类型的最大值加1
            return Universe(max(param_type.level, return_type.level))
            
        elif isinstance(term, Lambda):
            # Lambda类型推导
            # 检查参数类型
            param_type = self.infer(term.var_type)
            if not isinstance(param_type, Universe):
                raise TypeError(f"Parameter type must be a universe, got {param_type}")
                
            # 在扩展的上下文中推导主体类型
            with self.in_context(self.context.extend(term.var_name, term.var_type)):
                body_type = self.infer(term.body)
                
            # Lambda的类型是对应的Pi类型
            return Pi(term.var_name, term.var_type, body_type)
            
        elif isinstance(term, App):
            # 应用类型推导
            # 推导函数类型
            func_type = self.infer(term.func)
            if not isinstance(func_type, Pi):
                raise TypeError(f"Cannot apply non-function: {term.func}")
                
            # 检查参数类型
            arg_type = self.infer(term.arg)
            if not self.is_equal(arg_type, func_type.var_type):
                raise TypeError(f"Argument type mismatch: expected {func_type.var_type}, got {arg_type}")
                
            # 返回替换后的类型
            return self.substitute(func_type.body, func_type.var_name, term.arg)
            
        else:
            raise TypeError(f"Unknown term type: {type(term)}")
    
    def substitute(self, term: Term, var_name: str, replacement: Term) -> Term:
        """替换变量"""
        if isinstance(term, Var):
            return replacement if term.name == var_name else term
            
        elif isinstance(term, Universe):
            return term
            
        elif isinstance(term, Pi):
            # 避免变量捕获
            if term.var_name == var_name:
                return term
            return Pi(
                term.var_name,
                self.substitute(term.var_type, var_name, replacement),
                self.substitute(term.body, var_name, replacement)
            )
            
        elif isinstance(term, Lambda):
            # 避免变量捕获
            if term.var_name == var_name:
                return term
            return Lambda(
                term.var_name,
                self.substitute(term.var_type, var_name, replacement),
                self.substitute(term.body, var_name, replacement)
            )
            
        elif isinstance(term, App):
            return App(
                self.substitute(term.func, var_name, replacement),
                self.substitute(term.arg, var_name, replacement)
            )
            
        else:
            raise TypeError(f"Unknown term type: {type(term)}")
    
    def is_equal(self, term1: Term, term2: Term) -> bool:
        """检查两个项是否相等"""
        if type(term1) != type(term2):
            return False
            
        if isinstance(term1, Var):
            return term1.name == term2.name
            
        elif isinstance(term1, Universe):
            return term1.level == term2.level
            
        elif isinstance(term1, Pi):
            return (term1.var_name == term2.var_name and
                    self.is_equal(term1.var_type, term2.var_type) and
                    self.is_equal(term1.body, term2.body))
                    
        elif isinstance(term1, Lambda):
            return (term1.var_name == term2.var_name and
                    self.is_equal(term1.var_type, term2.var_type) and
                    self.is_equal(term1.body, term2.body))
                    
        elif isinstance(term1, App):
            return (self.is_equal(term1.func, term2.func) and
                    self.is_equal(term1.arg, term2.arg))
                    
        else:
            raise TypeError(f"Unknown term type: {type(term1)}")
    
    @contextmanager
    def in_context(self, new_context: Context):
        """上下文管理器，用于临时切换上下文"""
        old_context = self.context
        self.context = new_context
        try:
            yield
        finally:
            self.context = old_context 
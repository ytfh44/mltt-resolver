from typing import Optional
from ..syntax.terms import *
from ..syntax.values import *
from ..context import Context
from .evaluator import Evaluator
from .normalizer import Normalizer

class TypeError(Exception):
    """类型错误"""
    pass

class TypeChecker:
    """类型检查器"""
    
    def __init__(self):
        self.context = Context()
        self.evaluator = Evaluator()
        self.normalizer = Normalizer(self.evaluator)
        
    def infer(self, term: Term) -> Term:
        """推导项的类型"""
        if isinstance(term, Var):
            # 变量类型从上下文中查找
            type_ = self.context.get_var_type(term.name)
            if type_ is None:
                raise TypeError(f"未绑定的变量: {term.name}")
            return type_
            
        elif isinstance(term, Universe):
            # Type_n : Type_{n+1}
            return Universe(term.level + 1)
            
        elif isinstance(term, Pi):
            # 检查参数类型
            param_type_type = self.infer(term.var_type)
            param_type_value = self.normalizer.normalize(param_type_type)
            if not isinstance(param_type_value, UniverseValue):
                raise TypeError(f"参数类型必须是一个Universe: {term.var_type}")
                
            # 在扩展的上下文中检查返回类型
            extended_context = self.context.extend(term.var_name, term.var_type)
            with self.in_context(extended_context):
                return_type_type = self.infer(term.body)
                return_type_value = self.normalizer.normalize(return_type_type)
                
            if not isinstance(return_type_value, UniverseValue):
                raise TypeError(f"返回类型必须是一个Universe: {term.body}")
                
            # Pi类型的类型是两个Universe的最大值
            param_level = param_type_value.level
            return_level = return_type_value.level
            return Universe(max(param_level, return_level))
            
        elif isinstance(term, Lambda):
            # Lambda表达式需要注解类型
            raise TypeError("无法推导Lambda表达式的类型，需要类型注解")
            
        elif isinstance(term, App):
            # 推导函数类型
            func_type = self.infer(term.func)
            func_type_normal = self.normalizer.normalize(func_type)
            
            if not isinstance(func_type, Pi):
                raise TypeError(f"应用的第一项必须是函数类型: {term.func}")
                
            # 检查参数类型
            if not self.check(term.arg, func_type.var_type):
                raise TypeError(f"参数类型不匹配: 期望 {func_type.var_type}，实际 {term.arg}")
                
            # 替换返回类型中的变量
            return self.substitute(func_type.body, term.arg, func_type.var_name)
                
        raise TypeError(f"无法推导类型: {term}")
        
    def check(self, term: Term, expected_type: Term) -> bool:
        """检查项是否具有预期类型"""
        # 特殊处理Universe的情况
        if isinstance(term, Universe):
            if not isinstance(expected_type, Universe):
                raise TypeError(f"类型宇宙必须是另一个类型宇宙的类型: {term}")
            if term.level >= expected_type.level:
                raise TypeError(f"类型宇宙层级错误: Type_{term.level} 不能是 Type_{expected_type.level} 的类型")
            return True

        # 首先检查expected_type是否是一个有效的类型
        try:
            type_type = self.infer(expected_type)
            if not isinstance(self.normalizer.normalize(type_type), UniverseValue):
                raise TypeError(f"期望的类型 {expected_type} 不是一个有效的类型")
        except TypeError as e:
            raise TypeError(f"无效的类型: {e}")

        if isinstance(term, Lambda):
            if not isinstance(expected_type, Pi):
                raise TypeError("Lambda表达式的类型必须是Pi类型")
            
            # 检查Lambda表达式
            extended_context = self.context.extend(expected_type.var_name, expected_type.var_type)
            with self.in_context(extended_context):
                if not self.check(term.body, expected_type.body):
                    raise TypeError(f"Lambda体类型不匹配: 期望 {expected_type.body}")
            return True
            
        try:
            actual_type = self.infer(term)
        except TypeError as e:
            raise TypeError(f"无法推导类型: {e}")
        
        if not self.is_equal(actual_type, expected_type):
            raise TypeError(f"类型不匹配: 期望 {expected_type}，实际 {actual_type}")
        return True
            
    def is_equal(self, t1: Term, t2: Term) -> bool:
        """检查两个类型是否相等（通过规范化比较）"""
        # 特殊处理Universe的情况
        if isinstance(t1, Universe) and isinstance(t2, Universe):
            return t1.level == t2.level
        
        n1 = self.normalizer.normalize(t1)
        n2 = self.normalizer.normalize(t2)
        return self.values_equal(n1, n2)
        
    def values_equal(self, v1: Value, v2: Value) -> bool:
        """比较两个值是否相等"""
        if isinstance(v1, UniverseValue) and isinstance(v2, UniverseValue):
            return v1.level == v2.level
            
        elif isinstance(v1, VarValue) and isinstance(v2, VarValue):
            return v1.name == v2.name
            
        elif isinstance(v1, ClosureValue) and isinstance(v2, ClosureValue):
            # 比较闭包的结构
            return (v1.var_name == v2.var_name and 
                   self.values_equal(self.evaluator.eval(v1.body), 
                                   self.evaluator.eval(v2.body)))
                                   
        elif isinstance(v1, NeutralValue) and isinstance(v2, NeutralValue):
            # 比较中性值的结构
            if not isinstance(v1.term, type(v2.term)):
                return False
            if len(v1.args) != len(v2.args):
                return False
            if isinstance(v1.term, Var) and isinstance(v2.term, Var):
                if v1.term.name != v2.term.name:
                    return False
            return all(self.values_equal(a1, a2) for a1, a2 in zip(v1.args, v2.args))
            
        return False
        
    def substitute(self, term: Term, value: Term, var_name: str) -> Term:
        """在项中替换变量"""
        if isinstance(term, Var):
            return value if term.name == var_name else term
            
        elif isinstance(term, Universe):
            return term
            
        elif isinstance(term, Pi):
            if term.var_name == var_name:
                return term
            new_var_type = self.substitute(term.var_type, value, var_name)
            new_body = self.substitute(term.body, value, var_name)
            return Pi(term.var_name, new_var_type, new_body)
            
        elif isinstance(term, Lambda):
            if term.var_name == var_name:
                return term
            new_var_type = self.substitute(term.var_type, value, var_name)
            new_body = self.substitute(term.body, value, var_name)
            return Lambda(term.var_name, new_var_type, new_body)
            
        elif isinstance(term, App):
            new_func = self.substitute(term.func, value, var_name)
            new_arg = self.substitute(term.arg, value, var_name)
            return App(new_func, new_arg)
            
        return term
        
    def in_context(self, new_context):
        """上下文管理器"""
        class ContextManager:
            def __init__(self, checker, context):
                self.checker = checker
                self.new_context = context
                self.old_context = None
                
            def __enter__(self):
                self.old_context = self.checker.context
                self.checker.context = self.new_context
                
            def __exit__(self, exc_type, exc_val, exc_tb):
                self.checker.context = self.old_context
                
        return ContextManager(self, new_context)
from ..syntax.terms import *
from .normalizer import Normalizer
from ..context import Context

class TypeChecker:
    def __init__(self):
        self.context = Context()
        self.normalizer = Normalizer()
    
    def check(self, term: Term, expected_type: Term) -> bool:
        """检查term是否具有expected_type类型"""
        actual_type = self.infer(term)
        return self.is_equal(actual_type, expected_type)
    
    def infer(self, term: Term) -> Term:
        """推导term的类型"""
        # ... (保持原来的实现) ...

    def is_equal(self, t1: Term, t2: Term) -> bool:
        """检查两个项是否相等（包括alpha等价性）"""
        # 使用规范化来检查等价性
        n1 = self.normalizer.normalize(t1)
        n2 = self.normalizer.normalize(t2)
        return self.syntactic_equal(n1, n2)
    
    def syntactic_equal(self, t1: Term, t2: Term) -> bool:
        """语法层面的相等性检查"""
        if type(t1) != type(t2):
            return False
            
        if isinstance(t1, Var):
            return t1.name == t2.name
            
        elif isinstance(t1, Universe):
            return t1.level == t2.level
            
        elif isinstance(t1, Pi):
            # 重命名参数以确保一致性
            fresh_name = self.normalizer.fresh_name(t1.param_name)
            t1_return = self.substitute(t1.return_type, t1.param_name, Var(fresh_name))
            t2_return = self.substitute(t2.return_type, t2.param_name, Var(fresh_name))
            return (self.syntactic_equal(t1.param_type, t2.param_type) and
                   self.syntactic_equal(t1_return, t2_return))
                   
        elif isinstance(t1, Lambda):
            # 类似Pi的处理
            fresh_name = self.normalizer.fresh_name(t1.param_name)
            t1_body = self.substitute(t1.body, t1.param_name, Var(fresh_name))
            t2_body = self.substitute(t2.body, t2.param_name, Var(fresh_name))
            return (self.syntactic_equal(t1.param_type, t2.param_type) and
                   self.syntactic_equal(t1_body, t2_body))
                   
        elif isinstance(t1, Apply):
            return (self.syntactic_equal(t1.func, t2.func) and
                   self.syntactic_equal(t1.arg, t2.arg))
                   
        return False 
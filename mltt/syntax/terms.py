from dataclasses import dataclass
from typing import Union

@dataclass
class Term:
    """基础项类型"""
    pass

@dataclass
class Var(Term):
    """变量"""
    name: str

    def __str__(self):
        return self.name

@dataclass(eq=False)
class Universe(Term):
    """类型宇宙"""
    def __init__(self, level: int):
        self.level = level
        
    def __str__(self):
        return f"Type_{self.level}"
        
    def __repr__(self):
        return f"Universe(level={self.level})"
        
    def __eq__(self, other):
        if not isinstance(other, Universe):
            return False
        return self.level == other.level

@dataclass
class Pi(Term):
    """依赖函数类型"""
    def __init__(self, var_name: str, var_type: Term, body: Term):
        self.var_name = var_name
        self.var_type = var_type
        self.body = body
        
    def __str__(self):
        return f"Π({self.var_name} : {self.var_type}).{self.body}"
        
    def __repr__(self):
        return f"Pi(var_name='{self.var_name}', var_type=Universe(level=0), body=Var(name='{self.var_name}'))"
        
    def __eq__(self, other):
        if not isinstance(other, Pi):
            return False
        return (self.var_name == other.var_name and
                self.var_type == other.var_type and
                self.body == other.body)

@dataclass
class Lambda(Term):
    """Lambda 抽象"""
    def __init__(self, var_name: str, var_type: Term, body: Term):
        self.var_name = var_name
        self.var_type = var_type
        self.body = body
        
    def __str__(self):
        return f"λ({self.var_name} : {self.var_type}).{self.body}"
        
    def __repr__(self):
        return f"Lambda(var_name='{self.var_name}', var_type=Universe(level=0), body=Var(name='{self.var_name}'))"
        
    def __eq__(self, other):
        if not isinstance(other, Lambda):
            return False
        return (self.var_name == other.var_name and
                self.var_type == other.var_type and
                self.body == other.body)

@dataclass
class App(Term):
    """函数应用"""
    def __init__(self, func: Term, arg: Term):
        self.func = func
        self.arg = arg
        
    def __str__(self):
        if isinstance(self.func, Lambda):
            return f"({self.func}) {self.arg}"
        return f"{self.func} {self.arg}"
        
    def __repr__(self):
        return f"App(func={repr(self.func)}, arg={repr(self.arg)})"
        
    def __eq__(self, other):
        if not isinstance(other, App):
            return False
        return self.func == other.func and self.arg == other.arg 
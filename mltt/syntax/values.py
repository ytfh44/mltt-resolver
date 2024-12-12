from dataclasses import dataclass
from typing import Dict, List, Optional
from .terms import Term, App

@dataclass
class Value:
    """值的基类"""
    pass

@dataclass
class VarValue(Value):
    """变量值"""
    def __init__(self, name: str):
        self.name = name
        
    def __str__(self):
        return self.name
        
    def __repr__(self):
        return f"VarValue(name='{self.name}')"
        
    def __eq__(self, other):
        if not isinstance(other, VarValue):
            return False
        return self.name == other.name

@dataclass
class UniverseValue(Value):
    """类型宇宙值"""
    def __init__(self, level: int):
        self.level = level
        
    def __str__(self):
        return f"Type_{self.level}"
        
    def __repr__(self):
        return f"UniverseValue(level={self.level})"
        
    def __eq__(self, other):
        if not isinstance(other, UniverseValue):
            return False
        return self.level == other.level

@dataclass
class ClosureValue(Value):
    """闭包值"""
    def __init__(self, env: dict, var_name: str, body: Term):
        self.env = env
        self.var_name = var_name
        self.body = body
        
    def __str__(self):
        return f"λ (x). ..."
        
    def __repr__(self):
        return f"ClosureValue(env={self.env}, var_name='{self.var_name}', body={repr(self.body)})"
        
    def __eq__(self, other):
        if not isinstance(other, ClosureValue):
            return False
        return (self.var_name == other.var_name and
                self.body == other.body)

@dataclass
class NeutralValue(Value):
    """中性值"""
    def __init__(self, term: Term, args: list[Value]):
        self.term = term
        self.args = args
        
    def __str__(self):
        if isinstance(self.term, App):
            return str(self.term)
        if not self.args:
            return str(self.term)
        return " ".join([str(self.term)] + [str(arg) for arg in self.args])
        
    def __repr__(self):
        return f"NeutralValue(term={repr(self.term)}, args={self.args})"
        
    def __eq__(self, other):
        if not isinstance(other, NeutralValue):
            return False
        return (self.term == other.term and
                self.args == other.args) 
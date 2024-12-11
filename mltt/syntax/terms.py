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

@dataclass
class Universe(Term):
    """Universe类型 (Type_n)"""
    level: int

    def __str__(self):
        return f"Type_{self.level}"

@dataclass
class Pi(Term):
    """依赖函数类型 (Π)"""
    var_name: str
    var_type: 'Term'
    body: 'Term'

    def __str__(self):
        return f"Π ({self.var_name} : {self.var_type}). {self.body}"

@dataclass
class Lambda(Term):
    """Lambda抽象"""
    var_name: str
    var_type: 'Term'
    body: 'Term'

    def __str__(self):
        return f"λ ({self.var_name} : {self.var_type}). {self.body}"

@dataclass
class App(Term):
    """函数应用"""
    func: 'Term'
    arg: 'Term'

    def __str__(self):
        return f"{self.func} {self.arg}" 
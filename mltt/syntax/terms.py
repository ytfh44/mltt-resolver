from dataclasses import dataclass
from typing import Union

@dataclass
class Var:
    """变量"""
    name: str

@dataclass
class Universe:
    """Universe类型 (Type_n)"""
    level: int

@dataclass
class Pi:
    """依赖函数类型 (Π)"""
    param_name: str
    param_type: 'Term'
    return_type: 'Term'

@dataclass
class Lambda:
    """Lambda抽象"""
    param_name: str
    param_type: 'Term'
    body: 'Term'

@dataclass
class Apply:
    """函数应用"""
    func: 'Term'
    arg: 'Term'

# 项的类型定义
Term = Union[Var, Universe, Pi, Lambda, Apply] 
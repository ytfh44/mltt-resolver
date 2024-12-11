from dataclasses import dataclass
from typing import Dict, Optional
from .terms import Term

@dataclass
class Value:
    """求值后的值"""
    pass

@dataclass
class VarValue(Value):
    """变量值"""
    name: str

@dataclass
class UniverseValue(Value):
    """Universe值"""
    level: int

@dataclass
class ClosureValue(Value):
    """闭包值 - 用于Lambda表达式"""
    env: Dict[str, 'Value']
    param_name: str
    body: Term

@dataclass
class NeutralValue(Value):
    """中性值 - 无法进一步规约的表达式"""
    head: Term
    args: list[Term] 
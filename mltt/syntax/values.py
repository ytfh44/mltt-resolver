from dataclasses import dataclass
from typing import Dict, List, Optional
from .terms import Term

@dataclass
class Value:
    """值的基类"""
    pass

@dataclass
class VarValue(Value):
    """变量值"""
    name: str

    def __str__(self):
        return self.name

@dataclass
class UniverseValue(Value):
    """Universe值"""
    level: int

    def __str__(self):
        return f"Type₀" if self.level == 0 else f"Type_{self.level}"

@dataclass
class ClosureValue(Value):
    """闭包值"""
    env: Dict[str, Value]
    var_name: str
    body: Term

    def __str__(self):
        return f"λ ({self.var_name}). ..."

@dataclass
class NeutralValue(Value):
    """中性值（不能被进一步规约的表达式）"""
    term: Term
    args: List[Value]

    def __str__(self):
        if not self.args:
            return str(self.term)
        args_str = " ".join(str(arg) for arg in self.args)
        return f"{self.term} {args_str}" 
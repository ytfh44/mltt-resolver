from dataclasses import dataclass
from typing import Dict, Optional
from .syntax import Term

@dataclass
class Context:
    bindings: Dict[str, Term]
    
    def __init__(self):
        self.bindings = {}
    
    def extend(self, name: str, type_: Term) -> 'Context':
        new_ctx = Context()
        new_ctx.bindings = self.bindings.copy()
        new_ctx.bindings[name] = type_
        return new_ctx
    
    def lookup(self, name: str) -> Optional[Term]:
        return self.bindings.get(name) 
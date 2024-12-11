from dataclasses import dataclass
from typing import List, Optional, Union

@dataclass
class Var:
    name: str
    
@dataclass 
class Universe:
    level: int  # Type_0, Type_1, etc.

@dataclass
class Pi:
    param_name: str
    param_type: 'Term'
    return_type: 'Term'

@dataclass
class Lambda:
    param_name: str
    param_type: 'Term'
    body: 'Term'

@dataclass
class Apply:
    func: 'Term'
    arg: 'Term'

# Values in our type theory
Term = Union[Var, Universe, Pi, Lambda, Apply] 
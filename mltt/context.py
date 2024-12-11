from typing import Dict, Optional
from .syntax.terms import Term

class Context:
    """类型上下文，用于存储变量的类型信息"""
    
    def __init__(self):
        self.vars: Dict[str, Term] = {}
        
    def add_var(self, name: str, type_: Term) -> None:
        """添加变量及其类型到上下文"""
        self.vars[name] = type_
        
    def get_var_type(self, name: str) -> Optional[Term]:
        """获取变量的类型"""
        return self.vars.get(name)
        
    def has_var(self, name: str) -> bool:
        """检查变量是否在上下文中"""
        return name in self.vars
        
    def extend(self, name: str, type_: Term) -> 'Context':
        """创建一个新的扩展上下文"""
        new_context = Context()
        new_context.vars = self.vars.copy()
        new_context.add_var(name, type_)
        return new_context
        
    def __str__(self) -> str:
        """字符串表示"""
        items = [f"{name}: {type_}" for name, type_ in self.vars.items()]
        return ", ".join(items) 
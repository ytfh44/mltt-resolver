from typing import Dict, Optional
from .syntax.terms import Term, Universe, Pi, Var, Lambda, App
from copy import deepcopy

class Context:
    """类型上下文，用于存储变量的类型信息"""
    
    def __init__(self):
        self.vars: Dict[str, Term] = {}
        
    def add_var(self, name: str, type_: Term) -> None:
        """添加变量及其类型到上下文
        创建类型的完全独立副本，确保类型的属性不会被其他操作影响
        """
        # 创建完全独立的类型副本
        if isinstance(type_, Universe):
            self.vars[name] = Universe(level=type_.level)
        elif isinstance(type_, Pi):
            self.vars[name] = Pi(
                var_name=type_.var_name,
                var_type=deepcopy(type_.var_type),
                body=deepcopy(type_.body)
            )
        else:
            self.vars[name] = deepcopy(type_)
        
    def get_var_type(self, name: str) -> Optional[Term]:
        """获取变量的类型
        返回类型的副本，确保原始类型不会被修改
        """
        type_ = self.vars.get(name)
        if type_ is None:
            return None
        # 创建完全独立的类型副本
        if isinstance(type_, Universe):
            return Universe(level=type_.level)
        elif isinstance(type_, Pi):
            return Pi(
                var_name=type_.var_name,
                var_type=deepcopy(type_.var_type),
                body=deepcopy(type_.body)
            )
        else:
            return deepcopy(type_)
        
    def has_var(self, name: str) -> bool:
        """检查变量是否在上下文中"""
        return name in self.vars
        
    def extend(self, name: str, type_: Term) -> 'Context':
        """创建一个新的扩展上下文
        确保新上下文中的类型与原上下文中的类型完全独立
        如果变量名已存在，则更新其类型
        """
        new_context = Context()
        # 复制现有变量
        for var_name, var_type in self.vars.items():
            if var_name != name:  # 只复制不同名的变量
                if isinstance(var_type, Universe):
                    new_context.vars[var_name] = Universe(level=var_type.level)
                elif isinstance(var_type, Pi):
                    new_context.vars[var_name] = Pi(
                        var_name=var_type.var_name,
                        var_type=deepcopy(var_type.var_type),
                        body=deepcopy(var_type.body)
                    )
                else:
                    new_context.vars[var_name] = deepcopy(var_type)
        # 添加新变量
        new_context.add_var(name, type_)
        return new_context
        
    def __str__(self):
        """返回上下文的字符串表示。"""
        if not self.vars:
            return ""
        return ", ".join(f"{name}: {type_}" for name, type_ in self.vars.items()) 
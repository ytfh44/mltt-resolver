import pytest
from mltt.context import Context
from mltt.syntax.terms import *

def test_context_operations():
    """测试上下文操作"""
    ctx = Context()
    
    # 初始状态
    assert not ctx.has_var("x")
    assert ctx.get_var_type("x") is None
    assert str(ctx) == ""
    
    # 添加变量
    type0 = Universe(0)
    ctx.add_var("x", type0)
    assert ctx.has_var("x")
    assert ctx.get_var_type("x") == type0
    assert str(ctx) == "x: Type_0"
    
    # 扩展上下文
    type1 = Universe(1)
    new_ctx = ctx.extend("y", type1)
    assert new_ctx.has_var("x")
    assert new_ctx.has_var("y")
    assert new_ctx.get_var_type("x") == type0
    assert new_ctx.get_var_type("y") == type1
    assert str(new_ctx) == "x: Type_0, y: Type_1"
    
    # 原上下文不变
    assert ctx.has_var("x")
    assert not ctx.has_var("y")
    assert str(ctx) == "x: Type_0" 
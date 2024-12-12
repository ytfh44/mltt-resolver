import pytest
from mltt.syntax.values import *
from mltt.syntax.terms import *

def test_value_str():
    """测试值的字符串表示"""
    # 变量值
    var = VarValue("x")
    assert str(var) == "x"
    
    # Universe值
    univ0 = UniverseValue(0)
    assert str(univ0) == "Type_0"
    univ1 = UniverseValue(1)
    assert str(univ1) == "Type_1"
    
    # 闭包值
    env = {"x": UniverseValue(0)}
    closure = ClosureValue(env, "x", Var("x"))
    assert str(closure) == "λ (x). ..."
    
    # 中性值
    neutral = NeutralValue(Var("x"), [])
    assert str(neutral) == "x"
    
    neutral_with_args = NeutralValue(Var("f"), [UniverseValue(0), VarValue("x")])
    assert str(neutral_with_args) == "f Type_0 x"

def test_value_repr():
    """测试值的repr表示"""
    # 变量值
    var = VarValue("x")
    assert repr(var) == "VarValue(name='x')"
    
    # Universe值
    univ = UniverseValue(0)
    assert repr(univ) == "UniverseValue(level=0)"
    
    # 闭包值
    env = {"x": UniverseValue(0)}
    closure = ClosureValue(env, "x", Var("x"))
    assert repr(closure) == "ClosureValue(env={'x': UniverseValue(level=0)}, var_name='x', body=Var(name='x'))"
    
    # 中性值
    neutral = NeutralValue(Var("x"), [])
    assert repr(neutral) == "NeutralValue(term=Var(name='x'), args=[])"
    
    neutral_with_args = NeutralValue(Var("f"), [UniverseValue(0), VarValue("x")])
    assert repr(neutral_with_args) == "NeutralValue(term=Var(name='f'), args=[UniverseValue(level=0), VarValue(name='x')])" 
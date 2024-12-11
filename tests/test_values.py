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
    assert str(univ0) == "Type₀"
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
    assert str(neutral_with_args) == "f Type₀ x" 
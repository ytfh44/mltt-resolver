import pytest
from mltt.core.normalizer import Normalizer
from mltt.core.evaluator import Evaluator
from mltt.syntax.terms import *
from mltt.syntax.values import *

def test_normalizer():
    """测试规范化器"""
    evaluator = Evaluator()
    normalizer = Normalizer(evaluator)
    
    # 规范化变量
    var = Var("x")
    result = normalizer.normalize(var)
    assert isinstance(result, VarValue)
    assert result.name == "x"
    
    # 规范化Universe
    univ = Universe(0)
    result = normalizer.normalize(univ)
    assert isinstance(result, UniverseValue)
    assert result.level == 0
    
    # 规范化Lambda
    lam = Lambda("x", Universe(0), Var("x"))
    result = normalizer.normalize(lam)
    assert isinstance(result, ClosureValue)
    assert result.var_name == "x"
    assert result.body == Var("x")
    
    # 规范化应用
    evaluator.env["x"] = UniverseValue(0)
    app = App(lam, Var("x"))
    result = normalizer.normalize(app)
    assert isinstance(result, UniverseValue)
    assert result.level == 0
    
    # 生成新的变量名
    name = normalizer.fresh_name("x")
    assert name == "x'" 
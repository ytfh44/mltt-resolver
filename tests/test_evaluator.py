import pytest
from mltt.core.evaluator import Evaluator
from mltt.syntax.terms import *
from mltt.syntax.values import *

def test_evaluator():
    """测试求值器"""
    evaluator = Evaluator()
    
    # 变量求值
    var = Var("x")
    assert isinstance(evaluator.eval(var), VarValue)
    assert evaluator.eval(var).name == "x"
    
    # Universe求值
    univ = Universe(0)
    assert isinstance(evaluator.eval(univ), UniverseValue)
    assert evaluator.eval(univ).level == 0
    
    # Lambda求值
    lam = Lambda("x", Universe(0), Var("x"))
    closure = evaluator.eval(lam)
    assert isinstance(closure, ClosureValue)
    assert closure.var_name == "x"
    assert closure.body == Var("x")
    
    # 应用求值（闭包）
    evaluator.env["x"] = UniverseValue(0)
    app = App(lam, Var("x"))
    result = evaluator.eval(app)
    assert isinstance(result, UniverseValue)
    assert result.level == 0
    
    # 应用求值（中性值）
    evaluator.env.clear()  # 清除环境
    app = App(Var("f"), Var("x"))
    result = evaluator.eval(app)
    assert isinstance(result, NeutralValue)
    assert isinstance(result.term, App)
    assert len(result.args) == 1
    assert isinstance(result.args[0], VarValue)
    
    # 其他项求值为中性值
    pi = Pi("x", Universe(0), Var("x"))
    result = evaluator.eval(pi)
    assert isinstance(result, NeutralValue)
    assert result.term == pi
    assert len(result.args) == 0

def test_environment():
    """测试环境管理"""
    evaluator = Evaluator()
    
    # 初始环境
    assert evaluator.eval(Var("x")).name == "x"
    
    # 添加绑定
    evaluator.env["x"] = UniverseValue(0)
    assert isinstance(evaluator.eval(Var("x")), UniverseValue)
    assert evaluator.eval(Var("x")).level == 0
    
    # 临时环境
    new_env = {"x": UniverseValue(1)}
    with evaluator.in_env(new_env):
        assert isinstance(evaluator.eval(Var("x")), UniverseValue)
        assert evaluator.eval(Var("x")).level == 1
    
    # 恢复原环境
    assert isinstance(evaluator.eval(Var("x")), UniverseValue)
    assert evaluator.eval(Var("x")).level == 0 
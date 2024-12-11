import pytest
from mltt.core.evaluator import Evaluator
from mltt.syntax.terms import *
from mltt.syntax.values import *

def test_evaluator_universe():
    """Test evaluation of universe types"""
    evaluator = Evaluator()
    
    # Evaluate Type₀
    type0 = Universe(0)
    value = evaluator.eval(type0)
    assert isinstance(value, UniverseValue)
    assert value.level == 0

def test_evaluator_variable():
    """Test evaluation of variables"""
    evaluator = Evaluator()
    
    # Evaluate free variable
    var = Var("x")
    value = evaluator.eval(var)
    assert isinstance(value, VarValue)
    assert value.name == "x"

def test_evaluator_lambda():
    """Test evaluation of lambda abstractions"""
    evaluator = Evaluator()
    
    # λ (x : A). x
    lam = Lambda("x", Var("A"), Var("x"))
    value = evaluator.eval(lam)
    assert isinstance(value, ClosureValue)
    assert value.var_name == "x"
    assert value.body == Var("x")

def test_evaluator_application():
    """Test evaluation of applications"""
    evaluator = Evaluator()
    
    # (λ (x : A). x) y
    lam = Lambda("x", Var("A"), Var("x"))
    app = App(lam, Var("y"))
    value = evaluator.eval(app)
    assert isinstance(value, VarValue)
    assert value.name == "y"

def test_evaluator_pi():
    """Test evaluation of Pi types"""
    evaluator = Evaluator()
    
    # Π (x : A). B
    pi = Pi("x", Var("A"), Var("B"))
    value = evaluator.eval(pi)
    assert isinstance(value, NeutralValue)
    assert isinstance(value.term, Pi)
    assert value.term.var_name == "x"
    assert value.term.var_type == Var("A")
    assert value.term.body == Var("B") 
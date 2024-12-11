import pytest
from mltt.syntax.terms import *
from mltt.core.checker import TypeChecker

def test_universe_creation():
    """Test creation of universe levels"""
    u0 = Universe(0)
    u1 = Universe(1)
    assert u0.level == 0
    assert u1.level == 1
    assert str(u0) == "Type₀"

def test_variable():
    """Test variable creation and representation"""
    var = Var("x")
    assert var.name == "x"
    assert str(var) == "x"

def test_lambda():
    """Test lambda abstraction"""
    type0 = Universe(0)
    var_x = Var("x")
    lambda_term = Lambda("x", type0, var_x)
    assert lambda_term.var_name == "x"
    assert lambda_term.var_type == type0
    assert lambda_term.body == var_x

def test_pi_type():
    """Test Pi type construction"""
    type0 = Universe(0)
    var_a = Var("A")
    pi_type = Pi("A", type0, var_a)
    assert pi_type.var_name == "A"
    assert pi_type.var_type == type0
    assert pi_type.body == var_a

def test_application():
    """Test function application"""
    func = Var("f")
    arg = Var("x")
    app = App(func, arg)
    assert app.func == func
    assert app.arg == arg
    assert str(app) == "f x" 
import pytest
from mltt.syntax import *
from mltt.syntax.terms import *

def test_universe_creation():
    """Test universe type creation"""
    type0 = Universe(0)
    assert type0.level == 0

def test_variable():
    """Test variable creation"""
    var = Var("x")
    assert var.name == "x"

def test_lambda():
    """Test lambda abstraction"""
    type0 = Universe(0)
    var_type = Var("A")
    var = Var("x")
    lam = Lambda("x", var_type, var)
    assert lam.var_name == "x"
    assert lam.var_type == var_type
    assert lam.body == var

def test_pi_type():
    """Test dependent function type (Pi type)"""
    type0 = Universe(0)
    var_type = Var("A")
    var = Var("x")
    pi = Pi("x", var_type, var)
    assert pi.var_name == "x"
    assert pi.var_type == var_type
    assert pi.body == var

def test_application():
    """Test function application"""
    func = Var("f")
    arg = Var("x")
    app = App(func, arg)
    assert app.func == func
    assert app.arg == arg

def test_syntax_str():
    """Test string representation of syntax terms"""
    type0 = Universe(0)
    assert str(type0) == "Type_0"
    
    var = Var("x")
    assert str(var) == "x"
    
    lam = Lambda("x", Var("A"), Var("x"))
    assert str(lam) == "λ (x : A). x"
    
    pi = Pi("x", Var("A"), Var("B"))
    assert str(pi) == "Π (x : A). B"
    
    app = App(Var("f"), Var("x"))
    assert str(app) == "f x"

def test_syntax_eq():
    """Test equality comparison of syntax terms"""
    assert Universe(0) == Universe(0)
    assert Universe(0) != Universe(1)
    
    assert Var("x") == Var("x")
    assert Var("x") != Var("y")
    
    assert Lambda("x", Var("A"), Var("x")) == Lambda("x", Var("A"), Var("x"))
    assert Lambda("x", Var("A"), Var("x")) != Lambda("y", Var("A"), Var("y"))
    
    assert Pi("x", Var("A"), Var("B")) == Pi("x", Var("A"), Var("B"))
    assert Pi("x", Var("A"), Var("B")) != Pi("y", Var("A"), Var("B"))
    
    assert App(Var("f"), Var("x")) == App(Var("f"), Var("x"))
    assert App(Var("f"), Var("x")) != App(Var("g"), Var("x"))
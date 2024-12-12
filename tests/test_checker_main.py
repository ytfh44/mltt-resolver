import pytest
from mltt.checker import TypeChecker, TypeError as MLTTTypeError
from mltt.syntax.terms import *
from mltt.context import Context

def test_var_type_inference():
    """Test variable type inference"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # Add variable to context
    checker.context.add_var("x", type0)
    
    # Test variable lookup
    var = Var("x")
    assert checker.infer(var) == type0
    
    # Test unbound variable
    with pytest.raises(MLTTTypeError, match="Unbound variable"):
        checker.infer(Var("y"))

def test_universe_type_inference():
    """Test universe type inference"""
    checker = TypeChecker()
    
    # Type_0 : Type_1
    type0 = Universe(0)
    assert checker.infer(type0) == Universe(1)
    
    # Type_1 : Type_2
    type1 = Universe(1)
    assert checker.infer(type1) == Universe(2)

def test_pi_type_inference():
    """Test Pi type inference"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # Π (x : Type_0). Type_0
    pi = Pi("x", type0, type0)
    assert checker.infer(pi) == Universe(1)
    
    # Invalid parameter type
    with pytest.raises(MLTTTypeError, match="Unbound variable"):
        checker.infer(Pi("x", Var("A"), type0))
    
    # Invalid return type
    with pytest.raises(MLTTTypeError, match="Unbound variable"):
        checker.infer(Pi("x", type0, Var("B")))

def test_lambda_type_inference():
    """Test lambda type inference"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # λ (x : Type_0). x
    lam = Lambda("x", type0, Var("x"))
    pi_type = checker.infer(lam)
    assert isinstance(pi_type, Pi)
    assert pi_type.var_name == "x"
    assert pi_type.var_type == type0
    
    # Test that the body type is correct
    with checker.in_context(checker.context.extend("x", type0)):
        assert checker.infer(Var("x")) == type0
    
    # Invalid parameter type
    with pytest.raises(MLTTTypeError, match="Unbound variable"):
        checker.infer(Lambda("x", Var("A"), Var("x")))

def test_application_type_inference():
    """Test application type inference"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # Set up context
    var_a = Var("A")
    checker.context.add_var("A", type0)
    checker.context.add_var("x", var_a)
    
    # (λ (y : A). y) x
    lam = Lambda("y", var_a, Var("y"))
    app = App(lam, Var("x"))
    assert checker.infer(app) == var_a
    
    # Invalid function
    with pytest.raises(MLTTTypeError, match="Cannot apply non-function"):
        checker.infer(App(type0, Var("x")))
    
    # Type mismatch
    with pytest.raises(MLTTTypeError, match="Argument type mismatch"):
        checker.infer(App(lam, type0))

def test_substitution():
    """Test variable substitution"""
    checker = TypeChecker()
    
    # Simple variable substitution
    assert checker.substitute(Var("x"), "x", Var("y")) == Var("y")
    assert checker.substitute(Var("x"), "y", Var("z")) == Var("x")
    
    # Pi type substitution
    pi = Pi("x", Var("A"), Var("x"))
    subst = checker.substitute(pi, "A", Universe(0))
    assert isinstance(subst, Pi)
    assert subst.var_name == "x"
    assert subst.var_type == Universe(0)
    assert subst.body == Var("x")
    
    # Lambda substitution
    lam = Lambda("x", Var("A"), Var("x"))
    subst = checker.substitute(lam, "A", Universe(0))
    assert isinstance(subst, Lambda)
    assert subst.var_name == "x"
    assert subst.var_type == Universe(0)
    assert subst.body == Var("x")
    
    # Application substitution
    app = App(Var("f"), Var("x"))
    subst = checker.substitute(app, "f", Var("g"))
    assert isinstance(subst, App)
    assert subst.func == Var("g")
    assert subst.arg == Var("x")

def test_context_manager():
    """Test context manager functionality"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # Original context
    checker.context.add_var("x", type0)
    assert checker.context.get_var_type("x") == type0
    
    # New context
    new_ctx = Context()
    new_ctx.add_var("y", type0)
    
    # Test context switching
    with checker.in_context(new_ctx):
        assert checker.context.get_var_type("x") is None
        assert checker.context.get_var_type("y") == type0
    
    # Back to original context
    assert checker.context.get_var_type("x") == type0
    assert checker.context.get_var_type("y") is None 
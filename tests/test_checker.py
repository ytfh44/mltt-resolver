import pytest
from mltt.syntax.terms import *
from mltt.core.checker import TypeChecker, TypeError
from mltt.context import Context
from functools import wraps

def expect_type_error(func):
    """装饰器：期望测试函数抛出TypeError"""
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            func(*args, **kwargs)
            pytest.fail(f"Expected TypeError in {func.__name__}")
        except TypeError:
            pass  # 测试通过
    return wrapper

def test_identity_type_check():
    """Test type checking of the identity function"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # id : Π (A : Type₀). Π (x : A). A
    id_type = Pi("A", type0, Pi("x", Var("A"), Var("A")))
    
    # id = λ (A : Type₀). λ (x : A). x
    id_term = Lambda("A", type0, Lambda("x", Var("A"), Var("x")))
    
    assert checker.check(id_term, id_type)

def test_application_type_check():
    """Test type checking of function application"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # Create a simple function type A -> A
    a_var = Var("A")
    func_type = Pi("x", a_var, a_var)
    
    # Create a function application
    func = Var("f")
    arg = Var("a")
    app = App(func, arg)
    
    # Set up context
    context = Context()
    context.add_var("A", type0)
    context.add_var("a", a_var)
    context.add_var("f", func_type)
    
    checker.context = context
    assert checker.check(app, a_var)

@expect_type_error
def test_invalid_type():
    """Test that invalid types are rejected"""
    checker = TypeChecker()
    type0 = Universe(0)
    checker.check(Var("x"), Var("y"))

@expect_type_error
def test_universe_hierarchy_invalid():
    """Test that invalid universe hierarchy is rejected"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    checker.check(type1, type0)

def test_universe_hierarchy_valid():
    """Test that valid universe hierarchy is accepted"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    type2 = Universe(2)
    
    # Type₀ : Type₁
    assert checker.check(type0, type1)
    # Type₁ : Type₂
    assert checker.check(type1, type2)
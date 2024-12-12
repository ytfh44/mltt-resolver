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

@expect_type_error
def test_invalid_return_type():
    """测试返回类型不是 Universe 类型的情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建一��返回类型不是 Universe 的 Pi 类型
    invalid_pi = Pi("x", type0, Var("x"))  # 返回类型是变量，不是 Universe
    
    # 这应该抛出 TypeError
    checker.infer(invalid_pi)

@expect_type_error
def test_cannot_infer_type():
    """测试无法推断类型的情况"""
    checker = TypeChecker()
    
    # 创建一个无法推断类型的项（比如一个未知变量的应用）
    invalid_term = App(Var("unknown"), Var("x"))
    
    # 这应该抛出 TypeError
    checker.infer(invalid_term)

def test_context_manager():
    """测试上下文管理器的使用"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建一个新的上下文
    context = Context()
    context.add_var("A", type0)
    
    # 使用上下文管理器
    with checker.in_context(context):
        # 在新上下文中，A 应该是一个有效的类型
        var_a = Var("A")
        assert checker.infer(var_a) == type0
    
    # 在原上下文中，A 应该不存在
    with pytest.raises(TypeError):
        checker.infer(Var("A"))

@expect_type_error
def test_invalid_application():
    """测试参数类型不匹配的情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建一个函数类型 (A : Type₀) → A
    id_type = Pi("A", type0, Var("A"))
    
    # 创建一个函数
    id_func = Lambda("A", type0, Lambda("x", Var("A"), Var("x")))
    
    # 添加到上下文
    context = Context()
    context.add_var("id", id_type)
    checker.context = context
    
    # 尝试用错误的参数类型调用函数
    invalid_app = App(Var("id"), type0)  # 应该是一个类型，而不是 Universe
    checker.check(invalid_app, type0)

@expect_type_error
def test_invalid_lambda_body():
    """测试 Lambda 体类型不匹配的情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建一个函数类型 (A : Type₀) → A → A
    func_type = Pi("A", type0, Pi("x", Var("A"), Var("A")))
    
    # 创建一个 Lambda，但其体的类型不匹配
    invalid_lambda = Lambda("A", type0, Lambda("x", Var("A"), type0))  # 返回 Type₀ 而不是 A
    
    # 这应该抛出 TypeError
    checker.check(invalid_lambda, func_type)

@expect_type_error
def test_invalid_return_type_complex():
    """测试更复杂的返回类型不是 Universe 类型的情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 创建一个嵌套的 Pi 类型，内部返回类型不是 Universe
    invalid_pi = Pi("A", type1, Pi("x", Var("A"), type0))  # 返回 Type₀ 而不是一个类型
    
    # 这应该抛出 TypeError
    checker.infer(invalid_pi)

@expect_type_error
def test_cannot_infer_type_complex():
    """测试更复杂的无法推断类型的情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建一个复杂的无法推断类型的项
    context = Context()
    context.add_var("A", type0)
    checker.context = context
    
    # 尝试对一个类型应用另一个类型
    invalid_term = App(type0, type0)  # Universe 不是函数类型
    
    # 这应该抛出 TypeError
    checker.infer(invalid_term)

def test_context_manager_nested():
    """测试嵌套的上下文管理器使用"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 创建两个上下文
    context1 = Context()
    context1.add_var("A", type0)
    
    context2 = Context()
    context2.add_var("B", type1)
    
    # 嵌套使用上下文管理器
    with checker.in_context(context1):
        assert checker.infer(Var("A")) == type0
        
        with checker.in_context(context2):
            assert checker.infer(Var("B")) == type1
            # A 在这里应该不可见
            with pytest.raises(TypeError):
                checker.infer(Var("A"))
        
        # 恢复到 context1，应该可以��� A 但看不到 B
        assert checker.infer(Var("A")) == type0
        with pytest.raises(TypeError):
            checker.infer(Var("B"))

@expect_type_error
def test_invalid_application_complex():
    """测试更复杂的参数类型不匹配情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建一个依赖函数类型 (A : Type₀) → (x : A) → A
    id_type = Pi("A", type0, Pi("x", Var("A"), Var("A")))
    
    # 创建一个函数
    id_func = Lambda("A", type0, Lambda("x", Var("A"), Var("x")))
    
    # 添加到上下文
    context = Context()
    context.add_var("id", id_type)
    checker.context = context
    
    # 尝试用错误的参数类型调用函数
    invalid_app = App(App(Var("id"), type0), type0)  # 第二个参数应该是 type0 的实例，而不是 type0 本身
    
    # 这应该抛出 TypeError
    checker.check(invalid_app, type0)

@expect_type_error
def test_invalid_lambda_body_complex():
    """测试更复杂的 Lambda 体类型不匹配情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建一个复杂的函数类型 (A : Type₀) → (x : A) → (y : A) → A
    func_type = Pi("A", type0, Pi("x", Var("A"), Pi("y", Var("A"), Var("A"))))
    
    # 创建一个 Lambda，但最层��回类型不匹配
    invalid_lambda = Lambda("A", type0, 
        Lambda("x", Var("A"), 
            Lambda("y", Var("A"), type0)))  # 返回 Type₀ 而不是 A
    
    # 这应该抛出 TypeError
    checker.check(invalid_lambda, func_type)

def test_evaluator():
    """测试求值器的功能"""
    from mltt.core.evaluator import Evaluator
    from mltt.syntax.terms import Var, Universe, Lambda, App
    from mltt.syntax.values import VarValue, UniverseValue, ClosureValue, NeutralValue
    
    evaluator = Evaluator()
    
    # 测试变量求值
    var = Var("x")
    var_value = evaluator.eval(var)
    assert isinstance(var_value, VarValue)
    assert var_value.name == "x"
    
    # 测试 Universe 求值
    universe = Universe(0)
    universe_value = evaluator.eval(universe)
    assert isinstance(universe_value, UniverseValue)
    assert universe_value.level == 0
    
    # 测试 Lambda 求值
    lambda_term = Lambda("x", Universe(0), Var("x"))
    lambda_value = evaluator.eval(lambda_term)
    assert isinstance(lambda_value, ClosureValue)
    assert lambda_value.var_name == "x"
    assert lambda_value.body == Var("x")
    
    # 测试应用求值（闭包）
    app = App(lambda_term, universe)
    app_value = evaluator.eval(app)
    assert isinstance(app_value, UniverseValue)
    assert app_value.level == 0
    
    # 测试应用求值（中性值）
    var_app = App(var, universe)
    var_app_value = evaluator.eval(var_app)
    assert isinstance(var_app_value, NeutralValue)
    assert isinstance(var_app_value.term, App)
    assert len(var_app_value.args) == 1
    assert isinstance(var_app_value.args[0], UniverseValue)

def test_evaluator_env():
    """测试求值器的环境管理"""
    from mltt.core.evaluator import Evaluator
    from mltt.syntax.terms import Var, Universe
    from mltt.syntax.values import VarValue, UniverseValue
    
    evaluator = Evaluator()
    
    # 测试环境管理器
    var = Var("x")
    universe = Universe(0)
    universe_value = evaluator.eval(universe)
    
    # 在新环境中求值
    with evaluator.in_env({"x": universe_value}):
        var_value = evaluator.eval(var)
        assert isinstance(var_value, UniverseValue)
        assert var_value.level == 0
    
    # 恢复到原环境
    var_value = evaluator.eval(var)
    assert isinstance(var_value, VarValue)
    assert var_value.name == "x"

def test_values():
    """测试值的功能"""
    from mltt.syntax.values import VarValue, UniverseValue, ClosureValue, NeutralValue
    from mltt.syntax.terms import Var, Universe, App
    
    # 测试 VarValue
    var_value = VarValue("x")
    assert str(var_value) == "x"
    assert repr(var_value) == "VarValue(name='x')"
    
    # 测试 UniverseValue
    universe_value = UniverseValue(0)
    assert str(universe_value) == "Type_0"
    assert repr(universe_value) == "UniverseValue(level=0)"
    
    # 测试 ClosureValue
    closure_value = ClosureValue({}, "x", Var("x"))
    assert str(closure_value) == "λ (x). ..."
    assert repr(closure_value) == "ClosureValue(env={}, var_name='x', body=Var(name='x'))"
    
    # 测试 NeutralValue
    neutral_value = NeutralValue(App(Var("f"), Var("x")), [VarValue("x")])
    assert str(neutral_value) == "f x"
    assert repr(neutral_value) == "NeutralValue(term=App(func=Var(name='f'), arg=Var(name='x')), args=[VarValue(name='x')])"

def test_terms():
    """测试项的功能"""
    from mltt.syntax.terms import Var, Universe, Pi, Lambda, App
    
    # 测试 Var
    var = Var("x")
    assert str(var) == "x"
    assert repr(var) == "Var(name='x')"
    
    # 测试 Universe
    universe = Universe(0)
    assert str(universe) == "Type_0"
    assert repr(universe) == "Universe(level=0)"
    
    # 测试 Pi
    pi = Pi("x", Universe(0), Var("x"))
    assert str(pi) == "Π(x : Type_0).x"
    assert repr(pi) == "Pi(var_name='x', var_type=Universe(level=0), body=Var(name='x'))"
    
    # 测试 Lambda
    lambda_term = Lambda("x", Universe(0), Var("x"))
    assert str(lambda_term) == "λ(x : Type_0).x"
    assert repr(lambda_term) == "Lambda(var_name='x', var_type=Universe(level=0), body=Var(name='x'))"
    
    # 测试 App
    app = App(lambda_term, var)
    assert str(app) == "(λ(x : Type_0).x) x"
    assert repr(app) == "App(func=Lambda(var_name='x', var_type=Universe(level=0), body=Var(name='x')), arg=Var(name='x'))"

def test_context():
    """测试上下文的功能"""
    from mltt.context import Context
    from mltt.syntax.terms import Universe, Var
    
    # 创建上下文
    context = Context()
    
    # 测试添加变量
    type0 = Universe(0)
    context.add_var("A", type0)
    assert context.get_var_type("A") == type0
    
    # 测试获取不存在的变量
    assert context.get_var_type("B") is None
    
    # 测试扩展上下文
    extended = context.extend("B", type0)
    assert extended.get_var_type("A") == type0
    assert extended.get_var_type("B") == type0
    
    # 测试原上下文不变
    assert context.get_var_type("B") is None
import pytest
from mltt.core.checker import TypeChecker, TypeError
from mltt.syntax.terms import *
from mltt.syntax.values import *
from mltt.context import Context

def test_universe_type_checking():
    """测试Universe类型检查"""
    checker = TypeChecker()
    
    # Type_0 : Type_1
    assert checker.check(Universe(0), Universe(1))
    
    # Type_1 : Type_2
    assert checker.check(Universe(1), Universe(2))
    
    # Type_2 不能是 Type_1 的类型
    with pytest.raises(TypeError, match="类型宇宙层级错误"):
        checker.check(Universe(2), Universe(1))
    
    # Type_0 不能是 Type_0 的类型
    with pytest.raises(TypeError, match="类型宇宙层级错误"):
        checker.check(Universe(0), Universe(0))
    
    # Universe必须是另一个Universe的类型
    with pytest.raises(TypeError, match="类型宇宙必须是另一个类型宇宙的类型"):
        checker.check(Universe(0), Var("x"))

def test_lambda_type_checking():
    """测试Lambda表达式类型检查"""
    checker = TypeChecker()
    
    # λ (x : Type_0). x : Π (x : Type_0). Type_0
    lam = Lambda("x", Universe(0), Var("x"))
    pi = Pi("x", Universe(0), Universe(0))
    assert checker.check(lam, pi)
    
    # Lambda表达式的类型必须是Pi类型
    with pytest.raises(TypeError, match="Lambda表达式的类型必须是Pi类型"):
        checker.check(lam, Universe(0))
    
    # Lambda体类型不匹配
    bad_pi = Pi("x", Universe(0), Universe(1))
    with pytest.raises(TypeError, match="类型不匹配: 期望 Type_1，实际 Type_0"):
        checker.check(lam, bad_pi)

def test_type_inference():
    """测试类型推导"""
    checker = TypeChecker()
    
    # 无法推导Lambda表达式的类型
    lam = Lambda("x", Universe(0), Var("x"))
    with pytest.raises(TypeError, match="无法推导Lambda表达式的类型"):
        checker.infer(lam)
    
    # 应用的第一项必须是函数类型
    app = App(Universe(0), Var("x"))
    with pytest.raises(TypeError, match="应用的第一项必须是函数类型"):
        checker.infer(app)
    
    # 参数类型不匹配
    checker.context.add_var("f", Pi("x", Universe(0), Var("x")))
    checker.context.add_var("y", Universe(1))
    app = App(Var("f"), Var("y"))
    with pytest.raises(TypeError, match="类型不匹配: 期望 Type_0，实际 Type_1"):
        checker.infer(app)

def test_invalid_types():
    """测试无效类型"""
    checker = TypeChecker()
    
    # 期望的类型不是一个有效的类型
    with pytest.raises(TypeError, match="无效的类型: 未绑定的变量: y"):
        checker.check(Var("x"), Var("y"))
    
    # 无效的类型
    with pytest.raises(TypeError, match="无效的类型"):
        checker.check(Var("x"), App(Var("f"), Var("x")))

def test_pi_type_inference():
    """测试Pi类型推导"""
    checker = TypeChecker()
    
    # 参数类型必须是Universe
    checker.context.add_var("A", Var("B"))
    with pytest.raises(TypeError, match="参数类型必须是一个Universe: A"):
        checker.infer(Pi("x", Var("A"), Universe(0)))
    
    # 返回类型必须是Universe
    checker.context.add_var("A", Universe(0))
    with pytest.raises(TypeError, match="未绑定的变量: y"):
        checker.infer(Pi("x", Universe(0), Var("y")))
    
    # 返回类型必须是Universe（带有上下文）
    checker.context.add_var("y", Var("z"))
    with pytest.raises(TypeError, match="返回类型必须是一个Universe"):
        checker.infer(Pi("x", Universe(0), Var("y")))

def test_application_type_inference():
    """测试应用类型推导"""
    checker = TypeChecker()
    
    # 应用的第一项必须是函数类型
    checker.context.add_var("x", Universe(0))
    with pytest.raises(TypeError, match="应用的第一项必须是函数类型"):
        checker.infer(App(Var("x"), Var("x")))
    
    # 参数类型不匹配
    checker.context.add_var("f", Pi("x", Universe(0), Var("x")))
    checker.context.add_var("y", Universe(1))
    with pytest.raises(TypeError, match="类型不匹配: 期望 Type_0，实际 Type_1"):
        checker.infer(App(Var("f"), Var("y")))
    
    # 正确的应用
    checker.context.add_var("z", Universe(0))
    result = checker.infer(App(Var("f"), Var("z")))
    assert result == Var("z")

def test_type_checking():
    """测试类型检查"""
    checker = TypeChecker()
    
    # 期望的类型必须是有效的类型
    checker.context.add_var("x", Universe(0))
    with pytest.raises(TypeError, match="无效的类型: 未绑定的变量: y"):
        checker.check(Var("x"), Var("y"))
    
    # 期望的类型不是一个有效的类型
    checker.context.add_var("y", Var("z"))
    with pytest.raises(TypeError, match="无效的类型"):
        checker.check(Var("x"), Var("y"))
    
    # Lambda表达式的类型必须是Pi类型
    lam = Lambda("x", Universe(0), Var("x"))
    with pytest.raises(TypeError, match="Lambda表达式的类型必须是Pi类型"):
        checker.check(lam, Universe(0))
    
    # Lambda体类型不匹配
    pi = Pi("x", Universe(0), Universe(1))
    with pytest.raises(TypeError, match="类型不匹配: 期望 Type_1，实际 Type_0"):
        checker.check(lam, pi)

def test_value_equality():
    """测试值相等性比较"""
    checker = TypeChecker()
    
    # Universe值相等性
    assert checker.values_equal(UniverseValue(0), UniverseValue(0))
    assert not checker.values_equal(UniverseValue(0), UniverseValue(1))
    
    # 变量值相等性
    assert checker.values_equal(VarValue("x"), VarValue("x"))
    assert not checker.values_equal(VarValue("x"), VarValue("y"))
    
    # 闭包值相等性
    env = {"x": UniverseValue(0)}
    closure1 = ClosureValue(env, "x", Var("x"))
    closure2 = ClosureValue(env, "x", Var("x"))
    closure3 = ClosureValue(env, "y", Var("y"))
    assert checker.values_equal(closure1, closure2)
    assert not checker.values_equal(closure1, closure3)
    
    # 中性值相等性
    neutral1 = NeutralValue(Var("x"), [UniverseValue(0)])
    neutral2 = NeutralValue(Var("x"), [UniverseValue(0)])
    neutral3 = NeutralValue(Var("x"), [UniverseValue(1)])
    neutral4 = NeutralValue(Var("y"), [UniverseValue(0)])
    neutral5 = NeutralValue(Var("x"), [])
    neutral6 = NeutralValue(Universe(0), [UniverseValue(0)])
    assert checker.values_equal(neutral1, neutral2)
    assert not checker.values_equal(neutral1, neutral3)
    assert not checker.values_equal(neutral1, neutral4)
    assert not checker.values_equal(neutral1, neutral5)
    assert not checker.values_equal(neutral1, neutral6)
    
    # 不同类型的值不相等
    assert not checker.values_equal(UniverseValue(0), VarValue("x"))
    assert not checker.values_equal(closure1, neutral1)

def test_substitution():
    """测试变量替换"""
    checker = TypeChecker()
    
    # 变量替换
    assert checker.substitute(Var("x"), Universe(0), "x") == Universe(0)
    assert checker.substitute(Var("y"), Universe(0), "x") == Var("y")
    
    # Pi类型替换
    pi = Pi("x", Var("A"), Var("x"))
    subst = checker.substitute(pi, Universe(0), "A")
    assert isinstance(subst, Pi)
    assert subst.var_name == "x"
    assert subst.var_type == Universe(0)
    assert subst.body == Var("x")
    
    # 不替换绑定变量
    pi = Pi("x", Universe(0), Var("x"))
    subst = checker.substitute(pi, Universe(1), "x")
    assert subst == pi
    
    # Lambda替换
    lam = Lambda("x", Var("A"), Var("x"))
    subst = checker.substitute(lam, Universe(0), "A")
    assert isinstance(subst, Lambda)
    assert subst.var_name == "x"
    assert subst.var_type == Universe(0)
    assert subst.body == Var("x")
    
    # 不替换绑定变量
    lam = Lambda("x", Universe(0), Var("x"))
    subst = checker.substitute(lam, Universe(1), "x")
    assert subst == lam
    
    # 应用替换
    app = App(Var("f"), Var("x"))
    subst = checker.substitute(app, Universe(0), "f")
    assert isinstance(subst, App)
    assert subst.func == Universe(0)
    assert subst.arg == Var("x")

def test_context_manager():
    """测试上下文管理器"""
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
    
    # Nested context
    with checker.in_context(new_ctx):
        with checker.in_context(checker.context):
            assert checker.context.get_var_type("y") == type0
        assert checker.context.get_var_type("y") == type0
    assert checker.context.get_var_type("x") == type0 

def test_context_manager_advanced():
    """测试上下文管理器的高级功能"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 设置初始上下文
    checker.context.add_var("x", type0)
    checker.context.add_var("y", type1)
    
    # 创建多个上下文
    ctx1 = Context()
    ctx1.add_var("a", type0)
    ctx1.add_var("x", type1)  # 覆盖原有的x
    
    ctx2 = Context()
    ctx2.add_var("b", type1)
    ctx2.add_var("y", type0)  # 覆盖原有的y
    
    # 测试嵌套上下文切换
    with checker.in_context(ctx1) as ctx1_mgr:
        # 检查ctx1生效
        assert checker.context.get_var_type("a") == type0
        assert checker.context.get_var_type("x") == type1
        assert checker.context.get_var_type("y") is None
        
        with checker.in_context(ctx2) as ctx2_mgr:
            # 检查ctx2生效
            assert checker.context.get_var_type("a") is None
            assert checker.context.get_var_type("b") == type1
            assert checker.context.get_var_type("y") == type0
            
            # 在嵌套上下文中进行类型检查
            checker.context.add_var("z", type0)
            assert checker.check(Var("z"), type0)
            
            # 检查类型错误
            with pytest.raises(TypeError):
                checker.check(Var("z"), type1)
        
        # 检查恢复到ctx1
        assert checker.context.get_var_type("a") == type0
        assert checker.context.get_var_type("x") == type1
        assert checker.context.get_var_type("y") is None
        assert checker.context.get_var_type("z") is None
    
    # 检查恢复到原始上下文
    assert checker.context.get_var_type("x") == type0
    assert checker.context.get_var_type("y") == type1
    assert checker.context.get_var_type("a") is None
    assert checker.context.get_var_type("b") is None
    assert checker.context.get_var_type("z") is None
    
    # 测试异常情况下的上下文恢复
    try:
        with checker.in_context(ctx1):
            raise ValueError("测试异常")
    except ValueError:
        pass
    
    # 检查上下文是否正确恢复
    assert checker.context.get_var_type("x") == type0
    assert checker.context.get_var_type("y") == type1
    assert checker.context.get_var_type("a") is None
    
    # 测试上下文管理器的返回值
    with checker.in_context(ctx1) as ctx_mgr:
        assert ctx_mgr is None

def test_context_manager_edge_cases():
    """测试上下文管理器的边界情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建上下文
    ctx = Context()
    ctx.add_var("x", type0)
    
    # 测试上下文管理器的异常处理
    class TestException(Exception):
        pass
    
    # 测试异常情况
    old_context = checker.context
    try:
        with checker.in_context(ctx):
            raise TestException("测试异常")
    except TestException:
        # 确保上下文被恢复
        assert checker.context == old_context
    
    # 测试嵌套异常
    try:
        with checker.in_context(ctx):
            with checker.in_context(Context()):
                raise TestException("嵌套异常")
    except TestException:
        # 确保上下文被恢复
        assert checker.context == old_context
    
    # 测试多层嵌套
    ctx1 = Context()
    ctx1.add_var("a", type0)
    
    ctx2 = Context()
    ctx2.add_var("b", type0)
    
    ctx3 = Context()
    ctx3.add_var("c", type0)
    
    # 三层嵌套
    with checker.in_context(ctx1):
        assert checker.context.get_var_type("a") == type0
        with checker.in_context(ctx2):
            assert checker.context.get_var_type("b") == type0
            with checker.in_context(ctx3):
                assert checker.context.get_var_type("c") == type0
            assert checker.context.get_var_type("b") == type0
        assert checker.context.get_var_type("a") == type0
    assert checker.context == old_context
    
    # 测试上下文管理器的返回值
    with checker.in_context(ctx) as result:
        assert result is None

def test_type_checking_errors():
    """测试类型检查错误处理"""
    checker = TypeChecker()
    
    # 无法推导类型的情况
    checker.context.add_var("x", Universe(0))
    with pytest.raises(TypeError, match="无法推导类型: 未绑定的变量: f"):
        checker.check(App(Var("f"), Var("x")), Universe(0))
    
    # 类型宇宙层级错误
    with pytest.raises(TypeError, match="类型宇宙层级错误"):
        checker.check(Universe(1), Universe(1))
    
    # 类型宇宙必须是另一个类型宇宙的类型
    with pytest.raises(TypeError, match="类型宇宙必须是另一个类型宇宙的类型"):
        checker.check(Universe(0), Var("x"))

def test_type_inference_errors():
    """测试类型推导错误处理"""
    checker = TypeChecker()
    
    # 未绑定的变量
    with pytest.raises(TypeError, match="未绑定的变量"):
        checker.infer(Var("x"))
    
    # 无法推导Lambda表达式的类型
    lam = Lambda("x", Universe(0), Var("x"))
    with pytest.raises(TypeError, match="无法推导Lambda表达式的类型"):
        checker.infer(lam)
    
    # 应用的第一项必须是函数类型
    checker.context.add_var("x", Universe(0))
    with pytest.raises(TypeError, match="应用的第一项必须是函数类型"):
        checker.infer(App(Var("x"), Var("x")))
    
    # 参数类型不匹配
    checker.context.add_var("f", Pi("x", Universe(0), Var("x")))
    checker.context.add_var("y", Universe(1))
    with pytest.raises(TypeError, match="类型不匹配"):
        checker.infer(App(Var("f"), Var("y")))
    
    # 参数类型必须是Universe
    checker.context.add_var("A", Var("B"))
    with pytest.raises(TypeError, match="参数类型必须是一个Universe"):
        checker.infer(Pi("x", Var("A"), Universe(0)))
    
    # 返回类型必须是Universe
    checker.context.add_var("y", Var("z"))
    with pytest.raises(TypeError, match="返回类型必须是一个Universe"):
        checker.infer(Pi("x", Universe(0), Var("y")))

def test_context_manager_implementation():
    """测试上下文管理器的具体实现"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建上下文
    ctx = Context()
    ctx.add_var("x", type0)
    
    # 获取上下文管理器实例
    ctx_mgr = checker.in_context(ctx)
    
    # 测试初始状态
    assert ctx_mgr.checker == checker
    assert ctx_mgr.new_context == ctx
    assert ctx_mgr.old_context is None
    
    # 测试进入上下文
    old_context = checker.context
    ctx_mgr.__enter__()
    assert ctx_mgr.old_context == old_context
    assert checker.context == ctx
    
    # 测试退出上下文
    ctx_mgr.__exit__(None, None, None)
    assert checker.context == old_context
    
    # 测试异常情况
    try:
        ctx_mgr.__enter__()
        raise ValueError("测试异常")
    except ValueError:
        ctx_mgr.__exit__(ValueError, ValueError("测试异常"), None)
    assert checker.context == old_context

def test_context_manager_complex():
    """测试上下文管理器的复杂场景"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 创建上下文
    ctx1 = Context()
    ctx1.add_var("x", type0)
    ctx1.add_var("y", type1)
    
    ctx2 = Context()
    ctx2.add_var("a", type0)
    ctx2.add_var("b", type1)
    
    # 测试嵌套上下文中的类型检查
    with checker.in_context(ctx1):
        # 检查变量类型
        assert checker.infer(Var("x")) == type0
        assert checker.infer(Var("y")) == type1
        
        # 在嵌套上下文中进行类型检查
        with checker.in_context(ctx2):
            # 检查变量类型
            assert checker.infer(Var("a")) == type0
            assert checker.infer(Var("b")) == type1
            
            # 检查类型错误
            with pytest.raises(TypeError, match="未绑定的变量"):
                checker.infer(Var("x"))  # x 在当前上下文中不可见
            
            # 检查复杂类型
            pi_type = Pi("z", type0, type0)  # 修改为相同的类型
            lam = Lambda("z", type0, Var("z"))
            assert checker.check(lam, pi_type)
            
            # 检查应用
            checker.context.add_var("f", pi_type)
            checker.context.add_var("z", type0)
            app = App(Var("f"), Var("z"))
            assert checker.infer(app) == type0
    
    # 测试异常恢复
    old_context = checker.context
    ctx_mgr = checker.in_context(ctx1)
    try:
        ctx_mgr.__enter__()
        raise KeyError("测试异常")
    except KeyError:
        ctx_mgr.__exit__(KeyError, KeyError("测试异常"), None)
    assert checker.context == old_context
    
    # 测试上下文管理器的返回值
    with checker.in_context(ctx1) as result:
        assert result is None
        # 在上下文中进行类型检查
        assert checker.check(Var("x"), type0)
        assert checker.check(Var("y"), type1)

def test_application_type_checking():
    """测试应用类型检查"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 创建一个函数类型 Π (x : Type_0). Type_1
    pi_type = Pi("x", type0, type1)
    checker.context.add_var("f", pi_type)
    
    # 创建一个参数
    checker.context.add_var("x", type0)
    
    # 测试正确的应用
    app = App(Var("f"), Var("x"))
    assert checker.infer(app) == type1
    
    # 测试错误的应用 - 参数类型不匹配
    checker.context.add_var("y", type1)
    app = App(Var("f"), Var("y"))
    with pytest.raises(TypeError, match="类型不匹配"):
        checker.infer(app)
    
    # 测试错误的应用 - 函数类型不正确
    checker.context.add_var("g", type0)
    app = App(Var("g"), Var("x"))
    with pytest.raises(TypeError, match="应用的第一项必须是函数类型"):
        checker.infer(app)

def test_type_checking_errors_advanced():
    """测试高级类型检查错误"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 测试无效的类型
    checker.context.add_var("x", type0)
    checker.context.add_var("y", Var("z"))  # z 是未定义的变量
    with pytest.raises(TypeError, match="无效的类型"):
        checker.check(Var("x"), Var("y"))
    
    # 测试Lambda体类型不匹配
    lam = Lambda("x", type0, Var("x"))
    pi = Pi("x", type0, type1)
    with pytest.raises(TypeError, match="类型不匹配"):
        checker.check(lam, pi)
    
    # 测试类型宇宙层级错误
    with pytest.raises(TypeError, match="类型宇宙层级错误"):
        checker.check(Universe(1), Universe(1))
    
    # 测试类型宇宙必须是另一个类型宇宙的类型
    with pytest.raises(TypeError, match="类型宇宙必须是另一个类型宇宙的类型"):
        checker.check(Universe(0), Var("x"))

def test_context_manager_final():
    """测试上下文管理器的最终场景"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建上下文
    ctx = Context()
    ctx.add_var("x", type0)
    
    # 测试上下文管理器的返回值
    with checker.in_context(ctx) as result:
        assert result is None
    
    # 测试异常情况
    ctx_mgr = checker.in_context(ctx)
    try:
        ctx_mgr.__enter__()
        raise Exception("未知异常")
    except Exception:
        ctx_mgr.__exit__(Exception, Exception("未知异常"), None)
    
    # 测试多层嵌套和异常
    try:
        with checker.in_context(ctx):
            with checker.in_context(Context()):
                raise ValueError("嵌套异常")
    except ValueError:
        pass

def test_application_type_checking_edge_cases():
    """测试应用类型检查的边界情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 创建一个函数类型 Π (x : Type_0). Type_1
    pi_type = Pi("x", type0, type1)
    checker.context.add_var("f", pi_type)
    
    # 创建一个变量作为函数
    checker.context.add_var("g", type0)
    
    # 测试函数类型规范化
    app = App(Var("g"), Var("x"))
    with pytest.raises(TypeError, match="应用的第一项必须是函数类型"):
        checker.infer(app)
    
    # 测试参数类型不匹配
    checker.context.add_var("x", type1)  # 参数类型错误
    app = App(Var("f"), Var("x"))
    with pytest.raises(TypeError, match="类型不匹配: 期望 Type_0，实际 Type_1"):
        checker.infer(app)

def test_type_checking_invalid_universe():
    """测试无效的类型宇宙"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 创建一个变量作为类型
    checker.context.add_var("x", type0)
    checker.context.add_var("y", type1)  # y 的类型是 Type_1
    
    # 测试类型不匹配
    with pytest.raises(TypeError, match="类型不匹配: 期望 y，实际 Type_0"):
        checker.check(Var("x"), Var("y"))  # x 的类型是 Type_0，y 的类型是 Type_1
    
    # 测试无效的类型
    checker.context.add_var("z", Var("w"))  # w 是未定义的变量
    with pytest.raises(TypeError, match="类型宇宙必须是另一个类型宇宙的类型: Type_0"):
        checker.check(type0, Var("z"))

def test_context_manager_all_cases():
    """测试上下文管理器的所有情况"""
    checker = TypeChecker()
    type0 = Universe(0)
    
    # 创建上下文
    ctx = Context()
    ctx.add_var("x", type0)
    
    # 测试正常情况
    with checker.in_context(ctx):
        assert checker.context == ctx
    
    # 测试异常情况 - TypeError
    try:
        with checker.in_context(ctx):
            raise TypeError("类型错误")
    except TypeError:
        assert checker.context != ctx  # 确保上下文已恢复
    
    # 测试异常情况 - 其他异常
    try:
        with checker.in_context(ctx):
            raise ValueError("其他错误")
    except ValueError:
        assert checker.context != ctx  # 确保上下文已恢复
    
    # 测试嵌套异常
    old_context = checker.context
    try:
        with checker.in_context(ctx):
            with checker.in_context(Context()):
                raise Exception("嵌套异常")
    except Exception:
        assert checker.context == old_context  # 确保上下文已恢复
    
    # 测试上下文管理器的完整生命周期
    ctx_mgr = checker.in_context(ctx)
    assert ctx_mgr.old_context is None
    
    # 进入上下文
    ctx_mgr.__enter__()
    assert ctx_mgr.old_context is not None
    assert checker.context == ctx
    
    # 退出上下文 - 正常情况
    ctx_mgr.__exit__(None, None, None)
    assert checker.context != ctx
    
    # 退出上下文 - 异常情况
    ctx_mgr.__enter__()
    ctx_mgr.__exit__(ValueError, ValueError("测试异常"), None)
    assert checker.context != ctx

def test_application_type_checking_final():
    """测试应用类型检查的最终场景"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 创建一个函数类型 Π (x : Type_0). Type_1
    pi_type = Pi("x", type0, type1)
    checker.context.add_var("f", pi_type)
    
    # 创建一个参数
    checker.context.add_var("x", type0)
    
    # 测试正确的应用
    app = App(Var("f"), Var("x"))
    result = checker.infer(app)
    assert result == type1
    
    # 测试错误的应用 - 参数类型不匹配
    checker.context.add_var("y", type1)  # 参数类型错误
    app = App(Var("f"), Var("y"))
    with pytest.raises(TypeError, match="类型不匹配: 期望 Type_0，实际 Type_1"):
        checker.infer(app)
    
    # 测试错误的应用 - 函数类型不正确
    checker.context.add_var("g", type0)
    app = App(Var("g"), Var("x"))
    with pytest.raises(TypeError, match="应用的第一项必须是函数类型"):
        checker.infer(app)

def test_type_checking_errors_final():
    """测试类型检查错误的最终场景"""
    checker = TypeChecker()
    type0 = Universe(0)
    type1 = Universe(1)
    
    # 创建一个变量作为类型
    checker.context.add_var("x", type0)
    checker.context.add_var("y", type0)  # y 的类型是 Type_0
    
    # 测试类型不匹配
    with pytest.raises(TypeError, match="类型不匹配: 期望 y，实际 Type_0"):
        checker.check(Var("x"), Var("y"))  # x 的类型是 Type_0，期望匹配变量 y
    
    # 测试无效的类型
    checker.context.add_var("z", Var("w"))  # w 是未定义的变量
    with pytest.raises(TypeError, match="无效的类型: 期望的类型 z 不是一个有效的类型"):
        checker.check(Var("x"), Var("z"))  # 使用变量而不是 Universe 类型
    
    # 测试 Lambda 表达式类型检查
    lam = Lambda("x", type0, Var("x"))
    pi = Pi("x", type0, type1)
    with pytest.raises(TypeError, match="类型不匹配: 期望 Type_1，实际 Type_0"):
        checker.check(lam, pi)
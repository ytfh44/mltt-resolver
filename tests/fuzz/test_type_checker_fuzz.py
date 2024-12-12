from hypothesis import given, strategies as st
from mltt.syntax.terms import *
from mltt.core.checker import TypeChecker, TypeError as MLTTTypeError
import pytest

# 定义策略
@st.composite
def universe_strategy(draw):
    """生成 Universe 类型"""
    level = draw(st.integers(min_value=0, max_value=10))
    return Universe(level)

@st.composite
def var_strategy(draw):
    """生成变量"""
    name = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5))
    return Var(name)

@st.composite
def term_strategy(draw, max_depth=3):
    """生成任意项"""
    if max_depth <= 1:
        # 基础情况：只生成变量或 Universe
        return draw(st.one_of(var_strategy(), universe_strategy()))
    
    # 递归情况
    strategies = [
        var_strategy(),
        universe_strategy(),
        # Pi 类型
        st.builds(
            Pi,
            var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
            var_type=term_strategy(max_depth=max_depth-1),
            body=term_strategy(max_depth=max_depth-1)
        ),
        # Lambda 表达式
        st.builds(
            Lambda,
            var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
            var_type=term_strategy(max_depth=max_depth-1),
            body=term_strategy(max_depth=max_depth-1)
        ),
        # 应用
        st.builds(
            App,
            func=term_strategy(max_depth=max_depth-1),
            arg=term_strategy(max_depth=max_depth-1)
        )
    ]
    return draw(st.one_of(*strategies))

# 混沌测试
@given(term=term_strategy())
def test_type_checker_fuzz(term):
    """测试类型检查器在任意输入下的行为"""
    checker = TypeChecker()
    
    try:
        # 尝试推导类型
        type_ = checker.infer(term)
        
        # 如果成功推导出类型，验证它是一个有效的类型
        assert isinstance(type_, Term)
        
        # 验证类型检查
        assert checker.check(term, type_)
        
    except MLTTTypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(
    var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
    var_type=term_strategy(),
    body=term_strategy()
)
def test_lambda_pi_fuzz(var_name, var_type, body):
    """测试 Lambda 和 Pi 类型的构造和类型检查"""
    checker = TypeChecker()
    
    # 构造 Lambda 和对应的 Pi 类型
    lam = Lambda(var_name, var_type, body)
    pi = Pi(var_name, var_type, body)
    
    try:
        # 尝试推导 Pi 类型的类型
        pi_type = checker.infer(pi)
        assert isinstance(pi_type, Universe)
        
        # 尝试检查 Lambda 表达式是否符合 Pi 类型
        checker.check(lam, pi)
        
    except MLTTTypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(
    func=term_strategy(),
    arg=term_strategy()
)
def test_application_fuzz(func, arg):
    """测试函数应用的类型检查"""
    checker = TypeChecker()
    app = App(func, arg)
    
    try:
        # 尝试推导应用的类型
        type_ = checker.infer(app)
        assert isinstance(type_, Term)
        
    except MLTTTypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}") 
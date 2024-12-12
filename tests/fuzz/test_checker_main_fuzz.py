import pytest
from hypothesis import given, strategies as st
from mltt.syntax.terms import *
from mltt.checker import TypeChecker, TypeError as MLTTTypeError
from mltt.context import Context

# 定义策略
@st.composite
def term_strategy(draw, max_depth=3):
    """生成任意项"""
    if max_depth <= 1:
        # 基础情况：只生成变量或 Universe
        return draw(st.one_of(
            st.builds(Var, name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5)),
            st.builds(Universe, level=st.integers(min_value=0, max_value=5))
        ))
    
    # 递归情况
    return draw(st.one_of(
        st.builds(Var, name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5)),
        st.builds(Universe, level=st.integers(min_value=0, max_value=5)),
        st.builds(
            Pi,
            var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
            var_type=term_strategy(max_depth=max_depth-1),
            body=term_strategy(max_depth=max_depth-1)
        ),
        st.builds(
            Lambda,
            var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
            var_type=term_strategy(max_depth=max_depth-1),
            body=term_strategy(max_depth=max_depth-1)
        ),
        st.builds(
            App,
            func=term_strategy(max_depth=max_depth-1),
            arg=term_strategy(max_depth=max_depth-1)
        )
    ))

@st.composite
def context_strategy(draw):
    """生成上下文"""
    context = Context()
    num_vars = draw(st.integers(min_value=0, max_value=5))
    
    for _ in range(num_vars):
        name = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5))
        type_ = draw(st.builds(Universe, level=st.integers(min_value=0, max_value=5)))
        context.add_var(name, type_)
    
    return context

# 混沌测试
@given(term=term_strategy(), expected_type=term_strategy())
def test_type_checker_check_fuzz(term, expected_type):
    """测试类型检查"""
    checker = TypeChecker()
    
    try:
        result = checker.check(term, expected_type)
        assert isinstance(result, bool)
    except MLTTTypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(term=term_strategy())
def test_type_checker_infer_fuzz(term):
    """测试类型推导"""
    checker = TypeChecker()
    
    try:
        type_ = checker.infer(term)
        assert isinstance(type_, Term)
    except MLTTTypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(t1=term_strategy(), t2=term_strategy())
def test_type_checker_is_equal_fuzz(t1, t2):
    """测试类型相等性检查"""
    checker = TypeChecker()
    
    try:
        result = checker.is_equal(t1, t2)
        assert isinstance(result, bool)
        
        # 验证相等性的基本性质
        assert checker.is_equal(t1, t1)  # 自反性
        assert checker.is_equal(t2, t2)  # 自反性
        assert checker.is_equal(t1, t2) == checker.is_equal(t2, t1)  # 对称性
    except MLTTTypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(
    term=term_strategy(),
    var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
    replacement=term_strategy()
)
def test_type_checker_substitute_fuzz(term, var_name, replacement):
    """测试替换操作"""
    checker = TypeChecker()
    
    try:
        result = checker.substitute(term, var_name, replacement)
        assert isinstance(result, Term)
    except MLTTTypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(context=context_strategy())
def test_type_checker_context_fuzz(context):
    """测试上下文管理"""
    checker = TypeChecker()
    old_context = checker.context
    
    with checker.in_context(context):
        assert checker.context == context
        
        # 尝试在新上下文中进行类型检查
        for name, type_ in context.vars.items():
            var = Var(name)
            try:
                assert checker.infer(var) == type_
            except MLTTTypeError:
                pass  # 预期的类型错误
            except Exception as e:
                pytest.fail(f"Unexpected error: {e}")
    
    assert checker.context == old_context 
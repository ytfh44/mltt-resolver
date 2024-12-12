from hypothesis import given, strategies as st
from mltt.syntax.terms import *
from mltt.syntax.values import *
from mltt.core.checker import TypeChecker, TypeError
from mltt.context import Context
import pytest

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
@given(term=term_strategy(), context=context_strategy())
def test_core_checker_infer_fuzz(term, context):
    """测试类型推导"""
    checker = TypeChecker()
    checker.context = context
    
    try:
        type_ = checker.infer(term)
        assert isinstance(type_, Term)
        
        # 验证推导出的类型是有效的
        if isinstance(term, Universe):
            assert isinstance(type_, Universe)
            assert type_.level == term.level + 1
        elif isinstance(term, Lambda):
            pytest.fail("Lambda 表达式不应该能够推导类型")
        elif isinstance(term, Var):
            # 变量必须在上下文中
            assert term.name in context.vars
            assert type_ == context.get_var_type(term.name)
        elif isinstance(term, Pi):
            # Pi 类型的参数类型和返回类型必须是 Universe
            try:
                param_type_type = checker.infer(term.var_type)
                assert isinstance(checker.normalizer.normalize(param_type_type), UniverseValue)
                
                # 在扩展的上下文中检查返回类型
                extended_context = context.extend(term.var_name, term.var_type)
                with checker.in_context(extended_context):
                    return_type_type = checker.infer(term.body)
                    assert isinstance(checker.normalizer.normalize(return_type_type), UniverseValue)
            except TypeError:
                pass  # 预期的类型错误
        elif isinstance(term, App):
            # 应用的函数必须是 Pi 类型
            try:
                func_type = checker.infer(term.func)
                if isinstance(func_type, Pi):
                    # 检查参数类型匹配
                    assert checker.check(term.arg, func_type.var_type)
            except TypeError:
                pass  # 预期的类型错误
    except TypeError:
        # Lambda 表达式应该抛出类型错误
        if isinstance(term, Lambda):
            pass
        # 未绑定的变量应该抛出类型错误
        elif isinstance(term, Var) and term.name not in context.vars:
            pass
        # Pi 类型的参数类型或返回类型不是 Universe 时应该抛出类型错误
        elif isinstance(term, Pi):
            try:
                param_type_type = checker.infer(term.var_type)
                param_type_value = checker.normalizer.normalize(param_type_type)
                if not isinstance(param_type_value, UniverseValue):
                    pass
                else:
                    extended_context = context.extend(term.var_name, term.var_type)
                    with checker.in_context(extended_context):
                        return_type_type = checker.infer(term.body)
                        return_type_value = checker.normalizer.normalize(return_type_type)
                        if not isinstance(return_type_value, UniverseValue):
                            pass
                        else:
                            raise  # 不应该到达这里
            except TypeError:
                pass  # 预期的类型错误
        # 非 Pi 类型的应用应该抛出类型错误
        elif isinstance(term, App):
            try:
                func_type = checker.infer(term.func)
                if not isinstance(func_type, Pi):
                    pass
                else:
                    # 参数类型不匹配应该抛出类型错误
                    if not checker.check(term.arg, func_type.var_type):
                        pass
                    else:
                        raise  # 不应该到达这里
            except TypeError:
                pass  # 预期的类型错误
        else:
            raise
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(term=term_strategy(), expected_type=term_strategy())
def test_core_checker_check_fuzz(term, expected_type):
    """测试类型检查"""
    checker = TypeChecker()
    
    try:
        result = checker.check(term, expected_type)
        assert isinstance(result, bool)
        assert result is True
        
        # 验证特殊情况
        if isinstance(term, Universe):
            assert isinstance(expected_type, Universe)
            assert term.level < expected_type.level
    except TypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(t1=term_strategy(), t2=term_strategy())
def test_core_checker_is_equal_fuzz(t1, t2):
    """测试类型相等性检查"""
    checker = TypeChecker()
    
    try:
        result = checker.is_equal(t1, t2)
        assert isinstance(result, bool)
        
        # 验证相等性的基本性质
        assert checker.is_equal(t1, t1)  # 自反性
        assert checker.is_equal(t2, t2)  # 自反性
        assert checker.is_equal(t1, t2) == checker.is_equal(t2, t1)  # 对称性
        
        # 验证 Universe 的特殊情况
        if isinstance(t1, Universe) and isinstance(t2, Universe):
            assert result == (t1.level == t2.level)
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(
    term=term_strategy(),
    value=term_strategy(),
    var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5)
)
def test_core_checker_substitute_fuzz(term, value, var_name):
    """测试替换操作"""
    checker = TypeChecker()
    
    try:
        result = checker.substitute(term, value, var_name)
        assert isinstance(result, Term)
        
        # 验证替换的基本性质
        if isinstance(term, Var) and term.name == var_name:
            assert result == value
        elif isinstance(term, Universe):
            assert result == term
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(
    var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
    var_type=term_strategy(),
    body=term_strategy()
)
def test_core_checker_lambda_pi_fuzz(var_name, var_type, body):
    """测试 Lambda 和 Pi 类型的检查"""
    checker = TypeChecker()
    
    try:
        # 构造 Lambda 和对应的 Pi 类型
        lam = Lambda(var_name, var_type, body)
        pi = Pi(var_name, var_type, body)
        
        # Lambda 表达式不能直接推导类型
        with pytest.raises(TypeError):
            checker.infer(lam)
        
        # 但可以检查它是否符合 Pi 类型
        try:
            assert checker.check(lam, pi)
        except TypeError:
            pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(
    func=term_strategy(),
    arg=term_strategy()
)
def test_core_checker_application_fuzz(func, arg):
    """测试函数应用的类型检查"""
    checker = TypeChecker()
    app = App(func, arg)
    
    try:
        # 尝试推导应用的类型
        type_ = checker.infer(app)
        assert isinstance(type_, Term)
        
        # 如果函数不是 Pi 类型，应该抛出错误
        if not isinstance(func, Pi):
            pytest.fail("非 Pi 类型的函数应用应该抛出错误")
    except TypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(v1=term_strategy(), v2=term_strategy())
def test_core_checker_values_equal_fuzz(v1, v2):
    """测试值相等性检查"""
    checker = TypeChecker()
    
    try:
        # 先求值再比较
        value1 = checker.evaluator.eval(v1)
        value2 = checker.evaluator.eval(v2)
        
        result = checker.values_equal(value1, value2)
        assert isinstance(result, bool)
        
        # 验证相等性的基本性质
        assert checker.values_equal(value1, value1)  # 自反性
        assert checker.values_equal(value2, value2)  # 自反性
        assert checker.values_equal(value1, value2) == checker.values_equal(value2, value1)  # 对称性
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}") 
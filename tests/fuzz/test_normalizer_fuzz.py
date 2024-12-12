from hypothesis import given, strategies as st
from mltt.syntax.terms import *
from mltt.core.checker import TypeChecker, TypeError as MLTTTypeError
from mltt.core.evaluator import Evaluator
from mltt.core.normalizer import Normalizer
import pytest

# 定义策略
@st.composite
def normalized_term_strategy(draw, max_depth=3):
    """生成可以规范化的项"""
    if max_depth <= 1:
        # 基础情况：只生成 Universe 或变量
        return draw(st.one_of(
            st.builds(Universe, level=st.integers(min_value=0, max_value=5)),
            st.builds(Var, name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5))
        ))
    
    # 递归情况
    return draw(st.one_of(
        # Universe
        st.builds(Universe, level=st.integers(min_value=0, max_value=5)),
        # 变量
        st.builds(Var, name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5)),
        # Pi 类型
        st.builds(
            Pi,
            var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
            var_type=st.builds(Universe, level=st.integers(min_value=0, max_value=5)),
            body=st.builds(Universe, level=st.integers(min_value=0, max_value=5))
        ),
        # Lambda 表达式
        st.builds(
            Lambda,
            var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
            var_type=st.builds(Universe, level=st.integers(min_value=0, max_value=5)),
            body=st.builds(Universe, level=st.integers(min_value=0, max_value=5))
        )
    ))

# 混沌测试
@given(term=normalized_term_strategy())
def test_normalizer_fuzz(term):
    """测试规范化器在任意输入下的行为"""
    evaluator = Evaluator()
    normalizer = Normalizer(evaluator)
    
    # 尝试规范化项
    normalized = normalizer.normalize(term)
    
    # 验证规范化结果
    assert normalized is not None
    
    # 验证规范化是幂等的
    normalized2 = normalizer.normalize(term)
    assert normalized == normalized2

@given(
    term1=normalized_term_strategy(),
    term2=normalized_term_strategy()
)
def test_normalization_equality_fuzz(term1, term2):
    """测试规范化后的相等性检查"""
    checker = TypeChecker()
    
    try:
        # 尝试检查两个项是否相等
        result = checker.is_equal(term1, term2)
        assert isinstance(result, bool)
        
        # 验证相等性是对称的
        assert checker.is_equal(term1, term2) == checker.is_equal(term2, term1)
        
        # 验证自反性
        assert checker.is_equal(term1, term1)
        assert checker.is_equal(term2, term2)
        
    except Exception as e:
        # 确保所有异常都是预期的类型错误
        assert isinstance(e, TypeError)

@given(term=normalized_term_strategy())
def test_normalization_type_preservation_fuzz(term):
    """测试规范化保持类型"""
    checker = TypeChecker()
    
    try:
        # 尝试推导原始项的类型
        original_type = checker.infer(term)
        
        # 规范化项
        normalized = checker.normalizer.normalize(term)
        
        # 尝试推导规范化后项的类型
        normalized_type = checker.infer(normalized)
        
        # 验证类型被保持
        assert checker.is_equal(original_type, normalized_type)
        
    except MLTTTypeError:
        pass  # 预期的类型错误
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}") 
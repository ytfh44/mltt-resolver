from hypothesis import given, strategies as st
from mltt.syntax.terms import *
from mltt.syntax.values import *
from mltt.core.evaluator import Evaluator
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
def env_strategy(draw):
    """生成环境"""
    env = {}
    num_vars = draw(st.integers(min_value=0, max_value=5))
    
    for _ in range(num_vars):
        name = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5))
        value = draw(st.one_of(
            st.builds(VarValue, name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5)),
            st.builds(UniverseValue, level=st.integers(min_value=0, max_value=5))
        ))
        env[name] = value
    
    return env

# 混沌测试
@given(term=term_strategy())
def test_evaluator_eval_fuzz(term):
    """测试求值器的基本功能"""
    evaluator = Evaluator()
    
    try:
        # 尝试求值
        value = evaluator.eval(term)
        assert isinstance(value, Value)
        
        # 验证求值结果的类型
        if isinstance(term, Universe):
            assert isinstance(value, UniverseValue)
            assert value.level == term.level
        elif isinstance(term, Var):
            assert isinstance(value, VarValue)
            assert value.name == term.name
        elif isinstance(term, Lambda):
            assert isinstance(value, ClosureValue)
            assert value.var_name == term.var_name
            assert value.body == term.body
        elif isinstance(term, Pi):
            assert isinstance(value, NeutralValue)
            assert value.term == term
        elif isinstance(term, App):
            # 应用可能产生任何类型的值
            assert isinstance(value, (VarValue, UniverseValue, ClosureValue, NeutralValue))
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(term=term_strategy(), env=env_strategy())
def test_evaluator_with_env_fuzz(term, env):
    """测试带环境的求值"""
    evaluator = Evaluator()
    evaluator.env = env.copy()
    
    try:
        # 尝试在环境中求值
        value = evaluator.eval(term)
        assert isinstance(value, Value)
        
        # 验证环境中的变量
        if isinstance(term, Var) and term.name in env:
            assert evaluator.eval(term) == env[term.name]
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(
    func=term_strategy(),
    arg=term_strategy(),
    env=env_strategy()
)
def test_evaluator_application_fuzz(func, arg, env):
    """测试函数应用求值"""
    evaluator = Evaluator()
    evaluator.env = env.copy()
    
    try:
        # 构造应用
        app = App(func, arg)
        
        # 尝试求值
        value = evaluator.eval(app)
        assert isinstance(value, Value)
        
        # 验证求值结果的类型
        if isinstance(func, Lambda):
            # Lambda 应用可能产生任何类型的值
            assert isinstance(value, (VarValue, UniverseValue, ClosureValue, NeutralValue))
        else:
            # 非 Lambda 应用应该产生中性值
            assert isinstance(value, NeutralValue)
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(term=term_strategy(), env1=env_strategy(), env2=env_strategy())
def test_evaluator_env_isolation_fuzz(term, env1, env2):
    """测试环境隔离"""
    evaluator = Evaluator()
    
    try:
        # 在第一个环境中求值
        evaluator.env = env1.copy()
        value1 = evaluator.eval(term)
        
        # 在第二个环境中求值
        evaluator.env = env2.copy()
        value2 = evaluator.eval(term)
        
        # 如果项中没有自由变量，结果应该相同
        if isinstance(term, Universe):
            assert value1 == value2
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}")

@given(
    var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
    var_type=term_strategy(),
    body=term_strategy(),
    arg=term_strategy()
)
def test_evaluator_beta_reduction_fuzz(var_name, var_type, body, arg):
    """测试 beta 归约"""
    evaluator = Evaluator()
    
    try:
        # 构造 Lambda 和应用
        lam = Lambda(var_name, var_type, body)
        app = App(lam, arg)
        
        # 求值
        value = evaluator.eval(app)
        assert isinstance(value, Value)
    except Exception as e:
        pytest.fail(f"Unexpected error: {e}") 
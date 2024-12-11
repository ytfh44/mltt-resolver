import pytest
from hypothesis import given, strategies as st
from mltt.syntax.terms import *
from mltt.core.checker import TypeChecker

# 定义策略：生成有效的变量名
var_names = st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=10)

# 定义策略：生成宇宙层级
universe_levels = st.integers(min_value=0, max_value=5)

# 定义策略：生成简单的类型表达式
@st.composite
def simple_types(draw):
    """生成简单的类型表达式"""
    level = draw(universe_levels)
    return Universe(level)

# 定义策略：生成变量
@st.composite
def variables(draw):
    """生成变量表达式"""
    name = draw(var_names)
    return Var(name)

# 定义策略：生成 Lambda 表达式
@st.composite
def lambda_terms(draw):
    """生成 Lambda 表达式"""
    var_name = draw(var_names)
    var_type = draw(simple_types())
    body = draw(variables())
    return Lambda(var_name, var_type, body)

# 定义策略：生成 Pi 类型
@st.composite
def pi_types(draw):
    """生成 Pi 类型"""
    var_name = draw(var_names)
    var_type = draw(simple_types())
    body = draw(simple_types())
    return Pi(var_name, var_type, body)

@given(simple_types())
def test_universe_type_check(type_expr):
    """测试任意宇宙层级的类型检查"""
    checker = TypeChecker()
    next_universe = Universe(type_expr.level + 1)
    assert checker.check(type_expr, next_universe)

@given(var_names)
def test_variable_creation(name):
    """测试变量创建的有效性"""
    var = Var(name)
    assert var.name == name
    assert str(var) == name

@given(lambda_terms())
def test_lambda_well_formed(term):
    """测试 Lambda 表达式的结构完整性"""
    assert isinstance(term, Lambda)
    assert isinstance(term.var_name, str)
    assert isinstance(term.var_type, Term)
    assert isinstance(term.body, Term)

@given(pi_types())
def test_pi_type_well_formed(pi_type):
    """测试 Pi 类型的结构完整性"""
    assert isinstance(pi_type, Pi)
    assert isinstance(pi_type.var_name, str)
    assert isinstance(pi_type.var_type, Term)
    assert isinstance(pi_type.body, Term)

@given(variables(), variables())
def test_application_creation(func, arg):
    """测试应用表达式的创建"""
    app = App(func, arg)
    assert app.func == func
    assert app.arg == arg
    assert str(app) == f"{str(func)} {str(arg)}" 
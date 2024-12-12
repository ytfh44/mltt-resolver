from hypothesis import given, strategies as st, settings, HealthCheck
from mltt.syntax.terms import *
from mltt.context import Context
import pytest
from copy import deepcopy

# 定义策略
@st.composite
def var_name_strategy(draw):
    """生成变量名"""
    return draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=3))

@st.composite
def type_strategy(draw, max_depth=2):
    """生成类型"""
    if max_depth <= 1:
        return draw(st.builds(Universe, level=st.integers(min_value=0, max_value=3)))
    
    return draw(st.one_of(
        st.builds(Universe, level=st.integers(min_value=0, max_value=3)),
        st.builds(
            Pi,
            var_name=var_name_strategy(),
            var_type=type_strategy(max_depth=max_depth-1),
            body=type_strategy(max_depth=max_depth-1)
        )
    ))

@st.composite
def context_strategy(draw):
    """生成上下文"""
    context = Context()
    num_vars = draw(st.integers(min_value=0, max_value=3))
    used_names = set()
    
    for _ in range(num_vars):
        # 生成一个未使用的变量名
        while True:
            name = draw(var_name_strategy())
            if name not in used_names:
                break
        used_names.add(name)
        
        type_ = draw(type_strategy())
        context.add_var(name, type_)
    
    return context

@st.composite
def unused_var_name_strategy(draw, context):
    """生成一个在给定上下文中未使用的变量名"""
    used_names = set(context.vars.keys())
    while True:
        name = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=3))
        if name not in used_names:
            return name

# 混沌测试
@given(name=var_name_strategy(), type_=type_strategy())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_context_add_var_fuzz(name, type_):
    """测试添加变量"""
    context = Context()
    
    # 添加变量
    context.add_var(name, type_)
    
    # 验证变量已添加
    assert context.has_var(name)
    assert context.get_var_type(name) == type_
    
    # 验证字符串表示
    assert str(context) == f"{name}: {type_}"

@given(context=context_strategy(), name=var_name_strategy())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_context_get_var_type_fuzz(context, name):
    """测试获取变量类型"""
    # 获取变量类��
    type_ = context.get_var_type(name)
    
    # 验证结果
    if name in context.vars:
        assert type_ == context.vars[name]
    else:
        assert type_ is None

@given(context=context_strategy(), name=var_name_strategy())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_context_has_var_fuzz(context, name):
    """测试检查变量存在"""
    # 检查变量是否存在
    result = context.has_var(name)
    
    # 验证结果
    assert result == (name in context.vars)

@st.composite
def _context_extend_strategy(draw):
    """生成测试用例的所有输入"""
    context = draw(context_strategy())
    type_ = draw(type_strategy())
    # 生成一个未使用的变量名
    used_names = set(context.vars.keys())
    while True:
        name = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=3))
        if name not in used_names:
            break
    return context, name, type_

@given(data=_context_extend_strategy())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_context_extend_fuzz(data):
    """测试扩展上下文"""
    context, name, type_ = data
    
    # 记录原始上下文的变量
    original_vars = {var_name: deepcopy(var_type) for var_name, var_type in context.vars.items()}
    
    # 扩展上下文
    new_context = context.extend(name, type_)
    
    # 验证原上下文未改变
    assert len(context.vars) == len(original_vars)
    for var_name, var_type in original_vars.items():
        assert context.has_var(var_name)
        assert context.get_var_type(var_name) == var_type
    
    # 验证新上下文包含所有原始变量，并且它们的类型保持不变
    for var_name, var_type in original_vars.items():
        assert new_context.has_var(var_name)
        # 直接比较类型，因为 Term 类型已经实现了正确的 __eq__ 方法
        assert new_context.get_var_type(var_name) == var_type
    
    # 验证新变量已添加
    assert new_context.has_var(name)
    assert new_context.get_var_type(name) == type_
    
    # 验证新上下文的大小正确
    expected_size = len(original_vars) + 1  # 新变量名一定不在原上下文中
    assert len(new_context.vars) == expected_size

@given(context=context_strategy())
@settings(suppress_health_check=[HealthCheck.too_slow])
def test_context_str_fuzz(context):
    """测试字符串表示"""
    # 获取字符串表示
    result = str(context)
    
    # 验证结果
    expected_items = [f"{name}: {type_}" for name, type_ in context.vars.items()]
    expected = ", ".join(expected_items)
    assert result == expected
    
    # 验证空上下文
    empty_context = Context()
    assert str(empty_context) == "" 
from hypothesis import given, strategies as st
from mltt.syntax.terms import *
from mltt.core.checker import TypeChecker
from mltt.context import Context

# 定义策略
@st.composite
def context_strategy(draw, max_vars=5):
    """生成上下文"""
    context = Context()
    num_vars = draw(st.integers(min_value=0, max_value=max_vars))
    
    for _ in range(num_vars):
        name = draw(st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5))
        type_ = draw(st.builds(Universe, level=st.integers(min_value=0, max_value=5)))
        context.add_var(name, type_)
    
    return context

@st.composite
def nested_contexts_strategy(draw, max_depth=3):
    """生成嵌套的上下文列表"""
    depth = draw(st.integers(min_value=1, max_value=max_depth))
    return [draw(context_strategy()) for _ in range(depth)]

# 混沌测试
@given(context=context_strategy())
def test_context_manager_fuzz(context):
    """测试单个上下文管理器"""
    checker = TypeChecker()
    old_context = checker.context
    
    with checker.in_context(context):
        # 验证上下��已经切换
        assert checker.context == context
        
        # 尝试在新上下文中进行类型检查
        for name, type_ in context.bindings.items():
            var = Var(name)
            assert checker.infer(var) == type_
    
    # 验证上下文已经恢复
    assert checker.context == old_context

@given(contexts=nested_contexts_strategy())
def test_nested_context_manager_fuzz(contexts):
    """测试嵌套的上下文管理器"""
    checker = TypeChecker()
    old_context = checker.context
    current_context = old_context
    
    try:
        for ctx in contexts:
            with checker.in_context(ctx):
                # 验证上下文已经切换
                assert checker.context == ctx
                current_context = ctx
                
                # 尝试在新上下文中进行类型检查
                for name, type_ in ctx.bindings.items():
                    var = Var(name)
                    assert checker.infer(var) == type_
                
                # 随机抛出异常
                if draw(st.booleans()):
                    raise ValueError("Random error")
                
    except ValueError:
        pass
    
    # 验证上下文已经恢复到最初状态
    assert checker.context == old_context

@given(
    context=context_strategy(),
    var_name=st.text(alphabet=st.characters(whitelist_categories=('Lu', 'Ll')), min_size=1, max_size=5),
    type_=st.builds(Universe, level=st.integers(min_value=0, max_value=5))
)
def test_context_modification_fuzz(context, var_name, type_):
    """测试上下文修改"""
    checker = TypeChecker()
    old_context = checker.context
    
    with checker.in_context(context):
        # 在上下文中添加新变量
        checker.context.add_var(var_name, type_)
        
        # 验证变量已添加
        assert checker.context.get_var_type(var_name) == type_
        
        # 尝试使用新变量进行类型检查
        var = Var(var_name)
        assert checker.infer(var) == type_
    
    # 验证上下文已经恢复，新变量不可见
    assert checker.context == old_context
    assert checker.context.get_var_type(var_name) is None 
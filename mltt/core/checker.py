"""类型检查器的实现。

这个模块实现了 Martin-Löf 类型论的类型检查器。主要功能包括：
1. 类型推导（infer）：推导一个项的类型
2. 类型检查（check）：检查一个项是否具有指定的类型
3. 类型相等性检查（is_equal）：检查两个类型是否相等

主要的类型规则：
1. Universe 层级：Type_n : Type_{n+1}
2. 变量：从上下文中查找类型
3. Pi 类型（函数类型）：(x : A) → B，其中 A 和 B 都必须是类型
4. Lambda 表达式：需要类型注解
5. 应用：函数应用必须类型匹配
"""

from typing import Optional, Type
from ..syntax.terms import *
from ..syntax.values import *
from ..context import Context
from .evaluator import Evaluator
from .normalizer import Normalizer
from contextlib import contextmanager

class TypeError(Exception):
    """类型错误异常"""
    pass

class ContextManager:
    """上下文管理器类"""
    def __init__(self, checker, new_context):
        self.checker = checker
        self.new_context = new_context
        self.old_context = None

    def __enter__(self):
        self.old_context = self.checker.context
        self.checker.context = self.new_context
        return None

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.checker.context = self.old_context

class TypeChecker:
    """类型检查器的实现。
    
    主要职责：
    1. 类型推导：infer 方法
    2. 类型检查：check 方法
    3. 类型相等性检查：is_equal 方法
    
    属性：
        context: 型检查的上下文环境
        evaluator: 求值器，用于计算表达式的值
        normalizer: 规范化器，用于将类型规范化以便比较
    """
    
    def __init__(self):
        self.context = Context()
        self.evaluator = Evaluator()
        self.normalizer = Normalizer(self.evaluator)
        
    def infer(self, term: Term) -> Term:
        """推导项的类型。
        
        这是类型检查器的核心方法，它根据类型系统的规则推导出一个项的类型。
        主要处理以下几种情况：
        1. 变量：从上下文中查找类型
        2. Universe：Type_n 的类型是 Type_{n+1}
        3. Pi 类型：需要检查参数类型和返回类型
        4. Lambda 表达式：需要类型注解
        5. 应用：检查函数类型和参数类型是否匹配
        
        Args:
            term: 要���导类型的项
            
        Returns:
            推导出的类型
            
        Raises:
            TypeError: 当无法推导类型或类型不合法时
        """
        if isinstance(term, Var):
            # 变量类型从上下文中查找
            type_ = self.context.get_var_type(term.name)
            if type_ is None:
                raise TypeError(f"未绑定的变量: {term.name}")
            return type_
            
        elif isinstance(term, Universe):
            # Type_n : Type_{n+1}
            return Universe(term.level + 1)
            
        elif isinstance(term, Pi):
            """
            Pi 类型的类型检查是最复杂的部分，需要处理以下几种情况：
            1. 参数类型必须是一个 Universe（类型的类型）
            2. 返回类型必须是一个有效的类型，可以是：
               - Universe：直接有效
               - 变量：需要特殊处理
               - Pi 类型：需要递归检查
               - 其他：必须确保其类型是 Universe
            3. 变量作为类型使用时的特殊情况：
               - 如果变量是当前 Pi 类型绑定的变量，其类型必须是 Universe
               - 如果变量是其他地方绑定的变量，其类型必须是 Universe
               - 变量的值必须是 Universe 或者另一个变量（类型变量）
            4. 嵌套的 Pi 类型需要特殊处理：
               - 内部 Pi 类型的返回类型必须是一个类型
               - 不能返回一个 Universe，因为它不是一个有效的类型
            """
            # 1. 检查参数类型
            param_type_type = self.infer(term.var_type)
            param_type_value = self.normalizer.normalize(param_type_type)
            if not isinstance(param_type_value, UniverseValue):
                raise TypeError(f"参数类型必须是一个Universe: {term.var_type}")
                
            # 2. 在扩展的上下文中检查返回类型
            extended_context = self.context.extend(term.var_name, term.var_type)
            with self.in_context(extended_context):
                # 检查返回类型本身是否是一个有效的类型
                return_type = term.body
                
                # 3. 处理不同类型的返回类型
                # 3.1 如果返回类型是一个变量
                if isinstance(return_type, Var):
                    var_type = self.context.get_var_type(return_type.name)
                    if var_type is None:
                        raise TypeError(f"未绑定的变量: {return_type.name}")
                    
                    # 检查变量的类型
                    var_type_value = self.normalizer.normalize(var_type)
                    
                    # 3.1.1 如果变量的类型不是 Universe，需要进一步检查
                    if not isinstance(var_type_value, UniverseValue):
                        # 如果不是当前绑定的变量，检查它的类型
                        if return_type.name != term.var_name:
                            var_type = self.context.get_var_type(return_type.name)
                            var_type_value = self.normalizer.normalize(var_type)
                            if not isinstance(var_type_value, UniverseValue):
                                raise TypeError("返回类型必须是一个Universe")
                        else:
                            # 如果是当前绑定的变量，检查它的类型是否是 Universe
                            param_type_value = self.normalizer.normalize(term.var_type)
                            if not isinstance(param_type_value, UniverseValue):
                                raise TypeError(f"变量 {return_type.name} 不能作为类型使用")
                    
                    # 3.1.2 检查变量的值
                    var_value = self.evaluator.eval(return_type)
                    # 变量的值必须是 Universe 或者另一个变量（类型变量）
                    if not isinstance(var_value, (UniverseValue, VarValue)):
                        # 如果是当前绑定的变量，它不能作为类型使用
                        if return_type.name == term.var_name:
                            raise TypeError(f"变量 {return_type.name} 不能作为类型使用")
                        # 如果是其他变量，检查它的类型
                        var_type = self.context.get_var_type(return_type.name)
                        var_type_value = self.normalizer.normalize(var_type)
                        if not isinstance(var_type_value, UniverseValue):
                            raise TypeError(f"变量 {return_type.name} 不能作为类型使用")
                    
                    # 3.1.3 如果是当前绑定的变量，它不能作为类型使用
                    if return_type.name == term.var_name:
                        raise TypeError(f"变量 {return_type.name} 不能作为类型使用")
                
                # 3.2 如果返回类型是一个 Pi 类型，递归检查
                elif isinstance(return_type, Pi):
                    # 递归检查这个 Pi 类型
                    return_type_type = self.infer(return_type)
                    return_type_value = self.normalizer.normalize(return_type_type)
                    # 内部 Pi 类型的返回类型必须是一个类型，不能是 Universe
                    if isinstance(return_type.body, Universe):
                        raise TypeError(f"Pi 类型的返回类型不能是 Universe: {return_type.body}")
                
                # 3.3 如果返回类型是一个 Universe，直接通过
                elif isinstance(return_type, Universe):
                    pass
                
                # 3.4 其他情况，检查返回类型的类型
                else:
                    return_type_type = self.infer(return_type)
                    return_type_value = self.normalizer.normalize(return_type_type)
                    if not isinstance(return_type_value, UniverseValue):
                        raise TypeError(f"返回类型必须是一个Universe: {term.body}")
                
                # 4. 计算 Pi 类型的类型（两个 Universe 的最大值）
                param_level = param_type_value.level
                return_type_type = self.infer(return_type)
                return_type_value = self.normalizer.normalize(return_type_type)
                return_level = return_type_value.level
                return Universe(max(param_level, return_level))
            
        elif isinstance(term, Lambda):
            """Lambda 表��式的类型检查。
            
            Lambda 表达式要类型注解，因为在没有类型注解的情况下，
            无法唯一确定参数的类型。这是因为同一 Lambda 表达式可能
            有多个有效的类型。
            
            例如：λx.x 可以有以下类型：
            - ∀(A : Type₀). A → A
            - ∀(A : Type₁). A → A
            - Bool → Bool
            - Nat → Nat
            等等。
            """
            raise TypeError("无法推导Lambda表达式的类型，需要类型注解")
            
        elif isinstance(term, App):
            """函数应用的类型检查。
            
            函数应用的类型检查需要：
            1. 推导函数的类型，确保是 Pi 类型
            2. 检查参数的类型是否与函数的参数类型匹配
            3. 计算返回类型（可能需要替换）
            """
            # 1. 推导函数类型
            func_type = self.infer(term.func)
            func_type_normal = self.normalizer.normalize(func_type)
            
            # 确保函数类型是 Pi 类型
            if not isinstance(func_type, Pi):
                raise TypeError(f"应用的第一项必须是函数类型: {term.func}")
                
            # 2. 检查参数类型
            if not self.check(term.arg, func_type.var_type):
                raise TypeError(f"参数类型不匹: 期望 {func_type.var_type}，实际 {term.arg}")
                
            # 3. 计算返回类型（替换参数）
            return self.substitute(func_type.body, term.arg, func_type.var_name)
                
        raise TypeError(f"无法推导类型: {term}")
        
    def check(self, term: Term, expected_type: Term) -> bool:
        """检查项是否具有预期类型。
        
        类型检查的主要步骤：
        1. 特殊处理 Universe 的情况
        2. 检查预期类型是否是一个有效的类型
        3. 对于 Lambda 表达式，需要特殊处理
        4. 其他情况，推导实际类型并与预期类型比较
        
        Args:
            term: 要检查的项
            expected_type: 预期的类型
            
        Returns:
            如果类型检查通过，返回 True
            
        Raises:
            TypeError: 当类型检查失败时
        """
        # 1. 特殊处理Universe的情况
        if isinstance(term, Universe):
            if not isinstance(expected_type, Universe):
                raise TypeError(f"类型宇宙必须是另一个类型宇宙的类型: {term}")
            if term.level >= expected_type.level:
                raise TypeError(f"类型宇宙层级错误: Type_{term.level} 不能是 Type_{expected_type.level}")
            return True

        # 2. 检查expected_type是否是一个有效的类型
        try:
            type_type = self.infer(expected_type)
            if not isinstance(self.normalizer.normalize(type_type), UniverseValue):
                raise TypeError(f"期望的类型 {expected_type} 不是一个有效的类型")
        except TypeError as e:
            raise TypeError(f"无效的类型: {e}")

        # 3. 处理 Lambda 表达式
        if isinstance(term, Lambda):
            if not isinstance(expected_type, Pi):
                raise TypeError("Lambda表达式的类型必须是Pi类型")

            # 在扩展的上下文中检查 Lambda 体
            extended_context = self.context.extend(expected_type.var_name, expected_type.var_type)

            with self.in_context(extended_context):
                if not self.check(term.body, expected_type.body):
                    raise TypeError(f"Lambda体类型不匹配: 期望 {expected_type.body}")
            return True

        # 4. 其他情况：推导实际类型并比较
        try:
            actual_type = self.infer(term)
        except TypeError as e:
            raise TypeError(f"无法推导类型: {e}")

        if not self.is_equal(actual_type, expected_type):
            # 如果是Universe类型，使用下划线格式
            if isinstance(expected_type, Universe) and isinstance(actual_type, Universe):
                raise TypeError(f"类型不匹配: 期望 Type_{expected_type.level}，实际 Type_{actual_type.level}")
            else:
                raise TypeError(f"类型不匹配: 期望 {expected_type}，实际 {actual_type}")
        return True
            
    def is_equal(self, t1: Term, t2: Term) -> bool:
        """检查两个类型是否相等（通过规范化比较）。
        
        类型相等性检查的步骤：
        1. 特殊处理 Universe 的情况（直接比较层级）
        2. 其他情况，通过规范化后比较值
        
        Args:
            t1: 第一个类型
            t2: 第二个类型
            
        Returns:
            如果两个类型相等，返回 True
        """
        # 1. 特殊处理Universe的情况
        if isinstance(t1, Universe) and isinstance(t2, Universe):
            return t1.level == t2.level
        
        # 2. 其他情况，通过规范化比较
        n1 = self.normalizer.normalize(t1)
        n2 = self.normalizer.normalize(t2)
        return self.values_equal(n1, n2)
        
    def values_equal(self, v1: Value, v2: Value) -> bool:
        """比较两个值是否相等。
        
        值相等性检查需要处理以下几种情况：
        1. Universe：比较层级
        2. 变量：比较名称
        3. 闭包：比较结构（变量名和体）
        4. 中性值：���较结构（项和参数）
        
        Args:
            v1: 第一个值
            v2: 第二个值
            
        Returns:
            如果两个值相等，返回 True
        """
        # 1. Universe 的情况
        if isinstance(v1, UniverseValue) and isinstance(v2, UniverseValue):
            return v1.level == v2.level
            
        # 2. 变量的情况
        elif isinstance(v1, VarValue) and isinstance(v2, VarValue):
            return v1.name == v2.name
            
        # 3. 闭包的情况
        elif isinstance(v1, ClosureValue) and isinstance(v2, ClosureValue):
            # 比较闭包的结构
            return (v1.var_name == v2.var_name and 
                   self.values_equal(self.evaluator.eval(v1.body), 
                                   self.evaluator.eval(v2.body)))
                                   
        # 4. 中性值的情况
        elif isinstance(v1, NeutralValue) and isinstance(v2, NeutralValue):
            # 比较中性值的结构
            if not isinstance(v1.term, type(v2.term)):
                return False
            if len(v1.args) != len(v2.args):
                return False
            if isinstance(v1.term, Var) and isinstance(v2.term, Var):
                if v1.term.name != v2.term.name:
                    return False
            return all(self.values_equal(a1, a2) for a1, a2 in zip(v1.args, v2.args))
            
        return False
        
    def substitute(self, term: Term, value: Term, var_name: str) -> Term:
        """替换项中的变量。
        
        这个方法用于在类型检查过程中，将函数应用时的实际参数
        替换到函数体中。需要注意的是，这里的替换是语法层面的，
        不涉及求值。
        
        替换规则：
        1. 如果遇到同名变量，不替换（变量遮蔽）
        2. 如果遇到绑定同名变量的 Lambda/Pi，不替换内部（变量遮蔽）
        3. 递归替换子项
        
        Args:
            term: 要进行替换的项
            value: 用于替换的值
            var_name: 要替换的变量名
            
        Returns:
            替换后的项
        """
        if isinstance(term, Var):
            # 如果是要替换的变量，返回替换值
            if term.name == var_name:
                return value
            # 否则保持不变
            return term
            
        elif isinstance(term, Universe):
            # Universe 不包含变量，直接返回
            return term
            
        elif isinstance(term, Pi):
            # 如果绑定同名变量，不替换内部（变量遮蔽）
            if term.var_name == var_name:
                return term
            # 否则递归替换
            return Pi(term.var_name,
                     self.substitute(term.var_type, value, var_name),
                     self.substitute(term.body, value, var_name))
                     
        elif isinstance(term, Lambda):
            # 如果绑定同名变量，不替换内部（变量遮蔽）
            if term.var_name == var_name:
                return term
            # 否则递归替换
            return Lambda(term.var_name,
                        self.substitute(term.var_type, value, var_name),
                        self.substitute(term.body, value, var_name))
                        
        elif isinstance(term, App):
            # 递归替换函数和参数
            return App(self.substitute(term.func, value, var_name),
                      self.substitute(term.arg, value, var_name))
                      
        return term
        
    def in_context(self, context):
        """在指定上下文中执行代码块。

        Args:
            context: 要使用的上下文

        Returns:
            上下文管理器实例
        """
        return ContextManager(self, context)
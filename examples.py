from mltt.syntax.terms import *
from mltt.core.checker import TypeChecker

def test_identity():
    checker = TypeChecker()
    
    # Type₀
    type0 = Universe(0)
    
    # id : Π (A : Type₀). Π (x : A). A
    id_type = Pi("A", type0, Pi("x", Var("A"), Var("A")))
    
    # id = λ (A : Type₀). λ (x : A). x
    id_term = Lambda("A", type0, Lambda("x", Var("A"), Var("x")))
    
    try:
        if checker.check(id_term, id_type):
            print("Identity function type checks!")
            
            # 测试规范化
            normal_form = checker.normalizer.normalize(id_term)
            print(f"Normal form: {normal_form}")
    except TypeError as e:
        print(f"Type error: {e}")

if __name__ == "__main__":
    test_identity() 
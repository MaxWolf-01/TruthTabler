from truth_tabler import TruthTabler
from bool_expressions import _OPERATORS

if __name__ == '__main__':
    print(f"Valid variables are alphabets(lower and upper is treated as 1) "
          f"\nValid Operators are: {list(_OPERATORS.values())}"
          f"\nOperator heirarchy(high to low): {list(_OPERATORS.keys())}")
    expr = input("Expression: ")
    print(expr)
    truthTabler = TruthTabler(expr)
    truthTabler.print_result()

from truth_tabler import TruthTabler
from bool_expressions import _OPERATORS

if __name__ == '__main__':

    def info():
        print(f"Valid variables are alphabets(lower and upper is treated as 1) "
              f"\nValid Operators are: {list(_OPERATORS.values())}"
              f"\nOperator heirarchy(high to low): {list(_OPERATORS.keys())}")

    print('Press H for help')
    while True:
        user_in = input('Expression: ')
        if user_in.upper() == 'H':
            info()
        else:
            truthTabler = TruthTabler(user_in)
            truthTabler.print_result()

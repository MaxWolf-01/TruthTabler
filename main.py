from src.truth_tabler import TruthTabler, BracketException
from src.bool_expressions import OPERATORS, InvalidExpressionException

if __name__ == '__main__':

    def info():
        print(f"Valid variables are alphabets(lower and upper is treated as 1) "
              f"\nValid Operators are: {list(OPERATORS.values())}"
              f"\nOperator heirarchy(high to low): {list(OPERATORS.keys())}")

    print('Type help for help')
    while True:
        user_in = input('Expression: ')
        if user_in in 'endexit':
            break
        elif user_in in 'help':
            info()
        else:
            try:
                truthTabler = TruthTabler(user_in)
                truthTabler.print()
            except (BracketException, InvalidExpressionException) as e:
                print('   ', e)

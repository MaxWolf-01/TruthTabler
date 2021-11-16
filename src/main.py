import cProfile
import pstats

from truth_tabler import TruthTabler
from bool_expressions import OPERATORS
from exceptions import BracketException, InvalidExpressionException

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
                with cProfile.Profile() as pr:
                    truthTabler = TruthTabler(user_in)

                stats = pstats.Stats(pr)
                stats.sort_stats(pstats.SortKey.TIME)
                stats.print_stats()

                truthTabler.print()
            except (BracketException, InvalidExpressionException) as e:
                print('   ', e)


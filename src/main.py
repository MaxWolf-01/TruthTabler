# import cProfile
# import pstats

from truth_tabler import TruthTabler
from optimization import QuineMcCluskey
from truth_table import get_pretty_truthtable
from operator_symbols import SUPPORTED_OPERATORS
from Exceptions import TablerException

MODES = ['T', 'TT', 'CE']
STOP_COMMANDS = ['X', 'END', 'EXIT']
EXIT_INFO = f"To switch modes/get out of a mode use: {' or '.join(STOP_COMMANDS)} (case insensitive)"
MODE_INFO = f"'TT' for Truthtabler\n'CE' to create an expression with truth table values\n'T' to make a plain" \
            f"truth-table with variables"


def main():
    main_info = f"\n{MODE_INFO}\n{EXIT_INFO}\n"
    print("Type 'H' for help in any mode.")
    while True:
        mode = input("Choose mode[T/TT/CE]: ").upper()
        if stop_app(mode):
            break
        elif get_help(mode):
            print(main_info)
            continue
        choose_mode(mode)


def choose_mode(mode):
    print()
    if mode == 'TT':
        truthtabler_mode()
    elif mode == 'CE':
        create_expression_mode()
    elif mode == 'T':
        table_mode()
    else:
        print(MODE_INFO)


def table_mode():
    table_help = f"Variables have to be single characters.\n{EXIT_INFO}"
    while True:  # tdo howto clean this up
        in_ = input('T> variables: ')
        if stop_app(in_):
            break
        elif get_help(in_):
            print(table_help)
            continue
        print(get_pretty_truthtable(vars_=set(in_.replace(' ', ''))))


def truthtabler_mode():
    tabler_info = f'\n{EXIT_INFO}\n{SUPPORTED_OPERATORS}\n'
    while True:
        expr_input = input('TT> Expression: ')
        if stop_app(expr_input):
            break
        elif get_help(expr_input):
            print(tabler_info)
            continue
        elif expr_input == '':
            print('Please enter a boolean expression! (type "how" for info)')
            continue
        try:
            truthTabler = TruthTabler(expr_input)
            truthTabler.print_with_options()
        except TablerException as e:
            print('', e)


def create_expression_mode():
    CE_info = f'{EXIT_INFO}\n'\
              f'\nTruthtable starts with 0 - increasing\n' \
              f'Don\'t care\'s are represented by X or x.\n'
    while True:
        vars_ = input('Names of the variables(single char per variable)\nCE> variables: ').replace(' ', '')
        if len(vars_) == 0:
            print("Please enter at least 1 variable!")
            continue
        elif stop_app(vars_):
            break
        elif get_help(vars_):
            print(CE_info)
            continue
        else:
            run_QuineMcCluskey(vars_)


def run_QuineMcCluskey(vars_):
    Q = QuineMcCluskey()
    if input('CE> Enter truth-table values one by one? (else TT values as list)\n[y/n]: ') == 'y':
        TTvalues = getTT_values_1b1(vars_)
        if TTvalues[0] and TTvalues[0] == 'exit':
            return
    else:
        try:
            TTvalues = eval(input('CE> Truthtable list: '))
            if len(TTvalues) % 2:
                print("Invalid length of list: Must be a power of 2!")
                return
        except (SyntaxError, NameError):
            print("Invalid input. Must be in list format with 1s 0s or Xs! e.g.: [1,0,x,0]")
            return
    Q.minimize(TTvalues, variable_names=vars_)
    print(f'\nOutput: {Q.minimal_expr}\n(from: {TTvalues})\n')


def getTT_values_1b1(vars_):
    TTvalues = []
    i = 0
    while i < 2 ** len(vars_):
        in_ = input(f'{i}: ')
        if in_.upper() != 'X' and (not in_.isnumeric() or in_ in '' or len(in_) > 1):
            if stop_app(in_):
                return ['exit']
            print('Invalid Input! (Has to be single binary digit or X)')
            continue
        elif in_.upper() == 'X':
            TTvalues.append('X')
        else:
            TTvalues.append(int(in_))
        i += 1
    return TTvalues


def stop_app(input_):
    return input_.upper() in STOP_COMMANDS


def get_help(input_):
    return input_.upper() == 'H'


if __name__ == '__main__':
    # with cProfile.Profile() as pr:
    main()
    # stats = pstats.Stats(pr)
    # stats.sort_stats(pstats.SortKey.TIME)
    # stats.print_stats()

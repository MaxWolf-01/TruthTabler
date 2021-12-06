# import cProfile
# import pstats

from truth_tabler import TruthTabler
from optimization import QuineMcCluskey
from Exceptions import BracketException, InvalidExpressionException

MODES = ['TT', 'CE']
STOP_COMMANDS = ['X', 'END', 'EXIT']
info = f"To switch modes/get out of a mode use: {' or '.join(STOP_COMMANDS)} (case insensitive)\n" \
       f"Type 'TT' for Truthtabler and 'CE' to create an expression with truth table values!\n"


def main():
    print(f"{info}\nType 'H' for help")
    while True:
        mode = input("Choose mode[TT/CE]: ").upper()
        if stop_app(mode):
            break
        elif get_help(mode):
            print(info)
            continue
        choose_mode(mode)


def choose_mode(mode):
    print()
    if mode == 'TT':
        truthtabler()
    elif mode == 'CE':
        create_expression()
    else:
        print(info)


def truthtabler():
    while True:
        expr_input = input('TT> Expression: ')
        if stop_app(expr_input):
            break
        elif get_help(expr_input):
            print(info)
            continue
        else:
            try:
                truthTabler = TruthTabler(expr_input)
                truthTabler.print_with_options()
            except (BracketException, InvalidExpressionException) as e:
                print('', e)


# Clean code tdo??
def create_expression():
    CE_info = f'\nTruthtable starts with 0 - increasing\n' \
              f'Don\'t care\'s are represented by X or x.\n{info}\n'
    while True:
        vars_ = input('Names of the variables(single char per variable)\nCE> variables: ').replace(' ', '')
        if stop_app(vars_):
            break
        elif get_help(vars_):
            print(CE_info)
            continue
        else:
            Q = QuineMcCluskey()
            if input('CE> Enter truth-table values one by one? (else TT values as list)\n[y/n]: ') == 'y':
                TTvalues = getTT_values_1b1(vars_, CE_info=CE_info)
                if TTvalues[0] and TTvalues[0] == 'exit':
                    return
            else:
                try:
                    TTvalues = eval(input('CE> Truthtable list: '))
                    if len(TTvalues) % 2:
                        print("Invalid length of list: Must be a power of 2!")
                        break
                except (SyntaxError, NameError):
                    print("Invalid input. Must be in list format with 1s 0s or Xs! e.g.: [1,0,x,0]")
                    break
            Q.minimize(TTvalues, variable_names=vars_)
            print(f'\nOutput: {Q.minimal_expr}\n(from: {TTvalues})\n')


def getTT_values_1b1(vars_, CE_info):
    TTvalues = []
    i = 0
    while i < 2 ** len(vars_):
        in_ = input(f'{i}: ')
        if in_.upper() not in 'X' and (not in_.isnumeric() or in_ in '' or len(in_) > 1):
            if stop_app(in_):
                return ['exit']
            print(CE_info, '\n(Invalid Input!)')
            continue
        if in_ in 'xX':
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

import itertools
import re
from prettytable import PrettyTable
from Exceptions import BracketException, InvalidExpressionException


def getVariables(expr):
    # Variables have to be a letter and of length 1
    if isinstance(expr, int):
        return None
    if isinstance(expr, str):
        expr = split_to_list(expr)
    vars_ = sorted({x for x in expr if x.isalpha() and len(x) == 1})
    if not vars_:
        raise InvalidExpressionException('Expression has no valid variable(s)! (Must be single letters)')
    return vars_


def createTT(n):
    return list(itertools.product([0, 1], repeat=n))


def reverse_table(table):
    # regular table is from all 0s to all 1s.
    return table[::-1]


def split_to_list(expr):
    """
    turns the expression into a list, using '( )!¬·+-' as delimiters. Case is ignored.
    """
    return [e for e in re.split('([(| |)|!|¬|·|+|-|↓|↑])', expr.upper()) if e != " " and e != ""]


def check_brackets(expr):
    if expr.count('(') != expr.count(')'):
        raise BracketException(expr, [expr.count('('), expr.count(')')])


class TruthTable:
    def __init__(self, expr: str, reversed_table=False):
        check_brackets(expr)
        self.variables = getVariables(expr)
        self.table = createTT(len(self.variables))
        if reversed_table:
            self.table = reverse_table(self.table)


def main():
    print(get_pretty_truthtable())


def get_pretty_truthtable(vars_=None):
    if vars_ is None:
        vars_ = set(input('T> variables: ').replace(' ', ''))
    field_names = ['#', *vars_]
    TT = createTT(len(vars_))
    if input('Reverse Table (->from all 1s to all 0s)\nT> [y/n]? :') == 'y':
        TT.reverse()
    rows = [[i, ] for i in range(len(TT))]
    for i in range(len(rows)):
        rows[i].extend(TT[i])
    pT = PrettyTable()
    pT.field_names = field_names
    pT.add_rows(rows)
    return pT


if __name__ == '__main__':
    main()

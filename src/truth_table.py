import itertools
import re


def getVariables(expr: list):
    return sorted({x for x in expr if x.isalpha() and len(x) == 1})


def createTT(n):
    return list(itertools.product([0, 1], repeat=n))


def reverse_table(table):
    return table[::-1]


def prepare(expr):
    """
    turns the expression into a list, using '( )!¬·+-' as delimiters. Lower and uppercase letters are treated
    as a single variable
    """
    return [e for e in re.split('([(| |)|!|¬|·|+|-])', expr.upper()) if e != " " and e != ""]


class TruthTable:
    def __init__(self, expr: str, reversed_table=False):
        self.variables = getVariables(prepare(expr))
        self.table = createTT(len(self.variables))
        if reversed_table:
            self.table = reverse_table(self.table)

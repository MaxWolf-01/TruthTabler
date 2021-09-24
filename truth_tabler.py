import re
from copy import deepcopy
from bool_expressions import *
from normal_forms import CDNF, CCNF
from prettytable import PrettyTable


class BracketException(Exception):
    def __init__(self, expr):
        super(Exception, self).__init__(f'Number of opening and closing brackets do not match: {expr}')


class TruthTabler:
    def __init__(self, expr: str):
        self.expr = self.prepare(expr)
        self.check_validness(expr)
        self.OGexpr = expr
        self.TT = TruthTable(self.expr)
        self.xTree = ExpressionTree(self.expr, self.TT, True)
        self.result = self.xTree.solve()
        self.CDNF = CDNF(self.TT, self.result)
        self.CCNF = CCNF(self.TT, self.result)

    @staticmethod
    def check_validness(expr):
        if expr.count('(') != expr.count(')'):
            raise BracketException(expr)

    @staticmethod
    def prepare(expr):
        """
        turns the expression into a list, using '(', ')' and ' ' as delimiters. Lower and uppercase letters are treated
        as a single variable
        """
        return [e for e in re.split('([(| |)|!])', expr.upper()) if e != " " and e != ""]

    def print_result(self):
        prettyTable = PrettyTable()

        field_names = ['#', *deepcopy(self.TT.variables), self.OGexpr]

        rows = [[i, ] for i in range(len(self.TT.table))]
        for i in range(len(rows)):
            rows[i].extend(self.TT.table[i])
            rows[i].append(self.result[i])

        prettyTable.field_names = field_names
        prettyTable.add_rows(rows)
        print(prettyTable, f'\n Optimized expression:' 
                           f'\n   CDNF:\n \t{self.CDNF}'
                           f'\n   CCNF:\n \t{self.CCNF}')


class Optimizer:
    def __init__(self, truth_tabler: TruthTabler):
        self.CDNF = CDNF(truth_tabler.TT.table, truth_tabler.result)
        self.CCNF = CCNF(truth_tabler.TT.table, truth_tabler.result)

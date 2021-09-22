import re
from copy import deepcopy

from bool_expressions import *
from prettytable import PrettyTable


class TruthTabler:
    def __init__(self, expr: str):
        self.expr = self.prepare(expr)
        self.check_validness(expr)
        self.OGexpr = expr
        self.xTree = ExpressionTree(self.expr, TruthTable(self.expr), True)
        self.result = self.xTree.solve()

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

        field_names = deepcopy(self.xTree.TT.variables)
        field_names.append(self.OGexpr)
        field_names.append('#')
        prettyTable.field_names = field_names

        rows = [list(row) for row in self.xTree.TT.table]
        for i in range(len(rows)):
            rows[i].append(self.result[i])
            rows[i].append(i)
        prettyTable.add_rows(rows)

        print(prettyTable)


class BracketException(Exception):
    def __init__(self, expr):
        super(Exception, self).__init__(f'Number of opening and closing brackets do not match: {expr}')

import re
from bool_expressions import *
from prettytable import PrettyTable


class TruthTabler:
    def __init__(self, expr):
        self.check_validness(expr)
        self.expr = self.prepare(expr)
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
        return [e for e in re.split('([(| |)])', expr.upper()) if e != " " and e != ""]

    def __str__(self):
        prettyTable = PrettyTable()

        vars_ = self.xTree.TT.variables
        vars_.append(self.OGexpr)
        field_names = vars_
        prettyTable.field_names = field_names

        rows = [list(row) for row in self.xTree.TT.table]
        for i in range(len(rows)):
            rows[i].append(self.result[i])
        prettyTable.add_rows(rows)

        return prettyTable.__str__()


class BracketException(Exception):
    def __init__(self, expr):
        super(Exception, self).__init__(f'Number of opening and closing brackets do not match: {expr}')

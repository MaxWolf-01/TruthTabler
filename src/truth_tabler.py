from copy import deepcopy

from prettytable import PrettyTable

import circuit_creator
import truth_table
from bool_expressions import ExpressionSolver
from normal_forms import CCNF, CDNF
from operator_signs import _AND, _OR
from optimization import QuineMcCluskey


class TruthTabler:
    def __init__(self, expr: str = None):
        self.TT = None
        self.expr = ''
        self.xTree = None
        self.result = []
        self.CDNF = None
        self.CCNF = None
        self.minimal_expr = ''
        self.circuit = None
        self.variables = []
        if expr:
            self.evaluate(expr)

    def evaluate(self, expr):
        self.__init__()
        self.TT = truth_table.TruthTable(expr)
        self.expr = expr
        self.xTree = ExpressionSolver(expr, self.TT)
        print('Solving expression...')
        self.result = self.xTree.solve()
        print('Creating normal forms...')
        self.CDNF = CDNF(self.TT, self.result)
        self.CCNF = CCNF(self.TT, self.result)
        print('Minimizing...')
        self.minimal_expr = QuineMcCluskey(self.result, self.TT.variables).minimal_expr
        print('Creating Circuit...')
        self.circuit = circuit_creator.create_circuit_from_expr(self.minimal_expr)
        self.variables = truth_table.getVariables(self.expr)

    def print(self):
        prettyTable = PrettyTable()

        field_names = ['#', *deepcopy(self.TT.variables), self._get_formated_OGexpr(self.expr)]

        rows = [[i, ] for i in range(len(self.TT.table))]
        for i in range(len(rows)):
            rows[i].extend(self.TT.table[i])
            rows[i].append(self.result[i])

        prettyTable.field_names = field_names
        prettyTable.add_rows(rows)
        print(prettyTable, f'\n Normal Forms: ({_AND} = AND; {_OR} = OR)'
                           f'\n   CDNF:\n \t{self.CDNF}'
                           f'\n   CCNF:\n \t{self.CCNF}\n'
                           f'\n Minimal expression:'
                           f'\n    \t{self.minimal_expr}'
                           f'\n {self.result}')
        circuit_creator.print_space(self.circuit, self.variables)

    @staticmethod
    def _get_formated_OGexpr(expr):
        # prevents non unique field names for prettytable (if an expression is a single variable)
        if len(expr) == 1:
            expr = '(' + expr + ')'
        return expr

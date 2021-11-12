from copy import deepcopy

from prettytable import PrettyTable
from bool_expressions import TruthTable, ExpressionSolver
from normal_forms import CCNF, CDNF, _CONJUNCTION, _DISJUNCTION
from optimization import QuineMcCluskey


class TruthTabler:
    def __init__(self, expr: str = None):
        self.TT = None
        self.expr = ''
        self.expr = ''
        self.xTree = None
        self.result = []
        self.CDNF = None
        self.CCNF = None
        self.minimal_expr = ''
        if expr:
            self.evaluate(expr)

    def evaluate(self, expr):
        self.__init__()
        self.TT = TruthTable(expr)
        self.expr = expr
        self.xTree = ExpressionSolver(expr, self.TT, is_root=True)
        print('Solving expression...')
        self.result = self.xTree.solve()
        print('Creating normal forms...')
        self.CDNF = CDNF(self.TT, self.result)
        self.CCNF = CCNF(self.TT, self.result)
        print('Minimizing...')
        self.minimal_expr = QuineMcCluskey(self.result, self.TT.variables).minimal_expr

    def print(self):
        prettyTable = PrettyTable()

        field_names = ['#', *deepcopy(self.TT.variables), self._get_formated_OGexpr()]

        rows = [[i, ] for i in range(len(self.TT.table))]
        for i in range(len(rows)):
            rows[i].extend(self.TT.table[i])
            rows[i].append(self.result[i])

        prettyTable.field_names = field_names
        prettyTable.add_rows(rows)
        print(prettyTable, f'\n Normal Forms: ({_CONJUNCTION} = AND; {_DISJUNCTION} = OR)'
                           f'\n   CDNF:\n \t{self.CDNF}'
                           f'\n   CCNF:\n \t{self.CCNF}\n'
                           f'\n Minimal expression:'
                           f'\n    \t{self.minimal_expr}'
                           f'\n {self.result}')

    def _get_formated_OGexpr(self):
        # prevents non unique field names for prettytable (if an expression is a single variable)
        expr = self.expr
        if len(self.expr) == 1:
            expr = '(' + self.expr + ')'
        return expr

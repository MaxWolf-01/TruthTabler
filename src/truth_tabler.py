from copy import deepcopy

from prettytable import PrettyTable
from src.truth_table import prepare
from src.bool_expressions import TruthTable, ExpressionTree
from src.normal_forms import CCNF, CDNF, _CONJUNCTION, _DISJUNCTION
from src.optimization import QuineMcCluskey


class TruthTabler:
    def __init__(self, expr: str = None):
        self.TT = None
        self.OGexpr = ''
        self.expr = []
        self.xTree = None
        self.result = []
        self.CDNF = None
        self.CCNF = None
        self.minimal_expr = ''
        if expr:
            self.evaluate(expr)

    def evaluate(self, expr):
        self.__init__()
        self.check_validness(expr)
        self.TT = TruthTable(expr)
        self.OGexpr = expr
        self.expr = prepare(expr)
        self.xTree = ExpressionTree(self.expr, self.TT, is_root=True)
        self.result = self.xTree.solve()
        self.CDNF = CDNF(self.TT, self.result)
        self.CCNF = CCNF(self.TT, self.result)
        self.minimal_expr = QuineMcCluskey(self.result).minimal_expr

    @staticmethod
    def check_validness(expr):
        if expr.count('(') != expr.count(')'):
            raise BracketException(expr, [expr.count('('), expr.count(')')])

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
                           f'\n   CCNF:\n \t{self.CCNF}'
                           f'\n   Minimal expression:\n \t{self.minimal_expr}'
                           f'\n {self.result}')

    def _get_formated_OGexpr(self):
        # prevents non unique field names for prettytable
        OG = self.OGexpr
        if len(self.OGexpr) == 1:
            OG = '(' + self.OGexpr + ')'
        return OG


class BracketException(Exception):
    def __init__(self, expr, msg):
        super(Exception, self).__init__(f'Number of opening and closing brackets do not match: {msg[0]} != {msg[1]} '
                                        f'for: "{expr}"')

from copy import deepcopy

from prettytable import PrettyTable

from truth_table import TruthTable, getVariables
from circuit_creator import space_to_string, create_circuit_from_expr
from bool_expressions import ExpressionSolver
from normal_forms import CCNF, CDNF
from operator_symbols import OPERATOR_SIGNS
from optimization import QuineMcCluskey
from logic_gates import NandMaker, NorMaker


class TruthTabler:
    def __init__(self, expr: str = None):
        self.TT = None
        self.expr = ''
        self.xTree = None
        self.result = []
        self.CDNF = None
        self.CCNF = None
        self.minimal_expr = ''
        self.NAND = None
        self.NOR = None
        self.expr_circuit = None
        self.minimal_expr_circuit = None
        self.NAND_circuit = None
        self.NOR_circuit = None
        self.variables = []
        self.print_options = None
        if expr:
            self.evaluate(expr)

    def evaluate(self, expr):
        self.__init__()
        self.TT = TruthTable(expr)
        self.expr = expr
        print('\nSolving expression...', end=' ')
        self.result = ExpressionSolver().solve(expr)
        print('Creating normal forms...', end=' ')
        self.CDNF = CDNF(self.TT, self.result)
        self.CCNF = CCNF(self.TT, self.result)
        print('Minimizing...', end=' ')
        self.minimal_expr = QuineMcCluskey(self.result, self.TT.variables).minimal_expr
        print('Converting to NAND and NOR...', end=' ')
        self.NAND = NandMaker().make_gate_expr(self.minimal_expr)
        self.NOR = NorMaker().make_gate_expr(self.minimal_expr)
        print('Creating Circuits...\n')
        self.variables = getVariables(self.expr)
        self.expr_circuit = space_to_string(create_circuit_from_expr(self.expr), self.variables)
        self.minimal_expr_circuit = space_to_string(create_circuit_from_expr(self.minimal_expr), self.variables)
        self.NAND_circuit = space_to_string(create_circuit_from_expr(self.NAND), self.variables)
        self.NOR_circuit = space_to_string(create_circuit_from_expr(self.NOR), self.variables)

        self.print_options = self.get_print_options()

    def create_prettyTable(self):
        table = PrettyTable()

        field_names = ['#', *deepcopy(self.TT.variables), self._get_formated_OGexpr(self.expr)]

        rows = [[i, ] for i in range(len(self.TT.table))]
        for i in range(len(rows)):
            rows[i].extend(self.TT.table[i])
            rows[i].append(self.result[i])

        table.field_names = field_names
        table.add_rows(rows)
        return table

    @staticmethod
    def _get_formated_OGexpr(expr):
        # prevents non unique field names for prettytable (if an expression is a single variable)
        if len(expr) == 1:
            expr = '(' + expr + ')'
        return expr

    def print(self):
        print(self.create_prettyTable(),
              f'\n Normal Forms: ({OPERATOR_SIGNS["AND"]} = AND; {OPERATOR_SIGNS["OR"]} = OR)'
              f'\n   CDNF:\n \t{self.CDNF}'
              f'\n   CCNF:\n \t{self.CCNF}\n'
              f'\n Minimal expression:'
              f'\n    \t{self.minimal_expr}'
              f'\n {self.result}'
              f'\n With NAND:'
              f'\n  {self.NAND}'
              f'\n With NOR:'
              f'\n  {self.NOR}'
              f'\n')
        print(self.minimal_expr_circuit)

    def print_with_options(self):
        print(self.create_prettyTable())
        print("\nType H for option info.")
        info = self.get_option_description()
        while True:
            in_ = input("Enter option: ").upper()
            if in_ == "H":
                print(info)
            elif in_ in ["NEW", "EXIT", "X"]:
                break
            else:
                try:
                    self.print_option(in_)
                except KeyError as e:
                    print(f'\nOption {e.args[0]} not found.{info}')

    def print_option(self, option):
        print(self.print_options[option], '\n')

    def get_print_options(self):
        CNAND = f'\n With NAND:' \
                f'\n{self.NAND_circuit}'
        CNOR = f'\n With NOR:' \
               f'\n{self.NOR_circuit}'
        return {'NF': f'\n   CDNF:\n \t{self.CDNF}'
                      f'\n   CCNF:\n \t{self.CCNF}',
                'M': f'\n Minimal expression:'
                     f'\n    \t{self.minimal_expr}',
                'G': f'\n With NAND:'
                     f'\n  {self.NAND}'
                     f'\n With NOR:'
                     f'\n  {self.NOR}',
                'C': self.expr_circuit,
                'CM': self.minimal_expr_circuit,
                'CG': f'{CNAND}\n{CNOR}',
                'CNAND': CNAND,
                'CNOR': CNOR
                }

    def get_option_description(self):
        option_desciptions = ["normal forms", "minimal expression", "with NAND and NOR",
                              "as circuit", "minimal expression as circuit", "NAND and NOR as circuit",
                              "NAND as Circuit", "NOR as circuit"]

        options_and_descriptions = \
            f'\n"new/exit/x" for new expression. "H" for Help\n' \
            f'\nEnter one of the following options to show expression...\n' \
            f'{self.build_option_descr_str(option_desciptions)}'
        # f'{nl.join(f"{op} : {desc}" for op, desc in zip(self.print_options, option_desciptions))}\n'
        return options_and_descriptions

    def build_option_descr_str(self, option_descr):
        options_with_description = ''
        option_keys = list(self.print_options)
        for i, x in enumerate(zip(self.print_options, option_descr)):
            if i < len(self.print_options) / 2:
                left_side = f'{x[0]} : {x[1]} '
                adjust = 24 - len(left_side)
                options_with_description += f'{left_side}{" "*adjust}'
                options_with_description += f'| {option_keys[i + len(self.print_options) // 2]} : ' \
                                            f'{option_descr[i + len(self.print_options) // 2]}\n'
            elif len(self.print_options) % 2 and x[0] == option_keys[i]:
                options_with_description += f'{x[0]} : {x[1]}\n'
        return options_with_description

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
        self.attribute_options = None
        self.option_descr = None
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
        self.NAND = NandMaker().make_gate_expr(self.expr)
        self.NOR = NorMaker().make_gate_expr(self.expr)
        print('Creating Circuits...\n')
        self.variables = getVariables(self.expr)
        try:
            self.expr_circuit = space_to_string(create_circuit_from_expr(self.expr), self.variables)
            self.minimal_expr_circuit = space_to_string(create_circuit_from_expr(self.minimal_expr), self.variables)
            self.NAND_circuit = space_to_string(create_circuit_from_expr(self.NAND), self.variables)
            self.NOR_circuit = space_to_string(create_circuit_from_expr(self.NOR), self.variables)
        except Exception:
            print("Ooops: Failed to create circuits :(")
        self.attribute_options = self.get_print_options()
        self.option_descr = self.get_option_description()

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

    def get_print_options(self):
        CNAND = f'\nWith NAND:' \
                f'\n{self.NAND_circuit}'
        CNOR = f'\nWith NOR:' \
               f'\n{self.NOR_circuit}'
        return {'NF': f'\nCDNF:\n {self.CDNF}'
                      f'\nCCNF:\n {self.CCNF}',
                'M': f'\nMinimal expression:'
                     f'\n {self.minimal_expr}',
                'G': f'\nWith NAND:'
                     f'\n {self.NAND}'
                     f'\nWith NOR:'
                     f'\n {self.NOR}',
                'C': self.expr_circuit,
                'T': f'{self.create_prettyTable()}\n{self.result}',
                'CM': self.minimal_expr_circuit,
                'CG': f'{CNAND}\n{CNOR}',
                'CNAND': CNAND,
                'CNOR': CNOR,
                'S': self.start_save_options
                }

    def get_option_description(self):
        option_desciptions = ["normal forms", "minimal expression", "with NAND and NOR",
                              "as circuit", "table with result", "minimal expression as circuit",
                              "NAND and NOR as circuit", "NAND as Circuit", "NOR as circuit",
                              "Open save menu (choose options to save to file)"]

        options_and_descriptions = \
            f'\n"new/exit/x" for new expression. "H" for Help\n' \
            f'\nEnter one of the following options to show expression...\n' \
            f'{self.build_option_descr_str(option_desciptions)}'
        return options_and_descriptions

    def build_option_descr_str(self, option_descr):
        options_with_description = ''
        option_keys = list(self.attribute_options)
        for i, x in enumerate(zip(self.attribute_options, option_descr)):
            if i < len(self.attribute_options) // 2:
                left_side = f'{x[0]} : {x[1]} '
                adjust = 24 - len(left_side)
                options_with_description += f'{left_side}{" " * adjust}'
                options_with_description += f'| {option_keys[i + len(self.attribute_options) // 2]} : ' \
                                            f'{option_descr[i + len(self.attribute_options) // 2]}\n'
            elif len(self.attribute_options) % 2 and x[0] == option_keys[-1]:
                options_with_description += f'{x[0]} : {x[1]}\n'
        return options_with_description

    def print_with_options(self):
        print(self.create_prettyTable())
        print(self.result)
        print("\nType H for option info.")
        self.option_menu(mode_prompt="O> Enter option: ")

    def option_menu(self, mode_prompt, file=None):
        while True:
            option = input(mode_prompt).upper()
            if option == "H":
                print(self.option_descr)
            elif option in ["NEW", "EXIT", "X"]:
                break
            elif option == 'S' and mode_prompt[:2] == 'S>':
                print("Already in save mode!")
            else:
                try:
                    if mode_prompt[:2] == 'S>':
                        self.save_option_to_file(self.attribute_options[option], file)
                        print("Saved!")
                    else:
                        self.print_option(option)
                except KeyError as e:
                    print(f'\nOption {e.args[0]} not found.{self.option_descr}')

    def print_option(self, option):
        if option == 'S':
            self.attribute_options[option]()
        else:
            print(self.attribute_options[option], '\n')

    def start_save_options(self):
        print("Choose from the same options('H') to save output to a text file.")
        file = self.create_new_txt_file()
        print(f'Created file: {file}')
        self.option_menu(mode_prompt="S> Enter option: ", file=file)

    @staticmethod
    def save_option_to_file(option, file):
        with open(file, 'a', encoding='utf-8') as f:
            f.write(f'\n{option}')

    def create_new_txt_file(self):
        import os
        i = 0
        FILENAME = 'expression'
        DOWNLOADS_FOLDER = os.path.join(os.getenv('USERPROFILE'), 'Downloads')
        FILE = os.path.join(DOWNLOADS_FOLDER, f'{FILENAME}{i}.txt')
        while os.path.isfile(FILE):
            FILE = os.path.join(DOWNLOADS_FOLDER, f'{FILENAME}{i}.txt')
            i += 1
        with open(FILE, 'w') as f:
            f.write(f'Saved expression: {self.expr}\n')
        return FILE

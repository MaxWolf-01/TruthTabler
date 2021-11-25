from bool_expressions import Node, translate_operators, ExpressionSolver
from normal_forms import _NOT
from truth_table import getVariables, prepare_to_list

_NAND = '↑'
_NOR = '↓'


class LogicGateMaker:
    def __init__(self, operator, expr=None):
        self.operator = operator
        self.expr = None
        if expr:
            self.get_gate_expression(expr)

    def get_gate_expression(self, expr):
        unifier = globals()[self.operator + 'unifier']()
        unified_expr = unifier.unify(expr)
        unified_expr = translate_operators(prepare_to_list(_format_str_expr(_list_expr_as_str(unified_expr))))
        unified_expr = _extract_vars_from_lists_in_parsed_list_expr(_back_to_list_expr(unified_expr))
        self.expr = self.create_NAND_NOR(unified_expr)
        return self.expr

    def create_NAND_NOR(self, uniform_expression):
        sign = globals()[f'_N{self.operator}']

        def invert(expr):
            if len(expr) == 1:
                # no useless parenthesis aroung single variables for readability
                return f'({expr}{sign}{expr})'
            else:
                return f'(({expr}){sign}({expr}))'

        def convert(expr: list, invert_next=False):
            converted_expr = ""
            invert_this = invert_next
            for i, x in enumerate(expr):
                while isinstance(x, list) and len(x) == 1:
                    x = x[0]
                if not isinstance(x, list):
                    if x == 'NOT':
                        if isinstance(expr[i + 1], list):
                            if expr[i+1][0] == 'NOT':
                                converted_expr = convert(expr[i+1][1])  # removes double negations
                                break
                        else:
                            invert_this = True
                    elif len(x) == 1:
                        converted_expr += f'{x}'
                    else:
                        converted_expr += f'{sign}'
                else:
                    invert_next = i != 1 and len(x) == 3  # i == 1 or 2
                    converted_expr += convert(x, invert_next)
            if invert_this:
                return invert(converted_expr)
            elif len(expr) == 1 or len(expr) == 2:
                return converted_expr
            return f'({converted_expr})'
        return convert([uniform_expression])


class NandMaker(LogicGateMaker):
    def __init__(self, normal_form=None):
        super().__init__('AND', normal_form)


class NorMaker(LogicGateMaker):
    def __init__(self, normal_form=None):
        super().__init__('OR', normal_form)


class ExpressionUnifier:
    """
    :returns a boolean expression consisting of only 'AND', 'OR' or 'NOT' converted to an expressing consiting only of
    either 'AND' or 'OR' and 'NOT'
    """

    def __init__(self, operator, expr=None):
        self.operator = operator
        self.expr = expr
        self.unified_expr = None
        if expr:
            self.unify(expr)

    def unify(self, expr):
        node = Node(expr)
        tree = _extract_vars_from_lists_in_parsed_list_expr(node.get_expression_as_lists())
        if self.is_unified(node.get_expression_as_string()):
            return tree
        unified = self._convert(tree)
        unified = self.remove_all_double_negations(unified)
        self.unified_expr = unified
        return unified

    def _convert(self, expr: list):
        sign = self.operator
        de_morgan = False
        left = None
        right = None
        operator = None
        for i, x in enumerate(expr):
            if x in ['AND', 'OR', 'NOT']:
                operator = x
                de_morgan = (operator != sign and not operator == 'NOT')
            else:
                if isinstance(x, list):
                    x = self._convert(x)
                if left:
                    right = x
                else:
                    left = x
        if de_morgan:
            converted_expr = [_NOT, [[[_NOT, left]], sign, [_NOT, right]]]
        else:
            if operator == 'NOT':
                converted_expr = [_NOT, left]
            else:
                converted_expr = [left, sign, right]
        return converted_expr

    def is_unified(self, expr):
        return self.contains_only_NOT(expr) or not self.contains_different_operators(expr, self.operator)

    @staticmethod
    def contains_only_NOT(expr):
        return 'OR' not in expr and 'AND' not in expr

    @staticmethod
    def contains_different_operators(expr, operator):
        return ('OR' in expr and 'AND' in expr) or operator not in expr

    @staticmethod
    def remove_all_double_negations(unified_expr):
        change = True
        old_expr = unified_expr
        new_expr = []
        while change:
            new_expr = ExpressionUnifier._remove_double_negations(unified_expr)
            change = new_expr != old_expr
            old_expr = new_expr
        return new_expr

    @staticmethod
    def _remove_double_negations(expr):
        def _is_double_negated(expr_, i_):
            return expr_[i_] == _NOT and isinstance(expr_[i_ + 1], list) and expr_[i_ + 1][0] == _NOT

        new_expr = []
        for i, x in enumerate(expr):
            if isinstance(x, list):
                new_expr.append(ExpressionUnifier._remove_double_negations(x))
            elif _is_double_negated(expr, i):
                return expr[i + 1][1]
            else:
                new_expr.append(x)
        return new_expr


def _extract_vars_from_lists_in_parsed_list_expr(parsed_expr):
    string_expr = _list_expr_as_str(parsed_expr)
    vars_ = getVariables(_format_str_expr(string_expr))
    for var in vars_:
        change = True
        while change:
            old_expr = string_expr
            string_expr = string_expr.replace(f'["{var}"]', f'"{var}"', -1)
            change = string_expr != old_expr
    return eval(string_expr)


def _back_to_list_expr(expr):
    new_expr = ''
    for i, x in enumerate(expr):
        if x == '(':
            new_expr += '['
        elif x == ')':
            new_expr += ']'
        else:
            if expr[i - 1] and expr[i - 1] != '(' and new_expr[-1:] != ',':
                new_expr += ','
            new_expr += f'"{x}"'
            if expr[i + 1] and expr[i + 1] != ')' and new_expr[-1:] != ',':
                new_expr += ','
    return eval(new_expr)


def _list_expr_as_str(parsed_expr):
    return f"{parsed_expr}".replace("\'", '"', -1)


def _format_str_expr(expr):
    expr = expr.replace('[', '(', -1)
    expr = expr.replace(']', ')', -1)
    expr = expr.replace(',', '', -1)
    expr = expr.replace('"', '', -1)
    return expr


class ANDunifier(ExpressionUnifier):
    def __init__(self, expr=None):
        super().__init__('AND', expr)


class ORunifier(ExpressionUnifier):
    def __init__(self, expr=None):
        super().__init__('OR', expr)


test_cases = ['(¬A+¬B)·(¬A+B)·(A+B)', '(A and ¬B)', '(¬A+¬B)·(¬A+B)', '(C·D)+(¬A·C)+(¬A·D)+(¬A·¬B)+(¬B·C)',
              '(¬A·B)·(A+B)+(¬A+B)', '(A OR B)', 'NOT (A OR B)']


def test(expresssions: list):
    for expr in expresssions:
        result = ExpressionSolver(expr).solve()
        NOR = NorMaker(expr)
        NAND = NandMaker(expr)
        NAND_result = ExpressionSolver(NAND.expr).solve()
        NOR_result = ExpressionSolver(NOR.expr).solve()
        print(f'{expr} : {result}')
        if NAND_result != result:
            print(f'WRONG NAND : {NAND_result}')
        if NOR_result != result:
            print(f'WRONG NOR : {NOR_result})')

        print(f'\n{NOR.expr}\n{NAND.expr}\n')


def main():
    test(test_cases)


if __name__ == '__main__':
    main()

# from truth_tabler import TruthTabler
#
# tabler = TruthTabler()
# x1 = '(¬A+¬B)·(¬A+B)·(A+B)'
# x2 = '(¬A+¬B)·(¬A+B)·(A+B)'
# print(tabler.evaluate(remove_double_negations(de_morgan_outer(x1))) == tabler.evaluate(x1))
# print(tabler.evaluate(remove_double_negations(de_morgan_inner(x2))) == tabler.evaluate(x2))

#                                             (¬A+¬B)·(¬A+B)·(A+B) # CCNF
#                                            ¬(¬(¬A+¬B)+¬(¬A+B)+¬(A+B)) same as above  # CCNF to OR -> demorgan outer
#                                            ¬(A·B)·¬(A·¬B)·¬(¬A·¬B) same as above # CCNF to AND -> demorgan inner
#
#                          should b nand      (((A↓B) ↓ (A ↓ (B↓B))) ↓ ((A↓B) ↓ (A ↓ (B↓B))) ↓ (((A↓A) ↓ (B↓B)))) ↓
#                                             (((A↓B) ↓ (A ↓ (B↓B))) ↓ ((A↓B) ↓ (A ↓ (B↓B))) ↓ (((A↓A) ↓ (B↓B))))
#                                             (¬A·¬B)+(A·B) CDNF
#                                             ¬(A+B)+¬(¬A+¬B) CDNF sao. # CDNF to OR -> demorgan inner
#                                             ¬(¬(¬A·¬B)·¬(A·B)) CDNF sao. # CDNF to AND -> demorgan outer

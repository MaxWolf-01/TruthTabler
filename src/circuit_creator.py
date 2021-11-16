import random

from circuit_creator_helper_methods import *
from circuit_creator_static_variables import *
from truth_table import prepare, getVariables
from bool_expressions import Node, translate_operators
import time

LINE_WIDTH = 0


def connect_lines(lines, var_count, idx_var0, idx_var1):
    idx0 = idx_var0 * 2
    idx1 = idx_var1 * 2

    lines[idx0][1] = LINE_JOIN
    lines[idx1][3] = LINE_JOIN

    for i in range(idx_var0 * 2 + 1, var_count * 2 + 2):
        lines[i][1] = LINE_HORIZONTAL

    for i in range(idx_var1 * 2 + 1, var_count * 2 + 2):
        lines[i][3] = LINE_HORIZONTAL


def build_box(space, x, y, sign, is_negated0, is_negated1):
    def write_blueprint(x_, y_, blueprint):
        counter = 0
        for j in blueprint:
            space[x_ + counter][y_] = j
            counter += 1

    struct = ("|---|", f"|{sign}|-" + LINE_CORNER, "|---|")
    offset = 0
    for i in struct:
        write_blueprint(x, y + offset, i)
        offset += 1

    space[x - 1][y] = "o" if is_negated0 else "-"
    space[x - 1][y + 2] = "o" if is_negated1 else "-"


def print_space(space, variables=None):
    if variables is None:
        variables = []

    # for dramatic effect baby YES
    def sleep():
        time.sleep(random.random() * 0.3 + 0.1)

    sleep()
    print(" ".join(variables))

    height = len(space[0])

    for y in range(height):
        cache = ""
        for x in range(len(space)):
            cache += space[x][y]

        sleep()
        print(cache)


def draw_horizontal_connected_line(space, x, y, length):
    space[x][y] = "+"
    for i in range(1, length):
        space[x + i][y] = "-"


def draw_horizontal_line(space, x, y, length):
    for i in range(length):
        space[x + i][y] = "-"
    space[x + length][y] = LINE_CORNER


def draw_vertical_line_up(space, x, y, length):
    for i in range(0, length - 1):
        space[x][y - i] = "|"
    space[x][y - length + 1] = LINE_CORNER


def draw_vertical_line_down(space, x, y, length):
    for i in range(0, length - 1):
        space[x][y + i] = "|"
    space[x][y + length - 1] = LINE_CORNER


# (("A"), "AND", ("B"))
# TODO: make variables global
# TODO: extract duplicates
# TODO: make build lines use global variables
# TODO: make building the lines and building the box one function
# TODO: use better variable names
# TODO: make build_box have y = 1 default
# TODO: dont override the + when combining two gates
def fill_circuit(tree, variables):
    if tree[0] == "NOT":
        tree = tree[1]

    is_var0 = is_variable(tree[0])
    is_var1 = is_variable(tree[2])
    var_count = len(variables)
    operator = tree[1]

    # check each possibility on how we should format
    if is_var0 and is_var1:
        idx_var0 = variables.index(get_variable(tree[0]))
        idx_var1 = variables.index(get_variable(tree[2]))

        space = build_lines(4, var_count)
        connect_lines(space, var_count, idx_var0, idx_var1)

        extend_space(space, 8, 4)
        build_box(space, LINE_WIDTH, 1, globals()[f"{operator}_SIGN"], is_negated(tree[0]), is_negated(tree[2]))

        return space, LINE_WIDTH + 6, 2, 1

    elif is_var0 and not is_var1:
        idx_var0 = variables.index(get_variable(tree[0]))

        lower_space, out_x, out_y, level = fill_circuit(tree[2], variables)
        extend_space(lower_space, 8, len(lower_space[0]))

        upper_space = build_lines(4, var_count)
        extend_space(upper_space, 8 * (level + 1), 4)

        build_box(upper_space, LINE_WIDTH + 8 * level, 1, globals()[f"{operator}_SIGN"],
                  is_negated(tree[0]), is_negated(tree[2]))

        draw_horizontal_connected_line(upper_space, idx_var0 * 2, 1, LINE_WIDTH + 8 * level - idx_var0 * 2 - 1)
        merge_spaces(upper_space, lower_space)

        out_y += 4

        draw_vertical_line_up(upper_space, out_x, out_y - 1, out_y - 3)

        return upper_space, LINE_WIDTH + 8 * (level + 1) - 2, 2, level + 1

    elif not is_var0 and is_var1:
        idx_var1 = variables.index(get_variable(tree[2]))

        upper_space, out_x, out_y, level = fill_circuit(tree[0], variables)
        extend_space(upper_space, 8, len(upper_space[0]))

        lower_space = build_lines(4, var_count)
        extend_space(lower_space, 8 * (level + 1), 4)

        build_box(lower_space, LINE_WIDTH + 8 * level, 1, globals()[f"{operator}_SIGN"],
                  is_negated(tree[0]), is_negated(tree[2]))

        draw_horizontal_connected_line(lower_space, idx_var1 * 2, 3, LINE_WIDTH + 8 * level - idx_var1 * 2 - 1)
        merge_spaces(upper_space, lower_space)

        draw_vertical_line_down(upper_space, out_x, out_y + 1, len(upper_space[0]) - out_y - 3)

        return upper_space, LINE_WIDTH + 8 * (level + 1) - 2, len(upper_space[0]) - 2, level + 1

    else:
        upper_space, upper_out_x, upper_out_y, upper_level = fill_circuit(tree[0], variables)
        lower_space, lower_out_x, lower_out_y, lower_level = fill_circuit(tree[2], variables)

        if upper_level > lower_level:
            extend_space(lower_space, 8 * (upper_level - lower_level + 1), len(lower_space[0]))
            extend_space(upper_space, 8, len(upper_space[0]))
        elif upper_level < lower_level:
            extend_space(upper_space, 8 * (lower_level - upper_level + 1), len(upper_space[0]))
            extend_space(lower_space, 8, len(lower_space[0]))
        else:
            extend_space(upper_space, 8, len(upper_space[0]))
            extend_space(lower_space, 8, len(lower_space[0]))

        level = max(upper_level, lower_level)

        middle_space = build_lines(4, var_count)
        extend_space(middle_space, LINE_WIDTH + 8 * (level + 1), 4)
        build_box(middle_space, LINE_WIDTH + 8 * level, 1, globals()[f"{operator}_SIGN"],
                  is_negated(tree[0]), is_negated(tree[2]))

        middle_upper_in_y = 1 + len(upper_space[0])
        middle_lower_in_y = 3 + len(upper_space[0])
        merge_spaces(upper_space, middle_space)

        lower_out_y += len(upper_space[0])
        merge_spaces(upper_space, lower_space)

        if upper_level > lower_level:
            draw_horizontal_line(upper_space, lower_out_x, lower_out_y, 8 * (level - lower_level))
        elif upper_level < lower_level:
            draw_horizontal_line(upper_space, upper_out_x, upper_out_y, 8 * (level - upper_level))

        out_x = LINE_WIDTH + 8 * level - 2
        draw_vertical_line_down(upper_space, out_x, upper_out_y + 1, middle_upper_in_y - upper_out_y)
        draw_vertical_line_up(upper_space, out_x, lower_out_y - 1, lower_out_y - middle_lower_in_y)

        return upper_space, LINE_WIDTH + 8 * (level + 1) - 2, middle_upper_in_y + 1, level + 1


def create_circuit(tree, variables):
    global LINE_WIDTH
    LINE_WIDTH = len(variables) * 2 + 2
    return fill_circuit(tree, variables)[0]


def create_circuit_from_string(expr):
    tree = Node(expr).get_expression_as_lists()
    vars_ = getVariables(expr)
    return create_circuit(tree, vars_)


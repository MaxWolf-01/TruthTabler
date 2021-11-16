from circuit_creator_static_variables import *


def is_variable(branch):
    return all(isinstance(x, str) for x in branch)


def is_negated(branch):
    return branch[0] == "NOT"


def get_variable(branch):
    return branch[-1]


def build_lines(height, var_count):
    space = []

    # we dont do one liners here
    for i_width in range(var_count):
        space.append([LINE_VERTICAL] * height)
        space.append([" "] * height)

    for i in range(2):
        space.append([" "] * height)

    return space


def extend_space(space, amount, height):
    for i in range(amount):
        space.append([" "] * height)


def merge_spaces(space1, space2):
    for column in range(len(space1)):
        space1[column].extend(space2[column])

# used for translating string & function names
OPERATORS = {
    'NOT': ("NOT", "!", '¬', '-'),
    'AND': ("AND", "&&", '&', '·', '∧'),
    'OR': ("OR", "||", '+', '∨'),
    'NAND': ('NAND', '↑'),
    'NOR': ('NOR', '↓'),
    'XOR': ("XOR", '⊕', '⊻'),
    'IF': ("IF", '→', "->", '=>'),
    'EQ': ('EQ', "==", "⟷", 'EQUALS')
}

# used for printing
# TODO find signs for XOR and EQ that work in terminal
OPERATOR_SIGNS = {
    'NOT': '¬',
    'AND': '·',  # '∧', '∨' dont work in terminal
    'OR': '+',
    'NAND': '↑',
    'NOR': '↓',
    'XOR': '⊻',  # '⊕',⊻  dont work in terminal
    'IF': '→',
    'EQ': '⟷',
}

SUPPORTED_OPERATORS = '\n'.join(str(OPERATORS[k]) for k in OPERATORS)

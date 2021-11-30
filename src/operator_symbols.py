# used for translating string & function names
OPERATORS = {
    'NOT': ("NOT", "!", '¬', '-'),
    'AND': ("AND", "&&", '&', '·', '∧'),
    'OR': ("OR", "||", '+', '∨'),
    'NAND': ('NAND', '↑'),
    'NOR': ('NOR', '↓'),
    'XOR': ("XOR", '⊻'),
    'IF': ("IF", '→', "->", '=>'),
    'EQ': ('EQ', "==", "⟷", 'EQUALS')
}

# used for printing
OPERATOR_SIGNS = {
    'NOT': '¬',
    'AND': '·',  # '∧', '∨' dont work in terminal
    'OR': '+',
    'NAND': '↑',
    'NOR': '↓',
    'XOR': '⊻',
    'IF': '→',
    'EQ': '⟷',
}
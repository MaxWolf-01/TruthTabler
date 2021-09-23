import itertools


class TruthTable:
    @staticmethod
    def createTT(n):
        return list(itertools.product([0, 1], repeat=n))

    @staticmethod
    def getVariables(expr):
        return sorted({x for x in expr if x.isalpha() and len(x) == 1})
    
    def __init__(self, expr: list, reversed_table = False):
        self.variables = self.getVariables(expr)
        self.table = self.createTT(len(self.variables))
        if reversed_table:
            self.reverse_table()

    def reverse_table(self):
        self.table = self.table[::-1]
        
from truth_table import TruthTable


class NormalForm:
    def __init__(self, truth_table: TruthTable, results, nf_params):
        self.TT = truth_table
        self.TT_results = self.set_results(results)
        self.result = self.NF(*nf_params)

    def __str__(self):
        return "".join(self.result)

    @staticmethod
    def set_results(results):
        if type(results) == list:
            return results
        return [int(val) for val in results]

    def NF(self, cdnf_else_ccnf: bool, inner_junction: str, outer_junction: str) -> list:
        if len(self.TT_results) != len(self.TT.table):
            raise Exception('Invalid Input (result and truth table rows do not match in length)')
        nf = []
        for i in range(len(self.TT.table)):
            if self.TT_results[i] == cdnf_else_ccnf:
                if nf:
                    nf.append(outer_junction)
                nf.append('(')
                row = self.TT.table[i]
                for j in range(len(self.TT.variables)):
                    if j != 0:
                        nf.append(inner_junction)
                    var = self.TT.variables[j]
                    if row[j] if cdnf_else_ccnf else not row[j]:
                        nf.append(var)
                    else:
                        nf.append('¬')
                        nf.append(var)
                nf.append(')')
        return nf


class CDNF(NormalForm):
    def __init__(self, truth_table, results):
        super(CDNF, self).__init__(truth_table, results, [True, '&', '||'])


class CCNF(NormalForm):
    def __init__(self, truth_table, results):
        super(CCNF, self).__init__(truth_table, results, [False, '||', '&'])


# '∧', '∨' dont work in terminal
# x = CCNF(TruthTable(['p', 'q', 'r'], True), '10100100')
# print(x)

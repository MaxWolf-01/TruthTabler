from truth_table import TruthTable

_CONJUNCTION = '·'
_DISJUNCTION = '+'
_NOT = '¬'
# '∧', '∨' dont work in terminal; '||' is annoying bcs 2 chars


class NormalForm:
    def __init__(self, truth_table: TruthTable, results, nf_params):
        self.TT = truth_table
        self.TT_results = self.set_results(results)
        self.result = self.NF(*nf_params)

    def __str__(self):
        return self.result

    @staticmethod
    def set_results(results):
        if type(results) == str:
            return [int(val) for val in results]
        return results

    def NF(self, cdnf_else_ccnf: bool, inner_junction: str, outer_junction: str):
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
                    if j:
                        nf.append(inner_junction)
                    var = self.TT.variables[j]
                    if row[j] if cdnf_else_ccnf else not row[j]:
                        nf.append(var)
                    else:
                        nf.append(_NOT)
                        nf.append(var)
                nf.append(')')
        return ''.join(nf)


class CDNF(NormalForm):
    def __init__(self, truth_table, results):
        super(CDNF, self).__init__(truth_table, results, [True, _CONJUNCTION, _DISJUNCTION])


class CCNF(NormalForm):
    def __init__(self, truth_table, results):
        super(CCNF, self).__init__(truth_table, results, [False, _DISJUNCTION, _CONJUNCTION])

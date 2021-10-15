import math
import string
from copy import deepcopy

from src.normal_forms import _CONJUNCTION, _DISJUNCTION, _NOT
from src.truth_table import createTT


# todo Dont care's (just omit the terms in the pi_table)

def factor_expression():
    pass  # todo


class QuineMcCluskey:
    def __init__(self, truth_table_result=None):
        self.TT = []
        self.minterms = []
        self.minterm_groups = {}
        self.prime_implicants = set()
        self.essential_prime_implicants = set()
        self.minimal_expr = ''
        if truth_table_result:
            self.minimize(truth_table_result)

    def minimize(self, result):
        if len(result) % 2:
            raise Exception(f'Invalid result length {len(result)}. Not a power of 2.')
        self.__init__()
        self.TT = createTT(self.get_num_vars(result))
        self.minterms = self.get_minterm_idxs(result)
        if self.is_constant()[0]:
            constant = self.is_constant()[1]
            self.minimal_expr = constant
            return constant
        self._group_minterms()
        self._merge_all_groups()
        self._solve_prime_implicant_table()
        self._set_minimal_expr()
        return self.minimal_expr

    @staticmethod
    def get_num_vars(truth_table_result):
        return int(math.log2(len(truth_table_result)))

    @staticmethod
    def get_minterm_idxs(truth_table_result):
        return tuple(i for i in range(len(truth_table_result)) if truth_table_result[i] == 1)

    def is_constant(self):
        if not self.minterms:
            return True, 0
        if len(self.minterms) == len(self.TT):
            return True, 1
        return False, None

    def _group_minterms(self):
        # groups the minterms based on the number of ones
        for i in range(len(self.minterms)):
            minterm_index = self.minterms[i]
            ith_minterm = self.TT[minterm_index]
            minterm_group = ith_minterm.count(1)
            self.minterm_groups.setdefault(minterm_group, []).append(((minterm_index,), ith_minterm))

    def _merge_all_groups(self):
        while True:
            if not self._merge_groups():
                break

    def _merge_groups(self):
        """
        merges each minterm of group n with each minterm of group n+1 if possible
        :returns: True if able to further merge else False
        """
        merged_minterm_groups = {}
        ticked = set()
        for group_count in range(len(self.minterm_groups) - 1):
            group = list(self.minterm_groups.keys())[group_count]
            next_group = list(self.minterm_groups.keys())[group_count + 1]
            for minterm_idx in range(len(self.minterm_groups[group])):
                minterm = self.minterm_groups[group][minterm_idx]
                for next_minterm_idx in range(len(self.minterm_groups[next_group])):
                    next_minterm = self.minterm_groups[next_group][next_minterm_idx]

                    merged_minterm = self._merge_minterms(minterm, next_minterm)
                    if merged_minterm:
                        merged_minterm_groups.setdefault(group, []).append(merged_minterm)
                        ticked.add(minterm)
                        ticked.add(next_minterm)

                if minterm not in ticked:
                    self.prime_implicants.add(minterm)
        self._check_last_group_for_ticked_minterms(ticked)
        if merged_minterm_groups:
            self.minterm_groups = merged_minterm_groups
            return True
        return False

    @staticmethod
    def _merge_minterms(m1, m2):
        """
        if minterms differ in a single bit, replace said bit with '_'
        :returns: The minterms involved in the merge and the merged minterm || False if more than one bit difference
        e.g: ((0,), (0,0,0)), ((1,), (0,0,1)) => ((0, 1), (0,0,'_'))
        """
        different_bits_idxs = [i for i in range(len(m1[1])) if m1[1][i] != m2[1][i]]
        if len(different_bits_idxs) > 1:
            return False
        merged = list(m1[1])
        merged[different_bits_idxs[0]] = '_'
        minterm_numbers = tuple(set(m1[0]).union(set(m2[0])))
        return minterm_numbers, tuple(merged)

    def _check_last_group_for_ticked_minterms(self, ticked):
        for minterm in self.minterm_groups[list(self.minterm_groups.keys())[-1]]:
            if minterm not in ticked:
                self.prime_implicants.add(minterm)

    def _solve_prime_implicant_table(self):
        self.prime_implicants = self._remove_duplicate_implicants(self.prime_implicants)
        pi_table = self.create_prime_implicant_table(self.prime_implicants)
        while pi_table:
            initial_table = deepcopy(pi_table)
            pi_table = self._reduce_pi_table(pi_table)
            if initial_table == pi_table:  # no further reduction possible
                break
        if pi_table:
            raise Exception("This boolean function is cyclic. Not implemented yet")  # todo

    def _reduce_pi_table(self, pi_table):
        pi_table = self._extract_epis(pi_table)
        pi_table = self._row_dominance(pi_table)
        pi_table = self._col_dominance(pi_table)
        return pi_table

    @staticmethod
    def _remove_duplicate_implicants(prime_implicants):
        pis = list(prime_implicants)
        no_duplicate_pis = []
        for pi in pis:
            ndpi_values = [ndpi[1] for ndpi in no_duplicate_pis]
            pi_occurence = ndpi_values.count(pi[1])
            if pi_occurence == 0:
                no_duplicate_pis.append(pi)
        return no_duplicate_pis

    @staticmethod
    def create_prime_implicant_table(prime_implicants) -> dict:
        """
        columns(keys) : minterm numbers
        rows(values) : all prime implicants that cover the minterm
        """
        pi_table = dict()
        for prime_implicant in prime_implicants:
            for minterm in prime_implicant[0]:
                pi_table.setdefault(minterm, [])
                pi_table[minterm].append(prime_implicant[1])
        return dict(sorted(pi_table.items()))

    def _extract_epis(self, pi_table):
        new_epis = self._get_epis(pi_table)
        if new_epis:
            self.essential_prime_implicants.update(new_epis)
            return self._remove_covered_minterms(pi_table, self._get_minterms_covered_by_epi(pi_table, new_epis))
        return pi_table

    @staticmethod
    def _get_epis(pi_table):
        epis = set()
        for minterm in pi_table.keys():
            if len(pi_table[minterm]) == 1:
                epis.add(pi_table[minterm][0])
        return epis

    @staticmethod
    def _remove_covered_minterms(pi_table, covered_minterms):
        for minterm in covered_minterms:
            del pi_table[minterm]
        return pi_table

    @staticmethod
    def _get_minterms_covered_by_epi(pi_table, epis):
        covered_minterms = set()
        for minterm in pi_table.keys():
            for epi in epis:
                if epi in pi_table[minterm]:
                    covered_minterms.add(minterm)
        return covered_minterms

    def _row_dominance(self, pi_table):
        """
        Removes prime implicants whose covered minterms are subsets of other prime implicants (redundant)
        """
        dominated_pis = self._get_row_dominated_prime_implicants(pi_table)
        return self._remove_dominated_pis(pi_table, dominated_pis)

    @staticmethod
    def _get_row_dominated_prime_implicants(pi_table):
        """
        :returns: prime implicants which are subsets of other prime implicants
        A prime implicant which covers all the minterms of another is a superset of said prime implicant / dominates.
        If two or more prime implicants cover the same minterms the first one is taken as dominant,
        since we can take either one.
        """
        dominated_pis = set()
        pi_occ_table = QuineMcCluskey.transposed_pi_table(pi_table)
        for i1 in range(len(pi_occ_table)):
            pi1 = pi_occ_table[list(pi_occ_table.keys())[i1]]
            for i2 in range(len(pi_occ_table)):
                if i1 != i2 and i2 > i1:
                    pi2 = pi_occ_table[list(pi_occ_table.keys())[i2]]
                    if pi1.issubset(pi2):
                        dominated_pis.add(list(pi_occ_table.keys())[i1])
                    elif pi2.issubset(pi1):
                        dominated_pis.add(list(pi_occ_table.keys())[i2])
        return dominated_pis

    @staticmethod
    def _remove_dominated_pis(pi_table, dominated_pis):
        for dom in dominated_pis:
            for minterm in pi_table:
                if dom in pi_table[minterm]:
                    pi_table[minterm] = tuple(pi for pi in pi_table[minterm] if pi != dom)
        return pi_table

    @staticmethod
    def transposed_pi_table(pi_table):
        """
        switches keys and values of the regular prime implicant table
          =>  prime implicants(keys) : minterms(values)
        """
        pis = set((pi for pis in list(pi_table.values()) for pi in pis))
        pi_occurences = dict()
        for pi in pis:
            pi_occurences.setdefault(pi, set())
            for minterm in pi_table:
                if pi in pi_table[minterm]:
                    pi_occurences[pi].add(minterm)
        return pi_occurences

    def _col_dominance(self, pi_table):
        dominated_minterms = self._get_col_dominating_prime_implicants(pi_table)
        pi_table = self._remove_covered_minterms(pi_table, dominated_minterms)
        return pi_table

    @staticmethod
    def _get_col_dominating_prime_implicants(pi_table):
        dominating_cols = set()
        for mint1 in pi_table.keys():
            for mint2 in pi_table.keys():
                if mint1 != mint2 and mint2 > mint1:
                    if set(pi_table[mint1]).issubset(set(pi_table[mint2])):
                        dominating_cols.add(mint2)
                    elif set(pi_table[mint2]).issubset(set(pi_table[mint1])):
                        dominating_cols.add(mint1)
        return dominating_cols

    def _set_minimal_expr(self):
        vars_ = string.ascii_uppercase
        for epi in self.essential_prime_implicants:
            if self.minimal_expr:
                self.minimal_expr += _DISJUNCTION
            self.minimal_expr += '('
            for i in range(len(epi)):
                if epi[i] == '_':
                    continue
                if epi[i] == 1:
                    self.minimal_expr += vars_[i]
                    self.minimal_expr += _CONJUNCTION
                else:
                    self.minimal_expr += _NOT + vars_[i]
                    self.minimal_expr += _CONJUNCTION
            self.minimal_expr = self.minimal_expr[:len(self.minimal_expr) - 1]
            self.minimal_expr += ')'


# Q = QuineMcCluskey()
# print(Q.minimize([1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0]))  # cyclic
# print(TruthTabler(Q.minimal_expr).result == [1,0,1,1,1,1,1,1,1,1,1,1,1,1,0,0])

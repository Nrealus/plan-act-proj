from __future__ import annotations

import sys

sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
import warnings
import math
from enum import Enum
from copy import copy, deepcopy
from src.utility.unionfind import UnionFind2
from domain import ComparisonOp, Domain
from constraints import ConstraintType
from stn import STN

############################################

# 28 / 08 / 2022

# The binding constraint network is implemented here.
# Additional info is available in the notes for constraints.py,
# notably on the linkage in constraint propagation between the STN and BCN.

# Currently, (partial) propagation is achieved through full lookahead arc consistency (aka maintaining arc consistency) based on AC-3.
# In the future, adapting a more advanced constraint propagation algorithm would be desirable.

# Representations and data structures aren't very optimised, except for the Union-Find for the unification/equality constraint.
# Relation tables are represented in a very crude way. In the future, a B-tree or BDD representation could be used.
# Support for "functional" (continuous) relations would be very welcome in the future

# As a side note, the union-find isn't necessarily that suitable if we want to support ordering constraints,
# as using a simple adjacency list representation of a graph (just like for the other constraints) would be easier for that.
# However, we would lose the efficiency of the lookups and connected component fetching.

# Extensions accounting for uncertainty, probability, and partial observability are kept for later.

############################################


class BCN():

    def __init__(self):
        self.m_domains: typing.Dict[str, Domain] = {}
        self.m_unifications: UnionFind2 = UnionFind2()
        self.m_disj_unifications: typing.Dict[str,typing.Set[str]] = {}
        self.m_separations: typing.Dict[str,typing.Set[str]] = {}
        self.m_orderings: typing.Dict[str,typing.Set[str]] = {}
        self.m_general_relations: typing.Dict[str,typing.Tuple[typing.Tuple[str,...], typing.List[typing.Tuple[object,...]]]] = {}
        # general relations inefficient but good enough for now... B+Tree ???
        # linear arithmetic constraints ? for example for durations...
        # ANSWER : through general relation constraints (corresponding to formula) and fape-type linking between binding constraint net and temporal net
        self.m_old_domains: typing.Dict[str, Domain] = {}
        self.m_old_unifications: UnionFind2 = UnionFind2()
        self.m_old_disj_unifications: typing.Dict[str,typing.Set[str]] = {}
        self.m_old_separations: typing.Dict[str,typing.Set[str]] = {}
        self.m_old_orderings: typing.Dict[str,typing.Set[str]] = {}
        self.m_old_general_relations: typing.Dict[str,typing.Tuple[typing.Tuple[str,...], typing.List[typing.Tuple[object,...]]]] = {}

    def backup(self) -> None:

        self.m_old_domains = deepcopy(self.m_domains)
        self.m_old_unifications = deepcopy(self.m_unifications)
        self.m_old_disj_unifications = deepcopy(self.m_disj_unifications)
        self.m_old_separations = deepcopy(self.m_separations)
        self.m_old_orderings = deepcopy(self.m_orderings)
        self.m_old_general_relations = deepcopy(self.m_general_relations)

    def restore(self) -> None:

        self.m_domains = self.m_old_domains
        self.m_unifications = self.m_old_unifications
        self.m_disj_unifications = self.m_old_disj_unifications
        self.m_separations = self.m_old_separations
        self.m_old_orderings = self.m_old_orderings
        self.m_general_relations = self.m_old_general_relations

    def clear(self) -> None:

        self.m_domains = {}
        self.m_unifications = UnionFind2()
        self.m_disj_unifications = {}
        self.m_separations = {}
        self.m_orderings = {}
        self.m_general_relations = {}

        self.m_old_domains = {}
        self.m_old_unifications = UnionFind2()
        self.m_old_disj_unifications = {}
        self.m_old_separations = {}
        self.m_old_orderings = {}
        self.m_old_general_relations = {}

    # full lookahead (maintaining) arc consistency, based on ac3
    # quite an inefficient implementation because of the copying etc...
    # ideally - the domain objects should only contain pointers to values, not the values themselves
    # that way, we can get away with feeding this function with shallow copies - or maybe even find a better way than that - instead of deep copies
    # the implementation also has some temporary/caching shallow copies of lists/sets which ideally would have to be dealt with 
    # also the representation of table relations is (way too) naive - but is enough for now
    def _propagate(
        self,
        p_input_constrs:typing.List[typing.Tuple[ConstraintType,typing.Any]],
        p_stn:STN=None
    ) -> bool:

        # CLARIFICATIONS :
        #
        # input constraints are given in format (Type, Constraint)
        # the format for Constraint is :
        # for unary less(or equal) and greater(or equal) - (var1, value)
        # for unification - (var1, var2)
        # for disjunctive unification - (var1, [other_vars...])
        # for separation - (var1, var2) - nothing fancy
        # for general relations - (relation_name, ([param_vars...], [[vars_values...]...]))
        #
        # !!!!! INPUT (unification and separation) CONSTRAINTS MUST BE SYMMETRIC !!!!!
        # obviously, that can only be the case for 
        #
        #file:///home/nrealus/T%C3%A9l%C3%A9chargements/781f16-3.pdf

        worklist = p_input_constrs#list(p_input_constrs)
        while (len(worklist) > 0):

            (constr_type, constr) = worklist.pop(0)

            change_info = []
            var1 = None
            val = None
            var2 = None
            var2list = []

            if constr_type == ConstraintType.DOMAIN_VAL_LE or constr_type == ConstraintType.DOMAIN_VAL_GE:

                var1 = constr[0]
                val = constr[1]

                if constr_type == ConstraintType.DOMAIN_VAL_LE:
                    changed = self.m_domains[var1].restrict_to(ComparisonOp.LE, val)
                elif constr_type == ConstraintType.DOMAIN_VAL_GE:
                    changed = self.m_domains[var1].restrict_to(ComparisonOp.GE, val)

                if changed:
                    change_info.append((var1,val))

                if self.m_domains[var1].is_empty():
                    return False

            elif constr_type == ConstraintType.UNIFICATION:
                
                var1 = constr[0]
                var2 = constr[1]
                
                if ((var1 in self.m_separations and var2 in self.m_separations[var1])
                    or (var2 in self.m_separations and var1 in self.m_separations[var2])
                ):
                    return False

                self.m_unifications.add_and_union(var1, var2)
                
                changed = self.m_domains[var1].intersection(self.m_domains[var2])
                if changed:
                    change_info.append((var1,var2))

                if self.m_domains[var1].is_empty():
                    return False
            
            elif constr_type == ConstraintType.DISJ_UNIFICATION:
                
                var1 = constr[0]
                var2list = constr[1]

                self.m_disj_unifications.setdefault(var1,set()).update(var2list)

                _temp = deepcopy(self.m_domains[var2list[0]]) # deep copy so that the actual domain of var2list[0] doesn't get modified in the loop
                for i in range(1,len(var2list)): # start at 1 instead of 0 because first element already taken care of on the previous line
                    _temp.union(self.m_domains[var2list[i]])

                changed = self.m_domains[var1].intersection(_temp)
                if changed:
                    change_info.append((var1,var2list))

                if self.m_domains[var1].is_empty():
                    return False

            elif constr_type == ConstraintType.SEPARATION:
                
                var1 = constr[0]
                var2 = constr[1]

                if ((self.m_unifications.contains([var1])
                    and self.m_unifications.contains([var2])
                    and self.m_unifications.find(var1) == self.m_unifications.find(var2))
                        or (self.m_domains[var1].size() == 1 and self.m_domains[var1].get_values() == self.m_domains[var2].get_values())
                ):
                    return False

                self.m_separations.setdefault(var1,set()).add(var2)

                changed = self.m_domains[var1].difference_if_other_is_singleton(self.m_domains[var2])
                if changed:
                    change_info.append((var1,var2))
                
                if self.m_domains[var1].is_empty():
                    return False

            elif constr_type == ConstraintType.ORDER_LE or constr_type == ConstraintType.ORDER_GE:
                
                var1 = constr[0]
                var2 = constr[1]

                self.m_separations.setdefault(var1,set()).add(var2)

                changed = self.m_domains[var1].difference_if_other_is_singleton(self.m_domains[var2])
                if changed:
                    change_info.append((var1,var2))
                
                if self.m_domains[var1].is_empty():
                    return False

            elif constr_type == ConstraintType.GENERAL_RELATION:
                
                relation_name = constr[0]
                relation_param_vars = list(constr[1][0])
                relation_table = list(constr[1][1]) # copy (shallow) so that the input parameter doesn't get modified
                self.m_general_relations.setdefault(relation_name,(relation_param_vars,[]))[1].extend(relation_table)

                n_rows = len(self.m_general_relations[relation_name][1])
                for row in range(n_rows-1,-1,-1): # backwards loop, so no problem removing elements from list
                    for col in range(len(self.m_general_relations[relation_name][1][row])):
                        if not self.m_domains[relation_param_vars[col]].contains(self.m_general_relations[relation_name][1][row][col]):
                            self.m_general_relations[relation_name][1].pop(row)
                            break
                
                proj_doms:typing.Dict[str,Domain] = {}
                for col in range(len(relation_param_vars)):
                    var = relation_param_vars[col]
                    proj_doms[var] = Domain()
                    for row in range(len(self.m_general_relations[relation_name][1])):
                        proj_doms[var].add_discrete_value(self.m_general_relations[relation_name][1][row][col])

                for var in proj_doms:

                    changed = self.m_domains[var].intersection(proj_doms[var])
                    if changed:
                        change_info.append((var,relation_name))

                    if self.m_domains[var].is_empty():
                        return False

            while len(change_info) > 0:

                (var1, arg) = change_info.pop(0)
                val = None
                var2 = None
                var2list = []
                relname = None

                if constr_type == ConstraintType.DOMAIN_VAL_LE or constr_type == ConstraintType.DOMAIN_VAL_GE:
                    val = arg
                elif constr_type == ConstraintType.UNIFICATION or constr_type == ConstraintType.SEPARATION:
                    var2 = arg
                elif constr_type == ConstraintType.DISJ_UNIFICATION:
                    var2list = arg
                elif constr_type == ConstraintType.GENERAL_RELATION:
                    relname = arg

                if self.m_unifications.contains([var1]):
                    for v in self.m_unifications.connected_component(var1):
                        if v != var1 and v != var2:
                            worklist.append((ConstraintType.UNIFICATION,(v, var1)))
                            worklist.append((ConstraintType.UNIFICATION,(var1, v)))

                if var1 in self.m_disj_unifications:
                    worklist.append((ConstraintType.DISJ_UNIFICATION,(var1,list(self.m_disj_unifications[var1]))))
                for v in self.m_disj_unifications:
                    if v != var1 and var1 in self.m_disj_unifications[v]:
                        worklist.append((ConstraintType.DISJ_UNIFICATION,(v,list(self.m_disj_unifications[v]))))

                if var1 in self.m_separations:
                    for v in self.m_separations[var1]:
                        if v != var2: #and obviously v can't be having a separation with itself anyway
                            worklist.append((ConstraintType.SEPARATION,(v, var1)))
                            worklist.append((ConstraintType.SEPARATION,(var1, v)))

                for name in self.m_general_relations:
                    if name != relname and var1 in self.m_general_relations[name][0]:
                        worklist.append((ConstraintType.GENERAL_RELATION,(name, self.m_general_relations[name])))

                if p_stn != None:
                    if var1 in p_stn.m_constraints.values():
                        if not p_stn._propagate([],self):
                            return False
                        # "min(domain(var1))" is taken directly in the function, no need to make a new grounded constraint, just need to update the minimal network
                        # that's why there is no constraint specified, because it updates the minimal network using the minimal value of the corresponding variable
                        # in the future the implementation details of this may be changed, and "simplified" (to be careful) to grounded constraints

        return True

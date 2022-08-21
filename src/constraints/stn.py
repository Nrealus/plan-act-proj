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
from bcn import BCN

############################################

# 28 / 08 / 2022

# The simple temporal network is implemented here.
# Additional info is available in the notes for constraints.py,
# notably on the linkage in constraint propagation between the STN and BCN.

# Currently, propagation is done in a non-incremental way using a direct computation of
# the all-pairs shortest paths matrix using the Floyd-Warshall algorithm.
# In the future, a more subtle and efficient approach (Johnson's algorithm, Planken 2008 path consistency, others...)

# Extensions accounting for uncertainty, probability, and partial observability are kept for later.

# The linking with object variables (see constraints.py) is not complete yet, and must be slightly changed for easier support of "multivaluate duration" object variables.
# Moreover, this approach allows to support even more general duration constraints, such as t2 - t1 <= func(x1, ..., xn)
# where t1, t2 are timepoints (temporal variables) in this STN, xi are object variables, and func is a function.
# Indeed, we can use an object variable "delta" to constrain two timepoints in this STN
# and create a general relation constraint in the BCN binding delta to func(x1, ..., xn).
# |---------relation_delta_func------------|
# | x1 | x2 | ... | xn | delta             |
# | v1 | v2 | ... | vn | func(v1, ..., vn) |  (for example, v1+v2)
# (This table representation is discrete, but in the general case it can all be continuous.)
# (Although for that we'll have to find a way to represent continuous/functional relations in the BCN)

############################################

class STN():

    def __init__(self):
        self.m_controllability: typing.Dict[str, bool] = { "origin" : True }
        # bool indicates whether the variable is controllable or not. Zero time point controllable ? idk
        self.m_constraints: typing.Dict[typing.Tuple[str,str],str] = {} #typing.Set[(str,typing.Tuple(str))]] = {}
        # to deal with general temporal constraints of form t2 - t1 <= f(x1, ... , xn)
        # for now : only var
        # constraints of the form : t2 - t1 <= d (object variable) are interpreted as : t2 - t1 <= max{ v | v € dom(v) } : dom(v) = domain of v in binding constr net
        self.m_minimal_network: typing.Dict[typing.Tuple[str,str],float] = {}
        # ("dist_STN(t1,t2) is the minimal delay between t1 and t2, which is given in the minimal network")

        self.m_old_variables: typing.Dict[str, bool] = { "origin" : True }
        self.m_old_constraints: typing.Dict[typing.Tuple[str,str],str] = {} #typing.Set[(str,typing.Tuple(str))]] = {}
        self.m_old_minimal_network: typing.Dict[typing.Tuple[str,str],float] = {}

    def backup(self) -> None:

        self.m_controllability = deepcopy(self.m_old_variables)
        self.m_constraints = deepcopy(self.m_old_constraints)
        self.m_minimal_network = deepcopy(self.m_old_minimal_network)

    def restore(self) -> None:

        self.m_controllability = self.m_old_variables
        self.m_constraints = self.m_old_constraints
        self.m_minimal_network = self.m_old_minimal_network

    def clear(self) -> None:

        self.m_controllability: typing.Dict[str, bool] = { "origin" : True }
        self.m_constraints: typing.Dict[typing.Tuple[str,str],str] = {} #typing.Set[(str,typing.Tuple(str))]] = {}
        self.m_minimal_network: typing.Dict[typing.Tuple[str,str],float] = {}

        self.m_old_variables: typing.Dict[str, bool] = { "origin" : True }
        self.m_old_constraints: typing.Dict[typing.Tuple[str,str],str] = {} #typing.Set[(str,typing.Tuple(str))]] = {}
        self.m_old_minimal_network: typing.Dict[typing.Tuple[str,str],float] = {}

    def size(self) -> int:

        return len(self.m_controllability)

    def _propagate(
        self,
        p_input_constraints:typing.List[typing.Tuple[str,str,str]],
        p_bcn:BCN
    ) -> bool:

        worklist = p_input_constraints#list(p_input_constraints)
        for (t1, t2, var) in worklist:
            self.m_controllability.setdefault(t1,True)# will deal with controllability later
            self.m_controllability.setdefault(t2,True)# will deal with controllability later
            self.m_constraints[(t1,t2)] = var #.setdefault((t1,t2),set()).add(var)
            #if len(head_params) == 0: # t2 - t1 <= d where d is "just" a variable. if the tuple of params was not empty, head_name would be interpreted as the relation name "f" of f(x1,...xn), xi being the head_params, for t2 - t1 <= f(x1,...,xn)
            if (t2,t1) in self.m_constraints: # (t2,t1), not (t1,t2) !!!!!
                #for other_var in self.m_constraints[(t2,t1)]:
                other_var = self.m_constraints[(t2,t1)]
                if other_var != var:
                    if (not p_bcn._propagate([(
                        ConstraintType.DOMAIN_VAL_GE,
                        (other_var,-p_bcn.m_domains[var].max_value()))], self)
                    ):
                        return False

        res = self._apsp(p_bcn)

        for v in self.m_controllability:
            if res[(v,v)] < 0:
                return False

        self.m_minimal_network = res
        return True
        #return (variables, constraints, res)

    # consistency : if there is a < 0 sum path cycle ...? check that
    # floyd warshall all-pairs shortest path (O(n^3))
    def _apsp(self, p_bcn:BCN): # floyd warshall apprach
        
        res = dict(self.m_minimal_network)
        for q in self.m_controllability:
            for u in self.m_controllability:
                for v in self.m_controllability:
                    res[(u,v)] = min(
                        res.setdefault((u,v),self._eval((u,v), p_bcn)),
                        res.setdefault((u,q),self._eval((u,q), p_bcn)) + res.setdefault((q,v),self._eval((q,v), p_bcn)))
        return res

    def _eval(self, p_cstr:typing.Tuple[str,str], p_bcn:BCN):

        # !! look if there are domain constraints
        #                                           ....?
        if p_cstr in self.m_constraints:
            return p_bcn.m_domains[self.m_constraints[p_cstr]].max_value()
        else:
            return math.inf

    #def minimal_network_pc(self): # planken incremental apprach
    #    res: typing.Dict[str,typing.Set[(str,str)]] = {}
    #
    #    return res
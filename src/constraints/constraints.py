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
from bcn import BCN
from stn import STN

############################################

# 28 / 08 / 2022

# The main constraint network is implemented here.
# Its purpose is to store and aggregate constraints on temporal and object variables
# to allow the planning and acting system to make informed decisions during planning search, execution and monitoring
# using various queries (like "unified", "unifiable", "separated", "separable", or to check variables' possible legal values (domains)).

# To achieve this, we need to propagate constraints introduced by the planning search,
# which is done through local (incomplete) consistency checking,
# leaving out full consistency checking for the final planning search nodes,
# as that is more expensive (algorithmically). (See GNT 2016 4.4 (iirc))

# Constants are represented as object variables with a singleton domain.

# As such it wraps a "binding constraint network" (BCN) on object variables, and a "simple temporal network" (STN) on temporal variables (points).
# These networks are combined and need each other (references passed in constraint propagation) to support mixing temporal and object variables.
# In the STN, temporal constraints constrain (duh) temporal variables (time points) to happen within a bounded window relatively to each other.
# The lower and upper bound of this window correspond to object variables.
# Usually, values are used directly instead, but with a "constant" object variable this can be done as well.
# However, if these "duration bounds" object variables were not fixed constants but "actual variables",
# constraint propagation in one of the networks should trigger propagation in the other one.
# This can happen in the BCN after a change on their domain (due to the propagation of some other constraint),
# or in the STN after a new constraint on the same temporal variables is propagated.
# This is why there is a reference to the STN in the BCN constraint propagation function and vice-versa.

# For more details about the integration of object and temporal variables, see FAPE (Bit-Monnot, 2020).

# The implementation is, of course, not ideal and could be optimised.
# Some redesigns could be possible in the future as well.

############################################

class ConstraintType(Enum):
    UNIFICATION = 0
    DISJ_UNIFICATION = 1
    SEPARATION = 2
    GENERAL_RELATION = 3
    ORDER_LE = 4
    ORDER_GE = 5
    DOMAIN_VAL_LE = 6
    DOMAIN_VAL_GE = 7
    TEMPORAL = 8

class ConstraintNetwork():

    def __init__(self):
        self.m_bcn: BCN = BCN()
        self.m_stn: STN = STN()

        # general relations are the only ones which can have both temporal and object variables
        # in fact it's using them that we can link them together

    def declare_and_init_objvars(self, p_domains: typing.Dict[str, Domain]):

        self.m_bcn.m_unifications.make_set(p_domains.keys())
        self.m_bcn.m_domains = dict(p_domains)

    def objvar_domain(self, p_var:str) -> Domain:

        return self.m_bcn.m_domains[p_var]#.get_values()

    def objvars_unified(self, p_var1:str, p_var2:str) -> bool:

        # include check of symmetric orderings ? (v1 (<=) v2) and (v2 (<=) v1) <==> v1 (=) v2
        # that actually would be much easier to represent with a graph as a "traditional" adjancency list than a disjoint set (union-find)...
        if (self.m_bcn.m_unifications.contains([p_var1]) and self.m_bcn.m_unifications.contains([p_var2])
            and self.m_bcn.m_unifications.find(p_var1) == self.m_bcn.m_unifications.find(p_var2)
        ):
            return True
        if self.m_bcn.m_domains[p_var1].size() == 1:
            return self.m_bcn.m_domains[p_var1].get_values() == self.m_bcn.m_domains[p_var2].get_values()
        return False

    def objvars_unifiable(self, p_var1:str, p_var2:str) -> bool:

        if ((p_var1 in self.m_bcn.m_separations and p_var2 in self.m_bcn.m_separations[p_var1])
            or (p_var2 in self.m_bcn.m_separations and p_var1 in self.m_bcn.m_separations[p_var2])
        ):
            return False
        if not self.m_bcn.m_domains[p_var1].intersects(self.m_bcn.m_domains[p_var2]):
            return False
        if self.m_bcn.m_unifications.contains([p_var1]) and self.m_bcn.m_unifications.contains([p_var2]):
            cc1 = self.m_bcn.m_unifications.connected_component(p_var1)
            cc2 = self.m_bcn.m_unifications.connected_component(p_var2)
            for unif_var1 in cc1:
                for unif_var2 in cc2:
                # O(n*m) unfortunately, but that will be enough (for now...:p)
                    if unif_var1 in self.m_bcn.m_separations and unif_var2 in self.m_bcn.m_separations[unif_var1]:
                        return False
        return True

    def objvars_separable(self, p_var1:str, p_var2:str) -> bool:

        return not self.objvars_unified(p_var1, p_var2)

    def objvars_separated(self, p_var1:str, p_var2:str) -> bool:
        
        return not self.objvars_unifiable(p_var1, p_var2)

    # "mixed constraints" (involving both temporal and object variables) are dealt with using both constraints networks
    def propagate_constraints(
        self,
        p_input_constrs:typing.List[typing.Tuple[ConstraintType,typing.Any]],
        p_just_checking_no_propagation=False,
    ) -> bool:
        
        binding_constraints_worklist = []
        temporal_constraints_worklist = []
        
        _temp_bin_constrs:typing.Dict[typing.Tuple[str,str],typing.Set[ConstraintType]] = {}
        for (cstr_type, cstr) in p_input_constrs:
            if cstr_type == ConstraintType.TEMPORAL:
                temporal_constraints_worklist.append(cstr)
            else:
                if cstr_type == ConstraintType.UNIFICATION or cstr_type == ConstraintType.SEPARATION:
                    if not cstr in _temp_bin_constrs or not cstr_type in _temp_bin_constrs[cstr]:
                        _temp_bin_constrs[cstr] = set([cstr_type])
                        binding_constraints_worklist.append((cstr_type,(cstr[0],cstr[1])))
                        binding_constraints_worklist.append((cstr_type,(cstr[1],cstr[0])))
                    else:
                        warnings.warn("No need to feed symmetric binary constraints to this function... It takes care of it by itself.")
                else:
                    binding_constraints_worklist.append((cstr_type,cstr))
        
        self.m_bcn.backup()
        self.m_stn.backup()

        if (self.m_bcn._propagate(binding_constraints_worklist,self.m_stn)
            and self.m_stn._propagate(temporal_constraints_worklist,self.m_bcn)
        ):
            if p_just_checking_no_propagation:
                self.m_bcn.restore()
                self.m_stn.restore()
            return True

        self.m_bcn.restore()
        self.m_stn.restore()
        return False

############################################


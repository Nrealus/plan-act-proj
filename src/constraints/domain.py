from __future__ import annotations

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum

############################################

# NOTE: Domain, 22 / 08 / 2022

# This file contains the implementation for the general Domain type.
# Its purpose is to wrap the value domain of "object variables" appearing in constraints.

# As such, Domain objects are one of the base buildings blocks of the system and will probably be heavily used in most if its parts.
# They are already heavily used in the constraint networks. (see src.constraints)

# Currently, only discrete domains are supported.
# Moreover, they are implemented in a quite naive way, which could certainly be optimised. (trailing / double linked list representation)

# Discrete domains are good enough for now.
# Infinite (continuous) domains support would be very welcome.
# Maybe it will even become inevitable...

# A lot could be redesigned, especially if support for infinite domains is considered.
# As a matter of fact, using "get_values()" to return a set of values makes sense for discrete domains, but not really for infinite domains.
# Considering python is a dynamic language it could be easily achieved, but ideally the implementation should be rigorous and portable to other (strongly-typed) languages.

############################################

class DomainType(Enum):
    DISCRETE=0

class Domain():

    _UNKNOWN_VALUE_VAR = "_unknown_value_var" # special variable, which is not unifiable with any other, even itself
    _ANY_VALUE_VAR = "_any_value_var" # special variable, which is unifiable with everything, including itself

    def __init__(
        self,
        p_type:DomainType=DomainType.DISCRETE,
        p_initial_allowed_values:typing.Iterable=[]
    ):
        self.m_type:DomainType = p_type
        self._m_discrete_values:typing.Set = set(p_initial_allowed_values)

    def get_values(self):

        if self.m_type == DomainType.DISCRETE:
            return set(self._m_discrete_values)
        return NotImplemented

    def contains(self, value):
        
        return value in self.get_values()

    def is_empty(self):
        
        if self.m_type == DomainType.DISCRETE:
            return self.size() == 0
        return NotImplemented

    def size(self):
        
        if self.m_type == DomainType.DISCRETE:
            return len(self._m_discrete_values)
        return NotImplemented

    def intersects(self, other_domain:Domain):
        
        if self.m_type == DomainType.DISCRETE and other_domain.m_type == DomainType.DISCRETE:
            for v in self._m_discrete_values:
                if v in other_domain._m_discrete_values:
                    return True
            return False
        return NotImplemented

    def intersection(self, other_domain:Domain):
        
        if self.m_type == DomainType.DISCRETE and other_domain.m_type == DomainType.DISCRETE:
            res = False
            new_set = set()
            for v in self._m_discrete_values:
                if v in other_domain._m_discrete_values:
                    new_set.add(v)
                else:
                    res = True
            self._m_discrete_values = new_set
            return res
        return NotImplemented

    def union(self, other_domain:Domain):
        
        if self.m_type == DomainType.DISCRETE and other_domain.m_type == DomainType.DISCRETE:
            res = False
            for v in other_domain._m_discrete_values:
                if v not in self._m_discrete_values:
                    res = True
                self._m_discrete_values.add(v)
            return res
        return NotImplemented

    # adapted for the special case of separation constraints. general case : p.40 file:///home/nrealus/T%C3%A9l%C3%A9chargements/781f16-3.pdf
    #def arc_separation(self, other_domain:Domain):
    def difference_if_other_is_singleton(self, other_domain:Domain):
        
        # for the special case of separation
        if self.m_type == DomainType.DISCRETE and other_domain.m_type == DomainType.DISCRETE:
            res = False
            if other_domain.size() == 1:
                for v in other_domain.get_values(): # there is actually only 1 value, so only 1 iteration. iterating because it's a set - there is no indexing
                    for i_v1 in self.get_values():
                        if i_v1 == v:
                            res = True
                            break                
                if res == True:
                    self._m_discrete_values.remove(v)
            return res
        # below : general case (with != operator for separation : for other constraints only need to adapt the operator)
        #if self.m_type == DomainType.DISCRETE and other_domain.m_type == DomainType.DISCRETE:
        #    res = False
        #    _b = True
        #    _temp = list(self.get_values())
        #    for i_v1 in _temp:
        #        _b = True
        #        for i_v2 in other_domain.get_values():
        #            if i_v1 != i_v2:
        #                _b = False
        #                continue
        #        if _b:
        #            res = True
        #            self._m_discrete_values.remove(i_v1)
        #    return res
        return NotImplemented

    def restrict_to_ls(self, value, strict=False):
        
        if self.m_type == DomainType.DISCRETE:
            res = False
            new_set = set()
            for v in self._m_discrete_values:
                if (strict and v < value) or v <= value:
                    new_set.add(v)
                else:
                    res = True
            self._m_discrete_values = new_set
            return res
        return NotImplemented

    def restrict_to_gt(self, value, strict=False):
        
        if self.m_type == DomainType.DISCRETE:
            res = False
            new_set = set()
            for v in self._m_discrete_values:
                if (strict and v > value) or v >= value:
                    new_set.add(v)
                else:
                    res = True
            self._m_discrete_values = new_set
            return res
        return NotImplemented

    def add_discrete_value(self, value):
        
        self._m_discrete_values.add(value)
    
    def remove_discrete_value(self, value):
        
        self._m_discrete_values.discard(value)

    def min_value(self):
        
        if self.m_type == DomainType.DISCRETE:
            return min(self._m_discrete_values)
        return NotImplemented

    def max_value(self):
        
        if self.m_type == DomainType.DISCRETE:
            return max(self._m_discrete_values)
        return NotImplemented

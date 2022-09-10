from __future__ import annotations

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.utility.new_int_id import new_int_id
from src.constraints.constraints import ConstraintNetwork, ConstraintType

############################################

# NOTE: Base, 29 / 08 / 2022

# Lots of basic building blocks / primitives are implemented / defined here.

# Specifically Assertions, Actions and Methods (which are practically the same in terms of structure).

# "Temporal assertions" (Assertions for short) are the main building block of the approach to temporal planning used in the project.
# They can be described as temporally qualified fluents on state variables.
# There are usually two types of Assertions - Persistence and Transition (sometimes called Change) - but sometimes a third type is also considered (Assignment)
# Persistence assertions express the fact that a state variable is equal to a certain value for the whole duration of a temporal interval
# Transition assertions express the fact that a state variable has a certain value at the beginning of a temporal interval,
# and then at some point acquires (or transitions to) another value, which it holds until the interval's end.
# Assertions are used to describe temporal knowledge.
# They are composed of a head (state variable name and parameter names, as well as parameter values (i.e. variables)) and a temporal interval, i.e. a start and end time point variable

# Actions

# Methods

############################################

class AssertionType(Enum):
    PERSISTENCE=0
    TRANSITION=1

class Assertion(tuple):

    __slots__ = []
    def __new__(cls,
        p_type:AssertionType,
        p_sv_name:str,
        p_sv_params_keys:typing.Tuple[str,...],
        p_sv_params_values:typing.Tuple[str,...],
        p_sv_val:object,
        p_sv_val_sec:object=None,
        p_time_start:str="",
        p_time_end:str="",
    ):
        # create (supposed to be) unique timepoint variable names corresponding to the start and end of this assertion
        k = new_int_id()
        if p_time_start == "":
            ts = "__ts_asrt_{0}".format(str(k))
        else:
            ts = p_time_start
        if p_time_end == "":
            te = "__te_asrt_{0}".format(str(k))
        else:
            te = p_time_end
        return tuple.__new__(cls, (p_type, p_sv_name, p_sv_params_keys, p_sv_params_values, ts, te, p_sv_val, p_sv_val_sec))

    @property
    def type(self) -> AssertionType:
        return tuple.__getitem__(self, 0)

    @property
    def sv_name(self) -> str:
        return tuple.__getitem__(self, 1)

    @property
    def sv_params_keys(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 2)

    @property
    def sv_params_values(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 3)

    @property
    def time_start(self) -> str:
        return tuple.__getitem__(self, 4)

    @property
    def time_end(self) -> str:
        return tuple.__getitem__(self, 5)

    @property
    def sv_val(self) -> object:
        return tuple.__getitem__(self, 6)

    @property
    def sv_val_sec(self) -> object:
        return tuple.__getitem__(self, 7)

    def __getitem__(self, item):
        raise TypeError

    def has_same_head(self, p_other_assertion:Assertion) -> bool:
        
        return self.sv_name == p_other_assertion.sv_name and self.sv_params_keys == p_other_assertion.sv_params_keys
    
    def propagate_causal_support_by(self,
        p_test_supporter:Assertion,
        p_cn:ConstraintNetwork,
        p_backtrack=True,
    ) -> typing.Tuple[bool, int]:

        num_backtracks = 0
        # check if the assertions have the same head
        if self.has_same_head(p_test_supporter):
            constrs = []
            for i in range(len(p_test_supporter.sv_params_values)):
                constrs.append((ConstraintType.UNIFICATION, (p_test_supporter.sv_params_values[i], self.sv_params_values[i])))
            # check if parameters of the assertions are unified
            if p_cn.propagate_constraints(constrs):
                num_backtracks += 1
            else:
                return (False, 0)
        else:
            return (False, 0)
        # check if the end timepoint of the tested supporter and start timepoint of the tested supportee are unified
        # and if the values (variables, describing the values) of the assertion's sv are unified
        if (p_test_supporter.type == AssertionType.PERSISTENCE
            and p_cn.propagate_constraints([
                (ConstraintType.TEMPORAL,(p_test_supporter.time_end, self.time_start, 0, False)),
                (ConstraintType.TEMPORAL,(self.time_start, p_test_supporter.time_end, 0, False)),
                (ConstraintType.UNIFICATION,(p_test_supporter.sv_val, self.sv_val))])
            and p_cn.tempvars_unified(p_test_supporter.time_end, self.time_start)
        ):
            num_backtracks += 1
            if p_backtrack:
                for _ in range(num_backtracks):
                    p_cn.backtrack()
            return (True, num_backtracks)
        elif (p_test_supporter.type == AssertionType.TRANSITION
            and p_cn.propagate_constraints([
                (ConstraintType.TEMPORAL,(p_test_supporter.time_end, self.time_start, 0, False)),
                (ConstraintType.TEMPORAL,(self.time_start, p_test_supporter.time_end, 0, False)),
                (ConstraintType.UNIFICATION,(p_test_supporter.sv_val_sec, self.sv_val))])
            and p_cn.tempvars_unified(p_test_supporter.time_end, self.time_start)
        ):
            num_backtracks += 1
            if p_backtrack:
                for _ in range(num_backtracks):
                    p_cn.backtrack()
            return (True, num_backtracks)
        else:
            for _ in range(num_backtracks):
                p_cn.backtrack()
            return (False, 0)

    def check_conflict(self, p_other_assertion:Assertion, p_cn:ConstraintNetwork):
        """
        Determines whether this assertion is conflicting with the specified input assertion, based on the specified constraint network
        Used to determine (potential) conflicts in a chronicle (for search purposes)
        Arguments:
            p_asrt2
                Assertion to test against
            p_cn:
                Constraint network to test against
        Returns:
            True if this assertion is possibly conflitcing with the specified assertion (based on the specified constraint network)
            False otherwise
        Side effects:
            None
        """
        # an assertion can't be conflicting with itself
        if self == p_other_assertion:
            return False
        # check if the head of this assertion and the specified one is different
        elif self.has_same_head(p_other_assertion):
            for i in range(len(self.sv_params_values)):
                if not p_cn.objvars_unifiable(self.sv_params_values[i],p_other_assertion.sv_params_values[i]):
                    return False
        else:
        #    warnings.warn("shouldn't happen...!!!!")
            return False

        if self.type == AssertionType.PERSISTENCE and p_other_assertion.type == AssertionType.PERSISTENCE:

            if p_cn.objvars_separable(self.sv_val, p_other_assertion.sv_val):
                # if the assertions' temporal windows possibly intersect
                if (self.time_start == p_other_assertion.time_end
                    or p_other_assertion.time_start == self.time_end
                    or p_cn.tempvars_minimal_directed_distance(self.time_start,p_other_assertion.time_end)
                    * p_cn.tempvars_minimal_directed_distance(p_other_assertion.time_start,self.time_end) >= 0
                ):
                    return True
            return False

        elif self.type == AssertionType.TRANSITION and p_other_assertion.type == AssertionType.TRANSITION:

            # if the assertions' temporal windows possibly intersect
            if (self.time_start == p_other_assertion.time_end
                or p_other_assertion.time_start == self.time_end
                or p_cn.tempvars_minimal_directed_distance(self.time_start,p_other_assertion.time_end)
                * p_cn.tempvars_minimal_directed_distance(p_other_assertion.time_start,self.time_end) >= 0
            ):
                # if the transition statements have the same (unified) values and same start and end timepoints
                # or have the same (unified) values and are connected by the end of one another
                # then there's no conflict
                if ((p_cn.objvars_unified(self.sv_val, p_other_assertion.sv_val) and p_cn.objvars_unified(self.sv_val_sec, p_other_assertion.sv_val_sec)
                    and p_cn.tempvars_unified(self.time_start,p_other_assertion.time_start)
                    and p_cn.tempvars_unified(self.time_end,p_other_assertion.time_end))
                or (p_cn.objvars_unified(self.sv_val, p_other_assertion.sv_val_sec)
                    and p_cn.tempvars_unified(self.time_start,p_other_assertion.time_end))
                or (p_cn.objvars_unified(p_other_assertion.sv_val, self.sv_val_sec)
                    and p_cn.tempvars_unified(p_other_assertion.time_start,self.time_end))
                ):
                    return False
                else:
                    return True
            return False

        else:

            if self.type == AssertionType.PERSISTENCE:
                asrt_pers = self
                asrt_trans = p_other_assertion
            else:
                asrt_pers = p_other_assertion
                asrt_trans = self

            # if the assertions' temporal windows possibly intersect
            if (asrt_pers.time_start == asrt_trans.time_end
                or asrt_trans.time_start == asrt_pers.time_end
                or p_cn.tempvars_minimal_directed_distance(asrt_pers.time_start,asrt_trans.time_end)
                * p_cn.tempvars_minimal_directed_distance(asrt_trans.time_start,asrt_pers.time_end) >= 0
            ):
                # if have the same (unified) values and are connected by the end of one another
                # then there's no conflict
                if ((p_cn.objvars_unified(asrt_trans.sv_val_sec, asrt_pers.sv_val)
                    and p_cn.tempvars_unified(asrt_pers.time_start,asrt_trans.time_end))
                or (p_cn.objvars_unified(asrt_pers.sv_val, asrt_trans.sv_val)
                    and p_cn.tempvars_unified(asrt_trans.time_start,asrt_pers.time_end))
                ):
                    return False
                else:
                    return True
            return False

#class Timeline():
#    m_sv_name:str
#    m_assertions:typing.List[Assertion]

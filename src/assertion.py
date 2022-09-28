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

############################################

class AssertionType(Enum):
    PERSISTENCE=0
    TRANSITION=1

class Assertion():

    def __init__(self,
        p_type:AssertionType,
        p_sv_name:str,
        p_sv_params:typing.Tuple[typing.Tuple[str,str],...],
        p_sv_val:str,
        p_sv_val_sec:str=None,
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
        
        self._type = p_type
        self._sv_name = p_sv_name
        self._sv_params = p_sv_params
        self._time_start = ts
        self._time_end = te
        self._sv_val = p_sv_val
        self._sv_val_sec = p_sv_val_sec

    @property
    def type(self) -> AssertionType:
        return self._type

    @property
    def sv_name(self) -> str:
        return self._sv_name

    @property
    def sv_params(self) -> typing.Tuple[typing.Tuple[str,str],...]:
        return self._sv_params

    @property
    def time_start(self) -> str:
        return self._time_start

    @property
    def time_end(self) -> str:
        return self._time_end

    @property
    def sv_val(self) -> str:
        return self._sv_val

    @property
    def sv_val_sec(self) -> str:
        return self._sv_val_sec

    def has_same_head(self, p_other_assertion:Assertion) -> bool:
        '''
        Determines whether this assertion and the argument assertion have the same head
        (i.e. same name and same parameter names)
        Arguments:
            p_other_assertion (Assertion):
                Specified assertion to test against
        Returns:
            True if this assertion and the argument assertion have the same head
        '''
        if self.sv_name != p_other_assertion.sv_name:
            return False
        if len(self.sv_params) != len(p_other_assertion.sv_params):
            return False
        for _i in range(len(self.sv_params)):
            if self.sv_params[_i][0] != p_other_assertion.sv_params[_i][0]:
                return False
        return True
    
    def propagate_causal_support_by(self,
        p_test_supporter:Assertion,
        p_cn:ConstraintNetwork,
        p_revert_on_failure:bool,
        p_revert_on_success:bool,
    ) -> bool:
        '''
        Attempts to propagate the constraints necessary to enforce causal support of this assertion
        by the specified assertion in the specified constraint network.
        Used to determine whether this assertion can be causally supported by the specified assertion
        with the specified constraint network by propagating the constraints necessary to enforce causal support.
        If propagation is successful, then causal support with the specified arguments is indeed possible 
        and remains enforced if p_backtrack is False).
        Arguments:
            p_test_supporter (Assertion):
                Candidate supporter assertion to test
            p_cn (ConstraintNetwork):
                The constraint network where to propagate causal support constraints
            p_backtrack (bool, True by default):
                Whether to backtrack the changes propagated to the constraint network (in case it is successful).
                In other words, whether to keep the causal support enforced or simply check if it is possible.
        Returns:
            A tuple (bool, int) where the bool value describes whether the propagation was successful (i.e. whether causal support can be enforced)
            and where the int value describes the number of constraint batches that have been propagated. As such if the bool value is False, the int element is 0.            
            Moreover, the int element can be used to backtrack by hand later if the constraints remain enforced (i.e. p_backtrack is False)
        Side effects:
            Changes propagated to p_cn, in case p_backtrack is False.
        '''
        # check if the assertions have the same head
        if self.has_same_head(p_test_supporter):
            constrs = []
            for i in range(len(p_test_supporter.sv_params)):
                constrs.append((ConstraintType.UNIFICATION, (p_test_supporter.sv_params[i][1], self.sv_params[i][1])))
            # check if parameters of the assertions are unified
            p_cn.backup()
            if not p_cn.propagate_constraints(constrs, p_backup=False, p_revert_on_failure=True, p_revert_on_success=False):
                if p_revert_on_failure:
                    p_cn.backtrack()
                return False
        else:
            return False
        # check if the end timepoint of the tested supporter and start timepoint of the tested supportee are unified
        # and if the values (variables, describing the values) of the assertion's sv are unified
        if (p_test_supporter.type == AssertionType.PERSISTENCE
            and p_cn.propagate_constraints([
                (ConstraintType.TEMPORAL,(p_test_supporter.time_end, self.time_start, 0, False)),
                (ConstraintType.TEMPORAL,(self.time_start, p_test_supporter.time_end, 0, False)),
                (ConstraintType.UNIFICATION,(p_test_supporter.sv_val, self.sv_val))],
                p_backup=False, p_revert_on_failure=False, p_revert_on_success=False)
            and p_cn.tempvars_unified(p_test_supporter.time_end, self.time_start)
        ):
            if p_revert_on_success:
                p_cn.backtrack()
            return True
        elif (p_test_supporter.type == AssertionType.TRANSITION
            and p_cn.propagate_constraints([
                (ConstraintType.TEMPORAL,(p_test_supporter.time_end, self.time_start, 0, False)),
                (ConstraintType.TEMPORAL,(self.time_start, p_test_supporter.time_end, 0, False)),
                (ConstraintType.UNIFICATION,(p_test_supporter.sv_val_sec, self.sv_val))],
                p_backup=False, p_revert_on_failure=False, p_revert_on_success=False)
            and p_cn.tempvars_unified(p_test_supporter.time_end, self.time_start)
        ):
            if p_revert_on_success:
                p_cn.backtrack()
            return True
        else:
            if p_revert_on_failure:
                p_cn.backtrack()
            return False

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
            for i in range(len(self.sv_params)):
                if not p_cn.objvars_unifiable(self.sv_params[i][1],p_other_assertion.sv_params[i][1]):
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

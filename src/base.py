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
# There are usually two types of Assertions (Persistence, Transition) but sometimes a third type is also considered (Assignment)
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
    TRANSITION=1 # or change
    #ASSIGNMENT=2
        # "assignment" statements left out.
        # previous notes : 
            # deal with equal start and end times for transition statements
            # (which are like "conditional" assignments, if "previous" value is not "any")
            # without converting to persistence statements.
            # ad-hoc approach required to try 
            # use the open / closed intervals (even with equal start and end) for something ?
            # only use semi open intervals ? instead of fully open
            # (alternative transition subdivision ? [[+[[+[]) special treatment for [[ when same time point ?
     #NEG_PERSISTENCE=3


# actually assertion *template*
class Assertion(tuple):

    __slots__ = []
    def __new__(cls,
        p_type:AssertionType,
        p_sv_name:str,
        p_sv_params_names:typing.Tuple[str,...],
        p_sv_params_vars:typing.Tuple[str,...],
        p_sv_val:object,
        p_sv_val_sec:object=None):

        k = new_int_id()
        ts = "_ts_asrt_{0}".format(str(k))
        te = "_te_asrt_{0}".format(str(k))
        return tuple.__new__(cls, (p_type, p_sv_name, p_sv_params_names, p_sv_params_vars, ts, te, p_sv_val, p_sv_val_sec))

    @property
    def type(self) -> AssertionType:
        return tuple.__getitem__(self, 0)

    @property
    def sv_name(self) -> str:
        return tuple.__getitem__(self, 1)

    @property
    def sv_params_names(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 2)

    @property
    def sv_params_vars(self) -> typing.Tuple[str,...]:
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

    def is_causally_supported_by(self, p_other_assertion:Assertion, p_cn:ConstraintNetwork) -> bool:

        if (self.sv_name == p_other_assertion.sv_name and self.sv_params_names == p_other_assertion.sv_params_names):
            for i in range(len(self.sv_params_vars)):
                if p_cn.objvars_separable(self.sv_params_vars[i],p_other_assertion.sv_params_vars[i]):
                    return False
        else:
            return False
        if (self.time_start == p_other_assertion.time_end
            or (p_cn.m_stn.m_minimal_network[(self.time_start, p_other_assertion.time_end)] == 0
                and p_cn.m_stn.m_minimal_network[(p_other_assertion.time_end, self.time_start)] == 0)
        ):
            if ((p_other_assertion.type == AssertionType.PERSISTENCE and p_cn.objvars_unified(p_other_assertion.sv_val, self.sv_val))
                or (p_other_assertion.type == AssertionType.TRANSITION and p_cn.objvars_unified(p_other_assertion.sv_val_sec, self.sv_val))
            ):
                return True
        return False

    def check_conflict(self, p_asrt2:Assertion, p_cn:ConstraintNetwork):

        if self == p_asrt2:
            return False
        elif self.sv_name == p_asrt2.sv_name and self.sv_params_names == p_asrt2.sv_params_names:
            b = True
            for i in range(len(self.sv_params_vars)):
                if not p_cn.objvars_unifiable(self.sv_params_vars[i],p_asrt2.sv_params_vars[i]):
                    return False
        #else:
        #    warnings.warn("shouldn't happen...!!!!")

        if self.type == AssertionType.PERSISTENCE and p_asrt2.type == AssertionType.PERSISTENCE:

            if b and p_cn.objvars_separable(self.sv_val, p_asrt2.sv_val):
                #if (p_cn.propagate_constraints([
                #    (ConstraintType.TEMPORAL,(self.m_time_start,p_asrt2.m_time_end,0,False)),
                #    (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,self.m_time_end,0,False)),
                #    ],p_just_checking_no_propagation=True) 
                #):
                if (p_cn.m_stn.m_minimal_network[(self.time_start,p_asrt2.time_end)]
                    * p_cn.m_stn.m_minimal_network[(p_asrt2.time_start,self.time_end)] >= 0
                ):
                    return True
            return False

        elif self.type == AssertionType.TRANSITION and p_asrt2.type == AssertionType.TRANSITION:

            if b:
                #if (p_cn.propagate_constraints([
                #    (ConstraintType.TEMPORAL,(self.m_time_start,p_asrt2.m_time_end,0,False)),
                #    (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,self.m_time_end,0,False)),
                #    ],p_just_checking_no_propagation=True) 
                #):
                if (p_cn.m_stn.m_minimal_network[(self.time_start,p_asrt2.time_end)]
                    * p_cn.m_stn.m_minimal_network[(p_asrt2.time_start,self.time_end)] >= 0
                ):
                    #if ((p_cn.objvars_unified(self.m_sv_val, p_asrt2.m_sv_val) and p_cn.objvars_unified(self.m_sv_val_sec, p_asrt2.m_sv_val_sec)
                    #    and (p_cn.propagate_constraints([
                    #        (ConstraintType.TEMPORAL,(self.m_time_start,p_asrt2.m_time_start,0, False)),
                    #        (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,self.m_time_start,0, False)),
                    #        (ConstraintType.TEMPORAL,(self.m_time_end,p_asrt2.m_time_end,0, False)),
                    #        (ConstraintType.TEMPORAL,(p_asrt2.m_time_end,self.m_time_end,0, False)),
                    #        ],p_just_checking_no_propagation=True)))
                    #or (p_cn.objvars_unified(self.m_sv_val, p_asrt2.m_sv_val_sec)
                    #    and p_cn.propagate_constraints([
                    #        (ConstraintType.TEMPORAL,(self.m_time_start,p_asrt2.m_time_end,0, False)),
                    #        (ConstraintType.TEMPORAL,(p_asrt2.m_time_end,self.m_time_start,0, False)),
                    #        ],p_just_checking_no_propagation=True))
                    #or (p_cn.objvars_unified(p_asrt2.m_sv_val, self.m_sv_val_sec)
                    #    and p_cn.propagate_constraints([
                    #        (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,self.m_time_end,0, False)),
                    #        (ConstraintType.TEMPORAL,(self.m_time_end,p_asrt2.m_time_start,0, False)),
                    #        ],p_just_checking_no_propagation=True))
                    #):
                    if ((p_cn.objvars_unified(self.sv_val, p_asrt2.sv_val) and p_cn.objvars_unified(self.sv_val_sec, p_asrt2.sv_val_sec)
                        and p_cn.m_stn.m_minimal_network[(self.time_start,p_asrt2.time_start)] == 0
                        and p_cn.m_stn.m_minimal_network[(p_asrt2.time_start,self.time_start)] == 0
                        and p_cn.m_stn.m_minimal_network[(self.time_end,p_asrt2.time_end)] == 0
                        and p_cn.m_stn.m_minimal_network[(p_asrt2.time_end,self.time_end)] == 0)
                    or (p_cn.objvars_unified(self.sv_val, p_asrt2.sv_val_sec)
                        and p_cn.m_stn.m_minimal_network[(self.time_start,p_asrt2.time_end)] == 0
                        and p_cn.m_stn.m_minimal_network[(p_asrt2.time_end,self.time_start)] == 0)
                    or (p_cn.objvars_unified(p_asrt2.sv_val, self.sv_val_sec)
                        and p_cn.m_stn.m_minimal_network[(p_asrt2.time_start,self.time_end)] == 0
                        and p_cn.m_stn.m_minimal_network[(self.time_end,p_asrt2.time_start)] == 0)
                    ):
                        return False
                    else:
                        return True
            return False

        else:

            if self.type == AssertionType.PERSISTENCE:
                asrt_pers = self
                asrt_trans = p_asrt2
            else:
                asrt_pers = p_asrt2
                asrt_trans = self

            if b:
                #if (p_cn.propagate_constraints([
                #    (ConstraintType.TEMPORAL,(asrt_pers.m_time_start,asrt_trans.m_time_end,0,False)),
                #    (ConstraintType.TEMPORAL,(asrt_trans.m_time_start,asrt_pers.m_time_end,0,False)),
                #    ],p_just_checking_no_propagation=True) 
                #):
                if (p_cn.m_stn.m_minimal_network[(asrt_pers.time_start,asrt_trans.time_end)]
                    * p_cn.m_stn.m_minimal_network[(asrt_trans.time_start,asrt_pers.time_end)] >= 0
                ):
                    #if ((p_cn.objvars_unified(asrt_trans.m_sv_val_sec, asrt_pers.m_sv_val)
                    #    and p_cn.propagate_constraints([
                    #        (ConstraintType.TEMPORAL,(asrt_pers.m_time_start,asrt_trans.m_time_end,0, False)),
                    #        (ConstraintType.TEMPORAL,(asrt_trans.m_time_end,asrt_pers.m_time_start,0, False)),
                    #        ],p_just_checking_no_propagation=True))
                    #or (p_cn.objvars_unified(asrt_pers.m_sv_val, asrt_trans.m_sv_val)
                    #    and p_cn.propagate_constraints([
                    #        (ConstraintType.TEMPORAL,(asrt_trans.m_time_start,asrt_pers.m_time_end,0, False)),
                    #        (ConstraintType.TEMPORAL,(asrt_pers.m_time_end,asrt_trans.m_time_start,0, False)),
                    #        ],p_just_checking_no_propagation=True))
                    #):
                    if ((p_cn.objvars_unified(asrt_trans.sv_val_sec, asrt_pers.sv_val)
                        and p_cn.m_stn.m_minimal_network[(asrt_pers.time_start,asrt_trans.time_end)] == 0
                        and p_cn.m_stn.m_minimal_network[(asrt_trans.time_end,asrt_pers.time_start)] == 0)
                    or (p_cn.objvars_unified(asrt_pers.sv_val, asrt_trans.sv_val)
                        and p_cn.m_stn.m_minimal_network[(asrt_trans.time_start,asrt_pers.time_end)] == 0
                        and p_cn.m_stn.m_minimal_network[(asrt_pers.time_end,asrt_trans.time_start)] == 0)
                    ):
                        return False
                    else:
                        return True
            return False

#class Timeline():
#    m_sv_name:str
#    m_assertions:typing.List[Assertion]

# actually action *template*
class Action():

    __slots__ = []
    def __new__(cls,
    p_action_name:str,
    p_action_params_names:typing.Tuple[str,...],
    p_action_params_vars:typing.Tuple[str,...],
    p_assertions:typing.Set[Assertion]=set(),
    p_constraints:typing.Set[typing.Tuple[ConstraintType,typing.Any]]=set()):

        k = new_int_id()
        ts = "_ts_act_{0}".format(str(k))
        te = "_te_act_{0}".format(str(k))
        return tuple.__new__(cls, (p_action_name, p_action_params_names, p_action_params_vars, ts, te, p_assertions, p_constraints))

    @property
    def action_name(self) -> str:
        return tuple.__getitem__(self, 0)

    @property
    def action_params_names(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 1)

    @property
    def action_params_vars(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 2)

    @property
    def time_start(self) -> str:
        return tuple.__getitem__(self, 3)

    @property
    def time_end(self) -> str:
        return tuple.__getitem__(self, 4)

    @property
    def assertions(self) -> typing.Set[Assertion]:
        return tuple.__getitem__(self, 5)
    # (unsupported assertions) (Nau 2020 : "no supported assertions = if you insert an action into a chronicle, you need to figure out how to support it")
    # reminds of HGN(?) ActorSim(?) and Bit-Monnot 2020 (hierarchronicles - "method chronicles with subtasks and no effects" and "action chronicles with effects and no subtasks")

    @property
    def constraints(self) -> typing.Set[typing.Tuple[ConstraintType,typing.Any]]:
        return tuple.__getitem__(self, 6)

    def __getitem__(self, item):
        raise TypeError

class Method():

    __slots__ = []
    def __new__(cls,
    p_method_name:str,
    p_method_params_names:typing.Tuple[str,...],
    p_method_params_vars:typing.Tuple[str,...],
    p_assertions:typing.Set[Assertion]=set(),
    p_constraints:typing.Set[typing.Tuple[ConstraintType,typing.Any]]=set()):

        k = new_int_id()
        ts = "_ts_meth_{0}".format(str(k))
        te = "_te_meth_{0}".format(str(k))
        return tuple.__new__(cls, (p_method_name, p_method_params_names, p_method_params_vars, ts, te, p_assertions, p_constraints))

    @property
    def method_name(self) -> str:
        return tuple.__getitem__(self, 0)

    @property
    def method_params_names(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 1)

    @property
    def method_params_vars(self) -> typing.Tuple[str,...]:
        return tuple.__getitem__(self, 2)

    @property
    def time_start(self) -> str:
        return tuple.__getitem__(self, 3)

    @property
    def time_end(self) -> str:
        return tuple.__getitem__(self, 4)

    @property
    def assertions(self) -> typing.Set[Assertion]:
        return tuple.__getitem__(self, 5)
    # actually subgoals ; Nau 2020: "can't make a change happen, can only create subgoals"
    
    @property
    def constraints(self) -> typing.Set[typing.Tuple[ConstraintType,typing.Any]]:
        return tuple.__getitem__(self, 6)

    def __getitem__(self, item):
        raise TypeError
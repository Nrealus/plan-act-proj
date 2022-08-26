from __future__ import annotations
from ast import Assert

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.constraints.constraints import ConstraintNetwork, ConstraintType

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
class Assertion(typing.NamedTuple):

    m_type:AssertionType
    
    # name + params : "head"
    m_sv_name:str
    m_sv_params_names:typing.Tuple[str,...]
    m_sv_params_vars:typing.Tuple[str,...] # to ground : set a variable with a singleton domain;
    
    #m_sv_value_type:type     # for "state relations" as in Roberts 2021 - the value type is bool (and the value is implicitly always True ...?)

    # two value fields are given to deal with transition assertions. for non transition assertions - m_sv_val2 is None
    # these fields actually refer to variables (hence the "str" type) which describe the possible values. to ground them, set to a "constant variable" i.e. a variable with a singleton domain
    m_sv_val:str     # "main" value field   
    m_sv_val_sec:str # "secondary" value field (used for transitions)

    # maybe use a tuple, and if assertion type is transition, assume that the tuple has 2 elements ?
    # maybe good for python, but unsure about anything else. keep as is for now.

    m_time_start:str
    #m_time_start_interval_open:bool # should be always false except for "unknown" value persistence assertions decomposed from transition assertions
    m_time_end:str
    #m_time_end_interval_open:bool # idem

    def is_causally_supported_by(self, p_other_assertion:Assertion, p_cn:ConstraintNetwork) -> bool:

        if (self.m_sv_name == p_other_assertion.m_sv_name and self.m_sv_params_names == p_other_assertion.m_sv_params_names):
            for i in range(len(self.m_sv_params_vars)):
                if p_cn.objvars_separated(self.m_sv_params_vars[i],p_other_assertion.m_sv_params_vars[i]):
                    return False
        else:
            return False

        if (p_other_assertion.m_type == AssertionType.PERSISTENCE
            and p_cn.propagate_constraints([
                (ConstraintType.TEMPORAL,(self.m_time_start,p_other_assertion.m_time_end,0,False)),
                (ConstraintType.TEMPORAL,(p_other_assertion.m_time_end,self.m_time_start,0,False)),
                (ConstraintType.UNIFICATION), (p_other_assertion.m_sv_val, self.m_sv_val)
                ],p_just_checking_no_propagation=True)
        ):
            return True
        elif (p_other_assertion.m_type == AssertionType.TRANSITION
            and p_cn.propagate_constraints([
                (ConstraintType.TEMPORAL,(self.m_time_start,p_other_assertion.m_time_end,0,False)),
                (ConstraintType.TEMPORAL,(p_other_assertion.m_time_end,self.m_time_start,0,False)),
                (ConstraintType.UNIFICATION), (p_other_assertion.m_sv_val_sec, self.m_sv_val)
                ],p_just_checking_no_propagation=True)
        ):
            return True

        return False

    def check_conflict(self, p_asrt2:Assertion, p_cn:ConstraintNetwork):

        if self == p_asrt2:
            return False
        elif self.m_sv_name == p_asrt2.m_sv_name and self.m_sv_params_names == p_asrt2.m_sv_params_names:
            b = True
            for i in range(len(self.m_sv_params_vars)):
                if not p_cn.objvars_unifiable(self.m_sv_params_vars[i],p_asrt2.m_sv_params_vars[i]):
                    return False

        if self.m_type == AssertionType.PERSISTENCE and p_asrt2.m_type == AssertionType.PERSISTENCE:

            if b and p_cn.objvars_separable(self.m_sv_val, p_asrt2.m_sv_val):
                if (p_cn.propagate_constraints([
                    (ConstraintType.TEMPORAL,(self.m_time_start,p_asrt2.m_time_end,0,False)),
                    (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,self.m_time_end,0,False)),
                    ],p_just_checking_no_propagation=True) 
                ):
                    return True
            return False

        elif self.m_type == AssertionType.TRANSITION and p_asrt2.m_type == AssertionType.TRANSITION:

            if b:
                if (p_cn.propagate_constraints([
                    (ConstraintType.TEMPORAL,(self.m_time_start,p_asrt2.m_time_end,0,False)),
                    (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,self.m_time_end,0,False)),
                    ],p_just_checking_no_propagation=True) 
                ):
                    if ((p_cn.objvars_unified(self.m_sv_val, p_asrt2.m_sv_val) and p_cn.objvars_unified(self.m_sv_val_sec, p_asrt2.m_sv_val_sec)
                        and (p_cn.propagate_constraints([
                            (ConstraintType.TEMPORAL,(self.m_time_start,p_asrt2.m_time_start,0, False)),
                            (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,self.m_time_start,0, False)),
                            (ConstraintType.TEMPORAL,(self.m_time_end,p_asrt2.m_time_end,0, False)),
                            (ConstraintType.TEMPORAL,(p_asrt2.m_time_end,self.m_time_end,0, False)),
                            ],p_just_checking_no_propagation=True)))
                    or (p_cn.objvars_unified(self.m_sv_val, p_asrt2.m_sv_val_sec)
                        and p_cn.propagate_constraints([
                            (ConstraintType.TEMPORAL,(self.m_time_start,p_asrt2.m_time_end,0, False)),
                            (ConstraintType.TEMPORAL,(p_asrt2.m_time_end,self.m_time_start,0, False)),
                            ],p_just_checking_no_propagation=True))
                    or (p_cn.objvars_unified(p_asrt2.m_sv_val, self.m_sv_val_sec)
                        and p_cn.propagate_constraints([
                            (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,self.m_time_end,0, False)),
                            (ConstraintType.TEMPORAL,(self.m_time_end,p_asrt2.m_time_start,0, False)),
                            ],p_just_checking_no_propagation=True))
                    ):
                        return False
                    else:
                        return True
            return False

        else:

            if self.m_type == AssertionType.PERSISTENCE:
                asrt_pers = self
                asrt_trans = p_asrt2
            else:
                asrt_pers = p_asrt2
                asrt_trans = self

            if b:
                if (p_cn.propagate_constraints([
                    (ConstraintType.TEMPORAL,(asrt_pers.m_time_start,asrt_trans.m_time_end,0,False)),
                    (ConstraintType.TEMPORAL,(asrt_trans.m_time_start,asrt_pers.m_time_end,0,False)),
                    ],p_just_checking_no_propagation=True) 
                ):
                    if ((p_cn.objvars_unified(asrt_trans.m_sv_val_sec, asrt_pers.m_sv_val)
                        and p_cn.propagate_constraints([
                            (ConstraintType.TEMPORAL,(asrt_pers.m_time_start,asrt_trans.m_time_end,0, False)),
                            (ConstraintType.TEMPORAL,(asrt_trans.m_time_end,asrt_pers.m_time_start,0, False)),
                            ],p_just_checking_no_propagation=True))
                    or (p_cn.objvars_unified(asrt_pers.m_sv_val, asrt_trans.m_sv_val)
                        and p_cn.propagate_constraints([
                            (ConstraintType.TEMPORAL,(asrt_trans.m_time_start,asrt_pers.m_time_end,0, False)),
                            (ConstraintType.TEMPORAL,(asrt_pers.m_time_end,asrt_trans.m_time_start,0, False)),
                            ],p_just_checking_no_propagation=True))
                    ):
                        return False
                    else:
                        return True
            return False

#class Timeline(typing.NamedTuple):
#    m_sv_name:str
#    m_assertions:typing.List[Assertion]

# actually action *template*
class Action(typing.NamedTuple):

    m_action_name:str
    m_action_params_names:typing.Tuple[str,...]
    m_action_params_vars:typing.Tuple[str,...]

    m_time_start:str
    m_time_end:str

    m_assertions:typing.Set[Assertion] = set()
    # (unsupported assertions) (Nau 2020 : "no supported assertions = if you insert an action into a chronicle, you need to figure out how to support it")
    # reminds of HGN(?) ActorSim(?) and Bit-Monnot 2020 (hierarchronicles - "method chronicles with subtasks and no effects" and "action chronicles with effects and no subtasks")
    m_constraints:typing.Set[typing.Tuple[ConstraintType,typing.Any]] = set()


# actually method *template*
class Method(typing.NamedTuple):

    m_method_name:str
    m_method_params_names:typing.Tuple[str,...]
    m_method_params_vars:typing.Tuple[str,...]
    
    m_time_start:str
    m_time_end:str

    m_assertions:typing.Set[Assertion] = set() # actually subgoals ; Nau 2020: "can't make a change happen, can only create subgoals"
    m_constraints:typing.Set[typing.Tuple[ConstraintType,typing.Any]] = set()

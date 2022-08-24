from __future__ import annotations
from ast import Assert

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.constraints.constraints import ConstraintNetwork, ConstraintType
from src.constraints.domain import Domain

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
    m_sv_params_vars:typing.Tuple[str,...] # to ground : set a variale with a singleton domain;

    m_time_start:str
    #m_time_start_interval_open:bool # should be always false except for "unknown" value persistence assertions decomposed from transition assertions
    m_time_end:str
    #m_time_end_interval_open:bool # idem
    
    #m_sv_value_type:type     # for "state relations" as in Roberts 2021 - the value type is bool (and the value is implicitly always True ...?)

    # two value fields are given to deal with transition assertions. for non transition assertions - m_sv_val2 is None
    # these fields actually refer to variables (hence the "str" type) which describe the possible values. to ground them, set to a "constant variable" i.e. a variable with a singleton domain
    m_sv_val:str     # "main" value field   
    m_sv_val_sec:str # "secondary" value field (used for transitions)

    # maybe use a tuple, and if assertion type is transition, assume that the tuple has 2 elements ?
    # maybe good for python, but unsure about anything else. keep as is for now.


#class Timeline(typing.NamedTuple):
#    m_sv_name:str
#    m_assertions:typing.List[Assertion]


class ChronicleTransformation(Enum):
    #"refinement transformation ?" no sense since we don't do tasks (yet) ? and goal refinements / methods add subgoals, which are assertions, which are already taken care of
    ADD_PERSISTENCE_ASSERTION = 0
    ADD_TRANSITION_ASSERTION = 1
    ADD_CONSTRAINT = 2
    ADD_ACTION = 3
## useless ?

# experiments on unification with goal nodes of goal memory ?
class Chronicle():

    def __init__(self):
        #self.m_variables:typing.Set[str] = set()
        self.m_goal = None
        # in bit-monnot 2022 there are also subtasks. adapting to subgoals seems weird, as subgoals can (are) already specified in unsupported assertions
        self.m_unsupported_assertions:typing.List[Assertion] = []
        self.m_supported_assertions:typing.List[Assertion] = []
        # "subdivide" even further ? (un)supported conditions/effects (separately)
        self.m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]] = []
        #self.m_actions = [] - in GNT 2016 (book) - "a set A of temporally qualified primitives and tasks"...

        self.m_causal_links:typing.Dict[Assertion,typing.Set[Assertion]] = {} # other way to store supported assertions...? (how to do with those that are "a priori" supported?)
    
    def clear(self):
        self.m_goal = None
        self.m_unsupported_assertions = []
        self.m_supported_assertions = []
        self.m_constraints = []
        self.m_causal_links = {}

    # checking possible conflicts should be done incrementally with every transformation of the chronicle
    # assuming the new assertions and constraints are consistent with each other - checking conflicts with "old" assertions and constraints
    # as for conflicts in new assertions and constraints, assume that they are formed/built as to be consistent with each other
    # OR will have to deal with them anyway, either here (in this method or a similar one) or somewhere else
    def get_resulting_conflicts(self, p_new_assertions:typing.Iterable[Assertion], p_cn:ConstraintNetwork):

        def persistences_conflict(p_asrt1:Assertion, p_asrt2:Assertion):
            if p_asrt1 == p_asrt2:
                return False
            elif p_asrt1.m_sv_name == p_asrt2.m_sv_name and p_asrt1.m_sv_params_names == p_asrt2.m_sv_params_names:
                #eq_constrs_on_sv_params:typing.List[typing.Tuple[ConstraintType,typing.Any]] = []
                #for i in range(len(p_asrt1.m_sv_params_vars)):
                #    eq_constrs_on_sv_params.append((ConstraintType.UNIFICATION,(p_asrt1.m_sv_params_vars[i],p_asrt2.m_sv_params_vars[i])))
                #if (p_cn.propagate_constraints_partial(eq_constrs_on_sv_params,p_just_checking_no_propagation=True) 
                #    and p_cn.objvars_separable(p_asrt1.m_sv_val, p_asrt2.m_sv_val)
                #):
                # is it equivalent to check if the param state vars are unifiable ?
                b = True
                for i in range(len(p_asrt1.m_sv_params_vars)):
                    if p_cn.objvars_separated(p_asrt1.m_sv_params_vars[i],p_asrt2.m_sv_params_vars[i]):
                        b = False
                        break
                if b and p_cn.objvars_separable(p_asrt1.m_sv_val, p_asrt2.m_sv_val):
                    if (p_cn.propagate_constraints([
                        (ConstraintType.TEMPORAL,(p_asrt1.m_time_start,p_asrt2.m_time_end,0,False)),
                        (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,p_asrt1.m_time_end,0,False)),
                        ],p_just_checking_no_propagation=True) 
                    ):
                        return True
            return False

        def transitions_conflict(p_asrt1:Assertion, p_asrt2:Assertion):
            if p_asrt1 == p_asrt2:
                return False
            elif p_asrt1.m_sv_name == p_asrt2.m_sv_name and p_asrt1.m_sv_params_names == p_asrt2.m_sv_params_names:
                b = True
                for i in range(len(p_asrt1.m_sv_params_vars)):
                    if not p_cn.objvars_unifiable(p_asrt1.m_sv_params_vars[i],p_asrt2.m_sv_params_vars[i]):
                        b = False
                        break
                if b:
                    if (p_cn.propagate_constraints([
                        (ConstraintType.TEMPORAL,(p_asrt1.m_time_start,p_asrt2.m_time_end,0,False)),
                        (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,p_asrt1.m_time_end,0,False)),
                        ],p_just_checking_no_propagation=True) 
                    ):
                        if ((p_cn.objvars_unified(p_asrt1.m_sv_val, p_asrt2.m_sv_val) and p_cn.objvars_unified(p_asrt1.m_sv_val_sec, p_asrt2.m_sv_val_sec)
                            and (p_cn.propagate_constraints([
                                (ConstraintType.TEMPORAL,(p_asrt1.m_time_start,p_asrt2.m_time_start,0, False)),
                                (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,p_asrt1.m_time_start,0, False)),
                                (ConstraintType.TEMPORAL,(p_asrt1.m_time_end,p_asrt2.m_time_end,0, False)),
                                (ConstraintType.TEMPORAL,(p_asrt2.m_time_end,p_asrt1.m_time_end,0, False)),
                                ],p_just_checking_no_propagation=True)))
                        or (p_cn.objvars_unified(p_asrt1.m_sv_val, p_asrt2.m_sv_val_sec)
                            and p_cn.propagate_constraints([
                                (ConstraintType.TEMPORAL,(p_asrt1.m_time_start,p_asrt2.m_time_end,0, False)),
                                (ConstraintType.TEMPORAL,(p_asrt2.m_time_end,p_asrt1.m_time_start,0, False)),
                                ],p_just_checking_no_propagation=True))
                        or (p_cn.objvars_unified(p_asrt2.m_sv_val, p_asrt1.m_sv_val_sec)
                            and p_cn.propagate_constraints([
                                (ConstraintType.TEMPORAL,(p_asrt2.m_time_start,p_asrt1.m_time_end,0, False)),
                                (ConstraintType.TEMPORAL,(p_asrt1.m_time_end,p_asrt2.m_time_start,0, False)),
                                ],p_just_checking_no_propagation=True))
                        ):
                            return False
                        else:
                            return True
            return False

        def persistence_transition_conflict(p_asrt_pers:Assertion, p_asrt_trans:Assertion):
            if p_asrt_pers.m_sv_name == p_asrt_trans.m_sv_name and p_asrt_pers.m_sv_params_names == p_asrt_trans.m_sv_params_names:
                b = True
                for i in range(len(p_asrt_pers.m_sv_params_vars)):
                    if not p_cn.objvars_unifiable(p_asrt_pers.m_sv_params_vars[i],p_asrt_trans.m_sv_params_vars[i]):
                        b = False
                        break
                if b:
                    if (p_cn.propagate_constraints([
                        (ConstraintType.TEMPORAL,(p_asrt_pers.m_time_start,p_asrt_trans.m_time_end,0,False)),
                        (ConstraintType.TEMPORAL,(p_asrt_trans.m_time_start,p_asrt_pers.m_time_end,0,False)),
                        ],p_just_checking_no_propagation=True) 
                    ):
                        if ((p_cn.objvars_unified(p_asrt_trans.m_sv_val_sec, p_asrt_pers.m_sv_val)
                            and p_cn.propagate_constraints([
                                (ConstraintType.TEMPORAL,(p_asrt_pers.m_time_start,p_asrt_trans.m_time_end,0, False)),
                                (ConstraintType.TEMPORAL,(p_asrt_trans.m_time_end,p_asrt_pers.m_time_start,0, False)),
                                ],p_just_checking_no_propagation=True))
                        or (p_cn.objvars_unified(p_asrt_pers.m_sv_val, p_asrt_trans.m_sv_val)
                            and p_cn.propagate_constraints([
                                (ConstraintType.TEMPORAL,(p_asrt_trans.m_time_start,p_asrt_pers.m_time_end,0, False)),
                                (ConstraintType.TEMPORAL,(p_asrt_pers.m_time_end,p_asrt_trans.m_time_start,0, False)),
                                ],p_just_checking_no_propagation=True))
                        ):
                            return False
                        else:
                            return True
            return False

        res:typing.List[typing.Tuple[Assertion,Assertion]] = []

        # naive brute force implementation
        # can use heuristics, info accumulated during search etc for inference (causal chains etc) to restrict the search / candidate flaws
        for new_asrt in p_new_assertions:
            for asrt in self.m_unsupported_assertions + self.m_supported_assertions:
                if new_asrt.m_type == AssertionType.PERSISTENCE and asrt.m_type == AssertionType.PERSISTENCE:
                    if persistences_conflict(new_asrt, asrt):
                        res.append((new_asrt, asrt))
                elif new_asrt.m_type == AssertionType.TRANSITION and asrt.m_type == AssertionType.TRANSITION:
                    if transitions_conflict(new_asrt, asrt):
                        res.append((new_asrt, asrt))
                else:
                    if new_asrt.m_type == AssertionType.PERSISTENCE:
                        asrt_pers = new_asrt
                        asrt_trans = asrt
                    else:
                        asrt_pers = asrt
                        asrt_trans = new_asrt
                    if persistence_transition_conflict(asrt_pers, asrt_trans):
                        res.append((new_asrt, asrt))

        return res

# actually action *template*
class Action(typing.NamedTuple):
    m_action_name:str
    m_action_params_names:typing.Tuple[str,...]
    m_action_params_vars:typing.Tuple[str,...]

    m_time_start:str
    m_time_end:str

    m_assertions = []
    # (unsupported assertions) (Nau 2020 : "no supported assertions = if you insert an action into a chronicle, you need to figure out how to support it")
    # reminds of HGN(?) ActorSim(?) and Bit-Monnot 2020 (hierarchronicles - "method chronicles with subtasks and no effects" and "action chronicles with effects and no subtasks")
    m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]] = []


# actually method *template*
class Method(typing.NamedTuple):
    m_method_name:str
    m_method_params_names:typing.Tuple[str,...]
    m_method_params_vars:typing.Tuple[str,...]
    
    m_time_start:str
    m_time_end:str

    m_assertions = [] # actually subgoals ; Nau 2020: "can't make a change happen, can only create subgoals"
    m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]] = []


def is_action_applicable(action:Action, chronicle:Chronicle, time:str): # time : str - var name : to have grounding : pass in a variable singleton domain
    pass


def is_method_applicable(action:Method, chronicle:Chronicle, time:str):
    pass

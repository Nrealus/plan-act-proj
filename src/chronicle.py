from __future__ import annotations
from ast import Assert

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.base import Assertion, AssertionType, Action, Method
from src.constraints.constraints import ConstraintNetwork, ConstraintType

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
        self.m_assertions:typing.Dict[Assertion, bool] = [] # boolean value indicates whether assertion is supported or unsupported
        # "subdivide" even further ? (un)supported conditions/effects (separately)
        self.m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]] = []
        #self.m_actions = [] - in GNT 2016 (book) - "a set A of temporally qualified primitives and tasks"...

        self.m_causal_support:typing.Dict[Assertion,typing.Set[Assertion]] = {} # other way to store supported assertions...? (how to do with those that are "a priori" supported?)

        self.m_delayed_support_from_task = {}

        # represent all assertions in a "causal graph" ? : vertices : assertions, edges : incoming causal links
        # non supported assertions - no edges incoming (no causal links / no supporters)
        # for a priori supported assertions : need a special causal link / edge ("a priori causal link ?") (or persistence assertion (starting from time 0 ?) with on a sv with "any" value)

    def clear(self):
        
        self.m_goal = None
        self.m_assertions = {}
        self.m_constraints = []
        self.m_causal_support = {}

    def get_unsupported_assertions(self) -> typing.List[Assertion]:

        res = []
        for i_asrt in self.m_assertions:
            if self.m_assertions[i_asrt] == False:
                res.append(i_asrt)
        return res

    def is_action_or_method_applicable(self, p_act_or_meth:Action, p_time:str, p_cn:ConstraintNetwork):

        if (p_cn.propagate_constraints([
            (ConstraintType.TEMPORAL,(p_act_or_meth.m_time_start,p_time,0,False)),
            (ConstraintType.TEMPORAL,(p_time,p_act_or_meth.m_time_start,0,False)),
            ],p_just_checking_no_propagation=True) 
        ): # if action/method's starting time is p_time
            b = True
            for i_asrt in self.m_assertions:
                if (p_cn.propagate_constraints([
                        (ConstraintType.TEMPORAL,(p_act_or_meth.m_time_start,i_asrt.m_time_start,0,False)),
                        (ConstraintType.TEMPORAL,(i_asrt.m_time_start,p_act_or_meth.m_time_start,0,False)),
                        ],p_just_checking_no_propagation=True)
                    and len(self.m_causal_support[i_asrt]) == 0
                ):
                    b = False
            if b: # if this chronicle supports all "starting" temporal assertions in action/method (whose starting time is the same as the starting time of the action/method)
                for i_chronicle_asrt in self.m_assertions:
                    if self.m_assertions[i_chronicle_asrt] == False:
                        for i_act_or_meth_asrt in p_act_or_meth.m_assertions:
                            if i_chronicle_asrt.is_causally_supported_by(i_act_or_meth_asrt, p_cn):
                                return True
            return False

    # checking possible conflicts should be done incrementally with every transformation of the chronicle
    # assuming the new assertions and constraints are consistent with each other - checking conflicts with "old" assertions and constraints
    # as for conflicts in new assertions and constraints, assume that they are formed/built as to be consistent with each other
    # OR will have to deal with them anyway, either here (in this method or a similar one) or somewhere else
    def get_induced_conflicts(self, p_input_assertions:typing.Iterable[Assertion], p_cn:ConstraintNetwork) -> typing.List[typing.Tuple[Assertion,Assertion]]:

        def persistences_conflict(p_asrt1:Assertion, p_asrt2:Assertion):
            if p_asrt1 == p_asrt2:
                return False
            elif p_asrt1.m_sv_name == p_asrt2.m_sv_name and p_asrt1.m_sv_params_names == p_asrt2.m_sv_params_names:
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
        for new_asrt in p_input_assertions:
            for asrt in self.m_assertions:
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
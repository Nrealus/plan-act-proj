from __future__ import annotations
from ast import Assert

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.base import Assertion, AssertionType, Action, Method
from src.constraints.constraints import ConstraintNetwork, ConstraintType

class ChronicleTransformationType(Enum):
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

        self.m_assertions:typing.Dict[Assertion, bool] = {} # bool value : supported or not
        self.m_causal_network:typing.Dict[Assertion, Assertion] = {} # value : supporter assertion. if a priori supported : None
        self.m_conflicts:typing.Set[typing.Tuple[Assertion,Assertion]] = set()

        self.m_constraints:typing.Set[typing.Tuple[ConstraintType,typing.Any]] = []
        #self.m_actions = [] - in GNT 2016 (book) - "a set A of temporally qualified primitives and tasks"...

    def clear(self):
        
        self.m_goal = None
        self.m_assertions = {}
        self.m_causal_network = {}
        self.m_constraints = []

    def transform_chronicle(self,
        p_new_assertions:typing.Iterable[Assertion],
        p_new_constraints:typing.Iterable[typing.Tuple[ConstraintType,typing.Any]],
        p_cn:ConstraintNetwork
    ):
        
        self.m_conflicts.update(self.get_induced_conflicts(p_new_assertions,p_cn))

        

    def is_action_or_method_applicable(self, p_act_or_meth:Action|Method, p_time:str, p_cn:ConstraintNetwork):

        res = False
        # the action/method's starting time must be "now" (p_time)
        if (p_cn.propagate_constraints([
            (ConstraintType.TEMPORAL,(p_act_or_meth.m_time_start,p_time,0,False)),
            (ConstraintType.TEMPORAL,(p_time,p_act_or_meth.m_time_start,0,False)),
            ],p_just_checking_no_propagation=True) 
        ):
            for i_act_or_meth_asrt in p_act_or_meth.m_assertions:
                for i_chronicle_asrt in self.m_assertions:
                    if i_act_or_meth_asrt == i_chronicle_asrt:
                        break
                    # the chronicle must support all action/method's assertions
                    if not (i_act_or_meth_asrt in self.m_causal_network or i_act_or_meth_asrt.is_causally_supported_by(i_chronicle_asrt, p_cn)):
                        return False
                    # the action/method must support must have at least one assertion supporting an unsupported one of the chronicle
                    if res == False and i_chronicle_asrt.is_causally_supported_by(i_act_or_meth_asrt, p_cn):
                        res = True
        return res

    # checking possible conflicts should be done incrementally with every transformation of the chronicle
    # assuming the new assertions and constraints are consistent with each other - checking conflicts with "old" assertions and constraints
    # as for conflicts in new assertions and constraints, assume that they are formed/built as to be consistent with each other
    # OR will have to deal with them anyway, either here (in this method or a similar one) or somewhere else
    def get_induced_conflicts(self, p_new_assertions:typing.Iterable[Assertion], p_cn:ConstraintNetwork) -> typing.Set[typing.Tuple[Assertion,Assertion]]:

        res:typing.Set[typing.Tuple[Assertion,Assertion]] = set()

        # naive brute force implementation
        # can use heuristics, info accumulated during search etc for inference (causal chains etc) to restrict the search / candidate flaws
        for new_asrt in p_new_assertions:
            for asrt in self.m_assertions:
                if asrt.check_conflict(new_asrt, p_cn):# and not (new_asrt, asrt) in res:
                    res.add((asrt,new_asrt))
        return res
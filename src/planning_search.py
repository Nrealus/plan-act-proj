from __future__ import annotations

import sys

from src.constraints.constraints import ConstraintType
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

import typing
from enum import Enum
from src.base import Action, Assertion, Method

class ResolverType(Enum):
    pass

class SearchNodeType(Enum):
    FLAW = 0
    RESOLVER = 1
    CHARLIE = 2
    EVE = 3
    HELPER = 4

class FlawNodeInfo(typing.NamedTuple):
    m_assertion1:Assertion
    m_assertion2:Assertion
    # if assertion2 is None, then it's an unsupportd assertion / open goal flaw
    # if not, then conflict assertion
    # if more complicated flaws are introduced, a more detailed / general representation may be needed

class ResolverNodeInfo(typing.NamedTuple):
    m_type:ResolverType
    m_assertion1:Assertion
    m_assertion2:Assertion
    m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]]
    m_action_instance:Action
    m_method_instance:Method

class CharlieMoveInfo(typing.NamedTuple):
    chosen_controllable_times:typing.List[str]
    wait_time:float # here float could make sense...! i.e. wait until a certain "real" time, not necessarily towards a variable / time point. in that case - "str"
    # if it's <= 0 it means we have a "play" move. if not - "wait" move

class EveMoveInfo(typing.NamedTuple):
    m_chosen_uncontrollable_times:typing.List[str]

class SearchNode():

    def __init__(self,
        p_node_type:SearchNodeType,
        p_parent:SearchNode,
        p_time:float,
        p_state:object,
        #p_constraints:object,
        #p_goal_memory:List[GoalMemoryElement]
    ):
        self.m_node_type = p_node_type
        self.m_parent = p_parent
        self.m_children:typing.List[SearchNode] = []

        self.m_time = p_time
        self.m_state = p_state
        self.m_constraints = None#p_constraints # constr net, i guess 
        self.m_goal_memory = None#p_goal_memory
        #self.scheduled_time_points ?
        #other variables than time points ? maybe already accounted for in constr net ?

        # V these actually correspond to the edge coming from the parent V
        # in other words, it contains the details of the _parent_'s choice for this node 
        self.m_flaw_node_info = None
        self.m_resolver_node_info = None
        self.m_charlie_move_info = None
        self.m_eve_move_info = None
        # as such, we have the following:
        # flaw type node : has non-empty resolver_info or eve_move_info (depending on previous node), nothing if root
        # resolver type node : has non-empty flaw_info
        # charlie type node : same as flaw type node (depending on parent node, non-empty resolver_info or eve_move_info)
        # eve node type : has non-empty charlie_move_info
        
        # so, if we want to know the search choices made at this node, we need to go through its children and look at their "info" fields
        # or, if we want to know our choices "directly", store them in lists, "parallel" to the children list
        # e.g. flaws[], resolvers[], charlie_moves[], eve_moves[] (indices corresponding to children list)


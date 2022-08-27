from __future__ import annotations

import sys

from src.goal_memory import GoalMemory
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from copy import deepcopy
import typing
from enum import Enum
from src.constraints.constraints import ConstraintNetwork, ConstraintType
from src.base import Assertion, Action, Method
from src.chronicle import Chronicle

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
    #m_type:ResolverType
    m_assertion:Assertion
    m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]]
    m_action_or_method_instance:Action|Method

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
        p_chronicle:Chronicle,
        #p_constraints:object,
        #p_goal_memory:List[GoalMemoryElement]
        p_flaw_node_info:FlawNodeInfo=None,
        p_resolver_node_info:ResolverNodeInfo=None,
        p_charlie_move_info:CharlieMoveInfo=None,
        p_eve_move_info:EveMoveInfo=None,
    ):
        self.m_node_type:SearchNodeType = p_node_type
        self.m_parent:SearchNode = p_parent
        self.m_children:typing.List[SearchNode] = []

        self.m_time:float = p_time
        self.m_state:object = p_state
        self.m_chronicle:Chronicle = p_chronicle
        #self.m_constraints = None#p_constraints # constr net, i guess 
        self.m_constraint_network = ConstraintNetwork()
        self.m_goal_memory:GoalMemory = None#p_goal_memory
        #self.scheduled_time_points ?
        #other variables than time points ? maybe already accounted for in constr net ?

        # V these actually correspond to the edge coming from the parent V
        # in other words, it contains the details of the _parent_'s choice for this node 
        self.m_flaw_node_info:FlawNodeInfo = p_flaw_node_info
        self.m_resolver_node_info:ResolverNodeInfo = p_resolver_node_info
        self.m_charlie_move_info:CharlieMoveInfo = p_charlie_move_info
        self.m_eve_move_info:EveMoveInfo = p_eve_move_info
        # as such, we have the following:
        # flaw type node : has non-empty resolver_info or eve_move_info (depending on previous node), nothing if root
        # resolver type node : has non-empty flaw_info
        # charlie type node : same as flaw type node (depending on parent node, non-empty resolver_info or eve_move_info)
        # eve node type : has non-empty charlie_move_info
        
        # so, if we want to know the search choices made at this node, we need to go through its children and look at their "info" fields
        # or, if we want to know our choices "directly", store them in lists, "parallel" to the children list
        # e.g. flaws[], resolvers[], charlie_moves[], eve_moves[] (indices corresponding to children list)


    def build_children(self):

        if self.m_node_type == SearchNodeType.FLAW:

            # resolvable at time now !!
            flaws = self.select_flaws() # can depend on search strategy
            for fi in flaws:

                self.m_children.append(SearchNode(p_node_type=SearchNodeType.RESOLVER,
                    p_parent=self,
                    p_time=self.m_time,
                    p_state=self.m_state,
                    p_chronicle=self.m_chronicle,
                    p_flaw_node_info=fi))

        if self.m_node_type == SearchNodeType.RESOLVER:

            # usable at time now !!
            resolvers = self.select_resolvers()
            for ri in resolvers:
                
                transformed_chronicle = deepcopy(self.m_chronicle)

                if self.m_flaw_node_info.m_assertion2 is not None: # flaw : conflict flaw - only resolver can only be constraint enforcement
                    transformed_chronicle.m_conflicts.remove((self.m_flaw_node_info.m_assertion1,self.m_flaw_node_info.m_assertion2))
                    transformed_chronicle.transform_chronicle(
                        [],
                        ri.m_constraints,
                        self.m_constraint_network)
                elif ri.m_action_or_method_instance is not None: # flaw : unsupported assertion - action / method insertion resolver
                    # causal network ?
                    transformed_chronicle.transform_chronicle(
                        ri.m_action_or_method_instance.m_assertions,
                        ri.m_action_or_method_instance.m_constraints,
                        self.m_constraint_network)
                elif ri.m_assertion is not None:  # flaw : unsupported assertion -direct supporter resolver : new assertion "prolonging" an existing one (nau 2020) (=causal link ?)
                    # causal network ?
                    transformed_chronicle.transform_chronicle(
                        ri.m_assertion,
                        ri.m_constraints,
                        self.m_constraint_network)
                else:  # flaw : unsupported assertion - direct support resolver : constraints to use an existing assertion as a supporter
                    # causal network ?
                    transformed_chronicle.transform_chronicle(
                        [],
                        ri.m_constraints,
                        self.m_constraint_network)

                # unify last two ?

                self.m_children.append(SearchNode(p_node_type=SearchNodeType.FLAW,
                    p_parent=self,
                    p_time=self.m_time,
                    p_state=self.m_state,
                    p_chronicle=transformed_chronicle,
                    p_resolver_node_info=ri))

                # not necessarily charlie or flaw : both children type should be possible... since resolver nodes are like "or"
                # self.m_children.append(SearchNode(p_node_type=SearchNodeType.CHARLIE,
                #     p_parent=self,
                #     p_time=self.m_time,
                #     p_state=self.m_state,
                #     p_chronicle=transformed_chronicle,
                #     p_resolver_node_info=ri))

        if self.m_node_type == SearchNodeType.CHARLIE:
            pass
            # for ...
            #     self.m_children.append(SearchNode(p_node_type=SearchNodeType.EVE,
            #         p_parent=self,
            #         p_time=self.m_time,
            #         p_state=self.m_state,
            #         p_chronicle=transformed_chronicle,
            #         p_charlie_move_info=ci))

        if self.m_node_type == SearchNodeType.EVE:
            pass
            # for ...
            #     self.m_children.append(SearchNode(p_node_type=SearchNodeType.CHARLIE,
            #         p_parent=self,
            #         p_time=self.m_time,
            #         p_state=self.m_state,
            #         p_chronicle=transformed_chronicle,
            #         p_eve_move_info=ei))
            # for ...
            #     self.m_children.append(SearchNode(p_node_type=SearchNodeType.FLAW,
            #         p_parent=self,
            #         p_time=self.m_time,
            #         p_state=self.m_state,
            #         p_chronicle=transformed_chronicle,
            #         p_eve_move_info=ei))

    def select_flaws(self) -> typing.List[FlawNodeInfo]:
        # use non null self.m_resolver_node_info or self.m_eve_move_info
        res = []
        # in general : "priority queue" (or just priority order in list) according to search strategy
        # for example : flaws with only one possible resolver first... (FAPE 2020 p.40)
        # maybe if mcts is used, not all children at the same time ? maybe come back to this node later and "complete" its children ?--
        for (asrt,supported) in self.m_chronicle.m_assertions:
            if not supported: 
                res.append(FlawNodeInfo(m_assertion1=asrt, m_assertion2=None))
        for (asrt1, asrt2) in self.m_chronicle.m_conflicts:
            res.append(FlawNodeInfo(m_assertion1=asrt1, m_assertion2=asrt2))
        return res

    def select_resolvers(self) -> typing.List[ResolverNodeInfo]:
        res = []
        # suggest resolver by analizing the flaw, chronicle etc... (later heuristics...)
        # use non null self.m_resolver_flaw_info
        return res

    def select_charlie_moves(self) -> typing.List[CharlieMoveInfo]:
        res = []
        # use non null self.m_resolver_node_info or self.m_eve_move_info
        return res

    def select_eve_moves(self) -> typing.List[EveMoveInfo]:
        res = []
        # use non null self.m_charlie_move_info
        return res

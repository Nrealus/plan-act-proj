from __future__ import annotations
import re

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

class ResolverType(Enum):
    CONFLICT_SEPARATION=0
    EXISTING_DIRECT_SUPPORT_NOW=1
    NEW_DIRECT_SUPPORT_NOW=2
    METHOD_INSERTION_NOW=3
    ACTION_INSERTION_NOW=4

class FlawNodeInfo(typing.NamedTuple):
    m_assertion1:Assertion
    m_assertion2:Assertion
    # if assertion2 is None, then it's an unsupportd assertion / open goal flaw
    # if not, then conflict assertion
    # if more complicated flaws are introduced, a more detailed / general representation may be needed

class ResolverNodeInfo(typing.NamedTuple):
    m_type:ResolverType
    m_direct_support_assertion:Assertion
    m_direct_support_assertion_supporter:Assertion
    m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]]
    m_act_or_meth_instance:Action|Method
    m_act_or_meth_assertion_support_info:typing.List[typing.Tuple[Assertion,Assertion,bool]]

class CharlieMoveInfo(typing.NamedTuple):
    m_chosen_controllable_times:typing.List[str]
    m_wait_time:float # here float could make sense...! i.e. wait until a certain "real" time, not necessarily towards a variable / time point. in that case - "str"
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
        p_goal_memory:GoalMemory=None,
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
        self.m_constraint_network = ConstraintNetwork() # should this really be here or inside the chronicle ?
        self.m_goal_memory:GoalMemory = p_goal_memory
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
            flaws = self.select_flaws() # order/priority can depend on search strategy
            for fi in flaws:

                self.m_children.append(SearchNode(p_node_type=SearchNodeType.RESOLVER,
                    p_parent=self,
                    p_time=self.m_time,
                    p_state=self.m_state,
                    p_chronicle=deepcopy(self.m_chronicle),
                    p_goal_memory=deepcopy(self.m_goal_memory),
                    p_flaw_node_info=fi))

        if self.m_node_type == SearchNodeType.RESOLVER:

            # usable at time now !!
            resolvers = self.select_resolvers() # order/priority can depend on search strategy
            for ri in resolvers:
                
                transformed_chronicle = deepcopy(self.m_chronicle)

                if ri.m_type == ResolverType.CONFLICT_SEPARATION:

                    self.m_constraint_network.propagate_constraints(ri.m_constraints)

                    transformed_chronicle.m_conflicts.remove((self.m_flaw_node_info.m_assertion1,self.m_flaw_node_info.m_assertion2))
                    transformed_chronicle.m_constraints.update(ri.m_constraints)

                elif ri.m_type == ResolverType.EXISTING_DIRECT_SUPPORT_NOW or ri.m_type == ResolverType.NEW_DIRECT_SUPPORT_NOW:
                    
                    transformed_chronicle.m_assertions[ri.m_direct_support_assertion] = True
                    transformed_chronicle.m_causal_network[ri.m_direct_support_assertion] = ri.m_direct_support_assertion_supporter
                    # the assertion supporting the introduced direct supporter (for the flawed assertion)

                    transformed_chronicle.m_assertions[self.m_flaw_node_info.m_assertion1] = True
                    transformed_chronicle.m_causal_network[self.m_flaw_node_info.m_assertion1] = ri.m_direct_support_assertion

                    self.m_constraint_network.propagate_constraints(ri.m_constraints)

                    transformed_chronicle.m_constraints.update(ri.m_constraints)
                    transformed_chronicle.m_conflicts.update(transformed_chronicle.get_induced_conflicts([ri.m_direct_support_assertion], self.m_constraint_network))

                elif ri.m_type == ResolverType.METHOD_INSERTION_NOW or ri.m_type == ResolverType.ACTION_INSERTION_NOW:

                    transformed_chronicle.m_supporter_origin_commitment[self.m_flaw_node_info.m_assertion1] = ri.m_act_or_meth_instance
                    # transformed_chronicle.m_assertions[self.m_flaw_node_info.m_assertion1] = True
                    # NOTE : DON'T SET THE FLAWED UNSUPPORTED ASSERTION TO "SUPPORTED" ! (line of code above)
                    # if an action was inserted, setting the flawed unsupported assertion to supported will be done in the 2nd loop below.
                    # if a method was inserted, it could also have a subgoal ((unsupported) persistence assertion) supporting the flawed assertion, 
                    # which would be dealt with the same way as with an action (below)
                    # if the inserted method doesn't have a subgoal "directly" supporting the flawed assertion, we still commit (see above) to the fact that
                    # the supporter of the flawed assertion will come from a further decomposition (by a method/action) of one of the method's subgoal assertions.
                    # in that case, the supporter origin (see above) will have to be update to the new decomposing method/action.

                    for i_asrt in ri.m_act_or_meth_instance.m_assertions:
                        transformed_chronicle.m_assertions[i_asrt] = False

                    for (i_asrt_supportee, i_asrt_supporter) in ri.m_act_or_meth_assertion_support_info:
                        transformed_chronicle.m_assertions[i_asrt_supportee] = True
                        transformed_chronicle.m_causal_network[i_asrt_supportee] = i_asrt_supporter

                    self.m_constraint_network.propagate_constraints(ri.m_constraints)

                    transformed_chronicle.m_constraints.update(ri.m_constraints)
                    transformed_chronicle.m_conflicts.update(transformed_chronicle.get_induced_conflicts(ri.m_direct_support_assertion, self.m_constraint_network))

                # decision could be made using search control on whether to follow with a flaw or charlie child (or both)
                # until then / by default - both 

                self.m_children.append(SearchNode(p_node_type=SearchNodeType.FLAW,
                    p_parent=self,
                    p_time=self.m_time,
                    p_state=self.m_state,
                    p_chronicle=transformed_chronicle,
                    p_goal_memory=deepcopy(self.m_goal_memory),
                    # UPDATE GOAL MEMORY (WITH ACTION INTRODUCTIONS (or maybe all chronicle transformations) IN EXPANSIONS ?)
                    p_resolver_node_info=ri))

                self.m_children.append(SearchNode(p_node_type=SearchNodeType.CHARLIE,
                    p_parent=self,
                    p_time=self.m_time,
                    p_state=self.m_state,
                    p_chronicle=transformed_chronicle,
                    p_goal_memory=deepcopy(self.m_goal_memory),
                    # UPDATE GOAL MEMORY (WITH ACTION INTRODUCTIONS (or maybe all chronicle transformations) IN EXPANSIONS ?)
                    p_resolver_node_info=ri))

        if self.m_node_type == SearchNodeType.CHARLIE:
            pass
            # for ...
            #     self.m_children.append(SearchNode(p_node_type=SearchNodeType.EVE,
            #         p_parent=self,
            #         p_time=self.m_time,
            #         p_state=self.m_state,
            #         p_chronicle=transformed_chronicle,
            #         p_goal_memory=deepcopy(self.m_goal_memory),
            #         p_charlie_move_info=ci))

        if self.m_node_type == SearchNodeType.EVE:
            pass
            # for ...
            #     self.m_children.append(SearchNode(p_node_type=SearchNodeType.CHARLIE,
            #         p_parent=self,
            #         p_time=self.m_time,
            #         p_state=self.m_state,
            #         p_chronicle=transformed_chronicle,
            #         p_goal_memory=deepcopy(self.m_goal_memory),
            #         p_eve_move_info=ei))
            # for ...
            #     self.m_children.append(SearchNode(p_node_type=SearchNodeType.FLAW,
            #         p_parent=self,
            #         p_time=self.m_time,
            #         p_state=self.m_state,
            #         p_chronicle=transformed_chronicle,
            #         p_goal_memory=deepcopy(self.m_goal_memory),
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

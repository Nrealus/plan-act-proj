from __future__ import annotations

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from copy import deepcopy
import typing
from enum import Enum
from src.utility.new_int_id import new_int_id
from src.constraints.constraints import ConstraintNetwork, ConstraintType
from src.base import Assertion, Action, Method
from src.chronicle import Chronicle
from src.goal_node import GoalMode, GoalNode

class SearchNodeType(Enum):
    FLAW = 0
    RESOLVER = 1
    CHARLIE = 2
    EVE = 3

class ResolverType(Enum):
    CONFLICT_SEPARATION=0
    EXISTING_DIRECT_PERSISTENCE_SUPPORT_NOW=1
    NEW_DIRECT_PERSISTENCE_SUPPORT_NOW=2
    METHOD_INSERTION_NOW=3
    ACTION_INSERTION_NOW=4

class FlawNodeInfo():
    m_assertion1:Assertion
    m_assertion2:Assertion
    # if assertion2 is None, then it's an unsupportd assertion / open goal flaw
    # if not, then conflict assertion
    # if more complicated flaws are introduced, a more detailed / general representation may be needed

class ResolverNodeInfo():
    m_type:ResolverType
    m_direct_support_assertion:Assertion
    m_direct_support_assertion_supporter:Assertion
    m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]]
    m_action_or_method_instance:Action|Method
    m_act_or_meth_assertion_support_info:typing.List[typing.Tuple[Assertion,Assertion]]#,bool]]

class CharlieMoveInfo():
    m_selected_controllable_timepoints:typing.List[str]
    m_wait_time:float # here float could make sense...! i.e. wait until a certain "real" time, not necessarily towards a variable / time point. in that case - "str"
    # if it's <= 0 it means we have a "play" move. if not - "wait" move

class EveMoveInfo():
    m_selected_uncontrollable_timepoints:typing.List[str]

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
                    p_flaw_node_info=fi))

        if self.m_node_type == SearchNodeType.RESOLVER:

            # usable at time now !!
            old_chronicle = deepcopy(self.m_chronicle)
            
            resolvers = self.select_resolvers() # order/priority can depend on search strategy
            for ri in resolvers:
                
                transformed_chronicle = deepcopy(old_chronicle)
            
                resolvers = self.select_resolvers() # order/priority can depend on search strategy
                if ri.m_type == ResolverType.CONFLICT_SEPARATION:

                    transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_constraints)
                    transformed_chronicle.m_conflicts.remove((self.m_flaw_node_info.m_assertion1,self.m_flaw_node_info.m_assertion2))

                elif ri.m_type == ResolverType.EXISTING_DIRECT_PERSISTENCE_SUPPORT_NOW or ri.m_type == ResolverType.NEW_DIRECT_PERSISTENCE_SUPPORT_NOW:

                    new_action = Action(
                        m_action_name="monitor_assertion_{0}".format(str(new_int_id())),
                        m_action_params_names="assertion",
                        m_action_params_vars=self.m_flaw_node_info.m_assertion1,
                        m_time_start=self.m_flaw_node_info.m_assertion1.time_start,
                        m_time_end=self.m_flaw_node_info.m_assertion1.time_end,
                        m_assertions=set(), # self.m_flaw_node_info.m_assertion1.m_assertions
                        m_constraints=set(), # self.m_flaw_node_info.m_assertion1.m_constraints
                    )
                    if transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent is None:
                        parent = None
                    else:
                        if transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion is not None:
                            parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion.m_action_or_method_instance
                            # None still possible                                
                    transformed_chronicle.m_plan[new_action] = parent

                    # an action that will have to monitor whether the assertion is indeed respected during execution
                    # it is this action that will be triggered when the goal/assertion will be dispatched

                    transformed_chronicle.m_assertions[self.m_flaw_node_info.m_assertion1] = True
                    transformed_chronicle.m_causal_network[self.m_flaw_node_info.m_assertion1] = ri.m_direct_support_assertion

                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.COMMITTED
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions = [ri]
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_committed_expansion = ri
                    
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.EXPANDED
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions.append(ri)

                    # it is indeed None in the case of direct support from an existing persistence assertion, where only constraints are actually added
                    # (this is adressed right above)
                    if ri.m_direct_support_assertion_supporter is not None:

                        new_action2 = Action(
                            m_action_name="monitor_assertion_{0}".format(str(new_int_id())),
                            m_action_params_names="assertion",
                            m_action_params_vars=ri.m_direct_support_assertion,
                            m_time_start=ri.m_direct_support_assertion.time_start,
                            m_time_end=ri.m_direct_support_assertion.time_end,
                            m_assertions=set(), # ri.m_direct_support_assertion.m_assertions
                            m_constraints=set(), # ri.m_direct_support_assertion.m_constraints
                        )
                        transformed_chronicle.m_plan[new_action2] = parent # maybe new_action?

                        transformed_chronicle.m_assertions[ri.m_direct_support_assertion] = True
                        transformed_chronicle.m_causal_network[ri.m_direct_support_assertion] = ri.m_direct_support_assertion_supporter
                        # the assertion supporting the introduced direct supporter (for the flawed assertion)

                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion] = GoalNode()
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_mode = GoalMode.COMMITTED
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1]
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_possible_expansions = [ri]
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_committed_expansion = ri

                    transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_constraints)
                    transformed_chronicle.m_conflicts.update(transformed_chronicle.get_induced_conflicts([ri.m_direct_support_assertion]))

                elif ri.m_type == ResolverType.METHOD_INSERTION_NOW or ri.m_type == ResolverType.ACTION_INSERTION_NOW:

                    # NOTE : DON'T SET THE FLAWED UNSUPPORTED ASSERTION TO "SUPPORTED" !
                    # if an action was inserted, setting the flawed unsupported assertion to supported will be done in the 2nd loop below.
                    # if a method was inserted, it could also have a subgoal ((unsupported) persistence assertion) supporting the flawed assertion, 
                    # which would be dealt with the same way as with an action (below)
                    # if the inserted method doesn't have a subgoal "directly" supporting the flawed assertion, we still commit (see above) to the fact that
                    # the supporter of the flawed assertion will come from a further decomposition (by a method/action) of one of the method's subgoal assertions.
                    # in that case, the supporter origin (see above) will have to be update to the new decomposing method/action.
                    #transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.COMMITTED
                    #transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_committed_expansion = ri.m_act_or_meth_instance                    

                    if transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent is None:
                        parent = None
                    else:
                        if transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion is not None:
                            parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion.m_action_or_method_instance
                            # None still possible                                
                    transformed_chronicle.m_plan[ri.m_action_or_method_instance] = parent

                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.COMMITTED
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions = [ri]
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_committed_expansion = ri

                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.EXPANDED
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions.append(ri)

                    for i_asrt in ri.m_action_or_method_instance.assertions:
                            
                        transformed_chronicle.m_assertions[i_asrt] = False

                        transformed_chronicle.m_goal_nodes[i_asrt] = GoalNode()
                        transformed_chronicle.m_goal_nodes[i_asrt].m_mode = GoalMode.SELECTED
                        transformed_chronicle.m_goal_nodes[i_asrt].m_parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1]

                    for (i_asrt_supportee, i_asrt_supporter) in ri.m_act_or_meth_assertion_support_info:

                        # NOTE: support is guaranteed only for those assertions of the action which start at the same time as it !!
                        # others may not have guaranteed supporter ! which is why we first need to set to false and selected in the previous loop
                        transformed_chronicle.m_assertions[i_asrt_supportee] = True
                        transformed_chronicle.m_causal_network[i_asrt_supportee] = i_asrt_supporter

                        if i_asrt_supportee in ri.m_action_or_method_instance.assertions:
                            asrt = i_asrt_supportee
                        else: # either already in chronicle or introduced by action/method
                            asrt = i_asrt_supporter

                        if asrt != self.m_flaw_node_info.m_assertion1:
                            transformed_chronicle.m_goal_nodes[asrt].m_mode = GoalMode.COMMITTED
                            transformed_chronicle.m_goal_nodes[asrt].m_parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1]
                            transformed_chronicle.m_goal_nodes[asrt].m_possible_expansions = [ri]
                            transformed_chronicle.m_goal_nodes[asrt].m_committed_expansion = ri

                    transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_constraints)
                    transformed_chronicle.m_conflicts.update(transformed_chronicle.get_induced_conflicts(ri.m_action_or_method_instance.assertions))

                # decision could be made using search control on whether to follow with a flaw or charlie child (or both)
                # until then / by default - both 

                self.m_children.append(SearchNode(p_node_type=SearchNodeType.FLAW,
                    p_parent=self,
                    p_time=self.m_time,
                    p_state=self.m_state,
                    p_chronicle=transformed_chronicle,
                    p_resolver_node_info=ri))

                self.m_children.append(SearchNode(p_node_type=SearchNodeType.CHARLIE,
                    p_parent=self,
                    p_time=self.m_time,
                    p_state=self.m_state,
                    p_chronicle=transformed_chronicle,
                    p_resolver_node_info=ri))

        if self.m_node_type == SearchNodeType.CHARLIE:
            
            charlie_moves = self.select_charlie_moves()
            '''for ci in charlie_moves:

                transformed_chronicle = deepcopy(old_chronicle)

                # "play" move
                if ci.m_wait_time <= 0:
                # should the wait time be a float "offset" ? or should it be a time point that comes next ?
                #FIXME: probably. change this tomorrow

                    for ctr_tp in ci.m_selected_controllable_timepoints:

                        #for asrt in transformed_chronicle.m_assertions:
                            #if (transformed_chronicle.m_constraint_network.propagate_constraints([
                            #        (ConstraintType.TEMPORAL, (ctr_tp, asrt.m_time_start, 0, False)),
                            #        (ConstraintType.TEMPORAL, (asrt.m_time_start, ctr_tp, 0, False)),
                            #    ], p_just_checking_no_propagation=True)
                            #):
                        transformed_chronicle.m_constraint_network.propagate_constraints([
                            (ConstraintType.TEMPORAL, (ctr_tp, "ref_tp", self.m_time, False)),
                            (ConstraintType.TEMPORAL, ("ref_tp", ctr_tp, self.m_time, False)),
                        ])

                        for asrt in []: # assertions_starting_at_ctr_tp (need to check all time points "unified" with ctr_tp?)
                            if transformed_chronicle.m_goal_nodes[asrt].m_mode == GoalMode.COMMITTED:
                                transformed_chronicle.m_goal_nodes[asrt].m_mode = GoalMode.DISPATCHED
                                #NOTE: action dispatching ?..
                                # "preparation for execution -> execution_state state variable with inactive/running/completed values, then outcomes(successful,failed,unknown(?))"
                        # goal mode : dispatch (for start) for assertions whose starting time point is selected here
 
                    self.m_children.append(SearchNode(p_node_type=SearchNodeType.EVE,
                        p_parent=self,
                        p_time=self.m_time,
                        p_state=self.m_state,#new_state,
                        p_chronicle=transformed_chronicle,
                        p_charlie_move_info=ci))

                # "wait" move
                else:

                    self.m_children.append(SearchNode(p_node_type=SearchNodeType.EVE,
                        p_parent=self,
                        p_time=self.m_time + ci.m_wait_time,
                        p_state=self.m_state,
                        p_chronicle=transformed_chronicle,
                        p_charlie_move_info=ci))
            '''
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
            if not supported and self.m_chronicle.m_goal_nodes[asrt].m_mode != GoalMode.FORMULATED: 
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

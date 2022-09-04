from __future__ import annotations

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from copy import deepcopy
import typing
from enum import Enum
from src.utility.new_int_id import new_int_id
from src.constraints.constraints import ConstraintNetwork, ConstraintType
from src.base import ActionAndMethodTemplate, Assertion, Action, Method
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
    # if assertion2 is None, then the flaw is an unsupportd assertion / open goal flaw
    # if not, then the flaw is a (possibly) conflicting assertions flaw

class ResolverNodeInfo():
    m_type:ResolverType
    m_direct_support_assertion:Assertion
    m_direct_support_assertion_supporter:Assertion
    m_constraints:typing.Set[typing.Tuple[ConstraintType,typing.Any]]
    m_action_or_method_instance:Action|Method
    m_act_or_meth_assertion_support_info:typing.Set[typing.Tuple[Assertion,Assertion]]

class CharlieMoveInfo():
    m_selected_controllable_timepoints:typing.List[str]
    m_wait_time:float # here float could make sense...! i.e. wait until a certain "real" time, not necessarily towards a variable / time point. in that case - "str"
    # if it's <= 0 it means we have a "play" move. if not - "wait" move

class EveMoveInfo():
    m_selected_uncontrollable_timepoints:typing.List[str]

class SearchNode():

    monitor_action_template = ActionAndMethodTemplate(
        p_name="action_monitor_assertion",
        p_params_names=("p_assertion",),
        p_constraints=lambda ts,te,_:[
            (ConstraintType.TEMPORAL, (ts,te,0,False))
        ]
    )

    def __init__(self,
        p_node_type:SearchNodeType,
        p_parent:SearchNode,
        p_time:float,
        p_state:object,
        p_chronicle:Chronicle,
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
                
                # The chronicle of the child search node that is being created 
                transformed_chronicle = deepcopy(old_chronicle)
            
                if ri.m_type == ResolverType.CONFLICT_SEPARATION:

                    # Apply constraints resolving the flaw to the chronicle of the child search node currently being built
                    transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_constraints)
                    # Remove the adressed conflict from the collection of current conflicts in the chronicle of the child search node currently being built
                    transformed_chronicle.m_conflicts.remove((self.m_flaw_node_info.m_assertion1,self.m_flaw_node_info.m_assertion2))

                elif ri.m_type == ResolverType.EXISTING_DIRECT_PERSISTENCE_SUPPORT_NOW or ri.m_type == ResolverType.NEW_DIRECT_PERSISTENCE_SUPPORT_NOW:

                    # A "dummy action" considered to be the expansion of the goal corresponding to the addressed unsupported assertion
                    # Indeed, in accordance with the goal lifecycle, before a goal can be set to the "dispatched" mode,
                    # it needs to be in the "committed" mode, which represents the fact that a means to 
                    # achieve this goal (plan : action, method...) was found and committed to.
                    # Direct support of a previously unsupported assertion is a way to achieve (or guarantee/promise the achievement of) the
                    # goal corresponding to that assertion. To represent that in the *plan* (i.e. course of *action*, not just chronicle) we 
                    # make use of actions which are supposed to achieve / maintain the "promise" made in the chronicle.
                    # Which actually corresponds to the monitoring function of planning and acting.
                    # In conclusion - this action will have to monitor whether the newly directly supported assertion is indeed respected during execution
                    # It is this action that will be triggered when the goal/assertion will be dispatched
                    new_action = Action(
                        p_template=SearchNode.monitor_action_template,
                        p_params={"p_assertion":self.m_flaw_node_info.m_assertion1},
                        p_time_start=self.m_flaw_node_info.m_assertion1.time_start,
                        p_time_end=self.m_flaw_node_info.m_assertion1.time_end,
                    )
                    # Finding this new action's hierarchical place in the plan (parent (method) following the plan decomposition) 
                    parent = None
                    if not transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent is None:
                        if not transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion is None:
                            parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion
                    # Adding the action to the plan in the chronicle of the child search node currently being built
                    # Notice that the line above can still give a None parent
                    transformed_chronicle.m_plan[new_action] = parent
                    
                    # Transitioning the goal corresponding to the flawed assertion in this search node's chronicle to "expanded" mode
                    # with this action as a possible expansion
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.EXPANDED
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions.append(new_action)

                    # Setting the assertion from unsupported to supported and adding its supporter to the causal network
                    # in the chronicle of the child search node currently being built
                    transformed_chronicle.m_assertions[self.m_flaw_node_info.m_assertion1] = True
                    transformed_chronicle.m_causal_network[self.m_flaw_node_info.m_assertion1] = ri.m_direct_support_assertion
                    
                    # Transitioning the goal corresponding to the flawed assertion to "committed" mode with the action introduced above as its committed expansion
                    # in the chronicle of the child search node currently being built
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.COMMITTED
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions = [new_action]
                    transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_committed_expansion = new_action
                    
                    # The following code deals with the case where the direct supporter used was not already present in the chronicle
                    # and was created specifically to resolve the flaw. This newly created direct supporter must be, in turn, directly supported
                    # itself by a persistence assertion already present in the chronicle (ri.m_direct_support_assertion_supporter).
                    # As such, if it is None, direct_support_assertion must have necessarily been already present in the chronicle.
                    # And if it isn't, it needs to be managed (support from ri.m_direct_support_assertion_supporter, status of the corresponding goal)
                    if ri.m_direct_support_assertion_supporter is not None:

                        # Same as above, but addresses the supporter of the introduced direct supporter of the flawed unsupported assertion.
                        new_action2 = Action(
                            p_template=SearchNode.monitor_action_template,
                            p_params={"p_assertion":ri.m_direct_support_assertion},
                            p_time_start=ri.m_direct_support_assertion.time_start,
                            p_time_end=ri.m_direct_support_assertion.time_end,
                        )
                        # Same parent as for the direct supporter - the idea is that both these actions stem from the same decision
                        transformed_chronicle.m_plan[new_action2] = parent

                        # Not adressing ri.m_direct_support_assertion_supporter in this search node's chronicle,
                        # as in this case the ri.m_direct_support_assertion was newly created and not present in this search node's chronicle,
                        # which means that the goal corresponding to it simply doesn't exist yet.
                        # It exists in the chronicle of the child search node currently being built,
                        # where it is introduced in directly "committed" mode (see below)

                        # Same as in the above part
                        transformed_chronicle.m_assertions[ri.m_direct_support_assertion] = True
                        transformed_chronicle.m_causal_network[ri.m_direct_support_assertion] = ri.m_direct_support_assertion_supporter

                        # Same as in the above part
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion] = GoalNode()
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_mode = GoalMode.COMMITTED
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1]
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_possible_expansions = [new_action2]
                        transformed_chronicle.m_goal_nodes[ri.m_direct_support_assertion].m_committed_expansion = new_action2

                    # Apply the constraints introduced to allow the suggested direct supporter to be one
                    transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_constraints)
                    # Update the collection of current conflicts in the chronicle of the child search node currently being built
                    # with all the conflicts which may have appeared after the application of these constraints and possilby new direct supporter assertion
                    transformed_chronicle.m_conflicts.update(transformed_chronicle.get_induced_conflicts([ri.m_direct_support_assertion]))

                elif ri.m_type == ResolverType.METHOD_INSERTION_NOW or ri.m_type == ResolverType.ACTION_INSERTION_NOW:
                    
                    # Finding the hierarchical place in the plan (parent (method) following the plan decomposition)
                    # of the action/method suggested by this resolver
                    parent = None
                    if not transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent is None:
                        if not transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion is None:
                            parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_parent.m_committed_expansion
                    # Adding the action/method to the plan in the chronicle of the child search node currently being built
                    # Notice that the line above can still give a None parent
                    transformed_chronicle.m_plan[ri.m_action_or_method_instance] = parent

                    # Transitioning the goal corresponding to the flawed assertion in this search node's chronicle to "expanded" mode
                    # with action/method suggested in the resolver as a possible expansion
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_mode = GoalMode.EXPANDED
                    self.m_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1].m_possible_expansions.append(ri.m_action_or_method_instance)

                    # Transitioning the goal corresponding to the flawed assertion to "committed" mode with the action introduced above as its committed expansion
                    # in the chronicle of the child search node currently being built is done at the end of the 2nd next loop,
                    # as the flawed unsupported assertion must be one of the assertions supported by the action/method.

                    # Update the chronicle of the child search node currently being built by adding the assertions of the action/method chosen in the resolver to it
                    for i_asrt in ri.m_action_or_method_instance.assertions:
                        
                        transformed_chronicle.m_assertions[i_asrt] = False

                        transformed_chronicle.m_goal_nodes[i_asrt] = GoalNode()
                        transformed_chronicle.m_goal_nodes[i_asrt].m_mode = GoalMode.SELECTED
                        transformed_chronicle.m_goal_nodes[i_asrt].m_parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1]

                    # Manage the assertion supports which made the action/method applicable in the first place
                    # (i.e. set the supported assertions from unsupported to supported and add their supporter in the causal network)
                    for (i_asrt_supportee, i_asrt_supporter) in ri.m_act_or_meth_assertion_support_info:

                        # All of the assertions of the action/method, starting at the same time as it, have to be supported by the chronicle
                        # But those that do not start at the same time as it (and as such don't have to be supported by the chronicle)
                        # still need to be introduced, which is done in the loop above. 
                        transformed_chronicle.m_assertions[i_asrt_supportee] = True
                        transformed_chronicle.m_causal_network[i_asrt_supportee] = i_asrt_supporter
                                
                        # Also, at least one of the chronicle's assertions must be supported by an assertion from the action/method
                        # (The flawed unsupported assertion is (must) be one of them)
                        # These assertions and the corresponding goals are managed below
                        if i_asrt_supportee in ri.m_action_or_method_instance.assertions:
                            asrt = i_asrt_supportee
                        else:
                            asrt = i_asrt_supporter
                        if asrt != self.m_flaw_node_info.m_assertion1:
                            transformed_chronicle.m_goal_nodes[asrt].m_mode = GoalMode.COMMITTED
                            transformed_chronicle.m_goal_nodes[asrt].m_parent = transformed_chronicle.m_goal_nodes[self.m_flaw_node_info.m_assertion1]
                            transformed_chronicle.m_goal_nodes[asrt].m_possible_expansions = [ri.m_action_or_method_instance]
                            transformed_chronicle.m_goal_nodes[asrt].m_committed_expansion = ri.m_action_or_method_instance

                    # Apply the constraints introduced of the action/method and also any other constraints that may be in the resolver
                    # (NOTE: can there be any other ? think about it, and if yes - an example ?)
                    transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_action_or_method_instance.constraints)
                    transformed_chronicle.m_constraint_network.propagate_constraints(ri.m_constraints)

                    # Propagating the instantiation variable for the action/method
                    # Done here and not earlier (e.g. when adding the action/method to the plan)
                    # as other constraints should be propagated first (in order to use the correct )
                    _name = ri.m_action_or_method_instance.name
                    _params = ri.m_action_or_method_instance.template.params_names
                    transformed_chronicle.m_constraint_network.propagate_constraints([
                        (ConstraintType.GENERAL_RELATION,
                            ("__actmethinst_{0}{1}_rel".format(_name, _params),
                            ["__actmethinst_{0}{1}_param_{2}".format(_name,_params,_p) for _p in list(_params)]
                                + ["__actmethinst_{0}{1}_id".format(_name, _params)],
                            [list(transformed_chronicle.m_constraint_network.objvar_domain(_v).get_values())
                                + [new_int_id()] for _v in ri.m_action_or_method_instance.params.values()]
                            )
                        )
                    ])
                    # !! TODO !!: the above approach to general relations assumes an explicit discrete domains representation...
                    # As we cannot really represent all of the possible values for such variables/table columns explicitly,
                    # we will *NEED* better variable domain representations for that very soon.

                    # Update the collection of current conflicts in the chronicle of the child search node currently being built
                    # with all the conflicts which may have appeared after the application of the action/method
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
                            #    ], p_apply_and_push=True)
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

import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from enum import Enum
import typing
from src.base import Assertion
from src.constraints.constraints import ConstraintType

class GoalMode(Enum):
    FORMULATED = 0
    SELECTED = 1
    EXPANDED = 2
    COMMITTED = 3
    DISPATCHED = 4
    EVALUATED = 5
    FINISHED = 6

class GoalNode():

    def __init__(self):
        self.m_assertion:Assertion = None
        self.m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]] = []
        self.m_mode:GoalMode = GoalMode.FORMULATED
        self.m_expansions:typing.List = []
        self.m_committed_expansion = None
        self.m_metrics:typing.Dict = {}

class ExtendedGoalMemory():

    def __init__(self):
        self.m_goal_nodes:typing.List[GoalNode] = []

#goal_memory : List[GoalMemoryElement] = {}

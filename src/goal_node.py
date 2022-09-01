import sys
sys.path.append("/home/nrealus/perso/latest/prog/ai-planning-sandbox/python-playground7")

from enum import Enum
import typing
from src.base import Assertion

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
        #self.m_assertion:Assertion = None
        #self.m_constraints:typing.List[typing.Tuple[ConstraintType,typing.Any]] = []
        #self.m_constraint_network:ConstraintNetwork = ConstraintNetwork()
        self.m_mode:GoalMode = GoalMode.FORMULATED
        self.m_parent:GoalNode = None
        self.m_possible_expansions:typing.List = []
        self.m_committed_expansion = None
        self.m_metrics:typing.Dict = {}


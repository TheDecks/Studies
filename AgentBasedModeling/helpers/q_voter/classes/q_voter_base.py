import abc
from typing import Dict, Hashable, Optional

import networkx as nx


class QVoterBase(abc.ABC):

    _flexibility: float
    _p: float
    agent_opinion: Dict[Hashable, int]
    starting_opinion: Optional[int]

    def __init__(self, graph: nx.Graph, independent_opinion_switch: float,
                 independent_choice_parameter: float, influence_group_size: float = 4):
        """Create q voter model on graph. Graph nodes needs to be hashable.

        :param graph: networkx Graph object, whose nodes will be treated as agents.
        :param independent_opinion_switch: f parameter of q voter model.
        :param independent_choice_parameter: p parameter of q voter model.
        """
        self.graph = graph
        self.flexibility = independent_opinion_switch
        self.p = independent_choice_parameter
        self.agent_opinion = {}
        self.starting_opinion = None
        self.influence_group_size = influence_group_size

    @property
    def flexibility(self):
        return self._flexibility

    @flexibility.setter
    def flexibility(self, f: float):
        if f > 1:
            self._flexibility = 1
        elif f < 0:
            self._flexibility = 0
        else:
            self._flexibility = f

    @property
    def p(self):
        return self._flexibility

    @p.setter
    def p(self, p: float):
        if p > 1:
            self._p = 1
        elif p < 0:
            self._p = 0
        else:
            self._p = p

    @property
    def concentration(self):
        return sum([1 for _, opinion in self.agent_opinion.items() if opinion == self.starting_opinion])

    def initialize_agents(self, starting_opinion: int):
        self.agent_opinion = {agent: starting_opinion for agent in self.graph.nodes}
        self.starting_opinion = starting_opinion

    def vote_process(self):
        for _ in range(len(self.graph.nodes)):
            self._single_vote()

    def simulate(self, n_steps: int):
        for _ in range(n_steps):
            self.vote_process()

    @abc.abstractmethod
    def _single_vote(self): ...

import random
from typing import Dict, Hashable, List, Optional, Generator

import networkx as nx


class BassDiffusionModel:

    agent_adoption: Dict[Hashable, int]

    def __init__(
            self,
            graph: nx.Graph,
            innovation_coefficient: float,
            imitation_coefficient: float,
            influence_group_size: Optional[int] = None
    ):
        self.graph = graph
        self.p = innovation_coefficient
        self.q = imitation_coefficient
        self.agent_adoption = {}
        if influence_group_size is None:
            influence_group_size = len(self.graph.nodes)
        self.influence_group_size = influence_group_size
        self.__no_agents = len(self.graph.nodes)

    def release_innovation(self):
        self.agent_adoption = {agent: 1 if random.random() < self.p else 0 for agent in self.graph.nodes}

    @property
    def unadopted(self) -> List[Hashable]:
        return [agent for agent, adoption in self.agent_adoption.items() if adoption == 0]

    @property
    def adoption_rate(self) -> float:
        return sum([1 for _, adoption in self.agent_adoption.items() if adoption == 1]) / self.__no_agents

    def is_fully_adopted(self):
        for _, adoption in self.agent_adoption.items():
            if adoption == 0:
                return False
        return True

    def spread(self):
        new_adoption = self.agent_adoption.copy()
        for agent in self.unadopted:
            neighbours = list(self.graph.neighbors(agent))
            if len(neighbours) <= self.influence_group_size:
                influence_group = neighbours
            else:
                influence_group = random.sample(neighbours, self.influence_group_size)
            group_innovative_power = sum([self.agent_adoption[a] for a in influence_group]) / len(influence_group)
            if random.random() < group_innovative_power * self.q:
                new_adoption[agent] = 1
        self.agent_adoption = new_adoption

    def simulate(self, n_steps: Optional[int] = None) -> Generator[float, None, None]:
        yield self.adoption_rate
        times_run = 0
        while not self.is_fully_adopted():
            self.spread()
            a_rate = self.adoption_rate
            if a_rate == 0:
                break
            yield a_rate
            if n_steps is not None and times_run > n_steps:
                break
            times_run += 1

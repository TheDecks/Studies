import random
from typing import Dict, Hashable, List, Optional, Generator, Tuple

import networkx as nx


class BassDiffusionModelForce:

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
        self.agent_adoption = {agent: 0 for agent in self.graph.nodes}

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

    def spread(self) -> Tuple[float, float]:
        new_adoption = self.agent_adoption.copy()
        by_innovation = 0
        by_imitation = 0
        for agent in self.unadopted:
            if random.random() < self.p:
                new_adoption[agent] = 1
                by_innovation += 1
                continue
            neighbours = list(self.graph.neighbors(agent))
            if len(neighbours) <= self.influence_group_size:
                influence_group = neighbours
            else:
                influence_group = random.sample(neighbours, self.influence_group_size)
            group_innovative_power = sum([self.agent_adoption[a] for a in influence_group]) / len(influence_group)
            if random.random() < group_innovative_power * self.q:
                new_adoption[agent] = 1
                by_imitation += 1
        self.agent_adoption = new_adoption
        return by_innovation, by_imitation

    def simulate(self, n_steps: Optional[int] = None) -> Generator[Tuple[float, float, float], None, None]:
        # yield self.adoption_rate, 0, 0
        times_run = 0
        while not self.is_fully_adopted():
            by_innovation, by_imitation = self.spread()
            a_rate = self.adoption_rate
            yield (a_rate, by_imitation, by_innovation)
            if n_steps is not None and times_run > n_steps:
                break
            times_run += 1

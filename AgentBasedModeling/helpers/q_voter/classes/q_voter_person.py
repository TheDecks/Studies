import random
from typing import Hashable, Dict

from AgentBasedModeling.helpers.q_voter.classes import q_voter_base


class QVoterPerson(q_voter_base.QVoterBase):

    agent_type: Dict[Hashable, str]

    def initialize_agents(self, starting_opinion: int):
        super().initialize_agents(starting_opinion)
        _independent = random.sample(self.graph.nodes, int(self._p * len(self.graph.nodes)))
        self.agent_type = {
            agent: 'independent' if agent in _independent else 'conformist' for agent in self.graph.nodes
        }

    def _single_vote(self):
        agent = random.choice(list(self.agent_opinion.keys()))
        if self.agent_type[agent] == 'independent':
            if random.random() < self._flexibility:
                self.agent_opinion[agent] *= -1
            return
        neighbours = list(self.graph.neighbors(agent))
        if len(neighbours) < self.influence_group_size:
            influence_group = neighbours
        else:
            influence_group = random.sample(neighbours, self.influence_group_size)
        influence_score = sum([self.agent_opinion[agent] for agent in influence_group])
        if influence_score == self.starting_opinion * len(influence_group):
            self.agent_opinion[agent] = self.starting_opinion
        elif influence_score == -1 * self.starting_opinion * len(influence_group):
            self.agent_opinion[agent] = -1 * self.starting_opinion

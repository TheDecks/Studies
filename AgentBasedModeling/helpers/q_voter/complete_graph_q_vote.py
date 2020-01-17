import random


class CompleteGraphQVote:

    def __init__(self, agent_number: int, independent_opinion_switch: float,
                 independent_choice_parameter: float, influence_group_size: float = 4):
        self.agents = agent_number
        self.flexibility = independent_opinion_switch
        self.p = independent_choice_parameter
        self.influence_group_size = influence_group_size
        self.positives = self.agents

    def vote_process(self):
        for _ in range(self.agents):
            self._single_vote()

    def simulate(self, n_steps: int):
        for _ in range(n_steps):
            self.vote_process()

    def _single_vote(self):
        agent_opinion = 1 if random.random() < self.positives / self.agents else -1
        new_opinion = None
        if random.random() < self.p:
            if random.random() < self.flexibility:
                new_opinion = -1 * agent_opinion
        else:
            influence_group_opinion = self.__get_influence_group_opinion(is_agent_positive=agent_opinion == 1)
            if influence_group_opinion is not None:
                new_opinion = influence_group_opinion
        if new_opinion is not None:
            if new_opinion != agent_opinion:
                if new_opinion == 1:
                    self.positives += 1
                else:
                    self.positives -= 1

    def __get_influence_group_opinion(self, is_agent_positive: bool):
        checked = 0
        opinion = None
        curr_positives = self.positives - int(is_agent_positive)
        while checked < self.influence_group_size:
            this_agent_opinion = 1 if random.random() < curr_positives / (self.agents - 1 - checked) else -1
            if opinion is None:
                opinion = this_agent_opinion
            elif this_agent_opinion != opinion:
                return None
            else:
                checked += 1
                curr_positives -= int(this_agent_opinion == 1)
        return opinion

    @property
    def concentration(self):
        return self.positives

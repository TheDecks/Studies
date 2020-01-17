from typing import List

import networkx as nx
from AgentBasedModeling.helpers.q_voter.classes import q_voter_situation, q_voter_person, q_voter_base
from AgentBasedModeling.helpers.q_voter import complete_graph_q_vote
from AgentBasedModeling.lists.list7 import flexibility_probability_concentration_plot as fpc


def q_vote_complete_graph(
        no_agents: int,
        probabilities: List[float],
        flexibilities: List[float],
        mc_tries: int,
        n_steps: int,
        influence_size: int = 4,
        q_voter_class: type = q_voter_situation.QVoterSituation
):
    complete_graph = nx.complete_graph(n=no_agents)

    argument_no_1 = complete_graph if issubclass(q_voter_class, q_voter_base.QVoterBase) else no_agents

    flex_prob_con = {}

    for f in flexibilities:
        print(f"f={f}:")
        this_prob_con = {'p': [], 'concentration': []}
        flex_prob_con[f] = this_prob_con
        for p in probabilities:
            print(f"p={p}:")
            this_con = 0
            for i in range(mc_tries):
                # print(i)
                q_vote = q_voter_class(argument_no_1, f, p, influence_size)
                if issubclass(q_voter_class, q_voter_base.QVoterBase):
                    q_vote.initialize_agents(starting_opinion=1)
                q_vote.simulate(n_steps)
                this_con += q_vote.concentration / no_agents
            this_con /= mc_tries
            this_prob_con['p'].append(p)
            this_prob_con['concentration'].append(this_con)

    return flex_prob_con


if __name__ == "__main__":
    voters = [q_voter_situation.QVoterSituation, q_voter_person.QVoterPerson, complete_graph_q_vote.CompleteGraphQVote]
    voter = voters[2]
    agents = 100
    no_prob = 20
    prob = [i / no_prob for i in range(no_prob)]
    flex = [0.1, 0.2, 0.3, 0.4, 0.5]
    mc = 100
    n = 400
    influence = 4
    flex_prob_concentration = q_vote_complete_graph(agents, prob, flex, mc, n, influence, voter)
    fpc.flexibility_probability_concentration_plot(flex_prob_concentration)
    fpc.plt.show()

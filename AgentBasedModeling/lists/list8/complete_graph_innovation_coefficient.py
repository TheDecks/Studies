import networkx as nx

from AgentBasedModeling.helpers.bass_diffusion.bass_diffusion_model import BassDiffusionModel
from AgentBasedModeling.lists.list8 import labeler_plot

ps = [(i + 1) / 8 for i in range(8)]

complete_graph = nx.complete_graph(1000)

q = 0.38

prob_adoption_rate = {}

mc_steps = 50

for p in ps:
    print(f'p={p}')
    max_steps = 0
    all_runs = []
    for _ in range(mc_steps):
        this_ars = []
        bd = BassDiffusionModel(complete_graph, p, q)
        bd.release_innovation()
        for ar in bd.simulate():
            this_ars.append(ar)
        if len(this_ars) > max_steps:
            max_steps = len(this_ars)
        all_runs.append(this_ars)
    for ar_list in all_runs:
        ar_list += [1] * (max_steps - len(ar_list))
    averaged = []
    for i in range(max_steps):
        averaged.append(sum([run[i] for run in all_runs]) / mc_steps)
    prob_adoption_rate[p] = averaged

f, a = labeler_plot.labeler_plot(prob_adoption_rate, 'p')
a.set_title(f'Adoption rate evolution, CG(1000). q={q}, ig=1000, p=innovation rate')
labeler_plot.plt.show()

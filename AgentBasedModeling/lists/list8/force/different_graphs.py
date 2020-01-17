import networkx as nx

from AgentBasedModeling.helpers.bass_diffusion.bass_diffusion_model import BassDiffusionModel
from AgentBasedModeling.lists.list8 import labeler_plot


complete_graph = nx.complete_graph(1000)
ba_graph = nx.barabasi_albert_graph(1000, 10)
ws_graph = nx.watts_strogatz_graph(1000, 10, 0.3)
random_graph = nx.gnp_random_graph(1000, 0.3)
while not nx.is_connected(random_graph):
    random_graph = nx.gnp_random_graph(1000, 0.3)

labels_graphs = {
    'CG(1000)': complete_graph,
    'BA(1000, 10)': ba_graph,
    'WS(1000, 10, 0.3)': ws_graph,
    'RG(1000, 0.3)': random_graph
}

p = 0.03
q = 0.38

prob_adoption_rate = {}

mc_steps = 50

for label, graph in labels_graphs.items():
    print(f'graph={label}')
    max_steps = 0
    all_runs = []
    for _ in range(mc_steps):
        this_ars = []
        bd = BassDiffusionModel(graph, p, q)
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
    prob_adoption_rate[label] = averaged

f, a = labeler_plot.labeler_plot(prob_adoption_rate, 'graph')
a.set_title(f'Adoption rate evolution for different graphs, p={p}, q={q}, ig=1000')
labeler_plot.plt.show()

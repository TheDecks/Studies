import networkx as nx

from AgentBasedModeling.helpers.bass_diffusion.bass_diffusion_model_force import BassDiffusionModelForce
from AgentBasedModeling.lists.list8 import labeler_plot
from AgentBasedModeling.lists.list8.force import labeler_plot as lp

ps = [(i + 1) / 8 for i in range(8)]

complete_graph = nx.complete_graph(1000)

q = 0.38

prob_adoption_rate = {}
prob_imitation = {}
prob_innovation = {}

mc_steps = 50

for p in ps:
    print(f'p={p}')
    max_steps = 0
    all_runs = []
    all_runs_innovation = []
    all_runs_imitation = []
    for _ in range(mc_steps):
        this_ars = []
        this_innovation = []
        this_imitation = []
        bd = BassDiffusionModelForce(complete_graph, p, q)
        for ar, innovation, imitation in bd.simulate():
            this_ars.append(ar)
            this_innovation.append(innovation)
            this_imitation.append(imitation)
        if len(this_ars) > max_steps:
            max_steps = len(this_ars)
        all_runs.append(this_ars)
        all_runs_imitation.append(this_imitation)
        all_runs_innovation.append(this_innovation)
    for ar_list, innov_list, imit_list in zip(all_runs, all_runs_innovation, all_runs_imitation):
        ar_list += [1] * (max_steps - len(ar_list))
        innov_list += [1] * (max_steps - len(innov_list))
        imit_list += [1] * (max_steps - len(imit_list))
    averaged = []
    averaged_innovation = []
    averaged_imitation = []
    for i in range(max_steps):
        averaged.append(sum([run[i] for run in all_runs]) / mc_steps)
        averaged_imitation.append(sum([run[i] for run in all_runs_imitation]) / mc_steps)
        averaged_innovation.append(sum([run[i] for run in all_runs_innovation]) / mc_steps)
    prob_adoption_rate[p] = averaged
    prob_imitation[p] = averaged_imitation
    prob_innovation[p] = averaged_innovation

f, a = labeler_plot.labeler_plot(prob_adoption_rate, 'p')
a.set_title(f'Adoption rate evolution, CG(1000). q={q}, ig=1000, p=innovation rate')
labeler_plot.plt.show()

f, a = lp.labeler_plot_2(prob_imitation, prob_innovation, 'ig')
a.set_title(f'New adopters, CG(1000). q={q}')
labeler_plot.plt.show()

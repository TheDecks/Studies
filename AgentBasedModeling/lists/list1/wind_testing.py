from AgentBasedModeling.helpers.burning import wind
import matplotlib.pyplot as plt

import AgentBasedModeling.helpers.burning.forest_fire_model as ffm


def change_wind(direction: float, power: float, randomize: bool):
    wind.Wind().power = power
    wind.Wind().direction = direction
    wind.Wind().is_state_random = randomize


def process_forest(fire: ffm.ForestFireModel):
    fire.start_fire()
    fire.burn()


lattice_size = 50

probs = [p / 20 for p in range(20)]

# # percolation
#
# fig = plt.figure(figsize=(10, 8))
# ax = fig.add_subplot()
#
# perc_probs_no_wind = []
# perc_probs_right = []
# perc_probs_top = []
# perc_probs_left = []
# perc_probs_bottom = []
#
# for p in probs:
#
#     print(p)
#
#     counter_no_wind = 0
#     counter_right = 0
#     counter_top = 0
#     counter_left = 0
#     counter_bottom = 0
#
#     for i in range(100):
#
#         fir = ffm.ForestFireModel(lattice_size, p, None)
#         fir.create_cells()
#         fir.plant_trees()
#
#         change_wind(0, 0, False)  # no wind
#         process_forest(fir)
#         counter_no_wind += fir.is_top_hit
#         change_wind(0, 1, False)  # right
#         fir.restore()
#         process_forest(fir)
#         counter_right += fir.is_top_hit
#         change_wind(90, 1, False)  # top
#         fir.restore()
#         process_forest(fir)
#         counter_top += fir.is_top_hit
#         change_wind(180, 1, False)  # left
#         fir.restore()
#         process_forest(fir)
#         counter_left += fir.is_top_hit
#         change_wind(270, 1, False)  # bottom
#         fir.restore()
#         process_forest(fir)
#         counter_bottom += fir.is_top_hit
#
#     perc_probs_no_wind.append(counter_no_wind / 100)
#     perc_probs_right.append(counter_right / 100)
#     perc_probs_top.append(counter_top / 100)
#     perc_probs_left.append(counter_left / 100)
#     perc_probs_bottom.append(counter_bottom / 100)
#
#
# ax.plot(probs, perc_probs_no_wind, label='no wind')
# ax.plot(probs, perc_probs_right, label='to right')
# ax.plot(probs, perc_probs_top, label='to top')
# ax.plot(probs, perc_probs_left, label='to left')
# ax.plot(probs, perc_probs_bottom, label='to bottom')
#
# ax.legend()
# ax.set_title('Percolation probability for different winds.')
# ax.set_xlabel('plant probability')
# ax.set_ylabel('percolation probability')
#
# fig.savefig('wind_percolation_compare.png')

# avg biggest cluster

fig = plt.figure(figsize=(10, 8))
ax = fig.add_subplot()

cluster_sizes_no_wind = []
cluster_sizes_right = []
cluster_sizes_top = []
cluster_sizes_left = []
cluster_sizes_bottom = []

for p in probs:

    print(p)

    counter_no_wind = 0
    counter_right = 0
    counter_top = 0
    counter_left = 0
    counter_bottom = 0

    for i in range(100):

        fir = ffm.ForestFireModel(lattice_size, p, None)
        fir.create_cells()
        fir.plant_trees()

        change_wind(0, 0, False)  # no wind
        process_forest(fir)
        counter_no_wind += fir.find_biggest_cluster_by_me()
        change_wind(0, 1, False)  # right
        fir.restore()
        process_forest(fir)
        counter_right += fir.find_biggest_cluster_by_me()
        change_wind(90, 1, False)  # top
        fir.restore()
        process_forest(fir)
        counter_top += fir.find_biggest_cluster_by_me()
        change_wind(180, 1, False)  # left
        fir.restore()
        process_forest(fir)
        counter_left += fir.find_biggest_cluster_by_me()
        change_wind(270, 1, False)  # bottom
        fir.restore()
        process_forest(fir)
        counter_bottom += fir.find_biggest_cluster_by_me()

    cluster_sizes_no_wind.append(counter_no_wind / 100)
    cluster_sizes_right.append(counter_right / 100)
    cluster_sizes_top.append(counter_top / 100)
    cluster_sizes_left.append(counter_left / 100)
    cluster_sizes_bottom.append(counter_bottom / 100)


ax.plot(probs, cluster_sizes_no_wind, label='no wind')
ax.plot(probs, cluster_sizes_right, label='to right')
ax.plot(probs, cluster_sizes_top, label='to top')
ax.plot(probs, cluster_sizes_left, label='to left')
ax.plot(probs, cluster_sizes_bottom, label='to bottom')

ax.legend()
ax.set_title('Biggest cluster size for different winds.')
ax.set_xlabel('plant probability')
ax.set_ylabel('percolation probability')

fig.savefig('wind_biggest_cluster_compare.png')
from AgentBasedModeling.helpers.nagel_schreckenberg.freeway import Freeway
import matplotlib.pyplot as plt

ps = [0, 0.1, 0.2, 0.3]
qs = [(i + 1)/100 for i in range(99)]
step_limit = 30
fig = plt.figure()
ax = fig.add_subplot()
for p in ps:
    print(p)
    velocities = []
    for q in qs:
        print(q)
        f = Freeway(p, q, 1000, 1, 5, False, False)
        f.build_lanes()
        f.release_the_cars(1)
        f.run(50)
        velocities.append(f.mean_velocity)
    ax.plot(qs, velocities, label=f"{p}")

ax.legend()

plt.show()
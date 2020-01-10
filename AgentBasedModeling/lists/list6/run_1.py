from AgentBasedModeling.helpers.reynolds import reynolds_model as rm

model = rm.ReynoldsModel(50, avoid_distance=3)
model.setup_plotting()
model.add_boids(100, 3, 14/8 * 3.1415)
model.simulate(100, True)

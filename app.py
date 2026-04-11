from model import EpidemicModel

population = 50
grid_size = 20
infection_prob = 0.2
recovery_time = 10
steps = 10

model = EpidemicModel(
    population,
    grid_size,
    grid_size,
    infection_prob,
    recovery_time
)

for step in range(steps):
    print(f"Step: {step}")
    model.step()
    data = model.datacollector.get_model_vars_dataframe()
    print(data.iloc[-1])
    print("---------------------------")

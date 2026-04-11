from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agent import PersonAgent
import random


def count_state(model, state):
    return sum(1 for agent in model.scheduler.agents if agent.state == state)


class EpidemicModel(Model):
    def __init__(self, n, width, height, infection_prob, recovery_time):
        super().__init__()

        self.num_agents = n
        self.width = width
        self.height = height
        self.infection_prob = infection_prob
        self.recovery_time = recovery_time

        self.grid = MultiGrid(width, height, torus=True)
        self.scheduler = RandomActivation(self)

        for i in range(self.num_agents):
            agent = PersonAgent(i, self)
            self.scheduler.add(agent)

            x = random.randrange(self.width)
            y = random.randrange(self.height)
            self.grid.place_agent(agent, (x, y))

        patient_zero = random.choice(self.scheduler.agents)
        patient_zero.state = "I"

        self.datacollector = DataCollector(
            model_reporters={
                "Susceptible": lambda m: count_state(m, "S"),
                "Infected": lambda m: count_state(m, "I"),
                "Recovered": lambda m: count_state(m, "R"),
            }
        )

        self.datacollector.collect(self)

    def step(self):
        self.scheduler.step()
        self.datacollector.collect(self)

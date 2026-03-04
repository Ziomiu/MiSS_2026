from mesa import Agent
import random

from model import EpidemicModel


class PersonAgent(Agent):
    def __init__(self, unique_id, model: EpidemicModel):
        super().__init__(unique_id, model)
        # Just for type hints
        self.model: EpidemicModel = model

        self.state = "S"
        self.infection_time = 0

    def move(self):
        possible_steps = self.model.grid.get_neighborhood(
            self.pos,
            moore=True,
            include_center=False
        )
        new_position = random.choice(possible_steps)
        self.model.grid.move_agent(self, new_position)

    def infect_neighbors(self):
        neighbors = self.model.grid.get_cell_list_contents(
            self.model.grid.get_neighborhood(
                self.pos,
                moore=True,
                include_center=False
            )
        )

        for agent in neighbors:
            if agent.state == "S":
                if random.random() < self.model.infection_prob:
                    agent.state = "I"

    def step(self):
        self.move()

        if self.state == "I":
            self.infect_neighbors()
            self.infection_time += 1

            if self.infection_time >= self.model.recovery_time:
                self.state = "R"

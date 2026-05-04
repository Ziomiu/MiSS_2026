from mesa import Agent, Model
import random


class BasePersonAgent(Agent):
    def __init__(self, unique_id, model: Model):
        super().__init__(unique_id, model)
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
                include_center=True
            )
        )
        for agent in neighbors:
            if agent.state == "S" and random.random() < self.model.infection_prob:
                self._expose(agent)

    def _expose(self, agent):
        agent.state = "I"

    def step(self):
        self.move()
        if self.state == "I":
            self.infect_neighbors()
            self.infection_time += 1
            if self.infection_time >= self.model.recovery_time:
                self.state = "R"

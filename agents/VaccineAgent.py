from agents.BasePersonAgent import BasePersonAgent
import random


class VaccineAgent(BasePersonAgent):
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
            elif (
                agent.state == "P"
                and random.random() < (1 - 0.01 * self.model.transmission_rate_reduction) * self.model.infection_prob
            ):
                self._expose(agent)

    def _expose(self, agent):
        agent.state = "I"
        agent.infection_time = 0

    def step(self):
        self.move()
        if self.state == "I":
            self.infect_neighbors()
            self.infection_time += 1
            if self.infection_time >= self.model.recovery_time:
                self.state = "P"

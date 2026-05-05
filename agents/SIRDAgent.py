from agents.BasePersonAgent import BasePersonAgent
import random


class SIRDAgent(BasePersonAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.dead = False

    def _die(self):
        self.state = "D"
        self.dead = True

    def move(self):
        if not self.dead:
            super().move()

    def step(self):
        self.move()

        if self.state == "I":
            self.infect_neighbors()
            self.infection_time += 1

            if random.random() < self.model.death_prob:
                self._die()
                return
            
            if self.infection_time >= self.model.recovery_time:
                self.state = "R"

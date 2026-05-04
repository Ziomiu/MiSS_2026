from agents.BasePersonAgent import BasePersonAgent
import random


class HospitalAgent(BasePersonAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.hospitalized = False

    def move(self):
        if not self.hospitalized:
            super().move()

    def infect_neighbors(self):
        if not self.hospitalized:
            super().infect_neighbors()

    def _try_hospitalize(self):
        if (
            not self.hospitalized
            and self.model.hospital_current < self.model.hospital_capacity
            and random.random() < self.model.hospitalization_prob
        ):
            self.hospitalized = True
            self.state = "H"
            self.model.hospital_current += 1

    def step(self):
        self.move()
        if self.state == "I":
            self.infect_neighbors()
            self._try_hospitalize()
            self.infection_time += 1
            if self.infection_time >= self.model.recovery_time:
                self.state = "R"
        elif self.state == "H":
            self.infection_time += 1
            if self.infection_time >= self.model.recovery_time:
                self.model.hospital_current -= 1
                self.hospitalized = False
                self.state = "R"

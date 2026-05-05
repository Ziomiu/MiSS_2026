from agents.BasePersonAgent import BasePersonAgent


class SEIRAgent(BasePersonAgent):
    def _expose(self, agent):
        agent.state = "E"
        agent.infection_time = 0

    def step(self):
        self.move()

        if self.state == "E":
            self.infection_time += 1
            if self.infection_time >= self.model.exposure_time:
                self.state = "I"
                self.infection_time = 0
        elif self.state == "I":
            self.infect_neighbors()
            self.infection_time += 1
            if self.infection_time >= self.model.recovery_time:
                self.state = "R"

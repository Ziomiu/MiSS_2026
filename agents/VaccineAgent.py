from agents.BasePersonAgent import BasePersonAgent


class VaccineAgent(BasePersonAgent):
    def step(self):
        if self.state == "V":
            return
        super().step()

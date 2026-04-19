from models.BaseEpidemicModel import BaseEpidemicModel,count_state
from agents.VaccineAgent import VaccineAgent
import random


class VaccineModel(BaseEpidemicModel):
    """
    Po `vaccination_start` krokach od pierwszego zarażenia
    w każdym kroku szczepimy losowo `vaccination_rate` agentów.
    """

    agent_class = VaccineAgent

    def _configure(self, vaccination_start=10, vaccination_rate=3, **kwargs):
        self.vaccination_start = vaccination_start
        self.vaccination_rate = vaccination_rate
        self._steps_since_first_infection = 0
        self._vaccination_active = False

    def _extra_reporters(self):
        return {"Vaccinated": lambda m: count_state(m, "V")}

    def _vaccinate(self):
        susceptible = [a for a in self.scheduler.agents if a.state == "S"]
        to_vaccinate = random.sample(
            susceptible,
            min(self.vaccination_rate, len(susceptible)),
        )
        for agent in to_vaccinate:
            agent.state = "V"

    def step(self):
        self._steps_since_first_infection += 1
        if self._steps_since_first_infection >= self.vaccination_start:
            self._vaccinate()
        super().step()

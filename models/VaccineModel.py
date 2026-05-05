from models.BaseEpidemicModel import BaseEpidemicModel, count_state
from agents.VaccineAgent import VaccineAgent
from mesa.datacollection import DataCollector
import random


class VaccineModel(BaseEpidemicModel):
    """
    Po `vaccination_start` krokach od pierwszego zarażenia w każdym kroku szczepimy losowo
    `vaccination_rate` podatnych agentów. Agenci zaszczepieni oraz po przebyciu infekcji
    mają zmniejszone prawdopodobieństwo zakażenia, co jest określone poprzez parametr
    `transmission_rate_reduction`.
    """

    agent_class = VaccineAgent

    def _configure(self, vaccination_start=10, vaccination_rate=5, transmission_rate_reduction=90, **kwargs):
        self.vaccination_start = vaccination_start
        self.vaccination_rate = vaccination_rate
        self.transmission_rate_reduction = transmission_rate_reduction
        self._steps_since_first_infection = 0

    def _extra_reporters(self):
        return {"Partially immune": lambda m: count_state(m, "P")}
    
    def _init_datacollector(self):
        base_reporters = {
            "Susceptible": lambda m: count_state(m, "S"),
            "Infected": lambda m: count_state(m, "I")
        }
        base_reporters.update(self._extra_reporters())
        self.datacollector = DataCollector(model_reporters=base_reporters)

    def _vaccinate(self):
        susceptible = [a for a in self.scheduler.agents if a.state == "S"]
        to_vaccinate = random.sample(
            susceptible,
            min(self.vaccination_rate, len(susceptible))
        )
        for agent in to_vaccinate:
            agent.state = "P"

    def step(self):
        self._steps_since_first_infection += 1
        if self._steps_since_first_infection >= self.vaccination_start:
            self._vaccinate()
        super().step()

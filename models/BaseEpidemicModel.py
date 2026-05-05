from mesa import Model
from mesa.time import RandomActivation
from mesa.space import MultiGrid
from mesa.datacollection import DataCollector
from agents.BasePersonAgent import BasePersonAgent
import random


def count_state(model, state):
    return sum(1 for a in model.scheduler.agents if a.state == state)


class BaseEpidemicModel(Model):
    """
    Wspólna logika dla wszystkich wariantów modelu:
    - inicjalizacja siatki i harmonogramu,
    - rozmieszczenie agentów,
    - wyznaczenie pacjenta zero,
    - kolekcja danych (S, I, R).

    Podklasy przekazują klasę agenta przez `agent_class`
    i mogą rozszerzyć `_extra_reporters()` o dodatkowe serie.
    """

    agent_class = None

    def __init__(self, n, width, height, infection_prob, recovery_time, **kwargs):
        super().__init__()

        self.num_agents = n
        self.infection_prob = infection_prob
        self.recovery_time = recovery_time

        self._configure(**kwargs)

        self.grid = MultiGrid(width, height, torus=True)
        self.scheduler = RandomActivation(self)

        self._init_grid(width, height)
        self._init_patient_zero()
        self._init_datacollector()
        self.datacollector.collect(self)

    def _configure(self, **kwargs):
        pass

    def _make_agent(self, agent_id):
        if self.agent_class is None:
            self.agent_class = BasePersonAgent
        return self.agent_class(agent_id, self)

    def _extra_reporters(self):
        return {}

    def _init_grid(self, width, height):
        for i in range(self.num_agents):
            agent = self._make_agent(i)
            self.scheduler.add(agent)
            self.grid.place_agent(agent, (
                random.randrange(width),
                random.randrange(height)
            ))

    def _init_patient_zero(self):
        patient_zero = random.choice(self.scheduler.agents)
        patient_zero.state = "I"

    def _init_datacollector(self):
        base_reporters = {
            "Susceptible": lambda m: count_state(m, "S"),
            "Infected": lambda m: count_state(m, "I"),
            "Recovered": lambda m: count_state(m, "R")
        }
        base_reporters.update(self._extra_reporters())
        self.datacollector = DataCollector(model_reporters=base_reporters)

    def step(self):
        self.scheduler.step()
        self.datacollector.collect(self)

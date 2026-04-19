from models.BaseEpidemicModel import BaseEpidemicModel, count_state
from agents.HospitalAgent import HospitalAgent


class HospitalModel(BaseEpidemicModel):
    """
    Część zarażonych agentów trafia do szpitala, dlatego nie zarażają i nie ruszają się.
    Szpital ma ograniczoną pojemność.
    """

    agent_class = HospitalAgent

    def _configure(self, hospital_capacity=10, hospitalization_prob=0.1, **kwargs):
        self.hospital_capacity = hospital_capacity
        self.hospitalization_prob = hospitalization_prob
        self.hospital_current = 0

    def _extra_reporters(self):
        return {
            "Hospitalized": lambda m: count_state(m, "H"),
            "HospitalLoad": lambda m: m.hospital_current,
        }

from models.BaseEpidemicModel import BaseEpidemicModel, count_state
from agents.SIRDAgent import SIRDAgent


class SIRDModel(BaseEpidemicModel):
    """
    Zarażony agent w każdym kroku może umrzeć z prawdopodobieństwem `death_prob`.
    """

    agent_class = SIRDAgent

    def _configure(self, death_prob=0.05, **kwargs):
        self.death_prob = death_prob

    def _extra_reporters(self):
        return {"Deceased": lambda m: count_state(m, "D")}

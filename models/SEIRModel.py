from models.BaseEpidemicModel import BaseEpidemicModel, count_state
from agents.SEIRAgent import SEIRAgent


class SEIRModel(BaseEpidemicModel):
    """
    Zarażony agent przechodzi przez fazę inkubacji
    przez `exposure_time` kroków, zanim stanie się zakaźny.
    """

    agent_class = SEIRAgent
    
    def _configure(self, exposure_time=7, **kwargs):
        self.exposure_time = exposure_time

    def _extra_reporters(self):
        return {"Exposed": lambda m: count_state(m, "E")}

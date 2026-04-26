from models.BaseEpidemicModel import BaseEpidemicModel
from agents.FriendGroupAgent import FriendGroupAgent
import random


class FriendGroupModel(BaseEpidemicModel):
    """
    Każdy z zarażonych agentów przynależy do pewnej grupy znajomych.
    Agenci w obrębie grupy przyjaciół co ustaloną liczbę kroków `meeting_cooldown` dążą do spotkania
    ze znajomymi, które trwa `meeting_time` kroków i zaczyna się, gdy jest obecna ponad połowa grupy.
    Podczas spotkania agenci nie ruszają się.
    """

    agent_class = FriendGroupAgent

    def _configure(self, friend_groups_num=10, meeting_time=5, meeting_cooldown=20, **kwargs):
        self.friend_groups_num = friend_groups_num
        self.meeting_time = meeting_time
        self.meeting_cooldown = meeting_cooldown
        self._init_friend_groups()
    
    def _init_friend_groups(self):
        available_agents = list(self.scheduler.agents)

        for i in range(self.friend_groups_num):
            group_size = ((i+1) * self.num_agents) // self.friend_groups_num - \
                (i * self.num_agents) // self.friend_groups_num

            # Defining 'hotspot' for the group
            hotspot_x = random.randrange(self.grid.width)
            hotspot_y = random.randrange(self.grid.height)
            hotspot = (hotspot_x, hotspot_y)

            available_agents.sort(key=lambda a: -min(a.pos[0] - hotspot_x, a.pos[1] - hotspot_y))
            friend_group = available_agents[-group_size:]

            for agent in friend_group:
                agent.friend_group = set(friend_group)
                agent.hotspot = hotspot
                agent.meeting_time = self.meeting_time
                agent.meeting_cooldown = self.meeting_cooldown
                available_agents.pop()

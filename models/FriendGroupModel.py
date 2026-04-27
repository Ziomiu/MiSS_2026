from models.BaseEpidemicModel import BaseEpidemicModel
from agents.FriendGroupAgent import FriendGroupAgent
import random
import math


class FriendGroupModel(BaseEpidemicModel):
    """
    Każdy z zarażonych agentów przynależy do pewnej grupy znajomych.
    Agenci w obrębie grupy przyjaciół co ustaloną liczbę kroków `meeting_cooldown` dążą do spotkania
    ze znajomymi, które trwa `meeting_time` kroków i zaczyna się, gdy jest obecna cała grupa.
    Podczas spotkania agenci nie ruszają się.
    """

    agent_class = FriendGroupAgent

    def _configure(self, friend_groups_num=10, meeting_time=5, meeting_cooldown=20, **kwargs):
        self.friend_groups_num = friend_groups_num
        self.meeting_time = meeting_time
        self.meeting_cooldown = meeting_cooldown

    def _init_grid(self, width, height):
        i = 0
        radius_x = int(math.sqrt(width))
        radius_y = int(math.sqrt(height))
        group_sizes = self._split_agents_randomly()

        for group_size in group_sizes:
            # Defining 'hotspot' for the group
            hotspot_x = random.randrange(width)
            hotspot_y = random.randrange(height)
            hotspot = (hotspot_x, hotspot_y)
            friend_group = set()

            for _ in range(group_size):
                agent = self._make_agent(i)
                self.scheduler.add(agent)
                self.grid.place_agent(agent, (
                    random.randrange(max(0, hotspot_x - radius_x), min(width, hotspot_x + radius_x)),
                    random.randrange(max(0, hotspot_y - radius_y), min(height, hotspot_y + radius_y)),
                ))
                friend_group.add(agent)
                i += 1

            # Setting up agents
            for agent in friend_group:
                agent.friend_group = friend_group
                agent.hotspot = hotspot
                agent.meeting_time = self.meeting_time
                agent.meeting_cooldown = self.meeting_cooldown

    def _split_agents_randomly(self):
        group_sizes = [2] * self.friend_groups_num
        remainder = self.num_agents - (2 * self.friend_groups_num)

        for _ in range(remainder):
            idx = random.randrange(self.friend_groups_num)
            group_sizes[idx] += 1
            
        return group_sizes

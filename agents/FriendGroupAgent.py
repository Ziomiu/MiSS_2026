from agents.BasePersonAgent import BasePersonAgent
import random
import math


class FriendGroupAgent(BasePersonAgent):
    def __init__(self, unique_id, model):
        super().__init__(unique_id, model)
        self.friend_group = None
        self.hotspot = None
        self.meeting_time = 0
        self.current_time = -1
        self.meeting_cooldown = 0
        self.current_cooldown = 0

    def move(self):
        # There is a meeting - agent does not move
        if 0 <= self.current_time < self.meeting_time:
            self.current_time += 1
            return
        elif self.current_time == self.meeting_time:
            self.current_time = -1
            self.current_cooldown = self.meeting_cooldown
        else:
            self.current_cooldown = max(self.current_cooldown - 1, 0)

        if self.current_cooldown == 0: # agents want to meet with friends
            neighbors = self.model.grid.get_neighbors(self.pos, moore=True, include_center=True)
            num_friends = 0

            for friend in self.friend_group:
                if friend in neighbors:
                    num_friends += 1

            # Start the meeting if at least half the group is present
            if num_friends > len(self.friend_group) // 2:
                self.current_time = 0
                return

            dx = 1 if self.hotspot[0] > self.pos[0] else -1 if self.hotspot[0] < self.pos[0] else 0
            dy = 1 if self.hotspot[1] > self.pos[1] else -1 if self.hotspot[1] < self.pos[1] else 0
            new_pos = (self.pos[0] + dx, self.pos[1] + dy)

            if new_pos == (0, 0):
                super().move() # make a random move to not stand still
            else:
                self.model.grid.move_agent(self, new_pos)
        else: # there is a cooldown, make a random move
            super().move()

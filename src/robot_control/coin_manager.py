# coin_manager.py

from .robot_positions import PICK_POSES

class CoinManager:
    def __init__(self):
        # index of next coin for each stack
        self.next_index = [0, 0, 0]

    def get_next_pick_pose(self, stack_id: int):
        idx = self.next_index[stack_id]

        if idx >= len(PICK_POSES[stack_id]):
            raise RuntimeError(f"Stack {stack_id} is empty")

        pose = PICK_POSES[stack_id][idx]
        self.next_index[stack_id] += 1
        return pose

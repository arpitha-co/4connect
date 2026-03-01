# connect4_robot.py

try:
    from pyniryo import NiryoRobot
    _HAS_PYNIRYO = True
except Exception:
    NiryoRobot = None
    _HAS_PYNIRYO = False

from .coin_manager import CoinManager
from .robot_positions import DROP_POSES
from .robot_actions import RobotActions


class _MockNiryoRobot:
    """Lightweight mock of NiryoRobot to allow running without hardware."""
    def __init__(self, ip=None):
        self.ip = ip

    def calibrate_auto(self):
        print("[MockRobot] calibrate_auto() called")

    def move_to_home_pose(self):
        print("[MockRobot] move_to_home_pose() called")

    def move_pose(self, x, y, z, rx, ry, rz):
        print(f"[MockRobot] move_pose to ({x:.3f},{y:.3f},{z:.3f})")

    def grasp_with_tool(self):
        print("[MockRobot] grasp_with_tool() called")

    def release_with_tool(self):
        print("[MockRobot] release_with_tool() called")

    def close_connection(self):
        print("[MockRobot] close_connection() called")


class Connect4Robot:
    def __init__(self,
                 ip: str = "172.20.10.2",
                 safe_z: float = 0.35,
                 approach_dz: float = 0.06):

        # 1. Connect & init robot (try real robot, fallback to mock on error)
        self._connected_real_robot = False
        if _HAS_PYNIRYO:
            try:

                self.robot = NiryoRobot(ip)
                try:
                    self.robot.clear_collision_detected()
                    self.robot.calibrate_auto()
                except Exception:
                    pass
                try:
                    self.robot.move_to_home_pose()
                except Exception:
                    pass
                self._connected_real_robot = True
            except Exception as e:
                print(f"[connect4_robot] Could not connect to NiryoRobot: {e}")
                print("[connect4_robot] Falling back to MOCK mode.")
                self.robot = _MockNiryoRobot(ip)
        else:
            print("[connect4_robot] pyniryo not available — running in MOCK mode.")
            self.robot = _MockNiryoRobot(ip)

        # 2. Helpers
        self.actions = RobotActions(self.robot,
                                    safe_z=safe_z,
                                    approach_dz=approach_dz)
        self.coin_manager = CoinManager()

        # ROUND-ROBIN STACK ORDER
        self.stack_order = [0, 1, 2]       # cycle through these
        self.stack_pointer = 0             # which one to pick from next

    def _get_next_pick_pose(self):
        """
        Round-robin pick:
        - Try stack N (according to stack_order)
        - If empty → move to next stack in the cycle
        - Continue until all stacks empty
        """

        attempts = 0
        num_stacks = len(self.stack_order)

        while attempts < num_stacks:

            stack_id = self.stack_order[self.stack_pointer]

            try:
                # Successfully get a coin from this stack
                pose = self.coin_manager.get_next_pick_pose(stack_id)

                # Move pointer to next stack for the next pick
                self.stack_pointer = (self.stack_pointer + 1) % num_stacks

                return pose

            except RuntimeError:
                # Stack empty → skip to next
                self.stack_pointer = (self.stack_pointer + 1) % num_stacks
                attempts += 1

        # If we tried all stacks and all are empty:
        raise RuntimeError("All stacks are empty! No coins left.")

    def play_move(self, column: int):
        """
        Pick next coin in round-robin order and drop it in selected column.
        """
        if column < 0 or column >= len(DROP_POSES):
            raise ValueError(f"Column {column} out of range.")

        pick_pose = self._get_next_pick_pose()
        drop_pose = DROP_POSES[column]

        # Execute pick & place
        self.actions.pick(pick_pose)
        self.actions.place(drop_pose)

    def close(self):
        """Shutdown safely."""
        try:
            self.robot.move_to_home_pose()
        except Exception:
            pass
        try:
            self.robot.close_connection()
        except Exception:
            pass

# robot_actions.py

import time


class RobotActions:
    def __init__(self, robot, safe_z=0.40, approach_dz=0.08):
        """
        safe_z:      safe travel height above the board (e.g. 0.40 m)
        approach_dz: distance above the pick pose before going down (e.g. 0.08 m)
        """
        self.robot = robot
        self.SAFE_Z = safe_z
        self.APPROACH_DZ = approach_dz

    # --- Utility Movement ---
    def go_home(self):
        """Move robot safely to home pose."""
        self.robot.move_to_home_pose()

    def safe_above(self, pose):
        """Return a pose APPROACH_DZ above the given pose."""
        above = pose.copy()
        above[2] = pose[2] + self.APPROACH_DZ
        return above

    def safe_travel_pose(self, pose):
        """
        Return a pose with same X/Y/RPY as target,
        but Z set to global SAFE_Z (used for moving above board).
        """
        travel = pose.copy()
        travel[2] = self.SAFE_Z
        return travel

    # -------------------------
    #           PICK
    # -------------------------
    def pick(self, pose):
        """
        Full pick sequence (matches your script):
        home → above_pick (pose.z + APPROACH_DZ) → pick → lift_to_SAFE_Z
        """

        # A. Start from home for safety
        self.go_home()

        # B. Go above the coin (pose.z + APPROACH_DZ)
        above = self.safe_above(pose)
        self.robot.move_pose(*above)

        # C. Down to actual pick pose
        self.robot.move_pose(*pose)

        # D. Grasp (suction ON)
        self.robot.grasp_with_tool()
        time.sleep(1.0)   # same as in your script

        # E. Lift coin to SAFE_Z travel height
        lift = self.safe_travel_pose(pose)
        self.robot.move_pose(*lift)

    # -------------------------
    #           PLACE
    # -------------------------
    def place(self, pose):
        """
        Full drop sequence (matches your script):
        SAFE_Z over drop X/Y → down to drop → release → back to SAFE_Z → home

        Note: we do NOT use APPROACH_DZ above drop here; we come from SAFE_Z
        directly down to the drop height, just like in your working code.
        """

        # A. Move to correct X/Y at SAFE_Z (comes from above the board)
        travel_over = self.safe_travel_pose(pose)
        self.robot.move_pose(*travel_over)

        # B. Move straight down to exact drop Z
        self.robot.move_pose(*pose)

        # C. Release coin
        self.robot.release_with_tool()
        time.sleep(0.4)   # same as in your script

        # D. Move straight UP again to SAFE_Z above the board
        lift_up = self.safe_travel_pose(pose)
        self.robot.move_pose(*lift_up)

        # E. From safe height above board → go home
        self.go_home()

"""
Utility module allowing conversion of normalised motion values to hardware-specific ranges.
"""
from typing import Dict
from .common import normalise
from ..constants.control import CONTROL_NORM_IDLE, CONTROL_NORM_MAX, CONTROL_NORM_MIN
from ..constants.control import THRUSTER_MAX, THRUSTER_MIN, GRIPPER_MAX, GRIPPER_MIN, CORD_MAX, CORD_MIN


class Converter:
    """
    Static class acting as a namespace provider for converting the data.
    """

    @staticmethod
    def convert(motions: Dict[str, float]) -> Dict[str, int]:
        """
        Create the control data dictionary, built using the motions.
        """
        return {
            "T_HFP": Converter._thruster_hfp(motions),
            "T_HFS": Converter._thruster_hfs(motions),
            "T_HAP": Converter._thruster_hap(motions),
            "T_HAS": Converter._thruster_has(motions),
            "T_VFP": Converter._thruster_vfp(motions),
            "T_VFS": Converter._thruster_vfs(motions),
            "T_VAP": Converter._thruster_vap(motions),
            "T_VAS": Converter._thruster_vas(motions),
            "T_M": Converter._thruster_micro(motions),
            "M_C": Converter._cord(motions),
            "M_G": Converter._gripper(motions),
        }

    @staticmethod
    def _thruster_hfp(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for horizontal fore port thruster.
        """
        surge, yaw, sway = motions["surge"], motions["yaw"], motions["sway"]

        if surge and yaw:

            # If backwards, else forwards
            if surge < CONTROL_NORM_IDLE:
                value = -surge
            else:
                value = -yaw

        elif surge:
            value = -surge

        elif sway:
            value = sway

        elif yaw:
            value = -yaw

        else:
            value = CONTROL_NORM_IDLE

        return Converter._to_thruster_value(value)

    @staticmethod
    def _thruster_hfs(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for horizontal fore starboard thruster.
        """
        surge, yaw, sway = motions["surge"], motions["yaw"], motions["sway"]

        if surge and yaw:

            # If backwards, else forwards
            if surge < CONTROL_NORM_IDLE:
                value = -surge
            else:
                value = yaw

        elif surge:
            value = -surge

        elif sway:
            value = -sway

        elif yaw:
            value = yaw

        else:
            value = CONTROL_NORM_IDLE

        return Converter._to_thruster_value(value)

    @staticmethod
    def _thruster_hap(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for horizontal aft port thruster.
        """
        surge, yaw, sway = motions["surge"], motions["yaw"], motions["sway"]

        if surge and yaw:

            # If backwards, else forwards
            if surge < CONTROL_NORM_IDLE:
                value = -yaw
            else:
                value = surge

        elif surge:
            value = surge

        elif sway:
            value = sway

        elif yaw:
            value = yaw

        else:
            value = CONTROL_NORM_IDLE

        return Converter._to_thruster_value(value)

    @staticmethod
    def _thruster_has(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for vertical aft starboard thruster.
        """
        surge, yaw, sway = motions["surge"], motions["yaw"], motions["sway"]

        if surge and yaw:

            # If backwards, else forwards
            if surge < CONTROL_NORM_IDLE:
                value = yaw
            else:
                value = surge

        elif surge:
            value = surge

        elif sway:
            value = -sway

        elif yaw:
            value = -yaw

        else:
            value = CONTROL_NORM_IDLE

        return Converter._to_thruster_value(value)

    @staticmethod
    def _thruster_vfp(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for vertical fore port thruster.
        """
        heave, pitch, roll = motions["heave"], motions["pitch"], motions["roll"]

        if heave:
            value = heave

        elif pitch:
            value = -pitch

        elif roll:
            value = roll

        else:
            value = CONTROL_NORM_IDLE

        return Converter._to_thruster_value(value)

    @staticmethod
    def _thruster_vfs(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for vertical fore starboard thruster.
        """
        heave, pitch, roll = motions["heave"], motions["pitch"], motions["roll"]

        if heave:
            value = heave

        elif pitch:
            value = -pitch

        elif roll:
            value = -roll

        else:
            value = CONTROL_NORM_IDLE

        return Converter._to_thruster_value(value)

    @staticmethod
    def _thruster_vap(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for vertical aft port thruster.
        """
        heave, pitch, roll = motions["heave"], motions["pitch"], motions["roll"]

        if heave:
            value = heave

        elif pitch:
            value = pitch

        elif roll:
            value = roll

        else:
            value = CONTROL_NORM_IDLE

        return Converter._to_thruster_value(value)

    @staticmethod
    def _thruster_vas(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for vertical aft starboard thruster.
        """
        heave, pitch, roll = motions["heave"], motions["pitch"], motions["roll"]

        if heave:
            value = heave

        elif pitch:
            value = pitch

        elif roll:
            value = -roll

        else:
            value = CONTROL_NORM_IDLE

        return Converter._to_thruster_value(value)

    @staticmethod
    def _thruster_micro(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for micro ROV thruster.
        """
        micro = motions["micro"]

        value = micro if micro else CONTROL_NORM_IDLE

        return Converter._to_thruster_value(value)

    @staticmethod
    def _cord(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for cord control.
        """
        cord = motions["cord"]

        value = cord if cord else CONTROL_NORM_IDLE

        return int(normalise(value, CONTROL_NORM_MIN, CONTROL_NORM_MAX, CORD_MIN, CORD_MAX))

    @staticmethod
    def _gripper(motions: Dict[str, float]) -> int:
        """
        Hierarchical control for gripper control.
        """
        gripper = motions["gripper"]

        value = gripper if gripper else CONTROL_NORM_IDLE

        return int(normalise(value, CONTROL_NORM_MIN, CONTROL_NORM_MAX, GRIPPER_MIN, GRIPPER_MAX))

    @staticmethod
    def _to_thruster_value(value: float) -> int:
        """
        Change the normalised range into a hardware-specific range.
        """
        return int(normalise(value, CONTROL_NORM_MIN, CONTROL_NORM_MAX, THRUSTER_MIN, THRUSTER_MAX))

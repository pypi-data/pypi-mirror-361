from .high_level.hardware import HardwareRef


def get_object(object_name: str):
    return HardwareRef(object_name)

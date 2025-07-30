"""Helper functions for system detection and environment checks."""


def is_raspberry_pi():
    """Detect if the script is running on a Raspberry Pi."""
    try:
        with open("/proc/device-tree/model", "r") as f:
            return "Raspberry Pi" in f.read()
    except Exception:
        return False

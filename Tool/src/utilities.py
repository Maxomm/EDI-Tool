import os
import sys


def resource_path(relative_path):
    """Get absolute path to resource, works for dev and for PyInstaller"""

    try:
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        base_path = sys._MEIPASS
        relative_path = relative_path.split("/")[-1]
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

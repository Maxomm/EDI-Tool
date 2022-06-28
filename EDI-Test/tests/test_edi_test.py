import time

from edi_test import __version__
from src.edi_test.new_main import time_milliseconds


def test_version():
    assert __version__ == "0.1.0"


def test_time_milliseconds():
    assert time_milliseconds() == round(time.time() * 1000)

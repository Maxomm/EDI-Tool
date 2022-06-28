import time

from src.edi_test.new_main import time_milliseconds


def test_time_milliseconds():
    assert time_milliseconds() == round(time.time() * 1000)

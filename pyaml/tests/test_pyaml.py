import pyaml
from unittest import TestCase


class TestPyaml(TestCase):
    def test_dump_max_recusion(self):
        for i in range(0, 200):
            pyaml.dump({'a': 'b'})

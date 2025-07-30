import unittest
import numpy as np

import saftig as sg

from .test_filters import TestFilter

class TestLMSFilterC(unittest.TestCase, TestFilter):
    """ tests for the LeastMeanSquares filter implementation """
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        test_configurations = [
            {'normalized': True},
            {'normalized': True, 'coefficient_clipping': 2, 'step_scale': 0.5},
            {'normalized': False, 'step_scale': 0.001},
        ]
        self.set_target(sg.LMSFilterC, test_configurations)

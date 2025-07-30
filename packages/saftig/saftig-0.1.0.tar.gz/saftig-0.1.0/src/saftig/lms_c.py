""" faster LMS filter implemented in c """
from typing import Iterable
import numpy as np

#from ._lms_c import lms_step_c
from ._lms_c import LMS_C
from .common import FilterBase

class LMSFilterC(FilterBase):
    """LMS filter implementation in C (faster but harder to adjust)

    :param n_filter: Length of the FIR filter (how many samples are in the input window per output sample)
    :param idx_target: Position of the prediction
    :param n_channel: Number of witness sensor channels
    :param normalized: if True: NLMS, else LMS
    :param step_scale: the learning rate of the LMS filter

    >>> import saftig as sg
    >>> n_filter = 128
    >>> witness, target = sg.TestDataGenerator(0.1).generate(int(1e5))
    >>> filt = sg.LMSFilterC(n_filter, 0, 1)
    >>> filt.condition(witness, target)
    >>> prediction = filt.apply(witness, target) # check on the data used for conditioning
    >>> residual_rms = sg.RMS(target-prediction)
    >>> residual_rms > 0.05 and residual_rms < 0.15 # the expected RMS in this test scenario is 0.1
    True

    """
    filter_name = "LMS_C"

    def __init__(self,
                 n_filter:int,
                 idx_target:int,
                 n_channel:int,
                 step_scale:float=0.1,
                 normalized:bool=True,
                 coefficient_clipping:float|None=None):
        super().__init__(n_filter, idx_target, n_channel)
        self.filter = LMS_C(n_filter,
                            idx_target,
                            n_channel,
                            step_scale,
                            normalized,
                            np.nan if coefficient_clipping is None else coefficient_clipping)

    def reset(self) -> None:
        """ reset the filter coefficients to zero """
        raise RuntimeError("This is not implemented yet")

    def condition(self,
                  witness:Iterable[float]|Iterable[Iterable[float]],
                  target:Iterable[float]) -> bool:
        """ Use an input dataset to condition the filter

        :param witness: Witness sensor data
        :param target: Target sensor data
        """
        self.apply(witness, target, update_state=True)

    def apply(self,
              witness:Iterable[float]|Iterable[Iterable[float]],
              target:Iterable[float]=None,
              pad:bool=True,
              update_state:bool=False) -> Iterable[float]:
        """ Apply the filter to input data

        :param witness: Witness sensor data
        :param target: Target sensor data (is ignored)
        :param pad: if True, apply padding zeros so that the length matches the target signal

        :return: prediction
        """
        witness, target = self.check_data_dimensions(witness, target)
        assert target is not None, "Target data must be supplied"

        offset_target = self.n_filter - self.idx_target - 1
        pred_length = len(target) - self.n_filter + 1

        # iterate over data (the python loop is very slow)
        prediction = []
        for idx in range(0, pred_length):
            w_sel = witness[:,idx:idx+self.n_filter] # input to predcition

            pred = self.filter.step(w_sel, target[idx+offset_target])
            prediction.append(pred)

        prediction = np.array(prediction)
        if pad:
            prediction = np.concatenate([
                np.zeros(offset_target),
                prediction,
                np.zeros(len(target)-pred_length-offset_target)
                ])

        return prediction

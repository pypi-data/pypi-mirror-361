""" experiment in building a polynomial lms filter """

from typing import Iterable
import numpy as np

from .common import FilterBase


class PolynomialLMSFilter(FilterBase):
    r"""Experimental non-linear LMS-like filter implementation
    Implements: :math:`x[n] = \sum_p\sum_i\sum_t {w_i[n-t]}^pH_{it}` where p is the polynomial order, i the channel and t the index within the filter

    :param n_filter: Length of the FIR filter (how many samples are in the input window per output sample)
    :param idx_target: Position of the prediction
    :param n_channel: Number of witness sensor channels
    :param normalized: if True: NLMS, else LMS
    :param step_scale: the learning rate of the LMS filter
    :param order: polynomial order of the filter

    >>> import saftig as sg
    >>> n_filter = 128
    >>> witness, target = sg.TestDataGenerator(0.1).generate(int(1e5))
    >>> filt = sg.PolynomialLMSFilter(n_filter, 0, 1, step_scale=0.1, order=2, coefficient_clipping=4)
    >>> filt.condition(witness, target)
    >>> prediction = filt.apply(witness, target) # check on the data used for conditioning
    >>> residual_rms = sg.RMS((target-prediction)[1000:])
    >>> residual_rms > 0.05 and residual_rms < 0.15 # the expected RMS in this test scenario is 0.1
    True

    """

    #: The current FIR coefficients of the LMS filter
    filter_state:Iterable[Iterable[Iterable[float]]]|None = None
    filter_name = "PolyLMS"

    def __init__(self,
                 n_filter:int,
                 idx_target:int,
                 n_channel:int=1,
                 normalized:bool=True,
                 step_scale:float=0.5,
                 coefficient_clipping:float|None=None,
                 order:int=1):
        super().__init__(n_filter, idx_target, n_channel)
        self.normalized = normalized
        self.step_scale = step_scale
        self.coefficient_clipping = coefficient_clipping
        self.order = order

        assert self.step_scale > 0, "Step scale must be positive"
        assert self.coefficient_clipping is None or self.coefficient_clipping > 0, "coefficient_clipping must be positive"
        assert self.order > 0

        self.reset()

    def reset(self) -> None:
        """ reset the filter coefficients to zero """
        self.filter_state = np.zeros((self.order, self.n_channel, self.n_filter))

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
        :param update_state: if True, the filter state will be changed. If false, the filter state will remain

        :return: prediction
        """
        witness, target = self.check_data_dimensions(witness, target)
        assert target is not None, "Target data must be supplied"

        offset_target = self.n_filter - self.idx_target - 1
        pred_length = len(target) - self.n_filter + 1

        filter_state = self.filter_state if update_state else np.array(self.filter_state)

        # iterate over data (the python loop is very slow)
        prediction = []
        for idx in range(0, pred_length):
            # make prediction
            w_sel = witness[:,idx:idx+self.n_filter] # input to predcition
            pred = sum( np.einsum('ij,ij->', filter_state[i], w_sel**(i+1)) for i in range(self.order))
            err = target[idx+offset_target] - pred

            prediction.append(pred)

            # update filter
            if self.normalized:
                norm = np.einsum('ij,ij->', w_sel, w_sel)
                if norm < 0:
                    raise ValueError('Overflow! You are probably passing integers of insufficient precision to this function.')
                for i in range(self.order):
                    # NOTE: this might not be the correct/optimal normalization
                    filter_state[i] += 2*self.step_scale*err*w_sel**(i+1) / norm**((i+2)/2)
            else:
                for i in range(self.order):
                    filter_state[i] += 2*self.step_scale*err*w_sel**(i+1)

            if self.coefficient_clipping is not None:
                filter_state = np.clip(filter_state, -self.coefficient_clipping, self.coefficient_clipping)

        prediction = np.array(prediction)
        if pad:
            prediction = np.concatenate([
                np.zeros(offset_target),
                prediction,
                np.zeros(len(target)-pred_length-offset_target)
                ])

        return prediction

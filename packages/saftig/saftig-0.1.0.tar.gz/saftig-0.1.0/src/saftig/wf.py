""" Clasical static Wiener filter """
from typing import Union, Iterable
from warnings import warn

import numpy as np
from scipy.signal import correlate

from .common import FilterBase, make_2d_array

def mean_cross_correlation_offset(A, B, N, offset) -> Iterable[float]:
    """ estimate the cross-correlation between A and B """
    assert len(A) == len(B)
    assert offset < N

    if offset < N-1:
        return correlate(A, B[offset:-N+1+offset], mode='valid')
    return correlate(A, B[offset:], mode='valid')

def wf_calculate(witness:Iterable[float]|Iterable[Iterable[float]],
                 target:Iterable[float],
                 n_filter:int,
                 idx_target:int=0) -> Union[Iterable[Iterable[float]],bool]:
    """ caluclate the FIR coefficients for a wiener filter

    :param witness: Witness sensor data
    :param witness: Target sensor data
    :param n_filter: Length of the FIR filter (how many samples are in the input window per output sample)
    :param idx_target: offset of the prediction relative to the end of the array

    :return: filter coefficients, full_rank (bool)
    """
    target = np.array(target)
    witness = make_2d_array(witness)
    assert witness.shape[1] == target.shape[0], "Missmatch between witness and target data shape"
    assert n_filter <= target.shape[0], "Input data must be at least one filter length"

    # calculate input autocorrelation and cross-correlation to target
    R_ws = [mean_cross_correlation_offset(target, A, n_filter, idx_target) for A in witness] # R_ws[channel, time]
    R_ws = np.array(R_ws).flatten(order='C')

    def calc_r_matrix(A, B, n_filter):
        """ calculate the cross correlation matrix of a and b """
        cc = correlate(A, B[:-n_filter+1], mode='valid')
        return np.array([np.concatenate([cc[i::-1], cc[1:n_filter-i]]) for i in range(n_filter)])
    def calc_r_matrix_symmetric(A, B, n_filter):
        """ calculate the cross correlation matrix of a and b and average positive and negative lag
            to make the result symmetric (as is expected for an autocorrelation)
        """
        cc = correlate(A, B[n_filter:-n_filter], mode='valid')
        cc = np.concatenate([ [cc[n_filter]], (cc[n_filter+1:] + cc[n_filter-1::-1])/2 ])
        return np.array([np.concatenate([cc[i::-1], cc[1:n_filter-i]]) for i in range(n_filter)])

    if len(target) >= 3*n_filter: # using both sides is only possible if enough data is provided
        R_ww = np.block([[calc_r_matrix_symmetric(A, B, n_filter) for B in witness] for A in witness])
    else:
        R_ww = np.block([[calc_r_matrix(A, B, n_filter) for B in witness] for A in witness])

    # calculate pseudo-inverse correlation matrix of inputs and the filter coefficients
    # for some reason the scipy.linalg implementations were extremely slow on white noise test case => using numpy
    full_rank = bool(np.linalg.matrix_rank(R_ww, hermitian=True) == len(R_ww[0]))
    R_ww_inv = np.linalg.pinv(R_ww, hermitian=True)
    WFC = R_ww_inv.dot(R_ws)

    # unwrap into seperate FIR filters
    WFC = WFC.reshape((len(witness), n_filter))
    WFC = np.array([np.flip(i) for i in WFC])

    assert len(WFC[0]) == n_filter, "input data was to short resulting in an incompatible filter"

    return WFC, full_rank

def wf_apply(WFC:Iterable[Iterable[float]], witness:Iterable[Iterable[float]]) -> Iterable[Iterable[float]]:
    """apply the WF to witness data

        :param witness: Witness sensor data
        :param target: Target sensor data

        :return: prediction
    """
    assert len(witness[0]) >= len(WFC[0]), "Input minimum lenght is one filter length"
    witness = np.array(witness).astype(np.longdouble)
    return np.sum([correlate(A, WF, mode='valid') for A, WF in zip(witness, WFC)], axis=0)

class WienerFilter(FilterBase):
    """Satic Wiener filter implementation

    :param n_filter: Length of the FIR filter (how many samples are in the input window per output sample)
    :param idx_target: Position of the prediction
    :param n_channel: Number of witness sensor channels

    >>> import saftig as sg
    >>> n_filter = 128
    >>> witness, target = sg.TestDataGenerator(0.1).generate(int(1e5))
    >>> filt = sg.WienerFilter(n_filter, 0, 1)
    >>> _coefficients, full_rank = filt.condition(witness, target)
    >>> full_rank
    True
    >>> prediction = filt.apply(witness, target) # check on the data used for conditioning
    >>> residual_rms = sg.RMS(target-prediction)
    >>> residual_rms > 0.05 and residual_rms < 0.15 # the expected RMS in this test scenario is 0.1
    True

    """

    #: The FIR coefficients of the WF
    filter_state:Iterable[Iterable[float]]|None = None
    filter_name = "WF"

    def condition(self,
                  witness:Iterable[float]|Iterable[Iterable[float]],
                  target:Iterable[float]) -> bool:
        """ Use an input dataset to condition the filter

        :param witness: Witness sensor data
        :param target: Target sensor data
        """
        witness, target = self.check_data_dimensions(witness, target)

        self.filter_state, full_rank = wf_calculate(witness,
                                                    target,
                                                    self.n_filter,
                                                    idx_target=self.idx_target)

        if not full_rank:
            warn("Warning: Filter is not of full rank", RuntimeWarning)
        return self.filter_state, full_rank

    def apply(self,
              witness:Iterable[float]|Iterable[Iterable[float]],
              target:Iterable[float]=None,
              pad:bool=True,
              update_state:bool=False) -> Iterable[float]:
        """ Apply the filter to input data

        :param witness: Witness sensor data
        :param target: Target sensor data (is ignored)
        :param pad: if True, apply padding zeros so that the length matches the target signal
        :param update_state: ignored

        :return: prediction
        """
        witness, target = self.check_data_dimensions(witness, target)
        assert self.filter_state is not None, "The filter must be conditioned before calling apply()"

        prediction = wf_apply(self.filter_state, witness)
        if pad:
            prediction = np.concatenate([np.zeros(self.n_filter-1-self.idx_target), prediction, np.zeros(self.idx_target)])
        return prediction

"""Shared functionality for all other modules"""
from typing import Iterable

import numpy as np

def total_power(A:Iterable[float]) -> float:
    """calculate the total power of a signal (square or RMS)

    >>> import saftig, numpy
    >>> signal = numpy.ones(10) * 2
    >>> saftig.total_power(signal)
    4.0

    """
    return float(np.mean(np.square(A)))

def RMS(A:Iterable[float]) -> float:
    """ Calculate the root mean square value of an array """
	# float() is used to convert this into a standard float instead of a 0D numpy array
	# this simplifies writing doctests
    return float(np.sqrt(np.mean(np.square(A))))

def make_2d_array(A:Iterable|Iterable[Iterable]) -> np.array:
    """add a dimension to 1D arrays and leave 2D arrays as they are
    This is intended to allow 1D array input for single channel application

    :param A: input array

    :return: exteneded array

    :raises: ValueError if the input shape is not compatible

    >>> make_2d_array([1, 2])
    array([[1, 2]])

    >>> make_2d_array([[1, 2], [3, 4]])
    array([[1, 2],
           [3, 4]])

    """
    A = np.array(A)
    if len(A.shape) == 1:
        return np.array([A])
    if len(A.shape) == 2:
        return A
    raise ValueError("Input must be 1D or 2D array")


class FilterBase:
    """ common interface definition for Filter implementations

    :param n_filter: Length of the FIR filter
                     (how many samples are in the input window per output sample)
    :param idx_target: Position of the prediction
    :param n_channel: Number of witness sensor channels
    """
    filter_state = None
    filter_name:str|None = None

    def __init__(self, n_filter:int, idx_target:int, n_channel:int=1):
        self.n_filter = n_filter
        self.n_channel = n_channel
        self.idx_target = idx_target

        assert self.n_filter > 0, "n_filter must be a positive integer"
        assert self.n_channel > 0, "n_filter must be a positive integer"
        assert self.idx_target >= 0 and self.idx_target < self.n_filter, \
                "idx_target must not be negative and smaller than n_filter"
        assert self.filter_name is not None, "BaseFilter childs must set their name"

    def condition(self,
                  witness:Iterable[float]|Iterable[Iterable[float]],
                  target:Iterable[float]):
        """ Use an input dataset to condition the filter
        
        :param witness: Witness sensor data
        :param target: Target sensor data
        """
        # this should be implemented by the child class

    def apply(self,
              witness:Iterable[float]|Iterable[Iterable[float]],
              target:Iterable[float], pad:bool=True,
              update_state:bool=False) -> Iterable[float]:
        """ Apply the filter to input data
        
        :param witness: Witness sensor data
        :param target: Target sensor data
        :param pad: if True, apply padding zeros so that the length matches the target signal
        :param update_state: if True, the filter state will be changed. If false, the filter state will remain

        :return: prediction
        """
        # this should be implemented by the child class

    def check_data_dimensions(self,
                              witness:Iterable[float]|Iterable[Iterable[float]],
                              target:Iterable[float]) -> tuple[Iterable[Iterable[float]], Iterable[float]]:
        """Check the dimensions of the provided input data and apply make_2d_array()

        :param witness: Witness sensor data
        :param target: Target sensor data

        :return: data as (target, witness)

        :raises: AssertionError
        """
        target = np.array(target)
        witness = make_2d_array(witness)
        assert witness.shape[0] == self.n_channel, "witness data shape does not match configured channel count"
        assert target is None or target.shape[0] == witness.shape[1], "Missmatch between target and witness data shapes"

        return witness, target

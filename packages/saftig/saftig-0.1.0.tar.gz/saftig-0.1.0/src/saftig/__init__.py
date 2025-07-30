"""Static & Adaptive Filtering In Gravitational-wave-research
Implementations of prediction techniques with a unified interface.
"""
from .common import RMS, total_power
from .evaluation import (
    TestDataGenerator,
    residual_power_ratio,
    residual_amplitude_ratio,
    measure_runtime,
)

from .wf import WienerFilter
from .uwf import UpdatingWienerFilter
from .lms import LMSFilter
from .polylms import PolynomialLMSFilter

from .lms_c import LMSFilterC

#: A list of all filters for automated testing and comparisons
all_filters = [
    WienerFilter,
    UpdatingWienerFilter,
    LMSFilter,
    LMSFilterC,
    PolynomialLMSFilter,
]

from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from datetime import datetime
from qpace import Ctx, Backtest
from algoalpha import _lib
  


  
def __get_qpace_core_version__() -> str:
    """
    Version of qPACE core library used in compilation.
    """
    return _lib.get_core_version()
  
__checked_qpc_core__version__ = False
  
def __check__qpace_core_version__():
    global __checked_qpc_core__version__
    if not __checked_qpc_core__version__:
        __checked_qpc_core__version__ = True
        from qpace import __core__version__ as expected_core
        actual_core = __get_qpace_core_version__()
        if expected_core != actual_core:
            import warnings 
            warnings.warn(f"Script was compiled with qpace-core {expected_core}, but you have {actual_core} installed. This may cause issues. More: https://qpace.dev/faq#qpace-core-version-warning-from-script\nTry running `pip install qpace --upgrade` to fix this.")
  
__check__qpace_core_version__()


  
from . import intrinsics
from . import adaptive_schaff_trend_cycle
from . import amazing_oscillator
from . import exponential_trend
from . import supertrended_rsi
from . import triple_smoothed_signals

  
from dataclasses import dataclass
from typing import Optional, Union, Literal, TypedDict, Any, Tuple, List
from datetime import datetime
from qpace import Ctx, Backtest
from algoalpha import _lib
  
  

class MainAlert(TypedDict):
    time: datetime
    bar_index: int
    title: Optional[str]
    message: Optional[str]

class MainResultLocals(TypedDict):

    _initial: List[float]
    

    trend: List[int]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, exponentialRate: Optional[float] = None, initialDistance: Optional[float] = None, widthMultiplier: Optional[float] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_6569b6(ctx=ctx, _949_input_idHyNO=exponentialRate,_951_input_RMkWYh=initialDistance,_953_input_pbMnwS=widthMultiplier).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def _initial(self) -> float:
        return self.__inner._709__initial()
  

    @property
    def trend(self) -> int:
        return self.__inner._710_trend()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, exponentialRate: Optional[float] = None, initialDistance: Optional[float] = None, widthMultiplier: Optional[float] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_6569b6(ctx, _949_input_idHyNO=exponentialRate,_951_input_RMkWYh=initialDistance,_953_input_pbMnwS=widthMultiplier)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
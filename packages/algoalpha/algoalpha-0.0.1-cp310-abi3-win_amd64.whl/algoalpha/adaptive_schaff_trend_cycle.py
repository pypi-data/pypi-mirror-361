
  
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

    stc: List[float]
    

    macd: List[float]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, adaptiveLogicLength: Optional[int] = None, stcLength: Optional[int] = None, stcSensitivity: Optional[float] = None, macdFastLength: Optional[int] = None, macdSlowLength: Optional[int] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_470cff(ctx=ctx, _910_input_ZpfPzM=adaptiveLogicLength,_912_input_B08QUZ=stcLength,_914_input_fx5oTH=stcSensitivity,_916_input_btTAmK=macdFastLength,_918_input_ZExJou=macdSlowLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def stc(self) -> float:
        return self.__inner._665_stc()
  

    @property
    def macd(self) -> float:
        return self.__inner._666_macd()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, adaptiveLogicLength: Optional[int] = None, stcLength: Optional[int] = None, stcSensitivity: Optional[float] = None, macdFastLength: Optional[int] = None, macdSlowLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_470cff(ctx, _910_input_ZpfPzM=adaptiveLogicLength,_912_input_B08QUZ=stcLength,_914_input_fx5oTH=stcSensitivity,_916_input_btTAmK=macdFastLength,_918_input_ZExJou=macdSlowLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
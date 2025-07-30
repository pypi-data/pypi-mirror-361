
  
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
    return _lib.Incr_fn_main_00bba9(ctx=ctx, _4438_input_V7HpGo=adaptiveLogicLength,_4440_input_ybY9Pz=stcLength,_4442_input_EdWQi0=stcSensitivity,_4444_input_PhmEnP=macdFastLength,_4446_input_05VB3A=macdSlowLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def stc(self) -> float:
        return self.__inner._4193_stc()
  

    @property
    def macd(self) -> float:
        return self.__inner._4194_macd()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, adaptiveLogicLength: Optional[int] = None, stcLength: Optional[int] = None, stcSensitivity: Optional[float] = None, macdFastLength: Optional[int] = None, macdSlowLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_00bba9(ctx, _4438_input_V7HpGo=adaptiveLogicLength,_4440_input_ybY9Pz=stcLength,_4442_input_EdWQi0=stcSensitivity,_4444_input_PhmEnP=macdFastLength,_4446_input_05VB3A=macdSlowLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
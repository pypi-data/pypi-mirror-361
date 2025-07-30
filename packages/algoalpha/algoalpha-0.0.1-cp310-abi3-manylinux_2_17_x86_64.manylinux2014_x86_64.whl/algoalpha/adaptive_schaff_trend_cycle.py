
  
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
    return _lib.Incr_fn_main_51a838(ctx=ctx, _3262_input_BH1BRw=adaptiveLogicLength,_3264_input_fKDvvt=stcLength,_3266_input_fYeWUJ=stcSensitivity,_3268_input_TLSsGt=macdFastLength,_3270_input_gPw2jG=macdSlowLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def stc(self) -> float:
        return self.__inner._3017_stc()
  

    @property
    def macd(self) -> float:
        return self.__inner._3018_macd()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, adaptiveLogicLength: Optional[int] = None, stcLength: Optional[int] = None, stcSensitivity: Optional[float] = None, macdFastLength: Optional[int] = None, macdSlowLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_51a838(ctx, _3262_input_BH1BRw=adaptiveLogicLength,_3264_input_fKDvvt=stcLength,_3266_input_fYeWUJ=stcSensitivity,_3268_input_TLSsGt=macdFastLength,_3270_input_gPw2jG=macdSlowLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
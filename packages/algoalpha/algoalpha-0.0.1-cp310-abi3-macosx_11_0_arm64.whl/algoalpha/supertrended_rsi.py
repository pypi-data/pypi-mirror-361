
  
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

    rsi_value: List[float]
    

    rsi_moving_average: List[float]
    

    rsi_supertrend: List[float]
    

    trend_direction: List[int]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, rsiLength: Optional[int] = None, rsiSmoothingLength: Optional[int] = None, rsiSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, smoothRsi: Optional[bool] = None, maLength: Optional[int] = None, maType: Optional[str] = None, factor: Optional[float] = None, atrLength: Optional[int] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_a11175(ctx=ctx, _4495_input_rSMGqo=rsiLength,_4497_input_0vxR9Q=rsiSmoothingLength,_4499_input_7WhDHq=rsiSource,_4501_input_BqKXtu=smoothRsi,_4503_input_U5YN32=maLength,_4505_input_KITH3r=maType,_4507_input_aLVJwS=factor,_4509_input_tnQmDC=atrLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def rsi_value(self) -> float:
        return self.__inner._4270_rsi_value()
  

    @property
    def rsi_moving_average(self) -> float:
        return self.__inner._4271_rsi_moving_average()
  

    @property
    def rsi_supertrend(self) -> float:
        return self.__inner._4272_rsi_supertrend()
  

    @property
    def trend_direction(self) -> int:
        return self.__inner._4273_trend_direction()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, rsiLength: Optional[int] = None, rsiSmoothingLength: Optional[int] = None, rsiSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, smoothRsi: Optional[bool] = None, maLength: Optional[int] = None, maType: Optional[str] = None, factor: Optional[float] = None, atrLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_a11175(ctx, _4495_input_rSMGqo=rsiLength,_4497_input_0vxR9Q=rsiSmoothingLength,_4499_input_7WhDHq=rsiSource,_4501_input_BqKXtu=smoothRsi,_4503_input_U5YN32=maLength,_4505_input_KITH3r=maType,_4507_input_aLVJwS=factor,_4509_input_tnQmDC=atrLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          

  
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
    return _lib.Incr_fn_main_78431a(ctx=ctx, _2143_input_CVtuGT=rsiLength,_2145_input_92vhsU=rsiSmoothingLength,_2147_input_ZZcFzd=rsiSource,_2149_input_OHtb4U=smoothRsi,_2151_input_IHV87O=maLength,_2153_input_UFw7S6=maType,_2155_input_2XBhgo=factor,_2157_input_069HZy=atrLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def rsi_value(self) -> float:
        return self.__inner._1918_rsi_value()
  

    @property
    def rsi_moving_average(self) -> float:
        return self.__inner._1919_rsi_moving_average()
  

    @property
    def rsi_supertrend(self) -> float:
        return self.__inner._1920_rsi_supertrend()
  

    @property
    def trend_direction(self) -> int:
        return self.__inner._1921_trend_direction()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, rsiLength: Optional[int] = None, rsiSmoothingLength: Optional[int] = None, rsiSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, smoothRsi: Optional[bool] = None, maLength: Optional[int] = None, maType: Optional[str] = None, factor: Optional[float] = None, atrLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_78431a(ctx, _2143_input_CVtuGT=rsiLength,_2145_input_92vhsU=rsiSmoothingLength,_2147_input_ZZcFzd=rsiSource,_2149_input_OHtb4U=smoothRsi,_2151_input_IHV87O=maLength,_2153_input_UFw7S6=maType,_2155_input_2XBhgo=factor,_2157_input_069HZy=atrLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
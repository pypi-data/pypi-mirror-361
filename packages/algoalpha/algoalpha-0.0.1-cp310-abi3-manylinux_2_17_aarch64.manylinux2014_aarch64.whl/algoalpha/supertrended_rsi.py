
  
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
    return _lib.Incr_fn_main_b47589(ctx=ctx, _5671_input_Div80j=rsiLength,_5673_input_17bTwe=rsiSmoothingLength,_5675_input_IoNVdz=rsiSource,_5677_input_jftixK=smoothRsi,_5679_input_XHr1yi=maLength,_5681_input_MWDPfG=maType,_5683_input_T7qrc0=factor,_5685_input_FvKkTb=atrLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def rsi_value(self) -> float:
        return self.__inner._5446_rsi_value()
  

    @property
    def rsi_moving_average(self) -> float:
        return self.__inner._5447_rsi_moving_average()
  

    @property
    def rsi_supertrend(self) -> float:
        return self.__inner._5448_rsi_supertrend()
  

    @property
    def trend_direction(self) -> int:
        return self.__inner._5449_trend_direction()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, rsiLength: Optional[int] = None, rsiSmoothingLength: Optional[int] = None, rsiSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, smoothRsi: Optional[bool] = None, maLength: Optional[int] = None, maType: Optional[str] = None, factor: Optional[float] = None, atrLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_b47589(ctx, _5671_input_Div80j=rsiLength,_5673_input_17bTwe=rsiSmoothingLength,_5675_input_IoNVdz=rsiSource,_5677_input_jftixK=smoothRsi,_5679_input_XHr1yi=maLength,_5681_input_MWDPfG=maType,_5683_input_T7qrc0=factor,_5685_input_FvKkTb=atrLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
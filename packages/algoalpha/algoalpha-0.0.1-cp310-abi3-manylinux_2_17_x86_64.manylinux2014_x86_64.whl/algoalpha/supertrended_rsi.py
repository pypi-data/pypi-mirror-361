
  
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
    return _lib.Incr_fn_main_f3c121(ctx=ctx, _3319_input_6Xc6Nm=rsiLength,_3321_input_RhdvJD=rsiSmoothingLength,_3323_input_OzDymj=rsiSource,_3325_input_8wTKCt=smoothRsi,_3327_input_exTkB8=maLength,_3329_input_uBd9pD=maType,_3331_input_QkUtY8=factor,_3333_input_ge4X06=atrLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def rsi_value(self) -> float:
        return self.__inner._3094_rsi_value()
  

    @property
    def rsi_moving_average(self) -> float:
        return self.__inner._3095_rsi_moving_average()
  

    @property
    def rsi_supertrend(self) -> float:
        return self.__inner._3096_rsi_supertrend()
  

    @property
    def trend_direction(self) -> int:
        return self.__inner._3097_trend_direction()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, rsiLength: Optional[int] = None, rsiSmoothingLength: Optional[int] = None, rsiSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, smoothRsi: Optional[bool] = None, maLength: Optional[int] = None, maType: Optional[str] = None, factor: Optional[float] = None, atrLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_f3c121(ctx, _3319_input_6Xc6Nm=rsiLength,_3321_input_RhdvJD=rsiSmoothingLength,_3323_input_OzDymj=rsiSource,_3325_input_8wTKCt=smoothRsi,_3327_input_exTkB8=maLength,_3329_input_uBd9pD=maType,_3331_input_QkUtY8=factor,_3333_input_ge4X06=atrLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
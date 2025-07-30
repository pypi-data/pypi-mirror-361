
  
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

    v1: List[float]
    

    v2: List[float]
    

    dist: List[float]
    

    ndist: List[float]
    

    h: List[float]
    

    l: List[float]
    

    midp: List[float]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, mainSmoothingLength: Optional[int] = None, signalLength: Optional[int] = None, dataSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, tripleSmoothedMovingAverageType: Optional[str] = None, signalType: Optional[str] = None, bullishColor: Optional[Tuple[int, int, int, int]] = None, bearishColor: Optional[Tuple[int, int, int, int]] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_079608(ctx=ctx, _5710_input_VVXcCI=mainSmoothingLength,_5712_input_RzaOIu=signalLength,_5714_input_YQULi3=dataSource,_5716_input_385uOp=tripleSmoothedMovingAverageType,_5718_input_XEvzUh=signalType,_5720_input_SzkLPV=bullishColor,_5722_input_ffXgLK=bearishColor).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._5481_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._5482_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._5483_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._5484_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._5485_h()
  

    @property
    def l(self) -> float:
        return self.__inner._5486_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._5487_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, mainSmoothingLength: Optional[int] = None, signalLength: Optional[int] = None, dataSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, tripleSmoothedMovingAverageType: Optional[str] = None, signalType: Optional[str] = None, bullishColor: Optional[Tuple[int, int, int, int]] = None, bearishColor: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_079608(ctx, _5710_input_VVXcCI=mainSmoothingLength,_5712_input_RzaOIu=signalLength,_5714_input_YQULi3=dataSource,_5716_input_385uOp=tripleSmoothedMovingAverageType,_5718_input_XEvzUh=signalType,_5720_input_SzkLPV=bullishColor,_5722_input_ffXgLK=bearishColor)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
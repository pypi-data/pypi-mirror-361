
  
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
    return _lib.Incr_fn_main_b704d2(ctx=ctx, _2182_input_KqExcb=mainSmoothingLength,_2184_input_SsTIb5=signalLength,_2186_input_XQ9sMK=dataSource,_2188_input_ei0CxB=tripleSmoothedMovingAverageType,_2190_input_GPoXAj=signalType,_2192_input_9eSXdC=bullishColor,_2194_input_DvcGzg=bearishColor).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._1953_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._1954_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._1955_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._1956_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._1957_h()
  

    @property
    def l(self) -> float:
        return self.__inner._1958_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._1959_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, mainSmoothingLength: Optional[int] = None, signalLength: Optional[int] = None, dataSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, tripleSmoothedMovingAverageType: Optional[str] = None, signalType: Optional[str] = None, bullishColor: Optional[Tuple[int, int, int, int]] = None, bearishColor: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_b704d2(ctx, _2182_input_KqExcb=mainSmoothingLength,_2184_input_SsTIb5=signalLength,_2186_input_XQ9sMK=dataSource,_2188_input_ei0CxB=tripleSmoothedMovingAverageType,_2190_input_GPoXAj=signalType,_2192_input_9eSXdC=bullishColor,_2194_input_DvcGzg=bearishColor)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
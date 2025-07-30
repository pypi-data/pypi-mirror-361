
  
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
    return _lib.Incr_fn_main_8be3fb(ctx=ctx, _1006_input_0OMO4x=mainSmoothingLength,_1008_input_cQT3aI=signalLength,_1010_input_Uv7cxp=dataSource,_1012_input_aWfwhw=tripleSmoothedMovingAverageType,_1014_input_q0uSy1=signalType,_1016_input_TRvIwq=bullishColor,_1018_input_zm7IR0=bearishColor).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._777_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._778_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._779_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._780_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._781_h()
  

    @property
    def l(self) -> float:
        return self.__inner._782_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._783_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, mainSmoothingLength: Optional[int] = None, signalLength: Optional[int] = None, dataSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, tripleSmoothedMovingAverageType: Optional[str] = None, signalType: Optional[str] = None, bullishColor: Optional[Tuple[int, int, int, int]] = None, bearishColor: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_8be3fb(ctx, _1006_input_0OMO4x=mainSmoothingLength,_1008_input_cQT3aI=signalLength,_1010_input_Uv7cxp=dataSource,_1012_input_aWfwhw=tripleSmoothedMovingAverageType,_1014_input_q0uSy1=signalType,_1016_input_TRvIwq=bullishColor,_1018_input_zm7IR0=bearishColor)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
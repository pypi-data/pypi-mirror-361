
  
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
    return _lib.Incr_fn_main_a9b62b(ctx=ctx, _3358_input_PNkE35=mainSmoothingLength,_3360_input_fJuLmx=signalLength,_3362_input_JazZk4=dataSource,_3364_input_4ApvOv=tripleSmoothedMovingAverageType,_3366_input_2jViO3=signalType,_3368_input_brxYfS=bullishColor,_3370_input_ntL2D2=bearishColor).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._3129_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._3130_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._3131_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._3132_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._3133_h()
  

    @property
    def l(self) -> float:
        return self.__inner._3134_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._3135_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, mainSmoothingLength: Optional[int] = None, signalLength: Optional[int] = None, dataSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, tripleSmoothedMovingAverageType: Optional[str] = None, signalType: Optional[str] = None, bullishColor: Optional[Tuple[int, int, int, int]] = None, bearishColor: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_a9b62b(ctx, _3358_input_PNkE35=mainSmoothingLength,_3360_input_fJuLmx=signalLength,_3362_input_JazZk4=dataSource,_3364_input_4ApvOv=tripleSmoothedMovingAverageType,_3366_input_2jViO3=signalType,_3368_input_brxYfS=bullishColor,_3370_input_ntL2D2=bearishColor)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
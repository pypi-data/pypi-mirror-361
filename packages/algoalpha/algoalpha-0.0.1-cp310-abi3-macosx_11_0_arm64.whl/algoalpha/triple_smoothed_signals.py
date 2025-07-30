
  
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
    return _lib.Incr_fn_main_49f65b(ctx=ctx, _4534_input_01YWMC=mainSmoothingLength,_4536_input_fEtFwf=signalLength,_4538_input_H3mWtM=dataSource,_4540_input_SjJFkl=tripleSmoothedMovingAverageType,_4542_input_bLXPSt=signalType,_4544_input_eGkL3w=bullishColor,_4546_input_RQZTdh=bearishColor).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def v1(self) -> float:
        return self.__inner._4305_v1()
  

    @property
    def v2(self) -> float:
        return self.__inner._4306_v2()
  

    @property
    def dist(self) -> float:
        return self.__inner._4307_dist()
  

    @property
    def ndist(self) -> float:
        return self.__inner._4308_ndist()
  

    @property
    def h(self) -> float:
        return self.__inner._4309_h()
  

    @property
    def l(self) -> float:
        return self.__inner._4310_l()
  

    @property
    def midp(self) -> float:
        return self.__inner._4311_midp()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, mainSmoothingLength: Optional[int] = None, signalLength: Optional[int] = None, dataSource: Optional[Union[Literal["open", "high", "low", "close", "volume"], List[float]]] = None, tripleSmoothedMovingAverageType: Optional[str] = None, signalType: Optional[str] = None, bullishColor: Optional[Tuple[int, int, int, int]] = None, bearishColor: Optional[Tuple[int, int, int, int]] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_49f65b(ctx, _4534_input_01YWMC=mainSmoothingLength,_4536_input_fEtFwf=signalLength,_4538_input_H3mWtM=dataSource,_4540_input_SjJFkl=tripleSmoothedMovingAverageType,_4542_input_bLXPSt=signalType,_4544_input_eGkL3w=bullishColor,_4546_input_RQZTdh=bearishColor)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
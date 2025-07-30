
  
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

    custom_rsi: List[float]
    
    pass

class MainResult(TypedDict):
    alerts: List[MainAlert]
    locals: MainResultLocals


def main(ctx: Ctx, oscillatorLength: Optional[int] = None) -> MainResult:
    """
`main() -> void`
    """
    return _lib.Incr_fn_main_a363f3(ctx=ctx, _4466_input_T2oYBR=oscillatorLength).collect()

class MainLocals:
    def __init__(self, inner):
        self.__inner = inner

    

    @property
    def custom_rsi(self) -> float:
        return self.__inner._4229_custom_rsi()
  
      

class Main:
    """
`main() -> void`
    """
    
    def __init__(self, ctx: Ctx, oscillatorLength: Optional[int] = None):
        self.ctx = ctx
        self.inner = _lib.Incr_fn_main_a363f3(ctx, _4466_input_T2oYBR=oscillatorLength)
        self.locals = MainLocals(self.inner)

    def next(self, ) -> Optional[None]:
        return self.inner.next()
    
          
from core_simple import suduko, has_before
from typing import Iterator, TypeVar, Generator, List, Tuple, Callable, Optional
# Debug
from suduko_interative import direct_interative_mode
T = TypeVar("T")
class stream:
    # passed
    def check(src: Iterator[T],*, init: List[T] = [], ignore: List[T] = [], last_one: bool = True) -> Iterator[int]:
        tmp = sorted(init)
        idx = 0
        for x in src:
            if not x in ignore:
                if x in tmp:
                    yield idx
                else:
                    tmp.append(x)
            
            idx += 1
        if last_one:
            yield idx
    # passed (caution with empty arrays)
    def land(src: Iterator[T]) -> bool:
        for x in src:
            if not x:
                return False
        return True
    # passed
    def lor(src: Iterator[T]) -> bool:
        for x in src:
            if x:
                return True
        return False
    # passed 
    def lnot(src: Iterator[T]) -> Iterator[T]:
        for x in src:
            yield not x
    def omega_v(src: Callable[[int], bool]) -> Iterator[bool]:
        for x in range(0, 9):
            yield check_stream(src(x))
    def omega_c(src: Callable[[int], bool]) -> bool:
        return and_stream(stream.multi_check(src))
    # passed (need more test)
    def get_item(src: Iterator[T], by: T, last_one: bool = True) -> Iterator[int]:
        idx = 0
        for x in src:
            if x == by:
                yield idx
            idx += 1
        if last_one:
            yield idx

Self = TypeVar("Self", bound="suduko")

class merge_msg:
    def __init__(self, overwrite: bool, illegal: Optional[has_before] = None):
        self.overwrite = overwrite
        self.illegal = illegal
    def get_msg(self) -> Tuple[bool, Optional[has_before]]:
        return (self.overwrite, self.illegal)
    def get_overwrite(self) -> bool:
        return self.overwrite
    def get_if_has_before(self) -> Optional[has_before]:
        return self.illegal
    def raise_if_has_before(self):
        tmp = self.illegal

class suduko_check(suduko):
    def check_row(self, src : int, init: List[T] = []) -> bool:
        return next(stream.check(self.iter_row(src), init=init, ignore=[0])) == 9
    def check_column(self, src : int, init: List[T] = []) -> bool:
        return next(stream.check(self.iter_column(src), init=init, ignore=[0])) == 9
    def check_grid(self, src : int, init: List[T] = []) -> bool:
        return next(stream.check(self.iter_grid(src), init=init, ignore=[0])) == 9
    def check_columns(self) -> bool:
        return stream.omega_c(self.check_column)
    def check_rows(self) -> bool:
        return stream.omega_c(self.check_row)
    def check_grids(self) -> bool:
        return stream.omega_c(self.check_grid)
    def check_all(self) -> bool:
        t0 = self.check_rows()
        t1 = self.check_columns()
        t2 = self.check_grids()
        return t0 and t1 and t2
    def rem_dup_row(self, src: int):
        pass
    def rem_dup_column(self, src: int):
        pass
    def rem_dup_grid(self, src: int):
        pass
    def rem_dup_all(self, src: int):
        pass
    def eval_merge(self, src: Self, ) -> Iterator[Tuple[bool, Optional[has_before]]]:
        # evalate if a merge operation will need auxiliary actions
        pass
    def safe_merge(self, Self, *, force_overwrite: bool = True, force_valid: bool = True):
        pass

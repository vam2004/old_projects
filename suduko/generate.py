from core_simple import suduko, has_before, sanatizer, safe_parse_idx
from typing import Iterator, TypeVar, Generator, List, Tuple, Callable, Optional, Any
from random import Random
from copy import copy
import time
# from cli_encoder import interface
T = TypeVar("T")
TT = TypeVar("TT")
def hook_iter(src: Iterator[T], hook: Callable[[T], None]) -> Iterator[T]:
    for x in src:
        hook(x)
        yield x

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
    def omega_v(src: Callable[[int], bool], lazy_eval: bool = False) -> Iterator[bool]:
        for x in range(0, 9):
            tmp = src(x)
            yield tmp
    def omega_c(src: Callable[[int], bool]) -> bool:
        return stream.land(stream.omega_v(src))
    # passed (need more test)
    def get_item(src: Iterator[T], by: T, last_one: bool = True) -> Iterator[int]:
        idx = 0
        for x in src:
            if x == by:
                yield idx
            idx += 1
        if last_one:
            yield idx
    def check_suduko(src: Iterator[int], init: List[int] = []) -> bool:
         return next(stream.check(src, init=init, ignore=[0])) == 9
    def hook_dup(*args, hook: Callable[TT, None], **kwargs):
        for x in stream.check(*args, **kwargs, last_one=False):
            hook(x)

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
    def check_row(self, src: int, init: List[int] = []) -> bool:
        return stream.check_suduko(self.iter_row(src), init)
    def check_column(self, src : int, init: List[int] = []) -> bool:
        return stream.check_suduko(self.iter_column(src), init)
    def check_grid(self, src : int, init: List[int] = []) -> bool:
        return stream.check_suduko(self.iter_grid(src), init)
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

class suduko_merge(suduko_check):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.rem_ele: int = 0
        self.overw_c: int = 0
        self.add_ele: int = 0
    def cclear_idx(self, idx: int):
        sanatizer.sane_index(idx)
        if self.buffer[idx]:
            self.rem_ele += 1
            self.buffer[idx] = 0
    def merge_one(self, idx: int, src: int, overwrite: bool = True, force_clear: bool = False):
        sanatizer.sane_index(idx)
        sanatizer.sane_cval(src)
        if self.buffer[idx] == 0:
            if src != 0:
                self.add_ele += 1
                self.buffer[idx] = src
        elif overwrite:
            if src or force_clear:
                if self.buffer[idx] != src:
                    self.overw_c += 1
                    self.buffer[idx] = src
    def cclear_cr(self, column: int, row: int):
        tmp = safe_parse_idx.get_idx_table(column, row)
        self.cclear_idx(tmp)
    def cclear_gp(self, grid: int, pos: int):
        tmp = safe_parse_idx.get_idx_grid(grid, pos)
        self.cclear_idx(tmp)
    def rem_dup_row(self, pos: int, init: List[int] = []):
        tmp = lambda x: self.cclear_cr(pos, x)
        stream.hook_dup(self.iter_row(pos), init=init, ignore=[0], hook=tmp)
    def rem_dup_column(self, pos: int, init: List[int] = []):
        tmp = lambda x: self.cclear_cr(x, pos)
        stream.hook_dup(self.iter_column(pos), init=init, ignore=[0], hook=tmp)
    def rem_dup_grid(self, pos: int, init: List[int] = []):
        tmp = lambda x: self.cclear_gp(pos, x)
        stream.hook_dup(self.iter_grid(pos), init=init, ignore=[0], hook=tmp)
    def rem_dup_all(self):
        for x in range(0, 9):
            self.rem_dup_row(x)
            self.rem_dup_column(x)
            self.rem_dup_grid(x)
    def simple_merge(self, src: List[int], *, force_clear: bool = False, overwrite: bool = False, force_valid: bool = True):
        for i, x in enumerate(src):
            self.merge_one(i, x, overwrite)
        if force_valid:
            self.rem_dup_all()
            
class generate(suduko_merge):
    def __init__(self, seed: int, src: Optional[suduko] = None):
        super().__init__(src=src)
        if src is not None:
            self.add_ele = 81 - self.count_units([0])[0]
        self.seed = seed
        self.rand = Random()
        self.rand.seed(seed)
    def gen_pos(self) -> int:
        return self.rand.randint(0, 80)
    def gen_one(self) -> int:
        return self.rand.randint(1, 9)
    def gen_matriz(self, amount: int):
        tmp: List[int] = [0 for x in range(0, 81)]
        while self.add_ele < amount:
            pos = self.gen_pos()
            ele = self.gen_one()
            self.merge_one(pos, ele, overwrite=False)
    def validate_gen(self) -> int:
        self.rem_ele = 0
        self.rem_dup_all()
        self.add_ele -= self.rem_ele
        return self.add_ele
    def gen_valid(self, amount: int) -> Iterator[int]:
        was = self.add_ele
        while(self.add_ele < amount):
            self.gen_matriz(amount)
            self.validate_gen()
            # print("Counted: {}".format(81 - self.count_units([0])[0]))
            yield self.add_ele - was
            was = self.add_ele
    def try_gen(self, amount: int) -> int:
        was = self.add_ele
        amt = 0
        k0 = int((81 - amount + 0.5) * 8.1) + 2
        idx = 1
        k1 = 0.1
        for x in self.gen_valid(amount):
            idx = idx % k0
            amt += x
            if idx == 0:
                if amt / k0 < k1:
                    return self.add_ele - was
                amt = 0 
            idx += 1
    def beenchmark(self, amount) -> Tuple[float, int]:
        tmp = time.perf_counter()
        x = self.try_gen(amount)
        return (time.perf_counter() - tmp, x)



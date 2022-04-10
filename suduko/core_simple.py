from typing import List, Iterator, Any, Optional, TypeVar
from copy import deepcopy, copy
opt_i = Optional[int]
def has_in_iter(src: Iterator[Any], data: Any) -> bool:
    for i in src:
        if i == data:
            return True
    return False

class rawbuffer_err(Exception):
    def __init__(self, msg):
          super().__init__(msg)

class out_of_bounds(Exception):
      def __init__(self):
          super().__init__("Out of Bounds")

class sanatizer:
    def sane_cval(src: int):
        if src < 0 or src > 9:
            raise out_of_bounds()
    def sane_value(src: int):
        if src < 1 or src > 9:
            raise out_of_bounds()
    def sane_pos(pos: int):
        if pos < 0 or pos > 8:
            raise out_of_bounds()
    def sane_index(idx: int):
        if idx < 0 or idx > 80:
            raise out_of_bounds()
    def safe_int(src: str) -> Optional[int]:
        try:
            return int(src)
        except ValueError:
            return None

# legacy class
class parse_idx:
    def get_idx_table(column: int, row: int) -> int:
        return 9 * column + row
    def get_idx_grid(grid: int, pos: int):
        base = 9 * grid - 6 * (grid % 3)
        offs = 9 * (pos // 3) + (pos % 3)
        return base + offs
    def idx_to_column(src: int) -> int:
        return src % 9
    def idx_to_row(src: int) -> int:
        return src // 9
    def idx_to_grid(src: int) -> int:
        return ((src % 9) // 3) + 3 * (src // 27)
    
class safe_parse_idx(parse_idx):
    def get_idx_table(column: int, row: int) -> int:
        sanatizer.sane_pos(column)
        sanatizer.sane_pos(row)
        return 9 * column + row
    def get_idx_grid(grid: int, pos: int) -> int:
        sanatizer.sane_pos(grid)
        sanatizer.sane_pos(pos)
        base = 9 * grid - 6 * (grid % 3)
        offs = 9 * (pos // 3) + (pos % 3)
        return base + offs
    def idx_to_column(src: int) -> int:
        sanatizer.sane_index(src)
        return src % 9
    def idx_to_row(src: int) -> int:
        sanatizer.sane_index(src)
        return src // 9
    def idx_to_grid(src: int) -> int:
        sanatizer.sane_index(src)
        return ((src % 9) // 3) + 3 * (src // 27)
    
class idxs:
    def __init__(self, pos: int = 0):
        self.set_pos(pos)
    def set_pos(self, pos: int):
        sanatizer.sane_pos(pos)
        self.pos = pos
    def row(self) -> Iterator[int]:
        base = self.pos * 9
        for x in range(base, base + 9):
            yield x
    def column(self) -> Iterator[int]:
        base = self.pos
        for x in range(base, base + 81, 9):
            yield x
    def grid(self) -> Iterator[int]:
        src = self.pos
        base = 9 * src - 6 * (src % 3)
        for x in range(base, base + 27, 9):
            for y in range(x, x + 3):
                yield y
    def forall() -> Iterator[int]:
        return range(0, 81)
    
class pos_err:
    def __init__(self, column: opt_i,
                 row: opt_i, grid: opt_i):
        self.column = column
        self.row = row
        self.grid = grid
class has_before:
    def __init__(self, column: opt_i,
                 row: opt_i, grid: opt_i):
        self.flag: bool = False
        self.cache: Optional[pos_err] = None
        if row is not None:
            self.flag = True
        elif column is not None:
            self.flag = True
        elif grid is not None:
            self.flag = True
        if self.flag:
            self.cache = pos_err(column, row, grid)
    def has(self) -> bool:
        return self.flag

class has_before_err(Exception):
    def __init__(self, tmp: has_before):
        self.has_before = tmp

class mutate_err(Exception):
    pass

class cow_err(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

class suduko:
    clean_buffer = [0 for _ in range(0, 81)]
    def __init__(self, src: Optional[List[int]] = None,*, init_cow: Optional[List[int]] = None):
        if src is None:
            self.buffer = copy(suduko.clean_buffer)
        elif len(src) > 80:
            self.buffer = copy(src)
        else:
            raise rawbuffer_err("Got Few Units")
        self.shadow_buffer: List[int] = []
        self.has_cow: bool = False
        if init_cow is not None:
            if len(init_cow) == 0:
                self.init_cow()
            else:
                self.set_cow(init_cow)
    def init_cow(self):
        if not self.has_cow:
            self.shadow_buffer = copy(self.buffer)
            self.has_cow = True
        else:
            raise cow_err("Already Initialized")
    def sane_cow_init(self):
        if not self.has_cow:
            raise cow_err("Not Initialized")
    def illegal_changes(self, end: Any = 81, last_one: bool = True) -> Iterator[int]:
        self.sane_cow_init()
        for i, x in enumerate(self.shadow_buffer):
            if x and x != self.buffer[i]:
                yield i
        if last_one:
            yield end
    def eval_changes(self):
        self.sane_cow_init()
        if 81 != next(self.illegal_changes()):
            raise mutate_err()
    def undo_changes(self):
        self.sane_cow_init()
        for x in self.illegal_changes(last_one=False):
            self.buffer[x] = self.shadow_buffer[x]
    def set_shadow(self, src: List[int]):
        if len(src) == 81:
            self.shadow_buffer = copy(src)
        else:
            raise cow_err("Invalid Shadow Buffer Assignment")
        self.has_cow = True
    def load_to_shadow(self):
        self.shadow_buffer = copy(self.buffer)
    def clear_pos(self, idx: int):
        sanatizer.sane_index(idx)
        self.buffer[idx] = 0
    def take_idxs(self, src: Iterator[int]) -> Iterator[int]:
        for x in src:
            sanatizer.sane_index(x)
            yield self.buffer[x]
    def iter_all(self) -> Iterator[int]:
        for idx in range(0, 81):
            yield self.buffer[idx]
    def iter_row(self, src: int) -> Iterator[int]:
        return self.take_idxs(idxs(src).row())
    def iter_column(self, src: int) -> Iterator[int]:
        return self.take_idxs(idxs(src).column())
    def iter_grid(self, src: int) -> Iterator[int]:
        return self.take_idxs(idxs(src).grid())
    def has_in_row(self, src: int, row: int) -> bool:
        sanatizer.sane_value(src)
        return has_in_iter(self.iter_row(row), src)
    def has_in_column(self, src: int, column: int) -> bool:
        sanatizer.sane_value(src)
        return has_in_iter(self.iter_column(column), src)
    def has_in_grid(self, src: int, grid: int) -> bool:
        sanatizer.sane_value(src)
        return has_in_iter(self.iter_grid(grid), src)
    def set_one(self, idx: int, src: int, *, auto_check: bool = True) -> has_before:
        sanatizer.sane_cval(src)
        sanatizer.sane_index(src)
        row_e: Optional[int] = None
        column_e: Optional[int] = None
        grid_e: Optional[int] = None
        row: int = parse_idx.idx_to_row(idx)
        column: int = parse_idx.idx_to_column(idx)
        grid: int = parse_idx.idx_to_grid(idx)
        if src and auto_check:
            if self.has_in_row(src, row):
                row_e = row
            if self.has_in_column(src, column):
                column_e = column
            if self.has_in_grid(src, grid):
                grid_e = grid
        cache = has_before(column_e, row_e, grid_e)
        if not cache.has():
            self.buffer[idx] = src
        return cache
    def get_buffer(self):
        return self.buffer
    def set_buffer(self, src: List[int]):
        if len(src) < 81:
            raise rawbuffer_err("Low Buffer Size")
        self.buffer = src
    def count_units(self, by: List[int]) -> List[int]:
        if len(by) > 9 or len(by) < 1:
            raise out_of_bounds()
        for x in by:
            sanatizer.sane_cval(x)
        idx = [0 for _ in range(0, len(by))]
        for x in self.buffer:
            if x in by:
                idx[by.index(x)] += 1
        return idx

def test0() -> suduko:
    tmp = suduko()
    tmp.init_cow()
    tmp.set_one(0, 6)
    tmp.load_to_shadow()
    tmp.set_one(0, 5)
    return tmp

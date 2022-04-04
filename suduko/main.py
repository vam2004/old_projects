from typing import List, Iterator, Any, Optional
opt_i = Optional[int]
def has_in_iter(src: Iterator[Any], data: Any) -> bool:
    for i in src:
        if i == data:
            return True
    return False
def liter(src: Iterator[int]) -> Iterator[int]:
    for x in src:
        print(x)
        yield x

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
        if column is not None:
            self.flag = True
        if grid is not None:
            self.flag = True
        if self.flag:
            self.cache = pos_err(column, row, grid)
    def has(self) -> bool:
        return self.flag
class suduko:
    def __init__(self):
        self.buffer: List[int] = [0 for _ in range(0, 81)]
    def take_idxs(self, src: Iterator[int]) -> Iterator[int]:
        for x in src:
            # print("take: {} from {}".format(self.buffer[x], x))
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
    
    def set(self, idx: int, src: int) -> has_before:
        sanatizer.sane_cval(src)
        sanatizer.sane_index(src)
        row_e: Optional[int] = None
        column_e: Optional[int] = None
        grid_e: Optional[int] = None
        row: int = idx_to_row(idx)
        column: int = idx_to_column(idx)
        grid: int = idx_to_grid(idx) 
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

##def log_idxs(src: Iterator[int]):
##        for x in src:
##            log_idx(x)
##def log_idx(src: int):
##    print("column: {:>2}, row: {:>2}, idx: {}"
##                  .format(src % 9, src // 9, src))

class interface(suduko):
    def __init__(self,*, replace_void: str = ""):
        super().__init__()
        self.set_replace(replace_void)
    def set_replace(self, src: str):
        if len(src) > 1:
            raise ValueError("Too Much Chars")
        if len(src):
            self.replace_char = src[0]
        else:
            self.replace_char = ""
    def parse_grid(self, src: int) -> Iterator[str]:
        for x in self.take_idxs(idxs(src).grid()):
            yield str(x) if x != 0 else self.replace_char
    def parse_all(self) -> Iterator[str]:
        for x in self.iter_all():
            yield str(x) if x != 0 else self.replace_char
    def list_all(self):
        cache = list(self.parse_all())
        for x in range(0, 9):
            print("|", end="")
            for y in range(0, 3):
                base = 9 * x + 3 * y
                tmp = cache[base:(base+3)]
                print(" {} {} {} ".format(tmp[0], tmp[1], tmp[2]), end="|")
            print("")
    def get_buffer(self):
        return self.buffer

clear_void_replace = "x" 
class game(interface):
    def ask_action(self) -> bool:
        tmp = input("now?: ").lower()
        if len(tmp) < 1:
            return False
        if tmp == "ex":
            return False
        if tmp == "la":
            self.list_all()
            return True
        if tmp == "sv":
            if len(tmp) < 2:
                self.set_replace(clear_void_replace)
            else:
                self.set_replace(tmp[1])
            return True
        if tmp == "pl":
            return self.ask_pos()
        return False
    def ask_pos(self) -> bool:
        raw = input("pos: ").lower()
        if raw == "":
            return False
        tmp = raw.split()
        if len(tmp) < 3:
            print("Not Enough Arguments!")
        else:
            idx = self.__class__.parse(tmp)
            if idx is None:
                print("Invalid Arguments!")
            else:
                val = self.ask_val()
                if val is None:
                    print("Expected a integer")
                else:
                    self.play_one(idx, val)
        return True
    def ask_val(self) -> Optional[int]:
        raw = input("val: ")
        if raw == "":
            return None
        return sanatizer.safe_int(raw)
    def play_one(self, pos, val):
        try:
            tmp = self.set(pos, val)
            if tmp.has():
                print("Invalid Insertion!")
        except out_of_bounds:
            print("Value Out of Range!")
    def parse(src: List[str]) -> Optional[int]:
        if src[0] == "gp":
            t0 = sanatizer.safe_int(src[1])
            t1 = sanatizer.safe_int(src[2])
            if t0 is None or t1 is None:
                return None
            return get_idx_grid(t0, t1)
        if src[0] == "cr":
            t0 = sanatizer.safe_int(src[1])
            t1 = sanatizer.safe_int(src[2])
            if t0 is None or t1 is None:
                return None
            return get_idx_table(t1, t0)
        return 0

def main():
    tmp = game()
    while tmp.ask_action():
        pass

main()

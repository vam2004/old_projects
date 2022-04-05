from typing import List, Iterator, Any, Optional, Generic, TypeVar
from core_simple import suduko, sanatizer, parse_idx, idxs, out_of_bounds
##def log_idxs(src: Iterator[int]):
##        for x in src:
##            log_idx(x)
##def log_idx(src: int):
##    print("column: {:>2}, row: {:>2}, idx: {}"
##                  .format(src % 9, src // 9, src))

class chunk_error(Exception):
    def __init__(self, msg: str):
        super().__init__(msg)

T = TypeVar("T")
def safe_next(src: Iterator[T]) -> Optional[T]:
        try:
            return next(src)
        except StopIteration:
            return None
class chunks:
    def __init__(self,*, padding: Optional[T] = None, fill_end: bool = False):
        self._run = True
        self.fill_end = padding
        self.keep_end = fill_end
    def create(self, src: Iterator[T], off: int) -> Iterator[Iterator[Optional[T]]]:
        if off < 1:
            raise chunk_error("Invalid Offset")
        self.run = True
        while self._run:
            yield self.take(src, off)
    def take(self, src: Iterator[Any], amount: int) -> Iterator[Optional[T]]:
        if amount < 1:
            raise chunk_error("Invalid Amount")
        running: bool = True
        idx: int = 0
        while(idx < amount and running):
            try:
                yield next(src)
                idx += 1
            except StopIteration:
                running = False
        self._run = running
        if not running and self.keep_end:
            for x in range(idx, amount):
                yield self.fill_end
class fmt_unit:
    def thr(src: Iterator[str]) -> Iterator[str]:
        for x in chunks(padding="", fill_end=True).create(src, 3):
            tmp = list(x)
            yield "{}  {}  {}".format(tmp[0], tmp[1], tmp[2])
    def sep(src: Iterator[str],*, fill_first: bool = True, nth: int = 0) -> Iterator[str]:
        if fill_first:
            tmp = safe_next(src)
            if tmp is not None:
                yield "|{} |".format(tmp)
            nth -= 1
        if nth > 0:
            for tmp in chunks().take(src, nth):
                yield "{} |".format(tmp)
        else:
            for tmp in src:
                yield "{} |".format(tmp)
    
    def col(src: Iterator[str], sep: str = "\n") -> Iterator[str]:
        tmp = 0
        for x in src:
            if tmp and tmp % 3 == 0:
                yield sep
            tmp += 1
            yield x
class interface(suduko):
    def __init__(self,*, replace_void: str = ""):
        super().__init__()
        self.set_replace(replace_void)
        self.sep_grid_i = ("-" * 32)
        self.sep_grid_b = self.sep_grid_i
        self.sep_grid_a = self.sep_grid_i
    def set_grid_sep(self,*, between: Optional[str] = None,
                     after: Optional[str] = None,
                     before: Optional[str] = None):
        if between is not None:
            self.sep_grid_i = between
        if after is not None:
            self.sep_grid_a = after
        if before is not None:
            self.sep_grid_b = before
    def set_replace(self, src: str):
        if len(src) > 1:
            raise ValueError("Too Much Chars")
        if len(src):
            self.replace_char = src[0]
        else:
            self.replace_char = ""
    def parse_iter(self, src: Iterator[int]) -> Iterator[int]:
        for x in self.take_idxs(src):
            yield str(x) if x != 0 else self.replace_char
    def parse_grid(self, src: int) -> Iterator[str]:
        return self.parse_iter(idxs(src).grid())
    def parse_all(self) -> Iterator[str]:
        return self.parse_iter(idxs.forall())
    def parse_row(self, src: int) -> Iterator[str]:
        return self.parse_iter(idxs(src).row())
    def parse_column(self, src: int) -> Iterator[str]:
        return self.parse_iter(idxs(src).column())
    def list_all(self):
##        cache = list(self.parse_all())
##        for x in range(0, 9):
##            if x and not x % 3:
##                print("")
##            print("|", end="")
##            for y in range(0, 3):
##                base = 9 * x + 3 * y
##                tmp = cache[base:(base+3)]
##                print("{:>2} {:>2} {:>2} ".format(tmp[0], tmp[1], tmp[2]), end="|")
##            print("")
        
        print(self.sep_grid_b)
        for x in fmt_unit.col(self.all_row(), sep=self.sep_grid_i):
            print(x)
        print(self.sep_grid_a)
    def all_row(self):
        for x in range(0, 9):
            tmp = self.enc_row()
            if tmp is not None:
                yield tmp
    def list_row(self):
        pass
    def enc_row(self) -> Optional[str]:
        tmp = fmt_unit.thr(self.parse_all())
        lsi = safe_next(fmt_unit.thr(fmt_unit.sep(tmp, nth=3)))
        if lsi is not None:
            return "".join(list(lsi))
        return None

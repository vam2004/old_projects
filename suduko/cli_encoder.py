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
    def sep(src: Iterator[str],*, fill_first: bool = True, nth: int = 0, sep: str = "") -> Iterator[str]:
        if fill_first:
            tmp = safe_next(src)
            if tmp is not None:
                yield "{} {} {}".format(sep, tmp, sep)
            nth -= 1
        if nth > 0:
            for tmp in chunks().take(src, nth):
                yield "{} {}".format(tmp, sep)
        else:
            for tmp in src:
                yield "{} {}".format(tmp, sep)
    
    def col(src: Iterator[str], sep: str = "\n") -> Iterator[str]:
        tmp = 0
        for x in src:
            if tmp and tmp % 3 == 0:
                yield sep
            tmp += 1
            yield x

class interface(suduko):
    def __init__(self,*, replace_void: str = "", column_sep: str = "", sep_row_i: str = ("-" * 33),  from_raw: Optional[List[int]] = None, src: Optional[suduko] = None):
        super().__init__(from_raw)
        if src is not None:
            self.set_buffer(src.get_buffer())
        self.set_replace(replace_void)
        self.sep_grid_i = sep_row_i
        self.sep_grid_b = self.sep_grid_i
        self.sep_grid_a = self.sep_grid_i
        self.column_sep = column_sep
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
        for x in self.enc_all(True):
            print(x)
    def enc_all(self, flag: bool = True) -> Iterator[str]:
        if flag:
            yield self.sep_grid_b
        for x in fmt_unit.col(self.all_row(), sep=self.sep_grid_i):
            yield x
        if flag:
            yield self.sep_grid_a
    def all_row(self):
        for x in range(0, 9):
            tmp = self.enc_row(x)
            if tmp is not None:
                yield tmp
    def list_row(self, src: int):
        tmp = self.enc_row(x)
        if tmp is not None:
            print(tmp)
    def enc_row(self, src: int) -> Optional[str]:
        tmp = fmt_unit.thr(self.parse_row(src))
        lsi = safe_next(fmt_unit.thr(fmt_unit.sep(tmp, nth=3, sep=self.column_sep)))
        if lsi is not None:
            return "".join(list(lsi))
        return None

def list_all(x: suduko):
    interface(src=x, replace_void="_", column_sep="|").list_all()

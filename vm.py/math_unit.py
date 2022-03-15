from typing import Optional, TypeVar

Self = TypeVar('Self', bound='general_ula')

class general_ula:
    def __init__(self):
        self.o: bool = False # overflow
        self.u: bool = False # underflow
        self.n: bool = False # negative
        self.z: bool = False # zero
        self.ax: int = 0 # auxiliary
        self.ac: int = 0 # accumulator
    def clear_flags(self):
        self.o = False
        self.u = False
        self.n = False
        self.z = False
    def save_state(self) -> Self:
        out: Self = self.__class__()
        out.o = self.o
        out.u = self.u
        out.n = self.n
        out.z = self.z
        out.ax = self.ax
        out.ac = self.ac
    def load_state(self, src: Self):
        self.o = src.o
        self.u = src.u
        self.n = src.n
        self.z = src.z
        self.ax = src.ax
        self.ac = src.ac
    def swap(self):
        tmp = self.ax
        self.ax = self.ac
        self.ac = tmp

class signed16(general_ula):
    def normalize(self, src: int) -> int:
        if src > 0x7fff:
            self.o = True
            return 0x7fff
        elif src < -0x8000:
            self.u = True
            return -0x7fff
        else:
            return src
    def val_inv(self, src: int) -> int:
        src = self.normalize(src)
        if src == -0x8000:
            self.o = True
            self.u = True
            return -0x7fff
        else:
            return src
    def inv_one(self, src: int) -> int:
        src = self.val_inv(src)
        return (0xffff ^ (src & 0xffff)) + 1
    def inv_two(self, src: int):
        src = self.val_inv(src)
        return 0x10000 - (src & 0xffff)
    def to_host(self, src: int) -> int:
        if src > 0xffff:
            self.o = True
            src = 0xffff
        elif src >> 15:
            return src - 0x10000
        else:
            return src
    def from_host(self, src: int) -> int:
        src = self.normalize(src)
        if src < 0:
            return 0x10000 + src
        else:
            return src

class ula16(signed16):
    def into_sax(self):
        self.ax = self.to_host(self.ax)
    def into_sac(self):
        self.ac = self.to_host(self.ac)
    def back_sax(self):
        self.ax = self.from_host(self.ax)
    def back_sac(self):
        self.ac = self.from_host(self.ac)
    def addu(self):
        self.ac = self.ac + self.ax
    def update_uflags(self):
        if self.ac > 0xffff:
            self.o = True
        elif self.ac == 0:
            self.z = True
    def update_sflags(self):
        if (self.ac >> 15) & 1:
            self.n = True
        self.update_uflags()
    def lshu(self):
        if self.ax > 0xf:
            self.ax = 0xf
        self.ac = self.ac << self.ax
    def rshu(self):
        ac = self.ac
        self.ac = ac << self.ax
        if self.ac >> self.ax != ac:
            self.u = True
    def lxor(self):
        self.ac = self.ac ^ self.ax
    def land(self):
        self.ac = self.ac & self.ax
    def lor(self):
        self.ac = self.ac | self.ax
    def lnot(self):
        self.ac = self.ac ^ 0xffff
    def get_ac(self) -> int:
        return self.ax
    def set_ac(self, ac: int):
        self.ac = ac
    def set_ax(self, ax: int):
        self.ax = ax
    def clip_ax(self):
        self.ax = self.ax & 0xffff
    def clip_ac(self):
        self.ac = self.ac & 0xffff


    
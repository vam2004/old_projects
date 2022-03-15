from typing import Generator, Optional, Callable, Tuple, List;

IP_MEM_ADDR = 20 # address of intruction pointer
FR_MEM_ADDR = 22 # address of flags register
INT_HD_ADDR = 0x1004 # address of interrupts handler
SIGNAL_ADDR = 0x1002 # address of interrupt code register
RETURN_ADDR = 0x1000 # return point from a interrupt
SP_MEM_ADDR: int = 0x24 # address of stack pointer register
AC_MEM_ADDR: int = 0x00 # adress of acummulator

# big indian bit positons of flags
FLAG_POS_ZERO: int = 0x00
FLAG_POS_OVERFLOW: int = 0x01
FLAG_POS_UNDERFLOW: int = 0x02
FLAG_POS_INT: int = 0x3 # clear interrupt flag

def rev_dict(s):
    return {v: k for k, v in s.items()}

def b_ind_concat(b0: int, b1: int) -> int:
    return ((b0 % 255) << 8) | (b1 % 255)

def make_inst(op: int, rg: int) -> int:
    return (op << 3) | (rg % 7)

DEBUG_SIGNATURE = Callable[[int, int, int], bool]

int_codes = {
    'halt': 0x00, # halt system
    'seg_fault': 0x01, # segment fault
    'reboot': 0x02, # core reset
    'timer': 0x03, # system timer
    'zero_op': 0x04, # zero operation
}
int_names = rev_dict(int_codes)
op_names = {
    # addesses up to 0x0f are one-byte instructions 
    0x00: 'int', # interrupt with @rg as int_codes
    0x01: 'flag', # flush flag
    0x02: 'not', # bit-a-bit not with @rg
    0x03: 'add', # add @ac with @rg
    0x04: 'push', # push @rg onto stack
    0x05: 'pop', # pop from stack into @rg
    0x06: 'lsh', # left shift @ac with @rg
    0x07: 'rsh', # right shift @ac with @rg
    0x08: 'sadd', # signed version of 'add'
    0x09: 'srsh', # signed version of 'rsh'
    0x0a: 'slsh', # signed version of 'lsh'
    0x0b: 'sub', # subtract @rg of @ac
    0x0c: 'xor', # bit-a-bit xor of @ac with @rg
    0x0d: 'and', # bit-a-bit and of @ac with @rg
    0x0e: 'or', # bit-a-bit or of @ac with @rg
    0x0f: 'intr', # insterrupt with @rg
    # addesses among 0x10 and 0x1f are three-byte instructions
    0x10: 'addm', # add @rg with @addr
    0x11: 'read', # read @addr to @rg
    0x12: 'load', # write @rg into @addr
    0x13: 'lshm', # left shift @addr into @rg
    0x14: 'rshm', # right shift @addr into @rg
    0x15: 'iadd', # signed version of addm
    0x16: 'irsh', # signed version of rshm
    0x17: 'ilsh', # signed version of lshm
    0x18: 'jez', # jump if equal zero
    0x19: 'subm', # subtract @addr of @rg
    0x1a: 'rdpg', # read from imediate page at @rg offset  
    0x1b: 'wtpg', # write to imediate page at @rg offset
    0x1c: 'xorm', # bit-a-bit xor of @rg with @addr
    0x1d: 'andm', # bit-a-bit and of @rg with @addr
    0x1e: 'orm', # bit-a-bit or of @rg with
    0x1f: 'notm', # bit-a-bit not of @addr
}
op_codes = rev_dict(op_names)
class asm_pointer:
    def __init__(self, init: int):
        self.pointer = init
    def add(self, offset: int):
        self.pointer = self.pointer + offset
        return self
    def get(self) -> int:
        return self.pointer
    def get_low(self) -> int:
        return self.pointer & 0xff
    def get_high(self) -> int:
        return (self.pointer >> 8) & 0xff
    def set(self, adr: int):
        self.pointer = adr
        return self
    def add_high(self, src: int) -> int:
        self.add(src)
        return self.get_high()
    def add_low(self, src: int) -> int:
        self.add(src)
        return self.get_low()
        
base = asm_pointer(INT_HD_ADDR)
    
BOOT_ROM: bytearray = bytearray([
    make_inst(op_codes['addm'], 4),
    base.add_high(12),
    base.get_low(),
    make_inst(op_codes['read'], 1),
    base.add_high(-255),
    base.get_low(),
    make_inst(op_codes['jez'], 0),
    base.set(INT_HD_ADDR + 9).get_high(),
    base.get_low(),
    0xff,
    0xfa,
    0x86,
    0x00
]) 
def sign_16(s: int) -> int:
    s = s & 0xffff
    if s >> 15:
        s = s - 0x10000
    return s

def from_sign_with_overflow(s: int) -> int:
    if s < 0:
        s = 0x10000 + s
    return s

class VmSpec:
    def __init__(self):
        self.mem: bytearray = bytearray(0x10000)
        self.cycles: Optional[int] = 0
        self.hook: Optional[DEBUG_SIGNATURE] = None
        self.ip: int = INT_HD_ADDR
        self.sp: int = 0
        self.fl: int = 0
    def update_ip(self, src):
        #self.put16(IP_MEM_ADDR, src)
        self.ip = src
    def copy_mem(self, adr: int, src: bytearray):
        lim = len(src)
        if adr < 0:
            adr = 0
        if lim + adr > 0xffff:
            lim = 0xffff - adr
        if lim < 0:
            lim = 0
        for i in range(0, lim):
            #self.mem[adr + i] = src[i]
            self.put(adr + i, src[i])
    def copy_page(self, add: int, src: bytearray):
        off = (add << 8) & 0xff
        for x in range(0, 0xff):
            self.mem[off + x] = src[x]
    def read_page(self, add: int) -> Generator[int, None, None]:
        off = (add << 8) & 0xff
        for x in range(off, off + 0xff):
            #yield self.mem[off]
            yield self.get(off)
    def read_mem(self, adr: int, until: int) -> Generator[int, None, None]:
        if adr < 0:
            adr = 0
        if until + adr > 0xffff:
            until = 0xffff - adr
        if until < 0:
            until = 0
        for i in range(adr, adr + until):
            #yield self.mem[i]
            yield self.get(i)
    def read_mem16(self, adr: int, until: int) -> Generator[int, None, None]:
        until = until - (until % 2)
        if adr < 0:
            adr = 0
        if until + adr > 0xffff:
            until = 0xffff - adr
        if until < 0:
            until = 0
        for i in range(adr, adr + until, 2):
            yield self.get16(i)
    def set_hook(self, hook: Optional[DEBUG_SIGNATURE] = None):
        self.hook = hook
    def run(self) -> Optional[Tuple[int, bool]]:
        if self.cycles is not None and self.cycles < 1:
            return (0, True)
        ins: int = self.fetch()
        opc: int = ins[0]
        reg: int = ins[1]
        adr: int = ins[2]
        if self.hook is not None:
            hk = self.hook(opc, reg, adr)
            if hk:
                return (hk, True)
        hk = self.step(opc, reg, adr)
        if hk is None:
            if self.cycles is not None:
                self.cycles = self.cycles - 1
        else:
            return (hk, False)
    def update_sp(self, dir: bool):
        pos = self.get16(SP_MEM_ADDR)
        if dir:
            pos + 1
            if pos > 0xffff:
                self.process_int(int_codes['seg_fault'])
        else:
            pos - 1
            if pos < 0x0000:
                self.process_int(int_codes['seg_fault'])
        #self.put16(SP_MEM_ADDR, pos & 0xffff)
        self.sp = pos & 0xffff
    def step(self, opc: int, reg: int, adr: int) -> Optional[int]:
        reg: int = reg & 0x7
        adr: int = adr & 0xffff
        ac: Optional[int] = None
        lock_ip: bool = False
        underflow: bool = False
        # addesses up to 0x0f are one-byte instructions 
        if opc == op_codes['int']:
            lock_ip = True
            if reg:
                self.process_int(reg)
            return reg
        elif opc == op_codes['flag']:
            ac = (self.fl >> (reg & 0x0f)) ^ (reg >> 4)
        elif opc == op_codes['not']:
            ac = self.get16(reg) ^ 0xffff
            self.put16(reg, ac)
        elif opc == op_codes['add']:
            ac = self.get16(reg) + self.get16(AC_MEM_ADDR)
            self.put16(AC_MEM_ADDR, ac)
        elif opc == op_codes['push']:
            self.put16(self.get16(SP_MEM_ADDR), self.get16(reg))
            self.update_sp(True)
        elif opc == op_codes['pop']:
            ac = self.get16(SP_MEM_ADDR)
            self.put16(reg, ac)
            self.change_sp(False)
        elif opc == op_codes['lsh']:
            ax = self.get16(reg)
            tp = self.get16(AC_MEM_ADDR)
            if ax > 15:
                ax = 15
            ac = tp << ax
            self.put16(AC_MEM_ADDR, ac)
        elif opc == op_codes['rsh']:
            ax = self.get16(reg)
            tp = self.get16(AC_MEM_ADDR)
            ac = tp >> ax
            if ac << ax != tp:
                underflow = True
            self.put16(AC_MEM_ADDR, ac)
        elif opc == op_codes['sadd']:
            ac = from_sign_with_overflow(sign_16(self.get16(reg)) + sign_16(self.get16(AC_MEM_ADDR)))
            if ac >> 15:
                underflow = True 
            self.put16(AC_MEM_ADDR, ac)
        elif opc == op_codes['srsh']:
            pass
        elif opc == op_codes['slsh']:
            pass
        elif opc == op_codes['sub']:
            pass
        elif opc == op_codes['xor']:
            ac = self.get16(AC_MEM_ADDR) ^ self.get16(reg)
            self.put16(AC_MEM_ADDR, ac)
        elif opc == op_codes['and']:
            ac = self.get16(AC_MEM_ADDR) & self.get16(reg)
            self.put16(AC_MEM_ADDR, ac)
        elif opc == op_codes['or']:
            ac = self.get16(AC_MEM_ADDR) | self.get16(reg)  
            self.put16(AC_MEM_ADDR, ac)
        elif opc == op_codes['intr']:
            self.extended_int(self.get16(reg))
        # addesses over 0x10 and until 0x1f are three-byte instructions
        elif opc == op_codes['addm']:
            ac = self.get16(adr) + self.get16(reg)
            self.put16(reg, ac)
        elif opc == op_codes['read']:
            ac = self.get16(adr)
            self.put16(reg, ac)
        elif opc == op_codes['load']:
            self.put16(self.get16(adr), self.get16(reg))
        elif opc == op_codes['lshm']:
            ax = self.get16(adr)
            tp = self.get16(reg)
            if ax > 15:
                ax = 15
            ac = tp << ax
            self.put16(reg, ac)
        elif opc == op_codes['rshm']:
            ax = self.get16(adr)
            tp = self.get16(reg)
            ac = tp >> ax
            if ac << ax != tp:
                underflow = True
            self.put16(reg, ac)
        elif opc == op_codes['iadd']:
            pass
        elif opc == op_codes['irsh']:
            pass
        elif opc == op_codes['ilsh']:
            pass
        elif opc == op_codes['jez']:
            if (self.fl >> FLAG_POS_ZERO) & 1:
                self.update_ip(adr)
                lock_ip = True
        elif opc == op_codes['subm']:
            pass
        elif opc == op_codes['rdpg']:
            pass
        elif opc == op_codes['wtpg']:
            pass
        elif opc == op_codes['xorm']:
            ac = self.get16(reg) ^ self.get16(adr)
            self.put16(reg, ac)
        elif opc == op_codes['andm']:
            ac = self.get16(reg) & self.get16(adr)
            self.put16(reg, ac)
        elif opc == op_codes['orm']:
            pass
        elif opc == op_codes['notm']:
            pass
        else:
            pass
        if ac is not None:
            if ac > 0xffff:
                self.fl = self.fl | (1 << FLAG_POS_OVERFLOW)
            if ac:
                self.fl = self.fl | (1 << FLAG_POS_ZERO)
        if underflow:
            self.fl = self.fl | (1 << FLAG_POS_OVERFLOW)
        jmp_off = 1
        if opc >> 4:
            jmp_off = 3
        if not lock_ip:
            self.update_ip(self.ip + jmp_off) 
    def set_flag(self, flag_pos: int, value: bool):
        org = (self.fl >> flag_pos) & 1
        msk = org ^ value
        self.fl = self.fl ^ (msk << flag_pos) 
    def clear_cond_flags(self):
        self.fl = (self.fl >> 3) << 3
    def feed_cycles(self, c: Optional[int] = 0):
        self.cycles = c
    def get_registers(self) -> Generator[int, None, None]:
        for i in range(0, 16):
            yield self.get16(i)
    def extended_int(self, id: int) -> bool:
        return self.process_int(id & 0x7)
    def process_int(self, id: int) -> bool:
        if not ((self.fl >> 5) & 1): 
            self.put16(RETURN_ADDR, self.ip)
            self.put16(SIGNAL_ADDR, id)
            self.update_ip(INT_HD_ADDR)
            return False
        else:
            return True
    def get(self, add: int) -> int:
        x = self.mem[add]
        #print('read ['+hex(add)+']:'+hex(x))
        return x
    def put(self, add: int, src: int):
        #print('load ['+hex(add)+']:'+hex(src))
        self.mem[add] = src & 0xff
    def get16(self, add: int) -> int:
        msb = self.get(add) << 8
        lsb = self.get(add + 1)
        return msb + lsb
    def put16(self, add: int, src: int):
        self.put(add, src >> 8)
        self.put(add + 1, src)
    def fetch(self) -> [int, int, int]:
        if self.ip > 0xfffe:
            self.process_int(int_names['seg_fault'])
        b1 = self.get(self.ip) % 0xff
        rg = b1 & 0x7
        b2 = 0
        b3 = 0
        if (b1 >> 7) & 1:
            b2 = self.get(self.ip + 1)
            b3 = self.get(self.ip + 2)
        return [b1 >> 3, rg, b_ind_concat(b2, b3)]
class debug_raw:
    def __init__(self, vm: VmSpec):
        self.vm = vm
    def show(self, opc: int, reg: int, adr: int) -> bool:
        high = ''
        if opc >> 4: 
            high = ', ' + hex(adr)
        print('\n')
        print('[' + hex(opc) + '] ' + op_names[opc] + ': ' + hex(reg) + high)
        print('  IP: ' + hex(self.vm.ip))
        print('  SP: ' + hex(self.vm.sp))
        print('  FL: ' + hex(self.vm.fl))
        return False
class debug:
    def __init__(self, vm: VmSpec):
        self.vm = vm
    def print_mem(self, adr: int, utl: int, step: int) -> Generator[List[str], None, None]:
        for i in range(adr, utl, step):
            yield list(self.gen_mem_hex(i, i + step))
    def gen_mem_hex(self, adr: int, utl: int) -> Generator[str, None, None]:
        for i in self.vm.read_mem16(adr, adr + utl):
            yield hex(i)
            

try:
    vm = VmSpec()
    db = debug_raw(vm)
    mem_db = debug(vm)
    vm.feed_cycles(None)
    vm.copy_mem(INT_HD_ADDR, BOOT_ROM)
    vm.set_hook(db.show)
    for x in range(0, 5):
        vm.run()
        #print('returned:', vm.run())
        #print('memory:', list(map(hex, vm.read_mem16(vm.ip, 6))))
        print('register:', list(mem_db.gen_mem_hex(0, 16)))
except:
    print("Error:")
finally:
    print("Exited")
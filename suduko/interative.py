from cli_encoder import interface
from core_simple import sanatizer, has_before, safe_parse_idx, out_of_bounds
from typing import Optional, List
clear_void_replace = "x"
class sock_wrapper:
    def __init__(self, send, read):
        self.wsend = send
        self.wread = read
    def send(self, data: str):
        self.wsend(data)
    def read(self) -> str:
        return self.wread()
    def ask(self, data: str) -> str:
        self.send(data)
        return self.read()
    
class unknown_arg(Exception):
    pass

class few_args(Exception):
    pass

class invalid_pos(Exception):
    pass

class not_have_value(Exception):
    pass

class has_inside_err(Exception):
    def __init__(tmp: has_before):
        self.has_before = tmp

class abstract_game(interface):
    indict = {
        "gp": (safe_parse_idx.get_idx_table, False),
        "pg": (safe_parse_idx.get_idx_table, True),
        "cr": (safe_parse_idx.get_idx_table, False),
        "rc": (safe_parse_idx.get_idx_table, True)
    }
    def __init__(self,*,replace_void: str = "x"):
        super().__init__(replace_void=replace_void)
        self.auto_list = False
        self._sock = sock_wrapper(print, input)
    def set_auto_list(self, flag: bool):
        self.auto_list = flag   
    def play(self, pos, val):
        tmp = self.set_one(pos, val)
        if tmp.has():
            raise has_inside_err(tmp)
        elif self.auto_list:
            self.send_list_all()
    def send_list_all(self):
        for x in self.enc_all(): 
            self._sock.send(x)
    def do_action(self, data: List[str]):
        if len(data) < 2:
            raise few_args()
        if data[1] == "auto-list":
            if len(data) > 2 and src[3] == "false":
                self.auto_list = False
            else:
                self.auto_list = True
        if data[1] == "list-all":
            self.send_list_all()
    def send_msg(self, msg: str):
        self._sock.send(msg)
    def step(self) -> bool:
        raw = self._sock.read().lower()
        if raw == "" or raw == "exit":
            return False
        tmp = raw.split()
        if tmp[0] == "do":
            #if len(tmp) < 2:
                #return True
            self.do_action(tmp)
            return True
        if len(tmp) < 5:
            raise few_args()
        _idx = abstract_game.parse_pos(tmp)
        _val = abstract_game.parse_val(tmp)
        self.play(_idx, _val)
        return True
    def parse_pos(src: List[str]):
        t0 = sanatizer.safe_int(src[1])
        t1 = sanatizer.safe_int(src[2])
        if t0 is None or t1 is None:
            raise invalid_pos()
        act = src[0]
        if not act in abstract_game.indict:
            raise unknown_arg()
        _action, rot = abstract_game.indict[act]
        try:
            if rot:
                return _action(t1 - 1, t0 - 1)
            else:
                return _action(t0 - 1, t1 - 1)
        except out_of_bounds:
            raise invalid_pos()
    def parse_val(src: List[str]):
        if src[3] == "v":
            return sanatizer.safe_int(src[4])
        else:
            raise not_have_value()
    def step_encoded(self, on_err: bool = True):
        try:
            return self.step()
        except few_args:
            self.send_msg("Error: Few Args")
        except out_of_bounds:
            self.send_msg("Error: Value Out Of Range")
        except has_inside_err:
            self.send_msg("Error: The Value Already Exist")
        except not_have_value:
            self.send_msg("Error: Please Insert A Value")
        except unknown_arg:
            self.send_msg("Error: Not a Valid Value")
        return on_err

def main():
    tmp = abstract_game(replace_void="x")
    print("Next: ", end="")
    while tmp.step_encoded():
        print("Done!")
try:
    main()
except KeyboardInterrupt:
    print("\nExited!")
except Exception as E:
    raise E
    print("Critical Error!")

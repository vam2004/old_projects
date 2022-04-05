from cli_encoder import interface
from core_simple import sanatizer, parse_idx, out_of_bounds
from typing import Optional, List
clear_void_replace = "x" 
class game(interface):
    def __init__(self,*,replace_void: str = "x"):
        super().__init__(replace_void=replace_void)
        self.auto_list = False
    def set_auto_list(self, flag: bool):
        self.auto_list = flag
    def ask_action(self) -> bool:
        tmp = input("now?: ").lower().split()
        if len(tmp) <= 0:
            return self.ask_pos()
        if tmp[0] == "ex":
            return False
        if tmp[0] == "la":
            self.list_all()
            return True
        if tmp[0] == "vd":
            if len(tmp) < 2:
                self.set_replace(clear_void_replace)
            else:
                self.set_replace(tmp[1])
            return True
        if tmp[0] == "pl":
            return self.ask_pos()
        if tmp[0] == "auto-list":
            if len(tmp) < 2 or tmp[1] == "true":
                self.auto_list = True
            else:
                self.auto_list = False
        return self.ask_pos()
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
            elif self.auto_list:
                self.list_all()
        except out_of_bounds:
            print("Value Out of Range!")
    def parse(src: List[str]) -> Optional[int]:
        if src[0] == "gp":
            t0 = sanatizer.safe_int(src[1])
            t1 = sanatizer.safe_int(src[2])
            if t0 is None or t1 is None:
                return None
            return parse_idx.get_idx_grid(t0 - 1, t1 - 1)
        if src[0] == "cr":
            t0 = sanatizer.safe_int(src[1])
            t1 = sanatizer.safe_int(src[2])
            if t0 is None or t1 is None:
                return None
            return parse_idx.get_idx_table(t1 - 1, t0 - 1)
        return None

def main():
    tmp = game(replace_void="x")
    while tmp.ask_action():
        pass

main()

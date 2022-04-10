from sock_encoder import abstract_game
from core_simple import suduko
from typing import Optional
def direct_interative_mode(*,allow_unchecked: bool = False, src: Optional[suduko] = None) -> abstract_game:
    tmp = abstract_game(src=src,replace_void = "x", column_sep = "|", allow_unchecked = allow_unchecked)
    print("Next: ", end="")  
    try:
        while True:
            x = tmp.step_encoded()
            if x is not None:
                print("Done!")
                if not x:
                    break
            print("Next: ", end="")
    except KeyboardInterrupt:
        print("\nExited!")
        return tmp
    except Exception as E:
        raise E
        print("Critical Error!")
        return tmp
    #finally:
        #return tmp

if __name__ == '__main__':
    # direct_interative_mode()
    # -----------------------
    # Debug Only - Caution
    direct_interative_mode(allow_unchecked = True)

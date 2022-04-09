from sock_encoder import abstract_game
def direct_interative_mode(*,allow_unchecked: bool = False) -> abstract_game:
    tmp = abstract_game(replace_void="x", allow_unchecked = allow_unchecked)
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
    except Exception as E:
        raise E
        print("Critical Error!")
    finally:
        return tmp

if __name__ == '__main__':
    # direct_interative_mode()
    # -----------------------
    # Debug Only - Caution
    direct_interative_mode(allow_unchecked = True)

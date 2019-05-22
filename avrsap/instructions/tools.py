from ..addressing import token_to_ptr, token_to_value

def load_args(seg, args, t1="ptr", t2="value"):
    funcs = {"ptr":token_to_ptr,"value":token_to_value}

    seg.write_seg(funcs[t1](args[0], 1))
    seg.write_seg(funcs[t2](args[1], 2))
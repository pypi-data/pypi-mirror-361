def print_time(msg: str, elapsed_time: float):
    in_ms = elapsed_time * 1000
    print(msg, f"took {in_ms:.3f} ms")

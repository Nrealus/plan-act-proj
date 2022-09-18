class GlobalCounter:
    counter = 0

def new_int_id():
    GlobalCounter.counter += 1
    return GlobalCounter.counter
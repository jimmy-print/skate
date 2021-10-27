import math

def deg(radangle):
    return radangle * 180 / math.pi

def rad(degangle):
    return degangle * (math.pi / 180)

def all_same(items):
    return all(x == items[0] for x in items)

def all_unique(x):
    seen = set()
    return not any(i in seen or seen.add(i) for i in x)

def extract_sign(x):
    return x / abs(x)
import math
import os                 # blacklisted by import blacklist -> becomes `this`
from random import randint

# requests is blacklisted in config.blacklist (used below via attribute)
def run():
    for i in range(2):
        pass
    if randint() > 0:
        pass
    try:
        pass
    except Exception:
        pass

# attribute access on a blacklisted name should set alert + rename base
ref = requests.get

# attribute call on blacklisted base should rewrite to alertFunc
x = requests.post('http://example.com')

# plain name call not in blacklist should be kept
y = randint()
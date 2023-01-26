import time
import os
from pprint import pprint

for i in range(10**2):
    print(f"a: {i}")

pprint(dict(os.environ))
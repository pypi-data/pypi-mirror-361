import time
class pos():
    def __init__(self, x=0, y=0):
        self.x = x
        self.y = y
class clock():
    def __init__(self, h=0, m=0, s=0):
        self.h = h
        self.m = m
        self.s = s
    def str(self, a='0:0:0'):
        x=a.split(':')
        self.h = int(x[0])
        self.m = int(x[1])
        self.s = int(x[2])
    def put(self):
        return f'{self.h}:{self.m}:{self.s}'
    #更新为实时时间
    def get(self):
        self.h = time.localtime().tm_hour
        self.m = time.localtime().tm_min
        self.s = time.localtime().tm_sec

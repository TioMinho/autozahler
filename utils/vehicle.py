# -*- coding: utf-8 -*-
from random import randint
import numpy as np
import time

class Vehicle:
    tracks = []
    def __init__(self, i, xi, yi, wi, hi, max_age):
        self.id = i
        self.x = xi
        self.y = yi
        self.w = wi
        self.h = hi
        self.tracks = []
        self.done = False
        self.state = '0'
        self.age = 0
        self.max_age = max_age
    
    def updateCoords(self, xn, yn, wn, hn):
        self.age = 0
        self.tracks.append([self.x, self.y, self.w, self.h])
        self.x = xn
        self.y = yn
        self.w = wn
        self.h = hn
    
    def getSize(self):
        return np.array(self.tracks).mean(axis=0)[2:]

    def setDone(self):
        self.done = True
    
    def timedOut(self):
        return self.done
    
    def crossed_line(self, mid_start, bottom_start):
        if len(self.tracks) >= 2:
            if self.state == '0':
                if self.tracks[-1][0] >= mid_start and self.tracks[-2][0] <= mid_start and self.tracks[-1][1] <= bottom_start:
                    self.state = '1'
                    return True
            else:
                return False
        else:
            return False

    def age_one(self):
        self.age += 1
        if self.age > self.max_age:
            self.done = True
        return True

class MultiPerson:
    def __init__(self, persons, xi, yi):
        self.vehicles = vehicles
        self.x = xi
        self.y = yi
        self.tracks = []
        self.done = False
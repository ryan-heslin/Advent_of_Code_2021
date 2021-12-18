#! /usr/bin/env python3

import re
with open('inputs/day17.txt') as f:
    raw_input = f.read()

#target_x, target_y = *
processed = [ int(x) for x in re.findall('-?\d+', raw_input) ] 
xmin, xmax, ymin, ymax = processed

#answer1 =

#answer2 =
#print(f"Answer 2 = {answer2}")

class Trajectory():
    def __init__(self, x, y, xmin, xmax, ymin, ymax):
        self.x =  self.y = 0
        self.apogee = -10000000
        self.hit = False
        self.xvel = x
        self.yvel =  y
        self.x_sign = 1 if x <0 else -1 if x > 0 else 0
        self.xmin, self.xmax, self.ymin, self.ymax = xmin, xmax, ymin, ymax

    # Simulate Trajectory; return True if target entered, false if beyond bounds
    def step(self, mode):
        while True:
            self.x += self.xvel 
            self.y += self.yvel
            self.apogee = max(self.y, self.apogee)
            self.xvel += self.x_sign
            self.x_sign = 0 if self.xvel == 0 else self.x_sign
            self.yvel += -1
            if (self.x >= self.xmin and self.x <=self.xmax and
                    self.y >= self.ymin and self.y <=self.ymax):
                self.hit = True
            if self.y < self.ymin and self.yvel <= 0:
                if mode == 'part1':
                    return -1000 if not self.hit else self.apogee
                else:
                    return self.hit

    def __repr__(self):
        return f'x: {self.x}, y: {self.y}'

trajectories = [Trajectory(x, y, xmin, xmax, ymin, ymax) for x in range(xmax + 1) for y in range(-2000, 2000)]

apogees = [traj.step('part1') for traj in trajectories]

answer1 = max(apogees)

answer2 = sum([traj.step('part2') for traj in trajectories])

print(f"Answer 1 = {answer1}")
print(f"Answer 2 = {answer2}")

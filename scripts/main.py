G = 0.5
Vmax = -10

import random
import math

class Bird(object):
    def __init__(self, x = 0):
        self.x = x
        self.reset()

    def reset(self):
        self.pos = 400
        self.vel = -10
        self.acc = G
        self.survivetime = 0

    def fly(self, accel = 0):
        self.acc = G + accel
        self.vel += self.acc
        if self.vel <= Vmax:
            self.vel = Vmax
        self.pos += self.vel
        if self.pos <= -150:
            self.pos = -150
        
        self.survivetime += 1
    
    def flap(self):
        self.fly(-100)


class Obstacle(object):
    def __init__(self, min=0, max=720, size=250, x=1000, pos = None):
        # self.pos = 0
        # self.x = 1000
        self.init_params = {"min": min, "max": max, "size" : size, "x": x, "pos": pos}
        self.reset()

    def reset(self):
        if self.init_params["pos"] is None:
                self.generate_random(min=self.init_params["min"], max=self.init_params["max"], size=self.init_params["size"], x=self.init_params["x"])
        else:
            self.generate(pos=self.init_params["pos"], x=self.init_params["x"])


    def generate(self, pos = 0, x=1000):
        self.pos = pos
        self.x = x
    
    def generate_random(self, min=0, max=720, size=250, x=1000):
        self.pos = random.randint(min, max-size)
        self.x = x
    
    def move(self):
        self.x -= 5


class Score(object):
    def __init__(self):
        self.point = 0.
        self.attempt = 0
        self.factor = 1.
    
    def reset(self):
        self.point = 0.
        self.attempt += 1

    def gain(self):
        self.point += 1.
    


class Game(object):

    def __init__(self, window_size_x = 1600, window_size_y = 900, obstacle_gap_x = 500, obstacle_gap_y = 280, obstacle_width = 165, bird_x = 300, bird_size_x = 75, bird_size_y = 60):
        
        self.window_size_x = window_size_x
        self.window_size_y = window_size_y
        self.obstacle_gap_x = obstacle_gap_x
        self.obstacle_gap_y = obstacle_gap_y
        self.obstacle_width = obstacle_width
        self.bird_x = bird_x
        self.bird_size_x = bird_size_x
        self.bird_size_y = bird_size_y
    
        self.nbr_obstacles = self.window_size_x // (self.obstacle_gap_x - self.obstacle_width) + 1
        self.set_up()
        self.time = 0
        

    def set_up(self):
        self.B = Bird(self.bird_x)
        self.O = []
        for i in range(self.nbr_obstacles):
            self.O.append(Obstacle(min=0, max=self.window_size_y, size=self.obstacle_gap_y, x=500+(i+1)*self.obstacle_gap_x))
        self.S = Score()
        self.IOI = 0  # Incoming Obstacle Index
        

    def reset(self):
        self.B.reset()
        for i in range(self.nbr_obstacles):
            self.O[i].reset()
        self.S.reset()
        self.IOI = 0
        self.time = 0
    
    def run(self, action = 0):
        if action:
            self.B.fly(-100)
        else:
            self.B.fly()

        if self.B.pos <= -50: self.B.pos = -50

        for i in range(len(self.O)):
            self.O[i].move()

            if self.O[i].x < - self.obstacle_gap_x:
                self.O[i].generate_random(min=0, max=self.window_size_y, size=self.obstacle_gap_y, x=self.O[i-1].x + self.obstacle_gap_x)

            # dist_obstacle_bird = self.O[i].x + self.obstacle_width - self.B.x
            dist_obstacle_bird = self.O[self.IOI].x + self.obstacle_width - self.B.x
            if dist_obstacle_bird < 0: dist_obstacle_bird = self.window_size_y * 10
            if self.O[i].x + self.obstacle_width >= self.B.x and (self.O[i].x + self.obstacle_width - self.B.x < dist_obstacle_bird): 
                self.S.gain()
                self.IOI = i

        alive = float(not self.game_over())
        if alive: self.time += 1
        # print([self.B.pos, self.B.vel, self.O[self.IOI].x, self.O[self.IOI].pos])
        # print(self.time)
        return([self.B.pos, self.B.vel, self.O[self.IOI].x, self.O[self.IOI].pos], self.time, alive, float(action))



    def game_over(self):

        # collision ground
        if self.B.pos >= self.window_size_y - self.bird_size_y:
            return True
        
        # collision obstacles
        if (self.bird_x + self.bird_size_x > self.O[self.IOI].x and self.bird_x < self.O[self.IOI].x + self.obstacle_width) and (self.B.pos < self.O[self.IOI].pos -5 or self.B.pos + self.bird_size_y > self.O[self.IOI].pos + self.obstacle_gap_y +5):
            return True
        
        # NOT DEAD :)
        return False


    def game_over_easy(self):
        if self.B.pos >= self.window_size_y - self.bird_size_y: return True
        if self.B.pos < 0: return True
        return False

    def event(self):
        # self.B.flap()
        # self.bird_acc = -100
        pass






if __name__ == '__main__':
    b = Bird(50)
    positions = []
    for i in range(100):
        if i == 55 or i == 30:
            b.flap()
        else:
            b.fly()
        positions.append(b.pos)
        # print(b.pos)

    import matplotlib.pyplot as plt
    plt.plot(positions)
    plt.gca().invert_yaxis()
    plt.ylabel('bird y')
    plt.show()
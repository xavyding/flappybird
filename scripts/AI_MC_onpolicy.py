try:from main import Game
except:from scripts.main import Game
# from collections import Counter
import random
import numpy as np

import matplotlib.pyplot as plt


WINDOW_SIZE_X = 1600
WINDOW_SIZE_Y = 900
OBSTACLE_GAP = 280
# OBSTACLE_GAP = 900
OBSTACLE_GAPX = 600
OBSTACLE_WIDTH = 165 

BIRD_X = 300
BIRD_SIZE = 60
BIRD_SIZEX = BIRD_SIZE + 0.3*BIRD_SIZE

SCALE_FACTOR = 10
EPSILON = 0.05
GAMMA = 0.9
ACTION_COOLDOWN = 10
# ALPHA = 0.5
ALPHA = 0.2

class AI(object):
    def __init__(self):
        self.player_action = 0
        self.cooldown = 0

        self.G = Game(
            window_size_x = WINDOW_SIZE_X, 
            window_size_y = WINDOW_SIZE_Y, 
            obstacle_gap_x = OBSTACLE_GAPX, 
            obstacle_gap_y = OBSTACLE_GAP, 
            obstacle_width = OBSTACLE_WIDTH, 
            bird_x = BIRD_X, 
            bird_size_x = BIRD_SIZEX, 
            bird_size_y = BIRD_SIZE
        )


        #action value function
        # self.Q = np.zeros((int(WINDOW_SIZE_Y/SCALE_FACTOR), 120, int(WINDOW_SIZE_X/SCALE_FACTOR), int(WINDOW_SIZE_Y/SCALE_FACTOR), 2)) #states = bird position, bird velocity, next pipe distance, next pipe position. action: flap, not flap
        self.Q = np.zeros((int(WINDOW_SIZE_Y/SCALE_FACTOR), 2, int(WINDOW_SIZE_X/SCALE_FACTOR), int(WINDOW_SIZE_Y/SCALE_FACTOR), 2)) #states = bird position, bird velocity, next pipe distance, next pipe position. action: flap, not flap

        # returns
        # self.R = np.zeros((int(WINDOW_SIZE_Y/SCALE_FACTOR), 120, 2)) #states = bird position, bird velocity, action: flap, not flap

        self.epsilon = EPSILON #e-greedy
        self.gamma = GAMMA #discount
        self.expectreturn_debug = []


    def load_data(self):
        self.Q = np.load(r"Q.npy", allow_pickle=True)
        # self.R = np.load(r"R.npy", allow_pickle=True)
    
    def export_data(self):
        # np.save(folder+"/Q", np.asarray(self.Q))
        # np.save(folder+"/R", np.asarray(self.R))
        np.save("Q", np.asarray(self.Q))
        # np.save("R", np.asarray(self.R))

    def convert_obs_to_state(self, observer):
        if observer[1] < 0: pitch = 0 #bird flapping
        else: pitch = 1 #bird dropping
        state = [
            int(observer[0]/SCALE_FACTOR),
            pitch,
            int(observer[2]/SCALE_FACTOR),
            int(observer[3]/SCALE_FACTOR)
        ]

        return(state)



    def prediction(self, state):
        epsi = random.random()
        if self.Q[state[0], state[1], state[2], state[3], 0] > self.Q[state[0], state[1], state[2], state[3], 1]:
            #not flap default
            if epsi <= 1-self.epsilon/2: player_action = 0
            else: player_action = 1

        elif self.Q[state[0], state[1], state[2], state[3], 0] < self.Q[state[0], state[1], state[2], state[3], 1]:
            #flap default
            if epsi <= 1-self.epsilon/2: player_action = 1
            else: player_action = 0
        else:
            player_action = random.randint(0,1)

        return(player_action)




    def play(self, ending_episodes=np.inf, export=True):
        episode = 0
        expectreturn_temp = []
        while episode < ending_episodes:
            self.G.reset()
            
            episode += 1
            alive = 1
            # print("episode: #{}".format(episode))

            self.actions = []
            self.states = []

            #init once
            # observer, time, alive, flapped = self.G.run(random.randint(0,1))
            # state = [
            #     int(self.G.B.pos/SCALE_FACTOR), 
            #     int(self.G.B.vel*2 + 20), 
            #     int(self.G.O[self.G.IOI].x/SCALE_FACTOR), 
            #     int(self.G.O[self.G.IOI].pos/SCALE_FACTOR)
            # ]
            state = self.convert_obs_to_state([self.G.B.pos, self.G.B.vel, self.G.O[self.G.IOI].x, self.G.O[self.G.IOI].pos])
            self.states.append(state)

            while alive: #roll the game
                if self.cooldown < ACTION_COOLDOWN:
                    observer, time, alive, flapped = self.G.run(0)
                    self.cooldown += 1
                    continue
                
                self.cooldown = 0

                player_action = self.prediction(state)
                # player_action = random.randint(0,1)

                observer, time, alive, flapped = self.G.run(player_action)
                # print("---------------------", alive)
                self.actions.append(int(flapped))
                # state = [
                #     int(observer[0]/SCALE_FACTOR),
                #     int(observer[1]*2 + 20),
                #     int(observer[2]/SCALE_FACTOR),
                #     int(observer[3]/SCALE_FACTOR)
                # ]
                state = self.convert_obs_to_state(observer)
                self.states.append(state) #last state is the ending state, and we dont need it
            # print("-------------------")
            #one episode if over, now backprop in update Q
            G = 0

            le = len(self.actions)
            expectreturn_temp.append(le)
            if episode%100 == 0:
                self.expectreturn_debug.append(np.mean(expectreturn_temp))
                expectreturn_temp = []
                # plt.scatter(int(episode/100), self.expectreturn_debug[-1])
                # plt.pause(0.05)
            
            # if episode%1000 ==0:print(le, "---", self.states[-2][0], self.states[-2][1],self.Q[self.states[-2][0], self.states[-2][1], 0])
            if episode%1000 == 0:print(le, "--- ",int(episode/1000)," ---", self.states[0][0], self.states[0][1], self.Q[self.states[0][0], self.states[0][1], self.states[0][2],self.states[0][3],0], self.Q[self.states[0][0], self.states[0][1], self.states[0][2],self.states[0][3],1])
            
            for i in range(le):
                t = le - i -1
                # print(t, G)
                # print(i+10)

                state = self.states[t]
                action = self.actions[t]

                G = self.gamma*G + 1 #constant reward
                # self.R[state[0], state[1], action] += G #reward
                # self.Q[state[0], state[1], action] = self.R[state[0], state[1], action] / (i+1)
                self.Q[state[0], state[1], state[2], state[3], action] = self.Q[state[0], state[1], state[2], state[3], action] + ALPHA*(G - self.Q[state[0], state[1], state[2], state[3], action])
                
            if episode%2e6 ==0 and export:
                self.export_data()
        # plt.show()
        if export:
            self.export_data()
        




if __name__ == "__main__":
    ai = AI()
    # ai.play(1000000)
    # ai.load_data()
    # print(ai.Q)

    # ai.play(5e7,True)
    ai.play(5e7,False)

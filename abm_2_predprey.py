# %%

import numpy as np
from scipy.spatial import distance as spd
import matplotlib.pyplot as plt
import pygame
from PIL import Image
import time
import os
import sys



RES_X = 512
RES_Y = 512
DT = 0.1
STR_LENGTH = 3
N_PREDATORS = 100
N_PREYS = 200
RADIUS_1 = 2
RADIUS_2 = 12
rng = np.random.default_rng()

# %%

 
class Agent(object):
    def __init__(self, env, phi = None, x=None, y=None, dx=0, dy=0):
        self.env = env
        if x is None:
            self.x = np.random.randint(RES_X)
        if y is None:            
            self.y = np.random.randint(RES_Y)
        self.dx = dx
        self.dy = dy
        self.neighbors = []
        self.distances = []

        if phi is not None:
            self.phi = phi

        self.state = np.array([self.x, self.y, self.dx, self.dy])
    
    def __repr__(self) -> str:
        return "Agent: x = {}, y = {}, dx = {}, dy = {}".format(self.x, self.y, self.dx, self.dy)

    def get_neighborhood(self):
        
        self.neighbors = []
        self.distances = []

        for agent in self.env.agents:
            distance = np.sqrt((agent.x - self.x)**2 + (agent.y - self.y)**2)
            if agent is not self:
                if distance <= RADIUS:
                    self.neighbors.append(agent)
                    self.distances.append(distance)
        
        # self.neighbors = list(set(list(zip(self.distances, self.neighbors))))              


    def update(self):
        self.state = self.phi()
    
    def phi(self):
        
        #sensorial input
        self.get_neighborhood()
        #compute action
        self.dx = np.random.choice(list(range(-RES_X//8, RES_X//8)))
        self.dy = np.random.choice(list(range(-RES_Y//8, RES_Y//8)))

        #update state
        self.x = (self.x + self.dx) % RES_X
        self.y = (self.y + self.dy) % RES_Y
        state = np.array([self.x, self.y, self.dx, self.dy])
        return state


class Predator(Agent):
    def __init__(self, env, phi=None, x=np.random.randint(RES_X), y=np.random.randint(RES_Y), dx=0, dy=0, L=STR_LENGTH):
        super().__init__(env)
        self.L = L
        self.neighbors = dict(predators = [], preys = [])
        self.local_readings = [np.array([prey, prey.x, prey.y, prey.dx, prey.dy]) for prey in self.neighbors["preys"]] 
        self.message = self.local_readings
        self.eaten = 0
        if phi is not None:
            self.phi = phi
        # self.state = np.array([x, y, dx, dy, self.local_readings, self.message, self.neighbors, self.phi])
        self.state = np.array([self.x, self.y, self.dx, self.dy, self.local_readings, self.message, self.neighbors])

    def get_neighborhood(self):
        self.neighbors["preys"] = []
        self.local_readings = []    
        for prey in self.env.preys:
            # distance = np.sqrt((prey.x - self.x)**2 - (prey.y - self.y)**2)
            distance = spd.cityblock((self.x, self.y), (prey.x, prey.y))
            print(distance)
            if RADIUS_1 < distance <= RADIUS_2:
                # print(1)
                self.neighbors["preys"].append(prey)
                self.local_readings.append(np.array([prey, prey.x, prey.y, prey.dx, prey.dy, distance]))
            elif distance <= RADIUS_1:
                self.env.preys.remove(prey)
                self.eaten += 1

        # for pred in self.env.pred:
        #     if np.sqrt((pred.x - self.x)**2 - (pred.y - self.y)**2) <= RADIUS:
        #         self.neighbors["predators"].append(pred)                
    
    def __repr__(self) -> str:
        return "Predator: x = {}, y = {}, dx = {}, dy = {}".format(self.x, self.y, self.dx, self.dy)


    def update(self):
        self.state = self.phi()
    
    def phi(self):
        
        board = self.env.message_board
        
        #update local sensorial input
        self.get_neighborhood()
        #conjoint inputs
        total_inputs = self.local_readings + board.messages
        #process messages
        min_dist = RES_Y*RES_X
        min_index = 0
        for i in range(len(total_inputs)):
            if total_inputs[i][-1] < min_dist:
                min_dist = total_inputs[i][-1]
                min_index = i 
        try:
            self.dx, self.dy = (np.array([total_inputs[min_index][1], total_inputs[min_index][2]]) - np.array([self.x, self.y]))*DT
        except IndexError:
            self.dx = np.random.choice(list(range(-RES_X//8, RES_X//8)))*DT
            self.dy = np.random.choice(list(range(-RES_Y//8, RES_Y//8)))*DT            
        #messages are up to L sensorial inputs from the agent
        if len(self.local_readings) > 0:
            self.message = [prey for prey in list(rng.choice(self.local_readings, self.L))]
        else:
            self.message = []
        # print(self.message)
        self.env.message_board.messages + self.message
        #update state
        self.x = (self.x + int(self.dx)) % RES_X
        self.y = (self.y + int(self.dy)) % RES_Y

        return np.array([self.x, self.y, self.dx, self.dy, self.local_readings, self.message, self.neighbors])


class Prey(Agent):
    def __init__(self, env, phi=None, x=np.random.randint(RES_X), y=np.random.randint(RES_Y), dx=0, dy=0):
        super().__init__(env)
        
        self.neighbors = dict(predators = [], preys = [])
        self.local_readings = [np.array([pred, pred.x, pred.y, pred.dx, pred.dy]) for pred in self.neighbors["predators"]] 
        
        if phi is not None:
            self.phi = phi
        
        self.state = np.array([self.x, self.y, self.dx, self.dy, self.local_readings, self.neighbors])

    def get_neighborhood(self):
        # distance = np.sqrt((prey.x - self.x)**2 - (prey.y - self.y)**2)
        self.neighbors["predators"] = []
        self.local_readings = []    
        for pred in self.env.predators:
            distance = spd.cityblock((self.x, self.y), (pred.x, pred.y))
            if distance <= RADIUS_2:
                self.neighbors["predators"].append(pred)
                self.local_readings.append(np.array([pred, pred.x, pred.y, pred.dx, pred.dy, distance]))

        # for pred in self.env.pred:
        #     if np.sqrt((pred.x - self.x)**2 - (pred.y - self.y)**2) <= RADIUS:
        #         self.neighbors["predators"].append(pred)                
    
    def __repr__(self) -> str:
        return "Prey: x = {}, y = {}, dx = {}, dy = {}".format(self.x, self.y, self.dx, self.dy)


    def update(self):
        self.state = self.phi()
    
    def phi(self):

        #update local sensorial input
        self.get_neighborhood()

        #get closest predator

        min_dist = RES_Y*RES_X
        min_index = 0
        for i, reading in enumerate(self.local_readings):
            if self.local_readings[i][-1] < min_dist:
                min_dist = self.local_readings[i][-1]
                min_index = i 
        
        #run
        # print(self.local_readings)
        # print(min_index)
        try:
            self.dx, self.dy = (np.array([self.x, self.y]) - np.array([self.local_readings[min_index][1], self.local_readings[min_index][2]]))*DT
        except IndexError:
            self.dx = np.random.choice(list(range(-RES_X//8, RES_X//8)))*DT
            self.dy = np.random.choice(list(range(-RES_Y//8, RES_Y//8)))*DT

        #update state

        self.x = (self.x + int(self.dx)) % RES_X
        self.y = (self.y + int(self.dy)) % RES_Y

        return np.array([self.x, self.y, self.dx, self.dy, self.local_readings, self.neighbors])


class Environment(object):
    def __init__(self, num_agents = 100):

        self.agents = [Agent(self) for i in range(num_agents)]
        self.board = np.zeros((RES_X, RES_Y, 3), dtype=np.uint8)

    def update(self):
        self.board = np.zeros((RES_X, RES_Y, 3), dtype=np.uint8)
        for a in self.agents:
            self.board[a.x, a.y] = np.array([255, 0, 0], dtype=np.uint8)
            a.update()


class MessageBoard(object):
    def __init__(self, env):
        self.env = env
        self.messages = []


    def __str__(self):
        for m in self.messages:
            print(m)


class PreyPredatorEnvironment(Environment):
    def __init__(self, num_predators, num_preys):
        super().__init__()
        self.predators = [Predator(self) for i in range(num_predators)]
        self.preys = [Prey(self) for i in range(num_preys)]
        self.message_board = MessageBoard(self)
        self.board = np.zeros((RES_X, RES_Y, 3), dtype=np.uint8)
    
    def update(self):
        self.message_board.messages = []
        self.board = np.zeros((RES_X, RES_Y, 3), dtype=np.uint8)
        for pred in self.predators:
            pred.update()
            self.board[pred.x, pred.y] = np.array([255, 0, 0], dtype=np.uint8)
        for prey in self.preys:
            prey.update()
            self.board[prey.x, prey.y] = np.array([0, 255, 0], dtype=np.uint8)

# %%
env = PreyPredatorEnvironment(N_PREDATORS, N_PREYS)

# %%
env.message_board.messages
# %%

pygame.init()
screen = pygame.display.set_mode((RES_X, RES_Y), flags = 0)
screen.fill(0)



# %%
quit_loop = False

while not quit_loop:
    
    keys=pygame.key.get_pressed()
    env.update()
    
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.display.quit()
            quit_loop = True

        if keys[pygame.K_ESCAPE]:            
            pygame.display.quit()
            quit_loop = True

    im = env.board

    pygame.surfarray.blit_array(screen, im)
    pygame.display.update()   
    time.sleep(0.05)
# %%

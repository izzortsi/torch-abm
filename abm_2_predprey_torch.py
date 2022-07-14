# %%

import numpy as np
from scipy.spatial import distance as spd
import matplotlib.pyplot as plt
import pygame
from PIL import Image
import time
import os
import sys
import torch as t
import torch.nn as nn
import torch.nn.functional as F


RES_X = 512
RES_Y = 512
# RES_X = 1024
# RES_Y = 1024
DT = 0.08
STR_LENGTH = 3
N_PREDATORS = RES_X//8
N_PREYS = RES_X//2
RADIUS_1 = RES_X//128
RADIUS_2 = RES_X//32
rng = np.random.default_rng()
DISTANCE = lambda a1, a2: np.sqrt((a1.x - a2.x)**2 + (a1.y - a2.y)**2)
# DISTANCE = lambda a1, a2: spd.cityblock(np.array([a1.x, a1.y]), np.array([a2.x, a2.y]))
 
class Agent(object):
    def __init__(self, env, id, phi = None, x=None, y=None, dx=0, dy=0):
        self.env = env
        self.id = id
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
                if distance <= (RADIUS_1 +RADIUS_2)//2:
                    self.neighbors.append(agent)
                    self.distances.append(distance)
        
        # self.neighbors = list(set(list(zip(self.distances, self.neighbors))))              


    def update(self):
        self.state = self.phi()
    
    def phi(self):
        
        #sensorial input
        self.get_neighborhood()
        #compute action
        self.dx = np.random.choice(list(range(-RES_X//8, RES_X//8)))*DT
        self.dy = np.random.choice(list(range(-RES_Y//8, RES_Y//8)))*DT

        #update state
        self.x = (self.x + self.dx) % RES_X
        self.y = (self.y + self.dy) % RES_Y
        state = np.array([self.x, self.y, self.dx, self.dy])
        return state


class Predator(Agent):
    def __init__(self, env, id, phi=None, x=np.random.randint(RES_X), y=np.random.randint(RES_Y), dx=0, dy=0):
        super().__init__(env, id)
        self.L = self.env.L
        self.neighbors = dict(predators = [], preys = [])
        self.local_readings = [(prey, DISTANCE(self, prey)) for prey in self.neighbors["preys"]] 
        self.message = self.neighbors["preys"]
        self.eaten = 0
        if phi is not None:
            self.phi = phi
        self.state = np.array([self.x, self.y, self.dx, self.dy, self.local_readings, self.message, self.neighbors])

    def get_neighborhood(self):

        self.neighbors["preys"] = []
        self.local_readings = []  

        for prey in self.env.preys:
            distance = DISTANCE(self, prey)

            if RADIUS_1 < distance <= RADIUS_2+2*self.eaten:

                self.neighbors["preys"].append(prey)
                self.local_readings.append((prey, distance))
        # for pred in self.env.pred:
        #     if np.sqrt((pred.x - self.x)**2 - (pred.y - self.y)**2) <= RADIUS:
        #         self.neighbors["predators"].append(pred)                
    
    def __repr__(self) -> str:
        return "Predator {}; Eaten = {} ".format(self.id, self.eaten)

    def update(self):
        self.L = self.env.L
        self.state = self.phi()
    
    def phi(self):
        
        board = self.env.message_board
        
        #update local sensorial input
        self.get_neighborhood()
        # if len(self.local_readings) > 0 or len(board.messages) > 0:
        #     print(f"local readings: {self.local_readings}\n")
        #     print(f"neighborhood: {self.neighbors['preys']} \n")
        #     print(f"board messages: {board.messages}\n")
        #conjoint inputs
        # total_inputs = self.local_readings + board.messages
        total_inputs = self.neighbors["preys"] + board.messages
        #process messages
        # print(total_inputs)
        min_dist = RES_Y*RES_X
        min_index = 0
        closest_prey = None
        for i in range(len(total_inputs)):
            closest_prey = total_inputs[i]
            distance = DISTANCE(self, closest_prey)
            if distance < min_dist:
                min_dist = distance
                min_index = i 
                closest_prey = total_inputs[i]

        try:
            # print((np.array([total_inputs[min_index][1], total_inputs[min_index][2]]) - np.array([self.x, self.y]))*DT)
            self.dx, self.dy = (np.array([closest_prey.x, closest_prey.y]) - np.array([self.x, self.y]))*DT
            self.x = (self.x + int(self.dx)) % RES_X
            self.y = (self.y + int(self.dy)) % RES_Y
            if DISTANCE(self, closest_prey) < RADIUS_1:
                # print(closest_prey)
                self.eaten += 1
                self.env.preys.remove(closest_prey)
                self.env.message_board.messages.remove(closest_prey)
                if (closest_prey, distance) in self.local_readings:
                        self.local_readings.remove((closest_prey, distance))
                if closest_prey in self.neighbors["preys"]:    
                        self.neighbors["preys"].remove(closest_prey)
        except Exception as e:
            self.dx = np.random.choice(list(range(-RES_X//8, RES_X//8)))*DT
            self.dy = np.random.choice(list(range(-RES_Y//8, RES_Y//8)))*DT   
            self.x = (self.x + int(self.dx)) % RES_X
            self.y = (self.y + int(self.dy)) % RES_Y                  
        #messages are up to L sensorial inputs from the agent
        if len(self.neighbors["preys"]) > 0:
            # self.message = [list(prey_reading) for prey_reading in list(rng.choice(self.local_readings, self.env.L)) if not (prey_reading[0] in [reading[0] for reading in board.messages])]
            message = [
                prey for prey in list(
                    rng.choice(self.neighbors["preys"], 
                    min(len(self.neighbors["preys"]), self.env.L), 
                    replace=False)
                    )
                ]
            # print(message)
            # board_ids = [m[0].id for m in board.messages]
            for prey in message:
                # print(prey)
                if prey not in self.env.message_board.messages:
                    self.message.append(prey)
                    self.env.message_board.messages.append(prey)
                # if m[0].id not in board_ids:
                    # self.message.append(m) 
            # print(self.message, len(self.message))
        else:
            self.message = []
        
               

        return np.array([self.x, self.y, self.dx, self.dy, self.local_readings, self.message, self.neighbors])


class Prey(Agent):
    def __init__(self, env, id, phi=None, x=np.random.randint(RES_X), y=np.random.randint(RES_Y), dx=0, dy=0):
        super().__init__(env, id)
        
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
            distance = DISTANCE(self, pred)
            if distance <= RADIUS_2:
                self.neighbors["predators"].append(pred)
                self.local_readings.append(np.array([pred, pred.x, pred.y, pred.dx, pred.dy, distance]))

        # for pred in self.env.pred:
        #     if np.sqrt((pred.x - self.x)**2 - (pred.y - self.y)**2) <= RADIUS:
        #         self.neighbors["predators"].append(pred)                
    
    def __repr__(self) -> str:
        return "Prey {}".format(self.id)
        # return "Prey {}: x = ({}, {}), dx/dt = ({}, {})".format(self.id, self.x, self.y, self.dx, self.dy)


    def update(self):
        self.state = self.phi()
    
    def phi(self):

        #update local sensorial input
        
        self.dx = np.random.choice(list(range(-RES_X//8, RES_X//8)))*DT
        self.dy = np.random.choice(list(range(-RES_Y//8, RES_Y//8)))*DT

        #update state

        self.x = (self.x + int(self.dx)) % RES_X
        self.y = (self.y + int(self.dy)) % RES_Y

        return np.array([self.x, self.y, self.dx, self.dy, self.local_readings, self.neighbors])

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
        # print((np.array([self.x, self.y]) - np.array([self.local_readings[min_index][1], self.local_readings[min_index][2]]))*DT)
        self.dx, self.dy = (np.array([self.x, self.y]) - np.array([self.local_readings[min_index][0].x, self.local_readings[min_index][0].y]))*DT
    except IndexError:
        self.dx = np.random.choice(list(range(-RES_X//8, RES_X//8)))*DT
        self.dy = np.random.choice(list(range(-RES_Y//8, RES_Y//8)))*DT
    #update state
    self.x = (self.x + int(self.dx)) % RES_X
    self.y = (self.y + int(self.dy)) % RES_Y
    return np.array([self.x, self.y, self.dx, self.dy, self.local_readings, self.neighbors])        


class Environment(object):
    def __init__(self, num_agents = 100):

        self.agents = [Agent(self, i) for i in range(num_agents)]
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

    @property
    def size(self):
        return len(self.messages)
        
    def __str__(self):
        for m in self.messages:
            print(m)


class PreyPredatorEnvironment(Environment):
    def __init__(self, num_predators, num_preys, str_length = STR_LENGTH):
        super().__init__()
        self.L = str_length
        self.predators = [Predator(self, i) for i in range(num_predators)]
        self.preys = [Prey(self, i) for i in range(num_preys)]
        self.message_board = MessageBoard(self)
        self.board = np.zeros((RES_X, RES_Y, 3), dtype=np.uint8)
    
    def get_fittest_predator(self):
        eaten = 0
        fittest = None 
        for pred in self.predators:
            if pred.eaten > eaten:
                eaten = pred.eaten
                fittest = pred
        return fittest                

    def update(self):
        self.message_board.messages = []
        self.board = np.zeros((RES_X, RES_Y, 3), dtype=np.uint8)
        for pred in self.predators:
            pred.update()
            # self.board[pred.x, pred.y] = np.array([255, int(min((N_PREDATORS/N_PREYS)*pred.eaten, 255)), int(min((N_PREDATORS/N_PREYS)*pred.eaten, 255))], dtype=np.uint8)
            self.board[pred.x, pred.y] = np.array([255, 0, 0], dtype=np.uint8)
            # print(self.message_board.messages)
        for prey in self.preys:
            prey.update()
            self.board[prey.x, prey.y] = np.array([0, 255, 0], dtype=np.uint8)

# %%


pygame.init()
screen = pygame.display.set_mode((RES_X, RES_Y), flags = 0)
screen.fill([0, 0, 0])
env = PreyPredatorEnvironment(N_PREDATORS, N_PREYS)

quit_loop = False
preys_left = dict()
_iter = 0
while not quit_loop:
    
    keys=pygame.key.get_pressed()
    env.update()
    
    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            pygame.quit()
            quit_loop = True
            sys.exit()

        if keys[pygame.K_ESCAPE]:            
            pygame.quit()
            quit_loop = True
            sys.exit()

    im = env.board
    xim = Image.fromarray(im, mode="RGB")
    xim.save(f"frames/frame{_iter:04d}.jpg")
    # print(env.message_board.messages)

    pygame.surfarray.blit_array(screen, im)
    pygame.display.update()
    _iter += 1
    preys_left[_iter] = len(env.preys)
    if _iter % 20 == 0:
        print(f"{preys_left[_iter]} preys left at the {_iter}-th iteration.\n")
        print(f"Fittest predator: {env.get_fittest_predator()}.\n")
    if _iter % 100 == 0:
        STR_LENGTH += 1
        env.L = STR_LENGTH
        print(f"Increasing communication channel's size by 1; it's now: {STR_LENGTH}.\n")
        print(f"Message board size: {env.message_board.size}.\n")
        print(f"Message board messages: {env.message_board.messages}.\n")
    if len(env.preys) == 0:
        print("No preys left.")
        pygame.quit()
        quit_loop = True
        time.sleep(0.5)
        sys.exit()
    time.sleep(0.01)
# %%

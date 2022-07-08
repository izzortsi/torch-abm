
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
N_PREDATORS = 30
N_PREYS = 80
# RADIUS = (RES_X*RES_Y)/(N_PREYS+N_PREDATORS)**2
RADIUS = (RES_X*RES_Y)//(N_PREYS+N_PREDATORS)**2
print(RADIUS)
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
        if phi is not None:
            self.phi = phi
        # self.state = np.array([x, y, dx, dy, self.local_readings, self.message, self.neighbors, self.phi])
        self.state = np.array([self.x, self.y, self.dx, self.dy, self.local_readings, self.message, self.neighbors])

    def get_neighborhood(self):
        # distance = np.sqrt((prey.x - self.x)**2 - (prey.y - self.y)**2)
        self.neighbors["preys"] = []
        self.local_readings = []    
        for prey in self.env.preys:
            distance = spd.cityblock((self.x, self.y), (prey.x, prey.y))
            if distance <= RADIUS:
                self.neighbors["preys"].append(prey)
                self.local_readings.append(np.array([prey, prey.x, prey.y, prey.dx, prey.dy, distance]))

        # for pred in self.env.pred:
        #     if np.sqrt((pred.x - self.x)**2 - (pred.y - self.y)**2) <= RADIUS:
        #         self.neighbors["predators"].append(pred)                
    
    def __repr__(self) -> str:
        return "Agent: x = {}, y = {}, dx = {}, dy = {}".format(self.x, self.y, self.dx, self.dy)


    def update(self):
        self.state = self.phi(self.env)
        self.x = self.state[0]
        self.y = self.state[1]
        self.dx = self.state[2]
        self.dy = self.state[3]
        self.message = self.state[4]
        self.phi = self.state[5]
    
    def phi(self):
        
        board = self.env.message_board
        
        #update local sensorial input
        self.get_neighborhood()
        #conjoint inputs
        total_inputs = list(set(self.local_readings + list(board.messages)))
        #process messages
        min_dist = RES_Y*RES_X
        min_index = 0
        for i in range(len(total_inputs)):
            if total_inputs[i][-1] < min_dist:
                min_dist = total_inputs[i][-1]
                min_index = i 
        self.dx, self.dy = (np.array([total_inputs[min_index][1], total_inputs[min_index][2]]) - np.array([self.x, self.y]))*DT

        #messages are up to L sensorial inputs from the agent
        self.message = rng.choice(self.local_readings, self.L)
        

        #determine move

        #determine message

        #update state
        self.x = (self.x + self.dx) % RES_X
        self.y = (self.y + self.dy) % RES_Y

        #possibly update phi
        self.phi = self.phi


class Prey(Agent):
    def __init__(self, env, phi, x=np.random.randint(RES_X), y=np.random.randint(RES_Y), dx=0, dy=0):
        super().__init__(env, phi, x, y, dx, dy=dy)
        self.neighbors = dict(predators = [], preys = [])
        self.local_readings = [(predator, predator.x, predator.y, predator.dx, predator.dy) for predator in self.neighbors["predators"]] 
        self.phi = phi
        self.state = np.array([x, y, dx, dy, self.local_readings, self.neighbors])

    def get_neighborhood(self):

        for prey in self.env.preys:
            if np.sqrt((prey.x - self.x)**2 - (prey.y - self.y)**2) <= 1:
                self.neighbors["preys"].append(prey)

        for pred in self.env.pred:
            if np.sqrt((pred.x - self.x)**2 - (pred.y - self.y)**2) <= 1:
                self.neighbors["predators"].append(pred)                


    def update(self):
        self.state = self.phi(self.env)
        self.x = self.state[0]
        self.y = self.state[1]
        self.dx = self.state[2]
        self.dy = self.state[3]
        self.message = self.state[4]
        self.phi = self.state[5]
    
    def _phi(self):

        self.x = self.x + self.dx
        self.y = self.y + self.dy


class Environment(object):
    def __init__(self, screen, num_agents = 100):
        self.screen = screen
        self.agents = [Agent(self) for i in range(num_agents)]
        # self.board = np.zeros((RES_X, RES_Y, 3))
        self.board = np.zeros((RES_X, RES_Y, 3), dtype=np.uint8)

    def update(self):
        self.board = np.zeros((RES_X, RES_Y, 3), dtype=np.uint8)
        for a in self.agents:
            # self.board[a.x, a.y] = 255
            self.board[a.x, a.y] = np.array([255]*3, dtype=np.uint8)
            a.update()
            # self.screen.set_at((a.x, a.y), (0, 0, 0))

class MessageBoard(object):
    def __init__(self, env):
        self.env = env
        self.messages = {pred.message for pred in self.env.predators}


    def __str__(self):
        for m in self.messages:
            print(m)


class PreyPredatorEnvironment(Environment):
    def __init__(self, num_predators, num_preys):
        super().__init__(num_agents = num_predators + num_preys)
        self.predators = [Predator(self, phi_pred) for i in range(num_predators)]
        self.preys = [Prey(self, phi_prey) for i in range(num_preys)]
        # self.agents = {f"{i}": Agent() for i in range(num_agents)}
        self.message_board = MessageBoard(self)
        # self.agents_positions = np.array([np.array([self.agents[f"i"].x, self.agents[f"i"].y]) for i in range(num_agents)])
        # self.board = np.zeros((num_agents*3, num_agents*3))
    
    def update(self):
        for pred in self.predators:
            pred.update()
        for prey in self.preys:
            prey.update()

# %%
p = Predator(env)

# %%
p.x
# %%

p.env
# %%

# %%

pygame.init()
# screen = pygame.display.set_mode((RES_X, RES_Y), flags = 0, depth=24)
screen = pygame.display.set_mode((RES_X, RES_Y), flags = 0)
screen.fill(0)
env = Environment(screen, num_agents = 100)


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
    # im = np.clip(im, 0, 255).astype(np.uint8)

    # xim = Image.fromarray(im)

    # s_image = pygame.pixelcopy.make_surface(im)
    # screen.blit(s_image, (0, 0))
    pygame.surfarray.blit_array(screen, im)
    pygame.display.update()   
    time.sleep(0.05)
# %%

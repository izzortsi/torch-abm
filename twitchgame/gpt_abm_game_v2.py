#%%

import pygame
import random
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_CHARACTERS = 10
PERCEPTUAL_RADIUS_FACTOR = 10
MAX_SPEED = 5
MIN_LEVEL = 1
MAX_LEVEL = 10
NUM_LIVES = 3

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battling Simulation Game")

class Character:
    def __init__(self, x, y):
        self.level = MIN_LEVEL
        self.power = random.randint(1, 10)
        self.magic = random.randint(1, 10)
        self.speed = random.randint(1, MAX_SPEED)
        self.perception_radius = self.level * PERCEPTUAL_RADIUS_FACTOR
        self.x = x
        self.y = y
        self.lives = NUM_LIVES
        self.color = random.choice(['red', 'green', 'blue'])
        self.status_points = {'power': 0, 'magic': 0, 'speed': 0, 'perception': 0}

    def move_randomly(self):
        self.x += random.randint(-self.speed, self.speed)
        self.y += random.randint(-self.speed, self.speed)
        self.check_bounds()

    def move_towards(self, other_character):
        dx = other_character.x - self.x
        dy = other_character.y - self.y
        distance = (dx ** 2 + dy ** 2) ** 0.5
        if distance < self.perception_radius and self.level > other_character.level:
            self.move_away_from(other_character)
        else:
            angle = math.atan2(dy, dx)
            dx = math.cos(angle) * self.speed
            dy = math.sin(angle) * self.speed
            self.x += dx
            self.y += dy
            self.check_bounds()

    def move_away_from(self, other_character):
        dx = self.x - other_character.x
        dy = self.y - other_character.y
        angle = math.atan2(dy, dx)
        dx = math.cos(angle) * self.speed
        dy = math.sin(angle) * self.speed
        self.x += dx
        self.y += dy
        self.check_bounds()

    def check_bounds(self):
        if self.x < 0:
            self.x = 0
        elif self.x > SCREEN_WIDTH:
            self.x = SCREEN_WIDTH
        if self.y < 0:
            self.y = 0
        elif self.y > SCREEN_HEIGHT:
            self.y = SCREEN_HEIGHT

    def draw(self, screen):
        if self.color == 'red':
            color = (255, 0, 0)
        elif self.color == 'green':
            color = (0, 255, 0)
        elif self.color == 'blue':
            color = (0, 0, 255)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), 10)
        font = pygame.font.Font('freesansbold.ttf', 16)
        text = font.render(str(self.level), True, (0, 0, 0))
        text_rect = text.get_rect(center=(int(self.x), int(self.y - 15)))
        screen.blit(text, text_rect)

    def roll_dice(self):
        return random.randint(1, 10)

    def attack_power(self):
        power_dice_roll = self.roll_dice()
        magic_dice_roll = self.roll_dice()
        return (self.power + power_dice_roll) + (self.magic + magic_dice_roll) #+ self.status_points['magic'] + self.status_point['power']

    def battle(self, other_character):
        my_attack_power = self.attack_power()
        other_attack_power = other_character.attack_power()
        if my_attack_power > other_attack_power:
            other_character.lives -= 1
            self.level_up()            
        elif my_attack_power < other_attack_power:
            self.lives -= 1
            other_character.level_up()


    def level_up(self):
        self.level += 1
        choices = ['power', 'magic', 'speed', 'perception', 'life']
        chosen = random.choice(choices)
        if chosen == 'life':
            self.lives += 1
        else:
            self.status_points[chosen] += 1
            self.update_attributes()

    def level_down(self):
        self.level -= 1
        self.update_attributes()

    def update_attributes(self):
        self.power = random.randint(1, 10) + self.status_points['power']
        self.magic = random.randint(1, 10) + self.status_points['magic']
        self.speed = random.randint(1, MAX_SPEED) + self.status_points['speed']
        self.perception_radius = (self.level + self.status_points['perception']) * PERCEPTUAL_RADIUS_FACTOR

characters = []
for i in range(NUM_CHARACTERS):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    character = Character(x, y)
    characters.append(character)

while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
        screen.fill((255, 255, 255))

        for character in characters:
            for other_character in characters:
                if character != other_character:
                    dx = abs(character.x - other_character.x)
                    dy = abs(character.y - other_character.y)
                    if dx > SCREEN_WIDTH / 2:
                        dx = SCREEN_WIDTH - dx
                    if dy > SCREEN_HEIGHT / 2:
                        dy = SCREEN_HEIGHT - dy
                    distance = (dx ** 2 + dy ** 2) ** 0.5
                    if distance < 20:
                        character.battle(other_character)
                        print(character.level, other_character.level)

                    if distance < character.perception_radius:
                        if other_character.level < character.level:
                            character.move_towards(other_character)
                        elif other_character.level > character.level:
                            character.move_away_from(other_character)
                    else:
                        character.move_randomly()
            if character.lives <= 0:
                characters.remove(character)
            else:
                character.draw(screen)

        pygame.display.update()

# %%

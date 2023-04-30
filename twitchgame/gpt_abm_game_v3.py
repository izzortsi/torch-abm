
#%%
import pygame
import random
import math
from dataclasses import dataclass

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_CHARACTERS = 50
PERCEPTUAL_RADIUS_FACTOR = 2
SPEED_FACTOR = 0.5
MIN_LEVEL = 1
MAX_LEVEL = 10
NUM_LIVES = 3
CHARACTER_RADIUS = 5

screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battling Simulation Game")

@dataclass
class AttributePoints:

    power: int
    magic: int
    speed: int
    perception: int

class Character:
    def __init__(self, x, y):
        self.level = MIN_LEVEL
        self.lives = NUM_LIVES
        self.color = random.choice(['red', 'green', 'blue'])
        # self.attributes = {'power': random.randint(1, 10),
        #                         'magic': random.randint(1, 10), 
        #                         'speed': random.randint(1, 10), 
        #                         'perception': random.randint(1, 10)}
        self.attributes = AttributePoints(
                                    power=random.randint(1, 10),
                                    magic=random.randint(1, 10),
                                    speed=random.randint(1, 10),
                                    perception=random.randint(1, 10)
                                    )
        self._perception_radius = max(1, int(self.attributes.perception * PERCEPTUAL_RADIUS_FACTOR))
        self._effective_speed = max(1, int(self.attributes.speed * SPEED_FACTOR))
        self.x = x
        self.y = y
    @property
    def perception_radius(self):
        return self._perception_radius
    @perception_radius.getter
    def perception_radius(self):
        return max(1, int(self.attributes.perception * PERCEPTUAL_RADIUS_FACTOR))
    @property
    def effective_speed(self):
        return self._effective_speed
    @effective_speed.getter
    def effective_speed(self):
        return max(1, int(self.attributes.speed * SPEED_FACTOR))
    def get_distance_to(self, other_character):
     return ((self.x - other_character.x) ** 2 + (self.y - other_character.y) ** 2) ** 0.5
    def move_randomly(self):
        # print(-self.effective_speed, self.effective_speed)
        self.x += random.randint(-self.effective_speed, self.effective_speed)
        self.y += random.randint(-self.effective_speed, self.effective_speed)
        self.check_bounds()

    def move_towards(self, other_character):
        dx = other_character.x - self.x
        dy = other_character.y - self.y
        angle = math.atan2(dy, dx)
        dx = math.cos(angle) * self.effective_speed
        dy = math.sin(angle) * self.effective_speed
        self.x += dx
        self.y += dy
        self.check_bounds()

    def move_away_from(self, other_character):
        dx = self.x - other_character.x
        dy = self.y - other_character.y
        angle = math.atan2(dy, dx)
        dx = math.cos(angle) * self.effective_speed
        dy = math.sin(angle) * self.effective_speed
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
    def roll_dice(self):
        return random.randint(1, 10)

    def attack_power(self):
        power_dice_roll = self.roll_dice()
        magic_dice_roll = self.roll_dice()
        return (self.attributes.power + power_dice_roll) + (self.attributes.magic + magic_dice_roll) #+ self.attributes['magic'] + self.attributes_point['power']

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
            self.update_attributes(attribute=chosen)

    def level_down(self):
        self.level -= 1
        self.update_attributes()

    def update_attributes(self, attribute=None):
        if attribute:
            setattr(self.attributes, attribute, getattr(self.attributes, attribute) + 1)
        # self.perception_radius = self.attributes.perception * PERCEPTUAL_RADIUS_FACTOR            
        # self.effective_speed = self.attributes.speed * SPEED_FACTOR

    def draw(self, screen):
        if self.color == 'red':
            color = (255, 0, 0)
        elif self.color == 'green':
            color = (0, 255, 0)
        elif self.color == 'blue':
            color = (0, 0, 255)
        pygame.draw.circle(screen, color, (int(self.x), int(self.y)), CHARACTER_RADIUS)
        font = pygame.font.Font('freesansbold.ttf', 16)
        text = font.render(str(self.level), True, (0, 0, 0))
        text_rect = text.get_rect(center=(int(self.x), int(self.y - 15)))
        screen.blit(text, text_rect)

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
    dead_characters = []
    for character in characters:
        if character in dead_characters:
            pass
        else:
            for other_character in characters:
                if character != other_character:
                    distance = character.get_distance_to(other_character)
                    if distance < 2*CHARACTER_RADIUS:
                        character.battle(other_character)
                        # character.speed = random.randint(1, MAX_SPEED)
                        # character.perception_radius = character.level * PERCEPTUAL_RADIUS_FACTOR
                    elif distance >= 2*CHARACTER_RADIUS and distance < character.perception_radius:
                        if character.level > other_character.level:
                            character.move_towards(other_character)
                        elif character.level < other_character.level:
                            character.move_away_from(other_character)
                    else:
                        character.move_randomly()

            if character.lives <= 0:
                dead_characters.append(character)
                # characters.remove(character)
                print("character died")
            # print(character.level)
            else:
                print(character.attributes, character.level, character.lives, character.perception_radius, character.effective_speed)
                character.draw(screen)
    for dead_character in dead_characters:
        characters.remove(dead_character)
    pygame.display.update()



# %%

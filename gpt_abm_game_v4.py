#%%
import pygame
import random
import math
from dataclasses import dataclass

pygame.init()

SCREEN_WIDTH = 1280
SCREEN_HEIGHT = 720
NUM_CHARACTERS = 10
PERCEPTUAL_RADIUS_FACTOR = 3
SPEED_FACTOR = 0.5
MIN_LEVEL = 1
MAX_LEVEL = 10
NUM_LIVES = 3
CHARACTER_RADIUS = 2
NL = '\n'
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Battling Simulation Game")
@dataclass
class AttributePoints:

    power: int
    magic: int
    speed: int
    perception: int

    def __repr__(self):
        return f'Power: {self.power} {NL} Magic: {self.magic} {NL} Speed: {self.speed} {NL} Perception: {self.perception}'

class Character:
    def __init__(self, id, x, y):
        self.level = MIN_LEVEL
        self.lives = NUM_LIVES
        self.color = random.choice(['red', 'green', 'blue'])
        self.id = id
        # self.attributes = {'power': random.randint(1, 10),
        #                         'magic': random.randint(1, 10), 
        #                         'speed': random.randint(1, 10), 
        #                         'perception': random.randint(1, 10)}
        self.attributes = AttributePoints(
                                    power=random.randint(1, 10),
                                    magic=random.randint(1, 10),
                                    speed=random.randint(1, 10),
                                    perception=random.randint(CHARACTER_RADIUS, 10)
                                    )
        # self._perception_radius = max(1, int(self.attributes.perception * PERCEPTUAL_RADIUS_FACTOR)) + self.level
        self._perception_radius = max(1, int((self.attributes.perception + self.level) * PERCEPTUAL_RADIUS_FACTOR))
        self._effective_speed = max(1, int(self.attributes.speed * SPEED_FACTOR))
        self.x = x
        self.y = y
    def __repr__(self):
        return f'Character {self.id} with level {self.level} and lives {self.lives}. {NL}Attributes: {NL} {self.attributes}'
        
    @property
    def perception_radius(self):
        return self._perception_radius
    @perception_radius.getter
    def perception_radius(self):
        return max(1, int((self.attributes.perception + self.level) * PERCEPTUAL_RADIUS_FACTOR))
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
        return random.randint(1, 6)

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
        # Create a surface with an alpha channel
        perception_radius_surface = pygame.Surface((2*self.perception_radius, 2*self.perception_radius), pygame.SRCALPHA)
        pygame.draw.circle(perception_radius_surface, (128, 128, 128, 32), (self.perception_radius, self.perception_radius), self.perception_radius)
        # screen.blit(perception_radius_surface, (int(self.x - self.perception_radius), int(self.y - self.perception_radius)))
        screen.blit(perception_radius_surface, (int(self.x - self.perception_radius), int(self.y - self.perception_radius)))

        font = pygame.font.Font('freesansbold.ttf', 16)
        # text = font.render(str(self.id) + ": " + str(self.level), True, (0, 0, 0))
        
        text = font.render(f"{self.id}: {self.level}", True, (0, 0, 0))
        text_rect = text.get_rect(center=(int(self.x), int(self.y - 15)))
        screen.blit(text, text_rect)

characters = []
for i in range(NUM_CHARACTERS):
    x = random.randint(0, SCREEN_WIDTH)
    y = random.randint(0, SCREEN_HEIGHT)
    character = Character(i, x, y)
    characters.append(character)
c = 0
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
    c += 1
    screen.fill((255, 255, 255))
    # dead_characters = []
    battles = []
    random.shuffle(characters)
    for i, character in enumerate(characters):
        # if character in dead_characters:
        if False:
            pass
        else:
            for other_character in characters:
                if character != other_character:
                    distance = character.get_distance_to(other_character)
                    if distance < 2*CHARACTER_RADIUS:
                        if set([character.id, other_character.id]) not in battles:
                            battles.append(set([character.id, other_character.id]))
                            character.battle(other_character)
                            print(f"battle between {character.id} and {other_character.id} \n")
                            print(character.id, f"level: {character.level}, lives: {character.lives}, pradius: {character.perception_radius}, espeed: {character.effective_speed}")
                            print(other_character.id, f"level: {other_character.level}, lives: {other_character.lives}, pradius: {other_character.perception_radius}, espeed: {other_character.effective_speed}")
                            print("\n")
                            # character.speed = random.randint(1, MAX_SPEED)
                            # character.perception_radius = character.level * PERCEPTUAL_RADIUS_FACTOR
                    elif distance >= 2*CHARACTER_RADIUS and distance < character.perception_radius:
                        if character.level >= other_character.level:
                            character.move_towards(other_character)
                        elif character.level < other_character.level:
                            character.move_away_from(other_character)
                        else:
                            character.move_randomly()
                    else:
                        character.move_randomly()
                elif character == other_character and len(characters) == 1:
                    character.move_randomly()
            if character.lives <= 0:
                # dead_characters.append(character)
                characters.remove(character)
                print(f"character {character.id} died at level {character.level}")
            # print(character.level)
            elif other_character.lives <= 0:
                # dead_characters.append(other_character)
                characters.remove(other_character)
                print(f"character {other_character.id} died at level {other_character.level}")
                character.draw(screen)
            else:
                # print(character.id, f"level: {character.level}, lives: {character.lives}, pradius: {character.perception_radius}, espeed: {character.effective_speed}")
                character.draw(screen)
            
    # for dead_character in dead_characters:
        # characters.remove(dead_character)
    if c % 100 == 0:
        nl = '\n'
        print(f"{nl.join([character.__repr__() for character in characters])}")
    pygame.display.update()



# %%

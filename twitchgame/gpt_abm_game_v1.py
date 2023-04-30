# #%%


# import pygame
# import math
# import random

# pygame.init()

# SCREEN_WIDTH = 800
# SCREEN_HEIGHT = 600
# screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
# pygame.display.set_caption("Battling Simulation Game")

# class Character:
#     def __init__(self, level, power, magic, speed, perception):
#         self.level = level
#         self.power = power
#         self.magic = magic
#         self.speed = speed
#         self.perception = perception
#         self.x = random.randint(0, SCREEN_WIDTH)
#         self.y = random.randint(0, SCREEN_HEIGHT)

# NUM_CHARACTERS = 100
# characters = []
# for i in range(NUM_CHARACTERS):
#     level = random.randint(1, 10)
#     power = random.randint(1, 10)
#     magic = random.randint(1, 10)
#     speed = random.randint(1, 10)
#     perception = random.randint(50, 200)
#     character = Character(level, power, magic, speed, perception)
#     characters.append(character)

# # while True:
# #     for event in pygame.event.get():
# #         if event.type == pygame.QUIT:
# #             pygame.quit()
# #             quit()

# #     screen.fill((255, 255, 255))

# #     for character in characters:
# #         for other_character in characters:
# #             if character != other_character:
# #                 distance = ((character.x - other_character.x) ** 2 + (character.y - other_character.y) ** 2) ** 0.5
# #                 if distance < character.perception:
# #                     if character.x < other_character.x:
# #                         character.x += character.speed
# #                     else:
# #                         character.x -= character.speed

# #                     if character.y < other_character.y:
# #                         character.y += character.speed
# #                     else:
# #                         character.y -= character.speed
# #                 else:
# #                     dx = random.randint(-1, 1)
# #                     dy = random.randint(-1, 1)
# #                     character.x += dx * character.speed
# #                     character.y += dy * character.speed

# #         pygame.draw.circle(screen, (255, 0, 0), (character.x, character.y), 2)

# #     pygame.display.update()

# # %%
# while True:
#     for event in pygame.event.get():
#         if event.type == pygame.QUIT:
#             pygame.quit()
#             quit()

#     screen.fill((255, 255, 255))

#     for character in characters:
#         for other_character in characters:
#             if character != other_character:
#                 distance_x = abs(character.x - other_character.x)
#                 distance_y = abs(character.y - other_character.y)

#                 if distance_x > SCREEN_WIDTH / 2:
#                     distance_x = SCREEN_WIDTH - distance_x
#                 if distance_y > SCREEN_HEIGHT / 2:
#                     distance_y = SCREEN_HEIGHT - distance_y

#                 distance = (distance_x ** 2 + distance_y ** 2) ** 0.5

#                 if distance < character.perception:
#                     dx = other_character.x - character.x
#                     dy = other_character.y - character.y

#                     if dx > SCREEN_WIDTH / 2:
#                         dx -= SCREEN_WIDTH
#                     elif dx < -SCREEN_WIDTH / 2:
#                         dx += SCREEN_WIDTH

#                     if dy > SCREEN_HEIGHT / 2:
#                         dy -= SCREEN_HEIGHT
#                     elif dy < -SCREEN_HEIGHT / 2:
#                         dy += SCREEN_HEIGHT

#                     distance = (dx ** 2 + dy ** 2) ** 0.5

#                     if dx == 0:
#                         angle = 90 if dy > 0 else 270
#                     else:
#                         angle = math.atan(dy / dx)
#                         angle = math.degrees(angle)
#                         if dx < 0:
#                             angle += 180
#                         elif dy < 0:
#                             angle += 360

#                     dx = math.cos(math.radians(angle)) * character.speed
#                     dy = math.sin(math.radians(angle)) * character.speed

#                     character.x += dx
#                     character.y += dy

#                     if character.x < 0:
#                         character.x += SCREEN_WIDTH
#                     elif character.x > SCREEN_WIDTH:
#                         character.x -= SCREEN_WIDTH

#                     if character.y < 0:
#                         character.y += SCREEN_HEIGHT
#                     elif character.y > SCREEN_HEIGHT:
#                         character.y -= SCREEN_HEIGHT
#                 else:
#                     dx = random.randint(-1, 1)
#                     dy = random.randint(-1, 1)
#                     character.x += dx * character.speed
#                     character.y += dy * character.speed

#                     if character.x < 0:
#                         character.x += SCREEN_WIDTH
#                     elif character.x > SCREEN_WIDTH:
#                         character.x -= SCREEN_WIDTH

#                     if character.y < 0:
#                         character.y += SCREEN_HEIGHT
#                     elif character.y > SCREEN_HEIGHT:
#                         character.y -= SCREEN_HEIGHT

#         pygame.draw.circle(screen, (255, 0, 0), (int(character.x), int(character.y)), 10)

#     pygame.display.update()

#%%
import pygame
import random
import math

pygame.init()

SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
NUM_CHARACTERS = 50
PERCEPTUAL_RADIUS_FACTOR = 10
MAX_SPEED = 5
MIN_LEVEL = 1
MAX_LEVEL = 10

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
        pygame.draw.circle(screen, (255, 0, 0), (int(self.x), int(self.y)), 10)
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

    for character in characters:
        for other_character in characters:
            if character != other_character:
                distance = ((character.x - other_character.x) ** 2 + (character.y - other_character.y) ** 2) ** 0.5
                if distance < 20:
                    if character.level < other_character.level:
                        character.level -= 1
                    elif character.level >= other_character.level:
                        character.level += 1
                    character.speed = random.randint(1, MAX_SPEED)
                    character.perception_radius = character.level * PERCEPTUAL_RADIUS_FACTOR

        character.move_randomly()
        for other_character in characters:
            if character != other_character:
                distance = ((character.x - other_character.x) ** 2 + (character.y - other_character.y) ** 2) ** 0.5
                if distance < 20:
                    character.move_away_from(other_character)

        for i in range(len(characters)):
            for j in range(i + 1, len(characters)):
                if characters[i].x == characters[j].x and characters[i].y == characters[j].y:
                    if characters[i].level > characters[j].level:
                        characters[i].level += 1
                        characters[j].level -= 1
                    elif characters[j].level > characters[i].level:
                        characters[j].level += 1
                        characters[i].level -= 1
                    characters[i].speed = random.randint(1, MAX_SPEED)
                    characters[j].speed = random.randint(1, MAX_SPEED)
                    characters[i].perception_radius = characters[i].level * PERCEPTUAL_RADIUS_FACTOR
                    characters[j].perception_radius = characters[j].level * PERCEPTUAL_RADIUS_FACTOR
                    characters[i].check_bounds()
                    characters[j].check_bounds()
        if character.level <= 0:
            characters.remove(character)
            print("character died")
        # print(character.level)
        character.draw(screen)
    
    pygame.display.update()



# %%

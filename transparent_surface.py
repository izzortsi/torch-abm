
#%%
import pygame

pygame.init()
screen = pygame.display.set_mode((640, 480))
screen.fill((255, 255, 255))
# Create a surface with an alpha channel
circle_surface = pygame.Surface((100, 100), pygame.SRCALPHA)

# Draw a circle on the surface
pygame.draw.circle(circle_surface, (0, 255, 255, 128), (50, 50), 50)
pygame.draw.circle(circle_surface, (0, 0, 255, 128), (25, 25), 5)
# Blit the surface onto the screen
screen.blit(circle_surface, (100, 100))

pygame.display.update()

# Main game loop
while True:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            pygame.quit()
            quit()
# %%

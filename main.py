import pygame
from pathlib import Path

pygame.init()

DISPLAY_WIDTH = 800
DISPLAY_HEIGHT = 400

# Colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# Images
CAR_IMAGE = pygame.image.load(Path("assets", "racecar.png"))

# Game parts
game_display = pygame.display.set_mode((DISPLAY_WIDTH, DISPLAY_HEIGHT))
pygame.display.set_caption('A bit Racey')
clock = pygame.time.Clock()
crashed = False


# Game objects
def draw_car(x: float, y: float):
    game_display.blit(CAR_IMAGE, (x, y))


car_x = DISPLAY_WIDTH * 0.45
car_y = DISPLAY_HEIGHT * 0.8

while not crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

        print(event)

    game_display.fill(WHITE)
    draw_car(car_x, car_y)

    pygame.display.update()
    clock.tick(60)

pygame.quit()
quit()

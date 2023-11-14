import pygame
import math
from pathlib import Path


class Asset:
    CAR_IMAGE = pygame.image.load(Path("assets", "racecar.png"))


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


class Game:

    def __init__(self):
        # Window display dimensions
        self.WIDTH = 800
        self.HEIGHT = 400

        # Initilise the display surface
        self.surface = pygame.display.set_mode((self.WIDTH, self.HEIGHT))
        pygame.display.set_caption('A bit Racey')

        # Initialise other game components
        self.clock = pygame.time.Clock()
        self.has_crashed = False

        pygame.init()


class Car:

    def calculate_starting_x(self):
        car_height = self.texture.get_height()
        screen_height = self.game.HEIGHT

        return screen_height - car_height

    def calculate_starting_y(self):
        screen_height = self.game.WIDTH
        return math.floor(screen_height / 2)

    def __init__(self, game: Game):
        self.game = game
        self.texture = Asset.CAR_IMAGE

        self.x = self.calculate_starting_x()
        self.y = self.calculate_starting_y()

    def draw(self):
        self.game.surface.blit(self.texture, (self.x, self.y))


game = Game()
car = Car(game)

while not game.has_crashed:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            crashed = True

        print(event)

    game.surface.fill(Color.WHITE)
    car.draw()

    pygame.display.update()
    game.clock.tick(60)

pygame.quit()
quit()

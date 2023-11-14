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
        screen_width = self.game.WIDTH

        # Calculate where the centre of the car should go, and thus where the left edge of the car should be
        center_position = screen_width / 2
        left_edge_position = center_position - (self.texture.get_width() / 2)

        # Don't place the car in-between pixels
        return math.floor(left_edge_position)

    def calculate_starting_y(self):
        car_height = self.texture.get_height()
        screen_height = self.game.HEIGHT
        padding = 5  # 5px of bottom padding

        return screen_height - (car_height + padding)

    def __init__(self, game: Game):
        self.game = game
        self.texture = Asset.CAR_IMAGE

        self.x = self.calculate_starting_x()
        self.y = self.calculate_starting_y()
        print(self.x, self.y)
        print("Width height", self.texture.get_width(),
              self.texture.get_height())

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

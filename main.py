import pygame
import math
from pathlib import Path


class Asset:
    CAR_IMAGE = pygame.image.load(Path("assets", "racecar.png"))
    CAR_IMAGE_ALT = pygame.image.load(Path("assets", "racecar-alt.png"))


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


class DefaultTheme:
    ALTERNATE_TEXTURES = False
    BACKGROUND = Color.WHITE


class NightTheme(DefaultTheme):
    ALTERNATE_TEXTURES = True
    BACKGROUND = Color.BLACK


class Game:

    def __init__(self, theme: type[DefaultTheme]):
        # Window display config
        self.theme = theme
        self.background_color = self.theme.BACKGROUND

        # Initilise the display surface
        self.surface = pygame.display.set_mode((300, 300), pygame.RESIZABLE)
        pygame.display.set_caption('A bit Racey')

        # Initialise other game components
        self.clock = pygame.time.Clock()
        self.has_crashed = False

        pygame.init()

    def width(self) -> int:
        """Returns the width of the window, in pixels"""
        return self.surface.get_width()

    def height(self) -> int:
        """Returns the height of the window, in pixels"""
        return self.surface.get_height()

    def on_event(self, event):
        print(event)
        if event.type == pygame.QUIT:
            self.has_crashed = True

    def run(self):
        car = Car(game=self)

        while not self.has_crashed:
            for event in pygame.event.get():
                self.on_event(event)

            # Reset the surface
            self.surface.fill(self.background_color)

            # Re-draw the objects
            car.draw()

            pygame.display.update()
            self.clock.tick(60)


class Car:

    def calculate_starting_x(self):
        window_width = self.game.height()

        # Calculate where the centre of the car should go, and thus where the left edge of the car should be
        center_position = window_width / 2
        left_edge_position = center_position - (self.texture.get_width() / 2)

        # Don't place the car in-between pixels
        return math.floor(left_edge_position)

    def calculate_starting_y(self):
        car_height = self.texture.get_height()
        screen_height = self.game.height()
        padding = 5  # 5px of bottom padding

        return screen_height - (car_height + padding)

    def get_texture(self):
        return Asset.CAR_IMAGE_ALT if self.game.theme.ALTERNATE_TEXTURES else Asset.CAR_IMAGE

    def __init__(self, game: Game):
        self.game = game
        self.texture = self.get_texture()

        self.x = self.calculate_starting_x()
        self.y = self.calculate_starting_y()
        print(self.x, self.y)
        print("Width height", self.texture.get_width(),
              self.texture.get_height())

    def draw(self):
        self.game.surface.blit(self.texture, (self.x, self.y))


game = Game(theme=DefaultTheme)
game.run()
pygame.quit()
quit()

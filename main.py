from typing import Literal, Tuple
import pygame
import math
from pathlib import Path


class Asset:
    CAR_IMAGE = pygame.image.load(Path("assets", "racecar.png"))
    CAR_IMAGE_ALT = pygame.image.load(Path("assets", "racecar-alt.png"))


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    # From color palette at https://colorcodes.io/gray/asphalt-gray-color-codes/
    ASPHALT = (38, 40, 51)


class DefaultTheme:
    ALTERNATE_TEXTURES = False
    BACKGROUND = Color.WHITE


class NightTheme(DefaultTheme):
    ALTERNATE_TEXTURES = False
    BACKGROUND = Color.ASPHALT


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
        self.objects = []
        self.old_window_dimensions = (self.width(), self.height())
        self.key_action_callbacks = {}

        # Set up default keybinds
        self.keybinds = {
            pygame.K_LEFT: "move.left",
            pygame.K_RIGHT: "move.right"
        }

        for action in self.keybinds.values():
            self.key_action_callbacks[action] = {"up": None, "down": None}

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
        elif event.type == pygame.VIDEORESIZE:
            for object in self.objects:
                event.old_dimensions = self.old_window_dimensions
                object.on_window_resize(event)
            self.old_window_dimensions = (self.width(), self.height())
        elif event.type == pygame.KEYDOWN:
            if event.key in self.keybinds:
                action = self.keybinds[event.key]
                self.trigger_key_action(action, "down")
        elif event.type == pygame.KEYUP:
            if event.key in self.keybinds:
                action = self.keybinds[event.key]
                self.trigger_key_action(action, "up")

    def trigger_key_action(self, action: str, event_type: Literal["up",
                                                                  "down"]):
        action_callback = self.key_action_callbacks[action][event_type]
        if action_callback is None:
            return
        action_callback()

    def on_key_up(self, action: str):

        def decorator(callback):
            self.key_action_callbacks[action]["up"] = callback

        return decorator

    def on_key_down(self, action):

        def decorator(callback):
            self.key_action_callbacks[action]["down"] = callback

        return decorator

    def run(self):
        car = Car(game=self)
        self.objects.append(car)

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

    def height(self) -> int:
        return self.texture.get_height()

    def width(self) -> int:
        return self.texture.get_width()

    def calculate_starting_x(self):
        window_width = self.game.height()

        # Calculate where the centre of the car should go, and thus where the left edge of the car should be
        center_position = window_width / 2
        left_edge_position = center_position - (self.width() / 2)

        # Don't place the car in-between pixels
        return math.floor(left_edge_position)

    def calculate_starting_y(self):
        car_height = self.height()
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
        print("Width height", self.width(), self.height())

        @game.on_key_down("move.left")
        def move_left():
            print("LEFT")

    def calculate_center_bounds(
            self, parent_width: float,
            parent_height: float) -> Tuple[float, float, float, float]:
        """Calculates the bounding box of possible positions for the center point of this object"""
        x_padding = self.width() / 2
        y_padding = self.height() / 2

        x1 = 0 + x_padding
        x2 = parent_width - x_padding
        y1 = 0 + y_padding
        y2 = parent_height - y_padding

        return x1, y1, x2, y2

    def calculate_position_percentage(
            self, bounds: Tuple[float, float, float,
                                float]) -> Tuple[float, float]:
        """Calculates the position of the center of the object, returning coordinates in the form (x, y)

        - Coordinates are scaled from 0.0 to 1.0 to represent percentage relative to the provided bounding box
        """
        x1, y1, x2, y2 = bounds

        # Calculate the center of the object
        center_x = self.x + self.width() / 2
        center_y = self.y + self.height() / 2

        # Calculate the percentage position of the center relative to the bounding box
        center_percentage_x = (center_x - x1) / (x2 - x1)
        center_percentage_y = (center_y - y1) / (y2 - y1)

        return center_percentage_x, center_percentage_y

    def map_relative_position_to_box(
        self, position_percentage: Tuple[float, float],
        new_center_point_bounds: Tuple[float, float, float, float]
    ) -> Tuple[float, float]:
        """Calculates the new center point based on the saved percentage and the new bounding box dimensions"""
        x1, y1, x2, y2 = new_center_point_bounds

        # Calculate the new center based on the percentage and the new bounding box
        new_center_x = x1 + (x2 - x1) * position_percentage[0]
        new_center_y = y1 + (y2 - y1) * position_percentage[1]

        return new_center_x, new_center_y

    def on_window_resize(self, event):
        old_center_point_bounds = self.calculate_center_bounds(
            *event.old_dimensions)
        position_percentage = self.calculate_position_percentage(
            old_center_point_bounds)
        print("Was at", position_percentage)

        # Update object's position to be the in the same place relative to the window size
        new_center_point_bounds = self.calculate_center_bounds(
            event.w, event.h)
        new_center = self.map_relative_position_to_box(
            position_percentage, new_center_point_bounds)
        self.x = new_center[0] - self.width() / 2
        self.y = new_center[1] - self.height() / 2

        # Redraw the object
        self.draw()

    def draw(self):
        self.game.surface.blit(self.texture, (self.x, self.y))


game = Game(theme=NightTheme)
game.run()

# Game has finished
pygame.quit()
quit()

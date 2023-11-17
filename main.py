from typing import Literal, Tuple
import pygame
from pygame import Rect
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
        self.should_exit = False
        self.objects = []
        self.old_window_dimensions = (self.width(), self.height())
        self.key_action_callbacks = {}
        self.key_up_callbacks = {}

        # Set up default keybinds
        self.keybinds = {
            pygame.K_LEFT: "move.left",
            pygame.K_RIGHT: "move.right"
        }

        pygame.init()

    def width(self) -> int:
        """Returns the width of the window, in pixels"""
        return self.surface.get_width()

    def height(self) -> int:
        """Returns the height of the window, in pixels"""
        return self.surface.get_height()
    
    def window_rect(self) -> Rect:
        """Calculates the rectangle that represents the size of the window"""
        return Rect(0, 0, self.width(), self.height())

    def on_event(self, event):
        #print(event)
        if event.type == pygame.QUIT:
            self.should_exit = True
        elif event.type == pygame.VIDEORESIZE:
            for object in self.objects:
                event.old_dimensions = self.old_window_dimensions
                object.on_window_resize(event)
            self.old_window_dimensions = (self.width(), self.height())
        elif event.type == pygame.KEYDOWN:
            if event.key in self.keybinds:
                action = self.keybinds[event.key]
                self.trigger_key_action(action, event)
        elif event.type == pygame.KEYUP:
            if event.key in self.key_up_callbacks:
                callback = self.key_up_callbacks[event.key]
                callback()

    def trigger_key_action(self, action: str, event: pygame.event.Event):
        if action not in self.key_action_callbacks:
            return
        action_callback = self.key_action_callbacks[action]
        on_key_up = action_callback(event)
        self.key_up_callbacks[event.key] = lambda: on_key_up(event)

    def on_key_action(self, action: str):

        def decorator(callback):
            self.key_action_callbacks[action] = callback

        return decorator

    def run(self):
        car = Car(game=self)
        self.objects.append(car)

        while not self.should_exit:
            for event in pygame.event.get():
                self.on_event(event)

            # Reset the surface
            self.surface.fill(self.background_color)

            # Update the objects
            car.tick()
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

        # Velocity values, measured in pixels/tick
        self.velocity_x = 0
        self.velocity_y = 0

        # Bind movement callbacks to the appropiate key actions
        @game.on_key_action("move.left")
        def start_moving_left(event):

            def undo(event):
                self.velocity_x = 0
                print("Left stopped")

            self.velocity_x = -5
            print("Left started")
            return undo

        @game.on_key_action("move.right")
        def start_moving_right(event):

            def undo(event):
                self.velocity_x = 0
                print("Right stopped")

            self.velocity_x = 5
            print("Right started")
            return undo

        # @game.on_key_action("move.left")
        # def stop_moving_left():
        #     self.velocity_x = 0

    def calculate_center_bounds(
            self, parent_width: float,
            parent_height: float) -> Rect:
        """Returns a rectangle containing possible positions for the center point of this object"""
        x_padding = self.width() / 2
        y_padding = self.height() / 2

        start_x = 0 + x_padding
        start_y = 0 + y_padding
        width = parent_width - x_padding - start_x
        height = parent_height - y_padding - start_y

        return Rect(start_x, start_y, width, height)
    
    def collision_rect(self) -> Rect:
        """Calculates a rectangle representing the area taken up by this object (i.e. its collision box)"""
        print(Rect(self.x, self.y, self.width(), self.height()))
        return Rect(self.x, self.y, self.width(), self.height())

    def center_point(self) -> Tuple[float, float]:
        raise RuntimeError("depricated")
        """Calculates the coordinates of the center point of the object (not rounded)"""
        center_x = self.x + self.width() / 2
        center_y = self.y + self.height() / 2

        return (center_x, center_y)


    def calculate_position_percentage(
            self, rect: Rect) -> Tuple[float, float]:
        """Calculates the position of the center of the object, returning coordinates in the form (x, y)

        - Coordinates are scaled from 0.0 to 1.0 to represent percentage relative to the provided rectangle
        """
        x1, y1, x2, y2 = rect.topleft[0], rect.topleft[1], rect.bottomright[0], rect.bottomright[1] # FIXME
        our_x, our_y = self.collision_rect().center

        # Calculate the relative position of the center of this object
        our_percentage_x = (our_x - rect.left) / (rect.right - rect.left)
        our_percentage_y = (our_y - rect.top) / (rect.bottom - rect.top)
        center_percentage_x = (our_x - x1) / (x2 - x1)
        center_percentage_y = (our_y - y1) / (y2 - y1)


        print(center_percentage_x, center_percentage_y)
        print(our_percentage_x, our_percentage_y)
        return center_percentage_x, center_percentage_y

    def map_relative_position_to_box(
        self, position_percentage: Tuple[float, float],
        new_center_point_bounds: Rect
    ) -> Tuple[float, float]:
        """Calculates the new center point based on the saved percentage and the new bounding box dimensions"""
        x1, y1, x2, y2 = new_center_point_bounds

        # Calculate the new center based on the percentage and the new bounding box
        new_center_x = x1 + (x2 - x1) * position_percentage[0]
        new_center_y = y1 + (y2 - y1) * position_percentage[1]

        return new_center_x, new_center_y

    def is_within_window(self):
        our_collision_box = self.collision_rect()
        window_bounding_box = self.game.window_rect()

        



    def on_window_resize(self, event):
        old_center_point_bounds = self.calculate_center_bounds(
            *event.old_dimensions)
        position_percentage = self.calculate_position_percentage(
            old_center_point_bounds)
        print("Old center point bounds", old_center_point_bounds)
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

    def tick(self):
        x_movement = self.velocity_x
        y_movement = self.velocity_y

        self.x += x_movement
        self.y += y_movement

    def draw(self):
        self.game.surface.blit(self.texture, (self.x, self.y))


game = Game(theme=NightTheme)
game.run()

# Game has finished
pygame.quit()
quit()

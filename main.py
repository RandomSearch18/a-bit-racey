from __future__ import annotations
from typing import Callable, Literal, Tuple
import pygame
import math
from pathlib import Path
import time


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
    FOREGROUND = Color.BLACK


class NightTheme(DefaultTheme):
    ALTERNATE_TEXTURES = False
    BACKGROUND = Color.ASPHALT
    FOREGROUND = Color.WHITE


class Game:

    def __init__(self, theme: type[DefaultTheme]):
        # Window display config
        self.theme = theme
        self.background_color = self.theme.BACKGROUND

        # Initilise the display surface
        self.surface = pygame.display.set_mode((300, 300), pygame.RESIZABLE)
        pygame.display.set_caption("A bit Racey")

        # Initialise other game components
        self.clock = pygame.time.Clock()
        self.should_exit = False
        self.objects: list[GameObject] = []
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

    def window_rect(self) -> Tuple[float, float, float, float]:
        """Calculates the bounding box that represents the size of the window"""
        x1 = 0
        y1 = 0
        x2 = self.width()
        y2 = self.height()

        return x1, y1, x2, y2

    def window_center(self) -> Tuple[float, float]:
        """Calculates the coordinates of the center of the window"""
        x = self.width() / 2
        y = self.height() / 2
        return (x, y)

    def on_event(self, event):
        # print(event)
        if event.type == pygame.QUIT:
            self.should_exit = True
        elif event.type == pygame.VIDEORESIZE:
            event.old_dimensions = self.old_window_dimensions
            for object in self.objects:
                object.window_resize_handler.handle_window_resize(event)
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

    def create_text(self, text, font):
        surface = font.render(text, True, self.theme.FOREGROUND)
        return surface, surface.get_rect()

    def display_title(self, text: str):
        large_font = pygame.font.Font("freesansbold.ttf", 115)
        text_surface, text_rect = self.create_text(text, large_font)

        text_rect.center = self.window_center()
        self.surface.blit(text_surface, text_rect)
        self.update_display()

        print("You died!")
        time.sleep(2)

    def update_display(self):
        pygame.display.update()

    def on_crash(self):
        self.car.reset()
        self.display_title("You died!")

    def run(self):
        self.car = Car(game=self)
        self.objects.append(self.car)

        self.objects.append(Block(game=self))

        while not self.should_exit:
            for event in pygame.event.get():
                self.on_event(event)

            # Reset the surface
            self.surface.fill(self.background_color)

            # Update the objects
            for object in self.objects:
                object.run_tick_tasks()
                object.draw()

            self.update_display()
            self.clock.tick(60)


class Texture:

    def __init__(self, width, height):
        self.base_width = width
        self.base_height = height

    def height(self) -> float:
        return self.base_height

    def width(self) -> float:
        return self.base_width

    def draw_at(self, start_x, start_y):
        pass


class PlainColorTexture(Texture):

    def __init__(self, game: Game, color: Tuple[float, float, float], width,
                 height):
        self.game = game
        self.color = color
        super().__init__(width, height)

    def draw_at(self, start_x, start_y):
        pygame.draw.rect(
            self.game.surface, self.color,
            [start_x, start_y, self.width(),
             self.height()])


class ImageTexture(Texture):

    def __init__(self, game, image):
        self.game = game
        self.image = image

        width = self.image.get_width()
        height = self.image.get_height()
        super().__init__(width, height)

    def draw_at(self, start_x, start_y):
        self.game.surface.blit(self.image, (start_x, start_y))


class GameObject:

    def height(self) -> float:
        return self.texture.height()

    def width(self) -> float:
        return self.texture.width()

    def spawn_point(self) -> Tuple[float, float]:
        raise NotImplementedError()

    def reset(self):
        """Moves the object to its initial position (spawn point)"""
        spawn_point = self.spawn_point()
        self.x, self.y = spawn_point

    def __init__(self, texture: Texture,
                 window_resize_handler: WindowResizeHandler):
        assert hasattr(self, "game")
        self.tick_tasks: list[Callable] = []
        self.texture = texture
        self.window_resize_handler = window_resize_handler
        self.reset()

    def draw(self):
        raise NotImplementedError()

    def run_tick_tasks(self):
        for callback in self.tick_tasks:
            callback()

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

    def collision_box(self) -> Tuple[float, float, float, float]:
        """Calculates the visual bounding box (i.e. collision box) for this object"""
        x1 = self.x
        y1 = self.y
        x2 = self.x + self.width()
        y2 = self.y + self.height()

        return x1, y1, x2, y2

    def center_point(self) -> Tuple[float, float]:
        """Calculates the coordinates of the center point of the object (not rounded)"""
        center_x = self.x + self.width() / 2
        center_y = self.y + self.height() / 2

        return (center_x, center_y)

    def calculate_position_percentage(
            self, bounds: Tuple[float, float, float,
                                float]) -> Tuple[float, float]:
        """Calculates the position of the center of the object, returning coordinates in the form (x, y)
        
        - Coordinates are scaled from 0.0 to 1.0 to represent percentage relative to the provided bounding box
        """
        x1, y1, x2, y2 = bounds
        center_x, center_y = self.center_point()

        # Calculate the percentage position of the center relative to the bounding box
        center_percentage_x = (center_x - x1) / (x2 - x1)
        center_percentage_y = (center_y - y1) / (y2 - y1)

        return center_percentage_x, center_percentage_y

    def map_relative_position_to_box(
        self,
        position_percentage: Tuple[float, float],
        new_center_point_bounds: Tuple[float, float, float, float],
    ) -> Tuple[float, float]:
        """Calculates the new center point based on the saved percentage and the new bounding box dimensions"""
        x1, y1, x2, y2 = new_center_point_bounds

        # Calculate the new center based on the percentage and the new bounding box
        new_center_x = x1 + (x2 - x1) * position_percentage[0]
        new_center_y = y1 + (y2 - y1) * position_percentage[1]

        return new_center_x, new_center_y

    def is_within_window(self):
        our_collision_box = self.collision_box()
        window_bounding_box = self.game.window_rect()

        is_within_x = (our_collision_box[0] >= window_bounding_box[0]
                       and our_collision_box[2] <= window_bounding_box[2])

        is_within_y = (our_collision_box[1] >= window_bounding_box[1]
                       and our_collision_box[3] <= window_bounding_box[3])

        return is_within_x and is_within_y


class WindowResizeHandler:

    def __init__(self, game_object: GameObject):
        self.object = game_object

    def get_new_position(self, event) -> Tuple[float, float]:
        raise NotImplementedError()

    def handle_window_resize(self, event):
        new_position = self.get_new_position(event)
        self.object.x, self.object.y = new_position
        self.object.draw()


class LinearPositionScaling(WindowResizeHandler):

    def __init__(self, game_object: GameObject):
        super().__init__(game_object)

    def get_new_position(self, event) -> Tuple[float, float]:
        old_center_point_bounds = self.object.calculate_center_bounds(
            *event.old_dimensions)
        position_percentage = self.object.calculate_position_percentage(
            old_center_point_bounds)
        print("Was at", position_percentage)

        # Update object's position to be the in the same place relative to the window size
        new_center_point_bounds = self.object.calculate_center_bounds(
            event.w, event.h)
        new_center = self.object.map_relative_position_to_box(
            position_percentage, new_center_point_bounds)
        new_x = new_center[0] - self.object.width() / 2
        new_y = new_center[1] - self.object.height() / 2

        return new_x, new_y


class Velocity:

    def on_tick(self):
        x_movement = self.x
        y_movement = self.y

        self.object.x += x_movement
        self.object.y += y_movement

    def __init__(self, game_object: GameObject):
        # Magnitudes of velocity, measured in pixels/tick
        self.x = 0
        self.y = 0

        self.object = game_object
        self.object.tick_tasks.append(self.on_tick)


class Car(GameObject):

    def calculate_starting_x(self):
        window_width = self.game.width()

        # Calculate where the centre of the car should go, and thus where the left edge of the car should be
        center_position = window_width / 2
        left_edge_position = center_position - (self.width() / 2)

        return left_edge_position

    def calculate_starting_y(self):
        car_height = self.height()
        screen_height = self.game.height()
        padding = 5  # 5px of bottom padding

        return screen_height - (car_height + padding)

    def get_texture_image(self):
        return (Asset.CAR_IMAGE_ALT
                if self.game.theme.ALTERNATE_TEXTURES else Asset.CAR_IMAGE)

    def spawn_point(self) -> Tuple[float, float]:
        return (self.calculate_starting_x(), self.calculate_starting_y())

    def check_collision_with_window_edge(self):
        if not self.is_within_window():
            self.game.on_crash()

    def __init__(self, game: Game):
        self.game = game
        texture = ImageTexture(game, self.get_texture_image())
        super().__init__(texture=texture,
                         window_resize_handler=LinearPositionScaling(self))

        self.velocity = Velocity(self)
        self.tick_tasks.append(self.check_collision_with_window_edge)

        # Bind movement callbacks to the appropiate key actions
        @game.on_key_action("move.left")
        def start_moving_left(event):

            def undo(event):
                self.velocity.x = 0
                print("Left stopped")

            self.velocity.x = -5
            print("Left started")
            return undo

        @game.on_key_action("move.right")
        def start_moving_right(event):

            def undo(event):
                self.velocity.x = 0
                print("Right stopped")

            self.velocity.x = 5
            print("Right started")
            return undo

    def draw(self):
        self.texture.draw_at(self.x, self.y)


class Block(GameObject):

    def spawn_point(self) -> Tuple[float, float]:
        return (0, 0)

    def tick(self):
        pass

    def draw(self):
        self.texture.draw_at(self.x, self.y)

    def __init__(self, game: Game):
        self.game = game
        texture = PlainColorTexture(self.game, self.game.theme.FOREGROUND, 50,
                                    50)
        super().__init__(texture=texture,
                         window_resize_handler=LinearPositionScaling(self))


game = Game(theme=NightTheme)
game.run()

# Game has finished
pygame.quit()
quit()

from __future__ import annotations
from enum import Enum
from typing import Callable, Literal, Optional, Tuple
import pygame

# import pygame._sdl2 as pygame_sdl2
import math
import random
from pathlib import Path
import time


class Asset:
    CAR_IMAGE = pygame.image.load(Path("assets", "racecar.png"))
    CAR_IMAGE_ALT = pygame.image.load(Path("assets", "racecar-alt.png"))


class Color:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)
    RED = (255, 255, 255)
    # From color palette at https://colorcodes.io/gray/asphalt-gray-color-codes/
    ASPHALT = (38, 40, 51)


class DefaultTheme:
    ALTERNATE_TEXTURES = False
    BACKGROUND = Color.WHITE
    FOREGROUND = Color.BLACK
    FOREGROUND_BAD = Color.RED


class NightTheme(DefaultTheme):
    ALTERNATE_TEXTURES = False
    BACKGROUND = Color.ASPHALT
    FOREGROUND = Color.WHITE
    FOREGROUND_BAD = Color.RED


class Corner(Enum):
    TOP_LEFT = (0, 0)
    TOP_RIGHT = (1, 0)
    BOTOM_LEFT = (0, 1)
    BOTOM_RIGHT = (1, 1)


class PointSpecifier:
    def resolve(
        self, game: Game, width: float = 0, height: float = 0
    ) -> Tuple[float, float]:
        raise NotImplementedError()

    def move_left(self, pixels: float):
        raise NotImplementedError()

    def move_right(self, pixels: float):
        raise NotImplementedError()

    def move_up(self, pixels: float):
        raise NotImplementedError()

    def move_down(self, pixels: float):
        raise NotImplementedError()

    def move_to(
        self, absolute_coordinates: Tuple[float, float], width: float, height: float
    ):
        raise NotImplementedError()


class PixelsPoint(PointSpecifier):
    def __init__(self, x: float, y: float, relative_to: Corner = Corner.TOP_LEFT):
        self.x = x
        self.y = y
        self.relative_to = relative_to

    def resolve(
        self, game: Game, width: float = 0, height: float = 0
    ) -> Tuple[float, float]:
        outer_width = game.window_box().width
        outer_height = game.window_box().height
        multiplier_x, multiplier_y = self.relative_to.value

        # Coordinates of the window corner that we're working relative to
        base_x_coordinate = multiplier_x * outer_width
        base_y_coordinate = multiplier_y * outer_height

        # Calculate the number of pixels away from the corner that we should be at
        x_offset = -self.x if multiplier_x else +self.x
        y_offset = -self.y if multiplier_y else +self.y

        # Account for the x/y offsets not always measuring from our top-left
        x_offset -= width * multiplier_x
        y_offset -= height * multiplier_y

        # Calculate the desired coordinates of the top-left of our object
        actual_x_coordinate = base_x_coordinate + x_offset
        actual_y_coordinate = base_y_coordinate + y_offset

        # print(actual_x_coordinate, actual_y_coordinate)
        return (actual_x_coordinate, actual_y_coordinate)

    def move_right(self, pixels: float):
        x_corner = self.relative_to.value[0]
        pixel_movement = -pixels if x_corner else +pixels
        self.x += pixel_movement

    def move_left(self, pixels: float):
        x_corner = self.relative_to.value[0]
        pixel_movement = +pixels if x_corner else -pixels
        self.x += pixel_movement

    def move_down(self, pixels: float):
        y_corner = self.relative_to.value[1]
        pixel_movement = -pixels if y_corner else +pixels
        self.y += pixel_movement

    def move_up(self, pixels: float):
        y_corner = self.relative_to.value[1]
        pixel_movement = +pixels if y_corner else -pixels
        self.y += pixel_movement

    def move_to(
        self, target_coordinates: Tuple[float, float], width: float, height: float
    ):
        target_x, target_y = target_coordinates
        outer_width = game.window_box().width
        outer_height = game.window_box().height
        multiplier_x, multiplier_y = self.relative_to.value

        # Coordinates of the window corner that we're working relative to
        base_x_coordinate = multiplier_x * outer_width
        base_y_coordinate = multiplier_y * outer_height

        # Calculate the number of pixels away from the corner that we should be at
        x_difference = target_x - base_x_coordinate
        y_difference = target_y - base_y_coordinate

        # The differences should be measured from the corresponding corner of our object,
        # e.g. from object.top_right to window.top_right
        x_difference += width * multiplier_x
        y_difference += height * multiplier_y

        # Coordinates should be in the direction away from the outer box's chosen corner
        new_x = -x_difference if multiplier_x else +x_difference
        new_y = -y_difference if multiplier_y else +y_difference

        self.x, self.y = new_x, new_y


class PercentagePoint(PointSpecifier):
    def __init__(self, x: float, y: float, relative_to: Corner = Corner.TOP_LEFT):
        assert 0 <= x < 1
        assert 0 <= y < 1
        self.x = x
        self.y = y
        self.relative_to = relative_to

    def resolve(
        self, game: Game, width: float = 0, height: float = 0
    ) -> Tuple[float, float]:
        outer_box = game.window_box()
        x_pixels = self.x * outer_box.width
        y_pixels = self.y * outer_box.height

        pixels_point = PixelsPoint(x_pixels, y_pixels, self.relative_to)
        return pixels_point.resolve(game, width, height)


class Box:
    def __init__(self, x1: float, y1: float, x2: float, y2: float):
        self.x1 = x1
        self.y1 = y1
        self.x2 = x2
        self.y2 = y2

        self.width = x2 - x1
        self.height = y2 - y1

    @property
    def top(self) -> float:
        return self.y1

    @property
    def bottom(self) -> float:
        return self.y2

    @property
    def left(self) -> float:
        return self.x1

    @property
    def right(self) -> float:
        return self.x2

    def center(self) -> Tuple[float, float]:
        """Calculates the coordinates of the center of the box"""
        center_x = self.left + self.width / 2
        center_y = self.top + self.height / 2

        return (center_x, center_y)

    def is_inside(self, outer_box: Box, allowed_margin=0.0) -> bool:
        is_within_x = (
            outer_box.left - self.left <= allowed_margin
            and self.right - outer_box.right <= allowed_margin
        )

        is_within_y = (
            outer_box.top - self.top <= allowed_margin
            and self.bottom - outer_box.bottom <= allowed_margin
        )

        return is_within_x and is_within_y

    def is_outside(self, other_box: Box) -> bool:
        is_outside_x = self.right < other_box.left or self.left > other_box.right

        is_outside_y = self.bottom < other_box.top or self.top > other_box.bottom

        return is_outside_x or is_outside_y


class Game:
    def __init__(self, theme: type[DefaultTheme]):
        # Window display config
        self.theme = theme
        self.background_color = self.theme.BACKGROUND

        # Initilise the display surface
        self.surface = pygame.display.set_mode((300, 300), pygame.RESIZABLE)
        pygame.display.set_caption("A bit Racey")

        # Initialise other game components
        self.MAX_FPS = 60
        self.clock = pygame.time.Clock()
        self.has_died = False
        self.objects: list[GameObject] = []
        self.old_window_dimensions = (self.width(), self.height())
        self.key_action_callbacks = {}
        self.key_up_callbacks = {}

        # Set up default keybinds
        self.keybinds = {pygame.K_LEFT: "move.left", pygame.K_RIGHT: "move.right"}

        pygame.init()

    def width(self) -> int:
        """Returns the width of the window, in pixels"""
        return self.surface.get_width()

    def height(self) -> int:
        """Returns the height of the window, in pixels"""
        return self.surface.get_height()

    def window_box(self) -> Box:
        """Calculates the box that represents the size of the window"""
        x1 = 0
        y1 = 0
        x2 = self.width()
        y2 = self.height()

        return Box(x1, y1, x2, y2)

    def on_event(self, event):
        # print(event)
        if event.type == pygame.QUIT:
            self.exited = True
        elif event.type == pygame.VIDEORESIZE:
            event.old_dimensions = self.old_window_dimensions
            for object in self.objects:
                if not object.window_resize_handler:
                    continue
                object.window_resize_handler.handle_window_resize(event)
            self.old_window_dimensions = (self.width(), self.height())

        # Keyboard input
        elif event.type == pygame.KEYDOWN:
            if event.key in self.keybinds:
                action = self.keybinds[event.key]
                self.trigger_key_action(action, event)
        elif event.type == pygame.KEYUP:
            if event.key in self.key_up_callbacks:
                callback = self.key_up_callbacks[event.key]
                callback()

        # Touch input
        elif event.type == pygame.FINGERDOWN:
            target_point = PercentagePoint(event.x, event.y)
            self.car.movement_targets[event.finger_id] = target_point
        elif event.type == pygame.FINGERMOTION:
            target_point = PercentagePoint(event.x, event.y)
            self.car.movement_targets[event.finger_id] = target_point
        elif event.type == pygame.FINGERUP:
            try:
                self.car.movement_targets.pop(event.finger_id)
            except KeyError:
                print(f"Ignoring keypress from #{event.finger_id} on #{event.touch_id}")

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

    def create_text(self, text: str, font: pygame.font.Font):
        surface = font.render(text, True, self.theme.FOREGROUND)
        return surface, surface.get_rect()

    def display_title(self, text: str):
        large_font = pygame.font.Font("freesansbold.ttf", 115)
        text_surface, text_rect = self.create_text(text, large_font)

        window_center_x, window_center_y = self.window_box().center()
        text_rect.center = math.floor(window_center_x), math.floor(window_center_y)
        self.surface.blit(text_surface, text_rect)
        self.update_display()

        print("You died!")
        time.sleep(2)

    def update_display(self):
        pygame.display.update()

    def trigger_crash(self):
        self.display_title("You died!")
        self.has_died = True

    def run(self):
        self.exited = False
        while not self.exited:
            print("Starting new game!")
            self.game_session()

    def game_session(self):
        self.has_died = False

        self.car = Car(game=self)
        self.objects.append(self.car)

        # first_block_position = self.window_box().width * 0.5
        active_block = Block(game=self, spawn_at=-700)
        self.objects.append(active_block)

        self.fps_counter = FPSCounter(
            game=self, spawn_point=PixelsPoint(0, 0, Corner.TOP_RIGHT)
        )
        self.objects.append(self.fps_counter)

        while not self.has_died and not self.exited:
            for event in pygame.event.get():
                self.on_event(event)

            # Reset the surface
            self.surface.fill(self.background_color)

            # Spawn a new block if the old one has passed the bottom screen edge
            if active_block.coordinates()[1] > self.height():
                self.objects.remove(active_block)
                active_block = Block(game=self, spawn_at=-20)
                self.objects.append(active_block)

            # Update the objects
            for object in self.objects:
                object.run_tick_tasks()
                object.draw()

            self.update_display()
            self.clock.tick(self.MAX_FPS)

            # miliseconds_per_frame = self.clock.get_rawtime()
            # print(miliseconds_per_frame)

        self.objects.clear()
        self.key_action_callbacks.clear()
        self.key_up_callbacks.clear()


class Texture:
    def __init__(self, width, height):
        self.base_width = width
        self.base_height = height

    def height(self) -> float:
        return self.base_height

    def width(self) -> float:
        return self.base_width

    def draw_at(self, top_left: PointSpecifier):
        pass


class PlainColorTexture(Texture):
    def __init__(self, game: Game, color: Tuple[int, int, int], width, height):
        self.game = game
        self.color = color
        super().__init__(width, height)

    def draw_at(self, top_left):
        x1, y1 = top_left.resolve(self.game, self.width(), self.height())

        pygame.draw.rect(
            self.game.surface,
            self.color,
            [x1, y1, self.width(), self.height()],
        )


class TextTexture(Texture):
    def width(self) -> float:
        return self.current_rect.width

    def height(self) -> float:
        return self.current_rect.height

    def get_content(self):
        provided_content = self._get_content()
        if isinstance(provided_content, str):
            return (provided_content, self.game.theme.FOREGROUND)
        return provided_content

    def render_text(self, start_x: float, start_y: float):
        """Computes a surface and bounding rect for the text, but doesn't draw it to the screen"""
        text_content, text_color = self.get_content()
        use_antialiasing = True
        text_surface = self.font.render(text_content, use_antialiasing, text_color)

        text_rect = text_surface.get_rect()
        text_rect.left = math.floor(start_x)
        text_rect.top = math.floor(start_y)

        return text_surface, text_rect

    def __init__(
        self,
        game: Game,
        get_content: Callable[[], str | Tuple[str, Tuple[int, int, int]]],
        font: pygame.font.Font,
        get_color: Optional[Callable[[], Tuple[int, int, int]]] = None,
    ):
        self.game = game
        self._get_content = get_content
        self.font = font
        self.get_color = get_color or (lambda: self.game.theme.FOREGROUND)
        self.current_rect = self.render_text(0, 0)[1]
        super().__init__(self.width(), self.height())

    def draw_at(self, top_left: PointSpecifier):
        start_x, start_y = top_left.resolve(self.game, self.width(), self.height())
        text_surface, text_rect = self.render_text(start_x, start_y)
        self.current_rect = text_rect
        self.game.surface.blit(text_surface, text_rect)


class ImageTexture(Texture):
    def __init__(self, game, image):
        self.game = game
        self.image = image

        width = self.image.get_width()
        height = self.image.get_height()
        super().__init__(width, height)

    def draw_at(self, top_left: PointSpecifier):
        start_x, start_y = top_left.resolve(self.game, self.width(), self.height())
        self.game.surface.blit(self.image, (start_x, start_y))


class GameObject:
    def height(self) -> float:
        return self.texture.height()

    def width(self) -> float:
        return self.texture.width()

    def spawn_point(self) -> PointSpecifier:
        raise NotImplementedError()

    def reset(self):
        """Moves the object to its initial position (spawn point)"""
        spawn_point = self.spawn_point()
        self.position = spawn_point
        # self.x, self.y = spawn_point.resolve(self.game, self.width(), self.height())

    def __init__(
        self,
        texture: Texture,
        window_resize_handler: Optional[WindowResizeHandler] = None,
        solid=True,
    ):
        assert hasattr(self, "game")
        assert isinstance(self.game, Game)
        self.game: Game = self.game
        self.tick_tasks: list[Callable] = []
        self.texture = texture
        self.window_resize_handler = window_resize_handler
        self.is_solid = solid
        self.reset()

    def draw(self):
        raise NotImplementedError()

    def run_tick_tasks(self):
        for callback in self.tick_tasks:
            callback()

    def calculate_center_bounds(self, parent_width: float, parent_height: float) -> Box:
        """Calculates the box of possible positions for the center point of this object"""
        x_padding = self.width() / 2
        y_padding = self.height() / 2

        x1 = 0 + x_padding
        x2 = parent_width - x_padding
        y1 = 0 + y_padding
        y2 = parent_height - y_padding

        return Box(x1, y1, x2, y2)

    def collision_box(self) -> Box:
        """Calculates the visual bounding box (i.e. collision box) for this object"""
        x1, y1 = self.position.resolve(self.game, self.width(), self.height())
        x2 = x1 + self.width()
        y2 = y1 + self.height()

        return Box(x1, y1, x2, y2)

    def calculate_position_percentage(self, bounds: Box) -> Tuple[float, float]:
        """Calculates the position of the center of the object, returning coordinates in the form (x, y)

        - Coordinates are scaled from 0.0 to 1.0 to represent percentage relative to the provided bounding box
        """
        center_x, center_y = self.collision_box().center()

        # Calculate the percentage position of the center relative to the bounding box
        percentage_x = (center_x - bounds.left) / bounds.width
        percentage_y = (center_y - bounds.top) / bounds.height

        return percentage_x, percentage_y

    def map_relative_position_to_box(
        self,
        position_percentage: Tuple[float, float],
        new_center_point_bounds: Box,
    ) -> Tuple[float, float]:
        """Calculates the new center point based on the saved percentage and the new bounding box dimensions"""
        limit = new_center_point_bounds

        # Calculate the new center based on the percentage and the new bounding box
        new_center_x = limit.left + limit.width * position_percentage[0]
        new_center_y = limit.top + limit.height * position_percentage[1]

        return new_center_x, new_center_y

    def is_within_window(self, allowed_margin=0.0):
        window = self.game.window_box()
        return self.collision_box().is_inside(window, allowed_margin)

    def is_outside_window(self):
        window = self.game.window_box()
        return self.collision_box().is_outside(window)

    def coordinates(self):
        return self.position.resolve(self.game, self.width(), self.height())


class WindowResizeHandler:
    def __init__(self, game_object: GameObject):
        self.object = game_object

    def get_new_position(self, event) -> Tuple[float, float]:
        raise NotImplementedError()

    def handle_window_resize(self, event):
        new_position = self.get_new_position(event)
        self.object.position.move_to(
            new_position, self.object.width(), self.object.height()
        )
        self.object.draw()


class LinearPositionScaling(WindowResizeHandler):
    def __init__(self, game_object: GameObject):
        super().__init__(game_object)

    def get_new_position(self, event) -> Tuple[float, float]:
        old_center_point_bounds = self.object.calculate_center_bounds(
            *event.old_dimensions
        )
        position_percentage = self.object.calculate_position_percentage(
            old_center_point_bounds
        )
        print("Was at", position_percentage)

        # Update object's position to be the in the same place relative to the window size
        new_center_point_bounds = self.object.calculate_center_bounds(event.w, event.h)
        new_center = self.object.map_relative_position_to_box(
            position_percentage, new_center_point_bounds
        )
        new_x = new_center[0] - self.object.width() / 2
        new_y = new_center[1] - self.object.height() / 2

        return new_x, new_y


class Velocity:
    def on_tick(self):
        x_movement = self.x
        y_movement = self.y

        self.object.position.move_right(x_movement)
        self.object.position.move_down(y_movement)

    def __init__(self, game_object: GameObject, base_speed: float):
        # Magnitudes of velocity, measured in pixels/tick
        self.x = 0
        self.y = 0

        # The speed that the object will travel at by default (pixels/tick)
        self.base_speed = base_speed

        self.object = game_object
        self.object.tick_tasks.append(self.on_tick)

    def shove_x(self, multiplier=1.0):
        self.x = self.base_speed * multiplier

    def shove_y(self, multiplier=1.0):
        self.y = self.base_speed * multiplier


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
        return (
            Asset.CAR_IMAGE_ALT
            if self.game.theme.ALTERNATE_TEXTURES
            else Asset.CAR_IMAGE
        )

    def spawn_point(self) -> PointSpecifier:
        return PixelsPoint(self.calculate_starting_x(), self.calculate_starting_y())

    def check_touch_input(self):
        # pygame_sdl2
        pass

    def check_collision_with_window_edge(self):
        # Allow up to 1/2 of the car to go off the edge before it counts as a crash
        allowed_margin = self.width() / 2

        if not self.is_within_window(allowed_margin):
            self.game.trigger_crash()

    def check_collision_with_other_objects(self):
        for object in self.game.objects:
            if not object.is_solid:
                continue
            collided = not self.collision_box().is_outside(object.collision_box())
            if not collided:
                continue
            if object == self:
                continue
            self.game.trigger_crash()

    def set_velocity_from_keypresses(self):
        if len(self.pressed_directions) == 0:
            self.velocity.x = 0
            return

        # Ensures the last-pressed key takes priority
        pressed_direction = self.pressed_directions[-1]
        if pressed_direction == "LEFT":
            self.velocity.shove_x(-1)
        if pressed_direction == "RIGHT":
            self.velocity.shove_x(+1)

    def move_towards_movement_target(self):
        if not self.movement_targets:
            return

        # If a movement key is currently being pressed, that takes priority
        if self.pressed_directions:
            return

        # Take the last-added movement target since it corresponds to the last-touched point
        last_touched_finger = list(self.movement_targets.keys())[-1]
        target_coordinates = self.movement_targets[last_touched_finger].resolve(game)
        our_coordinates = self.collision_box().center()

        # If the car is very close to the touch point, move it there directly
        pixels_difference = target_coordinates[0] - our_coordinates[0]
        if abs(pixels_difference) <= self.velocity.base_speed:
            _, old_y = self.coordinates()
            # Convert center pos to left-edge pos:
            move_to_x = target_coordinates[0] - self.width() / 2

            new_coordinates = move_to_x, old_y
            self.position.move_to(new_coordinates, self.width(), self.height())
            return

        # Calculate if we have to move left or right to get to the target position,
        # and then move in that direction
        if pixels_difference > 0:
            self.velocity.shove_x(+1)
        elif pixels_difference < 0:
            self.velocity.shove_x(-1)

    def __init__(self, game: Game):
        self.game = game
        texture = ImageTexture(game, self.get_texture_image())
        super().__init__(
            texture=texture, window_resize_handler=LinearPositionScaling(self)
        )

        self.velocity = Velocity(self, 5)
        self.pressed_directions = []
        self.movement_targets: dict[int, PointSpecifier] = {}
        self.tick_tasks.append(self.check_collision_with_window_edge)
        self.tick_tasks.append(self.check_collision_with_other_objects)
        self.tick_tasks.append(self.set_velocity_from_keypresses)
        self.tick_tasks.append(self.move_towards_movement_target)

        # Bind movement callbacks to the appropiate key actions
        @game.on_key_action("move.left")
        def start_moving_left(event):
            def undo(event):
                self.pressed_directions.remove("LEFT")

            self.pressed_directions.append("LEFT")
            return undo

        @game.on_key_action("move.right")
        def start_moving_right(event):
            def undo(event):
                self.pressed_directions.remove("RIGHT")

            self.pressed_directions.append("RIGHT")
            return undo

    def draw(self):
        self.texture.draw_at(self.position)


class Block(GameObject):
    def spawn_point(self) -> PointSpecifier:
        return PixelsPoint(self.spawn_at_x, self.spawn_at_y)

    def tick(self):
        pass

    def draw(self):
        self.texture.draw_at(self.position)

    def __init__(self, game: Game, spawn_at: float = 0):
        self.game = game
        self.spawn_at_x = random.randrange(0, self.game.width())
        self.spawn_at_y = spawn_at
        texture = PlainColorTexture(self.game, self.game.theme.FOREGROUND, 50, 50)
        super().__init__(
            texture=texture, window_resize_handler=LinearPositionScaling(self)
        )
        self.velocity = Velocity(self, 5)
        self.velocity.shove_y()


class FPSCounter(GameObject):
    def tick(self):
        pass

    def draw(self):
        self.texture.draw_at(self.position)

    def get_text(self) -> str:
        fps = self.game.clock.get_fps()
        return f"{fps:.0f} FPS"

    def __init__(self, game: Game, spawn_point: PointSpecifier):
        self.game = game
        self.font = pygame.font.Font("freesansbold.ttf", 12)
        self.spawn_point = lambda: spawn_point
        texture = TextTexture(game, self.get_text, self.font)

        super().__init__(texture=texture)


game = Game(theme=NightTheme)
game.run()

# Game has finished
pygame.quit()
quit()

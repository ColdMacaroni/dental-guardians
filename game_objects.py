#!/usr/bin/env python3
# This file contains all the classes used for the game.

# Local imports
import colors
import fonts

# Global imports. No bloat hehe
from enum import Enum, auto
from typing import Any
from os.path import join as path_join
from pygame import SRCALPHA
from pygame.surface import Surface
from pygame.draw import rect
from pygame.font import Font
from pygame.image import load as image_load
from pygame.transform import scale as transform_scale


# This one is at the top because it's very important.
def screen_size() -> tuple[int, int]:
    """
    This function will return the width and height for the pygame screen
    It is a function so that the values are constant and accessible from
    every function.
    I do not use global variables because they may be modified by accident,
    python does not support constants.
    :return: x, y tuple
    """
    return 800, 600


class GameStatus(Enum):
    """
    These enum objects will be used to keep track of what the game is doing
    """

    TITLE_SCREEN = auto()
    CREDITS = auto()
    EXIT = auto()
    BATTLE_START = auto()
    BATTLE_MENU = auto()
    ITEM_MENU = auto()
    WEAPON_MENU = auto()
    PLAYER_ATTACK = auto()
    ENEMY_ATTACK = auto()
    VICTORY = auto()
    DEFEAT = auto()


class WeaponTypes(Enum):
    """
    These enum objects will be used to keep track of what the game is doing
    """

    BRUSH = auto()
    FLOSS = auto()
    # = auto()


def draw_border(
    surface: Surface, thickness=5, color=colors.RGB.BLACK
) -> Surface:
    """
    Draw a border around surface
    :param surface: Pygame surface
    :param thickness: Thickness of the line
    :param color: Color of the line
    :return: Same surface with border
    """
    width, height = surface.get_size()

    # Draw borders clockwise
    rect(surface, color, ((0, 0), (width, thickness)))
    rect(surface, color, ((width - thickness, 0), (width, height)))
    rect(surface, color, ((0, height - thickness), (width, height)))
    rect(surface, color, ((0, 0), (thickness, height)))

    return surface


class Menu:
    """
    This class lets you create an interactive menu that can be "blited" into a
    surface
    """

    def __init__(
        self,
        options: dict[str, Any],
        size: tuple[int, int],
        font: Font,
        antialias=True,
        text_offset=0,
        text_color=colors.RGB.BLACK,
        text_background=None,
        text_selected=colors.RGB.YELLOW,
        background_color=colors.RGBA.TRANSPARENT,
        background_image=None,
        padding=0,
    ):
        """
        :param background_image:
        :param options: A dict of strings and values to be returned
        :param size: Tuple of size in px
        :param font: Pygame font object

        :keyword antialias: Bool. True
        :keyword text_offset: Vertical offset for the text in px.
        :keyword text_color: RGB(A). Black
        :keyword text_background: Background color for the text.
        :keyword text_selected: The background color for the selected text
        :keyword background_color: Background color for the menu
        :keyword background_image: Image to be blited into the background
        :keyword padding: In pixels, distance from each side of the surface
        that will not be touched. Single int or clockwise tuple
        """
        # Parameters
        self.options = options
        self.size = size
        self.font = font

        # Keywords
        self.antialias = antialias
        self.text_color = text_color
        self.text_background = text_background
        self.text_selected = text_selected
        self.text_offset = text_offset
        self.background_color = background_color
        self.background_image = background_image

        # Validate padding
        if isinstance(padding, int):
            self.padding = (padding, padding, padding, padding)

        elif isinstance(padding, tuple) and len(padding) == 4:
            self.padding = padding

        else:
            raise TypeError(
                "Padding must be an int or tuple of length 4, "
                f"not {type(padding)}"
            )

        # Defaults
        # Start at first option
        self.current_option = 0

    def update_option(self, diff: int):
        """
        Changes the current option
        :param diff: Value to be added to the current option
        """
        self.current_option += diff

        # Wrap around should support changes of more than 1
        num_options = len(self.options)

        if self.current_option >= num_options:
            self.current_option %= num_options

        elif self.current_option < 0:
            self.current_option = num_options - 1

    def get_option(self, option=None) -> Any:
        """
        Returns the value of the currently selected options
        :param option: Optional override to self.current_option
        :return: Any
        """
        opt = self.current_option if option is None else option

        return tuple(self.options.values())[opt]

    def get_surface(self) -> Surface:
        """
        Returns a pygame surface containing the menu to be blited into another
        surface
        :return: Pygame Surface
        """
        # SRCALPHA needed to support RGBA colours. Slow.
        surface = Surface(self.size, flags=SRCALPHA)
        surface.fill(self.background_color)

        if self.background_image is not None:
            surface.blit(self.background_image, (0, 0))

        # Offsets arent tuples so that they can be reassigned
        # Padding from left
        horizontal_offset = self.padding[-1]
        # Padding from top
        vertical_offset = self.padding[0]

        for idx, option in enumerate(self.options.keys()):
            # Display a different highlight if this option's the current one
            text_bg = self.text_background

            if idx == self.current_option:
                text_bg = self.text_selected

            text = self.font.render(
                option, self.antialias, self.text_color, text_bg
            )
            surface.blit(text, (horizontal_offset, vertical_offset))

            # get_linesize() should return recommended line size, this way text
            # won't overlap
            vertical_offset += self.font.get_linesize() + self.text_offset

        return surface


class TextBox:
    """
    General purpose text box
    """

    def __init__(
        self,
        text: str,
        size: tuple[int, int],
        font: Font,
        padding=5,
        fg=colors.RGB.BLACK,
        bg=colors.RGB.WHITE,
        line_thickness=5,
        line_color=colors.RGB.BLACK,
    ):
        """
        :param text: Take a guess
        :param size: Size in px for the box
        :param font: Pygame font

        :param padding: Pixels to not be touched
        :param fg: Text color
        :param bg: Box bg colour
        :param line_thickness: Border around the text box,
        :param line_color: Color of border, set to None to not have one
        """
        self.text = text
        self.size = size
        self.font = font

        self.fg = fg
        self.bg = bg
        self.line_thickness = line_thickness
        self.line_color = line_color

        self.padding = padding + line_thickness

    def set_text(self, new_text: str):
        self.text = new_text

    def get_surface(self) -> Surface:
        """
        Create a cool textbox!!!
        :return: pygame surface
        """
        surface = Surface(self.size, flags=SRCALPHA)
        surface.fill(self.bg)

        surface.blit(
            self.font.render(self.text, True, self.fg),
            (self.padding, self.padding),
        )

        if self.line_color is not None:
            return draw_border(surface, self.line_thickness, self.line_color)
        else:
            return surface


class Enemy:
    def __init__(
        self, name: str, hp: int, size: tuple[int, int], weakness=None
    ):
        """
        :param name: The name of the enemy
        :param hp: Int. Health points
        :param size: (x, y) tuple
        :param weakness: WeaponTypes attribute
        """
        self.name = name
        self.hp = self.max_hp = hp
        self.size = size
        self.weakness = weakness

        self.sprites = {
            "idle": None,
            "hurt": None,
            "attack": None,
            "defeated": None,
        }

    def load_sprites(self, folder: str) -> None:
        """
        Load the sprites into this thing!
        :param folder: A Folder containing idle.png
                                           hurt.png
                                           attack.png
                                           defeated.png
        """
        for sprite in self.sprites.keys():
            try:
                # Convert returns a faster to draw image.
                tmp = image_load(f"{path_join(folder, sprite)}.png").convert()

                # I like how images look with the black color key
                tmp.set_colorkey(colors.RGB.BLACK)

                # noinspection PyTypeChecker
                self.sprites[sprite] = transform_scale(tmp, self.size)

            except FileNotFoundError:
                print(f"{sprite}.png does not exist for {self.name}")

    def get_sprite(self, status: GameStatus) -> Surface:
        """
        Returns enemy sprite relevant to the status given
        :param status: GameStatus attribute
        :return: Pygame surface
        """
        # Set which sprite to use
        status_sprite = {GameStatus.BATTLE_START: "idle"}

        surface = Surface(self.size, flags=SRCALPHA)
        surface.fill(colors.RGBA.TRANSPARENT)

        # Get either the sprite for the given status
        # or the first item as a fallback
        sprite = self.sprites[
            status_sprite.get(status, tuple(self.sprites.keys())[0])
        ]

        if sprite is not None:
            # noinspection PyTypeChecker
            surface.blit(sprite, (0, 0))

        return surface

    def get_healthbar(
        self,
        size=None,
        padding=10,
        bg_color=colors.RGB.YELLOW,
        text_color=colors.RGB.BLACK,
        bar_color=colors.RGB.GREEN,
    ) -> Surface:
        """
        Creates a blittable healthbar, very cool
        :param size: (x, y) tuple

        :param padding: distance in px from each side
        :param bg_color: Pygame Color
        :param text_color: Pygame Color
        :param bar_color: Pygame Color
        :return: Pygame surface
        """
        if size is None:
            width, height = screen_size()
            size = (width // 2, height // 4.8)

        # No alpha, shouldn't be necessary
        surface = Surface(size)
        surface.fill(bg_color)

        surface.blit(
            fonts.HEALTHBAR.render(self.name.capitalize(), True, text_color),
            (padding, padding),
        )

        return surface

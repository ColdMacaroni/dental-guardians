#!/usr/bin/env python3
# This file contains all the classes used for the game.

# Local imports
import pygame.draw

import colors
import fonts

# Global imports. No bloat hehe
from enum import Enum, auto
from typing import Any, Union
from os.path import join as path_join
from pygame import SRCALPHA
from pygame.surface import Surface
from pygame.draw import rect
from pygame.font import Font
from pygame.image import load as image_load
from pygame.transform import scale as transform_scale


# Forward declaration
class Player:
    pass


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
    USE_ITEM = auto()
    PLAYER_ATTACK = auto()
    ENEMY_ATTACK = auto()
    VICTORY = auto()
    DEFEAT = auto()


class WeaponType(Enum):
    """
    These enum objects will be used to keep track of what the game is doing
    """

    NONE = auto()
    BRUSH = auto()
    FLOSS = auto()
    # = auto()


class ItemType(Enum):
    """
    These enum objects will be used to keep track of what the game is doing
    """

    NONE = auto()
    DEFENCE = auto()
    DAMAGE = auto()
    # = auto()


class Status:
    def __init__(self, status):
        self.status = status
        self.weapon = None
        self.item = None

    def update(self, new_status):
        if isinstance(new_status, GameStatus):
            self.status = new_status

        elif isinstance(new_status, Weapon):
            self.status = GameStatus.PLAYER_ATTACK
            self.weapon = new_status

        elif isinstance(new_status, Item):
            self.status = GameStatus.USE_ITEM
            self.item = new_status


class Weapon:
    def __init__(
        self,
        name: str,
        damage: int,
        weapon_type: WeaponType,
        size: tuple[int, int] = (256, 256),
    ):
        self.name = name
        self.damage = damage
        self.type = weapon_type
        self.size = size
        self.sprite = None

    def load_sprite(self, filename):
        sprite = pygame.image.load(filename).convert()
        sprite.set_colorkey(colors.RGB.BLACK)
        self.sprite = sprite

    def get_surface(self):
        width, height = screen_size()
        surface = pygame.Surface((width, height))
        surface.blit(
            self.sprite, (width - self.size[0], height - self.size[1])
        )


class Item:
    def __init__(self, name: str, item_type: ItemType, magnitude: int = 1):
        self.name = name
        self.type = item_type
        self.mag = magnitude


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
        line=False,
        line_thickness=5,
        line_color=colors.RGB.BLACK,
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
        :keyword line: Whether to display a line or not.
        :keyword line_thickness: Thickness in px of line
        :keyword line_color: Color of line
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

        self.line = line
        self.line_thickness = line_thickness
        self.line_color = line_color

        self.padding = padding
        if self.line:
            self.padding += self.line_thickness

        # Defaults
        # Start at first option
        self.current_option = 0

    def update_option(self, diff: int):
        """
        Changes the current option
        :param diff: Value to be added to the current option
        """
        # In case its empty
        if self.options:

            self.current_option += diff

            # Wrap around should support changes of more than 1
            num_options = len(self.options)

            if self.current_option >= num_options:
                self.current_option %= num_options

            elif self.current_option < 0:
                self.current_option = num_options - 1

    def get_option(self) -> Any:
        """
        Returns the value of the currently selected options
        :return: Any
        """
        if self.options:
            return tuple(self.options.values())[self.current_option]

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
        horizontal_offset = self.padding
        # Padding from top
        vertical_offset = self.padding

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

        if self.line:
            return draw_border(surface, self.line_thickness, self.line_color)
        else:
            return surface


class TextBox:
    """
    General purpose text box
    """

    def __init__(
        self,
        text: str,
        font: Font,
        size=None,
        padding=5,
        fg=colors.RGB.BLACK,
        bg=colors.RGB.WHITE,
        line=False,
        line_thickness=5,
        line_color=colors.RGB.BLACK,
    ):
        """
        :param text: Take a guess
        :param font: Pygame font

        :param size: Size in px for the box
        :param padding: Pixels to not be touched
        :param fg: Text color
        :param bg: Box bg colour

        :param line: Whether to display a line or not
        :param line_thickness: Border around the text box,
        :param line_color: Color of border, set to None to not have one
        """
        self.font = font

        self.fg = fg
        self.bg = bg

        self.line = line
        self.line_thickness = line_thickness
        self.line_color = line_color

        self.padding = padding + (line_thickness if self.line else 0)

        if size is not None:
            self.size = size
            self.text = self.format_text(text)

        else:
            # Get a tight fitting box.
            self.size = (
                self.font.size(text)[0] + self.padding * 2,
                self.font.get_height() + self.padding * 2,
            )
            self.text = [text]

    def set_text(self, new_text: str):
        self.text = self.format_text(new_text)

    def format_text(self, text) -> list[str]:
        # WIDTH is the number of chars each line can have. I'm just gonna use
        # 0 as an approximate because anything else would be difficult and
        # inefficient
        WIDTH = round(self.size[0] // self.font.size('0')[0])

        # Split into lines. Then wrap each one
        lines = text.split('\n')
        final_lines = list()
        for string in lines:
            prev = 0
            idx = 0
            split = 0
            n_lines = list()
            while idx < len(string):
                split = prev + WIDTH - 1
                for i in range(split, idx - 1, -1):
                    if i >= len(string):
                        break
                    if string[i] == ' ':
                        split = i
                        break
                else:
                    if string[split - WIDTH] != ' ':
                        prev -= 1

                n_lines.append(string[prev:split])
                prev = split + 1
                idx = prev
                idx += 1
            final_lines += n_lines

        return final_lines

    def get_surface(self) -> Surface:
        """
        Create a cool textbox!!!
        :return: pygame surface
        """

        surface = Surface(self.size, flags=SRCALPHA)
        surface.fill(self.bg)

        v_offset = 0
        for line in self.text:
            surface.blit(
                self.font.render(line, True, self.fg),
                (self.padding, self.padding + v_offset),
            )
            v_offset += self.font.get_linesize()

        if self.line:
            return draw_border(surface, self.line_thickness, self.line_color)
        else:
            return surface


class Enemy:
    def __init__(
        self,
        name: str,
        hp: int,
        size: tuple[int, int],
        damage=2,
        weakness=None,
    ):
        """
        :param name: The name of the enemy
        :param hp: Int. Health points
        :param size: (x, y) tuple
        :param weakness: WeaponTypes attribute
        """
        self.name = name.title()
        self.hp = self.max_hp = hp
        self.size = size
        self.weakness = weakness
        self.damage = damage

        self.sprites = {
            "idle": None,
            "hurt": None,
            "attack": None,
            "defeat": None,
        }

    def load_sprites(self, folder: str, sprites_dict: dict=None) -> None:
        """
        Load the sprites into this thing!
        :param folder: A Folder containing idle.png
                                           hurt.png
                                           attack.png
                                           defeated.png
        """
        if sprites_dict is None:
            sprites_dict = {key: f"{key}.png" for key in self.sprites.keys()}

        for sprite in self.sprites.keys():
            try:
                # Convert returns a faster to draw image.
                tmp = image_load(
                    f"{path_join(folder, sprites_dict[sprite])}"
                ).convert()

                # I like how images look with the black color key
                tmp.set_colorkey(colors.RGB.BLACK)

                # noinspection PyTypeChecker
                self.sprites[sprite] = transform_scale(tmp, self.size)

            except FileNotFoundError:
                print(f"{sprite}.png does not exist for {self.name}")

    def take_damage(self, weapon: Weapon):
        dmg = 2
        if weapon.type is self.weakness:
            dmg *= 2

        self.hp -= dmg
        return dmg

    def get_damage(self):
        return self.damage

    def get_sprite(self, status: GameStatus) -> Surface:
        """
        Returns enemy sprite relevant to the status given
        :param status: GameStatus attribute
        :return: Pygame surface
        """
        # Set which sprite to use
        status_sprite = {
            GameStatus.BATTLE_START: "idle",
            GameStatus.BATTLE_MENU: "idle",
            GameStatus.PLAYER_ATTACK: "hurt",
            GameStatus.ENEMY_ATTACK: "attack",
        }

        surface = Surface(self.size, flags=SRCALPHA)
        surface.fill(colors.RGBA.TRANSPARENT)

        # Get either the sprite for the given status
        # or the first item as a fallback
        sprite = self.sprites.get(status_sprite.get(status, None), None)
        if sprite is None:
            sprite = tuple(self.sprites.values())[0]

        if sprite is not None:
            # noinspection PyTypeChecker
            surface.blit(sprite, (0, 0))

        return surface

    def get_healthbar(
        self,
        size=None,
        padding=10,
        bg_color=colors.RGB.WHITE,
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
        linesize = fonts.HEALTHBAR.get_linesize()

        surface.blit(
            fonts.HEALTHBAR.render(self.name.capitalize(), True, text_color),
            (padding, padding),
        )
        surface.blit(
            fonts.HEALTHBAR.render(
                f"{self.hp}/{self.max_hp} HP", True, text_color
            ),
            (padding, padding + linesize),
        )

        bar_thickness = size[1] // 10
        bar_width = size[0] - 30

        bar_complete = round(bar_width * (self.hp / self.max_hp))

        rect(
            surface,
            text_color,
            (
                (10, linesize * 2.5),
                (bar_width, bar_thickness),
            ),
        )

        rect(
            surface,
            bar_color,
            (
                (10, linesize * 2.5),
                (bar_complete, bar_thickness),
            ),
        )

        return draw_border(surface)


# noinspection PyRedeclaration
class Player:
    def __init__(
        self,
        max_hp,
        weapons: list[Union[Weapon, None]],
        items: list[Union[Item, None]],
        level=1,
    ):
        self.max_hp = max_hp
        self.hp = self.max_hp
        self.weapons = weapons
        self.level = level

        self.defence = 0

        self.items = items

    def __str__(self):
        return f"{self.hp}/{self.max_hp} HP\nLevel {self.level}."

    def use(self, item: Item):
        if item.type is ItemType.DEFENCE:
            self.defence += 1

        pass

    def take_damage(self, dmg: Union[int, float]) -> int:
        taken = dmg - self.defence / 2
        if taken < 0:
            taken = 0

        self.hp -= taken

        if self.hp < 0:
            self.hp = 0

        return taken

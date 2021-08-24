#!/usr/bin/env python3
# game.py
# A game for teaching kids about dental hygiene

# Local library imports
from typing import Any

import colors
import fonts

# Global library imports
import pygame
import os
from random import choice
from enum import Enum, auto
from itertools import islice


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


class Menu:
    """
    This class lets you create an interactive menu that can be "blited" into a surface
    """

    def __init__(self, options: dict[str, Any], size: tuple[int, int], font: pygame.font.Font,
                 antialias=True,
                 text_offset=0,
                 text_color=colors.RGB.BLACK,
                 text_background=None,
                 text_selected=colors.RGB.YELLOW,
                 background_color=colors.RGBA.TRANSPARENT,
                 background_image=None,
                 padding=0):
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
        :keyword padding: In pixels, distance from each side of the surface that will not be touched.
                          Can be either an int to signify the same padding on all sides or a tuple
                          of length 4 if you want to be specific. Clockwise.
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
            raise Exception("Padding must be an int or tuple of length 4, not " + str(type(float)))

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

        # The following code has been adapted from https://stackoverflow.com/a/59740280
        # Changed variable names and used the result of the second next as key for dict
        it = iter(self.options)

        # Consume n elements.
        next(islice(it, opt, opt), None)

        # Return the value at the current position.
        # This raises StopIteration if n is beyond the limits.
        # Use next(it, None) to suppress that exception.
        return self.options[next(it)]

    def get_surface(self) -> pygame.surface.Surface:
        """
        Returns a pygame surface containing the menu to be blited into another surface
        :return: Pygame Surface
        """
        # SRCALPHA needed to support RGBA colours. Slow.
        surface = pygame.Surface(self.size, flags=pygame.SRCALPHA)
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

            text = self.font.render(option, self.antialias, self.text_color, text_bg)
            surface.blit(text, (horizontal_offset, vertical_offset))

            # get_linesize() should return recommended line size, this way text won't overlap
            vertical_offset += self.font.get_linesize() + self.text_offset

        return surface


class Enemy:
    def __init__(self, name: str, hp: int, size: tuple[int, int], weakness=None):
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

        self.sprites = {"idle": None,
                        "hurt": None,
                        "attack": None,
                        "defeated": None}

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
                tmp = pygame.image.load(f"{os.path.join(folder, sprite)}.png").convert()

                # I like how images look with the black color key
                tmp.set_colorkey(colors.RGB.BLACK)

                # noinspection PyTypeChecker
                self.sprites[sprite] = pygame.transform.scale(tmp, self.size)

            except FileNotFoundError:
                print(f"{sprite}.png does not exist for {self.name}")

    def get_sprite(self, status: GameStatus) -> pygame.surface.Surface:
        """
        Returns enemy sprite relevant to the status given
        :param status: GameStatus attribute
        :return: Pygame surface
        """
        # Set which sprite to use
        status_sprite = {
            GameStatus.BATTLE_START: "idle"
        }

        surface = pygame.surface.Surface(self.size, flags=pygame.SRCALPHA)
        surface.fill(colors.RGBA.TRANSPARENT)

        # Get either the sprite for the given status or the first item as a fallback
        sprite = self.sprites[
            status_sprite.get(status,
                              tuple(self.sprites.keys())[0])]

        if sprite is not None:
            # noinspection PyTypeChecker
            surface.blit(sprite, (0, 0))

        return surface

    def get_healthbar(self, size: tuple[int, int],
                      padding=10,
                      bg_color=colors.RGB.YELLOW,
                      text_color=colors.RGB.BLACK,
                      bar_color=colors.RGB.GREEN) -> pygame.surface.Surface:
        """
        Creates a blittable healthbar, very cool
        :param size: (x, y) tuple

        :param padding: distance in px from each side
        :param bg_color: Pygame Color
        :param text_color: Pygame Color
        :param bar_color: Pygame Color
        :return: Pygame surface
        """
        # No alpha, shouldn't be necessary
        surface = pygame.surface.Surface(size)

        surface.fill(bg_color)

        surface.blit(
                fonts.HEALTHBAR.render(
                    self.name.capitalize(),
                    True,
                    text_color),
                (padding, padding))

        return surface


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


# -- Game
def generate_title(title: str,
                   image=None,
                   text_color=colors.RGB.BLACK, background_color=None) -> pygame.surface.Surface:
    """
    Creates a title screen!
    :param title: String
    :param image: blitable background

    :param text_color: Title font color
    :param background_color: Bg color

    :return: surface to be blited
    """
    size = screen_size()

    title_screen = pygame.Surface(size, flags=pygame.SRCALPHA)

    if image is not None:
        # Resize image to fit
        img_size = image.get_size()

        # Get index of smallest side
        smallest = 0 if img_size[0] < img_size[1] else 1

        # Fill with place holders
        new_img_size = [0, 0]

        # Make smallest size of target
        new_img_size[smallest] = size[smallest]

        # Not 1 -> 0, Not 0 -> 1. Yeah. Calculate new size using ratio
        new_img_size[not smallest] = round(
                (new_img_size[smallest] / img_size[smallest])
                * img_size[not smallest])

        resized_img = pygame.transform.scale(image, new_img_size)

        title_screen.blit(resized_img, (0, 0))

    title_screen.blit(
            fonts.TITLE.render(
                title,
                True,
                text_color,
                background_color),
            (30, size[1] // 2))

    return title_screen


def load_enemies(enemy_folder: str, hp=40) -> dict:
    """
    Loads enemies from the enemy folder, using the folder names as enemy names
    :param enemy_folder: A string to a folder containing folders
    :param hp: HP points for each enemy to have
    :return: A dict of Enemy objects
    """
    # Get list of folders, actually checking if they are folders
    enemy_folders = [folder
                     for folder in os.listdir(enemy_folder)
                     if os.path.isdir(os.path.join(enemy_folder, folder))]

    enemies = dict()
    for enemy in enemy_folders:
        # Tuple is sprite size
        enemies[enemy] = Enemy(enemy, hp, (256, 256))

        enemies[enemy].load_sprites(os.path.join(enemy_folder, enemy))

    return enemies


def generate_overlays() -> dict:
    """
    Generates all the overlays used in the program
    :return: Dict of GameStatus: Pygame surface
    """
    overlays = dict()
    overlays[GameStatus.TITLE_SCREEN] = generate_title(
        "Dental Guardian",
        image=pygame.image.load(
            os.path.join("images", "titlescreen.png")
        ),
        background_color=colors.RGB.WHITE)

    # TODO: Add a background to list
    # This is a list so that multiple stuff can be added
    overlays[GameStatus.BATTLE_START] = [None]

    # For checking that the layout fits the sample
    overlays[GameStatus.BATTLE_START] = [
     pygame.image.load(os.path.join("images", "example_layout.png")).convert()
    ]

    return overlays


def generate_menus() -> dict[GameStatus, Menu]:
    """
    Generates all the menus used
    :return: dict of Game status: menu obj
    """
    menus = dict()
    menus[GameStatus.TITLE_SCREEN] = Menu(
        {
            "Start": GameStatus.BATTLE_START,
            "Credits": GameStatus.CREDITS,
            "Exit": GameStatus.EXIT
        },
        (200, 128),
        fonts.BIG_MENU,
        padding=5,
        background_color=colors.MENU_BACKGROUND,
        text_selected=colors.MENU_HIGHLIGHTED)

    return menus


def generate_menu_offsets() -> dict[GameStatus, tuple[int, int]]:
    """
    Generates a dict of the offsets used for blitting the menus into the screen
    :return: A dict of string: (x, y)
    """
    width, height = screen_size()

    offsets = dict()
    offsets[GameStatus.TITLE_SCREEN] = (30, height - (height // 3))

    return offsets


# --
# 20x10 padding for battle menus


def main():
    """
    Contains and sets up the main event loop for pygame
    """
    # Start up pygame
    pygame.init()
    pygame.font.init()
    clock = pygame.time.Clock()

    # Also creating a tuple because some functions take that
    size = width, height = screen_size()
    screen = pygame.display.set_mode(size, vsync=1, flags=pygame.SRCALPHA)
    pygame.display.set_caption("Dental Guardians")

    menus = generate_menus()
    menu_offsets = generate_menu_offsets()
    overlays = generate_overlays()

    active_menu = None
    active_menu_offset = None
    active_overlay = None

    enemies = load_enemies(os.path.join("images", "enemies"))
    enemy = None

    status = GameStatus.TITLE_SCREEN

    playing = True
    while playing:
        # -- Event loop
        for event in pygame.event.get():
            # Mark current loop as last
            if event.type == pygame.QUIT:
                playing = False

            elif event.type == pygame.KEYDOWN:
                if active_menu is not None:
                    if event.key == pygame.K_UP:
                        active_menu.update_option(-1)

                    elif event.key == pygame.K_DOWN:
                        active_menu.update_option(1)

                    # K_RETURN is enter key
                    elif event.key == pygame.K_RETURN:
                        # Update status
                        status = active_menu.get_option()

                        # Reset active overlay and menu
                        active_menu = None
                        active_overlay = None
        # --

        # Set the actives to the current status
        if active_menu is None:
            active_menu = menus.get(status, None)
            active_menu_offset = menu_offsets.get(status, None)

        if active_overlay is None:
            active_overlay = overlays.get(status, None)

        # Reset screen
        screen.fill(colors.RGB.WHITE)

        # This would be so nice with a switch case (match)
        # -- Game statuses
        if status is GameStatus.TITLE_SCREEN:
            # Nothing to do here that is not handled by overlay and menu
            pass

        # Start battle
        elif status is GameStatus.BATTLE_START:
            assert isinstance(active_overlay, list), \
                f"Active overlay is {type(active_overlay)} " \
                f"instead of list during {status}"

            # Pick enemy
            if enemy is None:
                enemy = choice(tuple(enemies.values()))

            # Store so that it doesn't have to be called twice
            enemy_surface = enemy.get_sprite(status)
            enemy_offset = (width // 15, height // 25)

            healthbar_surface = enemy.get_healthbar((width // 2, height // 4.8))
            healthbar_offset = (width - healthbar_surface.get_width() - 50, 50)

            # Try to replace so that positioning stays the same
            if len(active_overlay) > 1:
                active_overlay[1] = (enemy_surface, enemy_offset)
            else:
                active_overlay.append((enemy_surface, enemy_offset))

            if len(active_overlay) > 2:
                active_overlay[2] = (healthbar_surface, healthbar_offset)
            else:
                active_overlay.append((healthbar_surface, healthbar_offset))

        elif status is GameStatus.EXIT:
            playing = False

        # -- Put the stuff
        if active_overlay is not None:
            if isinstance(active_overlay, list):
                screen.blits(
                    tuple(
                        # Create a tuple of overlays and offsets,
                        # the offset will be 0,0 if not set
                        [(overlay, (0, 0)) if not isinstance(overlay, tuple) else overlay
                         for overlay in active_overlay
                         if overlay is not None]
                    ))
            else:
                screen.blit(active_overlay, (0, 0))

        if active_menu is not None:
            screen.blit(active_menu.get_surface(), active_menu_offset)
        # --

        # Update display
        pygame.display.flip()

        # print(clock.get_fps())
        clock.tick(60)

    # Clean up and say bye
    pygame.font.quit()
    pygame.quit()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# game.py
# A game for teaching kids about dental hygiene

# Local library imports
import pathlib

import colors

# Global library imports
import pygame
from enum import Enum, auto
from itertools import islice
import os


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


class Menu:
    """
    This class lets you create an interactive menu that can be "blited" into a surface
    """
    def __init__(self, options, size, font: pygame.font.Font,
                 antialias=True,
                 text_offset=0,
                 text_color=colors.RGB.BLACK,
                 text_background=colors.RGBA.TRANSPARENT,
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
        self.text_selected= text_selected
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

    def update_option(self, diff):
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

    def get_option(self, option=None):
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

    def get_surface(self):
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
            if idx == self.current_option:
                text = self.font.render(option, self.antialias, self.text_color, self.text_selected)
            else:
                text = self.font.render(option, self.antialias, self.text_color, self.text_background)
            surface.blit(text, (horizontal_offset, vertical_offset))

            # get_linesize() should return recommended line size, this way text won't overlap
            vertical_offset += self.font.get_linesize() + self.text_offset

        return surface


def screen_size():
    """
    This function will return the width and height for the pygame screen
    It is a function so that the values are constant and accessible from
    every function.
    I do not use global variables because they may be modified by accident,
    python does not support constants.
    :return: x, y tuple
    """
    return 600, 400


# -- Pygame
def generate_title(title, title_font, image=None, text_color=colors.RGB.BLACK):
    """
    Creates a title screen!
    :param image: blitable background
    :param title: String
    :param title_font: pygame font

    :param text_color: Menu and title font color

    :return: surface to be blited
    """
    size = screen_size()

    title_screen = pygame.Surface(size, flags=pygame.SRCALPHA)

    if image is not None:
        title_screen.blit(image, (0, 0))

    title_screen.blit(title_font.render(title, True, text_color), (30, size[1] // 10))

    return title_screen

# --


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

    active_menu = None
    active_menu_offset = None
    active_overlay = None

    status = GameStatus.TITLE_SCREEN

    playing = True
    while playing:
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
                        print(active_menu.get_option())

        screen.fill(colors.RGB.WHITE)

        if status is GameStatus.TITLE_SCREEN:
            if active_overlay is None and active_menu is None:
                title_menu = Menu({"Start": GameStatus.BATTLE_START,
                                   "Credits": GameStatus.CREDITS,
                                   "Exit": GameStatus.EXIT},
                                  (200, 150),
                                  pygame.font.SysFont("Arial", 34))

                active_overlay = generate_title("Dental Guardians",
                                                pygame.font.SysFont("Arial", 64),
                                                image=pygame.image.load(
                                                  os.path.join("images", "titlescreen.png")
                                                ))
                active_menu = title_menu
                active_menu_offset = (width//3, height//2)

        elif status is GameStatus.BATTLE_MENU:
            pass

        if active_overlay is not None:
            screen.blit(active_overlay, (0, 0))

        if active_menu is not None:
            screen.blit(active_menu.get_surface(), active_menu_offset)

        #screen.blit(test_menu.get_surface(), (200, 200))  # TEST

        # Update display
        pygame.display.flip()

        # print(clock.get_fps())
        clock.tick(60)  # fps

    # Clean up and say bye
    pygame.font.quit()
    pygame.quit()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# game.py
# A game for teaching kids about dental hygiene

# Local library imports
import colors

# Global library imports
import pygame
from enum import Enum, auto
# Import os for os.path.join(), it'll be useful for cross compatibility


class GameStatus(Enum):
    """
    These enum objects will be used to keep track of what the game is doing
    """
    TITLE_SCREEN = auto()
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
                 text_color=colors.RGB.BLACK, background_color=colors.RGBA.TRANSPARENT,
                 padding=0):
        """
        :param options: A dict of strings and values to be returned
        :param size: Tuple of size in px
        :param font: Pygame font object

        :keyword antialias: Bool. True
        :keyword text_color: RGB(A). Black
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
        self.background_color = background_color

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

    def get_surface(self):
        """
        Returns a pygame surface containing the menu to be blited into another surface
        :return: Pygame Surface
        """
        surface = pygame.Surface(self.size, flags=pygame.SRCALPHA)
        surface.fill(self.background_color)
        # Offsets arent tuples so that they can be reassigned
        # Padding from left
        horizontal_offset = self.padding[-1]
        # Padding from top
        vertical_offset = self.padding[0]
        for option in self.options.keys():
            text = self.font.render(option, self.antialias, self.text_color)
            surface.blit(text, (horizontal_offset, vertical_offset))

            # get_linesize should return recommended line size, this way text won't overlap
            vertical_offset += self.font.get_linesize()

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
    screen = pygame.display.set_mode(size, vsync=1)
    pygame.display.set_caption("Dental Guardians")

    status = GameStatus.TITLE_SCREEN

    test_menu = Menu({"Start": 1, "End": 0}, (200, 200), pygame.font.SysFont("Arial", 17))  # TEST

    playing = True
    while playing:
        for event in pygame.event.get():
            # Mark current loop as last
            if event.type == pygame.QUIT:
                playing = False

        screen.fill(colors.RGB.WHITE)

        if status is GameStatus.TITLE_SCREEN:
            pass

        elif status is GameStatus.BATTLE_MENU:
            pass

        screen.blit(test_menu.get_surface(), (5, 5))  # TEST

        # Update display
        pygame.display.flip()

        clock.tick(60)  # fps

    # Clean up and say bye
    pygame.font.quit()
    pygame.quit()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()

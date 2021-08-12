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
    def __init__(self, options, size):
        """
        :param options: A list of strings that will be the options in the menu
        :param size: Tuple of size in px
        """
        self.options = options
        self.size = size

    def get_surface(self):
        """
        Returns a pygame surface containing the menu to be blited into another surface
        :return: Pygame Surface
        """
        surface = pygame.Surface(self.size)

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
    pygame.init()
    clock = pygame.time.Clock()

    # Also creating a tuple because some functions take that
    size = width, height = screen_size()
    screen = pygame.display.set_mode(size, vsync=1)
    pygame.display.set_caption("Dental Guardians")

    status = GameStatus.TITLE_SCREEN

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

        # Update display
        pygame.display.flip()

        clock.tick(60)  # fps

    # Clean up and say bye
    pygame.quit()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()

#!/usr/bin/env python3
# game.py
# A game for teaching kids about dental hygiene

# Local imports
import colors
import fonts
import scenes
from game_objects import *

# Global imports
import os
import pygame
from enum import Enum, auto
from random import choice
from typing import Any, Union


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
def generate_title(
    title: str, image=None, text_color=colors.RGB.BLACK, background_color=None
) -> pygame.surface.Surface:
    """
    Creates a title screen!
    :param title: String
    :param image: blittable background

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
            * img_size[not smallest]
        )

        resized_img = pygame.transform.scale(image, new_img_size)

        title_screen.blit(resized_img, (0, 0))

    title_screen.blit(
        fonts.TITLE.render(title, True, text_color, background_color),
        (30, size[1] // 2),
    )

    return title_screen


def load_enemies(enemy_folder: str, hp=40) -> dict:
    """
    Loads enemies from the enemy folder, using the folder names as enemy names
    :param enemy_folder: A string to a folder containing folders
    :param hp: HP points for each enemy to have
    :return: A dict of Enemy objects
    """
    # Get list of folders, actually checking if they are folders
    enemy_folders = [
        folder
        for folder in os.listdir(enemy_folder)
        if os.path.isdir(os.path.join(enemy_folder, folder))
    ]

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
        image=pygame.image.load(os.path.join("images", "titlescreen.png")),
        background_color=colors.RGB.WHITE,
    )

    # TODO: Add a background to list
    # This is a list so that multiple stuff can be added
    overlays[GameStatus.BATTLE_START] = [None]

    # For checking that the layout fits the sample
    overlays[GameStatus.BATTLE_START] = [
        pygame.image.load(
            os.path.join("images", "example_layout.png")
        ).convert()
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
            "Exit": GameStatus.EXIT,
        },
        (200, 128),
        fonts.BIG_MENU,
        padding=5,
        background_color=colors.MENU_BACKGROUND,
        text_selected=colors.MENU_HIGHLIGHTED,
    )

    return menus


def generate_offsets() -> dict[str, dict[GameStatus, tuple[int, int]]]:
    """
    Generates a dict of the offsets used for blitting the menus into the screen
    :return: A dict of string: (x, y)
    """
    width, height = screen_size()

    menu_offsets = dict()
    menu_offsets[GameStatus.TITLE_SCREEN] = (30, height - (height // 3))

    text_offsets = dict()
    text_offsets[GameStatus.BATTLE_START] = (width*2//5, height//3)

    return {"menu": menu_offsets, "text": text_offsets}


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
    offsets = generate_offsets()
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
            active_menu_offset = offsets["menu"].get(status, None)

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
            assert isinstance(active_overlay, list), (
                f"Active overlay is {type(active_overlay)} "
                f"instead of list during {status}"
            )

            # Pick enemy
            if enemy is None:
                enemy = choice(tuple(enemies.values()))

            # Store so that it doesn't have to be called twice
            enemy_surface = enemy.get_sprite(status)
            enemy_offset = (width // 15, height // 25)

            healthbar_surface = enemy.get_healthbar(
                (width // 2, height // 4.8)
            )
            healthbar_offset = (width - healthbar_surface.get_width() - 50, 50)

            text = TextBox(
                "Hellooooo",
                (width * 2 // 3, height // 3),
                fonts.DEFAULT,
                bg=colors.RGB.LIGHT_BLUE,
            )
            text_surface = text.get_surface()
            text_offset = (
                width - text_surface.get_width() - 20,
                height - text_surface.get_height() - 10,
            )
            # Try to replace so that positioning stays the same
            if len(active_overlay) > 1:
                active_overlay[1] = (text_surface, text_offset)
            else:
                active_overlay.append((text_surface, text_offset))

            if len(active_overlay) > 2:
                active_overlay[2] = (enemy_surface, enemy_offset)
            else:
                active_overlay.append((enemy_surface, enemy_offset))

            if len(active_overlay) > 3:
                active_overlay[3] = (healthbar_surface, healthbar_offset)
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
                        [
                            (overlay, (0, 0))
                            if not isinstance(overlay, tuple)
                            else overlay
                            for overlay in active_overlay
                            if overlay is not None
                        ]
                    )
                )
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
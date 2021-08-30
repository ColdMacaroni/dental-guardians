#!/usr/bin/env python3
# game.py
# A game for teaching kids about dental hygiene

# Local imports
import colors
import fonts
import scenes
from game_objects import screen_size, GameStatus, Enemy

# Global imports
import os
import pygame
from random import choice
from time import time


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

    all_scenes = scenes.generate_scenes()

    enemies = load_enemies(os.path.join("images", "enemies"))
    enemy = None

    status = GameStatus.TITLE_SCREEN

    # For handling changing stuff after while
    start_time = 0

    playing = True
    while playing:
        active_scene = all_scenes.get(status, None)

        # Reset screen
        screen.fill(colors.RGB.WHITE)

        # This would be so nice with a switch case (match)
        # -- Game statuses
        # - Nothing to do for TITLE_SCREEN
        # Start battle
        if status is GameStatus.BATTLE_START:
            assert isinstance(active_scene, scenes.BattleScene), (
                f"{status} scene is {type(active_scene)} "
                f"not {type(scenes.BattleScene)}"
            )
            # Pick enemy
            if active_scene.enemy.object is None:
                active_scene.enemy.object = enemy = choice(tuple(enemies.values()))

            active_scene.statics["info_box"].object.set_text(
                f"{all_scenes[status].enemy.object.name.capitalize()} challenges you!"
            )

            # Theres probably a way to do this with async but idk how to use that.
            # Go to next animation after a sec
            if start_time:
                if time() - start_time > 3:
                    start_time = 0
                    status = GameStatus.BATTLE_MENU
            else:
                start_time = time()

        elif status is GameStatus.BATTLE_MENU:
            active_scene.statics["info_box"].object.set_text()

        elif status is GameStatus.EXIT:
            playing = False

        if (active_scene := all_scenes.get(status, None)) is not None:
            screen.blit(active_scene.get_surface(status), (0, 0))
        # --

        # Update display
        pygame.display.flip()

        # print(clock.get_fps())
        clock.tick(60)

        # -- Event loop
        for event in pygame.event.get():
            # Mark current loop as last
            if event.type == pygame.QUIT:
                playing = False

            elif event.type == pygame.KEYDOWN:
                if (
                    active_scene is not None
                    and active_scene.menu.object is not None
                ):
                    active_menu = active_scene.menu.object
                    if event.key == pygame.K_UP:
                        active_menu.update_option(-1)

                    elif event.key == pygame.K_DOWN:
                        active_menu.update_option(1)

                    # K_RETURN is enter key
                    elif event.key == pygame.K_RETURN:
                        # Update status
                        new_option = active_menu.get_option()
                        status = (
                            new_option if new_option is not None else status
                        )
        # --

    # Clean up and say bye
    pygame.font.quit()
    pygame.quit()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()

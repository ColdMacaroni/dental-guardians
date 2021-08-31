#!/usr/bin/env python3
# game.py
# A game for teaching kids about dental hygiene
# v0.1

# Local imports
from typing import Union

import colors
import fonts
import game_objects
import scenes
from game_objects import screen_size, GameStatus, Enemy, Weapon

# Global imports
import os
import pygame
from random import choice
from time import time


def load_enemies(enemy_folder: str, hp=40) -> tuple:
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

    enemies = list()
    for enemy in enemy_folders:
        # Tuple is sprite size
        # TODO: Read args from jason file
        # args = json.load(os.path.join(enemy_folder, )
        new_enemy = Enemy(enemy, hp, (256, 256))

        new_enemy.load_sprites(os.path.join(enemy_folder, enemy))
        enemies.append(new_enemy)

    return tuple(enemies)


# TODO: Could probably fuse this with load enemy
def load_weapon(weapon_folder: str) -> list[Union[Weapon, None]]:
    weapon_folders = [
        folder

        for folder in os.listdir(weapon_folder)
        if os.path.isdir(os.path.join(weapon_folder, folder))
    ]
    weapons = list()

    for weapon in weapon_folders:
        # Tuple is sprite size
        # TODO: Read args from jason file
        # args = json.load(os.path.join(enemy_folder, )
        new_weapon = Weapon(weapon, 2, game_objects.WeaponType.BRUSH)

        # new_weapon.load_sprites(os.path.join(enemy_folder, weapon))
        weapons.append(new_weapon)

    return weapons if weapons else (None,)
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

    player = game_objects.Player(32, load_weapon(os.path.join("images", "weapons")))

    enemies = load_enemies(os.path.join("images", "enemies"))

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
                active_scene.enemy.object = choice(enemies)

            active_scene.statics["info_box"].object.set_text(
                f"{all_scenes[status].enemy.object.name.capitalize()} challenges you!"
            )

            # Theres probably a way to do this with async but idk how to use that.
            # Go to next animation after a sec
            if start_time:
                if time() - start_time > 1.5:
                    start_time = 0
                    status = GameStatus.BATTLE_MENU
            else:
                start_time = time()

        elif status is GameStatus.BATTLE_MENU:
            active_scene.statics["info_box"].object.set_text(str(player))

        elif status is GameStatus.WEAPON_MENU:
            # Set options
            if not active_scene.menu.object.options:
                active_scene.menu.object.options = {weapon.name: weapon for weapon in player.weapons if weapon is not None}
                active_scene.menu.object.options["Back"] = GameStatus.BATTLE_MENU

        elif status is GameStatus.ITEM_MENU:
            # Set weapons.
            if not active_scene.menu.object.options:
                active_scene.menu.object.options = player.items
                active_scene.menu.object.options["Back"] = GameStatus.BATTLE_MENU

        elif status is GameStatus.EXIT:
            playing = False

        if (active_scene := all_scenes.get(status, None)) is not None:
            screen.blit(active_scene.get_surface(status), (0, 0))
        # --

        # Update display
        pygame.display.flip()

        # print(clock.get_fps())
        # clock.tick(60)
        clock.tick(30)

        # -- Event loop
        for event in pygame.event.get():
            # Mark current loop as last
            if event.type == pygame.QUIT:
                playing = False

            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_SPACE:
                    active_scene.enemy.object.hp -= 1

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

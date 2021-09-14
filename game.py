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
from game_objects import screen_size, GameStatus, Enemy, Weapon, Status

# Global imports
import os
import pygame
import json
from random import choice
from time import time


def load_enemy(data: dict, folder: str) -> Enemy:
    weaknesses = {"placeholder": object()}

    enemy = Enemy(
        name=data["name"],
        hp=data["hp"],
        size=(data["size"]["x"], data["size"]["x"]),
        weakness=weaknesses.get(data.get("weakness", None), None),
    )

    enemy.load_sprites(folder, data["sprites"])

    return enemy


def load_weapon(data: dict, folder: str) -> Weapon:
    types = {
        "brush": game_objects.WeaponType.BRUSH,
        "floss": game_objects.WeaponType.FLOSS,
    }
    print(folder)
    return Weapon(
        name=data["name"],
        damage=data["damage"],
        weapon_type=types.get(data.get("weapon_type", None), None),
    )


def load_objects(folder: str) -> tuple:

    folders = [
        f for f in os.listdir(folder) if os.path.isdir(os.path.join(folder, f))
    ]
    print(os.listdir(folder))
    types = {"enemy": load_enemy, "weapon": load_weapon}

    objects = list()

    for obj in folders:
        with open(os.path.join(folder, obj, "data.json")) as file:
            data = json.load(file)

        objects.append(types[data["type"]](data, os.path.join(folder, obj)))

    return tuple(objects)


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

    weapons = list(load_objects(os.path.join("objects", "weapons")))

    player = game_objects.Player(32, weapons=weapons)

    enemies = load_objects(os.path.join("objects", "enemies"))

    status = Status(GameStatus.TITLE_SCREEN)

    # For handling changing stuff after while
    start_time = 0

    playing = True
    while playing:
        active_scene = all_scenes.get(status.status, None)

        # Reset screen
        screen.fill(colors.RGB.WHITE)

        # This would be so nice with a switch case (match)
        # -- Game statuses
        # - Nothing to do for TITLE_SCREEN
        # Start battle
        if status.status is GameStatus.BATTLE_START:
            assert isinstance(active_scene, scenes.BattleScene), (
                f"{status.status} scene is {type(active_scene)} "
                f"not {type(scenes.BattleScene)}"
            )
            # Pick enemy
            if active_scene.enemy.object is None:
                active_scene.enemy.object = choice(enemies)

            active_scene.statics["info_box"].object.set_text(
                f"{all_scenes[status.status].enemy.object.name.capitalize()} challenges you!"
            )

            # Theres probably a way to do this with async but idk how to use that.
            # Go to next animation after a sec
            if start_time:
                if time() - start_time > 1.5:
                    start_time = 0
                    status.update(GameStatus.BATTLE_MENU)
            else:
                start_time = time()

        elif status.status is GameStatus.BATTLE_MENU:
            active_scene.statics["info_box"].object.set_text(str(player))

        elif status.status is GameStatus.WEAPON_MENU:
            # Set options
            if not active_scene.menu.object.options:
                active_scene.menu.object.options = {
                    weapon.name: weapon
                    for weapon in player.weapons
                    if weapon is not None
                }
                active_scene.menu.object.options[
                    "Back"
                ] = GameStatus.BATTLE_MENU

        elif status.status is GameStatus.ITEM_MENU:
            # Set weapons.
            if not active_scene.menu.object.options:
                active_scene.menu.object.options = player.items
                active_scene.menu.object.options[
                    "Back"
                ] = GameStatus.BATTLE_MENU

        elif status.status is GameStatus.EXIT:
            playing = False

        if (active_scene := all_scenes.get(status.status, None)) is not None:
            screen.blit(active_scene.get_surface(status.status), (0, 0))
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
                        status.update(
                            new_option if new_option is not None else status.status
                        )
        # --

    # Clean up and say bye
    pygame.font.quit()
    pygame.quit()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()

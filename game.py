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

    status = GameStatus.TITLE_SCREEN

    playing = True
    while playing:
        active_scene = all_scenes.get(status, None)

        # Reset screen
        screen.fill(colors.RGB.WHITE)

        # This would be so nice with a switch case (match)
        # -- Game statuses
        if status is GameStatus.TITLE_SCREEN:
            # Nothing to do here that is not handled by scene
            pass

        # Start battle
        elif status is GameStatus.BATTLE_START:
            assert isinstance(active_scene, scenes.BattleScene), f"{status} scene is {type(active_scene)} " \
                                                                       f"not {type(scenes.BattleScene)}"
            # Pick enemy
            if active_scene.enemy.object is None:
                active_scene.enemy.object = choice(tuple(enemies.values()))

            active_scene.statics["info_box"].object.set_text(f"{all_scenes[status].enemy.object.name.capitalize()} challenges you!")

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
                if active_scene is not None and active_scene.menu.object is not None:
                    active_menu = active_scene.menu.object
                    if event.key == pygame.K_UP:
                        active_menu.update_option(-1)

                    elif event.key == pygame.K_DOWN:
                        active_menu.update_option(1)

                    # K_RETURN is enter key
                    elif event.key == pygame.K_RETURN:
                        # Update status
                        new_option = active_menu.get_option()
                        status = new_option if new_option is not None else status
        # --

    # Clean up and say bye
    pygame.font.quit()
    pygame.quit()
    print("Thanks for playing!")


if __name__ == "__main__":
    main()

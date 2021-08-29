#!/usr/bin/env python3
# Create scenes that can be rendered in the final game

# Local imports
import fonts
import colors
from game_objects import screen_size, GameStatus, Enemy, Menu, TextBox

# Global imports
from dataclasses import dataclass
from typing import Union
from os import path
from pygame.surface import Surface
from pygame import transform
from pygame import image


@dataclass
class Printable:
    object: Union[Menu, TextBox, Enemy]
    pos: tuple[int, int] = (0, 0)


@dataclass
class Scene:
    bg: Surface = None
    menu: Printable = None
    statics: list[Printable] = None

    def get_surface(self, *args, **kwargs) -> Surface:
        surface = Surface(screen_size())
        surface.fill(colors.RGB.WHITE)

        # Add the background
        if self.bg is not None:
            surface.blit(self.bg, (0, 0))

        # Put all the static objects first
        for static in self.statics:
            if static is not None:
                surface.blit(static.object.get_surface(), static.pos)

        # Then put the menu so that it's never covered
        if self.menu is not None:
            surface.blit(self.menu.object.get_surface(), self.menu.pos)

        return surface


class BattleScene(Scene):
    enemy: Printable
    healthbar: Printable = None

    def get_surface(self, status: GameStatus) -> Surface:
        """
        Same as Scene but with an enemy!
        :param status: Game status for sprite
        :return: surface
        """
        surface = super().get_surface()

        surface.blit(self.enemy.object, self.enemy.pos)

        # TODO: enemy method hp_changed. Only get healthbar if it has changed.
        #       Will reduce calls.
        # Update healthbar and draw.
        self.healthbar.object = self.enemy.object.get_healthbar()
        surface.blit(self.healthbar.pos, self.healthbar.pos)

        return surface


def resize_to_cover(image: Surface, size: tuple[int, int]) -> Surface:
    """
    Resizes a Surface so it the smallest side matches with the target size
    :param image: Pygame surface
    :param size: (x, y)
    :return: Same pygame surface, scaled.
    """
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
        (new_img_size[smallest] / img_size[smallest]) * img_size[not smallest]
    )

    return transform.scale(image, new_img_size)


def generate_scenes() -> dict[GameStatus, Scene]:
    """
    Create a scene object for all game statuses
    :return: Dict of game status to scene.
    """
    scenes = dict()
    display_size = display_width, display_height = screen_size()

    scenes[GameStatus.TITLE_SCREEN] = Scene(
        resize_to_cover(
            image.load(path.join("images", "titlescreen.png")), display_size
        ),
        Printable(
            Menu(
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
            ),
            (display_width // 20, display_height * 2 // 3)
        ),
        [
            Printable(
                TextBox(
                  "Dental Guardians",
                  fonts.TITLE,
                ),
                (display_width // 20, display_height // 2)
            )
        ]

    )

    return scenes

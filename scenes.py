#!/usr/bin/env python3
# Create scenes that can be rendered in the final game

# Local imports
from game_objects import *

# Global imports
from dataclasses import dataclass, field
from typing import Union
from pygame.surface import Surface
from pygame import transform


@dataclass
class Printable:
    object: Union[Menu, TextBox, Enemy]
    pos: tuple[int, int] = (0, 0)


@dataclass
class Scene:
    bg: Surface = None
    menu: Printable = None
    enemy: Printable = None
    statics: Union[list[Printable], None] = None

    def get_surface(self, *args, **kwargs) -> Surface:
        surface = Surface(screen_size())

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
    healthbar: Printable

    def get_surface(self, status) -> Surface:
        surface = super().get_surface()
        self.healthbar.object = self.enemy.object.get_healthbar()

        return


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
        (new_img_size[smallest] / img_size[smallest])
        * img_size[not smallest]
    )

    return transform.scale(image, new_img_size)


def generate_scenes() -> dict[GameStatus, Scene]:
    """
    Create a scene object for all game statuses
    :return: Dict of game status to scene.
    """
    scenes = dict()

    scenes[GameStatus.TITLE_SCREEN] = Scene(
        image_load
    )

    return scenes

#!/usr/bin/env python3
# Create scenes that can be rendered in the final game

# Local imports
import fonts
import colors
from game_objects import screen_size, GameStatus, Enemy, Menu, TextBox

# Global imports
from dataclasses import dataclass
from typing import Any, Union
from os import path
from pygame.surface import Surface
from pygame import transform
from pygame import image as image


@dataclass
class Printable:
    object: Union[Menu, TextBox, Enemy, None] = None
    pos: tuple[int, int] = (0, 0)


@dataclass
class Scene:
    bg: Union[Surface, None]
    menu: Printable
    statics: dict[Any, Printable]

    def get_surface(self, *args, **kwargs) -> Surface:
        surface = Surface(screen_size())
        surface.fill(colors.RGB.WHITE)

        # Add the background
        if self.bg is not None:
            surface.blit(self.bg, (0, 0))

        # Put all the static objects first
        for static in self.statics.values():
            if static.object is not None:
                surface.blit(static.object.get_surface(), static.pos)

        # Then put the menu so that it's never covered
        if self.menu.object is not None:
            surface.blit(self.menu.object.get_surface(), self.menu.pos)

        return surface


@dataclass
class BattleScene(Scene):
    enemy: Printable
    healthbar: Printable

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
        if self.enemy.object is not None:
            self.healthbar.object = self.enemy.object.get_healthbar()
            surface.blit(self.healthbar.object, self.healthbar.pos)

        return surface


def resize_to_cover(source: Surface, size: tuple[int, int]) -> Surface:
    """
    Resizes a Surface so it the smallest side matches with the target size
    :param source: Pygame surface
    :param size: (x, y)
    :return: Same pygame surface, scaled.
    """
    # Resize source to fit
    src_size = source.get_size()

    # Get index of smallest side
    smallest = 0 if src_size[0] < src_size[1] else 1

    # Fill with place holders
    new_src_size = [0, 0]

    # Make smallest size of target
    new_src_size[smallest] = size[smallest]

    # Not 1 -> 0, Not 0 -> 1. Yeah. Calculate new size using ratio
    new_src_size[not smallest] = round(
        (new_src_size[smallest] / src_size[smallest]) * src_size[not smallest]
    )

    return transform.scale(source, new_src_size)


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
        {"title_box":
            Printable(
                TextBox(
                  "Dental Guardians",
                  fonts.TITLE,
                ),
                (display_width // 20, display_height // 2)
            )
        }

    )

    # ----------------

    battle_start_box_size = (display_width * 2 // 3, display_height // 3)

    scenes[GameStatus.BATTLE_START] = BattleScene(
        resize_to_cover(image.load(path.join("images", "example_layout.png")), display_size),
        None,
        {
            "info_box": Printable(
                TextBox("placeholder",
                        fonts.DEFAULT,
                        battle_start_box_size
                        ),
                (
                    display_width - battle_start_box_size[0] - 20,
                    display_height - battle_start_box_size[1] - 10,
                )
            )
        }
    )
    return scenes

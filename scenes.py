#!/usr/bin/env python3
# Create scenes that can be rendered in the final game

# Local imports
from game_objects import *

# Global imports
from dataclasses import dataclass
from typing import Union
from pygame.surface import Surface


@dataclass
class Printable:
    object: Union[Menu, TextBox, Enemy]
    pos: tuple[int, int] = (0, 0)


@dataclass
class Scene:
    bg: Surface = None
    menu: Printable = None
    statics: Union[list[Printable], None] = None


def generate_scenes():
    ...

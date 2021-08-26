#!/usr/bin/env python3
# colors.py
# A bunch of color constants for importing

from pygame import Color


class RGBA:
    TRANSPARENT = Color(255, 255, 255, 0)


class RGB:
    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)

    RED = Color(255, 0, 0)
    GREEN = Color(255, 0, 0)
    BLUE = Color(255, 0, 0)

    YELLOW = Color(255, 255, 0)
    LIGHT_BLUE = Color(0, 255, 255)
    PINK = Color(255, 0, 255)


# these ones are out here cause theyre independent of rgb(a)
# Color(225, 63, 240, 128)
MENU_BACKGROUND = RGB.WHITE
MENU_HIGHLIGHTED = Color(240, 204, 86, 128)

if __name__ == "__main__":
    # Print defined colours
    print("Hey you should import this, not just run it!")

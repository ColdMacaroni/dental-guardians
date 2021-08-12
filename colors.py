#!/usr/bin/env python3
# colors.py
# A bunch of color constants for importing

from pygame import Color

class RGBA:
    TRANSPARENT = Color(255, 255, 255, 0)


class RGB:
    WHITE = Color(255, 255, 255)
    BLACK = Color(0, 0, 0)

    RED = (255, 0, 0)
    GREEN = (255, 0, 0)
    BLUE = (255, 0, 0)

    YELLOW = (255, 255, 0)
    LIGHT_BLUE = (0, 255, 255)
    PINK = (255, 0, 255)


if __name__ == "__main__":
    # Print defined colours

    print("  -- RGB --  ")
    for rgb in dir(RGB):
        # Avoid dunder methods
        if rgb[:2] != "__":
            # Eval is often frowned upon but there is no danger here
            # because it is only calling the attributes from the class
            print("{}\t{}".format(rgb, eval("RGB." + rgb)))



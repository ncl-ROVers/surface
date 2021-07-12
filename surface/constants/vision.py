"""
Computer vision constants.
"""
import numpy as np

# The height of result cut picture (when combining this is set to be default height, so it is easier to combine 5 faces)
MOSAIC_HEIGHT = 300

# The filter map for each color
COLOR_DICT = {"white": (np.array([0, 0, 50]), np.array([255, 255, 255])),
              "yellow": (np.array([15, 0, 0]), np.array([30, 255, 255])),
              "green": (np.array([60, 0, 0]), np.array([75, 255, 255])),
              "blue": (np.array([105, 0, 0]), np.array([120, 255, 255])),
              "purple": (np.array([145, 0, 0]), np.array([160, 255, 255])),
              "orange": (np.array([5, 0, 0]), np.array([15, 255, 255])),
              "red": (np.array([175, 0, 0]), np.array([190, 255, 255])),
              "pink": (np.array([160, 0, 0]), np.array([175, 255, 255])),
              "light_blue": (np.array([90, 0, 0]), np.array([105, 255, 255]))}

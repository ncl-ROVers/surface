"""
Computer vision constants.
"""
import numpy as _np

# The height of the cut picture
MOSAIC_HEIGHT = 300
# The filter map for each color
COLOR_DICT = {"white": (_np.array([0, 0, 50]), _np.array([255, 255, 255])),
               "yellow": (_np.array([15, 0, 0]), _np.array([30, 255, 255])),
               "green": (_np.array([60, 0, 0]), _np.array([75, 255, 255])),
               "blue": (_np.array([105, 0, 0]), _np.array([120, 255, 255])),
               "purple": (_np.array([145, 0, 0]), _np.array([160, 255, 255])),
               "orange": (_np.array([5, 0, 0]), _np.array([15, 255, 255])),
               "red": (_np.array([175, 0, 0]), _np.array([190, 255, 255])),
               "pink": (_np.array([160, 0, 0]), _np.array([175, 255, 255])),
               "light_blue": (_np.array([90, 0, 0]), _np.array([105, 255, 255]))}

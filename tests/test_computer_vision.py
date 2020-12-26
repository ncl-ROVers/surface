"""
Verify computer vision algorithms' performance and correctness.
"""
import os
import cv2
from surface.mussels import count_mussels


def test_final_result():
    """
    Test that the provided sample returns a correct result.
    """
    image = cv2.imread(os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets", "mussels_sample.png"))
    mussels_count, *_ = count_mussels(image)
    assert mussels_count == 8

"""
Implementation of the mussels counting task.
"""
from typing import Tuple
import cv2
import pandas
from pandas import DataFrame
import numpy as np
from numpy import ndarray
from sklearn.cluster import KMeans
from ..utils import logger


def _remove_circles(mask: np.ndarray) -> np.ndarray:
    """
    Remove the small circles (mussels) from the image.
    """
    contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)

    for _, contour in enumerate(contours):
        area = cv2.contourArea(contour)

        if area < 2000:
            cv2.drawContours(mask, [contour], 0, 0, -1)

    return mask


def _gaussian_blur_smooth(mask: np.ndarray) -> np.ndarray:
    """
    Convert the image to Canny Line with Gaussian blur.
    """
    # Erode the image
    kernel = np.ones((7, 7), np.uint8)
    mask = cv2.erode(mask, kernel, iterations=1)

    # Canny transform to get the edge of the image
    canny = cv2.Canny(mask, 20, 250)

    # Gaussian blur to smooth the edge to get the Hough line easier
    blurred = cv2.GaussianBlur(canny, (5, 5), 0)

    return blurred


def _get_edge_points(mask: np.ndarray) -> list:
    """
    Get the list of points on the edge of the square.
    """
    lines = cv2.HoughLinesP(mask, rho=0.1, theta=np.pi / 90, threshold=4, lines=4, minLineLength=200, maxLineGap=50)

    # Attach the points to a list
    lines = lines[:, 0, :]
    points = list()
    for x_1, y_1, x_2, y_2 in lines:
        points.append((x_1, y_1))
        points.append((x_2, y_2))

    return points


def _get_corner_points(points: list) -> np.ndarray:
    """
    Find the points on four edge by K-Means Cluster.
    """
    rect_points = DataFrame(points)
    rect_points = rect_points.rename(columns={0: "x", 1: "y"})

    # Use K-Means Cluster to classify different points (four corner points)
    points = KMeans(n_clusters=4).fit(rect_points)
    rect_points["label"] = points.labels_
    pandas.set_option("max_rows", 100)
    rect_points.sort_values("label")

    # Store different types of points
    edge_points = list()
    for i in range(4):
        df_all = _drop_noisy(rect_points[rect_points["label"] == i]).mean()
        edge_points.append((df_all.x, df_all.y))

    # Rearrange the order of points
    rect = np.array(edge_points, np.int32)
    rect = rect.reshape((-1, 1, 2))
    hull_rect = cv2.convexHull(rect)

    return hull_rect


def _drop_noisy(points: DataFrame) -> DataFrame:
    """
    Filter the outlier points in the data by delete the points lower than a certain area.
    """
    df_copy = points.copy()
    df_describe = df_copy.describe()
    for column in points.columns:
        mean = df_describe.loc["mean", column]
        std = df_describe.loc["std", column]
        minvalue = mean - 0.5 * std
        maxvalue = mean + 0.5 * std
        df_copy = df_copy[df_copy[column] >= minvalue]
        df_copy = df_copy[df_copy[column] <= maxvalue]

    return df_copy


def _find_mussels(image_greyscale: ndarray, mask: ndarray, hull_rect: ndarray) -> Tuple[int, ndarray]:
    """
    Find, count and draw the mussels.
    """
    # Find the circles in the image
    circles = cv2.HoughCircles(
        image_greyscale,
        method=cv2.HOUGH_GRADIENT,
        dp=1,
        minDist=20,
        param1=10,
        param2=8,
        minRadius=1,
        maxRadius=20
    )

    # Draw the circles on the image (and count the circles)
    num = 0
    for i in circles[0, :]:
        if cv2.pointPolygonTest(hull_rect, (int(i[0]), int(i[1])), measureDist=True) > (-int(i[2]) / 3):

            # Draw the outer circle, the center of the circle and increment the counter
            cv2.circle(mask, (int(i[0]), int(i[1])), int(i[2]), (0, 255, 0), 2)
            cv2.circle(mask, (int(i[0]), int(i[1])), 2, (0, 0, 255), 3)
            num += 1

    return num, mask


def count_mussels(image: np.ndarray) -> Tuple[int, ndarray, ndarray, ndarray, ndarray, ndarray]:
    """
    Count the number of the mussels in the given image.

    Additionally, returns the following images (ndarray-s):

        - Original image
        - Filtered with circles removed
        - Blurred and smoothed
        - Convex hull (4 corners)
        - Final image with found mussels marked
    """
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)

    # Set the range of the HSV field to create the mask
    lower = np.array([0, 0, 220])
    upper = np.array([255, 50, 255])
    grey = cv2.inRange(hsv, lower, upper)

    # Remove the mussels from the image
    circles_removed = _remove_circles(grey.copy())

    # Gaussian blur to smooth the edge to get the Hough line easier
    blurred_and_smoothed = _gaussian_blur_smooth(grey.copy())

    # Get the list of points on the edge of the square
    points = _get_edge_points(blurred_and_smoothed)

    # Find the points on four edges, using K-Means Cluster
    hull_rect = _get_corner_points(points)

    # Draw hull rect on the original image
    convex_hull: np.ndarray = image.copy()
    cv2.drawContours(convex_hull, [hull_rect], 0, (0, 0, 255), 3)

    # Find, count and draw the circles and square on the image
    mussels_count, mussels_found = _find_mussels(grey, image.copy(), hull_rect)
    logger.info(f"Counted {mussels_count} mussels in the passed image")

    return mussels_count, image, circles_removed, blurred_and_smoothed, convex_hull, mussels_found

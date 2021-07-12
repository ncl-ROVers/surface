"""
Coral reef task.

Module storing an implementation of the coral reef task.
"""
import cv2
import numpy as np
from ..constants.vision import RED, GREEN, BLUE, YELLOW


# Preprocessing part of the module
def align_photos(img_before: np.ndarray, img_now: np.ndarray, img_before_color: np.ndarray) -> np.ndarray:
    """
    Align photo from before and now to have the same perspective.

    :param img_before: image given as before converted into grayscale
    :param img_now: image taken now converted into grayscale
    :param img_before_color: original image given as before
    :return: transformed (aligned) image in color
    """
    # Create ORB detector with 5000 features
    # Find key points and descriptors. The first arg is the image, second arg is the mask, that is not required.
    kp1, first_descriptor = cv2.ORB_create(5000).detectAndCompute(img_before, None)
    kp2, second_descriptor = cv2.ORB_create(5000).detectAndCompute(img_now, None)

    # Match features between the two images. We create a Brute Force matcher with hamming distance as measurement mode.
    # Match the two sets of descriptors.
    matches = cv2.BFMatcher(cv2.NORM_HAMMING, crossCheck=True).match(first_descriptor, second_descriptor)

    # Sort matches on the basis of their Hamming distance.
    matches.sort(key=lambda x: x.distance)

    # Take the top 90 % matches forward.
    matches = matches[:int(len(matches) * 90)]

    # Define empty matrices of shape no_of_matches * 2.
    empty_first = np.zeros((len(matches), 2))
    empty_second = np.zeros((len(matches), 2))

    for idx, match in enumerate(matches):
        empty_first[idx, :] = kp1[match.queryIdx].pt
        empty_second[idx, :] = kp2[match.trainIdx].pt

    # Find the homography matrix.
    homography, _ = cv2.findHomography(empty_first, empty_second, cv2.RANSAC)

    # Use this matrix to transform the colored image wrt the reference image.
    transformed_img = cv2.warpPerspective(img_before_color, homography, (img_now.shape[1], img_now.shape[0]))

    return transformed_img


def get_white_masked_photo(img_bgr: np.ndarray) -> np.ndarray:
    """
    Get masked white parts of coral reef from the photo.

    :param img_bgr: Image as numpy array
    :return: Masked white parts of image
    """
    # Limits for white color used in inRange function
    lower_white = np.array([180, 180, 80])
    upper_white = np.array([255, 255, 255])

    # Kept bgr image for masking the photo
    mask = cv2.inRange(img_bgr, lower_white, upper_white)

    # Postprocessing of masked image, closing small holes inside the object
    kernel = np.ones((3, 3), np.uint8)
    closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=3)

    return closing


def get_pink_masked_photo(img_bgr: np.ndarray) -> np.ndarray:
    """
    Get masked pink parts of coral reef from the photo.

    :param img_bgr: Image as numpy array
    :return: Masked pink parts of image
    """
    # Limits for pink color used in inRange function
    lower_pink = np.array([100, 50, 130])
    upper_pink = np.array([240, 200, 230])

    # Used preprocessing with converting into hsv, because for pink colors it gives better results
    img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(img_hsv, lower_pink, upper_pink)

    # Postprocessing of masked image, closing small holes inside the object
    kernel = np.ones((3, 3), np.uint8)
    closing = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel=kernel, iterations=5)

    return closing


def find_contours(image_masked: np.ndarray) -> list:
    """
    Retrieve information (points, width and height) of specific changes and stores them in list.

    :param image_masked: Masked image
    :return: List of bounding boxes.
    """
    contours, _ = cv2.findContours(image_masked, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    array_of_bounding_boxes = []
    for contour in contours:
        area = cv2.contourArea(contour)
        area_min = 800
        area_max = 4000
        if area_min <= area <= area_max:
            (x_point, y_point, width, height) = cv2.boundingRect(contour)
            array_of_bounding_boxes.append((x_point, y_point, width, height))
    return array_of_bounding_boxes


# Main functionality and logic of the task
def draw_bounding_boxes(boxes: list, colour: tuple, image_now: np.ndarray) -> np.ndarray:
    """
    Draw bounding boxes on image.

    :param boxes: List of bounding boxes
    :param colour: Tuple of colour that is used to colour border of bounding box
    :param image_now: Image taken underwater
    :return: Image taken now with bounding boxes on it
    """
    for box in boxes:
        x_point = box[0]
        y_point = box[1]
        width = box[2]
        height = box[3]
        cv2.rectangle(image_now, (x_point, y_point), (x_point + width, y_point + height), colour, 2)
    return image_now


def get_bounding_boxes(recovery_mask: np.ndarray, growth_mask: np.ndarray,
                       death_mask: np.ndarray, bleaching_mask: np.ndarray, image_now: np.ndarray) -> np.ndarray:
    """
    Get any changes produced from image before and now.

    :param recovery_mask: Masked photo of recovery changes.
    :param growth_mask: Masked photo of growth changes.
    :param death_mask: Masked photo of death changes.
    :param bleaching_mask: Masked photo of bleaching changes.
    :param image_now:
    :return:
    """
    # Counter for keeping track of found changes, (only two types changes for image)
    counter = 0

    # Finding the bounding boxes for changes
    recovery_bounding_boxes = find_contours(recovery_mask)
    growth_bounding_boxes = find_contours(growth_mask)
    death_bounding_boxes = find_contours(death_mask)
    bleaching_bounding_boxes = find_contours(bleaching_mask)

    if recovery_bounding_boxes:
        counter += 1
        image_now = draw_bounding_boxes(recovery_bounding_boxes, BLUE, image_now)

    if growth_bounding_boxes:
        counter += 1
        image_now = draw_bounding_boxes(growth_bounding_boxes, GREEN, image_now)

    if death_bounding_boxes and counter < 2:
        counter += 1
        image_now = draw_bounding_boxes(death_bounding_boxes, YELLOW, image_now)

    if bleaching_bounding_boxes and counter < 2:
        counter += 1
        image_now = draw_bounding_boxes(bleaching_bounding_boxes, RED, image_now)
    return image_now


def determine_coral_reef_change() -> np.ndarray:
    """
    Process images and find the changes of the coral reef between two images.

    :return: Image with outlined changes
    """
    # Loading before and now images
    image_before = cv2.imread("photos/before.png")
    image_now = cv2.imread("photos/now.png")

    image_before = cv2.resize(image_before, (480, 360))
    image_now = cv2.resize(image_now, (480, 360))

    # Preprocessing images with bilateral filter to preserve edges
    image_before = cv2.bilateralFilter(image_before, 3, 75, 75)
    image_now = cv2.bilateralFilter(image_now, 3, 75, 75)

    # Converting images into grayscale
    gray_before = cv2.cvtColor(image_before, cv2.COLOR_BGR2GRAY)
    gray_now = cv2.cvtColor(image_now, cv2.COLOR_BGR2GRAY)

    transformed_image = align_photos(gray_before, gray_now, image_before)

    # Get masked white parts of image now and before (already aligned)
    img_masked_white = get_white_masked_photo(image_now)
    img_masked_white_before_aligned = get_white_masked_photo(transformed_image)

    # Get masked pink parts of image now and before (already aligned)
    pink_masked_now = get_pink_masked_photo(image_now)
    pink_masked_aligned = get_pink_masked_photo(transformed_image)

    # Get masked pink and white parts of before and now images
    pink_and_white_now = cv2.bitwise_or(img_masked_white, pink_masked_now)
    pink_and_white_before = cv2.bitwise_or(img_masked_white_before_aligned, pink_masked_aligned)

    # Recovery changes are when white parts from before become pink (BITWISE AND OPERATION)
    recovery_changes = cv2.bitwise_and(pink_masked_now, img_masked_white_before_aligned)

    # Bleaching changes are when pink parts from before become white (BITWISE AND OPERATION)
    bleaching_changes = cv2.bitwise_and(pink_masked_aligned, img_masked_white)

    # Growth changes are when there are only new pink parts that did not belong to before image and postprocessing
    growth_changes = pink_masked_now - pink_masked_aligned - recovery_changes + bleaching_changes
    growth_changes = cv2.morphologyEx(growth_changes, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8), 10)

    # Missing parts of coral reef and postprocessing
    death_changes = pink_and_white_before - pink_and_white_now
    death_changes = cv2.morphologyEx(death_changes, cv2.MORPH_OPEN, np.ones((7, 7), np.uint8), 10)

    return get_bounding_boxes(recovery_changes, growth_changes, death_changes, bleaching_changes, image_now)


if __name__ == "__main__":
    cv2.imshow("CHANGES", determine_coral_reef_change())
    cv2.waitKey(0)

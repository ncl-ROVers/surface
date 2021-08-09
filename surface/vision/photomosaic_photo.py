"""
Photomosaic.

Module storing an implementation of the cube photomosaic task.
"""

import typing
import cv2
import numpy as np
from ..constants.vision import MOSAIC_HEIGHT, COLOR_DICT
from ..utils import logger


def _filter_color(lower: np.ndarray, upper: np.ndarray, images: list) -> list:
    """
    Filter the color according to the threshold.

    :param lower: Lower threshold for filter
    :param upper: Upper threshold for filter
    :param images: List of HSV images
    :return: Masks after applying the filter
    """
    return [cv2.inRange(image_in_range, lower, upper) for image_in_range in images]


def _cut_images(images: list) -> list:
    """
    Cut the square in the images.

    :param images: list of images
    :return: the list of cut images
    """
    # Used for grabCut function, rectangle of points of predited foreground
    rect = (30, 30, 220, 220)

    img_white = list()
    # Iterating through the images and resizing them to preprocess the images with grabCut
    for idx in range(5):
        images[idx] = cv2.resize(images[idx], (256, 256))
        mask = np.zeros(images[idx].shape[:2], np.uint8)

        # Extract background and foreground images
        bgd_model = np.zeros((1, 65), np.float64)
        fgd_model = np.zeros((1, 65), np.float64)

        # grabCut extracts background from the image and gives foreground when combining masks
        cv2.grabCut(images[idx], mask, rect, bgd_model, fgd_model, 5, cv2.GC_INIT_WITH_RECT)
        mask2 = np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        img_white.append(images[idx] * mask2[:, :, np.newaxis])

    # List of found images is passed to the function that finds contours and biggest rectangle
    img_white = _find_rectangle(img_white)

    for index, image_to_resize in enumerate(img_white):
        img_white[index] = cv2.resize(image_to_resize, (int(image_to_resize.shape[0] / 2),
                                                        int(image_to_resize.shape[1] / 2)))

    return img_white


def _find_rectangle(images: list) -> list:
    """
    Use thresholding function to find face of the object.

    :param images: List of found sides of the object
    :return: Cut images with the biggest rectangle
    """
    for idx, image_to_find_rectangle in enumerate(images):
        # Preprocessing of the image with thresholding and dilation
        image_gray = cv2.cvtColor(image_to_find_rectangle, cv2.COLOR_BGR2GRAY)
        thresh = cv2.threshold(image_gray, 45, 255, cv2.THRESH_BINARY)[1]
        img_dilate = cv2.dilate(thresh, np.ones((5, 5)), iterations=1)

        # Preprocessed image is passed to get points of interest (points fo rectangle with width and height)
        _x, _y, _w, _h = _get_contours(img_dilate)

        # Slice the points of interest (face of the object from photo)
        images[idx] = images[idx][_y: _y + _h, _x:_x + _w]

    return images


def _get_contours(cut_image):
    """
    Add function to get the biggest contours of cut image. Function returns points of rectangle and lengths of sides.

    :param cut_image: masked images of sides
    :return: Points of the biggest rectangle in masked photo
    """
    contours, _ = cv2.findContours(cut_image, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    area_list = [[cv2.contourArea(cnt), cnt] for cnt in contours]
    biggest_contour_area = 0
    biggest_contour = 0
    for elem in area_list:
        if elem[0] > biggest_contour_area:
            biggest_contour_area = elem[0]
            biggest_contour = elem[1]
    peri = cv2.arcLength(biggest_contour, True)
    approx = cv2.approxPolyDP(biggest_contour, 0.02 * peri, True)
    x_point, y_point, width, height = cv2.boundingRect(approx)

    return x_point, y_point, width, height


def _resize_images(images: list) -> list:
    """
    Resize the images for combining.

    :param images: list of images
    :return: the resized cut images
    """
    index = 0
    for image_to_resize in images:
        # Dimensions of object = 120 cm long, 60 cm wide, and 60 cm tall
        # It is better to divide by height of the image than width
        width = int(image_to_resize.shape[0] * MOSAIC_HEIGHT / image_to_resize.shape[1])
        images[index] = cv2.resize(src=image_to_resize, dsize=(width, MOSAIC_HEIGHT))
        index += 1

    return images


def _type_division(dict_color_map: list) -> typing.Tuple[list, int]:
    """
    Divide the type of squares(upper and lower squares).

    Function assumes that first photo is taken of the top side's box.
    :param dict_color_map: the color map for squares
    :return: the index list of bottom squares, the index of top square
    """
    index = 1
    bottom_index = list()
    top_index = 0
    for _ in range(1, len(dict_color_map)):
        bottom_index.append(index)
        index += 1
    return bottom_index, top_index


def _combine_images(img_white: list, dict_color_map: list, bottom_index: list, top_index: int) -> np.ndarray:
    """
    Combine the squares to a image.

    :param img_white: the cut images
    :param dict_color_map: the color map for squares
    :param bottom_index: the index list of bottom squares
    :param top_index: the index of top square
    :return: the combined picture
    """
    left_img = img_white[bottom_index[0]]
    length_top = 0
    connect_color = _get_key(dict_color_map[bottom_index[0]], 1)
    for _ in range(3):
        for idx in range(3):
            img_index = idx + 1
            # Connect colors for side faces, color has to match with the next side
            if connect_color == _get_key(dict_color_map[bottom_index[img_index]], 3):
                left_img = np.concatenate((left_img, img_white[bottom_index[img_index]]), axis=1)
                connect_color = _get_key(dict_color_map[bottom_index[img_index]], 1)

                # Connect top side with the face and get the length of the top face to be matched
                if _get_key(dict_color_map[bottom_index[img_index]], 0) == _get_key(dict_color_map[top_index], 2):
                    length_top = left_img.shape[0] - img_white[bottom_index[img_index]].shape[0]

    # Get black background for matching photos
    canvas_top = np.ones((left_img.shape[0], left_img.shape[1], 3), dtype="uint8")
    canvas_top[:] = (0, 0, 0)

    # Get dimension to combine correctly top image with the bottom
    top_img = img_white[top_index]
    width_top = top_img.shape[0] + length_top
    height_top = top_img.shape[1] + MOSAIC_HEIGHT

    # Concatenate side faces with the black background and then add top face to correct position
    result = np.concatenate((canvas_top, left_img), axis=0)
    result[length_top: width_top, MOSAIC_HEIGHT:height_top] = top_img

    # Changed due to the width of result image that has to have 2 widths of smaller face and 2 widths of bigger face
    return result[:, :2 * img_white[1].shape[1] + 2 * img_white[2].shape[1]]


def _color_detect(images: list) -> list:
    """
    Detect the color in images.

    :param images: the list of images
    :return: the color map of squares
    """
    color_content = [{}, {}, {}, {}, {}]
    for color, value in COLOR_DICT.items():
        # Mask the images to get the colors we are interested in
        masks = _filter_color(value[0], value[1], images)

        for index_mask, mask in enumerate(masks):
            # Get contours of the masked image, focus on colors
            contours, _ = cv2.findContours(mask, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

            for _, contour in enumerate(contours):
                if cv2.contourArea(contour) > int(mask.shape[0] / 4):
                    moments = cv2.moments(contours[0])
                    if moments["m00"] != 0:
                        c_x = int(moments["m10"] / moments["m00"])
                        c_y = int(moments["m01"] / moments["m00"])
                    else:
                        c_x, c_y = 0, 0
                    horizontal = c_x / mask.shape[1]
                    vertical = c_y / mask.shape[0]
                    if color != "white":
                        check_for_color(horizontal, vertical, color_content, index_mask, color)

    return color_content


def check_for_color(horizontal, vertical, color_content, index_mask, color):
    """
    User helper function to check for color.
    """
    if (vertical < 0.2) & (horizontal < 0.7) & (horizontal > 0.3):
        color_content[index_mask][color] = 0
    elif (vertical > 0.8) & (horizontal < 0.7) & (horizontal > 0.3):
        color_content[index_mask][color] = 2
    elif (horizontal > 0.8) & (vertical < 0.7) & (vertical > 0.3):
        color_content[index_mask][color] = 1
    elif (horizontal < 0.2) & (vertical < 0.7) & (vertical > 0.3):
        color_content[index_mask][color] = 3
    else:
        logger.info("Error while trying to find the colour.")


def _get_key(dictionary: dict, value: int) -> list:
    """
    Get the key of dict() by value. Used for getting colours of object's faces to match.

    :param dictionary: the dict()
    :param value: the value of dict()
    :return: the key of dict()
    """
    return [l for l, v in dictionary.items() if v == value]


def helper_display(tag, image_helper):
    """
    Use helper function for images for displaying.
    """
    for index, name in enumerate(image_helper):
        cv2.imshow(tag + str(index), name)


def create_photomosaic(images: list) -> typing.Tuple[list, np.ndarray, list, list]:
    """
    Process the images and combine them by their color into a photomosaic.

    :param images: List of images in OpenCV format
    :return: Original images, Combined picture, the list of original pictures, the list of cut images
    """
    # Convert images to HSV color from a copy of the original images
    images_hsv = [cv2.cvtColor(_image, cv2.COLOR_BGR2HSV) for _image in images.copy()]
    # cut the useless part of the image
    img_cut = _cut_images(images_hsv)

    dict_color_map = _color_detect(img_cut[:1])

    # resize the images for combining
    img_white = _resize_images(img_cut)

    # divide the top and bottom image
    bottom_index, top_index = _type_division(dict_color_map)

    # combine the images
    result = _combine_images(img_white, dict_color_map, bottom_index, top_index)

    return images, cv2.cvtColor(result, cv2.COLOR_HSV2BGR), img, img_cut


if __name__ == "__main__":
    img = []
    # Added new dictionary of photos with different background and appropriate faces of object
    # PHOTOS MUST BE TAKEN IN CORRECT ORDER: TOP -> LEFT -> FRONT -> RIGHT -> BACK
    for i in range(5):
        # This line to be changed when we get the camera
        img.append(cv2.imread("./proper_samples/" + str(i + 1) + ".png"))

    _, result_img, image, image_cut = create_photomosaic(img.copy())

    cv2.imshow("result", cv2.resize(result_img, (0, 0), fx=0.5, fy=0.5))
    k = cv2.waitKey(0)
    if k == 27:  # wait for ESC key to exit
        cv2.destroyAllWindows()

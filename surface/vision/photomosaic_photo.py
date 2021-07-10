"""
Photomosaic
===========

Module storing an implementation of the cube photomosaic task.
"""
import typing as _typing
import cv2 as _cv2
import numpy as _np
from ..constants.vision import MOSAIC_HEIGHT, COLOR_DICT


def _filter_color(lower: _np.ndarray, upper: _np.ndarray, images: list) -> list:
    """
    Filter the color according to the threshold.

    :param lower: Lower threshold for filter
    :param upper: Upper threshold for filter
    :param images: List of HSV images
    :return: Masks after applying the filter
    """
    return [_cv2.inRange(image_in_range, lower, upper) for image_in_range in images]


def _cut_images(images: list) -> list:
    """
    Cut the square in the images

    :param images: list of images
    :return: the list of cut images
    """

    # Used for grabCut function
    rect = (30, 30, 220, 220)

    img_white = list()
    for idx in range(5):
        images[idx] = _cv2.resize(images[i], (256, 256))
        mask = _np.zeros(images[idx].shape[:2], _np.uint8)

        # Extract background and foreground images
        bgd_model = _np.zeros((1, 65), _np.float64)
        fgd_model = _np.zeros((1, 65), _np.float64)

        _cv2.grabCut(images[i], mask, rect, bgd_model, fgd_model, 5, _cv2.GC_INIT_WITH_RECT)
        mask2 = _np.where((mask == 2) | (mask == 0), 0, 1).astype('uint8')
        img_white.append(images[idx] * mask2[:, :, _np.newaxis])

    img_white = _find_rectangle(img_white)

    for index, image_to_resize in enumerate(img_white):
        img_white[index] = _cv2.resize(image_to_resize, (int(image_to_resize.shape[0] / 2),
                                                         int(image_to_resize.shape[1]/2)))
    print(len(img_white))

    return img_white


def _find_rectangle(images: list) -> list:
    """
    Function uses thresholding to find face of the object. Then it passes this masked image
    to function _get_contours
    :param images: List of found sides of the object
    :return: Cut images with the biggest rectangle
    """
    for idx, image_to_find_rectangle in enumerate(images):
        image_gray = _cv2.cvtColor(image_to_find_rectangle, _cv2.COLOR_BGR2GRAY)
        thresh = _cv2.threshold(image_gray, 45, 255, _cv2.THRESH_BINARY)[1]
        img_dilate = _cv2.dilate(thresh, _np.ones((5, 5)), iterations=1)
        _x, _y, _w, _h = _get_contours(img_dilate)
        images[idx] = images[idx][_y: _y + _h, _x:_x + _w]
    return images


def _get_contours(cut_image):
    """
    Function to get the biggest contours of cut image. After finding the biggest contour,
    function returns points of rectangle and lengths of sides.
    :param cut_image: masked images of sides
    :return: Points of the biggest rectangle in masked photo
    """
    contours, _ = _cv2.findContours(cut_image, _cv2.RETR_EXTERNAL, _cv2.CHAIN_APPROX_NONE)
    area_list = [[_cv2.contourArea(cnt), cnt] for cnt in contours]
    biggest_contour_area = 0
    biggest_contour = 0
    for elem in area_list:
        if elem[0] > biggest_contour_area:
            biggest_contour_area = elem[0]
            biggest_contour = elem[1]
    peri = _cv2.arcLength(biggest_contour, True)
    approx = _cv2.approxPolyDP(biggest_contour, 0.02 * peri, True)
    x_point, y_point, width, height = _cv2.boundingRect(approx)
    print(x_point, y_point, width, height)
    return x_point, y_point, width, height


def _resize_images(images: list) -> list:
    """
    resize the images for combining
    :param images: list of images
    :return: the resized cut images
    """
    index = 0
    for _img in images:
        # Dimensions of object = 120 cm long, 60 cm wide, and 60 cm tall
        # It is better to divide by height of the image than width
        width = int(_img.shape[0] * MOSAIC_HEIGHT / _img.shape[1])
        images[index] = _cv2.resize(src=_img, dsize=(width, MOSAIC_HEIGHT))
        index += 1

    return images


def _type_division(dict_color_map: list) -> \
        _typing.Tuple[list, int]:
    """
    divide the type of squares(upper and lower squares)
    Function assumes that first photo is taken of the top side's box
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


def _combine_images(img_white: list, dict_color_map: list, bottom_index: list, top_index: int) -> _np.ndarray:
    """
    combine the squares to a image
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
            if connect_color == _get_key(dict_color_map[bottom_index[img_index]], 3):
                left_img = _np.concatenate((left_img, img_white[bottom_index[img_index]]), axis=1)
                connect_color = _get_key(dict_color_map[bottom_index[img_index]], 1)
                if _get_key(dict_color_map[bottom_index[img_index]], 0) == _get_key(dict_color_map[top_index], 2):
                    length_top = left_img.shape[0] - img_white[bottom_index[img_index]].shape[0]

    canvas_top = _np.ones((left_img.shape[0], left_img.shape[1], 3), dtype="uint8")
    canvas_top[:] = (0, 0, 0)
    top_img = img_white[top_index]
    width_top = top_img.shape[0] + length_top
    height_top = top_img.shape[1] + MOSAIC_HEIGHT
    result = _np.concatenate((canvas_top, left_img), axis=0)
    result[length_top: width_top, MOSAIC_HEIGHT:height_top] = top_img
    # Changed due to the width of result image that has to have 2 widths of smaller face and 2 widths of bigger face
    return result[:, :2 * img_white[1].shape[1] + 2 * img_white[2].shape[1]]


def _color_detect(images: list) -> list:
    """
    detect the color in images
    :param images: the list of images
    :return: the color map of squares
    """
    color_content = [{}, {}, {}, {}, {}]
    for color, value in COLOR_DICT.items():
        masks = _filter_color(value[0], value[1], images)
        index_mask = 0
        for mask in masks:
            contours, _ = _cv2.findContours(mask, _cv2.RETR_TREE, _cv2.CHAIN_APPROX_SIMPLE)
            for _, contour in enumerate(contours):
                if _cv2.contourArea(contour) > int(mask.shape[0] / 4):
                    moments = _cv2.moments(contours[0])
                    if moments["m00"] != 0:
                        c_x = int(moments["m10"] / moments["m00"])
                        c_y = int(moments["m01"] / moments["m00"])
                    else:
                        c_x, c_y = 0, 0
                    horizontal = c_x / mask.shape[1]
                    vertical = c_y / mask.shape[0]
                    if color != "white":
                        check_for_color(horizontal, vertical, color_content, index_mask, color)
            index_mask += 1
    return color_content


def check_for_color(horizontal, vertical, color_content, index_mask, color):
    """
    Helper function to check for color
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
        print("error")


def _get_key(dictionary: dict, value: int) -> list:
    """
    get the key of dict() by value
    :param dictionary: the dict()
    :param value: the value of dict()
    :return: the key of dict()
    """
    return [l for l, v in dictionary.items() if v == value]


def helper_display(tag, image_helper):
    """
    Helper function for images for displaying
    """
    for index, name in enumerate(image_helper):
        _cv2.imshow(tag + str(index), name)


def create_photomosaic(images: list) -> _typing.Tuple[list, _np.ndarray, list, list]:
    """
    Process the images and combine them by their color into a photomosaic.
    :param images: List of images in OpenCV format
    :return: Original images, Combined picture, the list of original pictures, the list of cut images
    """
    # Convert images to HSV color from a copy of the original images
    images_hsv = [_cv2.cvtColor(_image, _cv2.COLOR_BGR2HSV) for _image in images.copy()]
    # cut the useless part of the image
    img_cut = _cut_images(images_hsv)

    dict_color_map = _color_detect(img_cut[:1])
    print(dict_color_map)
    # resize the images for combining
    img_white = _resize_images(img_cut)

    # divide the top and bottom image
    bottom_index, top_index = _type_division(dict_color_map)
    print("Image count", len(img_cut))
    print(bottom_index, top_index)

    # combine the images
    result = _combine_images(img_white, dict_color_map, bottom_index, top_index)

    return images, _cv2.cvtColor(result, _cv2.COLOR_HSV2BGR), img, img_cut


if __name__ == "__main__":
    img = []
    # Added new dictionary of photos with different background and appropriate faces of object
    # PHOTOS MUST BE TAKEN IN CORRECT ORDER: TOP -> LEFT -> FRONT -> RIGHT -> BACK
    for i in range(5):
        # This line to be changed when we get the camera
        img.append(_cv2.imread("./proper_samples/" + str(i + 1) + ".png"))
    print(len(img))
    _, result_img, image, image_cut = create_photomosaic(img.copy())

    _cv2.imshow("result", _cv2.resize(result_img, (0, 0), fx=0.5, fy=0.5))
    k = _cv2.waitKey(0)
    if k == 27:  # wait for ESC key to exit
        _cv2.destroyAllWindows()

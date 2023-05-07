import cv2
import numpy as np


def _cv2_findcontours(bin_img):
    """
    Helper function for OpenCV findContours.

    Reduces duplication of calls to findContours in the event the OpenCV function changes.

    Keyword inputs:
    bin_img = Binary image (np.ndarray)

    :param bin_img: np.ndarray
    :return contours: list
    :return hierarchy: np.array
    """
    contours, hierarchy = cv2.findContours(np.copy(bin_img), cv2.RETR_TREE, cv2.CHAIN_APPROX_NONE)[-2:]

    return contours, hierarchy


def _iterate_analysis(img, labeled_mask, n_labels, label, function, **kwargs):
    """Iterate over labels and apply an analysis function.
    Inputs:
    img      = image to be used for visualization
    mask     = labeled mask
    n_labels = number of expected labels
    label    = label parameter, modifies the variable name of observations recorded
    function = analysis function to apply to each submask
    kwargs   = additional keyword arguments to pass to the analysis function

    :param img: np.ndarray
    :param mask: np.ndarray
    :param n_labels: int
    :param label: str
    :param function: function
    :param kwargs: dict
    """
    mask_copy = np.copy(labeled_mask)
    if len(np.unique(mask_copy)) == 2 and np.max(mask_copy) == 255:
        mask_copy = np.where(mask_copy == 255, 1, 0).astype(np.uint8)
    for i in range(1, n_labels + 1):
        submask = np.where(mask_copy == i, 255, 0).astype(np.uint8)
        img = function(img=img, mask=submask, label=label, **kwargs)
    return img


def _object_composition(contours, hierarchy):
    """
    Groups objects into a single object, usually done after object filtering.

    Inputs:
    contours  = Contour tuple
    hierarchy = Contour hierarchy NumPy array

    Returns:
    group    = grouped contours list

    :param contours: tuple
    :param hierarchy: numpy.ndarray
    :return group: numpy.ndarray
    """
    stack = np.zeros((len(contours), 1))

    for c, cnt in enumerate(contours):
        if hierarchy[0][c][2] == -1 and hierarchy[0][c][3] > -1:
            stack[c] = 0
        else:
            stack[c] = 1

    ids = np.where(stack == 1)[0]
    group = np.array([], dtype=np.int32)
    if len(ids) > 0:
        contour_list = [contours[i] for i in ids]
        group = np.vstack(contour_list)

    return group


def _grayscale_to_rgb(img):
    """
    Convert a grayscale image to an RGB image.

    Inputs:
    img = Grayscale or RGB image data

    Returns:
    img = RGB image data

    :param img: np.ndarray
    :return img: np.ndarray
    """
    if len(np.shape(img)) == 2:
        img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)

    return img

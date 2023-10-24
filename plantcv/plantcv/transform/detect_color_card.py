"""Automatically detect color cards.

Algorithm written by mtwatso2-eng (github). Updated and implemented into PlantCV by Haley Schuhl.
"""
import os
import cv2
import math
import numpy as np
import pandas as pd
from plantcv.plantcv import params, outputs, fatal_error
from plantcv.plantcv._debug import _debug


def _is_square(contour):
    """Determine if a contour is square or not.

    Parameters
    ----------
    contour : list
        OpenCV contour.

    Returns
    -------
    bool
        True if the contour is square, False otherwise.
    """
    return (cv2.contourArea(contour) > 1000 and
            max(cv2.minAreaRect(contour)[1]) / min(cv2.minAreaRect(contour)[1]) < 1.27 and
            (cv2.contourArea(contour) / np.prod(cv2.minAreaRect(contour)[1])) > 0.8)


def detect_color_card(rgb_img, label=None, **kwargs):
    """Automatically detect a color card.

    Parameters
    ----------
    rgb_img : numpy.ndarray
        Input RGB image data containing a color card.
    label : str, optional
        modifies the variable name of observations recorded (default = pcv.params.sample_label).

    Returns
    -------
    numpy.ndarray
        Labeled mask of chips.
    """
    # Set lable to params.sample_label if None
    if label is None:
        label = params.sample_label

    radius = kwargs.get("radius", 20)
    threshold_type = kwargs.get("threshold_type", 1)
    threshold_value = kwargs.get("threshold_value", 51)

    # Hard code since we don't currently support other color cards
    nrows = 6
    ncols = 4

    # Convert to grayscale, threshold, and findContours
    imgray = cv2.cvtColor(rgb_img, cv2.COLOR_BGR2GRAY)
    gaussian = cv2.GaussianBlur(imgray, (11, 11), 0)
    thresh = cv2.adaptiveThreshold(gaussian, 255, threshold_type,
                                   cv2.THRESH_BINARY_INV, threshold_value, 2)
    contours, _ = cv2.findContours(thresh, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

    # Filter contours, keep only square-shaped ones
    filtered_contours = [contour for contour in contours if _is_square(contour)]
    # Calculate median area of square contours
    target_square_area = np.median([cv2.contourArea(cnt) for cnt in filtered_contours])
    # Filter contours again, keep only those within 20% of median area
    filtered_contours = [contour for contour in filtered_contours if
                         (0.8 < (cv2.contourArea(contour) / target_square_area) < 1.2)]

    # Throw a fatal error if no color card found
    if len(filtered_contours) == 0:
        fatal_error('No color card found')

    # Initialize chip shape lists
    mindex, marea, mwidth, mheight = [], [], [], []
    # Loop over our contours and size data about them
    for index, c in enumerate(filtered_contours):
        marea.append(cv2.contourArea(filtered_contours[index]))
        _, wh, _ = cv2.minAreaRect(c)  # Rotated rectangle
        mwidth.append(wh[0])
        mheight.append(wh[1])
        mindex.append(index)
    # Create dataframe for easy summary stats
    df = pd.DataFrame({'index': mindex, 'width': mwidth, 'height': mheight, 'area': marea})
    chip_size = df.loc[:, "area"].median()
    chip_height = df.loc[:, "height"].median()
    chip_width = df.loc[:, "width"].median()

    # Concatenate all contours into one array and find the minimum area rectangle
    rect = np.concatenate([[np.array(cv2.minAreaRect(i)[0]).astype(int)] for i in filtered_contours])
    rect = cv2.minAreaRect(rect)
    # Get the corners of the rectangle
    corners = np.array(np.intp(cv2.boxPoints(rect)))
    # Determine which corner most likely contains the white chip
    white_index = np.argmin([np.mean(math.dist(rgb_img[corner[1], corner[0], :], (255, 255, 255))) for corner in corners])
    corners = corners[np.argsort([math.dist(corner, corners[white_index]) for corner in corners])[[0, 1, 3, 2]]]
    # Increment amount is arbitrary, cell distances rescaled during perspective transform
    increment = 100
    centers = [[int(0 + i * increment), int(0 + j * increment)] for j in range(nrows) for i in range(ncols)]

    # Find the minimum area rectangle of the chip centers
    new_rect = cv2.minAreaRect(np.array(centers))
    # Get the corners of the rectangle
    box_points = cv2.boxPoints(new_rect).astype("float32")
    # Calculate the perspective transform matrix from the minimum area rectangle
    m_transform = cv2.getPerspectiveTransform(box_points, corners.astype("float32"))
    # Transform the chip centers using the perspective transform matrix
    new_centers = cv2.transform(np.array([centers]), m_transform)[0][:, 0:2]

    # Create blank img for drawing the labeled color card mask
    labeled_mask = np.zeros(imgray.shape)
    debug_img = np.copy(rgb_img)

    # Loop over the new chip centers and draw them on the RGB image and labeled mask
    for i, pt in enumerate(new_centers):
        cv2.circle(labeled_mask, new_centers[i], radius, (i + 1) * 10, -1)
        cv2.circle(debug_img, new_centers[i], radius, (255, 255, 0), -1)
        cv2.putText(debug_img, text=str(i), org=pt, fontScale=params.text_size, color=(0, 0, 0),
                    fontFace=cv2.FONT_HERSHEY_SIMPLEX, thickness=params.text_thickness)

    # Save out chip size for pixel to cm standardization
    outputs.add_observation(sample=label, variable='median_color_chip_size', trait='size of color card chips identified',
                            method='plantcv.plantcv.transform.detect_color_card', scale='square pixels',
                            datatype=float, value=chip_size, label="median")
    outputs.add_observation(sample=label, variable='median_color_chip_width', trait='width of color card chips identified',
                            method='plantcv.plantcv.transform.detect_color_card', scale='pixels',
                            datatype=float, value=chip_width, label="width")
    outputs.add_observation(sample=label, variable='median_color_chip_height', trait='height of color card chips identified',
                            method='plantcv.plantcv.transform.detect_color_card', scale='pixels',
                            datatype=float, value=chip_height, label="height")

    # Debugging
    _debug(visual=debug_img, filename=os.path.join(params.debug_outdir, f'{params.device}_color_card.png'))

    return labeled_mask

import cv2
import numpy as np
from scipy.spatial import distance as dist


def segment_card(image):
    thresh = threshold(image)
    contour = get_largest_contour(thresh)
    hull = cv2.convexHull(contour)
    corners = get_corners(hull)
    ordered_corners = order_points(corners)
    if len(ordered_corners) != 4:
        print("Card corners not found.")
        return None, None
    warped = warp(image, ordered_corners)
    shape_ratio = warped.shape[0] / warped.shape[1]
    has_card_shape = abs(shape_ratio - 1.393) < 0.40
    if has_card_shape:
        return warped, ordered_corners
    else:
        print(f"Card has bad ratio. Ratio value: {shape_ratio}")
        return None, None


def threshold(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    return thresh


def get_largest_contour(image):
    inverted = cv2.bitwise_not(image)
    kernel = np.ones((5, 5), np.uint8)
    dilation = cv2.dilate(inverted, kernel, iterations=2)
    contours, _ = cv2.findContours(dilation, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    return max(contours, key=cv2.contourArea)


def get_corners(hull):
    epsilon = 0.1 * cv2.arcLength(hull, True)
    approx = cv2.approxPolyDP(hull, epsilon, True)
    if len(approx) != 4:
        return []
    return approx.reshape((4, 2))


def order_points(pts):
    if len(pts) < 1:
        return []
    # sort the points based on their x-coordinates
    x_sorted = pts[np.argsort(pts[:, 0]), :]
    # grab the left-most and right-most points from the sorted
    # x-roodinate points
    leftmost = x_sorted[:2, :]
    rightmost = x_sorted[2:, :]
    # now, sort the left-most coordinates according to their
    # y-coordinates so we can grab the top-left and bottom-left
    # points, respectively
    leftmost = leftmost[np.argsort(leftmost[:, 1]), :]
    (tl, bl) = leftmost
    # now that we have the top-left coordinate, use it as an
    # anchor to calculate the Euclidean distance between the
    # top-left and right-most points; by the Pythagorean
    # theorem, the point with the largest distance will be
    # our bottom-right point
    D = dist.cdist(tl[np.newaxis], rightmost, "euclidean")[0]
    (br, tr) = rightmost[np.argsort(D)[::-1], :]
    # return the coordinates in top-left, top-right,
    # bottom-right, and bottom-left order
    return np.array([tl, tr, br, bl], dtype="float32")


def warp(image, corners):
    (tl, tr, br, bl) = corners[0], corners[1], corners[2], corners[3]
    width_a = np.sqrt(((br[0] - bl[0]) ** 2) + ((br[1] - bl[1]) ** 2))
    width_b = np.sqrt(((tr[0] - tl[0]) ** 2) + ((tr[1] - tl[1]) ** 2))
    # ...and now for the height of our new image
    height_a = np.sqrt(((tr[0] - br[0]) ** 2) + ((tr[1] - br[1]) ** 2))
    height_b = np.sqrt(((tl[0] - bl[0]) ** 2) + ((tl[1] - bl[1]) ** 2))
    # take the maximum of the width and height values to reach
    # our final dimensions
    max_width = max(int(width_a), int(width_b))
    max_weight = max(int(height_a), int(height_b))
    # construct our destination points which will be used to
    # map the screen to a top-down, "birds eye" view
    dst = np.array(
        [
            [0, 0],
            [max_width - 1, 0],
            [max_width - 1, max_weight - 1],
            [0, max_weight - 1],
        ],
        dtype="float32",
    )
    M = cv2.getPerspectiveTransform(np.array(corners), dst)
    return cv2.warpPerspective(image, M, (max_width, max_weight))
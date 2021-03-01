#!/usr/bin/python

import sys
import cv2
import numpy as np
from enum import Enum
from collections import deque
from segmentation import segment_card
from search import load_search_engine
import itertools


class State(Enum):
    UNSTABLE = 1
    SCANNING = 2
    DETECTED = 3
    FOUND = 4


def start_scanning(
    video_source="http://192.168.0.219:4747/mjpegfeed",
    engine_source="pkmn_vivid_voltage.pkl",
):
    cap = cv2.VideoCapture(video_source)
    _, frame = cap.read()
    height, width = frame.shape[:2]
    buffer = deque(
        [cv2.cvtColor(cap.read()[1].copy(), cv2.COLOR_BGR2GRAY) for _ in range(3)]
    )
    reference_frame = frame.copy()
    time_frame = 0
    state = State.UNSTABLE
    search_engine = load_search_engine(engine_source)
    prediction = np.zeros((480, 344, 3), dtype="uint8")
    while True:
        _, frame = cap.read()
        display_frame = frame.copy()
        display_frame = np.hstack((display_frame, prediction))
        if state == State.UNSTABLE:
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            diff = max(mse(gray, ft) for ft in buffer)
            is_stable = diff < 6
            state = State.SCANNING if is_stable else state
            buffer.append(gray)
            buffer.popleft()
        elif state == State.SCANNING:
            card, corners = segment_card(frame)
            if not card is None:
                state = state.DETECTED
                detected_frame = frame.copy()
                # cv2.imshow("card", card)
                frame = draw_bbox(display_frame, corners)
        elif state == State.DETECTED:
            best_result, dist = search_engine.search(card)
            if dist > 80:
                state = state.UNSTABLE
                prediction = np.zeros((480, 344, 3), dtype="uint8")
            else:
                print(best_result)
                prediction = cv2.imread(f"test_images/mtg_scraped/{best_result}")
                prediction = cv2.resize(prediction, (344, 480))
                print("prediction shape", prediction.shape)
                # cv2.imshow("predicted", predicted)
                state = State.FOUND
                frame = draw_bbox(display_frame, corners)
        elif state == State.FOUND:
            diff_from_detected_frame = mse(detected_frame, frame)
            is_stable = diff_from_detected_frame < 90
            # print(f"diff_from_detected_frame: {diff_from_detected_frame}")
            frame = draw_bbox(display_frame, corners)
            if not is_stable:
                # cv2.destroyWindow("card")
                state = State.UNSTABLE
        debug_text(display_frame, f"{state}", (15, 50))
        cv2.imshow("video", display_frame)
        # print(time_frame)
        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
        time_frame = time_frame + 1 if time_frame < 1000 else 0
    cap.release()
    cv2.destroyAllWindows()


def debug_text(frame, text, position):
    cv2.putText(
        frame,
        text,
        position,
        cv2.FONT_HERSHEY_SIMPLEX,
        1,
        (0, 255, 255),
        2,
        cv2.LINE_4,
    )


def mse(img1, img2):
    """
    Mean squared error of two given images measuring the images similarity.
    """
    err = np.sum((img1.astype("float") - img2.astype("float")) ** 2)
    err /= float(img1.shape[0] * img2.shape[1])
    return err


def draw_bbox(frame, corners):
    for i in range(len(corners)):
        x0, y0 = corners[i][0], corners[i][1]
        x1, y1 = corners[(i + 1) % 4][0], corners[(i + 1) % 4][1]
        cv2.line(frame, (x0, y0), (x1, y1), (0, 255, 0), 2)
    return frame


if __name__ == "__main__":
    start_scanning(engine_source="model.pkl")
# detect_lines.py
import cv2
import sys
import numpy as np
from typing import Tuple, List
import argparse

# Preprocessing: blur, threshold, Canny
def preprocess(gray: np.ndarray,
               blur_ksize: int = 5,
               canny_lo: int = 80,
               canny_hi: int = 200) -> Tuple[np.ndarray, np.ndarray]:
    blur = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    edges = cv2.Canny(binary, canny_lo, canny_hi, apertureSize=3)
    return binary, edges

# Cartesian features: length, angle, slope
def cart_features(p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[float, float, float]:
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy_cart = y1 - y2
    angle_cart = np.degrees(np.arctan2(dy_cart, dx))
    slope_cart = np.inf if dx == 0 else dy_cart / dx
    length = float(np.hypot(dx, y2 - y1))
    return length, angle_cart, slope_cart


# Cartesian features: length, angle, slope
def cart_features(p1: Tuple[int, int], p2: Tuple[int, int]) -> Tuple[float, float, float]:
    x1, y1 = p1
    x2, y2 = p2
    dx = x2 - x1
    dy_cart = y1 - y2
    angle_cart = np.degrees(np.arctan2(dy_cart, dx))
    slope_cart = np.inf if dx == 0 else dy_cart / dx
    length = float(np.hypot(dx, y2 - y1))
    return length, angle_cart, slope_cart

# Run detection: find and draw lines i and o based on criteria
def run_detection(image_path: str, debug: bool = True) -> None:
    img = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        print(f"Errore: impossibile caricare '{image_path}'")
        return

    _, edges = preprocess(img)
    raw = cv2.HoughLinesP(edges, 1, np.pi/180, 25,
                          minLineLength=30, maxLineGap=8)

    candidates = []  # (x1,y1,x2,y2, slope, my, mx)
    if raw is not None:
        for x1, y1, x2, y2 in raw[:,0]:
            _, _, slope = cart_features((x1, y1), (x2, y2))
            if slope > 0:
                mx = (x1 + x2) // 2
                my = (y1 + y2) // 2
                candidates.append((x1, y1, x2, y2, slope, my, mx))

    if len(candidates) < 2:
        print("Non ci sono abbastanza segmenti inclinati per formare una coppia.")
        return

    # Normalization factors
    m_vals = [c[4] for c in candidates]
    m_max = max(m_vals)
    H = img.shape[0]

    # Scoring parameters
    alpha = beta = gamma = delta = 1.0

    best_score = float('inf')
    best_pair = None
    # consider all pairs o,i with i to the right of o
    for o in candidates:
        for i in candidates:
            if i[6] <= o[6]:
                continue
            m_o, y_o = o[4], o[5]
            m_i, y_i = i[4], i[5]
            score = (alpha*(m_o/m_max)
                     + beta*(y_o/H)
                     + gamma*(1 - m_i/m_max)
                     + delta*(y_i/H))
            if score < best_score:
                best_score = score
                best_pair = (o, i)

    if best_pair is None:
        print("Nessuna coppia valida trovata.")
        return
    o_seg, i_seg = best_pair

    canvas = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
    # Draw o in yellow
    x1, y1, x2, y2 = o_seg[:4]
    cv2.line(canvas, (x1, y1), (x2, y2), (0, 255, 255), 2)
    # Draw i in blue
    x1, y1, x2, y2 = i_seg[:4]
    cv2.line(canvas, (x1, y1), (x2, y2), (255, 0, 0), 2)

    if debug:
        cv2.imshow('Best o (yellow) and i (blue)', canvas)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    cv2.imwrite('best_o_i.png', canvas)
    print(f"Miglior coppia trovata: o midpoint=({o_seg[6]},{o_seg[5]}), i midpoint=({i_seg[6]},{i_seg[5]})")
    print(f"Score = {best_score:.4f}. Overlay salvato in 'best_o_i.png'.")
# Unit tests
def test_cart_features():
    l, a, s = cart_features((0, 0), (1, -1))
    assert abs(a - 45.0) < 1e-6
    assert abs(s - 1.0) < 1e-6

def test_preprocess():
    img = np.zeros((50, 50), dtype=np.uint8)
    cv2.line(img, (5, 10), (45, 10), 255, 1)
    binary, edges = preprocess(img)
    assert binary.shape == img.shape and edges.shape == img.shape
    assert edges.max() > 0

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Ricerca retta i e o')
    parser.add_argument('image', nargs='?', default='/mnt/data/frame.jpg')
    parser.add_argument('--no-debug', action='store_true')
    parser.add_argument('--test', action='store_true')
    args = parser.parse_args()
    if args.test:
        test_cart_features(); test_preprocess(); print('Tests passati'); sys.exit(0)
    run_detection(args.image, debug=not args.no_debug)

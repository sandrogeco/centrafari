import cv2
import sys
import numpy as np
from typing import Tuple
from scipy.optimize import curve_fit

# 1. Preprocessing: blur + Otsu + Canny
def preprocess(gray: np.ndarray,
               blur_ksize: int = 5,
               canny_lo: int = 40,
               canny_hi: int = 120) -> np.ndarray:
    blur = cv2.GaussianBlur(gray, (blur_ksize, blur_ksize), 0)
    _, binary = cv2.threshold(blur, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
    edges = cv2.Canny(binary, canny_lo, canny_hi, apertureSize=3)
    return edges

# 2. Extract contour points
def extract_contour_points(edges: np.ndarray) -> np.ndarray:
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if not contours:
        raise ValueError("No contours found")
    largest = max(contours, key=cv2.contourArea)
    pts = np.squeeze(largest)
    return pts.astype(float)

# 3. Two-line model for curve_fit
def two_lines(x: np.ndarray,
              X0: float, Y0: float,
              mo: float, mi: float) -> np.ndarray:
    y = np.where(x <= X0,
                 Y0 + mo * (x - X0),
                 Y0 + mi * (x - X0))
    # Dynamic visualization of current fit line
    try:
        global gray, x_data, y_data
        canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        h, w = gray.shape
        # endpoints
        y_left = int(round(Y0 + mo * (0 - X0)))
        y_right = int(round(Y0 + mi * (w - X0)))
        cv2.line(canvas, (0, y_left), (w, y_right), (0, 255, 0), 1)
        cv2.imshow('Fitting...', canvas)
        cv2.waitKey(1)
    except Exception:
        pass
    return y

# 4. Main fit routine
def fit_lines(image_path: str,
              blur_ksize: int = 5,
              canny_lo: int = 40,
              canny_hi: int = 120,
              ftol: float = 1e-8,
              xtol: float = 1e-8,
              maxfev: int = 1000,
              debug: bool = True) -> None:
    global gray, x_data, y_data
    gray = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)
    if gray is None:
        print(f"Errore: impossibile caricare '{image_path}'")
        return

    edges = preprocess(gray, blur_ksize, canny_lo, canny_hi)
    pts = extract_contour_points(edges)
    # split contour by vertical margins
    x_min, x_max = np.min(pts[:,0]), np.max(pts[:,0])
    margin_frac = 0.1  # 10% margin on each side
    margin = (x_max - x_min) * margin_frac
    left_bound = x_min + margin
    right_bound = x_max - margin
    # central segment between vertical cuts
    mask_mid = (pts[:,0] >= left_bound) & (pts[:,0] <= right_bound)
    pts_mid = pts[mask_mid]
    pts_mid = pts_mid[np.lexsort((pts_mid[:, 1], pts_mid[:, 0]))] #founf leftest upper y
    # split into top and bottom pieces by median y
    y_med = pts_mid[0][1]
    top_pts = pts_mid[pts_mid[:,1] <= y_med]
    bot_pts = pts_mid[pts_mid[:,1] >  y_med]
    # draw both pieces
    canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    for x,y in top_pts.astype(int): cv2.circle(canvas,(x,y),1,(255,0,255),-1)
    for x,y in bot_pts.astype(int): cv2.circle(canvas,(x,y),1,(0,255,0),-1)
    if debug:
        cv2.imshow('Contour split', canvas)
        cv2.waitKey(0)
        cv2.destroyAllWindows()
    # keep only top for fitting
    pts = top_pts
    x_data = pts[:, 0]
    y_data = pts[:, 1]
    y_data = pts[:, 1]
    x_data = pts[:, 0]
    y_data = pts[:, 1]

    p0 = [np.median(x_data), np.min(y_data), 0.1, 1.0]
    # Ensure X0 within data range; Y0 must be above contour (<= min y_data)
    bounds = (
        [np.min(x_data), 0.0,          0.0, 0.0],
        [np.max(x_data), np.min(y_data), np.inf, np.inf]
    )

    popt, _ = curve_fit(
        two_lines, x_data, y_data,
        p0=p0, bounds=bounds,
        ftol=ftol, xtol=xtol, maxfev=maxfev
    )
    X0, Y0, mo, mi = popt

    # draw fitted lines extended
    h, w = gray.shape
    canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
    ctrs, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
    if ctrs:
        largest = max(ctrs, key=cv2.contourArea)
        cv2.drawContours(canvas, [largest], -1, (0,0,255), 1)
    xs = np.array([0, X0, w])
    ys_o = Y0 + mo * (xs - X0)
    ys_i = Y0 + mi * (xs - X0)
    cv2.line(canvas, (0, int(round(ys_o[0]))), (int(round(X0)), int(round(Y0))), (0,255,255), 2)
    cv2.line(canvas, (int(round(X0)), int(round(Y0))), (w, int(round(ys_i[2]))), (255,0,0), 2)
    cv2.circle(canvas, (int(round(X0)), int(round(Y0))), 5, (0,255,0), -1)

    if debug:
        cv2.imshow('Fit two lines', canvas)
        cv2.waitKey(0)
        cv2.destroyAllWindows()

    cv2.imwrite('fit_lines_result.png', canvas)
    print(f"Fit completed: X0={X0:.2f}, Y0={Y0:.2f}, mo={mo:.4f}, mi={mi:.4f}")

if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser(description='Fit two lines to contour')
    parser.add_argument('image', help='Path to grayscale image')
    parser.add_argument('--blur', type=int, default=5)
    parser.add_argument('--canny-lo', type=int, default=40)
    parser.add_argument('--canny-hi', type=int, default=120)
    parser.add_argument('--ftol', type=float, default=1e-8, help='ftol for curve_fit')
    parser.add_argument('--xtol', type=float, default=1e-8, help='xtol for curve_fit')
    parser.add_argument('--maxfev', type=int, default=1000, help='maxfev for curve_fit')
    parser.add_argument('--no-debug', action='store_true')
    args = parser.parse_args()
    fit_lines(
        args.image,
        blur_ksize=args.blur,
        canny_lo=args.canny_lo,
        canny_hi=args.canny_hi,
        ftol=args.ftol,
        xtol=args.xtol,
        maxfev=args.maxfev,
        debug=not args.no_debug
    )

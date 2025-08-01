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
    binary[0:5,:]=0
    binary[-5:, :] = 0
    binary[:, 0:5] = 0
    binary[:, -5:] = 0
    edges = cv2.Canny(binary, canny_lo, canny_hi, apertureSize=3)

    return edges,binary

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
    if (mi>mo): #y up =0!!
        return np.full_like(x,1e6)
    y = np.where(x <= X0,
                 Y0 + mo * (x - X0),
                 Y0 + mi * (x - X0))
    # Dynamic visualization of current fit line

    try:
        pippo
        global gray, x_data, y_data
        canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        h, w = gray.shape
        print('x:',X0,' y:',Y0,' mo:',mo,' mi:',mi)
        # endpoints
        y_left = int(round(Y0 + mo * (0 - X0)))
        y_right = int(round(Y0 + mi * (w - X0)))
        y_o=Y0+mo*(-X0)
        y_i=Y0+mi*(w-X0)
        #cv2.line(canvas, (0, y_left), (w, y_right), (0, 255, 0), 1)
        cv2.line(canvas, (0, int(round(y_o))), (int(round(X0)), int(round(Y0))), (0, 255, 255), 1)
        cv2.line(canvas, (int(round(X0)), int(round(Y0))), (w, int(round(y_i))), (255, 0, 0), 1)
        cv2.imshow('Fitting...', canvas)
        cv2.waitKey(0)
    except Exception:
        pass
    return y

def tre_lines(x: np.ndarray,
              X0: float, Y0: float,X1:float,Y1:float,
              m0: float, m1: float,m2:float) -> np.ndarray:
    if (X1<X0)or(m1>m0):
        return np.full_like(x,1e6)

    print(X0, ' ', Y0, ' ', X1, ' ', Y1, ' ', m0, ' ', m1, ' ', m2)
    y = np.where(
        x <= X0,
        Y0 + m0 * (x - X0),  # tratto 1
        np.where(
            x <= X1,
            (Y0 + m0 * (X1 - X0)) + m1 * (x - X1),  # tratto 2
            # tratto 3: continua da Y a X1
            (Y0 + m0 * (X1 - X0)) + m1 * (X1 - X1) + m2 * (x - X1)
        )
    )
    # Dynamic visualization of current fit line

    try:
        pippo
        global gray, x_data, y_data
        canvas = cv2.cvtColor(gray, cv2.COLOR_GRAY2BGR)
        h, w = gray.shape
        print('x:',X0,' y:',Y0,' mo:',mo,' mi:',mi)
        # endpoints
        y_left = int(round(Y0 + mo * (0 - X0)))
        y_right = int(round(Y0 + mi * (w - X0)))
        y_o=Y0+mo*(-X0)
        y_i=Y0+mi*(w-X0)
        #cv2.line(canvas, (0, y_left), (w, y_right), (0, 255, 0), 1)
        cv2.line(canvas, (0, int(round(y_o))), (int(round(X0)), int(round(Y0))), (0, 255, 255), 1)
        cv2.line(canvas, (int(round(X0)), int(round(Y0))), (w, int(round(y_i))), (255, 0, 0), 1)
        cv2.imshow('Fitting...', canvas)
        cv2.waitKey(0)
    except Exception:
        pass
    return y

# 4. Main fit routine
def fit_lines(image_input,image_output,cache,
              blur_ksize: int = 5,
              canny_lo: int = 40,
              canny_hi: int = 120,
              ftol: float = 1e-8,
              xtol: float = 1e-8,
              maxfev: int = 1000,
              debug: bool = False) -> None:
    global gray, x_data, y_data
   # image_input = cv2.imread(image_path, cv2.IMREAD_GRAYSCALE)


    edges,binary = preprocess(image_input, blur_ksize, canny_lo, canny_hi)
    #image_output[edges>0]=(255,0,0)
    try:
        pts = extract_contour_points(edges)
        # split contour by vertical margins

        margin_frac = 0.05  # 1% margin on each side
        leftset_upper=pts[np.lexsort((pts[:, 1], pts[:, 0]))]
        rightest_upper=pts[np.lexsort((pts[:, 0], pts[:, 1]))]
        y_h=leftset_upper[0][1]
        x_min=leftset_upper[0][0]
        x_max=rightest_upper[0][0]
        margin = (x_max - x_min) * margin_frac
        try:
            marginl=cache['margin_auto']
        except:
            marginl=0
            cache['margin_auto']=0
            cache['s_err']=np.Inf

        if cache['autoexp']:
            marginl=0
            cache['margin_auto']=0
            cache['s_err']=np.Inf

        left_bound = x_min + marginl
        right_bound = x_max - marginl

        mask = (pts[:,0] >= left_bound) & (pts[:,0] <= right_bound)
        pts_mask= pts[mask]

        top_pts = pts_mask[pts_mask[:,1] <= y_h]
        bot_pts = pts_mask[pts_mask[:,1] >  y_h]
        # draw both pieces
       # canvas = cv2.cvtColor(image_input, cv2.COLOR_GRAY2BGR)
#        for x,y in top_pts.astype(int): cv2.circle(image_output,(x,y),1,(255,0,255),-1)
#        for x,y in bot_pts.astype(int): cv2.circle(image_output,(x,y),1,(0,255,0),-1)
        if debug:
            cv2.imshow('Contour split', image_output)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        # keep only top for fitting
        pts = top_pts
        x_data = pts[:, 0]
        y_data = pts[:, 1]




        p0 = [np.mean(x_data), np.max(y_data)-1, -0.01, -1.0]
        # Ensure X0 within data range; Y0 must be above contour (<= min y_data)
        bounds = (
            [np.min(x_data), 0.0,-0.05,-np.Inf],
            [np.max(x_data), np.max(y_data), 0,0]
        )

        popt, _ = curve_fit(
            two_lines, x_data, y_data,
            p0=p0, bounds=bounds,
            ftol=ftol, xtol=xtol, maxfev=maxfev
        )
        X0, Y0, mo, mi= popt
        s=np.sum((y_data - two_lines(x_data, X0, Y0, mo, mi)) ** 2) / len(x_data)
        if (np.abs(s-cache['s_err'])/s>0.025)and((right_bound-left_bound)>(x_max-x_min)*0.75):
            cache['margin_auto']=marginl+2
            cache['s_err']=s
        msg="old "+str(cache['s_err']*1.05)+" new "+str(s)+" margin "+str(marginl)
        cv2.putText(image_output, msg, (5, 100), cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.5, (0,255,0), 1)


        h, w = image_input.shape
        xs = np.array([0, X0,w])
        ys=two_lines(xs,X0,Y0,mo,mi)
        cv2.line(image_output, (int(round(xs[0])), int(round(ys[0]))), (int(round(xs[1])), int(round(ys[1]))), (0,255,0), 1)
        cv2.line(image_output, (int(round(xs[1])), int(round(ys[1]))), (int(round(xs[2])), int(round(ys[2]))), (0, 255, 0), 1)
        cv2.circle(image_output,(int(round(X0)),int(round(Y0))),2,(0,255,0),2,-1)
        [cv2.circle(image_output, (int(p[0]),int(p[1])), 1, (255, 0, 0), 1, -1) for p in top_pts]
        #cv2.line(image_output, (int(round(xs[2])), int(round(ys[2]))), (int(round(xs[3])), int(round(ys[3]))), (0, 0, 255), 1)





        [cv2.circle(image_output,(e[0],e[1]),1,(255,0,0),-1) for e in edges]
        ctrs, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)
        if ctrs:
            largest = max(ctrs, key=cv2.contourArea)
            cv2.drawContours(image_output, [largest], -1, (0,0,255), 1)
        if debug:
            cv2.imshow('Fit two lines', image_output)
            cv2.waitKey(0)
            cv2.destroyAllWindows()
       # image_output=canvas
       # cv2.imwrite('fit_lines_result.png', canvas)
    except:
        X0=0
        Y0=0
    return image_output,(X0,Y0)
    #print(f"Fit completed: X0={X0:.2f}, Y0={Y0:.2f}, mo={mo:.4f}, mi={mi:.4f}")

if False:#__name__ == '__main__':
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
    #fit lines(image, 5,40,120,1e-8,1e-8,1000)
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

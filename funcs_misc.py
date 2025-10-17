import cv2

from utils import disegna_pallino, disegna_croce


def preprocess(image, cache):
    config = cache['config']

    if 'crop_w' not in config or 'crop_h' not in config:
        return image

    height, width = image.shape[:2]
    #image=image[-cache['config']['height']:,:]
    # Ritaglia immagine
    crop_center = config.get('crop_center', [width/2, height/2])
    crop_w = config['crop_w']
    crop_h = config['crop_h']
    start_y = max(int(crop_center[1] - crop_h / 2), 0)
    end_y = int(start_y + crop_h)
    start_x = max(int(crop_center[0] - crop_w / 2), 0)
    end_x = int(start_x + crop_w)
    image = image[start_y: end_y, :]
    image_o=image.copy()*0
    image_o[start_y : end_y, start_x : end_x] = image[start_y : end_y, start_x : end_x]
    image=cv2.convertScaleAbs(image, alpha=1.0, beta=20)


    # Stira immagine
    #image = cv2.resize(image, (0, 0), fx=1.0 * config['width'] / config['crop_w'], fy=1.0 * config['height'] / config['crop_h'])

    return image_o,image


def is_punto_ok(point, cache):
    stato_comunicazione = cache['stato_comunicazione']
    width = cache["config"]["width"]
    height = cache["config"]["height"]
    toh = stato_comunicazione.get('TOH', 50)
    tov = stato_comunicazione.get('TOV', 50)
    inclinazione = stato_comunicazione.get('inclinazione', 0)

    is_punto_centrato = (width / 2 - toh) <= point[0] <= (width / 2 + toh) \
        and (height / 2 - tov + inclinazione) <= point[1] <= (height / 2 + tov + inclinazione)

    return is_punto_centrato
    #disegna_pallino(image_output, point, 10, 'green' if is_punto_centrato else 'red', 1)


def visualizza_croce_riferimento(frame, x, y, width, heigth):
    disegna_croce(frame, (x - width / 2, y - heigth / 2), 1000, 1, 'green')
    disegna_croce(frame, (x + width / 2, y + heigth / 2), 1000, 1, 'green')

def point_in_rect(pt, rect):
    x, y = pt
    rx, ry, rw, rh = rect
    return (rx <= x <= rx + rw) and (ry <= y <= ry + rh)

import cv2
import numpy as np

def blur_and_sharpen(img, sigma=1.5, strength=0.8, eight_neighbors=False):
    """
    Anti-alias 'morbido' via GaussianBlur + sharpen con filter2D.

    :param img: immagine BGR/GRAY (uint8 o float32/float64)
    :param sigma: intensità blur gaussiano (1.0–3.0 tipico)
    :param strength: forza sharpen (0.3–1.2; più alto = più nitido)
    :param eight_neighbors: False => kernel 'a croce' (4-neighbors), True => 8-neighbors
    :return: immagine filtrata, stesso dtype dell'input
    """
    # Lavoro in float [0,1] per stabilità
    src_dtype = img.dtype
    x = img.astype(np.float32)
    if x.max() > 1.5:  # probabilmente uint8
        x /= 255.0

    # 1) BLUR (anti-alias / smoothing)
    x_blur = cv2.GaussianBlur(x, (0, 0), sigmaX=sigma, sigmaY=sigma)

    # 2) SHARPEN con filter2D
    a = float(strength)

    if not eight_neighbors:
        # kernel 'a croce' (4-neighbors): [[0,-a,0],[-a,1+4a,-a],[0,-a,0]]
        k = np.array([[0, -a, 0],
                      [-a, 1 + 4 * a, -a],
                      [0, -a, 0]], dtype=np.float32)
    else:
        # kernel 8-neighbors: tutti intorno pesati -a, centro 1+8a (più aggressivo)
        k = np.full((3, 3), -a, np.float32)
        k[1, 1] = 1 + 8 * a

    x_sharp = cv2.filter2D(x_blur, ddepth=-1, kernel=k, borderType=cv2.BORDER_REPLICATE)

    # clamp e ritorno al dtype originale
    x_sharp = np.clip(x_sharp, 0.0, 1.0)
    if src_dtype == np.uint8:
        x_sharp = (x_sharp * 255.0 + 0.5).astype(np.uint8)
    else:
        x_sharp = x_sharp.astype(src_dtype)

    return x_sharp
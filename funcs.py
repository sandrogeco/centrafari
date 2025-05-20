import numpy as np
import cv2
import logging

from utils import get_colore_bgr, angolo_vettori, find_y_by_x, angolo_esterno_vettori, differenza_vettori, disegna_croce

def preprocess(image, cache):
    config = cache['config']

    if 'crop_w' not in config or 'crop_h' not in config:
        return image

    height, width = image.shape[:2]

    # Ritaglia immagine
    crop_w = config['crop_w']
    crop_h = config['crop_h']
    image = image[int(height/2 - crop_h/2):int(height/2 + crop_h/2), int(width/2 - crop_w/2):int(width/2 + crop_w/2)]

    # Stira immagine
    image = cv2.resize(image, (0, 0), fx=1.0 * config['width'] / config['crop_w'], fy=1.0 * config['height'] / config['crop_h'])

    return image

def rileva_contorno(image, cache):
    if 'lut' not in cache:
        def pullapart(v):
            vs = 250
            v = v - 2 * np.sign(v - vs) * (np.abs(v - vs) ** 0.6)
            v = np.clip(v, 0, 255).astype(np.uint8)
            return v

        cache['lut'] = np.array([pullapart(d) for d in range(256)], dtype=np.uint8)

    image1 = cv2.LUT(image, cache['lut'])

    # Sembra che THRESH_OTSU funzioni abbastanza meglio di THRESH_BINARY, cioe' il contorno che viene
    # fuori e' meno influenzato dalla haze nell'immagine e piu' vicino al bordo vero
    _, binary_image = cv2.threshold(image1, 0, 255, cv2.THRESH_OTSU)

    edges = cv2.Canny(binary_image, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        logging.debug("   contours vuoto")
        return None, '[rileva_contorno_1], contours vuoto'

    contour = max(contours, key=lambda d: cv2.arcLength(d, False))
    contour = contour[contour[:, 0, 0].argsort()]
    return contour, None

def rileva_punto_angoloso(image_input, image_output, cache=None):
    WIDTH_PIXEL = image_input.shape[1]

    # Rileva contorno
    contour, err = rileva_contorno(image_input, cache)
    if contour is None or err is not None:
        return image_input, None,'[rileva_punto_angoloso] contour is None'

    # Analisi contorno
    if cache['DEBUG']:
        cv2.drawContours(image_output, [contour], -1, get_colore_bgr('red'), 1)

    delta = 20
    punti = []

    OFFSET_Y = 5

    for p in range(delta, 100 - delta, 1):
        p_prec = p - delta
        p_succ = p + delta

        x_prec = int(0.01 * p_prec * WIDTH_PIXEL)
        x = int(0.01 * p * WIDTH_PIXEL)
        x_succ = int(0.01 * p_succ * WIDTH_PIXEL)

        y_prec = find_y_by_x(contour, x_prec)
        y = find_y_by_x(contour, x)
        y_succ = find_y_by_x(contour, x_succ)
        if y_prec is None or y is None or y_succ is None:
            continue

        v_prec = (x_prec, y_prec + OFFSET_Y)
        v = (x, y + OFFSET_Y)
        v_succ = (x_succ, y_succ + OFFSET_Y)

        angolo = -angolo_esterno_vettori(differenza_vettori(v_prec, v), differenza_vettori(v_succ, v))

        v_prec_verso_alto = angolo_vettori((1, 0), differenza_vettori(v_prec, v)) > 0

        if 12 < angolo < 18 and v_prec_verso_alto:
            punti.append(v)
            # cv2.circle(image_output, v, 2, get_colore_bgr('green'), -1)
            # Decommenta queste due o tre linee sotto per visualizzare i vettori che danno l'angolo e per scrivere l'angolo
            # cv2.line(image_output, v_prec, v, get_colore_bgr('green'), 1)
            # cv2.line(image_output, v, v_succ, get_colore_bgr('green'), 1)
            # cv2.putText(image_output, f'{int(angolo)}', somma_vettori(v, (10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 1, get_colore_bgr('green'), 1)

    # Rimuovo i punti che sono troppo vicini alle estremita' del contour
    min_contour_x = np.min(contour[:, 0, 0])
    max_contour_x = np.max(contour[:, 0, 0])
    range_contour_x = max_contour_x - min_contour_x
    punti = [p for p in punti if min_contour_x + (0.05 * range_contour_x) < p[0] < max_contour_x - (0.05 * range_contour_x)]

    if len(punti) == 0:
        return image_output, None, '[rileva_punto_angoloso] nessun punto trovato'

    for punto in punti:
        cv2.circle(image_output, punto, 2, get_colore_bgr('green'), -1)

    punto_finale = tuple(np.median(punti, axis=0).astype(np.int32))

    if 'numero_medie_punto' in cache['config']:
        cache['lista_ultimi_punti'] = cache.get('lista_ultimi_punti', []) + [punto_finale]
        cache['lista_ultimi_punti'] = cache['lista_ultimi_punti'][-cache['config']['numero_medie_punto']:]
        punto_finale = tuple(np.median(cache['lista_ultimi_punti'], axis=0).astype(np.int32))

    cv2.circle(image_output, punto_finale, 10, get_colore_bgr('green'), -1)

    return image_output, punto_finale, None


def draw_point(image_output,point,cache):
    stato_comunicazione=cache['stato_comunicazione']

    if (cache['config']['width']/2-stato_comunicazione.get('TOH', 50))<point[0]:
        if point[0]<(cache['config']['width']/2+stato_comunicazione.get('TOH', 50)):
            if (cache['config']['height']/2-stato_comunicazione.get('TOV', 50) + stato_comunicazione.get('inclinazione', 0))<point[1]:
                if point[1]< (cache['config']['height']/2+ stato_comunicazione.get('TOV', 50)+ stato_comunicazione.get('inclinazione', 0)):
                    cv2.circle(image_output, point, 10, get_colore_bgr('green'), -1)
                    return

    cv2.circle(image_output, point, 10, get_colore_bgr('red'), -1)


def visualizza_croce_riferimento(frame, x, y, width, heigth):
    disegna_croce(frame, (x - width / 2, y - heigth / 2), 1000, 1, 'green')
    disegna_croce(frame, (x + width / 2, y + heigth / 2), 1000, 1, 'green')

import cv2

from utils import disegna_pallino, disegna_croce


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


def disegna_punto(image_output, point, cache):
    stato_comunicazione = cache['stato_comunicazione']
    width = cache["config"]["width"]
    height = cache["config"]["height"]
    toh = stato_comunicazione.get('TOH', 50)
    tov = stato_comunicazione.get('TOV', 50)
    inclinazione = stato_comunicazione.get('inclinazione', 0)

    is_punto_centrato = (width / 2 - toh) <= point[0] <= (width / 2 + toh) \
        and (height / 2 - tov + inclinazione) <= point[1] <= (height / 2 + tov + inclinazione)

    disegna_pallino(image_output, point, 10, 'green' if is_punto_centrato else 'red', -1)


def visualizza_croce_riferimento(frame, x, y, width, heigth):
    disegna_croce(frame, (x - width / 2, y - heigth / 2), 1000, 1, 'green')
    disegna_croce(frame, (x + width / 2, y + heigth / 2), 1000, 1, 'green')

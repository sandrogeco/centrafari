import sys
import cv2
import json

from funcs_misc import preprocess
from funcs_anabbagliante import rileva_punto_angoloso


if __name__ == "__main__":
    tipo_faro = sys.argv[1]
    path_image = sys.argv[2]

    # Carica la configurazione
    with open(f"config_{tipo_faro}.json", "r") as f:
        config = json.load(f)

    cache = {
        "DEBUG": True,
        "config": config,
    }

    image_input = cv2.imread(path_image)

    image_input = cv2.cvtColor(image_input, cv2.COLOR_BGR2GRAY)
    image_input = preprocess(image_input, cache)

    image_output = cv2.cvtColor(image_input.copy(), cv2.COLOR_GRAY2BGR)
    image_output, point, _ = rileva_punto_angoloso(image_input, image_output, cache)

    cv2.imwrite(path_image.replace(".jpg", "_OUT.jpg"), image_output)

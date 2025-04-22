import os
import cv2
import numpy as np
import subprocess

#region Funzioni

WHITE = (255, 255, 255)[::-1]
BLACK = (0, 0, 0)[::-1]
RED = (255, 0, 0)[::-1]
GREEN = (0, 255, 0)[::-1]
BLUE = (0, 0, 255)[::-1]

def find_y_by_x(contour, x):
    c = contour[:, 0, :]
    nearest_point = min(c, key=lambda p: abs(p[0] - x))
    return nearest_point[1]

def somma_vettori(v1, v2):
    return (v1[0] + v2[0], v1[1] + v2[1])

def differenza_vettori(v1, v2):
    return (v1[0] - v2[0], v1[1] - v2[1])

def angolo_vettori(v1, v2):
    x1, y1 = v1
    x2, y2 = v2

    dot = x1 * x2 + y1 * y2
    det = x1 * y2 - y1 * x2
    return np.arctan2(det, dot) * 180 / np.pi

def angolo_esterno_vettori(v1, v2):
    return angolo_vettori(differenza_vettori((0, 0), v1), v2)

#endregion

def rileva_contorno_semplice(image):
    # Su molte immagini questa funzione non riesce a trovare dei contorni validi e quindi
    # non si trova neanche il punto angoloso. Funziona molto meglio rileva_contorno_1
    _, binary_image = cv2.threshold(image, 128, 255, cv2.THRESH_BINARY)
    edges = cv2.Canny(binary_image, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("   contours vuoto")
        return None, '[rileva_contorno_semplice] contours vuoto'

    return max(contours, key=cv2.contourArea), None

def rileva_contorno_1(image):
    NUM_RIGHE = 20
    luminosita_prime_righe = np.min(image[0:NUM_RIGHE])
    luminosita_ultime_righe = np.max(image[-NUM_RIGHE:-1])

    soglia = (luminosita_prime_righe + luminosita_ultime_righe) / 2
    print(f"luminosita prima riga: {luminosita_prime_righe}, luminosita ultima riga: {luminosita_ultime_righe}, soglia: {soglia}")

    # Sembra che THRESH_OTSU funzioni abbastanza meglio di THRESH_BINARY, cioe' il contorno che viene
    # # fuori e' meno influenzato dalla haze nell'immagine e piu' vicino al bordo vero
    _, binary_image = cv2.threshold(image, soglia, 255, cv2.THRESH_OTSU)

    edges = cv2.Canny(binary_image, 50, 150)
    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        print("   contours vuoto")
        return None, '[rileva_contorno_1], contours vuoto'

    # return max(contours, key=cv2.contourArea), None
    return max(contours, key=lambda d: cv2.arcLength(d, False)), None

def rileva_punto_angoloso(image_input, image_output):
    WIDTH_PIXEL = image_input.shape[1]

    # Rileva contorno
    contour, err = rileva_contorno_1(image_input)
    if contour is None or err is not None:
        return image_output, '[rileva_punto_angoloso] contour is None'

    # Analisi contorno
    cv2.drawContours(image_output, [contour], -1, RED, 1)

    delta = 20
    punti = []

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

        v_prec = (x_prec, y_prec)
        v = (x, y)
        v_succ = (x_succ, y_succ)

        angolo = -angolo_esterno_vettori(differenza_vettori(v_prec, v), differenza_vettori(v_succ, v))

        v_prec_verso_alto = angolo_vettori((1, 0), differenza_vettori(v_prec, v)) > 0

        if angolo > 0 and 5 < angolo < 20 and v_prec_verso_alto:
            punti.append(v)
            # cv2.circle(image_output, v, 2, GREEN, -1)
            # Decommenta queste due o tre linee sotto per visualizzare i vettori che danno l'angolo e per scrivere l'angolo
            # cv2.line(image_output, v_prec, v, GREEN, 1)
            # cv2.line(image_output, v, v_succ, GREEN, 1)
            # cv2.putText(image_output, f'{int(angolo)}', somma_vettori(v, (10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN, 4)

    # Rimuovo i punti che sono troppo vicini alle estremita' del contour
    min_contour_x = np.min(contour[:, 0, 0])
    max_contour_x = np.max(contour[:, 0, 0])
    range_contour_x = max_contour_x - min_contour_x
    punti = [p for p in punti if min_contour_x + (0.05 * range_contour_x) < p[0] < max_contour_x - (0.05 * range_contour_x)]

    if len(punti) == 0:
        return image_output, '[rileva_punto_angoloso] nessun punto trovato'

    for punto in punti:
        cv2.circle(image_output, punto, 2, GREEN, -1)

    punto_finale = tuple(np.median(punti, axis=0).astype(np.int32))
    cv2.circle(image_output, punto_finale, 6, GREEN, -1)

    return image_output, None

if __name__ == "__main__":
    # Genera lista immagini da analizzare --------------------------------------
    lista_immagini: list = []

    # Tutte le immagini
    if True:
        path_root_out = "/tmp/OUT"
        subprocess.check_output(f"rm -rf {path_root_out}/*", shell=True)
        # for path_root in ["/tmp/faro_alogeno_anabbagliante", "/tmp/faro_xenon_anabbagliante", "/tmp/faro_xenon_abbagliante"]:
        for path_root in ["/tmp/faro_xenon_anabbagliante"]:
            if not os.path.exists(path_root):
                continue
            # for situazione in ['faro_alogeno_anabbagliante_12volt_0incl_centrato_pellicola45']:
            for situazione in os.listdir(path_root):
                path_folder = os.path.join(path_root, situazione)
                path_folder_out = os.path.join(path_root_out, path_root.split('/')[-1], situazione)
                os.makedirs(path_folder_out, exist_ok=True)
                for filename_image in os.listdir(path_folder):
                    lista_immagini.append({
                        'path_image': os.path.join(path_folder, filename_image),
                        'path_image_out': os.path.join(path_folder_out, filename_image),
                    })

    # Immagini particolari scelte a mano di casi patologici che devono essere corretti
    # In questo modo si possono fare modifiche e valutare subito se questi casi migliorano e quando
    # sono migliorati se ci sono regressioni
    if True:
        path_root_out = "/tmp/OUT2"
        subprocess.check_output(f"rm -rf {path_root_out}/*", shell=True)

        lista_immagini.append({
            'path_image': '/tmp/faro_alogeno_anabbagliante/faro_alogeno_anabbagliante_12volt_0incl_centrato_pellicola45/bri_64_contr_75_expabs_250.jpg',
            'path_image_out': '/tmp/OUT2/CONTOUR_TROPPO_DISTANTE_faro_alogeno_anabbagliante__12volt_0incl_centrato_pellicola45__bri_64_contr_75_expabs_250.jpg'
        })
        lista_immagini.append({
            'path_image': '/tmp/faro_alogeno_anabbagliante/faro_alogeno_anabbagliante_12volt_2incl_centrato_pellicola45/bri_32_contr_0_expabs_300.jpg',
            'path_image_out': '/tmp/OUT2/CONTOUR_TROPPO_DISTANTE__faro_alogeno_anabbagliante_12volt_2incl_centrato_pellicola45__bri_32_contr_0_expabs_300.jpg'
        })
        lista_immagini.append({
            'path_image': '/tmp/faro_alogeno_anabbagliante/faro_alogeno_anabbagliante_12volt_2incl_centrato_pellicola45/bri_64_contr_0_expabs_300.jpg',
            'path_image_out': '/tmp/OUT2/PUNTI_ERRATI__faro_alogeno_anabbagliante_12volt_2incl_centrato_pellicola45__bri_64_contr_0_expabs_300.jpg'
        })
        lista_immagini.append({
            'path_image': '/tmp/faro_alogeno_anabbagliante/faro_alogeno_anabbagliante_12volt_2incl_centrato_pellicola45/bri_-64_contr_100_expabs_2000.jpg',
            'path_image_out': '/tmp/OUT2/NESSUN_PUNTO_TROVATO__faro_alogeno_anabbagliante_12volt_2incl_centrato_pellicola45__bri_-64_contr_100_expabs_2000.jpg'
        })

    # Analizza le immagini -----------------------------------------------------

    for c, immagine in enumerate(lista_immagini):
        path_image = immagine['path_image']
        print(f"*** [{c}] Processando {path_image} ...")

        image_input = cv2.imread(path_image, cv2.IMREAD_GRAYSCALE)
        if image_input is None:
            print(f"*** [{c}] Immagine {path_image} non trovata")
            continue
        image_output = cv2.cvtColor(image_input.copy(), cv2.COLOR_GRAY2BGR)

        image_output, err = rileva_punto_angoloso(image_input, image_output)
        assert image_output is not None

        if err is not None:
            cv2.putText(image_output, err, (5, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, WHITE, 1)

        path_image_out = immagine['path_image_out']
        os.makedirs(os.path.dirname(path_image_out), exist_ok=True)
        cv2.imwrite(path_image_out, image_output)

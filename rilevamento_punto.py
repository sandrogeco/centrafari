import os
import cv2
import numpy as np
import subprocess
from matplotlib import  pyplot as plt
import matplotlib as mpl

mpl.use('tkagg')
#region Funzioni

WHITE = (255, 255, 255)[::-1]
BLACK = (0, 0, 0)[::-1]
RED = (255, 0, 0)[::-1]
GREEN = (0, 255, 0)[::-1]
BLUE = (0, 0, 255)[::-1]
MCORR=np.array([[1.19962087e+00, 3.03070135e-01, -6.59806746e+01],
           [5.05979992e-03, 1.64790684e+00, -7.66065165e+01],
           [-1.08610130e-04, 1.09172033e-03, 1.00000000e+00]])

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

    delta = 5
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
        #secondo me c'è un errore
        v_prec_verso_alto = angolo_vettori((1, 0), differenza_vettori(v_prec, v)) > 0

        if angolo > 0 and 5 < angolo < 20 and v_prec_verso_alto:
            punti.append(v)
            cv2.circle(image_output, v, 2, GREEN, -1)
        # Decommenta queste due o tre linee sotto per visualizzare i vettori che danno l'angolo e per scrivere l'angolo
            cv2.line(image_output, v_prec, v, GREEN, 1)
            cv2.line(image_output, v, v_succ, GREEN, 1)
            cv2.putText(image_output, f'{int(angolo)}', somma_vettori(v, (10, 10)), cv2.FONT_HERSHEY_SIMPLEX, 1, GREEN, 4)

    # Rimuovo i punti che sono troppo vicini alle estremita' del contour
    min_contour_x = np.min(contour[:, 0, 0])
    max_contour_x = np.max(contour[:, 0, 0])
    range_contour_x = max_contour_x - min_contour_x
    punti = [p for p in punti if min_contour_x + (0.05 * range_contour_x) < p[0] < max_contour_x - (0.05 * range_contour_x)]

    if len(punti) == 0:
        return image_output, (0,0),'[rileva_punto_angoloso] nessun punto trovato'

    for punto in punti:
        cv2.circle(image_output, punto, 2, GREEN, -1)

    punto_finale = tuple(np.median(punti, axis=0).astype(np.int32))
    cv2.circle(image_output, punto_finale, 6, GREEN, -1)

    return image_output,punto_finale, None


def dspl(x,image,cl=False):
    cv2.imshow(x, image)
    cv2.waitKey(0)
    if cl:
        cv2.destroyAllWindows()

def trova_contrni_abbagliante(image_input):
    WIDTH_PIXEL = image_input.shape[1]
    AREA=image_input.shape[0]*image_input.shape[1]
    LEVEL=0.9
    imout =image_input.copy()

    imout= cv2.warpPerspective(imout, MCORR, (imout.shape[1],imout.shape[0]))

    cv2.fastNlMeansDenoising(imout, imout, 1000)
    cv2.normalize(imout,imout,0,255,cv2.NORM_MINMAX)


    imout1=imout.copy()
    #imout2=imout.copy()
    c=np.cumsum(np.histogram(imout1.reshape(AREA),bins=255)[0])/AREA
    l=np.where(c>LEVEL)[0][0]
    imout1[imout<l]=0
    nup=np.sum([imout1>0])

    x = np.arange(imout1.shape[1])
    y = np.arange(imout1.shape[0])
    xx, yy = np.meshgrid(x, y)

    A = imout1.sum()

    x_cms = (np.int32)((xx * imout1).sum() / A)
    y_cms = (np.int32)((yy * imout1).sum() / A)

    print(x_cms, y_cms)

    imout=cv2.cvtColor(imout, cv2.COLOR_GRAY2BGR)

    try:
        edges = cv2.Canny(imout1, 50, 150)
        contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        contour=max(contours, key=lambda d: cv2.contourArea(d))
        lux = lum_zones(imout, x_cms, y_cms,50)
        cv2.drawContours(imout, [contour], -1, RED, 1)
        cv2.circle(imout, (x_cms, y_cms), 6, GREEN, -1)
        cv2.putText(imout, 'aut-level ' + str(l) + ' num pixel brighter ' + str(nup), (5, 20),
                    cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, WHITE, 1)
        cv2.putText(imout, 'x:' + str(x_cms) + ' y:' + str(y_cms), (5, 40), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, WHITE, 1)
        cv2.putText(imout, 'LUM:' + str(lux) , (5, 60), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, WHITE, 1)

    except:
        print('err')



    return imout, None


def lum_zones(img_input,x,y,r):
    img=img_input.copy()*0
    cv2.circle(img,[x,y],r,[1,1,1],-1)
    img=img*img_input
    l=np.mean(img[img>0])
    cv2.circle(img_input, [x, y], r, GREEN)
    return l


def correzione_prospettiva(img):
    src_pts = np.float32([
        [205, 144],  # in alto a sinistra
        [423, 141],  # in alto a destra
        [453, 356],  # in basso a destra
        [189, 366]  # in basso a sinistra
    ])

    width=((src_pts[2][0]-src_pts[3][0])+(src_pts[1][0]-src_pts[0][0]))/2
    xm=(src_pts[0][0]+src_pts[3][0])/2
    ym = (src_pts[0][1] + src_pts[1][1]) / 2
    height=width
   # width, height = 500, 700  # cambia in base al tuo caso

    dst_pts = np.float32([
        [xm, ym],
        [xm+width - 1, ym],
        [xm+width - 1, ym+height - 1],
        [xm, ym+height - 1]
    ])

    M = cv2.getPerspectiveTransform(src_pts, dst_pts)

    warped = cv2.warpPerspective(img, M, np.int32((width, height)))

    return warped




test='ana'
if __name__ == "__main__":
    if test=='PI':

        cap = cv2.VideoCapture(0)
        ret, frame = cap.read()

        if not ret:
            print("Failed to grab frame")
        else:
            # Save the image
            cv2.imwrite("/tmp/capture.jpg", frame)
            image_input = cv2.imread("/tmp/capture.jpg", cv2.IMREAD_GRAYSCALE)
            image_output = cv2.cvtColor(image_input, cv2.COLOR_GRAY2BGR)
            image_output, err = trova_contrni_abbagliante(image_output)


    if test=='ana':
        # Release the camera

      #  path_image='faro_xenon_abbagliante/faro_xenon_abbagliante_centrato_pellicola45/bri_0_contr_0_expabs_50.jpg'
        path_image = 'faro_xenon_anabbagliante/faro_xenon_anabbagliante_centrato_pellicola45/bri_0_contr_0_expabs_500.jpg'
        image_input = cv2.imread(path_image, cv2.IMREAD_GRAYSCALE)
        image_output = cv2.cvtColor(image_input.copy(), cv2.COLOR_GRAY2BGR)
        image_output,pt, err = rileva_punto_angoloso(image_input, image_output)
        lux1=lum_zones(image_output,pt[0]+100,pt[1]+100,80)
        lux2 = lum_zones(image_output, pt[0]-200, pt[1]+100, 80)
        cv2.putText(image_output, 'LUM:' + str(lux1)+" "+str(lux2), (5, 20), cv2.FONT_HERSHEY_COMPLEX_SMALL, 1, WHITE, 1)


    if test == 'abb':
        # Release the camera

        path_image = 'faro_xenon_abbagliante/faro_xenon_abbagliante_centrato_pellicola45/bri_0_contr_0_expabs_50.jpg'
        image_input = cv2.imread(path_image, cv2.IMREAD_GRAYSCALE)
        image_output = cv2.cvtColor(image_input.copy(), cv2.COLOR_GRAY2BGR)
        # image_output, err = rileva_punto_angoloso(image_input, image_output)
        image_output, err = trova_contrni_abbagliante(image_input)

    dspl('x',image_output,True)
    print('h')



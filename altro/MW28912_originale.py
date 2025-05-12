"""
//        ³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³
//        ³                                                           ³
//        ³                                                           ³
//        ³ - autore      : Enrico Molinari                           ³
//        ³ - data        : 08/11/2022                                ³
//        ³ - revisione   : 1.0                                       ³
//        ³ - descrizione : Centrafari-P10Linux                       ³
//        ³               :                                           ³
//        ³               :                                           ³
//        ³               :                                           ³
//        ³               :                                           ³
//        ³               :                                           ³
//        ³  Codice SW    : MW289-12                                  ³
//        ³               :                                           ³
//        ³  Hardware     : Raspberry con monitor 10 pollici (P10L)   ³
//        ³               :                                           ³
//        ³                                                           ³
//        ³                                                           ³
//        ³                                                           ³
//        ³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³³
"""

import sys
import socket
import math
import cv2
import numpy as np
from array import *
import tkinter as tk
import os
from tkinter import *
import PIL
from PIL import ImageTk # -> TODO: sudo apt-get install python3-pil.imagetk
import PIL.ImageOps

SCRIPT_VERSION = "V4.3_16/02/2024"

WINDOW_SHIFT_X = 278
WINDOW_SHIFT_Y = 130
WINDOW_WIDTH = 630
WINDOW_HEIGHT = 320

WINDOW_HALF_WIDTH = 315
WINDOW_HALF_HEIGHT = 160
posiz_pattern_x = 0
posiz_pattern_y = 0

lumen_accumul = 0
luminanza = 0
lux_25m = 0
mm_panel_per_pixel = 0.1250
inclinazione_pixel_panel = 0
#
# centroXpx = WINDOW_HALF_WIDTH + (5.0 / mm_panel_per_pixel)
# centroYpx = WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + (5.0 / mm_panel_per_pixel)
centroXpx = WINDOW_HALF_WIDTH + (8.0 / 0.1250)
centroYpx = WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + (3.0 / 0.1250)

# Xpx_in = centroXpx - (3.0 / mm_panel_per_pixel)
# Xpx_fin = centroXpx + (3.0 / mm_panel_per_pixel)
# Ypx_in = centroYpx - (3.0 / mm_panel_per_pixel)
# Ypx_fin = centroYpx + (3.0 / mm_panel_per_pixel)

Xpx_in = centroXpx - (5.0 / 0.1250)
Xpx_fin = centroXpx + (5.0 / 0.1250)
Ypx_in = centroYpx - (1.0 / 0.1250)
Ypx_fin = centroYpx + (1.0 / 0.1250)

offset_glarelight_lux = 0
#
centroXpx_ABB = WINDOW_HALF_WIDTH
centroYpx_ABB = WINDOW_HALF_HEIGHT + inclinazione_pixel_panel
offset_ABBlight_lux = 0

# Xpx_in_ABB = centroXpx_ABB - (3.0 / mm_panel_per_pixel)
# Xpx_fin_ABB = centroXpx_ABB + (3.0 / mm_panel_per_pixel)
# Ypx_in_ABB = centroYpx_ABB - (3.0 / mm_panel_per_pixel)
# Ypx_fin_ABB = centroYpx_ABB + (3.0 / mm_panel_per_pixel)

Xpx_in_ABB = centroXpx_ABB - (3.0 / 0.1250)
Xpx_fin_ABB = centroXpx_ABB + (3.0 / 0.1250)
Ypx_in_ABB = centroYpx_ABB - (3.0 / 0.1250)
Ypx_fin_ABB = centroYpx_ABB + (3.0 / 0.1250)

#

pixels_tac1_tac2 = 10
lunghezza_tac = 5

numero_di_tacche_abbagl_offset_x = -3
numero_di_tacche_abbagl_offset_y = 6

argomenti_passati_script = ["nome_script", "tipo_faro"]
argomenti_passati_script[0] = sys.argv[0]
argomenti_passati_script[1] = sys.argv[1]

replica_da_Proteus = "" # replica_da_Proteus = str(0)
port = int(sys.argv[2]) if len(sys.argv) >= 3 else 28500

display_croce = 0
pattern = 0
request_start_config = 1

shift1 = (0, -200)
shift2 = (0, 200)
shift3 = (-200, 0)
shift4 = (200, 0)

punto_di_massima_derivata = (0, 0)
punto_centrale_anabb = (0, 0)

punto1 = (0, 0)
punto2 = (0, 0)
punto3 = (0, 0)

punto1_test1 = (0, 0)
punto1_test2 = (0, 0)
punto1_test3 = (0, 0)

tol = 10  # in pixels
tolV = 10  # in pixels
tolH = 10  # in pixels
Larghezza_filtro_gaussiano = 21  # in pixels

SL1 = (WINDOW_HALF_WIDTH - tolH, 0)
EL1 = (WINDOW_HALF_WIDTH - tolH, WINDOW_HEIGHT)

SL2 = (WINDOW_HALF_WIDTH + tolH, 0)
EL2 = (WINDOW_HALF_WIDTH + tolH, WINDOW_HEIGHT)

SL3 = (0, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV)
EL3 = (WINDOW_WIDTH, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV)

SL4 = (0, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV)
EL4 = (WINDOW_WIDTH, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV)

tx_A = 0 # abbagliante
ty_A = 0 # abbagliante
tx_N = 0 # anabbagliante
ty_N = 0 # anabbagliante
tx_F = 0 # fendinebbia
ty_F = 0 # fendinebbia

start_row = 0
end_row = 0
start_col = 0
end_col = 0

lin_dem_anabb_offset_x = -200
lin_dem_anabb_offset_y = 5
lin_dem_anabb_coeff_angol = 0.267949192

lux_su_lineaX_AtH = 200
lux_su_lineaY_AtH = 200

alfa_LPF = 0.10000
Xc_curr = 0.00000 
Xc_prev = 0.00000
Yc_curr = 0.00000 
Yc_prev = 0.00000
Xc_float = 0.00000 
Yc_float = 0.00000

flag_NO_telecamera = 1
display_none_croci_linee_anabb = 0 
len_window_y = 60
linea_demarcazione_anabbagliante_invisibile = 0
banda_calc_anabb_visibile = 0
metodo_calc_anabb = 0
step_media = 1
step_contr = 4

maxLoc_tuple_prev_x = 0
maxLoc_tuple_filtered_x = 0
maxLoc_tuple_prev_y = 0
maxLoc_tuple_filtered_y = 0

maxVal_abb = 0

img_color = np.zeros([WINDOW_HEIGHT, WINDOW_WIDTH, 3], dtype=np.uint8)  # h,w,()

def refresh_mm_panel_per_pix_stuff():
    global centroXpx, centroYpx, Xpx_in, Xpx_fin, Ypx_in, Ypx_fin, Xpx_in_ABB, Xpx_fin_ABB, Ypx_in_ABB, Ypx_fin_ABB
    # centroXpx = WINDOW_HALF_WIDTH + (5.0 / mm_panel_per_pixel)
    centroXpx = WINDOW_HALF_WIDTH + (8.0 / 0.1250)
    # centroYpx = (
    #     WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + (5.0 / mm_panel_per_pixel)
    # )
    centroYpx = (
    WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + (3.0 / 0.1250)
    )
    # Xpx_in = centroXpx - (3.0 / mm_panel_per_pixel)
    # Xpx_fin = centroXpx + (3.0 / mm_panel_per_pixel)
    # Ypx_in = centroYpx - (3.0 / mm_panel_per_pixel)
    # Ypx_fin = centroYpx + (3.0 / mm_panel_per_pixel)
    Xpx_in = centroXpx - (5.0 / 0.1250)
    Xpx_fin = centroXpx + (5.0 / 0.1250)
    Ypx_in = centroYpx - (1.0 / 0.1250)
    Ypx_fin = centroYpx + (1.0 / 0.1250)
    centroYpx_ABB = WINDOW_HALF_HEIGHT + inclinazione_pixel_panel
    # Xpx_in_ABB = centroXpx_ABB - (3.0 / mm_panel_per_pixel)
    # Xpx_fin_ABB = centroXpx_ABB + (3.0 / mm_panel_per_pixel)
    # Ypx_in_ABB = centroYpx_ABB - (3.0 / mm_panel_per_pixel)
    # Ypx_fin_ABB = centroYpx_ABB + (3.0 / mm_panel_per_pixel)
    Xpx_in_ABB = centroXpx_ABB - (3.0 / 0.1250)
    Xpx_fin_ABB = centroXpx_ABB + (3.0 / 0.1250)
    Ypx_in_ABB = centroYpx_ABB - (3.0 / 0.1250)
    Ypx_fin_ABB = centroYpx_ABB + (3.0 / 0.1250)


def somma_xy(coppia1, coppia2):
    return (coppia1[0] + coppia2[0], coppia1[1] + coppia2[1])

def calcola_punto1(max_lux_xy):
    return (max_lux_xy[0]+lin_dem_anabb_offset_x, max_lux_xy[1]+lin_dem_anabb_offset_y) # return (max_lux_xy[0]-100, max_lux_xy[1]+15)

"""
def calcola_punto1(max_lux_xy):
    return (max_lux_xy[0]+0, max_lux_xy[1]+0) # return (max_lux_xy[0]-100, max_lux_xy[1]+15)
"""

def calcola_punto2(point1):
    if argomenti_passati_script[1] == "ANABBAGLIANTE" :
        return (
            point1[0] + WINDOW_HEIGHT, 
            (point1[1] - (int(WINDOW_HEIGHT * lin_dem_anabb_coeff_angol))), # return (point1[0]+altezza_frame, (point1[1]-(int(altezza_frame*0.267949192))))
        )
    elif argomenti_passati_script[1] == "FENDINEBBIA" :
        return (point1[0] + WINDOW_HEIGHT, point1[1])


def calcola_punto3(point1):
    return (point1[0] - WINDOW_HEIGHT, point1[1])


def refresh_tolerance_display():
    global SL1, EL1, SL2, EL2, SL3, EL3, SL4, EL4
    SL1 = (WINDOW_HALF_WIDTH - tolH, 0)
    EL1 = (WINDOW_HALF_WIDTH - tolH, WINDOW_HEIGHT)

    SL2 = (WINDOW_HALF_WIDTH + tolH, 0)
    EL2 = (WINDOW_HALF_WIDTH + tolH, WINDOW_HEIGHT)

    SL3 = (0, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV)
    EL3 = (WINDOW_WIDTH, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV)

    SL4 = (0, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV)
    EL4 = (WINDOW_WIDTH, WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV)


def display_griglia_HV(frame):
    if argomenti_passati_script[1] != "FENDINEBBIA":
        cv2.line(frame, SL1, EL1, (0, 255, 255), 1)
        cv2.line(frame, SL2, EL2, (0, 255, 255), 1)
    cv2.line(frame, SL3, EL3, (0, 255, 255), 1)
    cv2.line(frame, SL4, EL4, (0, 255, 255), 1)


def display_griglia_HV2(sfondo):
    if argomenti_passati_script[1] != "FENDINEBBIA":
        cv2.line(sfondo, SL1, EL1, (0, 255, 255), 1)
        cv2.line(sfondo, SL2, EL2, (0, 255, 255), 1)
    cv2.line(sfondo, SL3, EL3, (0, 255, 255), 1)
    cv2.line(sfondo, SL4, EL4, (0, 255, 255), 1)


def display_griglia_HV3(img_color):
    if argomenti_passati_script[1] != "FENDINEBBIA":
        cv2.line(img_color, SL1, EL1, (0, 0, 0), 1)
        cv2.line(img_color, SL2, EL2, (0, 0, 0), 1)
    cv2.line(img_color, SL3, EL3, (0, 0, 0), 1)
    cv2.line(img_color, SL4, EL4, (0, 0, 0), 1)


def display_scala_graduata_frame(frame):  # Orange / #FFA500 RGB
    cv2.line(frame, (20, 60), (620, 60), (0, 165, 255), 1)  # Line H1
    cv2.line(
        frame,
        (WINDOW_HALF_WIDTH, 60),
        (WINDOW_HALF_WIDTH, 60 + lunghezza_tac),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            frame,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            frame,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(frame, (20, 260), (620, 260), (0, 165, 255), 1)  # Line H2
    cv2.line(
        frame,
        (WINDOW_HALF_WIDTH, 260),
        (WINDOW_HALF_WIDTH, 260 - lunghezza_tac),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            frame,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            frame,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(
        frame, (20, 60), (20, 260), (0, 165, 255), 1
    )  # Line V1 - cv2.line(frame, (20,60), (20,420), (0,165,255), 1)
    cv2.line(
        frame,
        (20, WINDOW_HALF_HEIGHT),
        (20 + lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):  # for tac in range( 1, 17, 1 ):
        cv2.line(
            frame,
            (20, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            frame,
            (20, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(
        frame, (620, 60), (620, 260), (0, 165, 255), 1
    )  # Line V2 - cv2.line(frame, (620,60), (620,420), (0,165,255), 1)
    cv2.line(
        frame,
        (620, WINDOW_HALF_HEIGHT),
        (620 - lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):  # for tac in range( 1, 17, 1 ):
        cv2.line(
            frame,
            (620, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            frame,
            (620, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette


def display_scala_graduata_sfondo(sfondo):
    cv2.line(sfondo, (20, 60), (620, 60), (0, 165, 255), 1)  # Line H1
    cv2.line(
        sfondo,
        (WINDOW_HALF_WIDTH, 60),
        (WINDOW_HALF_WIDTH, 60 + lunghezza_tac),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            sfondo,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            sfondo,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(sfondo, (20, 260), (620, 260), (0, 165, 255), 1)  # Line H2
    cv2.line(
        sfondo,
        (WINDOW_HALF_WIDTH, 260),
        (WINDOW_HALF_WIDTH, 260 - lunghezza_tac),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            sfondo,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            sfondo,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(sfondo, (20, 60), (20, 260), (0, 165, 255), 1)  # Line V1
    cv2.line(
        sfondo,
        (20, WINDOW_HALF_HEIGHT),
        (20 + lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):
        cv2.line(
            sfondo,
            (20, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            sfondo,
            (20, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette

    cv2.line(sfondo, (620, 60), (620, 260), (0, 165, 255), 1)  # Line V2
    cv2.line(
        sfondo,
        (620, WINDOW_HALF_HEIGHT),
        (620 - lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 165, 255),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):
        cv2.line(
            sfondo,
            (620, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette
        cv2.line(
            sfondo,
            (620, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 165, 255),
            1,
        )  # tacchette


def display_scala_graduata_thermal(img_color):
    cv2.line(img_color, (20, 60), (620, 60), (0, 0, 0), 1)  # Line H1
    cv2.line(
        img_color,
        (WINDOW_HALF_WIDTH, 60),
        (WINDOW_HALF_WIDTH, 60 + lunghezza_tac),
        (0, 0, 0),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            img_color,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 0, 0),
            1,
        )  # tacchette
        cv2.line(
            img_color,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 60 + lunghezza_tac),
            (0, 0, 0),
            1,
        )  # tacchette

    cv2.line(img_color, (20, 260), (620, 260), (0, 0, 0), 1)  # Line H2
    cv2.line(
        img_color,
        (WINDOW_HALF_WIDTH, 260),
        (WINDOW_HALF_WIDTH, 260 - lunghezza_tac),
        (0, 0, 0),
        1,
    )  # tacchetta centrale
    for tac in range(1, 29, 1):
        cv2.line(
            img_color,
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH - pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 0, 0),
            1,
        )  # tacchette
        cv2.line(
            img_color,
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260),
            (WINDOW_HALF_WIDTH + pixels_tac1_tac2 * tac, 260 - lunghezza_tac),
            (0, 0, 0),
            1,
        )  # tacchette

    cv2.line(img_color, (20, 60), (20, 260), (0, 0, 0), 1)  # Line V1
    cv2.line(
        img_color,
        (20, WINDOW_HALF_HEIGHT),
        (20 + lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 0, 0),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):
        cv2.line(
            img_color,
            (20, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 0, 0),
            1,
        )  # tacchette
        cv2.line(
            img_color,
            (20, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (20 + lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 0, 0),
            1,
        )  # tacchette

    cv2.line(img_color, (620, 60), (620, 260), (0, 0, 0), 1)  # Line V2
    cv2.line(
        img_color,
        (620, WINDOW_HALF_HEIGHT),
        (620 - lunghezza_tac, WINDOW_HALF_HEIGHT),
        (0, 0, 0),
        1,
    )  # tacchetta centrale
    for tac in range(1, 9, 1):
        cv2.line(
            img_color,
            (620, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT - pixels_tac1_tac2 * tac),
            (0, 0, 0),
            1,
        )  # tacchette
        cv2.line(
            img_color,
            (620, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (620 - lunghezza_tac, WINDOW_HALF_HEIGHT + pixels_tac1_tac2 * tac),
            (0, 0, 0),
            1,
        )  # tacchette


def chiudi_programma(video, *args):
    print("Chiusura programma in corso...")
    video.release()
    sys.exit(0) # https://www.geeksforgeeks.org/python-exit-commands-quit-exit-sys-exit-and-os-_exit/

def zoom(img, zoom_factor=2):
    return cv2.resize(img, None, fx=zoom_factor, fy=zoom_factor)


def punto_anab_cr( gray_image, len_window_y, punto1_y, pos_x ):

    y_demark = punto1_y

    if ((punto1_y-len_window_y)<0):
        min_y = 0
    else:
        min_y = punto1_y-len_window_y

    if ((punto1_y+len_window_y)>319):
        Max_y = 319
    else:
        Max_y = punto1_y+len_window_y
    
    try :
        num_pixels = int( float(Max_y - min_y)/float(step_media) )
    except ZeroDivisionError :
        num_pixels = Max_y - min_y

    lux_media_su_lineaY = 0

    for pxY in range( min_y , Max_y , step_media ):
        lux_media_su_lineaY = lux_media_su_lineaY + gray_image[pxY][pos_x] # [y][x]
        
    try :
        lux_media_su_lineaY = int( float(lux_media_su_lineaY)/float(num_pixels) )
    except ZeroDivisionError :
        lux_media_su_lineaY = int( float(lux_media_su_lineaY)/float(319) )
    
    distanza_lux_abs_min = 1000000  

    for pxY in range( min_y , Max_y , step_media ):
        if( abs(gray_image[pxY][pos_x]-lux_media_su_lineaY)<distanza_lux_abs_min ):
            distanza_lux_abs_min = abs(gray_image[pxY][pos_x]-lux_media_su_lineaY)
            y_demark = pxY
    
    return (pos_x, y_demark)


def punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y, pos_x ):

    y_demark = punto1_y

    if ((punto1_y-len_window_y)<0):
        min_y = 0
    else:
        min_y = punto1_y-len_window_y

    if ((punto1_y+len_window_y)>310):
        Max_y = 310
    else:
        Max_y = punto1_y+len_window_y
    
    deriv_max = -1000000

    for pxY in range( min_y , Max_y , step_contr ):
        if( gray_image[pxY+step_contr][pos_x]-gray_image[pxY][pos_x]>deriv_max ):
            deriv_max = gray_image[pxY+step_contr][pos_x]-gray_image[pxY][pos_x]
            y_demark = pxY

    return (pos_x, y_demark)


def punto_Abb_up( gray_image, pos_x ):

    min_y = 80
    Max_y = 310
    y_demark = 160
    passo = 3

    lux_su_lineaY = 0

    for pxY in range( min_y , Max_y , passo ):
        if( gray_image[pxY][pos_x] > lux_su_lineaY ):
            lux_su_lineaY = gray_image[pxY][pos_x] 
        else:
            y_demark = pxY - passo
            break
        
    return (pos_x, y_demark)


def punto_Abb_dwn( gray_image, pos_x ):

    min_y = 310
    Max_y = 80
    y_demark = 160
    passo = -3

    lux_su_lineaY = 0

    for pxY in range( min_y , Max_y , passo ):
        if( gray_image[pxY][pos_x] > lux_su_lineaY ):
            lux_su_lineaY = gray_image[pxY][pos_x] 
        else:
            y_demark = pxY - passo
            break
        
    return (pos_x, y_demark)

"""

def punto_Abb_up_ORIZ( gray_image, pos_y ):

    min_x = 100
    Max_x = 610
    x_demark = 320
    passo = 3

    lux_su_lineaX = 0

    for pxX in range( min_x , Max_x , passo ):
        if( gray_image[pos_y][pxX] > lux_su_lineaX ):
            lux_su_lineaX = gray_image[pos_y][pxX] 
        else:
            x_demark = pxX - passo
            break
        
    return (x_demark, pos_y)


def punto_Abb_dwn_ORIZ( gray_image, pos_y ):

    min_x = 610
    Max_x = 100
    x_demark = 320
    passo = -3

    lux_su_lineaX = 0

    for pxX in range( min_x , Max_x , passo ):
        if( gray_image[pos_y][pxX] > lux_su_lineaX ):
            lux_su_lineaX = gray_image[pos_y][pxX] 
        else:
            x_demark = pxX - passo
            break
        
    return (x_demark, pos_y)

"""

#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------


def punto_Abb_up_ORIZ( gray_image, pos_y ):

    global lux_su_lineaX_AtH
    global maxVal_abb

    min_x = 30
    Max_x = 610
    x_demark = 320
    passo = 3

    for pxX in range( min_x , Max_x , passo ):
        if( gray_image[pos_y][pxX] >= maxVal_abb ): # if( gray_image[pos_y][pxX] >= lux_su_lineaX_AtH ):
            x_demark = pxX
        
    return (x_demark, pos_y)


def punto_Abb_dwn_ORIZ( gray_image, pos_y ):

    global lux_su_lineaX_AtH
    global maxVal_abb

    min_x = 610
    Max_x = 30
    x_demark = 320
    passo = -3

    for pxX in range( min_x , Max_x , passo ):
        if( gray_image[pos_y][pxX] >= maxVal_abb ): # if( gray_image[pos_y][pxX] >= lux_su_lineaX_AtH ):
            x_demark = pxX
        
    return (x_demark, pos_y)


def punto_Abb_up_VERT( gray_image, pos_x ):

    global lux_su_lineaY_AtH
    global maxVal_abb

    min_y = 80
    Max_y = 310
    y_demark = 160
    passo = 3

    for pxY in range( min_y , Max_y , passo ):
        if( gray_image[pxY][pos_x] >= maxVal_abb ): # if( gray_image[pxY][pos_x] >= lux_su_lineaY_AtH ):
            y_demark = pxY
        
    return (pos_x, y_demark)


def punto_Abb_dwn_VERT( gray_image, pos_x ):

    global lux_su_lineaY_AtH
    global maxVal_abb

    min_y = 310
    Max_y = 80
    y_demark = 160
    passo = -3

    for pxY in range( min_y , Max_y , passo ):
        if( gray_image[pxY][pos_x] >= maxVal_abb ): # if( gray_image[pxY][pos_x] >= lux_su_lineaY_AtH ):
            y_demark = pxY
        
    return (pos_x, y_demark)


#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------
#---------------------------------------------------------------------------------------------------------


def minimi_quadrati( data ):
    n = len(data)
    
    # Calcoliamo le somme necessarie
    sum_x = sum(x for x, y in data)
    sum_y = sum(y for x, y in data)
    sum_xx = sum(x * x for x, y in data)
    sum_xy = sum(x * y for x, y in data)
    
    # Calcoliamo i coefficienti della retta di regressione
    try :
        m = (n * sum_xy - sum_x * sum_y) / (n * sum_xx - sum_x**2)
    except ZeroDivisionError :
        m = 0

    try :
        b = (sum_y - m * sum_x) / n
    except ZeroDivisionError :
        b = 0

    return m, b


def display_croci_anabb( frame, Point1_CR, Point2_CR, Point3_CR, Point4_CR, Point5_CR, Point6_CR, Point7_CR, Status_Points_CR ):

    if Status_Points_CR[0] == 0 :
        cv2.line(frame, (Point1_CR[0]-10, Point1_CR[1] ), ( Point1_CR[0]+10, Point1_CR[1] ), (0, 0, 255), 2)
        cv2.line(frame, ( Point1_CR[0], Point1_CR[1]-10 ), ( Point1_CR[0], Point1_CR[1]+10 ), (0, 0, 255), 2)
    else :
        cv2.line(frame, (Point1_CR[0]-10, Point1_CR[1] ), ( Point1_CR[0]+10, Point1_CR[1] ), (255, 255, 0), 2)
        cv2.line(frame, ( Point1_CR[0], Point1_CR[1]-10 ), ( Point1_CR[0], Point1_CR[1]+10 ), (255, 255, 0), 2)
                             
    if Status_Points_CR[1] == 0 :
        cv2.line(frame, (Point2_CR[0]-10, Point2_CR[1] ), ( Point2_CR[0]+10, Point2_CR[1] ), (0, 0, 255), 2)
        cv2.line(frame, ( Point2_CR[0], Point2_CR[1]-10 ), ( Point2_CR[0], Point2_CR[1]+10 ), (0, 0, 255), 2)
    else :
        cv2.line(frame, (Point2_CR[0]-10, Point2_CR[1] ), ( Point2_CR[0]+10, Point2_CR[1] ), (255, 255, 0), 2)
        cv2.line(frame, ( Point2_CR[0], Point2_CR[1]-10 ), ( Point2_CR[0], Point2_CR[1]+10 ), (255, 255, 0), 2)

    if Status_Points_CR[2] == 0 :
        cv2.line(frame, (Point3_CR[0]-10, Point3_CR[1] ), ( Point3_CR[0]+10, Point3_CR[1] ), (0, 0, 255), 2)
        cv2.line(frame, ( Point3_CR[0], Point3_CR[1]-10 ), ( Point3_CR[0], Point3_CR[1]+10 ), (0, 0, 255), 2)
    else :
        cv2.line(frame, (Point3_CR[0]-10, Point3_CR[1] ), ( Point3_CR[0]+10, Point3_CR[1] ), (255, 255, 0), 2)
        cv2.line(frame, ( Point3_CR[0], Point3_CR[1]-10 ), ( Point3_CR[0], Point3_CR[1]+10 ), (255, 255, 0), 2)

    if Status_Points_CR[3] == 0 :
        cv2.line(frame, (Point4_CR[0]-10, Point4_CR[1] ), ( Point4_CR[0]+10, Point4_CR[1] ), (0, 0, 255), 2)
        cv2.line(frame, ( Point4_CR[0], Point4_CR[1]-10 ), ( Point4_CR[0], Point4_CR[1]+10 ), (0, 0, 255), 2)
    else :
        cv2.line(frame, (Point4_CR[0]-10, Point4_CR[1] ), ( Point4_CR[0]+10, Point4_CR[1] ), (255, 255, 0), 2)
        cv2.line(frame, ( Point4_CR[0], Point4_CR[1]-10 ), ( Point4_CR[0], Point4_CR[1]+10 ), (255, 255, 0), 2)

    if Status_Points_CR[4] == 0 :
        cv2.line(frame, (Point5_CR[0]-10, Point5_CR[1] ), ( Point5_CR[0]+10, Point5_CR[1] ), (0, 0, 255), 2)
        cv2.line(frame, ( Point5_CR[0], Point5_CR[1]-10 ), ( Point5_CR[0], Point5_CR[1]+10 ), (0, 0, 255), 2)
    else :
        cv2.line(frame, (Point5_CR[0]-10, Point5_CR[1] ), ( Point5_CR[0]+10, Point5_CR[1] ), (255, 255, 0), 2)
        cv2.line(frame, ( Point5_CR[0], Point5_CR[1]-10 ), ( Point5_CR[0], Point5_CR[1]+10 ), (255, 255, 0), 2)

    if Status_Points_CR[5] == 0 :
        cv2.line(frame, (Point6_CR[0]-10, Point6_CR[1] ), ( Point6_CR[0]+10, Point6_CR[1] ), (0, 0, 255), 2)
        cv2.line(frame, ( Point6_CR[0], Point6_CR[1]-10 ), ( Point6_CR[0], Point6_CR[1]+10 ), (0, 0, 255), 2)
    else :
        cv2.line(frame, (Point6_CR[0]-10, Point6_CR[1] ), ( Point6_CR[0]+10, Point6_CR[1] ), (255, 255, 0), 2)
        cv2.line(frame, ( Point6_CR[0], Point6_CR[1]-10 ), ( Point6_CR[0], Point6_CR[1]+10 ), (255, 255, 0), 2)

    if Status_Points_CR[6] == 0 : # blu
        cv2.line(frame, (Point7_CR[0]-10, Point7_CR[1] ), ( Point7_CR[0]+10, Point7_CR[1] ), (0, 0, 255), 2)
        cv2.line(frame, ( Point7_CR[0], Point7_CR[1]-10 ), ( Point7_CR[0], Point7_CR[1]+10 ), (0, 0, 255), 2)
    else :                        # giallo
        cv2.line(frame, (Point7_CR[0]-10, Point7_CR[1] ), ( Point7_CR[0]+10, Point7_CR[1] ), (255, 255, 0), 2)
        cv2.line(frame, ( Point7_CR[0], Point7_CR[1]-10 ), ( Point7_CR[0], Point7_CR[1]+10 ), (255, 255, 0), 2)


def display_linee_anabb( frame, Coefficiente_angolare_orizz, Termine_noto_orizz, Coefficiente_angolare_inclin, Termine_noto_inclin, WINDOW_WIDTH ) :
                
    punta_A_x_blu = 0
    punta_A_y_blu = int( (Coefficiente_angolare_orizz*(float(punta_A_x_blu))+Termine_noto_orizz ) )
    punta_B_x_blu = WINDOW_WIDTH
    punta_B_y_blu = int( (Coefficiente_angolare_orizz*(float(punta_B_x_blu))+Termine_noto_orizz ) )
    cv2.line(frame, (punta_A_x_blu, punta_A_y_blu ), ( punta_B_x_blu, punta_B_y_blu ), (0, 0, 255), 4)
    punta_A_x_giallo = 0
    punta_A_y_giallo = int( (Coefficiente_angolare_inclin*(float(punta_A_x_giallo))+Termine_noto_inclin ) )
    punta_B_x_giallo= WINDOW_WIDTH
    punta_B_y_giallo = int( (Coefficiente_angolare_inclin*(float(punta_B_x_giallo))+Termine_noto_inclin ) )                
    cv2.line(frame, (punta_A_x_giallo, punta_A_y_giallo ), ( punta_B_x_giallo, punta_B_y_giallo ), (255, 255, 0), 4)


def calc_y_sup_finestra_Lux_anabb() :

    global posiz_pattern_y
    sup_pix = 0
    if( (posiz_pattern_y - 60) < 1 ) :
        sup_pix = 1
    else :
        sup_pix = posiz_pattern_y - 60
    
    return sup_pix


def calc_y_inf_finestra_Lux_anabb() :

    global posiz_pattern_y
    inf_pix = 0
    if( (posiz_pattern_y + 60) > 318 ) :
        inf_pix = 318
    else :
        inf_pix = posiz_pattern_y + 60
    
    return inf_pix


"""
    if not video.isOpened():
        print("Could not open video")
        sys.exit(1)
"""


if __name__ == "__main__":
    # TODO 02/08/2023 - Attenzione a tenere l'indice fisso della telecamera
    # perche' potrebbe 
    
    for indice_telecamera in range( 0 , 11 , 1 ):
        video = cv2.VideoCapture(indice_telecamera)
        if video.isOpened():
            flag_NO_telecamera = 0
            break

    if flag_NO_telecamera == 0 :
        root = tk.Tk()
        root.overrideredirect(True) # remove the title bar and other default window formatting, Ive noticed this also removes the ability to full screen windows, drag edges to resize, and other native window management methods
        root.geometry(
            "{}x{}+{}+{}".format(
                WINDOW_WIDTH, WINDOW_HEIGHT, WINDOW_SHIFT_X, WINDOW_SHIFT_Y
            )
        )
        root.resizable(False, False)
        lmain = tk.Label(root)
        lmain.pack() # https://python-course.eu/tkinter/labels-in-tkinter.php
        # Decommentare se si vuole che cliccando sull'immagine lo script venga
        # chiuso (importare partial dalla libreria functools)
        # lmain.bind("<Button-1>", partial(chiudi_programma, video))

    with open("/tmp/all_msgs.txt", "w") as f:
        f.write("")
            
    def show_frame():
        # TODO 02/08/2023 - Rimuovere l'utilizzo di 'global'
        global request_start_config, posiz_pattern_x, posiz_pattern_y, lux_25m
        global tx_A, ty_A, tx_F, ty_F, tx_N, ty_N, pattern, translation_matrix
        global Larghezza_filtro_gaussiano, Larghezza_filtro_gaussiano, tolH, tolV
        global inclinazione_pixel_panel, display_croce, img_color, sfondo, mm_panel_per_pixel
        global punto1, punto2, punto3
        global start_row, end_row, start_col, end_col, numero_di_tacche_abbagl_offset_x, numero_di_tacche_abbagl_offset_y, lin_dem_anabb_offset_x, lin_dem_anabb_offset_y, lin_dem_anabb_coeff_angol   
        global sfondo_tmp, inverted_sfondo
        global lux_su_lineaX_AtH, lux_su_lineaY_AtH
        global punto1_x_new_calc, punto1_x_new_calc2, punto1_test1
        global alfa_LPF
        global flag_NO_telecamera
        global replica_da_Proteus
        global display_none_croci_linee_anabb
        global len_window_y
        global linea_demarcazione_anabbagliante_invisibile
        global banda_calc_anabb_visibile
        global metodo_calc_anabb
        global step_media, step_contr
        global maxLoc_tuple_prev_x, maxLoc_tuple_filtered_x, maxLoc_tuple_prev_y, maxLoc_tuple_filtered_y
        global maxVal_abb
        global punto_di_massima_derivata
        global punto_centrale_anabb
        global Xc_curr, Xc_prev, Yc_curr, Yc_prev, Xc_float, Yc_float

        
        client_socket = socket.socket()
        client_socket.connect(("localhost", port))

        if request_start_config == 1:

            if flag_NO_telecamera == 1:
                msg = "NO_telecamera"
            else:
                msg = "start_cfg %s " % SCRIPT_VERSION
        
        else:
            msg = "XYL %d %d %f " % (posiz_pattern_x, posiz_pattern_y, lux_25m)
            
        with open("/tmp/all_msgs.txt", "a") as f:
            f.write("[TX] " + msg + "\n")
        with open("/tmp/last_msg.txt", "w") as f:
            f.write(msg)

        client_socket.send(msg.encode())                              # send message
        replica_da_Proteus = client_socket.recv(1024).decode("UTF-8") # receive response = socket.recv is a blocking call - The return value is a bytes object representing the data received
        
        with open("/tmp/all_msgs.txt", "a") as f:
            f.write("[RX] " + replica_da_Proteus + "\n")

        if request_start_config == 1:
            request_start_config = 0
            if (argomenti_passati_script[1] == "ASK-VERS-PY") and (
                replica_da_Proteus[0:5] == "EXIT!"
            ):
                sys.exit()

            elif replica_da_Proteus[0:5] == "NoCAM":
                sys.exit() # chiudi_programma(video)

            elif replica_da_Proteus[0:5] == "CFG->":
                if replica_da_Proteus[5] == "0":  # analog
                    pattern = 0
                elif replica_da_Proteus[5] == "1":  # digital
                    pattern = 1
                elif replica_da_Proteus[5] == "2":  # thermal
                    pattern = 2
                # ----------------------------------
                if replica_da_Proteus[6] == "0":
                    display_croce = 0
                elif replica_da_Proteus[6] == "1":
                    display_croce = 1
            else:
                pattern = 0
                display_croce = 0
            # ----------------------------------------------------- // tol
            if replica_da_Proteus[7:10] == "TOV":
                tolV = int(replica_da_Proteus[10:13])  # in pixels
                refresh_tolerance_display()
            else:
                tolV = 10  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[13:16] == "mpx":  # mm_panel_per_pix
                mm_panel_per_pixel = float(replica_da_Proteus[16:24])
                refresh_mm_panel_per_pix_stuff()
            else:
                mm_panel_per_pixel = 0.1250
            # -----------------------------------------------------
            if replica_da_Proteus[24:27] == "inc":
                inclinazione_pixel_panel = int(replica_da_Proteus[27:31])
                refresh_tolerance_display()
                refresh_mm_panel_per_pix_stuff()
            else:
                inclinazione_pixel_panel = 0
            # -----------------------------------------------------
            if replica_da_Proteus[31:34] == "TOH":
                tolH = int(replica_da_Proteus[34:37])  # in pixels
                refresh_tolerance_display()
            else:
                tolH = 10  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[37:40] == "GSF":
                Larghezza_filtro_gaussiano = int(replica_da_Proteus[40:43])  # in pixels
            else:
                Larghezza_filtro_gaussiano = 21  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[43:46] == "TAX":  # abbagliante X
                tx_A = int(replica_da_Proteus[46:51])  # in pixels
            else:
                tx_A = 0  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[51:54] == "TAY":  # abbagliante Y
                ty_A = int(replica_da_Proteus[54:59])  # in pixels
            else:
                ty_A = 0  # in pixels

            if replica_da_Proteus[59:62] == "TNX":  # anabbagliante X
                tx_N = int(replica_da_Proteus[62:67])  # in pixels
            else:
                tx_N = 0  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[67:70] == "TNY":  # anabbagliante Y
                ty_N = int(replica_da_Proteus[70:75])  # in pixels
            else:
                ty_N = 0  # in pixels
            if replica_da_Proteus[75:78] == "TFX":  # fendinebbia X
                tx_F = int(replica_da_Proteus[78:83])  # in pixels
            else:
                tx_F = 0  # in pixels
            # -----------------------------------------------------
            if replica_da_Proteus[83:86] == "TFY":  # fendinebbia Y
                ty_F = int(replica_da_Proteus[86:91])  # in pixels
            else:
                ty_F = 0  # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[91:94] == 'CRI' ):   # Cropping riga iniziale  
                start_row = int(replica_da_Proteus[94:97])   # in pixels
            else:
                start_row = 0                                # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[97:100] == 'CRF' ):  # Cropping riga finale 
                end_row = int(replica_da_Proteus[100:103]) # in pixels
            else:
                end_row = 319                                # in pixels 
            #-----------------------------------------------------                             
            if( replica_da_Proteus[103:106] == 'CCI' ): # Cropping colonna iniziale 
                start_col = int(replica_da_Proteus[106:109]) # in pixels
            else:
                start_col = 0                                # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[109:112] == 'CCF' ): # Cropping colonna finale 
                end_col = int(replica_da_Proteus[112:115]) # in pixels
            else:
                end_col = 629                                # in pixels
            #-----------------------------------------------------    
            if( replica_da_Proteus[115:118] == 'tax' ):  
                numero_di_tacche_abbagl_offset_x = int(replica_da_Proteus[118:121]) # in pixels (-3)
            else:
                numero_di_tacche_abbagl_offset_x = -3                               # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[121:124] == 'tay' ):  
                numero_di_tacche_abbagl_offset_y = int(replica_da_Proteus[124:127]) # in pixels (+6)
            else:
                numero_di_tacche_abbagl_offset_y = 6                                # in pixels
            #-----------------------------------------------------
            if( replica_da_Proteus[127:130] == 'Lnx' ):  
                lin_dem_anabb_offset_x = int(replica_da_Proteus[130:135])      # in pixels
            else:
                lin_dem_anabb_offset_x = -200                                  # in pixels   
            #-----------------------------------------------------
            if( replica_da_Proteus[135:138] == 'Lny' ):  
                lin_dem_anabb_offset_y = int(replica_da_Proteus[138:143])      # in pixels
            else:
                lin_dem_anabb_offset_y = 5                                     # in pixels     
            #-----------------------------------------------------
            if( replica_da_Proteus[143:146] == 'AtH' ):  
                lux_su_lineaX_AtH = int(replica_da_Proteus[146:149])           # 0 - 255
            else:
                lux_su_lineaX_AtH = 200                                        # 0 - 255 
            #-----------------------------------------------------
            if( replica_da_Proteus[149:152] == 'Lnm' ):  
                lin_dem_anabb_coeff_angol = float(replica_da_Proteus[152:163]) # in pixels
            else:
                lin_dem_anabb_coeff_angol = 0.267949192                        # in pixels 
            #-----------------------------------------------------
            if( replica_da_Proteus[163:166] == 'alf' ):  
                alfa_LPF = float(replica_da_Proteus[166:173]) 
            else:
                alfa_LPF = 0.10000                        
            #-----------------------------------------------------
            if( replica_da_Proteus[173:176] == 'ncl' ):  
                display_none_croci_linee_anabb = int(replica_da_Proteus[176:178])       # 0,1,2,3 - 2 bytes
            else:
                display_none_croci_linee_anabb = 0                       
            #-----------------------------------------------------
            if( replica_da_Proteus[178:181] == 'lwn' ):  
                len_window_y = int(replica_da_Proteus[181:184])                         # 0 - 255 pixels - 3 bytes
            else:
                len_window_y = 60                       
            #-----------------------------------------------------
            if( replica_da_Proteus[184:187] == 'dnv' ):  
                if replica_da_Proteus[187] == "1":                                      # linea di demarcazione dell'anabbagliante = invisibile
                    linea_demarcazione_anabbagliante_invisibile = 1
                else:
                    linea_demarcazione_anabbagliante_invisibile = 0
            else:
                linea_demarcazione_anabbagliante_invisibile = 0
            #-----------------------------------------------------
            if( replica_da_Proteus[188:191] == 'bcn' ):  
                if replica_da_Proteus[191] == "1":                                      # banda di calcolo dell'anabbagliante = visibile
                    banda_calc_anabb_visibile = 1
                else:
                    banda_calc_anabb_visibile = 0
            else:
                banda_calc_anabb_visibile = 0
            #-----------------------------------------------------
            if( replica_da_Proteus[192:195] == 'mcb' ):  
                if replica_da_Proteus[195] == "1":                                      # metodo di calcolo dell'anabbagliante
                    metodo_calc_anabb = 1
                else:
                    metodo_calc_anabb = 0
            else:
                metodo_calc_anabb = 0
            #-----------------------------------------------------
            if( replica_da_Proteus[196:199] == 'stm' ):  
                step_media = int(replica_da_Proteus[199:202])                           # 0 - 255 pixels - 3 bytes
            else:
                step_media = 1                       
            #-----------------------------------------------------
            if( replica_da_Proteus[202:205] == 'stc' ):  
                step_contr = int(replica_da_Proteus[205:208])                           # 0 - 255 pixels - 3 bytes
            else:
                step_contr = 4                       
            #-----------------------------------------------------
            if( replica_da_Proteus[208:211] == 'AtV' ):  
                lux_su_lineaY_AtH = int(replica_da_Proteus[211:214])           # 0 - 255
            else:
                lux_su_lineaY_AtH = 200                                        # 0 - 255 
            #-----------------------------------------------------


        else:

            if replica_da_Proteus[0:13] == "inclinazione*":
                inclinazione_pixel_panel = int(replica_da_Proteus[13:17])      # in pixels
                refresh_tolerance_display()
                refresh_mm_panel_per_pix_stuff()
            elif replica_da_Proteus == "croce_ON":
                display_croce = 1
            elif replica_da_Proteus == "croce_OFF":
                display_croce = 0
            elif replica_da_Proteus == "pattern_analog":
                pattern = 0
            elif replica_da_Proteus == "pattern_digital":
                pattern = 1
            elif replica_da_Proteus == "pattern_thermal":
                pattern = 2

        if pattern == 1:  # pattern_digital
            if argomenti_passati_script[1] == "ANABBAGLIANTE":
                sfondo_tmp = cv2.imread("/home/pi/Applications/topauto_anabb.bmp")
                sfondo = cv2.cvtColor(sfondo_tmp, cv2.COLOR_BGR2RGB)
            elif argomenti_passati_script[1] == "ABBAGLIANTE":
                sfondo_tmp = cv2.imread("/home/pi/Applications/topauto_abb.bmp")
                sfondo = cv2.cvtColor(sfondo_tmp, cv2.COLOR_BGR2RGB)
            elif argomenti_passati_script[1] == "FENDINEBBIA":
                sfondo_tmp = cv2.imread("/home/pi/Applications/topauto_fend.bmp")
                sfondo = cv2.cvtColor(sfondo_tmp, cv2.COLOR_BGR2RGB)
            display_griglia_HV2(sfondo)

        ok, frame_originale = video.read()
        cv2.imwrite("/tmp/frame_originale.bmp", frame_originale)

        # Creiamo la matrice di traslazione a seconda se abbiamo abbagliante, anabbagliante o fendinebbia
        if argomenti_passati_script[1] == "ABBAGLIANTE":
            translation_matrix = np.array(
                [[1, 0, tx_A], [0, 1, ty_A]], dtype=np.float32
            )
        elif argomenti_passati_script[1] == "ANABBAGLIANTE":
            translation_matrix = np.array(
                [[1, 0, tx_N], [0, 1, ty_N]], dtype=np.float32
            )
        elif argomenti_passati_script[1] == "FENDINEBBIA":
            translation_matrix = np.array(
                [[1, 0, tx_F], [0, 1, ty_F]], dtype=np.float32
            )
        else :
            translation_matrix = np.array(
                [[1, 0, 0], [0, 1, 0]], dtype=np.float32
            )

        fr_resized = cv2.resize(
            frame_originale, (WINDOW_WIDTH, WINDOW_HEIGHT), interpolation=cv2.INTER_AREA
        )

        if argomenti_passati_script[1] in ["ANABBAGLIANTE", "FENDINEBBIA"]:
            frame_zom = zoom(fr_resized, 2.000) # 3.000
        elif argomenti_passati_script[1] == "ABBAGLIANTE":
            frame_zom = zoom(fr_resized, 1.000) 

        # apply the translation to the image
        frame_translated = cv2.warpAffine(
            src=frame_zom,
            M=translation_matrix,
            dsize=(WINDOW_WIDTH, WINDOW_HEIGHT),
        )

        #---------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------
        if argomenti_passati_script[1] in ["ANABBAGLIANTE", "FENDINEBBIA"]:
            alpha_anabb = 1 # Contrast control (1.5)
            beta_anabb = 1 # Brightness control (10)
            # call convertScaleAbs function    
            frame_NOT_stretched = cv2.convertScaleAbs(frame_translated, alpha=alpha_anabb, beta=beta_anabb) 
            #---------------------------------
            factor_stretching_Y = 2.500
            altezza, larghezza = frame_NOT_stretched.shape[:2]
            nuova_altezza = int(altezza * factor_stretching_Y)
            frame = cv2.resize(frame_NOT_stretched, (larghezza, nuova_altezza), interpolation=cv2.INTER_LINEAR)
            #---------------------------------
 
        elif argomenti_passati_script[1] == "ABBAGLIANTE":
            alpha_abb = 0.50 # Contrast control (0.5)
            beta_abb = 1 # Brightness control (1)
            # call convertScaleAbs function
            frame = cv2.convertScaleAbs(frame_translated, alpha=alpha_abb, beta=beta_abb)      
        #---------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------

        blurred = cv2.GaussianBlur(
            frame, (Larghezza_filtro_gaussiano, Larghezza_filtro_gaussiano), 0 # (51, 51) # (7, 7)
        )
        gray_image = cv2.cvtColor(blurred, cv2.COLOR_BGR2GRAY)
        frame_cropped = gray_image[0:280, 0:629] # frame_cropped = gray_image[0:260, 0:629] # frame_cropped = frame_resized[start_row:end_row, start_col:end_col]
        (minVal, maxVal, minLoc, maxLoc_tuple) = cv2.minMaxLoc(frame_cropped)

        maxVal_abb = maxVal

        #----------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------
        # Filtraggio passa-basso con medie continue (squadra RC SW) per il punto di massima intensità ottica
        maxLoc_tuple_filtered_x = int( float(maxLoc_tuple[0])*alfa_LPF + float(maxLoc_tuple_prev_x)*(1.0000-alfa_LPF) )
        maxLoc_tuple_prev_x = maxLoc_tuple_filtered_x
        maxLoc_tuple_filtered_y = int( float(maxLoc_tuple[1])*alfa_LPF + float(maxLoc_tuple_prev_y)*(1.0000-alfa_LPF) )
        maxLoc_tuple_prev_y = maxLoc_tuple_filtered_y
        maxLoc = ( maxLoc_tuple_filtered_x, maxLoc_tuple_filtered_y )
        #----------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------



        #---------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------
        if argomenti_passati_script[1] in ["ANABBAGLIANTE", "FENDINEBBIA"]:
            alpha_anabb = 1 # Contrast control (1.5)
            beta_anabb = -100 # Brightness control (10)
            # call convertScaleAbs function    
            gray_image_4color = cv2.convertScaleAbs(gray_image, alpha=alpha_anabb, beta=beta_anabb)  
            if pattern == 2:  # pattern_thermal
                img_color = cv2.applyColorMap(gray_image_4color, cv2.COLORMAP_HSV) # COLORMAP_RAINBOW, COLORMAP_JET
        elif argomenti_passati_script[1] == "ABBAGLIANTE":
            alpha_abb = 3 # Contrast control (0.5)
            beta_abb = -100 # Brightness control (1)
            # call convertScaleAbs function
            gray_image_4color = cv2.convertScaleAbs(gray_image, alpha=alpha_abb, beta=beta_abb)    
            if pattern == 2:  # pattern_thermal
                img_color = cv2.applyColorMap(gray_image_4color, cv2.COLORMAP_RAINBOW) # COLORMAP_RAINBOW, COLORMAP_JET
        #---------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------
        #---------------------------------------------------------------------------------



        #----------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------
        if argomenti_passati_script[1] in ["ANABBAGLIANTE", "FENDINEBBIA"]:

            lumen_accumul = 0
            for y in range( calc_y_sup_finestra_Lux_anabb(), calc_y_inf_finestra_Lux_anabb(), 1 ):
                for x in range( 1, 629, 1 ):
                    lumen_accumul += gray_image[y][x]
            
            lux_25m = int(lumen_accumul/100000) # 100

        elif argomenti_passati_script[1] == "ABBAGLIANTE":

            lux_25m = np.mean( gray_image[ 10:310, 10:620 ] )
        #----------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------
        #----------------------------------------------------------------------------------------------------------------------------------


        # pallino rosso (su pattern_analog) - punto di massima intensità ottica
        if display_croce == 1:
            if pattern == 0:  # pattern_analog
                cv2.circle(frame, maxLoc, 5, (255, 0, 0), 4)
            elif pattern == 1:  # pattern_digital
                cv2.circle(sfondo, maxLoc, 5, (255, 255, 255), 4)
            elif pattern == 2:  # pattern_thermal
                cv2.circle(img_color, maxLoc, 5, (0, 255, 255), 4)

        if argomenti_passati_script[1] in ["ANABBAGLIANTE", "FENDINEBBIA"]: # if (( argomenti_passati_script[1] == "ANABBAGLIANTE" ) or ( argomenti_passati_script[1] == "FENDINEBBIA" )) :
            if display_croce == 1:
                if pattern == 0:  # pattern_analog
                    cv2.line(
                        frame,
                        somma_xy(maxLoc, shift1),
                        somma_xy(maxLoc, shift2),
                        (255, 0, 0),
                        1,
                    )  # croce blu
                    cv2.line(
                        frame,
                        somma_xy(maxLoc, shift3),
                        somma_xy(maxLoc, shift4),
                        (255, 0, 0),
                        1,
                    )  # croce blu
                elif pattern == 1:  # pattern_digital
                    cv2.line(
                        sfondo,
                        somma_xy(maxLoc, shift1),
                        somma_xy(maxLoc, shift2),
                        (255, 255, 255),
                        1,
                    )  # croce blu
                    cv2.line(
                        sfondo,
                        somma_xy(maxLoc, shift3),
                        somma_xy(maxLoc, shift4),
                        (255, 255, 255),
                        1,
                    )  # croce blu
                elif pattern == 2:  # pattern_thermal
                    cv2.line(
                        img_color,
                        somma_xy(maxLoc, shift1),
                        somma_xy(maxLoc, shift2),
                        (0, 255, 255),
                        1,
                    )  # croce blu
                    cv2.line(
                        img_color,
                        somma_xy(maxLoc, shift3),
                        somma_xy(maxLoc, shift4),
                        (0, 255, 255),
                        1,
                    )  # croce blu

            """
            if argomenti_passati_script[1] == "ANABBAGLIANTE":

                cv2.rectangle(
                    frame,
                    (int(Xpx_in), int(Ypx_in)),
                    (int(Xpx_fin), int(Ypx_fin)),
                    (0, 255, 255),
                    2,
                )  # <- qui dentro ci ho raccolto la luce (luminanza)
            """

            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------

            punto1_tmp = calcola_punto1(maxLoc)

            Status_Points_CR = [0,0,0,0,0,0,0]
            punto1_x = punto1_tmp[0]
            punto1_y = punto1_tmp[1]            
            #--------------------------------------------------------------------------------


            if( argomenti_passati_script[1] == "ANABBAGLIANTE" ):


                ##-----------------------------------------------
                ##-----------------------------------------------------------------
                ##-----------------------------------------------

                if( punto1_x>=int(WINDOW_HALF_WIDTH/4) ):

                    if metodo_calc_anabb == 0 :
                        Point1_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/4) )  
                    else:
                        Point1_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/4) )
                    
                    Status_Points_CR[0] = 0
                
                else:

                    if metodo_calc_anabb == 0 :
                        Point1_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH/4)-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH/4) )
                    else:
                        Point1_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH/4)-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH/4) )

                    Status_Points_CR[0] = 1
                

                if( punto1_x>=int(WINDOW_HALF_WIDTH/2) ):

                    if metodo_calc_anabb == 0 :
                        Point2_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/2) ) 
                    else:
                        Point2_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/2) )

                    Status_Points_CR[1] = 0 

                else:

                    if metodo_calc_anabb == 0 :
                        Point2_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH/2)-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH/2) )
                    else:
                        Point2_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH/2)-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH/2) )
                    
                    Status_Points_CR[1] = 1


                if( punto1_x>=int(WINDOW_HALF_WIDTH*(3/4)) ):

                    if metodo_calc_anabb == 0 :
                        Point3_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH*(3/4)) )
                    else:
                        Point3_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH*(3/4)) )

                    Status_Points_CR[2] = 0  

                else:

                    if metodo_calc_anabb == 0 :
                        Point3_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH*(3/4))-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH*(3/4)) )
                    else:
                        Point3_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH*(3/4))-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH*(3/4)) )
                    
                    Status_Points_CR[2] = 1 


                if( punto1_x>=int(WINDOW_HALF_WIDTH) ):

                    if metodo_calc_anabb == 0 :
                        Point4_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH) )  
                    else:
                        Point4_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH) )  

                    Status_Points_CR[3] = 0

                else:

                    if metodo_calc_anabb == 0 :
                        Point4_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH)-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH) ) 
                    else:
                        Point4_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y-( (int)(((float)(int(WINDOW_HALF_WIDTH)-punto1_x))*lin_dem_anabb_coeff_angol) ), int(WINDOW_HALF_WIDTH) )
                    
                    Status_Points_CR[3] = 1


                if( punto1_x>=WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ):

                    if metodo_calc_anabb == 0 :
                        Point5_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )  
                    else:
                        Point5_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )

                    Status_Points_CR[4] = 0

                else:

                    if metodo_calc_anabb == 0 :
                        Point5_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(( WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )-punto1_x))*lin_dem_anabb_coeff_angol) ), WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )
                    else:
                        Point5_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y-( (int)(((float)(( WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )-punto1_x))*lin_dem_anabb_coeff_angol) ), WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )

                    Status_Points_CR[4] = 1


                if( punto1_x>=WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) ):

                    if metodo_calc_anabb == 0 :
                        Point6_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )  
                    else:
                        Point6_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )

                    Status_Points_CR[5] = 0

                else:

                    if metodo_calc_anabb == 0 :
                        Point6_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(( WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )-punto1_x))*lin_dem_anabb_coeff_angol) ), WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )
                    else:
                        Point6_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y-( (int)(((float)(( WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )-punto1_x))*lin_dem_anabb_coeff_angol) ), WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )

                    Status_Points_CR[5] = 1

     
                if( punto1_x>=WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ):

                    if metodo_calc_anabb == 0 :
                        Point7_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) 
                    else:
                        Point7_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) )
                    
                    Status_Points_CR[6] = 0 

                else:

                    if metodo_calc_anabb == 0 :
                        Point7_CR = punto_anab_cr( gray_image, len_window_y, punto1_y-( (int)(((float)(( WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) )-punto1_x))*lin_dem_anabb_coeff_angol) ), WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) )           
                    else:
                        Point7_CR = punto_anab_cr_MAX_Derivata( gray_image, len_window_y, punto1_y-( (int)(((float)(( WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) )-punto1_x))*lin_dem_anabb_coeff_angol) ), WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) )           
                    
                    Status_Points_CR[6] = 1

                ##-----------------------------------------------
                ##-----------------------------------------------------------------
                ##-----------------------------------------------



                #------------------------------------------------------------------------------------------------------------
                # linea di demarcazione gialla:
                # frame_copy = frame
                frame_copy = zoom(frame, 1.000)
                cv2.line(frame_copy, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 255, 0), 2)
                cv2.line(frame_copy, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 255, 0), 2)
                cv2.line(frame_copy, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 255, 0), 2)
                cv2.line(frame_copy, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 255, 0), 2)
                cv2.line(frame_copy, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 255, 0), 2)
                cv2.line(frame_copy, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 255, 0), 2)
                cv2.line(frame_copy, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 255, 0), 2)
                cv2.line(frame_copy, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 255, 0), 2)
                #------------------------------------------------------------------------------------------------------------

                def computo_estremo_sup(y_media, y_hight):
                    if( (y_media - y_hight) >= 0):
                        return y_media - y_hight
                    else: # < 0
                        return 0

                def computo_estremo_inf(y_media, y_hight):
                    if( (y_media + y_hight) < 315):
                        return y_media + y_hight
                    else: # >= 315
                        return 315

                passox = 15
                finestra = 50
                derivata_minima = 1000.00 # derivata_minima = massima negativa
                derivata_curr = 0
                y_prev = Point1_CR[1]
                y_curr = 0
                punto_di_massima_derivata_x = WINDOW_HALF_WIDTH
                punto_di_massima_derivata_y = WINDOW_HALF_HEIGHT
                punto_di_massima_derivata = (punto_di_massima_derivata_x, punto_di_massima_derivata_y)
                for x in range( Point1_CR[0]+passox, Point7_CR[0]+1, passox):
                    for y in range(  computo_estremo_sup(maxLoc[1], finestra) , computo_estremo_inf(maxLoc[1], finestra) , 1):
                        if( (frame_copy[y][x][0] == 255) and (frame_copy[y][x][1] == 255) and (frame_copy[y][x][2] == 0) ): # se giallo puro trovato
                            y_curr = y
                            derivata_curr = float(y_curr - y_prev)/float(passox)
                            if(derivata_curr < derivata_minima):
                                derivata_minima = derivata_curr
                                punto_di_massima_derivata_x = x
                                punto_di_massima_derivata_y = y
                                punto_di_massima_derivata = (punto_di_massima_derivata_x, punto_di_massima_derivata_y)
                            y_prev = y_curr 
                
                # cv2.circle(frame, punto_di_massima_derivata, 5, (255, 255, 0), 3)
                delta_y_min = 0
                finestra = 100
                sigma = 3 # 5
                passox_rollback = -2*sigma
                xc = punto_di_massima_derivata[0]
                ya = punto_di_massima_derivata[1]
                yb = punto_di_massima_derivata[1]
                yc = punto_di_massima_derivata[1]

                for xc in range( punto_di_massima_derivata[0]+passox_rollback, 20, passox_rollback ):
                    xa = xc - sigma
                    xb = xc + sigma
                    for y in range( punto_di_massima_derivata[1], computo_estremo_inf(punto_di_massima_derivata[1], finestra), 1 ):
                        if( (frame_copy[y][xa][0] == 255) and (frame_copy[y][xa][1] == 255) and (frame_copy[y][xa][2] == 0) ): # se giallo puro trovato
                            ya = y
                            break;
                    for y in range( punto_di_massima_derivata[1], computo_estremo_inf(punto_di_massima_derivata[1], finestra), 1 ):
                        if( (frame_copy[y][xb][0] == 255) and (frame_copy[y][xb][1] == 255) and (frame_copy[y][xb][2] == 0) ): # se giallo puro trovato
                            yb = y
                            break;
                    if( (abs(ya - yb)) <= delta_y_min ):
                        break;
                
                for y in range( punto_di_massima_derivata[1], computo_estremo_inf(punto_di_massima_derivata[1], finestra), 1 ):
                    if( (frame_copy[y][xc][0] == 255) and (frame_copy[y][xc][1] == 255) and (frame_copy[y][xc][2] == 0) ): # se giallo puro trovato
                        yc = y
                        break;

                punto_centrale_anabb = (xc, yc)

                # cv2.circle(frame, punto_centrale_anabb, 5, (0, 255, 255), 3)        # ciano
                # cv2.circle(frame, punto_di_massima_derivata, 5, (255, 255, 0), 3)   # giallo <----

                # Filtraggio X passa-basso con medie continue (squadra RC SW) per il punto centrale / punto angoloso (punto ciano)
                Xc_float = (float(punto_centrale_anabb[0]))*alfa_LPF + Xc_prev*(1.0000-alfa_LPF)
                Xc_prev = Xc_float
                Xc_curr = int( Xc_float )

                # Filtraggio Y passa-basso con medie continue (squadra RC SW) per il punto centrale / punto angoloso (punto ciano)
                Yc_float = (float(punto_centrale_anabb[1]))*alfa_LPF + Yc_prev*(1.0000-alfa_LPF)
                Yc_prev = Yc_float
                Yc_curr = int( Yc_float )

                punto1 = (Xc_curr, Yc_curr)



                """
                lista_punti = [ Point1_CR, Point2_CR, Point3_CR, Point4_CR, Point5_CR, Point6_CR, Point7_CR ]

                data_orizz = []
                data_inclin = []

                for p in range( 0, 6+1, 1):
                    if( Status_Points_CR[p] == 0 ) : # punti blu
                        data_orizz.append( lista_punti[p] )
                    else :                           # punti gialli
                        data_inclin.append( lista_punti[p] )

                coefficienti_orizz = minimi_quadrati(data_orizz)
                Coefficiente_angolare_orizz = coefficienti_orizz[0]
                Termine_noto_orizz = coefficienti_orizz[1]

                coefficienti_inclin = minimi_quadrati(data_inclin)
                Coefficiente_angolare_inclin = coefficienti_inclin[0]
                Termine_noto_inclin = coefficienti_inclin[1]

                try :
                    Xpoint_intersezione_2_rette_float_curr = (Termine_noto_orizz - Termine_noto_inclin)/(Coefficiente_angolare_inclin - Coefficiente_angolare_orizz)
                except ZeroDivisionError :
                    Xpoint_intersezione_2_rette_float_curr = float(WINDOW_HALF_WIDTH)

                # Filtraggio passa-basso con medie continue (squadra RC SW) per il punto centrale / punto angoloso (punto blu)
                Xpoint_intersezione_2_rette_float = Xpoint_intersezione_2_rette_float_curr*alfa_LPF + Xpoint_intersezione_2_rette_float_prev*(1.0000-alfa_LPF)
                Xpoint_intersezione_2_rette_float_prev = Xpoint_intersezione_2_rette_float
                Xpoint_intersezione_2_rette = int( Xpoint_intersezione_2_rette_float )


                array_posizY = [ Point1_CR[1], Point2_CR[1], Point3_CR[1], Point4_CR[1], Point5_CR[1], Point6_CR[1], Point7_CR[1] ] # [y]
                # array_posizX = [ Point1_CR[0], Point2_CR[0], Point3_CR[0], Point4_CR[0], Point5_CR[0], Point6_CR[0], Point7_CR[0] ] # [x]

                num_punt = 1
                pos_y_pnt = Point1_CR[1] # [y]

                for p in range( 1, 6+1, 1):
                    if( Status_Points_CR[p] == 0 ):
                        num_punt = num_punt + 1
                        pos_y_pnt = pos_y_pnt + array_posizY[p]
                    else:
                        offset_punto_blu = 0
                        punto1 = ( Xpoint_intersezione_2_rette + offset_punto_blu, int((float(pos_y_pnt))/((float(num_punt)))) ) # <<-----------
                        break
                """




                if pattern == 0 :     # pattern_analog

                    cv2.line(frame, (punto1[0]-5, punto1[1] ), ( punto1[0]+5, punto1[1] ), (0, 255, 255), 3)   # ciano
                    cv2.line(frame, ( punto1[0], punto1[1]-5 ), ( punto1[0], punto1[1]+5 ), (0, 255, 255), 3)  # ciano
                    cv2.circle(frame, punto1, 5, (0, 255, 255), 3)                                             # ciano

                    if banda_calc_anabb_visibile == 1 :

                        # calcolo della linea di sopra:
                        banda_calc_anabb_p1_sopra = ( 5, punto1_y - len_window_y ) 
                        banda_calc_anabb_p2_sopra = ( punto1_x, punto1_y - len_window_y ) 
                        banda_calc_anabb_p3_sopra = ( 630, punto1_y - len_window_y - int(lin_dem_anabb_coeff_angol*(float(630-punto1_x))) )
                        # calcolo della linea di sotto:
                        banda_calc_anabb_p1_sotto = ( 5, (punto1_y - len_window_y) + 2*len_window_y ) 
                        banda_calc_anabb_p2_sotto = ( punto1_x, (punto1_y - len_window_y) + 2*len_window_y ) 
                        banda_calc_anabb_p3_sotto = ( 630, (punto1_y - len_window_y - int(lin_dem_anabb_coeff_angol*(float(630-punto1_x)))) + 2*len_window_y )
                        centro_banda_calc_anabb = ( punto1_x , punto1_y )
                        # display della banda:
                        cv2.line(frame, (banda_calc_anabb_p1_sopra[0], banda_calc_anabb_p1_sopra[1] ), ( banda_calc_anabb_p2_sopra[0], banda_calc_anabb_p2_sopra[1] ), (139,69,19), 2) # saddlebrown
                        cv2.line(frame, (banda_calc_anabb_p2_sopra[0], banda_calc_anabb_p2_sopra[1] ), ( banda_calc_anabb_p3_sopra[0], banda_calc_anabb_p3_sopra[1] ), (139,69,19), 2) # saddlebrown
                        cv2.line(frame, (banda_calc_anabb_p1_sotto[0], banda_calc_anabb_p1_sotto[1] ), ( banda_calc_anabb_p2_sotto[0], banda_calc_anabb_p2_sotto[1] ), (139,69,19), 2) # saddlebrown
                        cv2.line(frame, (banda_calc_anabb_p2_sotto[0], banda_calc_anabb_p2_sotto[1] ), ( banda_calc_anabb_p3_sotto[0], banda_calc_anabb_p3_sotto[1] ), (139,69,19), 2) # saddlebrown                        
                        cv2.circle(frame, centro_banda_calc_anabb, 5, (139,69,19), 3) # saddlebrown


                elif pattern == 1 :   # pattern_digital
                    cv2.line(sfondo, (punto1[0]-5, punto1[1] ), ( punto1[0]+5, punto1[1] ), (255, 255, 0), 3)
                    cv2.line(sfondo, ( punto1[0], punto1[1]-5 ), ( punto1[0], punto1[1]+5 ), (255, 255, 0), 3)
                    cv2.circle(sfondo, punto1, 5, (255, 255, 0), 3)

                elif pattern == 2 :   # pattern_thermal
                    cv2.line(img_color, (punto1[0]-5, punto1[1] ), ( punto1[0]+5, punto1[1] ), (255, 255, 255), 3)
                    cv2.line(img_color, ( punto1[0], punto1[1]-5 ), ( punto1[0], punto1[1]+5 ), (255, 255, 255), 3)
                    cv2.circle(img_color, punto1, 5, (255, 255, 255), 3)


                """
                if display_none_croci_linee_anabb == 1 : # solo le croci
                    display_croci_anabb( frame, Point1_CR, Point2_CR, Point3_CR, Point4_CR, Point5_CR, Point6_CR, Point7_CR, Status_Points_CR )
                elif display_none_croci_linee_anabb == 2 : # solo le linee 
                    display_linee_anabb( frame, Coefficiente_angolare_orizz, Termine_noto_orizz, Coefficiente_angolare_inclin, Termine_noto_inclin, WINDOW_WIDTH )        
                elif display_none_croci_linee_anabb == 3 : # sia croci che linee
                    display_croci_anabb( frame, Point1_CR, Point2_CR, Point3_CR, Point4_CR, Point5_CR, Point6_CR, Point7_CR, Status_Points_CR )
                    display_linee_anabb( frame, Coefficiente_angolare_orizz, Termine_noto_orizz, Coefficiente_angolare_inclin, Termine_noto_inclin, WINDOW_WIDTH )
                """


            elif( argomenti_passati_script[1] == "FENDINEBBIA" ):

                Point1_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/4) )
                Point2_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH/2) )
                Point3_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH*(3/4)) )
                Point4_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, int(WINDOW_HALF_WIDTH) )
                Point5_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )
                Point6_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )
                Point7_CR = punto_anab_cr( gray_image, len_window_y, punto1_y, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) 

                num_punt = 1
                pos_y_pnt = Point1_CR[1] # [y]

                array_posizY = [ Point1_CR[1], Point2_CR[1], Point3_CR[1], Point4_CR[1], Point5_CR[1], Point6_CR[1], Point7_CR[1] ] # [y]

                for p in range( 1, 6+1, 1):
                    num_punt = num_punt + 1
                    pos_y_pnt = pos_y_pnt + array_posizY[p]

                punto1 = ( punto1_x, int((float(pos_y_pnt))/((float(num_punt)))) )

                cv2.line(frame, (punto1[0]-5, punto1[1] ), ( punto1[0]+5, punto1[1] ), (0, 255, 255), 3)   # ciano
                cv2.line(frame, ( punto1[0], punto1[1]-5 ), ( punto1[0], punto1[1]+5 ), (0, 255, 255), 3)  # ciano
                cv2.circle(frame, punto1, 5, (0, 255, 255), 3)                                             # ciano




            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------
            #--------------------------------------------------------------------------------


            # punto1 = calcola_punto1(maxLoc)
            # punto2 = calcola_punto2(punto1)
            # punto3 = calcola_punto3(punto1)

            posiz_pattern_x = punto1[0]
            posiz_pattern_y = punto1[1]
                
            if ( argomenti_passati_script[1] == "ANABBAGLIANTE" ) : # tol
                valutazione_vero_falso1 = ( (punto1[0]<(WINDOW_HALF_WIDTH+tolH)) and (punto1[0]>(WINDOW_HALF_WIDTH-tolH)) ) and ( (punto1[1]<(WINDOW_HALF_HEIGHT+inclinazione_pixel_panel+tolV)) and (punto1[1]>(WINDOW_HALF_HEIGHT+inclinazione_pixel_panel-tolV)) ) 
            elif ( argomenti_passati_script[1] == "FENDINEBBIA" ) :
                valutazione_vero_falso1 = ( (punto1[1]<(WINDOW_HALF_HEIGHT+inclinazione_pixel_panel+tolV)) and (punto1[1]>(WINDOW_HALF_HEIGHT+inclinazione_pixel_panel-tolV)) )



            if valutazione_vero_falso1:
                if pattern == 0:  # pattern_analog
                    # ANALOGICO
                    # linea di demarcazione DENTRO la tolleranza
                    if linea_demarcazione_anabbagliante_invisibile == 0 :


                        if ( ( punto1[0] > int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                            cv2.line(frame, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                        elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH/2) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH) ) ):
                            cv2.line(frame, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                        elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH*(3/4)) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) ):
                            cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                        elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) ) ):
                            cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                        elif ( ( punto1[0] > WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                            cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                            cv2.line(frame, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (0, 255, 0), 4)


                        """
                        # cv2.line(frame, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (0, 255, 0), 4)
                        cv2.line(frame, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                        cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                        cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                        cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                        cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                        cv2.line(frame, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                        # cv2.line(frame, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (0, 255, 0), 4)
                        """

                        # cv2.putText(frame, "ANABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)

                elif pattern == 1:  # pattern_digital
                    # DIGITALE
                    # linea di demarcazione DENTRO la tolleranza

                    if ( ( punto1[0] > int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                        cv2.line(sfondo, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH/2) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH) ) ):
                        cv2.line(sfondo, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH*(3/4)) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) ):
                        cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) ) ):
                        cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                    elif ( ( punto1[0] > WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                        cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                        cv2.line(sfondo, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (0, 255, 0), 4)

                    """
                    # cv2.line(sfondo, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                    cv2.line(sfondo, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                    # cv2.line(sfondo, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (0, 255, 0), 4)
                    """

                    # cv2.putText(sfondo, "ANABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)

                elif pattern == 2:  # pattern_thermal
                    # TERMICO
                    # linea di demarcazione DENTRO la tolleranza

                    if ( ( punto1[0] > int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                        cv2.line(img_color, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH/2) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH) ) ):
                        cv2.line(img_color, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH*(3/4)) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) ):
                        cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) ) ):
                        cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                    elif ( ( punto1[0] > WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                        cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                        cv2.line(img_color, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (0, 255, 0), 4)

                    """
                    # cv2.line(img_color, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (0, 255, 0), 4)
                    cv2.line(img_color, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (0, 255, 0), 4)
                    # cv2.line(img_color, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (0, 255, 0), 4)
                    """

                    # cv2.putText(img_color, "ANABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)

            else:
                if pattern == 0:  # pattern_analog
                    # ANALOGICO
                    # linea di demarcazione FUORI la tolleranza
                    if linea_demarcazione_anabbagliante_invisibile == 0 :

                        if ( ( punto1[0] > int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                            cv2.line(frame, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                        elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH/2) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH) ) ):
                            cv2.line(frame, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                        elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH*(3/4)) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) ):
                            cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                        elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) ) ):
                            cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                        elif ( ( punto1[0] > WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                            cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                            cv2.line(frame, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 0, 0), 4)

                        """
                        # cv2.line(frame, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 0, 0), 4)
                        cv2.line(frame, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                        cv2.line(frame, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                        cv2.line(frame, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                        cv2.line(frame, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                        cv2.line(frame, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                        cv2.line(frame, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                        # cv2.line(frame, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 0, 0), 4)
                        """

                        # cv2.putText(frame, "ANABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)

                elif pattern == 1:  # pattern_digital
                    # DIGITALE
                    # linea di demarcazione FUORI la tolleranza

                    if ( ( punto1[0] > int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                        cv2.line(sfondo, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH/2) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH) ) ):
                        cv2.line(sfondo, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH*(3/4)) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) ):
                        cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) ) ):
                        cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                    elif ( ( punto1[0] > WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                        cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                        cv2.line(sfondo, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 0, 0), 4)

                    """
                    # cv2.line(sfondo, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                    cv2.line(sfondo, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                    # cv2.line(sfondo, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 0, 0), 4)
                    """
                
                    # cv2.putText(sfondo, "ANABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)

                elif pattern == 2:  # pattern_thermal
                    # TERMICO
                    # linea di demarcazione FUORI la tolleranza

                    if ( ( punto1[0] > int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                        cv2.line(img_color, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH/2) ) and ( punto1[0] <= int(WINDOW_HALF_WIDTH) ) ):
                        cv2.line(img_color, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH*(3/4)) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) ):
                        cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                    elif ( ( punto1[0] > int(WINDOW_HALF_WIDTH) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) ) ):
                        cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                    elif ( ( punto1[0] > WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) ) and ( punto1[0] <= WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH*(3/4)) ) ):
                        cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                        cv2.line(img_color, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 0, 0), 4)

                    """
                    # cv2.line(img_color, ( 0, Point1_CR[1] ), ( Point1_CR[0], Point1_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point1_CR[0], Point1_CR[1] ), ( Point2_CR[0], Point2_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point2_CR[0], Point2_CR[1] ), ( Point3_CR[0], Point3_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point3_CR[0], Point3_CR[1] ), ( Point4_CR[0], Point4_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point4_CR[0], Point4_CR[1] ), ( Point5_CR[0], Point5_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point5_CR[0], Point5_CR[1] ), ( Point6_CR[0], Point6_CR[1] ), (255, 0, 0), 4)
                    cv2.line(img_color, ( Point6_CR[0], Point6_CR[1] ), ( Point7_CR[0], Point7_CR[1] ), (255, 0, 0), 4)
                    # cv2.line(img_color, ( Point7_CR[0], Point7_CR[1] ), ( 630, Point7_CR[1] ), (255, 0, 0), 4)
                    """

                    # cv2.putText(img_color, "ANABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)





        elif argomenti_passati_script[1] == "ABBAGLIANTE":

            """
            cv2.rectangle(
                frame,
                (int(Xpx_in_ABB), int(Ypx_in_ABB)),
                (int(Xpx_fin_ABB), int(Ypx_fin_ABB)),
                (0, 255, 255),
                2,
            )  # <- qui dentro ci ho raccolto la luce (luminanza)
            """



            # valutazione della linea orizzontale centrale dell'abbagliante
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            Point1_ABB_up_CR = punto_Abb_up_VERT( gray_image, int(WINDOW_HALF_WIDTH/2) )
            Point1_ABB_down_CR = punto_Abb_dwn_VERT( gray_image, int(WINDOW_HALF_WIDTH/2) )
            Point1_ABB_media_CR = ( int((Point1_ABB_up_CR[0]+Point1_ABB_down_CR[0])/2) , int((Point1_ABB_up_CR[1]+Point1_ABB_down_CR[1])/2) )

            Point2_ABB_up_CR = punto_Abb_up_VERT( gray_image, int(WINDOW_HALF_WIDTH*(3/4)) )
            Point2_ABB_down_CR = punto_Abb_dwn_VERT( gray_image, int(WINDOW_HALF_WIDTH*(3/4)) )
            Point2_ABB_media_CR = ( int((Point2_ABB_up_CR[0]+Point2_ABB_down_CR[0])/2) , int((Point2_ABB_up_CR[1]+Point2_ABB_down_CR[1])/2) )

            Point3_ABB_up_CR = punto_Abb_up_VERT( gray_image, WINDOW_HALF_WIDTH )
            Point3_ABB_down_CR = punto_Abb_dwn_VERT( gray_image, WINDOW_HALF_WIDTH )
            Point3_ABB_media_CR = ( int((Point3_ABB_up_CR[0]+Point3_ABB_down_CR[0])/2) , int((Point3_ABB_up_CR[1]+Point3_ABB_down_CR[1])/2) )

            Point4_ABB_up_CR = punto_Abb_up_VERT( gray_image, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )
            Point4_ABB_down_CR = punto_Abb_dwn_VERT( gray_image, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/4) )
            Point4_ABB_media_CR = ( int((Point4_ABB_up_CR[0]+Point4_ABB_down_CR[0])/2) , int((Point4_ABB_up_CR[1]+Point4_ABB_down_CR[1])/2) )

            Point5_ABB_up_CR = punto_Abb_up_VERT( gray_image, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )
            Point5_ABB_down_CR = punto_Abb_dwn_VERT( gray_image, WINDOW_HALF_WIDTH+int(WINDOW_HALF_WIDTH/2) )
            Point5_ABB_media_CR = ( int((Point5_ABB_up_CR[0]+Point5_ABB_down_CR[0])/2) , int((Point5_ABB_up_CR[1]+Point5_ABB_down_CR[1])/2) )

            #---------------------

            cv2.line(frame, (Point1_ABB_up_CR[0]-10, Point1_ABB_up_CR[1] ), ( Point1_ABB_up_CR[0]+10, Point1_ABB_up_CR[1] ), (255,215,0), 3) # gold
            cv2.line(frame, ( Point1_ABB_up_CR[0], Point1_ABB_up_CR[1]-10 ), ( Point1_ABB_up_CR[0], Point1_ABB_up_CR[1]+10 ), (255,215,0), 3) # gold  
            cv2.line(frame, (Point1_ABB_down_CR[0]-10, Point1_ABB_down_CR[1] ), ( Point1_ABB_down_CR[0]+10, Point1_ABB_down_CR[1] ), (255,215,0), 3) # gold
            cv2.line(frame, ( Point1_ABB_down_CR[0], Point1_ABB_down_CR[1]-10 ), ( Point1_ABB_down_CR[0], Point1_ABB_down_CR[1]+10 ), (255,215,0), 3) # gold

            cv2.line(frame, (Point2_ABB_up_CR[0]-10, Point2_ABB_up_CR[1] ), ( Point2_ABB_up_CR[0]+10, Point2_ABB_up_CR[1] ), (255,215,0), 3)
            cv2.line(frame, ( Point2_ABB_up_CR[0], Point2_ABB_up_CR[1]-10 ), ( Point2_ABB_up_CR[0], Point2_ABB_up_CR[1]+10 ), (255,215,0), 3)    
            cv2.line(frame, (Point2_ABB_down_CR[0]-10, Point2_ABB_down_CR[1] ), ( Point2_ABB_down_CR[0]+10, Point2_ABB_down_CR[1] ), (255,215,0), 3)
            cv2.line(frame, ( Point2_ABB_down_CR[0], Point2_ABB_down_CR[1]-10 ), ( Point2_ABB_down_CR[0], Point2_ABB_down_CR[1]+10 ), (255,215,0), 3)

            cv2.line(frame, (Point3_ABB_up_CR[0]-10, Point3_ABB_up_CR[1] ), ( Point3_ABB_up_CR[0]+10, Point3_ABB_up_CR[1] ), (255,215,0), 3)
            cv2.line(frame, ( Point3_ABB_up_CR[0], Point3_ABB_up_CR[1]-10 ), ( Point3_ABB_up_CR[0], Point3_ABB_up_CR[1]+10 ), (255,215,0), 3)    
            cv2.line(frame, (Point3_ABB_down_CR[0]-10, Point3_ABB_down_CR[1] ), ( Point3_ABB_down_CR[0]+10, Point3_ABB_down_CR[1] ), (255,215,0), 3)
            cv2.line(frame, ( Point3_ABB_down_CR[0], Point3_ABB_down_CR[1]-10 ), ( Point3_ABB_down_CR[0], Point3_ABB_down_CR[1]+10 ), (255,215,0), 3)

            cv2.line(frame, (Point4_ABB_up_CR[0]-10, Point4_ABB_up_CR[1] ), ( Point4_ABB_up_CR[0]+10, Point4_ABB_up_CR[1] ), (255,215,0), 3)
            cv2.line(frame, ( Point4_ABB_up_CR[0], Point4_ABB_up_CR[1]-10 ), ( Point4_ABB_up_CR[0], Point4_ABB_up_CR[1]+10 ), (255,215,0), 3)    
            cv2.line(frame, (Point4_ABB_down_CR[0]-10, Point4_ABB_down_CR[1] ), ( Point4_ABB_down_CR[0]+10, Point4_ABB_down_CR[1] ), (255,215,0), 3)
            cv2.line(frame, ( Point4_ABB_down_CR[0], Point4_ABB_down_CR[1]-10 ), ( Point4_ABB_down_CR[0], Point4_ABB_down_CR[1]+10 ), (255,215,0), 3)
            
            cv2.line(frame, (Point5_ABB_up_CR[0]-10, Point5_ABB_up_CR[1] ), ( Point5_ABB_up_CR[0]+10, Point5_ABB_up_CR[1] ), (255,215,0), 3)
            cv2.line(frame, ( Point5_ABB_up_CR[0], Point5_ABB_up_CR[1]-10 ), ( Point5_ABB_up_CR[0], Point5_ABB_up_CR[1]+10 ), (255,215,0), 3)    
            cv2.line(frame, (Point5_ABB_down_CR[0]-10, Point5_ABB_down_CR[1] ), ( Point5_ABB_down_CR[0]+10, Point5_ABB_down_CR[1] ), (255,215,0), 3)
            cv2.line(frame, ( Point5_ABB_down_CR[0], Point5_ABB_down_CR[1]-10 ), ( Point5_ABB_down_CR[0], Point5_ABB_down_CR[1]+10 ), (255,215,0), 3)

            posiz_pattern_y = int(( Point1_ABB_media_CR[1] + Point2_ABB_media_CR[1] + Point3_ABB_media_CR[1] + Point4_ABB_media_CR[1] + Point5_ABB_media_CR[1] )/5)

            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------



            # valutazione della linea verticale centrale dell'abbagliante
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------

            Point1_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, int(WINDOW_HALF_HEIGHT/2) )
            Point1_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, int(WINDOW_HALF_HEIGHT/2) )
            Point1_ABB_media_Hh = ( int((Point1_ABB_up_Hh[0]+Point1_ABB_down_Hh[0])/2) , int((Point1_ABB_up_Hh[1]+Point1_ABB_down_Hh[1])/2) )

            Point2_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, int(WINDOW_HALF_HEIGHT*(3/4)) )
            Point2_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, int(WINDOW_HALF_HEIGHT*(3/4)) )
            Point2_ABB_media_Hh = ( int((Point2_ABB_up_Hh[0]+Point2_ABB_down_Hh[0])/2) , int((Point2_ABB_up_Hh[1]+Point2_ABB_down_Hh[1])/2) )

            Point3_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, WINDOW_HALF_HEIGHT )
            Point3_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, WINDOW_HALF_HEIGHT )
            Point3_ABB_media_Hh = ( int((Point3_ABB_up_Hh[0]+Point3_ABB_down_Hh[0])/2) , int((Point3_ABB_up_Hh[1]+Point3_ABB_down_Hh[1])/2) )

            Point4_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, WINDOW_HALF_HEIGHT+int(WINDOW_HALF_HEIGHT/4) )
            Point4_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, WINDOW_HALF_HEIGHT+int(WINDOW_HALF_HEIGHT/4) )
            Point4_ABB_media_Hh = ( int((Point4_ABB_up_Hh[0]+Point4_ABB_down_Hh[0])/2) , int((Point4_ABB_up_Hh[1]+Point4_ABB_down_Hh[1])/2) )

            Point5_ABB_up_Hh = punto_Abb_up_ORIZ( gray_image, WINDOW_HALF_HEIGHT+int(WINDOW_HALF_HEIGHT/2) )
            Point5_ABB_down_Hh = punto_Abb_dwn_ORIZ( gray_image, WINDOW_HALF_HEIGHT+int(WINDOW_HALF_HEIGHT/2) )
            Point5_ABB_media_Hh = ( int((Point5_ABB_up_Hh[0]+Point5_ABB_down_Hh[0])/2) , int((Point5_ABB_up_Hh[1]+Point5_ABB_down_Hh[1])/2) )

            #---------------------

            cv2.line(frame, (Point1_ABB_up_Hh[0]-10, Point1_ABB_up_Hh[1] ), ( Point1_ABB_up_Hh[0]+10, Point1_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point1_ABB_up_Hh[0], Point1_ABB_up_Hh[1]-10 ), ( Point1_ABB_up_Hh[0], Point1_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point1_ABB_down_Hh[0]-10, Point1_ABB_down_Hh[1] ), ( Point1_ABB_down_Hh[0]+10, Point1_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point1_ABB_down_Hh[0], Point1_ABB_down_Hh[1]-10 ), ( Point1_ABB_down_Hh[0], Point1_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)

            cv2.line(frame, (Point2_ABB_up_Hh[0]-10, Point2_ABB_up_Hh[1] ), ( Point2_ABB_up_Hh[0]+10, Point2_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point2_ABB_up_Hh[0], Point2_ABB_up_Hh[1]-10 ), ( Point2_ABB_up_Hh[0], Point2_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point2_ABB_down_Hh[0]-10, Point2_ABB_down_Hh[1] ), ( Point2_ABB_down_Hh[0]+10, Point2_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point2_ABB_down_Hh[0], Point2_ABB_down_Hh[1]-10 ), ( Point2_ABB_down_Hh[0], Point2_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)

            cv2.line(frame, (Point3_ABB_up_Hh[0]-10, Point3_ABB_up_Hh[1] ), ( Point3_ABB_up_Hh[0]+10, Point3_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point3_ABB_up_Hh[0], Point3_ABB_up_Hh[1]-10 ), ( Point3_ABB_up_Hh[0], Point3_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point3_ABB_down_Hh[0]-10, Point3_ABB_down_Hh[1] ), ( Point3_ABB_down_Hh[0]+10, Point3_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point3_ABB_down_Hh[0], Point3_ABB_down_Hh[1]-10 ), ( Point3_ABB_down_Hh[0], Point3_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)

            cv2.line(frame, (Point4_ABB_up_Hh[0]-10, Point4_ABB_up_Hh[1] ), ( Point4_ABB_up_Hh[0]+10, Point4_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point4_ABB_up_Hh[0], Point4_ABB_up_Hh[1]-10 ), ( Point4_ABB_up_Hh[0], Point4_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point4_ABB_down_Hh[0]-10, Point4_ABB_down_Hh[1] ), ( Point4_ABB_down_Hh[0]+10, Point4_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point4_ABB_down_Hh[0], Point4_ABB_down_Hh[1]-10 ), ( Point4_ABB_down_Hh[0], Point4_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)
            
            cv2.line(frame, (Point5_ABB_up_Hh[0]-10, Point5_ABB_up_Hh[1] ), ( Point5_ABB_up_Hh[0]+10, Point5_ABB_up_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point5_ABB_up_Hh[0], Point5_ABB_up_Hh[1]-10 ), ( Point5_ABB_up_Hh[0], Point5_ABB_up_Hh[1]+10 ), (0, 0, 255), 3)    
            cv2.line(frame, (Point5_ABB_down_Hh[0]-10, Point5_ABB_down_Hh[1] ), ( Point5_ABB_down_Hh[0]+10, Point5_ABB_down_Hh[1] ), (0, 0, 255), 3)
            cv2.line(frame, ( Point5_ABB_down_Hh[0], Point5_ABB_down_Hh[1]-10 ), ( Point5_ABB_down_Hh[0], Point5_ABB_down_Hh[1]+10 ), (0, 0, 255), 3)

            posiz_pattern_x = int(( Point1_ABB_media_Hh[0] + Point2_ABB_media_Hh[0] + Point3_ABB_media_Hh[0] + Point4_ABB_media_Hh[0] + Point5_ABB_media_Hh[0] )/5)

            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            #------------------------------------------------------------------------------------------------------------------------------------------------------------------------
            


            if (
                (posiz_pattern_x < (WINDOW_HALF_WIDTH + tolH))
                and (posiz_pattern_x > (WINDOW_HALF_WIDTH - tolH))
            ) and (
                (posiz_pattern_y < (WINDOW_HALF_HEIGHT + inclinazione_pixel_panel + tolV))
                and (posiz_pattern_y > (WINDOW_HALF_HEIGHT + inclinazione_pixel_panel - tolV))
            ):
                if pattern == 0:  # pattern_analog
                    # ANALOGICO
                    # linea di demarcazione DENTRO la tolleranza
                    cv2.line(
                        frame,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (0, 255, 0),
                        2,
                    )  
                    cv2.line(
                        frame,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (0, 255, 0),
                        2,
                    )  
                    # cv2.putText(frame, "ABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)
                elif pattern == 1:  # pattern_digital
                    # DIGITALE
                    # linea di demarcazione DENTRO la tolleranza
                    cv2.line(
                        sfondo,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (0, 255, 0),
                        4,
                    )
                    cv2.line(
                        sfondo,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (0, 255, 0),
                        2,
                    ) 
                    # cv2.putText(sfondo, "ABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)
                elif pattern == 2:  # pattern_thermal
                    # TERMICO
                    # linea di demarcazione DENTRO la tolleranza
                    cv2.line(
                        img_color,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (0, 255, 0),
                        4,
                    )
                    cv2.line(
                        img_color,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (0, 255, 0),
                        2,
                    ) 
                    # cv2.putText(img_color, "ABBAGLIANTE CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,255,0), 2)

            else:
                if pattern == 0:  # pattern_analog
                    # ANALOGICO
                    # linea di demarcazione FUORI la tolleranza
                    cv2.line(
                        frame,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (255, 0, 0),
                        2,
                    ) 
                    cv2.line(
                        frame,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (255, 0, 0),
                        2,
                    )  
                    # cv2.putText(frame, "ABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)
                elif pattern == 1:  # pattern_digital
                    # DIGITALE
                    # linea di demarcazione FUORI la tolleranza
                    cv2.line(
                        sfondo,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (255, 0, 0),
                        4,
                    )
                    cv2.line(
                        sfondo,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (255, 0, 0),
                        2,
                    )  
                    # cv2.putText(sfondo, "ABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)
                elif pattern == 2:  # pattern_thermal
                    # TERMICO
                    # linea di demarcazione FUORI la tolleranza
                    cv2.line(
                        img_color,
                        (5, posiz_pattern_y),
                        (625, posiz_pattern_y),
                        (255, 0, 0), # (255, 255, 255)
                        4,
                    )
                    cv2.line(
                        img_color,
                        (posiz_pattern_x, 5),
                        (posiz_pattern_x, 315),
                        (255, 0, 0),
                        2,
                    )  
                    # cv2.putText(img_color, "ABBAGLIANTE NON CENTRATO", (20,30-5), cv2.FONT_ITALIC, 0.75, (0,0,255), 2)

        if pattern == 0:  # pattern_analog
            display_griglia_HV(frame)
        elif pattern == 2:  # pattern_thermal
            display_griglia_HV3(img_color)

        if pattern == 0:  # pattern_analog
            display_scala_graduata_frame(frame)
            frame_to_show = frame
        elif pattern == 1:  # pattern_digital
            display_scala_graduata_sfondo(sfondo)
            frame_to_show = sfondo
        elif pattern == 2:  # pattern_thermal
            display_scala_graduata_thermal(img_color)
            frame_to_show = img_color

        cv2.imwrite("/tmp/frame_to_show.png", frame_to_show)

        img = PIL.Image.fromarray(frame_to_show)
        imgtk = ImageTk.PhotoImage(image=img)
        lmain.imgtk = imgtk
        lmain.configure(image=imgtk)
        lmain.after(100, show_frame) # ogni 100ms itera a loop il corpo di "show_frame"


    show_frame()
    root.mainloop()

    chiudi_programma(video)

import os
import time

import cv2
import logging
import numpy as np
from utils import disegna_rettangolo, get_colore

def apri_camera():
    for i in range(11):
        video = cv2.VideoCapture(i)
        if video.isOpened():
            return i, video

    return None, None


def set_camera(i, config):
    logging.info(f"set_camera /dev/video{i}")
    try:
        #os.system(f"v4l2-ctl --device /dev/video{i} --set-ctrl=exposure_auto={config['exposure_auto']}")
        os.system(f"v4l2-ctl --device /dev/video{i} --set-ctrl=brightness={config['brightness']}")
        os.system(f"v4l2-ctl --device /dev/video{i} --set-ctrl=contrast={config['contrast']}")
        os.system(f"v4l2-ctl --device /dev/video{i} --set-ctrl=saturation={config['saturation']}")
        os.system(f"v4l2-ctl --device /dev/video{i} --set-ctrl=exposure_absolute={config['exposure_absolute']}")
        os.system(f"v4l2-ctl --device /dev/video{i} --list-ctrls")
    except Exception as e:
        logging.error(f"error: {e}")

def autoexp(image_input,cache):
    cache['autoexp'] = False
    try:
        r=np.max(image_input)
      #  logging.debug(f"cache-config: {cache['config']}")
        exp_old=cache['config']['exposure_absolute']
        if r>235:
            cache['config']['exposure_absolute']=cache['config']['exposure_absolute']*0.9
        if r <230:
            cache['config']['exposure_absolute'] = cache['config']['exposure_absolute'] * 1.1
        logging.debug(f"exp: {cache['config']['exposure_absolute']}")
        if cache['config']['exposure_absolute']<50:
            cache['config']['exposure_absolute']=50
        if cache['config']['exposure_absolute'] >10000:
            cache['config']['exposure_absolute'] = 10000

        if exp_old!=cache['config']['exposure_absolute']:
                os.system(f"v4l2-ctl --device /dev/video{cache['config']['indice_camera']} --set-ctrl=exposure_absolute={cache['config']['exposure_absolute']}")
                time.sleep(0.25)

                cache['autoexp'] = True
        cv2.putText(image_input, str(r)+" calcolo autoespozione in corso " + str(cache['config']['exposure_absolute']), (5, 80),
                cv2.FONT_HERSHEY_COMPLEX_SMALL, 0.8, get_colore('green'), 1)
    except Exception as e:
        logging.error(f"error: {e}")


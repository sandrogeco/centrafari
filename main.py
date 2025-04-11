import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
from scipy.ndimage import gaussian_filter

# Load the image

def tst(ax,img):
    if img.ndim == 3:
        img_gray =np.mean(img, axis=2)  # Converte in scala di grigi
    else:
        img_gray = img
    #normalizzo
    print("max "+str(np.max(img_gray)))
    print("min "+str(np.min(img_gray)))
    img_gray_n = (img_gray - np.min(img_gray)) / (np.max(img_gray) - np.min(img_gray))
    #filtro
    img_gray_nf = gaussian_filter(img_gray_n, sigma=10)

    img1=img_gray


    ax[0].imshow(img_gray,cmap='gray')
    ax[1].imshow(img_gray_n,cmap='gray')
    ax[2].imshow(img_gray_nf,cmap='gray')


    contour = ax[2].contour(img_gray_nf, levels=10)

px='/home/sandro/Downloads/immagini_anabbagliante_alogeno_12_0incl_centrato/'
pth=['bri_0_contr_0_expabs_1000.jpg','bri_0_contr_0_expabs_50.jpg']
for pthx in pth:

    img = mpimg.imread(px+pthx)
    fig, ax = plt.subplots(3, 1, figsize=(12, 6))
    tst(ax,img)
    plt.title(pthx)
plt.axis('off')  # To hide the axes
plt.show()

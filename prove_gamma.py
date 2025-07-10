import numpy as np
from scipy.optimize import curve_fit

# Dati
gamma_impostato = np.array([100, 200, 300, 400, 500])
valori = np.array([42, 55, 72, 92, 109])  # Valori pixel letti
valori = np.array([90, 108, 127, 142, 155])  # Valori pixel letti

# Modello
def risposta_gamma(gamma_fittizio, a, b, I):
    gamma_reale = a * gamma_fittizio + b
    return 255 * (I ** (1 / gamma_reale))

# Fit
popt, _ = curve_fit(risposta_gamma, gamma_impostato, valori, bounds=([0, 0, 0], [0.01, 10, 1]))
a, b, I = popt

# Risultato
print(f"a = {a:.5f}, b = {b:.5f}, I = {I:.5f}")
print(f"gamma reale = a * gamma_impostato + b")

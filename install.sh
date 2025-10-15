#!/bin/bash
set -e  # interrompe in caso di errore

echo "🔧 Aggiornamento pacchetti..."
sudo apt-get update -qq

echo "📦 Installazione librerie Python (OpenCV, Tkinter, SciPy)..."
sudo apt-get install -y \
    python3-opencv \
    python3-tk \
    python3-scipy \
    python3-pil \
    python3-pil.imagetk
echo "✅ Installazione completata!"
echo
echo "Verifica rapida:"
python3 - <<'EOF'
try:
    import cv2, tkinter, scipy
    print("OpenCV:", cv2.__version__)
    print("SciPy:", scipy.__version__)
    print("Tkinter: OK")
except Exception as e:
    print("❌ Errore:", e)
EOF

# ======================================================
# Crea una cartella in RAM e la monta in /mnt/ramdisk
# in modo automatico all'avvio del sistema (Raspberry Pi)
# ======================================================

RAMDIR="/mnt/temp"
SIZE="200M"      # puoi cambiare la dimensione
FSTAB="/etc/fstab"

echo " Creazione folder in RAM (${RAMDIR}, ${SIZE})"

# 1️⃣ Crea la directory se non esiste
if [ ! -d "$RAMDIR" ]; then
    echo "📁 Creo directory $RAMDIR"
    sudo mkdir -p "$RAMDIR"
fi

# 2️⃣ Controlla se la voce esiste già in /etc/fstab
if ! grep -q "$RAMDIR" "$FSTAB"; then
    echo "📝 Aggiungo voce in $FSTAB"
    echo "tmpfs   $RAMDIR   tmpfs   defaults,size=${SIZE},noatime,mode=1777   0   0" | sudo tee -a "$FSTAB" > /dev/null
else
    echo "ℹ️  Voce già presente in fstab, salto."
fi

# 3️⃣ Monta subito senza riavvio
echo "⚙️  Montaggio immediato..."
sudo mount -a

# 4️⃣ Mostra conferma
if mountpoint -q "$RAMDIR"; then
    echo "✅ RAM disk montato correttamente in $RAMDIR"
    df -h | grep "$RAMDIR"
else
    echo "❌ Errore: il mount non è riuscito!"
fi




#!/bin/bash

# Nome della cartella di output
PACK_DIR="pack"
PACKAGES_DIR="$PACK_DIR/packages"

echo "🔧 Creo la cartella '$PACK_DIR'..."
mkdir -p "$PACKAGES_DIR"

cd "$PACK_DIR"

apt download  liblapack3 libblas3  libopenblas0 libopenblas-base libgfortran5 libopenblas0-pthread libopenblas0-openmp libopenblas0-serial libblas-dev libatlas3-base libatlas-base-dev


echo "📦 Esporto i pacchetti installati in requirements.txt..."
pip3 freeze > "$PACK_DIR/requirements.txt"

echo "⬇️ Scarico i pacchetti localmente in '$PACKAGES_DIR'..."
pip3 download -r "$PACK_DIR/requirements.txt" -d "$PACKAGES_DIR"

echo "🗜️ Creo l'archivio compresso 'pack.tar.gz'..."
tar -czvf pack.tar.gz "$PACK_DIR"



echo "✅ Fatto! File creato: pack.tar.gz"


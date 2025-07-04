#!/bin/bash

echo "📦 INSTALLA PACK - installazione offline dei pacchetti Python"

# Verifica che pip sia presente
if ! command -v pip3 &> /dev/null; then
    echo "❌ pip3 non è installato. Installalo prima di procedere."
    exit 1
fi

# Se il pacchetto pack.tar.gz è presente, estrailo
if [ -f "pack.tar.gz" ]; then
    echo "📂 Estrazione di 'pack.tar.gz'..."
    tar -xzf pack.tar.gz
else
    echo "ℹ️ 'pack.tar.gz' non trovato. Presumo che 'pack/' sia già presente."
fi

# Controlla che ci sia la cartella pack con i file giusti
if [ ! -f "pack/requirements.txt" ] || [ ! -d "pack/packages" ]; then
    echo "❌ Cartella 'pack/' o file 'requirements.txt' mancante!"
    exit 1
fi

echo "🚀 Installazione pacchetti da 'pack/packages/' (offline)..."
pip3 install --no-index --find-links=pack/packages -r pack/requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Tutti i pacchetti sono stati installati correttamente!"
else
    echo "⚠️ Si è verificato un errore durante l'installazione."
fi

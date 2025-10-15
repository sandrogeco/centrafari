#!/bin/bash

cd /home/pi/Applications || exit 1

rm -f master.*
wget -q https://github.com/sandrogeco/centrafari/archive/refs/heads/master.zip

ZIPFILE="master.zip"
[ ! -f "$ZIPFILE" ] && echo "❌ File $ZIPFILE non trovato" && exit 1

TMPDIR=$(mktemp -d)

# Estrae solo i file .py
unzip -q "$ZIPFILE" '*.py' -d "$TMPDIR"

# Sposta tutti i .py (da sottocartelle incluse) nella cartella corrente
find "$TMPDIR" -type f -name "*.py" -exec mv {} . \;

rm -rf "$TMPDIR"

echo "✅ Estratti solo i file .py da $ZIPFILE nella cartella corrente"

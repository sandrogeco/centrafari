#!/bin/bash

set -euo pipefail

# shellcheck disable=SC2087

# Script per trasferire il file MW28912.py sul P10 target (tramite ssh) e
# avviarlo direttamente.

display_usage() {
    echo "Utilizzo:"
    echo "$0 <target_ip> <kill | send | run | send_run | help> <ABBAGLIANTE | ANABBAGLIANTE | FENDINEBBIA>"
}

kill_script() {
    # Chiudi tutti i programmi aperti
    # shellcheck disable=SC2087
    ssh "pi@$TARGET_IP" >/dev/null 2>&1 <<EOF
        echo 1234 | sudo -S pkill -15 -f "$TARGET_DESTINATION_FOLDER/MW28912.py" || true
        echo 1234 | sudo -S killall -9 MW28912 || true
EOF
}

send_script() {
    # Trasferisci il necessario sul P10 target
    scp "camera.py" pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"
    scp "comms.py" pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"
    scp "config_abbagliante.json" pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"
    scp "config_anabbagliante.json" pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"
    scp "funcs.py" pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"
    scp "MW28912.py" pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"
    scp "utils.py" pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"
}

run_script() {
    # Avvia gli script
    # shellcheck disable=SC2087
    ssh "pi@$TARGET_IP" <<EOF
        echo -e "\n\n\n\n"

        # Avvia lo script della telecamera
        cd "$TARGET_DESTINATION_FOLDER"
        DISPLAY=:0 nice -n 10 python3 "$TARGET_DESTINATION_FOLDER/MW28912.py" "$TIPO_FARO"
EOF
}

# ##############################################################################

ROOT_DIR="$(
    cd "$(dirname "$0")"
    pwd
)"
cd "$ROOT_DIR"

# Controllo iniziale degli argomenti
if (($# < 3)); then
    display_usage
fi

TARGET_IP="$1"
ACTION="$2"
TIPO_FARO="$3"

TARGET_DESTINATION_FOLDER="/home/pi/Applications"

case "$ACTION" in
"kill")
    kill_script
    ;;
"send")
    send_script
    ;;
"run")
    kill_script
    run_script
    ;;
"send_run")
    kill_script
    send_script
    run_script
    ;;
"help")
    display_usage
    ;;
*)
    display_usage
    exit 1
    ;;
esac

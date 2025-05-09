#!/bin/bash

#set -euo pipefail

# shellcheck disable=SC2087

# Script per trasferire il file MW28912.py sul P10 target (tramite ssh) e
# avviarlo direttamente.

display_usage() {
    echo "Utilizzo:"
    echo "$0 <target_ip> <kill | send | run | send_run | help> <ABBAGLIANTE | ANABBAGLIANTE | FENDINEBBIA>"
}

resetta_fotocamera() {
    ssh "pi@$TARGET_IP" <<EOF
        # Setup iniziale per la telecamera
        video_device="\$(find /dev -iname 'video*' | sort | head -n1)"
        echo "video_device: \$video_device"

        v4l2-ctl --device "\$video_device" --list-ctrls

        v4l2-ctl --device "\$video_device" --set-ctrl=exposure_auto=1
        v4l2-ctl --device "\$video_device" --set-ctrl=brightness=0
        v4l2-ctl --device "\$video_device" --set-ctrl=contrast=100
        v4l2-ctl --device "\$video_device" --set-ctrl=saturation=0
        v4l2-ctl --device "\$video_device" --set-ctrl=exposure_absolute=1000

        v4l2-ctl --device "\$video_device" --list-ctrls
EOF
}

kill_script() {
    # Chiudi tutti i programmi aperti
    # shellcheck disable=SC2087
    ssh "pi@$TARGET_IP" >/dev/null 2>&1 <<EOF
        echo 1234 | sudo -S pkill -15 -f "$TARGET_DESTINATION_PATH"
        echo 1234 | sudo -S killall -9 MW28912 || true
        echo 1234 | sudo -S kill -15 -f "emulatore_proteus.py"
EOF
}

send_script() {
    # Trasferisci lo script e l'emulatore del server sul P10 target
    {
      #  scp "script.py" pi@"$TARGET_IP":"$TARGET_DESTINATION_PATH"
        scp * pi@"$TARGET_IP":"$TARGET_DESTINATION_DIR"
        scp "emulatore_proteus.py" pi@"$TARGET_IP":"/tmp/emulatore_proteus.py"
    } >/dev/null
}

run_script() {
    # Avvia gli script
    # shellcheck disable=SC2087
    ssh "pi@$TARGET_IP" <<EOF
        echo -e "\n\n\n\n"
        sleep 1
        # Avvia lo script della telecamera
        DISPLAY=:0 nice -n 10 python3 "$TARGET_DESTINATION_PATH" "$TIPO_FARO"

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

#TARGET_DESTINATION_PATH="/tmp/script.py"
TARGET_DESTINATION_PATH="/home/pi/Applications/MW28912.py"
TARGET_DESTINATION_DIR="/home/pi/Applications/"

case "$ACTION" in
"kill")
    kill_script
    ;;
"send")
    send_script
    ;;
"run")
    kill_script
 #   resetta_fotocamera
    run_script
    ;;
"send_run")
    kill_script
    send_script
  #  resetta_fotocamera
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

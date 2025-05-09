#!/bin/bash

set -euo pipefail

# shellcheck disable=SC2087

# Script per trasferire il file MW28912.py sul P10 target (tramite ssh) e
# avviarlo direttamente.

display_usage() {
    echo "Utilizzo:"
    echo "$0 <target_ip> <kill | send | send_script_originale | run | send_run | scatta_foto | cattura_frame | help> <ABBAGLIANTE | ANABBAGLIANTE | FENDINEBBIA>"
}

kill_script() {
    # Chiudi tutti i programmi aperti
    # shellcheck disable=SC2087
    ssh "pi@$TARGET_IP" >/dev/null 2>&1 <<EOF
        echo 1234 | sudo -S pkill -15 -f "$TARGET_DESTINATION_PATH"
        echo 1234 | sudo -S pkill -15 -f "emulatore_proteus.py"
EOF
}

send_assets() {
    {
        scp "./assets/topauto_anabb.bmp" pi@"$TARGET_IP":"/home/pi/Applications/topauto_anabb.bmp"
        scp "./assets/topauto_abb.bmp" pi@"$TARGET_IP":"/home/pi/Applications/topauto_abb.bmp"
        scp "./assets/topauto_fend.bmp" pi@"$TARGET_IP":"/home/pi/Applications/topauto_fend.bmp"
    } >/dev/null
}

send_script() {
    # Trasferisci lo script e l'emulatore del server sul P10 target
    {
        scp "emulatore_proteus.py" pi@"$TARGET_IP":"/tmp/emulatore_proteus.py"
        scp "MW28912.py" pi@"$TARGET_IP":"$TARGET_DESTINATION_PATH"
    } >/dev/null
}

send_script_originale() {
    # Trasferisci lo script e l'emulatore del server sul P10 target
    {
        ssh "pi@$TARGET_IP" sh -c 'echo 1234 | sudo rm -f /tmp/all_msgs.txt /tmp/last_msg.txt'

        scp "emulatore_proteus.py" pi@"$TARGET_IP":"/tmp/emulatore_proteus.py"
        scp "MW28912_originale.py" pi@"$TARGET_IP":"$TARGET_DESTINATION_PATH"
    } >/dev/null
}

send_script_foca() {
    # Trasferisci lo script e l'emulatore del server sul P10 target
    {
        scp "emulatore_proteus.py" pi@"$TARGET_IP":"/tmp/emulatore_proteus.py"
        scp "MW28912_per_foca.py" pi@"$TARGET_IP":"$TARGET_DESTINATION_PATH"
    } >/dev/null
}

run_script() {
    PORTA_SERVER_PROTEUS="$((25000 + RANDOM % 5000))"
    echo -e "Porta random: $PORTA_SERVER_PROTEUS\n\n\n"

    # Avvia gli script
    # shellcheck disable=SC2087
    ssh "pi@$TARGET_IP" <<EOF
        echo -e "\n\n\n\n"

        # Setup iniziale per la telecamera
        video_device="\$(find /dev -iname 'video*' | sort | head -n1)"
        echo "video_device: \$video_device"
        v4l2-ctl --device "\$video_device" --set-ctrl=exposure_auto=1
        v4l2-ctl --device "\$video_device" --set-ctrl=contrast=100
        v4l2-ctl --device "\$video_device" --set-ctrl=saturation=0
        v4l2-ctl --device "\$video_device" --set-ctrl=exposure_absolute=50

        # Fai partire l'emulatore
        python3 "/tmp/emulatore_proteus.py" $PORTA_SERVER_PROTEUS &
        sleep 1

        echo 1234 | sudo -S rm -f /tmp/frame_originale.bmp /tmp/frame_to_show.png
        echo 1234 | sudo -S rm -f /tmp/all_msgs.txt /tmp/last_msg.txt

        # Avvia lo script della telecamera
        DISPLAY=:0 nice -n 10 python3 "$TARGET_DESTINATION_PATH" "$TIPO_FARO" $PORTA_SERVER_PROTEUS
EOF
}

scatta_foto() {
    ssh "pi@$TARGET_IP" <<EOF
        echo -e "\n\n\n\n"

        # Setup iniziale per la telecamera
        video_device="\$(find /dev -iname 'video*' | sort | head -n1)"
        echo "video_device: \$video_device"
        v4l2-ctl --device "\$video_device" --set-ctrl=exposure_auto=1
        v4l2-ctl --device "\$video_device" --set-ctrl=contrast=100
        v4l2-ctl --device "\$video_device" --set-ctrl=saturation=0
        v4l2-ctl --device "\$video_device" --set-ctrl=exposure_absolute=50

        rm -f /tmp/frame.jpg
        v4l2-ctl --device "\$video_device" \
            --stream-mmap --stream-to=/tmp/frame.jpg --stream-count=1
EOF

    scp pi@"$TARGET_IP":"/tmp/frame.jpg" "./test_data/$TIPO_FARO/raw/$(date +%s)_${ARG4:-none}.jpg"
}

cattura_frame() {
    DEST_DIR="./test_data/$TIPO_FARO/$(date +%s)"
    mkdir -p "$DEST_DIR"

    scp pi@"$TARGET_IP":"/tmp/frame_originale.bmp" "$DEST_DIR/frame_originale.bmp"
    scp pi@"$TARGET_IP":"/tmp/frame_to_show.png" "$DEST_DIR/frame_to_show.png"
    scp pi@"$TARGET_IP":"/tmp/last_msg.txt" "$DEST_DIR/last_msg.txt"
    scp pi@"$TARGET_IP":"/tmp/all_msgs.txt" "$DEST_DIR/all_msgs.txt"

    echo "$ARG4" >"$DEST_DIR/note.txt"
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
ARG4="${4:-}"

TARGET_DESTINATION_PATH="/home/pi/Applications/MW28912.py"

case "$ACTION" in
"kill")
    kill_script
    ;;
"send_assets")
    send_assets
    ;;
"send")
    send_script
    ;;
"send_originale")
    send_script_originale
    ;;
"send_foca")
    send_script_foca
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
"send_run_originale")
    kill_script
    send_script_originale
    run_script
    ;;
send_run_foca)
    kill_script
    send_script_foca
    run_script
    ;;
"scatta_foto")
    scatta_foto
    ;;
"cattura_frame")
    cattura_frame
    ;;
"help")
    display_usage
    ;;
*)
    display_usage
    exit 1
    ;;
esac

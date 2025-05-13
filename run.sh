#!/bin/bash

set -euo pipefail

# shellcheck disable=SC2087

display_usage() {
    echo "Utilizzo:"
    echo "$0 TARGET_IP=192.168.25.2 [TIPO_FARO=<ABBAGLIANTE | ANABBAGLIANTE | FENDINEBBIA>] <kill | send | run>"
}

kill_script() {
    # Chiudi tutti i programmi aperti
    echo "*** kill_script"

    # shellcheck disable=SC2087
    ssh "pi@$TARGET_IP" <<EOF
        echo 1234 | sudo -S pkill -15 -f "$TARGET_DESTINATION_FOLDER/MW28912.py" || true
        echo 1234 | sudo -S pkill -9 MW28912 || true
        echo 1234 | sudo -S pkill -15 "emulatore_proteus.py" || true
        echo 1234 | sudo -S pkill -15 "usb_video_capture_cm4" || true
EOF
}

send_script() {
    # Trasferisci lo script e l'emulatore del server sul P10 target
    echo "*** send_script"

    touch /tmp/checksum_file_centrafari.txt

    for file in \
        MW28912.py \
        camera.py \
        comms.py \
        funcs.py \
        utils.py \
        config_anabbagliante.json \
        config_abbagliante.json \
        assets/usb_video_capture_cm4 \
        ; do
        # Trasferisci solo i file effettivamente cambiati
        if ! grep -q "$(md5sum "$file" | cut -d' ' -f1)" /tmp/checksum_file_centrafari.txt; then
            scp $file pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"
        else
            echo "Skip send $file to $TARGET_IP"
        fi
    done

    if ! grep -q "$(md5sum emulatore_proteus.py | cut -d' ' -f1)" /tmp/checksum_file_centrafari.txt; then
        scp "emulatore_proteus.py" pi@"$TARGET_IP":"/tmp/emulatore_proteus.py"
    fi

    # Salva i checksum dei file trasferiti
    md5sum \
        MW28912.py \
        camera.py \
        comms.py \
        funcs.py \
        utils.py \
        config_anabbagliante.json \
        config_abbagliante.json \
        emulatore_proteus.py \
        assets/usb_video_capture_cm4 \
        >/tmp/checksum_file_centrafari.txt
}

run_script() {
    # Avvia gli script
    echo "*** run_script"

    # shellcheck disable=SC2087
    ssh "pi@$TARGET_IP" <<EOF
        echo -e "\n\n\n\n"
        sleep 1

        echo 1234 | sudo -S rm -f /tmp/all_msgs.txt

        # Avvia lo script della telecamera
        set -x
        DISPLAY=:0 nice -n 0 python3 $PROFILE_ARGS "$TARGET_DESTINATION_FOLDER/MW28912.py" "$TIPO_FARO"
        set +x
EOF
}

# ##############################################################################

ROOT_DIR="$(
    cd "$(dirname "$0")"
    pwd
)"
cd "$ROOT_DIR"

if [ "$1" = "-h" ] || [ "$1" = "--help" ]; then
    display_usage
    exit 0
fi

TARGET_DESTINATION_FOLDER="/home/pi/Applications"
PROFILE_ARGS=""

for arg in "$@"; do
    case "$arg" in
    # Impostazione parametri
    "TARGET_IP="*)
        TARGET_IP="${arg#*=}"
        ;;
    "TIPO_FARO="*)
        TIPO_FARO="${arg#*=}"
        ;;
    "TARGET_DESTINATION_FOLDER="*)
        TARGET_DESTINATION_FOLDER="${arg#*=}"
        ;;
    "PROFILE_SCRIPT=y" | "PROFILE_SCRIPT=n")
        if [ "$arg" = "PROFILE_SCRIPT=y" ]; then
            PROFILE_ARGS="-m cProfile -o /tmp/MW28912.prof"
        fi
        ;;

    # Azioni
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

    *)
        display_usage
        exit 1
        ;;
    esac
done

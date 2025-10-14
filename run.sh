#!/bin/bash

set -euo pipefail

# shellcheck disable=SC2087

display_usage() {
    echo "Utilizzo:"
    echo "run.sh <uno o piu' NOME_PARAMETRO=...> <una o piu' azioni da eseguire>"
    echo
    echo "I possibili parametri impostabili sono:"
    echo "   TARGET_IP"
    echo "   TARGET_SSH_PORT"
    echo "   TIPO_FARO=<anabbagliante | abbagliante | fendinebbia>"
    echo "   TARGET_DESTINATION_FOLDER"
    echo "   USA_EMULATORE=<y | n>"
    echo "   PORTA_SERVER_PROTEUS"
    echo "Le azioni possibili sono:"
    echo "   kill, send, force_send, run, run_centra_telecamera, remotelog (visualizza l'ultimo log sul target)"
    echo
    echo "Esempio di invocazione per inviare e avviare lo script sul target:"
    echo "run.sh TARGET_IP=192.168.25.111 TIPO_FARO=anabbagliante send run kill"
    echo "Oppure per semplicemente chiudere lo script sul target:"
    echo "run.sh TARGET_IP=192.168.25.111 kill"
}

kill_script() {
    # Chiudi tutti i programmi aperti
    echo "*** kill_script"

    # shellcheck disable=SC2087
    ssh -p "$TARGET_SSH_PORT" "pi@$TARGET_IP" >/dev/null 2>&1 <<EOF
        echo 1234 | sudo -S pkill -15 -f "$TARGET_DESTINATION_FOLDER/MW28912.py" || true
        echo 1234 | sudo -S pkill -15 -f "$TARGET_DESTINATION_FOLDER/MW28912_centra_telecamera.py" || true
        echo 1234 | sudo -S pkill -9 MW28912 || true
        echo 1234 | sudo -S pkill -9 mw28912 || true

        echo 1234 | sudo -S pkill -15 "emulatore_proteus.py" || true
        echo 1234 | sudo -S pkill -15 "usb_video_capture_cm4" || true
        echo 1234 | sudo -S rm -f /tmp/frame.jpg
EOF
}

send_script() {
    # Trasferisci lo script e l'emulatore del server sul P10 target
    echo "*** send_script"

    touch /tmp/checksum_file_centrafari.txt

    # Trasferisci tutti i file che servono al funzionamento dello script
    for file in \
        MW28912.py \
        MW28912_centra_telecamera.py \
        camera.py \
        comms.py \
        funcs_anabbagliante.py \
        funcs_abbagliante.py \
        funcs_luminosita.py \
        funcs_misc.py \
        utils.py \
        config_anabbagliante.json \
        config_abbagliante.json \
        assets/usb_video_capture_cm4 \
        ; do
        # Trasferisci solo i file effettivamente cambiati dall'ultimo invio
#        if ! grep -q "$(md5sum "$file" | cut -d' ' -f1)" /tmp/checksum_file_centrafari.txt; then
 #           scp -P "$TARGET_SSH_PORT" $file pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"
#        else
#            echo "Skip send $file to $TARGET_IP"
#        fi
            scp -P "$TARGET_SSH_PORT" $file pi@"$TARGET_IP":"$TARGET_DESTINATION_FOLDER"

    done

    # Trasferisci l'emulatore
    if ! grep -q "$(md5sum emulatore_proteus.py | cut -d' ' -f1)" /tmp/checksum_file_centrafari.txt; then
        scp -P "$TARGET_SSH_PORT" "emulatore_proteus.py" pi@"$TARGET_IP":"/tmp/emulatore_proteus.py"
    else
        echo "Skip send emulatore_proteus.py to $TARGET_IP"
    fi

    # Salva i checksum dei file appena trasferiti
    md5sum \
        MW28912.py \
        MW28912_centra_telecamera.py \
        camera.py \
        comms.py \
        funcs_anabbagliante.py \
        funcs_abbagliante.py \
        funcs_luminosita.py \
        funcs_misc.py \
        utils.py \
        config_anabbagliante.json \
        config_abbagliante.json \
        emulatore_proteus.py \
        assets/usb_video_capture_cm4 \
        >/tmp/checksum_file_centrafari.txt
}

run_allineamento() {
    echo "*** run_allineamento"

    # shellcheck disable=SC2087
    ssh -p "$TARGET_SSH_PORT" "pi@$TARGET_IP" <<EOF
        echo -e "\n\n\n\n"

        # Avvia l'emulatore e lo script della telecamera
        set -x
        if [ -n "$USA_EMULATORE" ]; then
            python3 "/tmp/emulatore_proteus.py" $PORTA_SERVER_PROTEUS &
        fi

        DISPLAY=:0 nice -n 0 python3 $PROFILE_ARGS "$TARGET_DESTINATION_FOLDER/MW28912.py" "$TIPO_FARO" $PORTA_SERVER_PROTEUS
        set +x
EOF
}

run_centra_telecamera() {
    echo "*** run_centra_telecamera"

    # shellcheck disable=SC2087
    ssh -p "$TARGET_SSH_PORT" "pi@$TARGET_IP" <<EOF
        echo -e "\n\n\n\n"

        # Avvia l'emulatore e lo script della telecamera
        set -x
        DISPLAY=:0 nice -n 0 python3 "$TARGET_DESTINATION_FOLDER/MW28912_centra_telecamera.py" "$TIPO_FARO"
        set +x
EOF
}

view_remote_log() {
    echo "*** view_remote_log"
    ssh -p "$TARGET_SSH_PORT" "pi@$TARGET_IP" <<'EOF'
        echo -e "\n\n\n\n"
        last_log=$(find /mnt/temp/ -type f -name 'MW28912py_log_*.log' 2>/dev/null | sort -r | head -1)

        echo -e "Visualizzazione log: $last_log\n\n"
        tail -f "$last_log"
EOF
}

view_remote_ctr_log() {
    echo "*** view_remote_ctr_log"
    ssh -p "$TARGET_SSH_PORT" "pi@$TARGET_IP" <<'EOF'
        echo -e "\n\n\n\n"
        last_log=$(find /tmp/ -type f -name 'MW28912py_centra_telecamerapy_log_*.log' 2>/dev/null | sort -r | head -1)

        echo -e "Visualizzazione log: $last_log\n\n"
        tail -f "$last_log"
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

TARGET_SSH_PORT=22
TARGET_DESTINATION_FOLDER="/home/pi/Applications"
PROFILE_ARGS=""
USA_EMULATORE=
PORTA_SERVER_PROTEUS=28500

# shellcheck disable=SC2124
ultima_azione="${@: -1}"
if [ "$ultima_azione" = "kill" ]; then
    trap "kill_script" EXIT
fi

for arg in "$@"; do
    case "$arg" in
    # Impostazione parametri
    "TARGET_IP="*)
        TARGET_IP="${arg#*=}"
        ;;
    "TARGET_SSH_PORT="*)
        TARGET_SSH_PORT="${arg#*=}"
        ;;
    "TIPO_FARO="*)
        TIPO_FARO="${arg#*=}"
        ;;
    "USA_EMULATORE=y" | "USA_EMULATORE=n")
        if [ "$arg" = "USA_EMULATORE=y" ]; then
            USA_EMULATORE=y
            PORTA_SERVER_PROTEUS="$((25000 + RANDOM % 5000))"
        fi
        ;;
    "PORTA_SERVER_PROTEUS="*)
        PORTA_SERVER_PROTEUS="${arg#*=}"
        ;;
    "TARGET_DESTINATION_FOLDER="*)
        TARGET_DESTINATION_FOLDER="${arg#*=}"
        ;;
    "PROFILE_SCRIPT=y" | "PROFILE_SCRIPT=n")
        if [ "$arg" = "PROFILE_SCRIPT=y" ]; then
            PROFILE_ARGS="-m cProfile -o /tmp/$(date +%s)_MW28912_py.prof"
        fi
        ;;

    # Azioni
    "kill")
        kill_script
        ;;
    "send")
        send_script
        ;;
    "force_send")
        echo "force_send: Eliminazione /tmp/checksum_file_centrafari.txt"
        rm -f /tmp/checksum_file_centrafari.txt
        send_script
        ;;
    "run" | "run_allineamento")
        run_allineamento
        ;;
    "run_centra_telecamera")
        run_centra_telecamera
        ;;
    "remotelog")
        view_remote_log
        ;;
    "remotectrlog")
        view_remote_log
        ;;

    *)
        display_usage
        echo -e "\n\n\n"
        echo "ERRORE! Argomento non riconosciuto! $arg"
        echo "Controlla l'help piu' sopra o con il comando $0 -h"
        exit 1
        ;;
    esac
done

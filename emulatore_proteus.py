"""Script che emula l'applicazione Proteus del centrafari TopAuto"""

import socket
import sys
from functools import partial
import time
import string
from signal import SIGINT, signal
from typing import List

# pylint: disable=C0103,W0718

# Utilizzo script:
# python3 emulatore_proteus.py <porta>


def prettify_packet(payload: List[int]) -> str:
    """Rende un pacchetto piu' facilmente leggibile."""

    result = "".join([f" {hex(b)[2:]}" for b in payload])
    result += "  /  "
    result += "".join(
        [f"{chr(b)}" if chr(b) in string.printable else " " for b in payload]
    )

    return result


def data_to_bytes(payload: str) -> bytes:
    return bytes(payload.encode("utf-8"))


def send_response(client_socket, payload: str) -> None:
    """Invia un messaggio ad un client."""
    print(f"[emulatore] >>>> TX {payload}", flush=True)
    client_socket.sendall(data_to_bytes(payload))


def cleanup_socket(tcp_socket, *_):
    """Chiude la connessione."""
    print("_cleanup_socket", flush=True)
    tcp_socket.detach()
    tcp_socket.close()
    sys.exit(0)


# ##############################################################################


def config1(config):
    # Alcuni valori iniziali
    config["tolV_df"] = 50
    config["tolH_df"] = 50


# ##############################################################################

config = {
    # 0=analog, 1=digital, 2=thermal
    "tipo_visualizzazione": 0,
    # 0=no, 1=si
    "visualizza_croce": 1,
    "tolV_df": 0,
    "mm_panel_per_pixel_df": 0.0,
    "inclinazione_in_pixels": 0,
    "tolH_df": 0,
    "Larghezza_filtro_gaussiano_df": 0,
    "tx_A_translation_matrix_df": 0,
    "ty_A_translation_matrix_df": 0,
    "tx_N_translation_matrix_df": 0,
    "ty_N_translation_matrix_df": 0,
    "tx_F_translation_matrix_df": 0,
    "ty_F_translation_matrix_df": 0,
    "start_row_df": 0,
    "end_row_df": 0,
    "start_col_df": 0,
    "end_col_df": 0,
    "numero_di_tacche_abbagl_offset_x_df": 0,
    "numero_di_tacche_abbagl_offset_y_df": 0,
    "lin_dem_anabb_offset_x_df": 0,
    "lin_dem_anabb_offset_y_df": 0,
    "lux_su_lineaX_AtH": 0,
    "lin_dem_anabb_coeff_angol_df": 0,
    "alfa_LPF": 0,
    "display_none_croci_linee_anabb": 0,
    "len_window_y": 0,
    # Non puo' essere 0
    "step_media": 1,
    "step_contr": 0,
    "lux_su_lineaY_AtH": 0,
}


def genera_stringa_config(c):
    return (
        "CFG->"
        + f"{c.get('tipo_visualizzazione', 0)}"
        + f"{c.get('visualizza_croce', 0)}"
        + f"TOV{c.get('tolV_df'):03}"
        + f"mpx{c.get('mm_panel_per_pixel_df'):1.6f}"
        + f"inc{c.get('inclinazione_in_pixels'):04}"
        + f"TOH{c.get('tolH_df'):03}"
        + f"GSF{c.get('Larghezza_filtro_gaussiano_df'):03}"
        + f"TAX{c.get('tx_A_translation_matrix_df'):05}"
        + f"TAY{c.get('ty_A_translation_matrix_df'):05}"
        + f"TNX{c.get('tx_N_translation_matrix_df'):05}"
        + f"TNY{c.get('ty_N_translation_matrix_df'):05}"
        + f"TFX{c.get('tx_F_translation_matrix_df'):05}"
        + f"TFY{c.get('ty_F_translation_matrix_df'):05}"
        + f"CRI{c.get('start_row_df'):03}"
        + f"CRF{c.get('end_row_df'):03}"
        + f"CCI{c.get('start_col_df'):03}"
        + f"CCF{c.get('end_col_df'):03}"
        + f"tax{c.get('numero_di_tacche_abbagl_offset_x_df'):03}"
        + f"tay{c.get('numero_di_tacche_abbagl_offset_y_df'):03}"
        + f"Lnx{c.get('lin_dem_anabb_offset_x_df'):05}"
        + f"Lny{c.get('lin_dem_anabb_offset_y_df'):05}"
        + f"AtH{c.get('lux_su_lineaX_AtH'):03}"
        + f"Lnm{c.get('lin_dem_anabb_coeff_angol_df'):1.9f}"
        + f"alf{c.get('alfa_LPF'):1.5f}"
        + f"ncl{c.get('display_none_croci_linee_anabb'):02}"
        + f"lwn{c.get('len_window_y'):03}"
        + "dnv0"
        + "bcn0"
        + "mcb0"
        + f"stm{c.get('step_media'):03}"
        + f"stc{c.get('step_contr'):03}"
        + f"AtV{c.get('lux_su_lineaY_AtH'):03}"
    )


if __name__ == "__main__":
    # La porta viene passata come primo argomento, oppure se non fosse
    # presente si usa 28500 come default
    SERVER_ADDRESS = (
        "127.0.0.1",
        int(sys.argv[1]) if len(sys.argv) >= 2 else 28500,
    )

    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.bind(SERVER_ADDRESS)
    tcp_socket.listen(1)

    signal(SIGINT, partial(cleanup_socket, tcp_socket))

    print(f"Avvio server emulatore_proteus.py {SERVER_ADDRESS}", flush=True)

    config1(config)

    while True:
        try:
            connection, client = tcp_socket.accept()

            try:
                data = list(connection.recv(128))
                data_str = ''.join([chr(d) for d in data])
                print(f"\n\n[emulatore] <<<< RX {prettify_packet(data)}", flush=True)

                if data_str == "start_cfg":
                    send_response(connection, genera_stringa_config(config))
                else:
                    send_response(connection, "croce_OFF")
            finally:
                time.sleep(1)

        except Exception as e:
            print(e, flush=True)
            break

    connection.close()
    cleanup_socket(tcp_socket)

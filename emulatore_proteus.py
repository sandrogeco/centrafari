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
    print(f"<<<< TX {payload}", flush=True)
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
    config["tolV_df"] = 10
    config["mm_panel_per_pixel_df"] = 0.1250
    config["tolH_df"] = 10
    config["Larghezza_filtro_gaussiano_df"] = 21
    config["step_media"] = 1

    # Valori presi dal file MW289_12.fis trovato sul NAS di Enrico
    config["mm_panel_per_pixel_df"] = 0.308
    config["Larghezza_filtro_gaussiano_df"] = 9
    config["ty_A_translation_matrix_df"] = 70
    config["tx_N_translation_matrix_df"] = -260
    config["ty_N_translation_matrix_df"] = 30
    config["tx_F_translation_matrix_df"] = -14
    config["ty_F_translation_matrix_df"] = 27
    config["start_row_df"] = 100
    config["end_row_df"] = 300
    config["start_col_df"] = 0
    config["end_col_df"] = 629
    config["numero_di_tacche_abbagl_offset_x_df"] = -7
    config["numero_di_tacche_abbagl_offset_y_df"] = 7
    config["lin_dem_anabb_offset_x_df"] = -170
    config["lin_dem_anabb_offset_y_df"] = -40
    config["lin_dem_anabb_coeff_angol_df"] = 0.112000
    config["alfa_LPF"] = 0.150000


def config2(config):
    # CFG->00TOV010mpx0.308000inc0000TOH010GSF031TAX-0005TAY00050TNX-0005TNY00050TFX-0280TFY-0058CRI100CRF300CCI000CCF629tax-06tay012Lnx-0230Lny00010AtH000Lnm0.112000003alf0.00000ncl00lwn000dnv0bcn0mcb0stm000stc000AtV000
    config["tipo_visualizzazione"] = 0
    config["visualizza_croce"] = 0
    config["tolV_df"] = 10
    config["mm_panel_per_pixel_df"] = 0.308
    config["inclinazione_in_pixels"] = 0
    config["tolH_df"] = 10
    config["Larghezza_filtro_gaussiano_df"] = 31
    config["tx_A_translation_matrix_df"] = -5
    config["ty_A_translation_matrix_df"] = 50
    config["tx_N_translation_matrix_df"] = -5
    config["ty_N_translation_matrix_df"] = 50
    config["tx_F_translation_matrix_df"] = -280
    config["ty_F_translation_matrix_df"] = -58
    config["start_row_df"] = 100
    config["end_row_df"] = 300
    config["start_col_df"] = 0
    config["end_col_df"] = 629
    config["numero_di_tacche_abbagl_offset_x_df"] = -6
    config["numero_di_tacche_abbagl_offset_y_df"] = 12
    config["lin_dem_anabb_offset_x_df"] = -230
    config["lin_dem_anabb_offset_y_df"] = 10
    config["lux_su_lineaX_AtH"] = 0
    config["lin_dem_anabb_coeff_angol_df"] = 0.112
    config["alfa_LPF"] = 0
    config["display_none_croci_linee_anabb"] = 0
    config["len_window_y"] = 0
    config["step_media"] = 1
    config["step_contr"] = 0
    config["lux_su_lineaY_AtH"] = 0

def config3(config):

    config["tipo_visualizzazione"] = 0
    config["visualizza_croce"] = 0
    config["tolV_df"] = 10
    config["mm_panel_per_pixel_df"] = 0.308
    config["inclinazione_in_pixels"] = 0
    config["tolH_df"] = 10
    config["Larghezza_filtro_gaussiano_df"] = 31
    config["tx_A_translation_matrix_df"] = -5
    config["ty_A_translation_matrix_df"] = 50

    config["tx_N_translation_matrix_df"] = -325
    config["ty_N_translation_matrix_df"] = -165

    config["tx_F_translation_matrix_df"] = -280
    config["ty_F_translation_matrix_df"] = -58
    config["start_row_df"] = 0
    config["end_row_df"] = 630
    config["start_col_df"] = 0
    config["end_col_df"] = 629
    config["numero_di_tacche_abbagl_offset_x_df"] = -6
    config["numero_di_tacche_abbagl_offset_y_df"] = 12
    config["lin_dem_anabb_offset_x_df"] = -230
    config["lin_dem_anabb_offset_y_df"] = 10
    config["lux_su_lineaX_AtH"] = 0
    config["lin_dem_anabb_coeff_angol_df"] = 0.112
    config["alfa_LPF"] = 0
    config["display_none_croci_linee_anabb"] = 0
    config["len_window_y"] = 0
    config["step_media"] = 1
    config["step_contr"] = 0
    config["lux_su_lineaY_AtH"] = 0

def config4(config):
    # CFG->00TOV010mpx0.308000inc0028TOH015GSF003TAX-0105TAY-0075TNX-0105TNY-0075TFX-0100TFY-0115CRI100CRF300CCI000CCF629tax000tay000Lnx00000Lny00000AtH204Lnm0.112000003alf0.90000ncl00lwn200dnv0bcn0mcb0stm001stc004AtV000
    # Con inclinazione al -1%
    config["tipo_visualizzazione"] = 0
    config["visualizza_croce"] = 0
    config["tolV_df"] = 10
    config["mm_panel_per_pixel_df"] = 0.308
    config["inclinazione_in_pixels"] = 28
    config["tolH_df"] = 15
    config["Larghezza_filtro_gaussiano_df"] = 3
    config["tx_A_translation_matrix_df"] = -105
    config["ty_A_translation_matrix_df"] = -75
    config["tx_N_translation_matrix_df"] = -105
    config["ty_N_translation_matrix_df"] = -75
    config["tx_F_translation_matrix_df"] = -100
    config["ty_F_translation_matrix_df"] = -115
    config["start_row_df"] = 100
    config["end_row_df"] = 300
    config["start_col_df"] = 0
    config["end_col_df"] = 629
    config["numero_di_tacche_abbagl_offset_x_df"] = 0
    config["numero_di_tacche_abbagl_offset_y_df"] = 0
    config["lin_dem_anabb_offset_x_df"] = 0
    config["lin_dem_anabb_offset_y_df"] = 0
    config["lux_su_lineaX_AtH"] = 204
    config["lin_dem_anabb_coeff_angol_df"] = 0.112
    config["alfa_LPF"] = 0.9
    config["display_none_croci_linee_anabb"] = 0
    config["len_window_y"] = 200
    config["step_media"] = 1
    config["step_contr"] = 4
    config["lux_su_lineaY_AtH"] = 0

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

    config_sent = False

    config4(config)
    config_string = None
    #config_string = "CFG->00TOV010mpx0.308000inc0028TOH015GSF003TAX-0105TAY-0035TNX-0105TNY-0133TFX-0100TFY-0115CRI100CRF300CCI000CCF629tax000tay000Lnx00000Lny00000AtH204Lnm0.112000003alf0.90000ncl00lwn200dnv0bcn0mcb0stm001stc004AtV000"
    #connection, client = tcp_socket.accept()
    while True:
        try:
            connection, client = tcp_socket.accept()

            try:
                data = list(connection.recv(128))
                print(f"\n\n>>>> RX {prettify_packet(data)}", flush=True)

                if not config_sent:
                    if config_string is None:
                        send_response(connection, genera_stringa_config(config))
                    else:
                        send_response(connection, config_string)
                    config_sent = True
                else:
                    send_response(connection, "CIAO")
            finally:
                time.sleep(1)

        except Exception as e:
            print(e, flush=True)
            break
    connection.close()
    cleanup_socket(tcp_socket)

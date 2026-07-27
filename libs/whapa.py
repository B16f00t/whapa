#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
whapa.py - Analizador de bases de datos de WhatsApp

COMETIDO DE ESTE ARCHIVO
    Es la herramienta principal: recibe una base de datos YA DESCIFRADA y
    permite consultarla, filtrarla y generar informes.

    Se apoya en tres bibliotecas, cada una con su cometido:
        whacodes.py   catalogo de codigos de tipo de mensaje
        whareader.py  lectura de la base (Android moderno, antiguo e iOS)
        whareport.py  filtrado, informe interactivo e informe imprimible

    Este archivo NO descifra: para eso esta whacipher.py.

QUE CAMBIA RESPECTO A LA VERSION ANTERIOR
    * Lee el esquema actual de Android (tabla `message`), el antiguo
      (tabla `messages`) y ademas iOS (`ChatStorage.sqlite`), autodetectando.
    * Reconoce 28 tipos de mensaje de Android y 27 de iOS, frente a los 15 de
      antes: encuestas, notas de video, vision unica, eventos, albumes,
      privacidad avanzada, etc.
    * Mensajes de sistema, citas, reacciones, ediciones y registro de llamadas.
    * Filtros nuevos: texto con expresion regular, remitente, direccion,
      codigo nativo de tipo, y banderas (borrados, destacados, con adjunto,
      reenviados, editados, con coordenadas).
    * Informe interactivo que aguanta conversaciones de cualquier tamano.
    * Informe imprimible aparte (-p) y exportacion a CSV (-x).

** Author: Ivan Moreno a.k.a B16f00t
** Github: https://github.com/B16f00t
"""

import os
import sys
import time
import shutil
import argparse
import subprocess
from configparser import ConfigParser

try:
    from colorama import init, Fore
    init()
except ImportError:
    class _F:
        RED = GREEN = YELLOW = CYAN = RESET = ""
    Fore = _F()

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import whadeps
import whacodes as codes
import whareader as reader
import whareport as report

whadeps.safe_console()

version = "2.00"
abs_path_file = os.path.abspath(__file__)
abs_path = os.path.split(abs_path_file)[0]
whapa_path = os.path.sep.join(abs_path.split(os.sep)[:-1])


def banner():
    """ Function Banner """
    print(r"""
     __      __.__          __________
    /  \    /  \  |__ _____ \______   \_____
    \   \/\/   /  |  \\__  \ |     ___/\__  \
     \        /|   Y  \/ __ \|    |     / __ \_
      \__/\  / |___|  (____  /____|    (____  /
           \/       \/     \/               \/
    --------- Whatsapp Parser v{} ---------
    """.format(version))


def help():
    """ Function show help """
    print("""    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t

    Usage: python3 whapa.py -h (for help)
    """)


def get_configs():
    """Lee cfg/settings.cfg (datos del informe)."""
    cfg = {"company": "", "record": "", "unit": "", "examiner": "", "notes": ""}
    path = os.path.join(whapa_path, "cfg", "settings.cfg")
    if not os.path.exists(path):
        return cfg
    try:
        parser = ConfigParser()
        parser.read(path, encoding="utf-8")
        for k in cfg:
            if parser.has_option("report", k):
                cfg[k] = parser.get("report", k).strip().strip('"')
    except Exception:
        pass
    return cfg


def parse_time(value):
    """Convierte 'dd-mm-yyyy HH:MM' (formato historico de whapa) a epoch UTC."""
    if not value:
        return None
    for fmt in ("%d-%m-%Y %H:%M:%S", "%d-%m-%Y %H:%M", "%d-%m-%Y",
                "%Y-%m-%d %H:%M:%S", "%Y-%m-%d %H:%M", "%Y-%m-%d"):
        try:
            import datetime
            d = datetime.datetime.strptime(value, fmt)
            return int(d.replace(tzinfo=datetime.timezone.utc).timestamp())
        except ValueError:
            continue
    sys.exit("[e] Fecha no valida: {} (usa dd-mm-yyyy HH:MM)".format(value))


# ===========================================================================
#  Construccion del filtro a partir de los argumentos
# ===========================================================================
TYPE_FLAGS = {
    "type_text": "text", "type_image": "image", "type_audio": "audio",
    "type_video": "video", "type_contact": "contact", "type_location": "location",
    "type_call": "call", "type_application": "document", "type_gif": "gif",
    "type_deleted": "deleted", "type_share": "live_location",
    "type_stickers": "sticker", "type_system": "system",
    "type_poll": "poll", "type_viewonce": "view_once_image",
    "type_videonote": "video_note", "type_event": "event",
}


def build_filter(args):
    """Traduce los argumentos de la linea de ordenes a un report.Filter."""
    kinds = set()
    for flag, kind in TYPE_FLAGS.items():
        if getattr(args, flag, False):
            kinds.add(kind)
            if kind == "view_once_image":       # agrupa los tres de vision unica
                kinds.update({"view_once_video", "view_once_voice"})
            if kind == "call":
                kinds.add("call_missed")

    chat = None
    if args.user:
        chat = args.user
    elif args.group:
        chat = args.group

    return report.Filter(
        text=args.text, regex=args.regex, case_sensitive=args.case_sensitive,
        whole_word=args.whole_word, chat=chat, sender=args.user_all or args.sender,
        date_from=parse_time(args.time_start), date_to=parse_time(args.time_end),
        direction=args.direction, kinds=kinds or None,
        raw_types=(set(int(x) for x in args.raw_types.split(","))
                   if args.raw_types else None),
        only_deleted=args.type_deleted and len(kinds) == 1,
        only_starred=args.starred, only_media=args.only_media,
        only_forwarded=args.forwarded, only_edited=args.edited,
        only_location=args.only_location,
        only_read=args.only_read, only_unread=args.only_unread)


# ===========================================================================
#  Modos
# ===========================================================================
def _aviso_media(args, r):
    """Resumen de adjuntos y mapas."""
    if not (args.media_path or args.maps):
        return
    hallados, faltan = r.get("media_found", 0), r.get("media_missing", 0)
    print("    Adjuntos: {} localizados, {} no encontrados{}".format(
        hallados, faltan, " (copiados al informe)" if args.copy_media else ""))
    if args.maps and (r.get("maps_ok") or r.get("maps_failed")):
        print("    Mapas: {} descargados, {} fallidos".format(
            r.get("maps_ok", 0), r.get("maps_failed", 0)))
    if faltan and not hallados:
        print(Fore.YELLOW + "    [!] No se ha localizado ningun adjunto. Comprueba "
                            "que -mp apunta a la carpeta WhatsApp del terminal "
                            "(la que contiene Media/)." + Fore.RESET)


def mode_messages(ext, flt, args, out_dir):
    """Modo mensajes: lista por consola y/o genera informe."""
    chats = ext.chats()

    if args.web:
        print(Fore.YELLOW + "[i] Filtrando por mensajes de WhatsApp Web" + Fore.RESET)
    if args.broadcast:
        chats = [c for c in chats if c.is_broadcast]

    total = 0
    seleccion = []
    for c in chats:
        msgs = [m for m in c.messages if flt.match(m, c.label)]
        if args.web:
            msgs = [m for m in msgs
                    if reader.infer_device(m.key_id) == "WhatsApp Web"]
        if msgs:
            seleccion.append((c, msgs))
            total += len(msgs)

    if not total:
        print(Fore.RED + "[!] Ningun mensaje cumple los criterios." + Fore.RESET)
        return None

    print("[i] {} mensaje(s) en {} chat(s)".format(total, len(seleccion)))

    if not (args.report or args.print_report or args.csv):
        for c, msgs in seleccion:
            print("\n" + Fore.CYAN + "=== {} ({}) ===".format(c.label, c.chat_id) + Fore.RESET)
            for m in msgs[:args.limit]:
                quien = "Yo" if m.from_me else (m.sender_label or c.label)
                print("  [{}] {}{}: {}".format(
                    reader.fmt_ts(m.timestamp), quien,
                    "" if m.kind is codes.Kind.TEXT else " <{}>".format(m.type_desc),
                    (m.display_text or "").replace("\n", " ")[:160]))
            if len(msgs) > args.limit:
                print("  ... y {} mas (usa -r, -p o -x)".format(len(msgs) - args.limit))
    return seleccion


def mode_info(ext, opt, args):
    """Modo informacion: 1 estados, 2 registro de llamadas, 3 chats activos."""
    if opt == "1":
        print(Fore.RED + "Status" + Fore.RESET)
        msgs = [m for m in ext.messages if "status@broadcast" in (m.chat_id or "")]
        print("Number of messages: {}".format(len(msgs)))
        for m in msgs[:args.limit]:
            print("  [{}] {} : {}".format(reader.fmt_ts(m.timestamp),
                                          m.sender or "", m.display_text[:120]))

    elif opt == "2":
        print(Fore.RED + "Calls" + Fore.RESET)
        calls = ext.calls
        ts0, ts1 = parse_time(args.time_start), parse_time(args.time_end)
        if ts0:
            calls = [c for c in calls if c.timestamp and c.timestamp >= ts0]
        if ts1:
            calls = [c for c in calls if c.timestamp and c.timestamp <= ts1]
        print("Number of calls: {}".format(len(calls)))
        for c in calls[:args.limit]:
            print("  [{}] {} {} {} {}".format(
                reader.fmt_ts(c.timestamp), reader.short_jid(c.jid),
                "saliente" if c.from_me else "entrante",
                "video" if c.video else "audio",
                "{}s {}".format(c.duration or 0, c.result or "")))
        if not calls:
            print(Fore.YELLOW + "  (sin registro de llamadas en esta base)" + Fore.RESET)

    elif opt == "3":
        print(Fore.RED + "Active chat list" + Fore.RESET)
        chats = ext.chats()
        print("Number of chats: {}".format(len(chats)))
        print("  {:<34} {:<26} {:>8}  {}".format("CHAT", "JID", "MSGS", "ULTIMO (UTC)"))
        for c in chats:
            print("  {:<34} {:<26} {:>8}  {}".format(
                c.label[:34], (c.chat_id or "")[:26], len(c.messages),
                reader.fmt_ts(c.last_ts)))
    elif opt == "4":
        print(Fore.RED + "Uncatalogued message types" + Fore.RESET)
        print("WhatsApp anade tipos nuevos con cada version. Los que aun no")
        print("estan en whacodes.py aparecen aqui con ejemplos, para poder")
        print("identificarlos y anadirlos.\n")
        sin_catalogar = {}
        for m in ext.messages:
            if m.kind is codes.Kind.UNKNOWN and m.raw_type is not None:
                sin_catalogar.setdefault(m.raw_type, []).append(m)
        if not sin_catalogar:
            print(Fore.GREEN + "  Todos los tipos presentes estan catalogados."
                  + Fore.RESET)
            return
        for t in sorted(sin_catalogar):
            msgs = sin_catalogar[t]
            con_texto = sum(1 for x in msgs if x.text)
            con_media = sum(1 for x in msgs if x.media_path)
            con_coord = sum(1 for x in msgs if x.latitude is not None)
            del_sistema = sum(1 for x in msgs if x.system_action)
            enviados = sum(1 for x in msgs if x.from_me)
            print(Fore.CYAN + "  Codigo {}".format(t) + Fore.RESET +
                  "  ({} mensaje(s))".format(len(msgs)))
            print("    con texto {} | con archivo {} | con coordenadas {} | "
                  "de sistema {} | enviados por el usuario {}".format(
                      con_texto, con_media, con_coord, del_sistema, enviados))
            for x in msgs[:3]:
                print("      [{}] {} -> {}".format(
                    reader.fmt_ts(x.timestamp),
                    x.sender_label or ("yo" if x.from_me else "?"),
                    (x.text or x.media_path or "(sin contenido en la tabla message)"
                     )[:70].replace("\n", " ")))
            print()
        print("Si identificas alguno, se anade en libs/whacodes.py y queda")
        print("disponible en todo el proyecto.")

    else:
        sys.exit("[e] Opcion de -i no valida: usa 1, 2, 3 o 4")


def mode_extract(ext, out_dir):
    """Modo extraccion: copia los adjuntos referenciados que existan en disco."""
    destino = os.path.join(out_dir, "extracted")
    os.makedirs(destino, exist_ok=True)
    con_ruta = [m for m in ext.messages if m.media_path]
    print("[i] {} mensaje(s) con archivo referenciado".format(len(con_ruta)))
    copiados = faltan = 0
    listado = os.path.join(destino, "_indice_adjuntos.txt")
    with open(listado, "w", encoding="utf-8") as fh:
        fh.write("fecha_utc\tchat\tdireccion\ttipo\truta_en_la_base\testado\n")
        for m in con_ruta:
            origen = m.media_path
            estado = "no encontrado"
            if origen and os.path.isfile(origen):
                try:
                    shutil.copy2(origen, os.path.join(destino, os.path.basename(origen)))
                    estado = "copiado"
                    copiados += 1
                except OSError as e:
                    estado = "error: {}".format(e)
            else:
                faltan += 1
            fh.write("{}\t{}\t{}\t{}\t{}\t{}\n".format(
                reader.fmt_ts(m.timestamp), m.chat_id,
                "enviado" if m.from_me else "recibido", m.type_desc, origen, estado))
    print("[-] {} archivo(s) copiado(s), {} no localizado(s)".format(copiados, faltan))
    print("[-] Indice: {}".format(listado))
    print(Fore.YELLOW + "[i] La base guarda rutas, no los archivos. Los que no se "
                        "localizan hay que aportarlos desde el volcado del terminal."
          + Fore.RESET)


def mode_carving(db_path, out_dir):
    """Carving con undark, si el binario esta disponible."""
    binario = "undark.exe" if os.name == "nt" else "undark"
    ruta = os.path.join(abs_path, binario)
    if not os.path.exists(ruta):
        print(Fore.RED + "[e] No se encuentra {} en libs/".format(binario) + Fore.RESET)
        return
    salida = os.path.join(out_dir, "carving.txt")
    try:
        with open(salida, "w", encoding="utf-8", errors="replace") as fh:
            subprocess.run([ruta, "--file", db_path, "--freespace"],
                           stdout=fh, stderr=subprocess.DEVNULL, check=False)
        print("[-] Carving guardado en {}".format(salida))
    except OSError as e:
        print(Fore.RED + "[e] No se pudo ejecutar undark: {}".format(e) + Fore.RESET)


# ===========================================================================
#  Linea de ordenes
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(
        description="To start choose a database and a mode with options",
        epilog="""Ejemplos:
  Listar los chats activos:
    python3 whapa.py msgstore.db -i 3
  Ver la conversacion con un numero:
    python3 whapa.py msgstore.db -m -u 34123456789 -wa wa.db
  Informe interactivo de todo (aguanta cualquier tamano):
    python3 whapa.py msgstore.db -m -a -r ES -o ./informe
  Informe imprimible de un chat y un rango de fechas:
    python3 whapa.py msgstore.db -m -u 34123456789 -ts "01-01-2024 00:00" \\
            -te "30-06-2024 23:59" -p -o ./salida
  Buscar texto con expresion regular y exportar a CSV:
    python3 whapa.py msgstore.db -m -a -t "transferenc\\w+" -re -x -o ./salida
  iOS (se autodetecta):
    python3 whapa.py ChatStorage.sqlite -m -a -r ES -o ./informe""",
        formatter_class=argparse.RawDescriptionHelpFormatter)

    parser.add_argument("database", help="Database file path - './msgstore.db' by default",
                        metavar="DATABASE", nargs='?', default="./msgstore.db")

    mode_parser = parser.add_argument_group("modes")
    mode_parser.add_argument("-m", "--messages", help="*** Message Mode ***", action="store_true")
    mode_parser.add_argument("-i", "--info",
                             help="*** Info Mode *** 1 Status - 2 Calls log - "
                                  "3 Actives chat list - 4 Uncatalogued message types")
    mode_parser.add_argument("-e", "--extract", help="*** Extract Mode ***", action="store_true")

    user_parser = parser.add_argument_group("recipients")
    user_parser.add_argument("-u", "--user", help="Show chat with a phone number, ej. 34123456789")
    user_parser.add_argument("-ua", "--user_all", help="Show messages made by a phone number")
    user_parser.add_argument("-g", "--group", help="Show chat with a group number, ej. 34123456-14508@g.us")
    user_parser.add_argument("-a", "--all", help="Show all chat messages", action="store_true")

    parser.add_argument("-wa", "--wa_file", help="Show names along with numbers (wa.db / ContactsV2.sqlite)")
    parser.add_argument("-o", "--output", help="Output path")
    parser.add_argument("-c", "--carving", help="Carving in the database", action="store_true")
    parser.add_argument("-mp", "--media_path",
                        help="WhatsApp folder copied from the phone, so the report "
                             "can show images and play audio/video")
    parser.add_argument("-cm", "--copy_media", action="store_true",
                        help="Copy the attachments into the report folder")
    parser.add_argument("-gm", "--maps", action="store_true",
                        help="Download a static map for each location and store it "
                             "inside the report (needs internet while generating)")
    parser.add_argument("--platform", choices=[codes.ANDROID, codes.ANDROID_LEGACY, codes.IOS],
                        help="Force platform (default: autodetect)")
    parser.add_argument("--limit", type=int, default=50,
                        help="Max messages shown on console (default 50)")

    out_parser = parser.add_argument_group("output")
    out_parser.add_argument("-r", "--report", nargs='?', const='EN', choices=['EN', 'ES'],
                            help="Make an interactive html report in 'EN' or 'ES'")
    out_parser.add_argument("-p", "--print_report", action="store_true",
                            help="Make a printable html report (paper / PDF)")
    out_parser.add_argument("-x", "--csv", action="store_true",
                            help="Export the selected messages to CSV")
    out_parser.add_argument("-k", "--kml", action="store_true",
                            help="Export the locations to KML (Google Earth, QGIS)")
    out_parser.add_argument("-1", "--single_file", action="store_true",
                            help="Interactive report as a single html file")

    f_parser = parser.add_argument_group("filters")
    f_parser.add_argument("-t", "--text", help="Show messages by text match")
    f_parser.add_argument("-re", "--regex", action="store_true",
                          help="Treat -t as a regular expression")
    f_parser.add_argument("-cs", "--case_sensitive", action="store_true",
                          help="Case sensitive text match")
    f_parser.add_argument("-ww", "--whole_word", action="store_true",
                          help="Match whole words only")
    f_parser.add_argument("-sn", "--sender", help="Show messages by sender")
    f_parser.add_argument("-d", "--direction", choices=["sent", "received", "system"],
                          help="Only sent, received or system messages")
    f_parser.add_argument("-w", "--web", help="Show messages made by Whatsapp Web", action="store_true")
    f_parser.add_argument("-s", "--starred", help="Show messages starred by owner", action="store_true")
    f_parser.add_argument("-b", "--broadcast", help="Show messages send by broadcast", action="store_true")
    f_parser.add_argument("-fw", "--forwarded", help="Show forwarded messages", action="store_true")
    f_parser.add_argument("-ed", "--edited", help="Show edited messages", action="store_true")
    f_parser.add_argument("-md", "--only_media", help="Show messages with attachment", action="store_true")
    f_parser.add_argument("-gp", "--only_location", help="Show messages with coordinates", action="store_true")
    f_parser.add_argument("-lr", "--only_read", action="store_true",
                          help="Only messages the recipient is recorded as having opened")
    f_parser.add_argument("-lu", "--only_unread", action="store_true",
                          help="Only messages with no read confirmation")
    f_parser.add_argument("-ts", "--time_start", help="Show messages by start time (dd-mm-yyyy HH:MM)")
    f_parser.add_argument("-te", "--time_end", help="Show messages by end time (dd-mm-yyyy HH:MM)")
    f_parser.add_argument("-rt", "--raw_types", help="Native type codes, comma separated (ej. 66,112)")

    t_parser = parser.add_argument_group("message types")
    t_parser.add_argument("-tt", "--type_text", help="Show text messages", action="store_true")
    t_parser.add_argument("-ti", "--type_image", help="Show image messages", action="store_true")
    t_parser.add_argument("-ta", "--type_audio", help="Show audio messages", action="store_true")
    t_parser.add_argument("-tv", "--type_video", help="Show video messages", action="store_true")
    t_parser.add_argument("-tc", "--type_contact", help="Show contact messages", action="store_true")
    t_parser.add_argument("-tl", "--type_location", help="Show location messages", action="store_true")
    t_parser.add_argument("-tx", "--type_call", help="Show audio/video call messages", action="store_true")
    t_parser.add_argument("-tp", "--type_application", help="Show application messages", action="store_true")
    t_parser.add_argument("-tg", "--type_gif", help="Show GIF messages", action="store_true")
    t_parser.add_argument("-td", "--type_deleted", help="Show deleted object messages", action="store_true")
    t_parser.add_argument("-tr", "--type_share", help="Show Real time location messages", action="store_true")
    t_parser.add_argument("-tk", "--type_stickers", help="Show Stickers messages", action="store_true")
    t_parser.add_argument("-tm", "--type_system", help="Show system messages", action="store_true")
    t_parser.add_argument("-tn", "--type_poll", help="Show poll messages (new)", action="store_true")
    t_parser.add_argument("-tq", "--type_viewonce", help="Show view once messages (new)", action="store_true")
    t_parser.add_argument("-tj", "--type_videonote", help="Show video note messages (new)", action="store_true")
    t_parser.add_argument("-tz", "--type_event", help="Show event messages (new)", action="store_true")

    if len(sys.argv) == 1:
        banner(); help(); parser.print_help(); sys.exit(0)

    args = parser.parse_args()
    banner()

    if not (args.messages or args.info or args.extract or args.carving):
        sys.exit("[e] Elige un modo: -m (mensajes), -i (informacion), "
                 "-e (extraccion) o -c (carving)")

    # Sin -o, el informe va al directorio actual. Nunca dentro de libs/: si la
    # herramienta se invoca desde ahi, se sube a la raiz del proyecto.
    out_dir = args.output
    if not out_dir:
        actual = os.path.abspath(os.getcwd())
        out_dir = whapa_path if actual == os.path.abspath(abs_path) else actual
        print("[i] Sin -o: el informe se guardara en {}".format(out_dir))
    out_dir = os.path.abspath(out_dir)
    os.makedirs(out_dir, exist_ok=True)

    if args.carving:
        mode_carving(args.database, out_dir)
        if not (args.messages or args.info or args.extract):
            return

    try:
        platform = args.platform or reader.detect_platform(args.database)
    except Exception as e:
        sys.exit("[e] {}".format(e))

    print("[i] Plataforma: {}".format(codes.PLATFORM_LABEL.get(platform, platform)))
    print("[i] Cargando datos ...")
    ext = reader.read(args.database, platform, args.wa_file)
    s = ext.summary()
    print("[i] {} mensajes - {} chats - {} contactos".format(
        s["total"], s["chats"], s["contacts"]))
    if getattr(ext, "damaged_text", 0):
        print(Fore.YELLOW + "[!] {} texto(s) con bytes no validos en el origen. "
                            "Se conserva lo legible y lo danado se marca con el "
                            "caracter \ufffd.".format(ext.damaged_text) + Fore.RESET)

    if args.info:
        mode_info(ext, args.info, args)
        print("\n[i] Finished")
        return

    if args.extract:
        mode_extract(ext, out_dir)
        print("\n[i] Finished")
        return

    # ---- modo mensajes ----
    flt = build_filter(args)
    if not (args.user or args.group or args.user_all or args.all or args.broadcast
            or not flt.is_empty()):
        sys.exit("[e] Elige destinatario (-u, -ua, -g, -a) o algun filtro")

    if not flt.is_empty():
        print("[i] Criterios aplicados:")
        for k, v in flt.describe():
            print("    {:<26} {}".format(k, v))

    seleccion = mode_messages(ext, flt, args, out_dir)
    if seleccion is None:
        return

    cfg = get_configs()
    titulo = cfg.get("record") or "Informe forense WhatsApp"
    lang = args.report or "ES"

    if args.report:
        destino = (os.path.join(out_dir, "report.html") if args.single_file
                   else os.path.join(out_dir, "report"))
        r = report.build_report(ext, destino, title=titulo,
                                single_file=args.single_file, lang=lang, flt=flt,
                                media_root=args.media_path,
                                copy_media=args.copy_media, maps=args.maps)
        print("[-] Informe interactivo: {}".format(r["path"]))
        _aviso_media(args, r)
        if r["mode"] == "folder":
            print("    HTML inicial {:.1f} KB - datos {:.1f} MB en {} paginas".format(
                r["shell_size"] / 1024, r["data_size"] / 1048576, r["pages"]))

    if args.print_report:
        destino = os.path.join(out_dir, "report_print.html")
        r = report.build_printable(ext, destino, title=titulo, flt=flt,
                                   case_ref=cfg.get("record") or None,
                                   examiner=cfg.get("examiner") or None,
                                   media_root=args.media_path,
                                   copy_media=args.copy_media)
        print("[-] Informe imprimible: {} ({} mensajes, ~{} hojas A4)".format(
            r["path"], r["messages"], max(1, r["messages"] // 45)))
        _aviso_media(args, r)
        if r["truncated"]:
            print(Fore.YELLOW + "[!] Documento truncado: afina los filtros." + Fore.RESET)

    if args.csv:
        destino = os.path.join(out_dir, "messages.csv")
        report.export_csv(report.search(ext, flt), destino)
        print("[-] CSV exportado: {}".format(destino))

    if args.kml:
        destino = os.path.join(out_dir, "locations.kml")
        n = report.export_kml(report.search(ext, flt), destino, titulo)
        if n:
            print("[-] KML exportado: {} ({} ubicacion(es))".format(destino, n))
        else:
            os.remove(destino)
            print(Fore.YELLOW + "[!] Ninguna ubicacion cumple los criterios; "
                                "no se ha generado el KML." + Fore.RESET)

    print("\n[i] Finished")


if __name__ == "__main__":
    main()

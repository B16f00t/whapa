#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
test_whapa.py - Pruebas de humo de WhaPa 2.00

Uso:  python3 doc/test_whapa.py

Crea bases de datos de prueba que reproducen los esquemas de Android e iOS y
comprueba que cada herramienta hace su trabajo. No necesita material real.
"""
import os
import sys
import sqlite3
import tempfile

RAIZ = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(RAIZ, "libs"))

import whacodes as codes
import whacipher
import whareader as reader
import whareport as report


def _db_android(path, n=60):
    con = sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    CREATE TABLE message_system(message_row_id INT, action_type INT);
    INSERT INTO jid VALUES (1,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1);""")
    for i in range(1, n + 1):
        con.execute("INSERT INTO message VALUES (?,?,?,?,?,?,?,?,?)",
                    (i, 1, i % 2, "K" * 32, 1, 1700000000000 + i * 1000,
                     0 if i % 3 else 66, "t%d" % i, 1 if i == 5 else 0))
    con.execute("INSERT INTO message_system VALUES (3,12)")
    con.commit(); con.close()


def _db_ios(path, n=60):
    con = sqlite3.connect(path)
    con.executescript("""
    CREATE TABLE ZWACHATSESSION(Z_PK INTEGER PRIMARY KEY, ZCONTACTJID TEXT, ZPARTNERNAME TEXT);
    CREATE TABLE ZWAMESSAGE(Z_PK INTEGER PRIMARY KEY, ZCHATSESSION INT, ZISFROMME INT,
      ZGROUPMEMBER INT, ZMESSAGEDATE REAL, ZMESSAGETYPE INT, ZTEXT TEXT,
      ZSTANZAID TEXT, ZSTARRED INT, ZFROMJID TEXT, ZMEDIAITEM INT);
    INSERT INTO ZWACHATSESSION VALUES (1,'34600111222@s.whatsapp.net','Juan');""")
    for i in range(1, n + 1):
        con.execute("INSERT INTO ZWAMESSAGE VALUES (?,?,?,?,?,?,?,?,?,?,?)",
                    (i, 1, i % 2, None, 721692800 + i * 60, 0 if i % 3 else 46,
                     "t%d" % i, "5E" + "0" * 18, 0, None, None))
    con.commit(); con.close()


def test_codigos():
    assert codes.kind_of(codes.ANDROID, 66) is codes.Kind.POLL
    assert codes.kind_of(codes.IOS, 46) is codes.Kind.POLL
    assert codes.kind_of(codes.ANDROID, 112) is codes.Kind.ADVANCED_PRIVACY
    assert codes.is_deleted(codes.ANDROID, 64) and codes.is_deleted(codes.IOS, 14)
    assert codes.kind_of(codes.ANDROID, 99999) is codes.Kind.UNKNOWN
    assert "comunidad" in codes.system_action_description(12).lower()
    print("  whacodes: catalogo de codigos OK")


def test_cipher():
    d = tempfile.mkdtemp()
    src = os.path.join(d, "a.db"); _db_android(src, 5)
    original = open(src, "rb").read()
    clave = "aa" * 32
    enc, dec = os.path.join(d, "a.crypt15"), os.path.join(d, "b.db")
    whacipher.encrypt(src, clave, enc)
    cab = whacipher.parse_header(open(enc, "rb").read())
    assert cab["version"] == "crypt15" and len(cab["iv"]) == 16
    whacipher.decrypt(enc, clave, dec)
    assert open(dec, "rb").read() == original
    print("  whacipher: crypt15 ida y vuelta byte a byte OK")


def test_lector():
    d = tempfile.mkdtemp()
    for nombre, crea, plat in (("msgstore.db", _db_android, codes.ANDROID),
                               ("ChatStorage.sqlite", _db_ios, codes.IOS)):
        p = os.path.join(d, nombre); crea(p)
        assert reader.detect_platform(p) == plat
        ext = reader.read(p)
        s = ext.summary()
        assert s["total"] == 60 and s["chats"] == 1
        assert len(ext.source_files[0]["sha256"]) == 64
        print("  whareader: {} detectado y leido OK".format(plat))


def test_filtros_e_informes():
    d = tempfile.mkdtemp()
    p = os.path.join(d, "msgstore.db"); _db_android(p)
    ext = reader.read(p)

    assert len(report.search(ext, report.Filter(text="t7"))) == 1
    assert len(report.search(ext, report.Filter(text="T7", case_sensitive=True))) == 0
    assert len(report.search(ext, report.Filter(text=r"^t[12]$", regex=True))) == 2
    assert len(report.search(ext, report.Filter(text="t", whole_word=True))) == 0
    assert len(report.search(ext, report.Filter(raw_types={66}))) == 20
    assert len(report.search(ext, report.Filter(only_starred=True))) == 1
    env = len(report.search(ext, report.Filter(direction="sent")))
    rec = len(report.search(ext, report.Filter(direction="received")))
    sis = len(report.search(ext, report.Filter(direction="system")))
    # el fixture incluye un mensaje de sistema, que no es ni enviado ni recibido
    assert sis == 1 and env + rec + sis == 60
    assert report.Filter().is_empty()
    print("  whareport: motor de filtrado OK")

    # informe interactivo: el HTML inicial no debe crecer con los mensajes
    tam = []
    for n in (50, 5000):
        q = os.path.join(d, "m%d.db" % n); _db_android(q, n)
        r = report.build_report(reader.read(q), os.path.join(d, "r%d" % n))
        tam.append(r["shell_size"])
    assert abs(tam[0] - tam[1]) < 2000, "el HTML inicial crece con los mensajes"
    print("  whareport: informe interactivo de tamano constante OK")

    # idiomas
    for lang, marca in (("ES", ">Buscar</button>"), ("EN", ">Search</button>")):
        r = report.build_report(ext, os.path.join(d, "l" + lang), lang=lang)
        assert marca in open(r["path"], encoding="utf-8").read()
    print("  whareport: informe en ES y EN OK")

    # imprimible con criterios documentados
    flt = report.Filter(text="t1", direction="sent")
    out = os.path.join(d, "print.html")
    r = report.build_printable(ext, out, flt=flt, case_ref="REF-1", max_messages=999)
    cuerpo = open(out, encoding="utf-8").read()
    assert "<script" not in cuerpo, "el imprimible no debe llevar JavaScript"
    assert "@page" in cuerpo and "Criterios de selección" in cuerpo
    assert "«t1»" in cuerpo and "REF-1" in cuerpo
    assert r["selected"] == r["messages"]
    print("  whareport: informe imprimible con criterios OK")

    # el informe interactivo respeta el filtro
    r1 = report.build_report(ext, os.path.join(d, "sf"))
    r2 = report.build_report(ext, os.path.join(d, "cf"), flt=report.Filter(raw_types={66}))
    assert r2["pages"] <= r1["pages"]
    print("  whareport: el informe interactivo respeta el filtro OK")

    # CSV
    hits = report.search(ext, report.Filter(text="t1"))
    csvp = os.path.join(d, "h.csv")
    report.export_csv(hits, csvp)
    cuerpo = open(csvp, encoding="utf-8-sig").read()
    assert cuerpo.startswith("n;chat;chat_jid;fecha_utc")
    assert len(cuerpo.strip().split("\n")) == len(hits) + 1
    print("  whareport: exportacion CSV OK")


def test_adjuntos():
    """Si se aporta la carpeta WhatsApp, el informe debe enlazar los archivos."""
    import struct, zlib, wave
    d = tempfile.mkdtemp()
    wa = os.path.join(d, "WhatsApp")
    os.makedirs(os.path.join(wa, "Media", "WhatsApp Images"))
    os.makedirs(os.path.join(wa, "Media", "WhatsApp Audio"))

    img = os.path.join(wa, "Media", "WhatsApp Images", "IMG-1.jpg")
    raw = b"".join(b"\x00" + bytes((0, 168, 132)) * 4 for _ in range(4))
    def ch(t, x):
        c = t + x
        return struct.pack(">I", len(x)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    open(img, "wb").write(b"\x89PNG\r\n\x1a\n"
                          + ch(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
                          + ch(b"IDAT", zlib.compress(raw)) + ch(b"IEND", b""))
    aud = os.path.join(wa, "Media", "WhatsApp Audio", "AUD-1.wav")
    with wave.open(aud, "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(b"\x00\x01" * 400)

    db = os.path.join(d, "msgstore.db")
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    CREATE TABLE message_media(message_row_id INT, chat_row_id INT, file_path TEXT,
      mime_type TEXT, file_size INT, media_caption TEXT);
    INSERT INTO jid VALUES (1,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1);
    INSERT INTO message VALUES (1,1,0,'K',1,1705300000000,1,NULL,0);
    INSERT INTO message VALUES (2,1,1,'K',NULL,1705300100000,2,NULL,0);
    INSERT INTO message VALUES (3,1,0,'K',1,1705300200000,1,NULL,0);""")
    # ruta absoluta del terminal, ruta relativa, y una que no existe
    con.executemany("INSERT INTO message_media VALUES (?,?,?,?,?,?)", [
        (1, 1, "/storage/emulated/0/WhatsApp/Media/WhatsApp Images/IMG-1.jpg",
         "image/jpeg", 72, None),
        (2, 1, "Media/WhatsApp Audio/AUD-1.wav", "audio/wav", 844, None),
        (3, 1, "/storage/emulated/0/WhatsApp/Media/WhatsApp Images/NO-EXISTE.jpg",
         "image/jpeg", 0, None)])
    con.commit(); con.close()

    ext = reader.read(db)

    # sin carpeta: no se localiza nada, pero el informe se genera igual
    r0 = report.build_report(ext, os.path.join(d, "sin"))
    assert r0["media_found"] == 0

    # con carpeta y copia: 2 de 3 localizados
    r1 = report.build_report(ext, os.path.join(d, "con"),
                             media_root=wa, copy_media=True)
    assert r1["media_found"] == 2 and r1["media_missing"] == 1, r1
    copiados = os.listdir(os.path.join(d, "con", "media"))
    assert "IMG-1.jpg" in copiados and "AUD-1.wav" in copiados

    # el dato del adjunto viaja en el archivo de datos del informe
    datos = open(os.path.join(d, "con", "data", "c0000_p0000.js"),
                 encoding="utf-8").read()
    assert "media/IMG-1.jpg" in datos and "media/AUD-1.wav" in datos

    # el imprimible incrusta la miniatura y deja constancia de la ruta original
    out = os.path.join(d, "print.html")
    report.build_printable(ext, out, media_root=wa, copy_media=True,
                           max_messages=99)
    cuerpo = open(out, encoding="utf-8").read()
    assert 'class="thumb"' in cuerpo
    assert "Ruta en la base" in cuerpo and "archivo no localizado" in cuerpo

    # el visor sabe pintar cada tipo
    assert "function mediaHtml" in report.JS and "<audio controls" in report.JS
    print("  whareport: adjuntos localizados, copiados y enlazados OK")


def test_ubicaciones():
    """Ubicaciones: bloque en el visor, KML valido y sin llamadas remotas."""
    import xml.etree.ElementTree as ET
    d = tempfile.mkdtemp()
    db = os.path.join(d, "msgstore.db")
    con = sqlite3.connect(db)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    CREATE TABLE message_location(message_row_id INT, chat_row_id INT,
      latitude REAL, longitude REAL);
    INSERT INTO jid VALUES (1,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1);
    INSERT INTO message VALUES (1,1,0,'K',1,1705300000000,5,NULL,0);
    INSERT INTO message VALUES (2,1,1,'K',NULL,1705300100000,16,NULL,0);
    INSERT INTO message VALUES (3,1,0,'K',1,1705300200000,0,'sin ubicacion',0);
    INSERT INTO message_location VALUES (1,1,36.72016,-4.42034);
    INSERT INTO message_location VALUES (2,1,40.41678,-3.70379);""")
    con.commit(); con.close()

    ext = reader.read(db)
    conubi = [m for m in ext.messages if m.latitude is not None]
    assert len(conubi) == 2

    # filtro por ubicacion
    assert len(report.search(ext, report.Filter(only_location=True))) == 2

    # KML valido y con las dos coordenadas
    kml = os.path.join(d, "loc.kml")
    n = report.export_kml(report.search(ext, report.Filter(only_location=True)), kml)
    assert n == 2
    raiz = ET.parse(kml).getroot()
    ns = {"k": "http://www.opengis.net/kml/2.2"}
    marcas = raiz.findall(".//k:Placemark", ns)
    assert len(marcas) == 2
    coords = [m.find(".//k:coordinates", ns).text for m in marcas]
    assert "-4.42034,36.72016,0" in coords, coords   # KML es lon,lat
    assert marcas[0].find(".//k:when", ns) is not None

    # sin ubicaciones no se inventa nada
    assert report.export_kml(
        report.search(ext, report.Filter(text="sin ubicacion")),
        os.path.join(d, "vacio.kml")) == 0

    # el visor pinta el bloque y NO enlaza imagenes remotas
    r = report.build_report(ext, os.path.join(d, "rep"))
    assert "function locHtml" in report.JS
    assert "openstreetmap.org" in report.JS and "google.com/maps" in report.JS
    datos = open(os.path.join(d, "rep", "data", "c0000_p0000.js"),
                 encoding="utf-8").read()
    assert "36.72016" in datos
    cuerpo = open(r["path"], encoding="utf-8").read()
    assert "staticmap" not in cuerpo, "el informe no debe pedir mapas al abrirse"
    assert 'src="http' not in cuerpo, "no debe haber recursos remotos en el HTML"
    print("  whareport: ubicaciones, KML y sin llamadas remotas OK")


def test_whachat_informes():
    """whachat debe generar los mismos informes que whapa."""
    import whachat
    d = tempfile.mkdtemp()
    chat = os.path.join(d, "Chat de WhatsApp con Juan.txt")
    open(chat, "w", encoding="utf-8").write(
        "25/8/20, 19:52:23 - Los mensajes y las llamadas estan cifrados de extremo a extremo.\n"
        "25/8/20, 19:52:30 - Juan Perez: Buenas\n"
        "25/8/20, 19:53:01 - Yo: te paso la foto\n"
        "25/8/20, 19:53:15 - Yo: IMG-1.jpg (archivo adjunto)\n"
        "25/8/20, 19:55:10 - Juan Perez: PTT-1.opus (archivo adjunto)\n")
    # adjuntos junto al chat, como los exporta WhatsApp
    import struct, zlib, wave
    raw = b"".join(b"\x00" + bytes((0, 168, 132)) * 4 for _ in range(4))
    def ch(t, x):
        c = t + x
        return struct.pack(">I", len(x)) + c + struct.pack(">I", zlib.crc32(c) & 0xffffffff)
    open(os.path.join(d, "IMG-1.jpg"), "wb").write(
        b"\x89PNG\r\n\x1a\n" + ch(b"IHDR", struct.pack(">IIBBBBB", 4, 4, 8, 2, 0, 0, 0))
        + ch(b"IDAT", zlib.compress(raw)) + ch(b"IEND", b""))
    with wave.open(os.path.join(d, "PTT-1.opus"), "wb") as w:
        w.setnchannels(1); w.setsampwidth(2); w.setframerate(8000)
        w.writeframes(b"\x00\x01" * 200)

    df = whachat.getDataFrame(chat, "android")
    assert len(df) == 5

    ext = whachat.to_extraction(df, "Yo", "%d/%m/%y %H:%M:%S", "android",
                                chat_name="Juan", source_file=chat)
    assert len(ext.messages) == 5
    tipos = {m.kind.value for m in ext.messages}
    assert "image" in tipos and "audio" in tipos and "system" in tipos
    # fechas resueltas aunque la mascara no sea la exacta
    ext2 = whachat.to_extraction(df, "Yo", "%d/%m/%Y %H:%M", "android")
    assert all(m.timestamp for m in ext2.messages), "las fechas deben resolverse igual"
    # direccion
    assert sum(1 for m in ext.messages if m.from_me) == 2
    # verificacion de origen
    assert len(ext.source_files[0]["sha256"]) == 64

    salida = os.path.join(d, "rep")
    hechos = whachat.informes(ext, salida, media_root=d, copy_media=True,
                              interactivo=True, imprimible=True, csv_out=True)
    clases = {c for c, _ in hechos}
    assert clases == {"interactivo", "imprimible", "csv"}
    for c, r in hechos:
        assert os.path.exists(r["path"])
        if c != "csv":
            assert r["media_found"] == 2, (c, r)
    # el informe interactivo es el mismo motor
    cuerpo = open(os.path.join(salida, "report", "index.html"), encoding="utf-8").read()
    assert "function runSearch" in cuerpo and "function mediaHtml" in cuerpo
    print("  whachat: mismos informes que whapa OK")


def test_consola_segura():
    """Imprimir emojis no debe abortar la herramienta (consola cp1252)."""
    import io
    import whadeps
    TXT = "mensaje con emoji \U0001f42d y acentos <<Bartolo>>"

    class FakeTTY(io.TextIOWrapper):
        def isatty(self):
            return True

    orig = sys.stdout
    try:
        # consola real cp1252: se conserva la codificacion, se reemplaza lo que no cabe
        buf = io.BytesIO()
        sys.stdout = FakeTTY(buf, encoding="cp1252", errors="strict")
        whadeps.safe_console()
        print(TXT)
        sys.stdout.flush()
        salida = buf.getvalue().decode("cp1252")
        assert "Bartolo" in salida and "acentos" in salida

        # salida canalizada: UTF-8 completo, emoji incluido
        buf2 = io.BytesIO()
        sys.stdout = io.TextIOWrapper(buf2, encoding="cp1252", errors="strict")
        whadeps.safe_console()
        print(TXT)
        sys.stdout.flush()
        assert "\U0001f42d" in buf2.getvalue().decode("utf-8")
    finally:
        sys.stdout = orig
    print("  consola: los emojis ya no abortan la ejecucion OK")


def test_lid():
    """Los identificadores LID no deben mostrarse como si fueran telefonos."""
    d = tempfile.mkdtemp()
    p = os.path.join(d, "m.db")
    con = sqlite3.connect(p)
    con.executescript("""
    CREATE TABLE jid(_id INTEGER PRIMARY KEY, raw_string TEXT);
    CREATE TABLE chat(_id INTEGER PRIMARY KEY, jid_row_id INT);
    CREATE TABLE message(_id INTEGER PRIMARY KEY, chat_row_id INT, from_me INT,
      key_id TEXT, sender_jid_row_id INT, timestamp INT, message_type INT,
      text_data TEXT, starred INT);
    INSERT INTO jid VALUES (1,'120363000000@g.us');
    INSERT INTO jid VALUES (2,'233749350498426@lid');
    INSERT INTO jid VALUES (3,'34600111222@s.whatsapp.net');
    INSERT INTO chat VALUES (1,1);
    INSERT INTO message VALUES (1,1,0,'K',2,1762844892000,0,'hola',0);""")
    con.commit(); con.close()

    # sin tabla de correspondencia: se marca como LID
    ext = reader.read(p)
    assert ext.messages[0].sender == "LID:233749350498426", ext.messages[0].sender

    # con tabla: se traduce al telefono
    con = sqlite3.connect(p)
    con.executescript("""
    CREATE TABLE lid_jid_map(lid_row_id INT, jid_row_id INT);
    INSERT INTO lid_jid_map VALUES (2,3);""")
    con.commit(); con.close()
    ext = reader.read(p)
    assert ext.messages[0].sender == "34600111222", ext.messages[0].sender
    print("  LID: marcado sin correspondencia y traducido con ella OK")


def test_gui_segura():
    gui = os.path.join(RAIZ, "whapa-gui.py")
    fuente = open(gui, encoding="utf-8").read()
    import ast
    arbol = ast.parse(fuente)
    # Se analiza el arbol, no el texto: la mencion en el comentario no cuenta
    for nodo in ast.walk(arbol):
        if isinstance(nodo, ast.Call) and isinstance(nodo.func, ast.Attribute):
            llamada = "{}.{}".format(
                getattr(nodo.func.value, "id", ""), nodo.func.attr)
            assert llamada not in ("os.system", "os.popen"), \
                "la interfaz no debe lanzar ordenes con " + llamada
    assert "subprocess.Popen" in fuente
    trabajo = fuente[fuente.index("def _work(self, argv):"):]
    for malo in ("filedialog.", "messagebox.", ".get()", "self.after("):
        assert malo not in trabajo, "acceso inseguro a Tk en el hilo de trabajo: " + malo
    print("  whapa-gui: sin os.system y sin tocar Tk desde el hilo de trabajo OK")


def test_sin_apis_obsoletas():
    import pathlib
    for f in pathlib.Path(os.path.join(RAIZ, "libs")).glob("wha*.py"):
        src = f.read_text(encoding="utf-8", errors="replace")
        assert "utcnow(" not in src, "{}: utcnow() obsoleto".format(f.name)
    assert sys.version_info >= (3, 11), "se requiere Python 3.11 o superior"
    print("  compatibilidad con Python 3.11+ OK")


if __name__ == "__main__":
    print("Pruebas de humo de WhaPa 2.00\n")
    test_codigos()
    test_cipher()
    test_lector()
    test_filtros_e_informes()
    test_adjuntos()
    test_ubicaciones()
    test_whachat_informes()
    test_consola_segura(); test_lid()
    test_gui_segura()
    test_sin_apis_obsoletas()
    print("\nTodas las pruebas han pasado.")

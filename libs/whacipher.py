#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
whacipher.py - Descifrado y cifrado de bases de datos de WhatsApp

COMETIDO DE ESTE ARCHIVO
    Convertir msgstore.db.crypt12 / .crypt14 / .crypt15 en un msgstore.db
    legible, y a la inversa. Nada mas: no lee mensajes ni genera informes.

QUE CAMBIA RESPECTO A LA VERSION ANTERIOR
    * Soporta crypt15 (copias cifradas de extremo a extremo, formato actual
      desde 2021), ademas de crypt12 y crypt14.
    * Ya no busca el inicio de los datos probando desplazamientos fijos a
      ciegas: analiza la cabecera protobuf del backup y extrae de ella el
      vector de inicializacion y el punto exacto donde empiezan los datos.
    * Deriva la clave de crypt15 con el bucle HMAC-SHA256 a partir de la clave
      raiz de 32 bytes.
    * Admite la clave como archivo .key de 158 bytes, como encrypted_backup.key
      o como 64 caracteres hexadecimales.
    * Autodetecta el formato: no hace falta indicarlo.

    Solo necesita pycryptodome. No requiere protobuf ni javaobj: la cabecera se
    analiza con un lector de varint incluido en este mismo archivo.

** Author: Ivan Moreno a.k.a B16f00t
** Github: https://github.com/B16f00t
"""

import os
import sys
import hmac
import zlib
import math
import argparse
from hashlib import sha256, md5

try:
    from Crypto.Cipher import AES
except ImportError:
    try:
        from Cryptodome.Cipher import AES
    except ImportError:
        sys.exit("Falta pycryptodome. Instalalo con: pip install pycryptodome")

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import whadeps
whadeps.safe_console()

version = "2.00"


def banner():
    """ Function Banner """
    print(r"""
     __      __.__            _________ .__       .__
    /  \    /  \  |__ _____   \_   ___ \|__|_____ |  |__   ___________
    \   \/\/   /  |  \\__  \  /    \  \/|  \____ \|  |  \_/ __ \_  __ \
     \        /|   Y  \/ __ \_\     \___|  |  |_> >   Y  \  ___/|  | \/
      \__/\  / |___|  (____  / \______  /__|   __/|___|  /\___  >__|
           \/       \/     \/         \/   |__|        \/     \/
    ------------- Whatsapp Cipher v{} -------------
    """.format(version))


def help():
    """ Function show help """
    print("""    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t

    Usage: python3 whacipher.py -h (for help)
    """)


# ===========================================================================
#  Lector protobuf mínimo (solo lo necesario para la cabecera del backup)
# ===========================================================================
def _read_varint(buf, pos):
    """Lee un varint de protobuf. Devuelve (valor, nueva_pos)."""
    result = 0
    shift = 0
    while True:
        b = buf[pos]
        pos += 1
        result |= (b & 0x7F) << shift
        if not (b & 0x80):
            break
        shift += 7
    return result, pos


def _iter_fields(buf):
    """Itera los campos de nivel superior de un mensaje protobuf.
    Devuelve tuplas (numero_campo, wire_type, valor_bytes_o_int)."""
    pos = 0
    n = len(buf)
    while pos < n:
        tag, pos = _read_varint(buf, pos)
        field_no = tag >> 3
        wire = tag & 0x07
        if wire == 0:            # varint
            val, pos = _read_varint(buf, pos)
            yield field_no, wire, val
        elif wire == 2:          # length-delimited (bytes / submensaje)
            length, pos = _read_varint(buf, pos)
            val = buf[pos:pos + length]
            pos += length
            yield field_no, wire, val
        elif wire == 5:          # 32-bit
            val = buf[pos:pos + 4]; pos += 4
            yield field_no, wire, val
        elif wire == 1:          # 64-bit
            val = buf[pos:pos + 8]; pos += 8
            yield field_no, wire, val
        else:
            raise ValueError("Wire type protobuf no soportado: {}".format(wire))


def parse_header(db_data):
    """Parsea la cabecera de un backup crypt14/15.

    Formato del fichero:
        [1 byte: tamaño del protobuf][?1 byte 0x01: tabla de features][protobuf]

    Devuelve dict con: version ('crypt14'|'crypt15'), iv (16 bytes),
    header_len (offset donde empiezan los datos cifrados).
    """
    protobuf_size = db_data[0]
    pos = 1
    # Byte opcional 0x01 = presencia de la tabla de features (solo msgstore)
    if len(db_data) > 1 and db_data[1] == 0x01:
        pos = 2
    protobuf_raw = db_data[pos:pos + protobuf_size]
    header_len = pos + protobuf_size

    version = None
    iv = None
    for field_no, wire, val in _iter_fields(protobuf_raw):
        if field_no == 2 and wire == 2:      # c14_cipher (crypt14)
            version = "crypt14"
            for sub_no, sub_wire, sub_val in _iter_fields(val):
                if sub_no == 5 and sub_wire == 2:   # C14_cipher.IV
                    iv = sub_val
        elif field_no == 3 and wire == 2:    # c15_iv (crypt15)
            version = "crypt15"
            for sub_no, sub_wire, sub_val in _iter_fields(val):
                if sub_no == 1 and sub_wire == 2:   # C15_IV.IV
                    iv = sub_val
    if iv is None or len(iv) != 16:
        raise ValueError("No se pudo extraer un IV de 16 bytes de la cabecera")
    return {"version": version, "iv": bytes(iv), "header_len": header_len}


# ===========================================================================
#  Derivación de clave crypt15  (idéntico a wa-crypt-tools encryptionloop)
# ===========================================================================
def _encryption_loop(first_iteration_data, message, output_bytes=32,
                     privateseed=b"\x00" * 32):
    """Bucle HMAC-SHA256 anidado que usa WhatsApp para derivar subclaves."""
    privatekey = hmac.new(privateseed, msg=first_iteration_data, digestmod=sha256).digest()
    data = b""
    output = b""
    permutations = int(math.ceil(output_bytes / 32.0))
    for i in range(1, permutations + 1):
        hasher = hmac.new(privatekey, msg=data, digestmod=sha256)
        if message is not None:
            hasher.update(message)
        hasher.update(i.to_bytes(1, byteorder="big"))
        data = hasher.digest()
        output += data[:min(output_bytes, len(data))]
    return output


def derive_key(root_key):
    """A partir de la clave raíz (32 B) obtiene la clave AES de cifrado."""
    return _encryption_loop(root_key, b"backup encryption", 32)


# ===========================================================================
#  Carga de la clave
# ===========================================================================
def load_key(key_source):
    """Carga una clave desde una ruta de archivo o una cadena hex.

    Devuelve (raw_key_32bytes, es_crypt15_root).
      - es_crypt15_root=True  -> raw_key es la clave RAÍZ crypt15 (32 B)
      - es_crypt15_root=False -> raw_key es la clave AES directa (crypt12/14)
    """
    # ¿Cadena hexadecimal de 64 caracteres? -> clave raíz crypt15
    if isinstance(key_source, str) and len(key_source.strip()) == 64:
        try:
            return bytes.fromhex(key_source.strip()), True
        except ValueError:
            pass

    if not os.path.exists(key_source):
        raise FileNotFoundError("No existe la clave: {}".format(key_source))

    with open(key_source, "rb") as fh:
        key_data = fh.read()

    if len(key_data) == 158:
        # Archivo .key clásico crypt12/14: la clave AES está en [126:158]
        return key_data[126:158], False
    if len(key_data) == 32:
        # Clave raíz crypt15 en binario
        return key_data, True
    # encrypted_backup.key (objeto Java serializado): la raíz son los 32 B finales
    if len(key_data) > 32:
        return key_data[-32:], True
    raise ValueError("Formato de clave no reconocido ({} bytes)".format(len(key_data)))


# ===========================================================================
#  Descifrado
# ===========================================================================
def _maybe_decompress(plaintext):
    """Descomprime zlib si procede; si no está comprimido, devuelve tal cual."""
    if plaintext[:2] == b"\x78" and plaintext[2:3] in (b"\x01", b"\x5e", b"\x9c", b"\xda"):
        try:
            return zlib.decompress(plaintext)
        except zlib.error:
            pass
    # Un SQLite empieza por "SQLite format 3\x00"
    if plaintext[:15] == b"SQLite format 3":
        return plaintext
    try:
        return zlib.decompress(plaintext)
    except zlib.error:
        return plaintext


def decrypt(db_file, key_source, output):
    """Descifra un backup WhatsApp autodetectando crypt12/14/15.

    Devuelve True si tiene éxito.
    """
    with open(db_file, "rb") as fh:
        db_data = fh.read()

    ext = os.path.splitext(db_file)[1].lower()
    raw_key, is_root = load_key(key_source)

    # --- crypt12: cabecera fija de 67 bytes, cola de 20 bytes ---
    if ext == ".crypt12":
        iv = db_data[51:67]
        data = db_data[67:-20]
        aes = AES.new(raw_key, AES.MODE_GCM, nonce=iv)
        plain = _maybe_decompress(aes.decrypt(data))
        with open(output, "wb") as fh:
            fh.write(plain)
        return True

    # --- crypt14 / crypt15: cabecera protobuf ---
    header = parse_header(db_data)
    iv = header["iv"]
    encrypted = db_data[header["header_len"]:]

    if header["version"] == "crypt15":
        aes_key = derive_key(raw_key) if is_root else raw_key
        # crypt15: los últimos 16 B son checksum md5(file) y 16 antes el tag GCM
        # Basta con quitar los 32 bytes finales y descifrar en modo GCM sin verificar.
        encrypted = encrypted[:-32] if len(encrypted) > 32 else encrypted
        aes = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
    else:  # crypt14
        if is_root:
            raise ValueError("Se ha proporcionado una clave raíz crypt15 para un backup crypt14")
        aes = AES.new(raw_key, AES.MODE_GCM, nonce=iv)

    plain = _maybe_decompress(aes.decrypt(encrypted))
    with open(output, "wb") as fh:
        fh.write(plain)
    return True


def decrypt_path(path, key_source, out_dir):
    """Descifra todos los .crypt12/14/15 de un directorio."""
    os.makedirs(out_dir, exist_ok=True)
    _, _, files = next(os.walk(path))
    done = 0
    for f in files:
        ext = os.path.splitext(f)[1].lower()
        if ext in (".crypt12", ".crypt14", ".crypt15"):
            out = os.path.join(out_dir, os.path.splitext(f)[0])
            try:
                decrypt(os.path.join(path, f), key_source, out)
                print("[-] {} -> {}".format(f, out))
                done += 1
            except Exception as e:
                print("[e] {}: {}".format(f, e))
    print("[i] {} bases descifradas".format(done))



# ===========================================================================
#  Cifrado crypt15
# ===========================================================================
def _write_varint(value):
    out = bytearray()
    while True:
        b = value & 0x7F
        value >>= 7
        if value:
            out.append(b | 0x80)
        else:
            out.append(b)
            return bytes(out)


def build_crypt15_header(iv, app_version="2.24.0.0", jid_suffix="00"):
    """Cabecera protobuf crypt15 mínima válida (mensaje BackupPrefix)."""
    c15 = b"\x0a" + _write_varint(len(iv)) + iv            # C15_IV.IV = campo 1
    av, js = app_version.encode(), jid_suffix.encode()
    info = (b"\x0a" + _write_varint(len(av)) + av +        # app_version = 1
            b"\x1a" + _write_varint(len(js)) + js)         # jidSuffix   = 3
    prefix = (b"\x08\x01" +                               # key_type = 1 (E2E)
              b"\x1a" + _write_varint(len(c15)) + c15 +    # c15_iv   = 3
              b"\x22" + _write_varint(len(info)) + info)   # info     = 4
    return bytes([len(prefix)]) + prefix


def encrypt(db_file, key_source, output, iv=None):
    """Cifra una base de datos en formato crypt15.

    El archivo resultante es un backup sintético: verifica y documenta su
    procedencia si lo incorporas a una actuación.
    """
    raw_key, is_root = load_key(key_source)
    aes_key = derive_key(raw_key) if is_root else raw_key
    iv = iv or os.urandom(16)
    with open(db_file, "rb") as fh:
        compressed = zlib.compress(fh.read())
    cipher = AES.new(aes_key, AES.MODE_GCM, nonce=iv)
    ciphertext, tag = cipher.encrypt_and_digest(compressed)
    header = build_crypt15_header(iv)
    body = ciphertext + tag
    with open(output, "wb") as fh:
        fh.write(header + body + md5(header + body).digest())
    return output



# ===========================================================================
#  Linea de ordenes
# ===========================================================================
def main():
    parser = argparse.ArgumentParser(
        description="Choose a file or path to decrypt or encrypt",
        epilog="""Ejemplos:
  Descifrar un archivo (crypt12/14/15, se autodetecta el formato):
    python3 whacipher.py -f msgstore.db.crypt15 -d key -o msgstore.db
  Descifrar con la clave raiz en hexadecimal (crypt15):
    python3 whacipher.py -f msgstore.db.crypt15 -d <64_hex> -o msgstore.db
  Descifrar todo un directorio:
    python3 whacipher.py -p ./backups -d key -o ./salida
  Cifrar en crypt15:
    python3 whacipher.py -f msgstore.db -e key -o msgstore.db.crypt15""",
        formatter_class=argparse.RawDescriptionHelpFormatter)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("-f", "--file", help="Database file to encrypt or decrypt", nargs='?')
    mode.add_argument("-p", "--path", help="Database path to decrypt", nargs='?')
    parser.add_argument("-d", "--decrypt",
                        help="Whatsapp Key path or 64 hex chars (Decrypt database)")
    parser.add_argument("-e", "--encrypt",
                        help="Whatsapp Key path or 64 hex chars (Encrypt database)")
    parser.add_argument("-o", "--output", help="Database output file or path")

    if len(sys.argv) == 1:
        banner(); help(); parser.print_help(); sys.exit(0)

    args = parser.parse_args()
    banner()

    if not args.output:
        sys.exit("[e] Indica la salida con -o")
    try:
        if args.path:
            if not args.decrypt:
                sys.exit("[e] Con -p solo se puede descifrar: anade -d CLAVE")
            decrypt_path(args.path, args.decrypt, args.output)
        elif args.file:
            if args.decrypt:
                decrypt(args.file, args.decrypt, args.output)
                print("[-] {} descifrado -> {}".format(args.file, args.output))
            elif args.encrypt:
                encrypt(args.file, args.encrypt, args.output)
                print("[-] {} cifrado -> {}".format(args.file, args.output))
                print("[i] El resultado es un backup generado por whapa; "
                      "documenta su procedencia si lo aportas a un procedimiento.")
            else:
                sys.exit("[e] Indica -d para descifrar o -e para cifrar")
        else:
            sys.exit("[e] Indica un archivo con -f o un directorio con -p")
    except Exception as e:
        sys.exit("[e] {}".format(e))


if __name__ == "__main__":
    main()

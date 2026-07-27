#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
whareader.py — Lectura de bases de datos de WhatsApp (Android e iOS)

COMETIDO DE ESTE ARCHIVO
    Abrir un volcado ya descifrado y traducirlo a un modelo común, para que el
    resto del proyecto no tenga que saber de qué plataforma procede:

        Android actual  : msgstore.db        -> tabla `message`
        Android antiguo : msgstore.db        -> tabla `messages`
        iOS             : ChatStorage.sqlite -> tabla `ZWAMESSAGE`

    Detecta el esquema por sí solo, tolera que falten tablas o columnas (varían
    con cada versión de WhatsApp) y abre siempre en modo solo lectura, de modo
    que el original nunca se modifica. Calcula el SHA-256 de cada origen para la
    cadena de custodia.

    NO descifra (de eso se encarga whacipher.py) ni genera informes (whareport.py).
    No tiene línea de órdenes: es una biblioteca que usan whapa.py y whapa-gui.py.

** Author: Ivan Moreno a.k.a B16f00t
** Github: https://github.com/B16f00t
"""

import os
import sqlite3
import hashlib
import datetime
from dataclasses import dataclass, field
from typing import Optional, List, Dict

import whacodes as codes

UTC = datetime.timezone.utc
COREDATA_EPOCH_OFFSET = 978307200   # Core Data (1/1/2001) -> Unix (1/1/1970)


# ===========================================================================
#  MODELO DE DATOS  (común a Android e iOS)
# ===========================================================================
def texto_seguro(valor):
    """Convierte a texto lo que venga de la base sin romperse.

    SQLite tiene tipado dinamico: en una columna declarada TEXT puede haber un
    BLOB, y entonces llega como bytes aunque el resto de la tabla sea texto.
    Sin esto, un solo valor asi aborta el analisis mucho despues, al formatear.
    """
    if isinstance(valor, (bytes, bytearray)):
        return valor.decode("utf-8", "replace")
    return valor


@dataclass
class Reaction:
    emoji: str
    sender: Optional[str] = None
    from_me: bool = False
    timestamp: Optional[int] = None


@dataclass
class Quote:
    text: Optional[str] = None
    sender: Optional[str] = None
    from_me: bool = False
    type_desc: Optional[str] = None


@dataclass
class Message:
    row_id: int
    chat_id: str
    from_me: bool
    sender: Optional[str]               # numero o LID, tal cual esta en la base
    timestamp: Optional[int]            # Unix epoch en segundos (UTC)
    kind: "codes.Kind"
    type_desc: str
    raw_type: Optional[int]
    text: Optional[str] = None
    key_id: Optional[str] = None
    media_path: Optional[str] = None
    media_mime: Optional[str] = None
    media_size: Optional[int] = None
    media_caption: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    starred: bool = False
    is_deleted: bool = False
    is_forwarded: bool = False
    edited: bool = False
    system_action: Optional[str] = None
    quote: Optional[Quote] = None
    reactions: List[Reaction] = field(default_factory=list)
    call_duration: Optional[int] = None
    call_video: bool = False
    call_result: Optional[str] = None
    sender_name: Optional[str] = None   # nombre del remitente, si esta en la agenda
    status: Optional[int] = None        # codigo de entrega/lectura
    status_desc: Optional[str] = None   # su descripcion legible
    delivered_ts: Optional[int] = None  # salida/recepcion en el dispositivo
    server_ts: Optional[int] = None     # llegada al servidor
    read_by: int = 0                    # en grupos: cuantos lo han leido
    delivered_to: int = 0               # en grupos: a cuantos ha llegado
    platform: str = ""

    @property
    def sender_label(self) -> str:
        """Como mostrar el remitente: nombre si lo hay, si no el identificador."""
        return self.sender_name or self.sender or ""

    # Campos que pueden llegar como bytes si la base los guardo como BLOB
    _CAMPOS_TEXTO = ("chat_id", "sender", "text", "type_desc", "key_id",
                     "media_path", "media_mime", "media_caption",
                     "system_action", "sender_name")

    def __post_init__(self):
        for campo in self._CAMPOS_TEXTO:
            valor = getattr(self, campo, None)
            if isinstance(valor, (bytes, bytearray)):
                setattr(self, campo, texto_seguro(valor))

    @property
    def display_text(self) -> str:
        return (self.text or self.media_caption or self.system_action
                or "[{}]".format(self.type_desc))

    @property
    def leido(self) -> bool:
        """Consta que el destinatario lo abrio.

        Que sea False no prueba que no se leyera: si el contacto tiene
        desactivada la confirmacion de lectura, el estado nunca pasa de
        "entregado".
        """
        return codes.status_leido(self.status, self.from_me) or self.read_by > 0


@dataclass
class Chat:
    chat_id: str
    name: Optional[str] = None
    is_group: bool = False
    messages: List[Message] = field(default_factory=list)

    @property
    def label(self) -> str:
        return self.name or (self.chat_id or "?").split("@")[0]

    @property
    def is_broadcast(self) -> bool:
        return "broadcast" in (self.chat_id or "")

    @property
    def first_ts(self):
        ts = [m.timestamp for m in self.messages if m.timestamp]
        return min(ts) if ts else None

    @property
    def last_ts(self):
        ts = [m.timestamp for m in self.messages if m.timestamp]
        return max(ts) if ts else None


@dataclass
class Contact:
    jid: str
    display_name: Optional[str] = None
    phone: Optional[str] = None
    status: Optional[str] = None

    def __post_init__(self):
        self.jid = texto_seguro(self.jid)
        self.display_name = texto_seguro(self.display_name)
        self.phone = texto_seguro(self.phone)
        self.status = texto_seguro(self.status)


@dataclass
class Call:
    jid: str
    timestamp: Optional[int]
    from_me: bool
    video: bool
    duration: Optional[int]
    result: Optional[str]


@dataclass
class Extraction:
    """Resultado completo de leer un volcado."""
    platform: str
    messages: List[Message] = field(default_factory=list)
    contacts: Dict[str, Contact] = field(default_factory=dict)
    calls: List[Call] = field(default_factory=list)
    chat_names: Dict[str, str] = field(default_factory=dict)
    lid_map: Dict[str, str] = field(default_factory=dict)
    damaged_text: int = 0        # textos con bytes no validos en el origen
    source_files: List[dict] = field(default_factory=list)

    def buscar_contacto(self, jid):
        """Contacto de un jid, resolviendo LID y comparando por numero.

        Un chat puede venir identificado por LID (`...@lid`), mientras que la
        agenda esta indexada por telefono. Sin cruzar ambos, la conversacion se
        queda sin nombre aunque el contacto este guardado.
        """
        if not jid:
            return None
        ct = self.contacts.get(jid)
        if ct:
            return ct
        equivalente = self.lid_map.get(jid)
        if equivalente:
            ct = self.contacts.get(equivalente)
            if ct:
                return ct
            jid = equivalente
        digitos = solo_digitos(jid.split("@")[0])
        if len(digitos) >= 6:
            if not hasattr(self, "_indice_num"):
                self._indice_num = {}
                for c in self.contacts.values():
                    for clave in (solo_digitos(c.phone),
                                  solo_digitos(c.jid.split("@")[0])):
                        if len(clave) >= 6:
                            self._indice_num.setdefault(clave, c)
            return self._indice_num.get(digitos)
        return None

    def chats(self) -> List[Chat]:
        buckets = {}
        for m in self.messages:
            c = buckets.get(m.chat_id)
            if c is None:
                # Prioridad: asunto del grupo guardado en la base > agenda > jid
                nombre = self.chat_names.get(m.chat_id)
                if not nombre:
                    ct = self.buscar_contacto(m.chat_id)
                    nombre = ct.display_name if ct else None
                if not nombre and str(m.chat_id).endswith("@lid"):
                    # Sin nombre y sin equivalencia: se marca para que no se
                    # confunda ese numero largo con un telefono
                    nombre = "LID:" + short_jid(m.chat_id)
                c = Chat(chat_id=m.chat_id, name=nombre,
                         is_group="g.us" in (m.chat_id or ""))
                buckets[m.chat_id] = c
            c.messages.append(m)
        out = list(buckets.values())
        out.sort(key=lambda c: (c.last_ts or 0), reverse=True)
        return out

    def summary(self) -> dict:
        by_kind, by_year = {}, {}
        for m in self.messages:
            by_kind[m.kind.value] = by_kind.get(m.kind.value, 0) + 1
            if m.timestamp:
                y = datetime.datetime.fromtimestamp(m.timestamp, UTC).year
                by_year[y] = by_year.get(y, 0) + 1
        ts = [m.timestamp for m in self.messages if m.timestamp]
        return {"total": len(self.messages),
                "chats": len({m.chat_id for m in self.messages}),
                "deleted": sum(1 for m in self.messages if m.is_deleted),
                "starred": sum(1 for m in self.messages if m.starred),
                "with_media": sum(1 for m in self.messages if m.media_path),
                "contacts": len(self.contacts), "calls": len(self.calls),
                "first_ts": min(ts) if ts else None,
                "last_ts": max(ts) if ts else None,
                "by_kind": dict(sorted(by_kind.items(), key=lambda x: -x[1])),
                "by_year": dict(sorted(by_year.items()))}


# ===========================================================================
#  UTILIDADES
# ===========================================================================
def ios_date_to_unix(zdate):
    if zdate is None:
        return None
    try:
        return int(float(zdate) + COREDATA_EPOCH_OFFSET)
    except (TypeError, ValueError):
        return None


def android_ts_to_unix(ts):
    if not ts:
        return None
    try:
        return int(int(ts) / 1000)
    except (TypeError, ValueError):
        return None


def fmt_ts(ts):
    if not ts:
        return ""
    try:
        return datetime.datetime.fromtimestamp(ts, UTC).strftime("%Y-%m-%d %H:%M:%S")
    except (OSError, ValueError, OverflowError):
        return str(ts)


def short_jid(jid):
    return "" if not jid else str(jid).split("@")[0]


def _resolve_sender(jid, lidmap=None):
    """Nombre a mostrar del remitente, traduciendo el LID si se puede."""
    if not jid:
        return None
    if lidmap and jid in lidmap:
        return short_jid(lidmap[jid])
    if str(jid).endswith("@lid"):
        # No hay correspondencia: se marca para no confundirlo con un telefono
        return "LID:" + short_jid(jid)
    return short_jid(jid)


def infer_device(key_id):
    """Dispositivo emisor inferido del key_id / ZSTANZAID."""
    if not key_id:
        return ""
    k = str(key_id).strip().upper()
    n = len(k)
    if 9 <= n <= 10 and k.isdigit():
        return "Sistema (grupo/comunidad)"
    if n == 18:
        return "Windows / Wear OS"
    if n == 20:
        if k.startswith("3EB0"):
            return "WhatsApp Web"
        if k.startswith("5E"):
            return "iOS"
        if k.startswith("3A"):
            return "iOS / iPadOS / macOS"
    if n in (30, 32):
        return "Android"
    return ""


def sha256_file(path, chunk=1 << 20):
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        while True:
            b = fh.read(chunk)
            if not b:
                break
            h.update(b)
    return h.hexdigest()


class _TextoTolerante:
    """Decodifica el texto de SQLite sin abortar cuando hay bytes invalidos.

    Las bases reales traen texto mal formado: emojis cortados por una borrado
    parcial, filas recuperadas a medias, mezclas de codificacion. Python aborta
    la consulta entera con `Could not decode to UTF-8` y se pierde el analisis
    completo por una sola fila.

    Aqui se sustituye lo que no se puede decodificar por el caracter de
    reemplazo (U+FFFD) y se lleva la cuenta, de modo que el analisis continua y
    ademas queda constancia de cuanto texto venia danado en el origen.
    """

    def __init__(self):
        self.danados = 0

    def __call__(self, crudo):
        try:
            return crudo.decode("utf-8")
        except UnicodeDecodeError:
            self.danados += 1
            return crudo.decode("utf-8", "replace")


def _open_ro(path):
    """Abre siempre en solo lectura: el original nunca se toca."""
    con = sqlite3.connect("file:{}?mode=ro".format(path), uri=True)
    con.text_factory = _TextoTolerante()
    return con


def _tables(con):
    cur = con.cursor()
    cur.execute("SELECT name FROM sqlite_master WHERE type IN ('table','view')")
    return {r[0] for r in cur.fetchall()}


def _cols(con, table):
    try:
        return {r[1] for r in con.execute("PRAGMA table_info({})".format(table))}
    except sqlite3.Error:
        return set()


def _pick(available, *candidates):
    """Primer nombre de columna que exista, o None. Absorbe los cambios de
    esquema entre versiones de WhatsApp sin romper la consulta."""
    for c in candidates:
        if c in available:
            return c
    return None


# ===========================================================================
#  LECTOR ANDROID
# ===========================================================================
def _android_subjects(con, tbls, jids):
    """jid del chat -> nombre del grupo.

    El nombre de un grupo no es su identificador: vive en la columna `subject`
    de la tabla `chat` (esquema actual) o de `chat_list` (esquema antiguo). Sin
    leerla, los grupos aparecen como `120363...`, que no le dice nada a nadie.
    Los chats individuales no tienen asunto: ahi el nombre sale de la agenda.
    """
    out = {}
    if "chat" in tbls and "subject" in _cols(con, "chat"):
        try:
            for jid_row, subject in con.execute(
                    "SELECT jid_row_id, subject FROM chat WHERE subject IS NOT NULL"):
                jid = jids.get(jid_row)
                if jid and subject:
                    out[texto_seguro(jid)] = texto_seguro(subject)
        except sqlite3.Error:
            pass
    if "chat_list" in tbls and "subject" in _cols(con, "chat_list"):
        c = _cols(con, "chat_list")
        col = _pick(c, "key_remote_jid", "raw_string_jid")
        if col:
            try:
                for jid, subject in con.execute(
                        "SELECT {}, subject FROM chat_list "
                        "WHERE subject IS NOT NULL".format(col)):
                    if jid and subject:
                        out.setdefault(jid, subject)
            except sqlite3.Error:
                pass
    return out


def _android_receipts(con, tbls):
    """message_row_id -> (entregado_a, leido_por)   (informe 4.6.55)

    En un chat de grupo se guarda una fila por participante, con la fecha en
    que cada uno recibio, leyo y reprodujo el mensaje. Permite decir a cuantos
    llego y cuantos lo abrieron, no solo si se entrego.
    """
    if "receipt_user" not in tbls:
        return {}
    c = _cols(con, "receipt_user")
    recibido = _pick(c, "receipt_timestamp", "received_timestamp")
    leido = _pick(c, "read_timestamp")
    reproducido = _pick(c, "played_timestamp")
    if not (recibido or leido):
        return {}
    sel = ", ".join(x or "NULL" for x in (recibido, leido, reproducido))
    out = {}
    try:
        for rid, rec, lee, rep in con.execute(
                "SELECT message_row_id, {} FROM receipt_user".format(sel)):
            entregados, leidos = out.get(rid, (0, 0))
            if rec and int(rec) > 0:
                entregados += 1
            if (lee and int(lee) > 0) or (rep and int(rep) > 0):
                leidos += 1
            out[rid] = (entregados, leidos)
    except sqlite3.Error:
        return {}
    return out


def _android_lid_map(con, tbls, jids):
    """LID -> numero de telefono, si la base trae la tabla de correspondencia.

    Desde 2024 WhatsApp identifica a los participantes de grupo con un LID
    (`...@lid`) en lugar del numero. Es un identificador opaco: en el informe se
    veria un numero larguisimo que no es un telefono. Si existe la tabla que
    relaciona ambos, se traduce; si no, se deja el LID tal cual y se marca como
    tal, que es preferible a hacerlo pasar por un numero.
    """
    for tabla, col_lid, col_jid in (("lid_jid_map", "lid_row_id", "jid_row_id"),
                                    ("jid_map", "lid_row_id", "jid_row_id")):
        if tabla not in tbls:
            continue
        c = _cols(con, tabla)
        if not {col_lid, col_jid} <= c:
            continue
        try:
            return {jids.get(l): jids.get(j)
                    for l, j in con.execute(
                        "SELECT {}, {} FROM {}".format(col_lid, col_jid, tabla))
                    if jids.get(l) and jids.get(j)}
        except sqlite3.Error:
            return {}
    return {}


def _android_media(con, tbls):
    if "message_media" not in tbls:
        return {}
    c = _cols(con, "message_media")
    sel = ", ".join(x or "NULL" for x in (
        _pick(c, "file_path"), _pick(c, "mime_type"),
        _pick(c, "file_size", "media_size"), _pick(c, "media_caption")))
    return {r[0]: r[1:] for r in con.execute(
        "SELECT message_row_id, {} FROM message_media".format(sel))}


def _android_system(con, tbls):
    if "message_system" not in tbls:
        return {}
    return {rid: codes.system_action_description(at) for rid, at in con.execute(
        "SELECT message_row_id, action_type FROM message_system")}


def _android_forwarded(con, tbls):
    if "message_forwarded" not in tbls:
        return set()
    return {r[0] for r in con.execute("SELECT message_row_id FROM message_forwarded")}


def _android_location(con, tbls):
    if "message_location" not in tbls:
        return {}
    if not {"latitude", "longitude"} <= _cols(con, "message_location"):
        return {}
    return {r[0]: (r[1], r[2]) for r in con.execute(
        "SELECT message_row_id, latitude, longitude FROM message_location")}


def _android_quotes(con, tbls, jids):
    if "message_quoted" not in tbls:
        return {}
    c = _cols(con, "message_quoted")
    sel = ", ".join(x or "NULL" for x in (
        _pick(c, "text_data"), _pick(c, "message_type"), _pick(c, "sender_jid_row_id")))
    out = {}
    for rid, t, mt, sj in con.execute(
            "SELECT message_row_id, {} FROM message_quoted".format(sel)):
        out[rid] = Quote(text=t, sender=short_jid(jids.get(sj)),
                         type_desc=codes.describe(codes.ANDROID, mt) if mt is not None else None)
    return out


def _android_addons(con, tbls, jids):
    """Reacciones (tipo 56) y ediciones (tipo 74)."""
    reacts, edited = {}, set()
    if "message_add_on" not in tbls:
        return reacts, edited
    c = _cols(con, "message_add_on")
    if "parent_message_row_id" not in c:
        return reacts, edited
    emojis = {}
    if "message_add_on_reaction" in tbls:
        col = _pick(_cols(con, "message_add_on_reaction"), "reaction")
        if col:
            emojis = {r[0]: r[1] for r in con.execute(
                "SELECT message_add_on_row_id, {} FROM message_add_on_reaction".format(col))}
    sender = _pick(c, "sender_jid_row_id") or "NULL"
    for aid, parent, fme, ts, atype, sj in con.execute(
            "SELECT _id, parent_message_row_id, from_me, timestamp, "
            "message_add_on_type, {} FROM message_add_on".format(sender)):
        t = int(atype or 0)
        if t == 56:
            reacts.setdefault(parent, []).append(Reaction(
                emoji=emojis.get(aid) or "\u00b7",
                sender=short_jid(jids.get(sj)) if sj else None,
                from_me=bool(fme), timestamp=android_ts_to_unix(ts)))
        elif t == 74:
            edited.add(parent)
    return reacts, edited


def _android_calls(con, tbls, jids):
    """Devuelve (mapa por message_row_id, lista de Call para el registro)."""
    if "call_log" not in tbls:
        return {}, []
    c = _cols(con, "call_log")
    cid = _pick(c, "call_id")
    sel = ", ".join(x or "NULL" for x in (
        _pick(c, "duration"), _pick(c, "video_call"), _pick(c, "call_result"),
        _pick(c, "timestamp"), _pick(c, "from_me"), _pick(c, "jid_row_id")))
    por_msg, registro = {}, []
    q = "SELECT {}, {} FROM call_log".format(cid or "NULL", sel)
    for call_id, dur, vid, res, ts, fme, jrow in con.execute(q):
        desc = codes.call_result_description(res) if res is not None else None
        if call_id:
            por_msg[call_id] = (dur, bool(vid), desc)
        registro.append(Call(jid=jids.get(jrow, "") or "", timestamp=android_ts_to_unix(ts),
                             from_me=bool(fme), video=bool(vid), duration=dur, result=desc))
    registro.sort(key=lambda x: x.timestamp or 0)
    return por_msg, registro


def _read_android_modern(con):
    tbls = _tables(con)
    jids = {r[0]: r[1] for r in con.execute("SELECT _id, raw_string FROM jid")}
    lidmap = _android_lid_map(con, tbls, jids)
    subjects = _android_subjects(con, tbls, jids)
    recibos = _android_receipts(con, tbls)
    media = _android_media(con, tbls)
    system = _android_system(con, tbls)
    fwd = _android_forwarded(con, tbls)
    loc = _android_location(con, tbls)
    quotes = _android_quotes(con, tbls, jids)
    reacts, edited = _android_addons(con, tbls, jids)
    calls_map, calls = _android_calls(con, tbls, jids)

    mc = _cols(con, "message")
    sql = """SELECT m._id, cj.raw_string, m.from_me, {sender}, m.timestamp,
                    m.message_type, m.text_data, m.key_id, {star},
                    {status}, {recv}, {srv}
             FROM message m
             LEFT JOIN chat c  ON c._id = m.chat_row_id
             LEFT JOIN jid  cj ON cj._id = c.jid_row_id
             ORDER BY m.timestamp""".format(
        sender=_pick(mc, "sender_jid_row_id") or "NULL",
        star=_pick(mc, "starred") or "0",
        status=_pick(mc, "status") or "NULL",
        recv=_pick(mc, "received_timestamp") or "NULL",
        srv=_pick(mc, "receipt_server_timestamp") or "NULL")

    out = []
    for (rid, chat_jid, fme, sj, ts, mtype, text, key_id, star,
         status, recv_ts, srv_ts) in con.execute(sql):
        kind, desc = codes.normalize(codes.ANDROID, mtype)
        p, mm, sz, cp = media.get(rid, (None, None, None, None))
        la, lo = loc.get(rid, (None, None))
        dur, vid, res = calls_map.get(rid, (None, False, None))
        entregados, leidos = recibos.get(rid, (0, 0))
        out.append(Message(
            row_id=rid, chat_id=chat_jid or "", from_me=bool(fme),
            sender=_resolve_sender(jids.get(sj), lidmap) if sj else None,
            timestamp=android_ts_to_unix(ts), kind=kind, type_desc=desc,
            raw_type=mtype, text=text, key_id=key_id, media_path=p,
            media_mime=mm, media_size=sz, media_caption=cp, latitude=la,
            longitude=lo, starred=bool(star),
            is_deleted=codes.is_deleted(codes.ANDROID, mtype),
            is_forwarded=rid in fwd, edited=rid in edited,
            system_action=system.get(rid), quote=quotes.get(rid),
            reactions=reacts.get(rid, []), call_duration=dur, call_video=vid,
            call_result=res,
            status=status,
            status_desc=codes.status_description(status, bool(fme)),
            delivered_ts=android_ts_to_unix(recv_ts),
            server_ts=android_ts_to_unix(srv_ts),
            delivered_to=entregados, read_by=leidos,
            platform=codes.ANDROID))
    return out, calls, subjects, lidmap


def _read_android_legacy(con):
    c = _cols(con, "messages")
    sql = """SELECT _id, key_remote_jid, key_from_me, remote_resource, timestamp,
                    media_wa_type, data, key_id, {star}, media_mime_type, {cap},
                    latitude, longitude, media_size
             FROM messages ORDER BY timestamp""".format(
        star=_pick(c, "starred") or "0", cap=_pick(c, "media_caption") or "NULL")
    out = []
    for (rid, chat_jid, fme, sender, ts, mtype, text, key_id, st,
         mime, caption, la, lo, size) in con.execute(sql):
        kind, desc = codes.normalize(codes.ANDROID_LEGACY, mtype)
        out.append(Message(
            row_id=rid, chat_id=chat_jid or "", from_me=bool(fme),
            sender=short_jid(sender), timestamp=android_ts_to_unix(ts), kind=kind,
            type_desc=desc, raw_type=mtype, text=text, key_id=key_id,
            media_mime=mime, media_caption=caption, media_size=size, latitude=la,
            longitude=lo, starred=bool(st),
            is_deleted=codes.is_deleted(codes.ANDROID_LEGACY, mtype),
            platform=codes.ANDROID_LEGACY))
    return out, [], {}, {}


def solo_digitos(valor):
    """Deja solo los digitos de un numero, para poder comparar formatos."""
    return "".join(ch for ch in str(valor or "") if ch.isdigit())


def _read_wa_contacts(path):
    """Contactos desde wa.db.

    El nombre de un contacto puede estar en varias columnas y no siempre en la
    primera: `display_name` solo se rellena si esta en la agenda del telefono.
    Si no lo esta, el nombre visible es el que esa persona se ha puesto en
    WhatsApp, que vive en `wa_name`. Se prueban por orden de fiabilidad.
    """
    if not path or not os.path.exists(path):
        return {}
    con = _open_ro(path)
    try:
        c = _cols(con, "wa_contacts")
        jid = _pick(c, "jid", "raw_string")
        if not jid:
            return {}
        # orden: agenda del telefono -> nombre puesto en WhatsApp -> otros
        cols_nombre = [x for x in (_pick(c, "display_name"), _pick(c, "wa_name"),
                                   _pick(c, "nickname"), _pick(c, "given_name"),
                                   _pick(c, "sort_name")) if x]
        num = _pick(c, "number")
        est = _pick(c, "status")
        sel = ", ".join(cols_nombre + [num or "NULL", est or "NULL"])
        out = {}
        for fila in con.execute("SELECT {}, {} FROM wa_contacts".format(jid, sel)):
            j = fila[0]
            if not j:
                continue
            nombres = fila[1:1 + len(cols_nombre)]
            telefono = fila[1 + len(cols_nombre)] if num else None
            estado = fila[-1] if est else None
            nombre = next((n for n in nombres if n and str(n).strip()), None)
            out[j] = Contact(jid=j, display_name=nombre, phone=telefono,
                             status=estado)
        return out
    finally:
        con.close()


# ===========================================================================
#  LECTOR iOS
# ===========================================================================
def _ios_media(con, tbls):
    if "ZWAMEDIAITEM" not in tbls:
        return {}
    c = _cols(con, "ZWAMEDIAITEM")
    sel = ", ".join(x or "NULL" for x in (
        _pick(c, "ZMEDIALOCALPATH"), _pick(c, "ZVCARDNAME", "ZVCARDSTRING"),
        _pick(c, "ZTITLE"), _pick(c, "ZLATITUDE"), _pick(c, "ZLONGITUDE"),
        _pick(c, "ZFILESIZE")))
    return {r[0]: r[1:] for r in con.execute(
        "SELECT Z_PK, {} FROM ZWAMEDIAITEM".format(sel))}


def _ios_members(con, tbls):
    if "ZWAGROUPMEMBER" not in tbls:
        return {}
    col = _pick(_cols(con, "ZWAGROUPMEMBER"), "ZMEMBERJID")
    if not col:
        return {}
    return {r[0]: r[1] for r in con.execute(
        "SELECT Z_PK, {} FROM ZWAGROUPMEMBER".format(col))}


def _ios_sessions(con, tbls):
    if "ZWACHATSESSION" not in tbls:
        return {}
    c = _cols(con, "ZWACHATSESSION")
    sel = ", ".join(x or "NULL" for x in (
        _pick(c, "ZCONTACTJID"), _pick(c, "ZPARTNERNAME")))
    return {r[0]: (r[1], r[2]) for r in con.execute(
        "SELECT Z_PK, {} FROM ZWACHATSESSION".format(sel))}


def _read_ios(con):
    tbls = _tables(con)
    media = _ios_media(con, tbls)
    members = _ios_members(con, tbls)
    sessions = _ios_sessions(con, tbls)
    mc = _cols(con, "ZWAMESSAGE")

    sql = """SELECT Z_PK, ZCHATSESSION, ZISFROMME, {gm}, ZMESSAGEDATE,
                    ZMESSAGETYPE, ZTEXT, {sz}, {st}, {fj}, {mi}
             FROM ZWAMESSAGE ORDER BY ZMESSAGEDATE""".format(
        gm=_pick(mc, "ZGROUPMEMBER") or "NULL", sz=_pick(mc, "ZSTANZAID") or "NULL",
        st=_pick(mc, "ZSTARRED") or "0", fj=_pick(mc, "ZFROMJID") or "NULL",
        mi=_pick(mc, "ZMEDIAITEM") or "NULL")

    out = []
    for pk, sess, fme, gm, zdate, mtype, text, sid, st, fj, mi in con.execute(sql):
        kind, desc = codes.normalize(codes.IOS, mtype)
        chat_jid, _ = sessions.get(sess, (None, None))
        mp = mv = mt = mla = mlo = msz = None
        if mi and mi in media:
            mp, mv, mt, mla, mlo, msz = media[mi]
        out.append(Message(
            row_id=pk, chat_id=chat_jid or "", from_me=bool(fme),
            sender=short_jid(members.get(gm) if gm else fj),
            timestamp=ios_date_to_unix(zdate), kind=kind, type_desc=desc,
            raw_type=mtype, text=text, key_id=sid, media_path=mp,
            media_caption=mt, media_size=msz, latitude=mla, longitude=mlo,
            starred=bool(st), is_deleted=codes.is_deleted(codes.IOS, mtype),
            platform=codes.IOS))
    # en iOS el nombre del chat (grupo incluido) esta en ZWACHATSESSION
    nombres = {j: n for j, n in sessions.values() if j and n}
    return out, [], nombres, {}


def _ios_chat_names(con):
    out = {}
    for _pk, (jid, name) in _ios_sessions(con, _tables(con)).items():
        if jid:
            out[jid] = Contact(jid=jid, display_name=name)
    return out


def _read_ios_contacts(path):
    """Contactos desde ContactsV2.sqlite."""
    if not path or not os.path.exists(path):
        return {}
    con = _open_ro(path)
    try:
        if "ZWAADDRESSBOOKCONTACT" not in _tables(con):
            return {}
        c = _cols(con, "ZWAADDRESSBOOKCONTACT")
        jid = _pick(c, "ZWHATSAPPID")
        if not jid:
            return {}
        sel = ", ".join(x or "NULL" for x in (
            _pick(c, "ZFULLNAME"), _pick(c, "ZPHONENUMBER")))
        out = {}
        for j, f, p in con.execute(
                "SELECT {}, {} FROM ZWAADDRESSBOOKCONTACT".format(jid, sel)):
            if j:
                key = j if "@" in str(j) else "{}@s.whatsapp.net".format(j)
                out[key] = Contact(jid=key, display_name=f, phone=p)
        return out
    finally:
        con.close()


# ===========================================================================
#  DETECCIÓN DE PLATAFORMA Y ENTRADA PRINCIPAL
# ===========================================================================
def detect_platform(db_path):
    """Autodetecta el esquema del volcado."""
    con = _open_ro(db_path)
    try:
        t = _tables(con)
    finally:
        con.close()
    if "ZWAMESSAGE" in t:
        return codes.IOS
    if "message" in t and "chat" in t:
        return codes.ANDROID
    if "messages" in t:
        return codes.ANDROID_LEGACY
    raise ValueError("Esquema de WhatsApp no reconocido. Tablas: {}".format(
        ", ".join(sorted(t)[:12]) or "ninguna"))


def _custody(path):
    return {"name": os.path.basename(path), "size": os.path.getsize(path),
            "sha256": sha256_file(path)}


def read(db_path, platform=None, wa_db=None, hash_sources=True):
    """Lee un volcado y devuelve una Extraction normalizada.

    db_path  : msgstore.db | ChatStorage.sqlite
    platform : fuerza la plataforma (por defecto, autodetección)
    wa_db    : wa.db (Android) o ContactsV2.sqlite (iOS), opcional
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError("No existe la base de datos: {}".format(db_path))
    platform = platform or detect_platform(db_path)
    con = _open_ro(db_path)
    danados = 0
    try:
        if platform == codes.ANDROID:
            messages, calls, chat_names, lidmap = _read_android_modern(con)
            contacts = _read_wa_contacts(wa_db)
        elif platform == codes.ANDROID_LEGACY:
            messages, calls, chat_names, lidmap = _read_android_legacy(con)
            contacts = _read_wa_contacts(wa_db)
        elif platform == codes.IOS:
            messages, calls, chat_names, lidmap = _read_ios(con)
            contacts = _ios_chat_names(con)
            contacts.update(_read_ios_contacts(wa_db))
        else:
            raise ValueError("Plataforma no soportada: {}".format(platform))
        danados = getattr(con.text_factory, "danados", 0)
    finally:
        con.close()

    sources = []
    if hash_sources:
        sources.append(_custody(db_path))
        if wa_db and os.path.exists(wa_db):
            sources.append(_custody(wa_db))

    ext = Extraction(platform=platform, messages=messages, contacts=contacts,
                     calls=calls, chat_names=chat_names, lid_map=lidmap,
                     damaged_text=danados, source_files=sources)
    _resolver_remitentes(ext)
    return ext


def _resolver_remitentes(ext):
    """Pone nombre a los remitentes de los grupos.

    En un grupo, cada mensaje trae el numero (o el LID) de quien lo envio. Sin
    cruzarlo con la agenda, el informe muestra una lista de numeros y hay que ir
    identificandolos a mano. Se resuelve una sola vez por remitente distinto,
    que en un grupo grande son muchos menos que mensajes.
    """
    cache = {}
    for m in ext.messages:
        if not m.sender or m.sender_name:
            continue
        clave = m.sender[4:] if m.sender.startswith("LID:") else m.sender
        if clave not in cache:
            ct = ext.buscar_contacto(clave)
            cache[clave] = ct.display_name if (ct and ct.display_name) else None
        m.sender_name = cache[clave]

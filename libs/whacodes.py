#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
whacodes.py — Catálogo de códigos de WhatsApp (Android + iOS)

Fuente: «Análisis forense de la aplicación WhatsApp en sistemas Android e iOS»
        Francisco Arenaz Benito, Ediciones Universidad de Salamanca (2026).

COMETIDO DE ESTE ARCHIVO
    Todo código numérico que aparezca en las bases de datos de WhatsApp vive
    aquí y solo aquí: tipos de mensaje de Android (moderno y antiguo), tipos de
    iOS, acciones de sistema, complementos (reacciones, ediciones) y llamadas.

    Ningún otro archivo del proyecto debe contener literales como `== 66` o
    `== 15`. Cuando WhatsApp añada un tipo nuevo, se toca únicamente este
    archivo. Los códigos no catalogados degradan a «Tipo sin catalogar (N)»,
    nunca rompen el análisis.

    No tiene interfaz de línea de órdenes: es una biblioteca de consulta que
    usan whapa.py, whareader.py y whareport.py.
"""

from enum import Enum


class Kind(str, Enum):
    """Vocabulario canónico común a Android e iOS."""
    TEXT = "text"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"
    CONTACT = "contact"
    LOCATION = "location"
    LIVE_LOCATION = "live_location"
    SYSTEM = "system"
    URL = "url"
    DOCUMENT = "document"
    GIF = "gif"
    STICKER = "sticker"
    DELETED = "deleted"
    CALL = "call"
    CALL_MISSED = "call_missed"
    EPHEMERAL_CHANGE = "ephemeral_change"
    VIEW_ONCE_IMAGE = "view_once_image"
    VIEW_ONCE_VIDEO = "view_once_video"
    VIEW_ONCE_VOICE = "view_once_voice"
    POLL = "poll"
    VIDEO_NOTE = "video_note"
    EVENT = "event"
    ALBUM = "album"
    CHANNEL_ADMIN_INV = "channel_admin_invite"
    CHANNEL_CREATE = "channel_create"
    STATUS_MENTION = "status_mention"
    AI_FEEDBACK = "ai_feedback"
    WA_NEWS = "wa_news"
    ADVANCED_PRIVACY = "advanced_privacy"
    UNKNOWN = "unknown"


# Etiquetas legibles del vocabulario canónico (para estadísticas del informe)
KIND_LABEL = {
    Kind.TEXT: "Texto", Kind.IMAGE: "Imagen", Kind.AUDIO: "Audio/nota de voz",
    Kind.VIDEO: "Vídeo", Kind.CONTACT: "Contacto", Kind.LOCATION: "Ubicación",
    Kind.LIVE_LOCATION: "Ubicación en tiempo real", Kind.SYSTEM: "Sistema",
    Kind.URL: "Enlace", Kind.DOCUMENT: "Documento", Kind.GIF: "GIF",
    Kind.STICKER: "Sticker/avatar", Kind.DELETED: "Borrado", Kind.CALL: "Llamada",
    Kind.CALL_MISSED: "Llamada perdida", Kind.EPHEMERAL_CHANGE: "Mensajes temporales",
    Kind.VIEW_ONCE_IMAGE: "Imagen de una vez", Kind.VIEW_ONCE_VIDEO: "Vídeo de una vez",
    Kind.VIEW_ONCE_VOICE: "Nota de voz de una vez", Kind.POLL: "Encuesta",
    Kind.VIDEO_NOTE: "Nota de vídeo", Kind.EVENT: "Evento", Kind.ALBUM: "Álbum",
    Kind.CHANNEL_ADMIN_INV: "Invitación admin. canal", Kind.CHANNEL_CREATE: "Creación de canal",
    Kind.STATUS_MENTION: "Mención en estado", Kind.AI_FEEDBACK: "Feedback Meta AI",
    Kind.WA_NEWS: "Novedades WhatsApp", Kind.ADVANCED_PRIVACY: "Privacidad avanzada",
    Kind.UNKNOWN: "Sin catalogar",
}

# ---------------------------------------------------------------------------
# Android moderno — tabla `message`, campo `message_type`   (informe 4.6.17)
# ---------------------------------------------------------------------------
ANDROID_MESSAGE_TYPE = {
    0: (Kind.TEXT, "Mensaje de texto y/o emoji"),
    1: (Kind.IMAGE, "Imagen"),
    2: (Kind.AUDIO, "Audio (archivo) o nota de voz"),
    3: (Kind.VIDEO, "Vídeo (archivo)"),
    4: (Kind.CONTACT, "Tarjeta de contacto"),
    5: (Kind.LOCATION, "Ubicación actual o lugares cercanos (estática)"),
    7: (Kind.SYSTEM, "Mensaje del sistema"),
    9: (Kind.DOCUMENT, "Documento (archivo)"),
    10: (Kind.CALL_MISSED, "Llamada/videollamada individual perdida"),
    13: (Kind.GIF, "GIF"),
    15: (Kind.DELETED, "Mensaje borrado por el remitente para todos"),
    16: (Kind.LIVE_LOCATION, "Ubicación en tiempo real"),
    20: (Kind.STICKER, "Sticker o avatar"),
    28: (Kind.WA_NEWS, "Cuenta oficial de WhatsApp (novedades)"),
    36: (Kind.EPHEMERAL_CHANGE, "Mensajes temporales activados/desactivados (chat individual)"),
    42: (Kind.VIEW_ONCE_IMAGE, "Imagen de visualización única"),
    43: (Kind.VIEW_ONCE_VIDEO, "Vídeo de visualización única"),
    64: (Kind.DELETED, "Mensaje de grupo borrado para todos por un administrador"),
    66: (Kind.POLL, "Encuesta"),
    81: (Kind.VIDEO_NOTE, "Nota de vídeo"),
    82: (Kind.VIEW_ONCE_VOICE, "Nota de voz de visualización única"),
    88: (Kind.AI_FEEDBACK, "Feedback del usuario sobre el bot de Meta AI"),
    90: (Kind.CALL, "Llamada o videollamada (no generada por enlace)"),
    92: (Kind.EVENT, "Evento"),
    94: (Kind.CHANNEL_ADMIN_INV, "Invitación para ser administrador de un canal"),
    99: (Kind.ALBUM, "Álbum multimedia"),
    103: (Kind.STATUS_MENTION, "Mención de un contacto en el Estado (o viceversa)"),
    112: (Kind.ADVANCED_PRIVACY, "Privacidad avanzada del chat activada/desactivada"),
}

# Android legacy — tabla `messages`, campo `media_wa_type`
ANDROID_MEDIA_WA_TYPE = {
    0: (Kind.TEXT, "Mensaje de texto"), 1: (Kind.IMAGE, "Imagen"),
    2: (Kind.AUDIO, "Audio o nota de voz"), 3: (Kind.VIDEO, "Vídeo"),
    4: (Kind.CONTACT, "Tarjeta de contacto"), 5: (Kind.LOCATION, "Ubicación"),
    8: (Kind.CALL, "Llamada de audio/vídeo"), 9: (Kind.DOCUMENT, "Documento"),
    10: (Kind.CALL_MISSED, "Llamada/videollamada perdida"),
    11: (Kind.SYSTEM, "En espera de mensaje"), 13: (Kind.GIF, "GIF"),
    14: (Kind.CONTACT, "Tarjeta de contacto (múltiple)"),
    15: (Kind.DELETED, "Mensaje borrado"),
    16: (Kind.LIVE_LOCATION, "Ubicación en tiempo real"),
    20: (Kind.STICKER, "Sticker"),
}

# ---------------------------------------------------------------------------
# iOS — tabla `ZWAMESSAGE`, campo `ZMESSAGETYPE`   (informe 5.3.8)
# ---------------------------------------------------------------------------
IOS_ZMESSAGETYPE = {
    0: (Kind.TEXT, "Mensaje de texto"), 1: (Kind.IMAGE, "Imagen"),
    2: (Kind.VIDEO, "Vídeo"), 3: (Kind.AUDIO, "Nota de voz o archivo de audio"),
    4: (Kind.CONTACT, "Tarjeta de contacto"),
    5: (Kind.LOCATION, "Ubicación en tiempo real o actual"),
    6: (Kind.SYSTEM, "Mensaje del sistema"), 7: (Kind.URL, "Enlace a una URL"),
    8: (Kind.DOCUMENT, "Documento (pdf, docx, xlsx…)"),
    10: (Kind.SYSTEM, "Mensaje del sistema"), 11: (Kind.GIF, "GIF"),
    14: (Kind.DELETED, "Mensaje eliminado para todos"),
    15: (Kind.STICKER, "Sticker o avatar"),
    28: (Kind.EPHEMERAL_CHANGE, "Cambio de temporalidad (chat individual)"),
    38: (Kind.VIEW_ONCE_IMAGE, "Imagen de visualización única"),
    39: (Kind.VIEW_ONCE_VIDEO, "Vídeo de visualización única"),
    46: (Kind.POLL, "Encuesta"),
    53: (Kind.VIEW_ONCE_VOICE, "Nota de voz de visualización única"),
    54: (Kind.VIDEO_NOTE, "Nota de vídeo"),
    55: (Kind.CHANNEL_CREATE, "Mensaje del sistema al crear/seguir un canal"),
    58: (Kind.AI_FEEDBACK, "Feedback del usuario sobre el bot de Meta AI"),
    59: (Kind.CALL, "Llamada, videollamada o chat de audio"),
    62: (Kind.CHANNEL_CREATE, "Mensaje del sistema al crear un canal"),
    63: (Kind.EVENT, "Evento"), 66: (Kind.ALBUM, "Álbum multimedia"),
    68: (Kind.STATUS_MENTION, "Mención de un contacto en el Estado (o viceversa)"),
    73: (Kind.ADVANCED_PRIVACY, "Privacidad avanzada del chat individual"),
}

# ---------------------------------------------------------------------------
# Android — `message_add_on.message_add_on_type`   (informe 4.6.18)
# ---------------------------------------------------------------------------
ADD_ON_TYPE = {
    56: "Reacción a un mensaje",
    67: "Votación en encuesta",
    68: "Mensaje temporal conservado en el chat",
    74: "Mensaje editado",
    79: "Mensaje fijado en el chat",
    93: "Evento",
}

# ---------------------------------------------------------------------------
# Android — `message_system.action_type`   (informe 4.6.45)
# ---------------------------------------------------------------------------
SYSTEM_ACTION_TYPE = {
    2: "Creación de un grupo por el usuario",
    4: "Se añadió a un contacto al grupo o a la lista de difusión",
    5: "Un participante salió del grupo",
    7: "Se eliminó a un contacto de la lista de difusión",
    9: "Creación de una lista de difusión",
    11: "Creación de un grupo o comunidad",
    12: "Se añadió a un contacto al grupo o comunidad",
    14: "Se eliminó a un usuario del grupo o comunidad",
    15: "Asignación de administrador de grupo",
    27: "Cambio de la descripción del grupo",
    29: "Solo los administradores pueden editar los ajustes del grupo",
    30: "Todos los miembros pueden editar los ajustes del grupo",
    31: "Solo los administradores pueden enviar mensajes al grupo",
    32: "Todos los miembros pueden enviar mensajes al grupo",
    56: "Duración de los mensajes temporales actualizada",
    58: "Contacto bloqueado o desbloqueado",
    59: "Mensajes temporales desactivados",
    67: "Aviso de cifrado de extremo a extremo (inicio de chat)",
    68: "Duración predeterminada de mensajes temporales en chats nuevos",
    79: "Un participante se unió al grupo desde la comunidad",
    81: "Asignación de administrador de comunidad",
    82: "Retirada de administrador de comunidad",
    84: "Aprobación de administradores para unirse al grupo activada",
    87: "Comunidad desactivada",
    91: "Cambio de ajustes del grupo o comunidad",
    129: "El contacto emisor no está en la agenda del usuario",
    132: "Creación de un canal",
    134: "Aviso de privacidad al unirse o crear un canal",
    137: "Cualquier miembro de la comunidad puede añadir grupos",
    138: "Solo administradores de la comunidad pueden añadir grupos",
    144: "Bienvenida a la comunidad",
    145: "Revisión de aprobación de unión de un grupo a una comunidad",
    148: "Bienvenida al grupo General (creación de comunidad)",
    149: "Bienvenida al grupo General (unión)",
}

# ---------------------------------------------------------------------------
# Android — `call_log`   (informe 4.6.4)
# ---------------------------------------------------------------------------
CALL_RESULT = {
    2: "Llamada sin contestar",
    4: "Llamada rechazada por todos los participantes",
    5: "Llamada descolgada (individual o por al menos un participante)",
    8: "El usuario se unió a un chat de audio en grupo",
}

CALL_TYPE = {
    0: "Llamada o videollamada (chat individual o grupal)",
    2: "Chat de audio en grupo",
}

# ---------------------------------------------------------------------------
# Android - `message.status`   (informe 4.6.17 y 8.3.1)
#
# El mismo numero significa cosas distintas segun el mensaje sea enviado o
# recibido: el 0, por ejemplo, es "no ha salido del telefono" en uno y
# "recibido en el dispositivo" en el otro. Por eso se consultan por separado.
# ---------------------------------------------------------------------------
STATUS_SENT = {
    0: "Enviado, aun no ha salido del telefono",
    1: "Enviado, aun no ha salido del telefono",
    4: "Entregado al servidor",
    5: "Entregado al destinatario",
    8: "Reproducido por el destinatario",
    13: "Leido por el destinatario",
}

STATUS_RECEIVED = {
    0: "Recibido en el dispositivo principal",
    9: "Recibido y reproducido por el usuario (sin conexion)",
    10: "Recibido y reproducido por el usuario",
    17: "Recibido y abierto en un dispositivo vinculado",
}

STATUS_SYSTEM = 6


def status_description(status, from_me):
    """Descripcion del estado de entrega/lectura de un mensaje."""
    if status is None:
        return ""
    try:
        status = int(status)
    except (TypeError, ValueError):
        return ""
    if status == STATUS_SYSTEM:
        return "Mensaje del sistema"
    tabla = STATUS_SENT if from_me else STATUS_RECEIVED
    return tabla.get(status, "Estado sin catalogar (codigo {})".format(status))


# Estados que acreditan que el destinatario abrio el mensaje
STATUS_LEIDO = {8, 13}


def status_leido(status, from_me):
    """True solo si consta que el destinatario abrio el mensaje.

    Ojo: que no conste NO prueba que no lo leyera. Si el contacto tiene
    desactivada la confirmacion de lectura, el estado no pasa de "entregado"
    aunque lo haya leido.
    """
    if not from_me or status is None:
        return False
    try:
        return int(status) in STATUS_LEIDO
    except (TypeError, ValueError):
        return False


# ---------------------------------------------------------------------------
# Plataformas
# ---------------------------------------------------------------------------
ANDROID = "android"
ANDROID_LEGACY = "android_legacy"
IOS = "ios"

PLATFORM_LABEL = {
    ANDROID: "Android (esquema actual)",
    ANDROID_LEGACY: "Android (esquema antiguo)",
    IOS: "iOS",
}

_TABLES = {
    ANDROID: ANDROID_MESSAGE_TYPE,
    ANDROID_LEGACY: ANDROID_MEDIA_WA_TYPE,
    IOS: IOS_ZMESSAGETYPE,
}

DELETED_CODES = {ANDROID: {15, 64}, ANDROID_LEGACY: {15}, IOS: {14}}


def normalize(platform, raw_type):
    """(Kind, descripción) para un código de tipo. Nunca lanza."""
    table = _TABLES.get(platform, {})
    try:
        raw_type = int(raw_type)
    except (TypeError, ValueError):
        return Kind.UNKNOWN, "Tipo desconocido ({!r})".format(raw_type)
    if raw_type in table:
        return table[raw_type]
    return Kind.UNKNOWN, "Tipo sin catalogar (código {})".format(raw_type)


def describe(platform, raw_type):
    return normalize(platform, raw_type)[1]


def kind_of(platform, raw_type):
    return normalize(platform, raw_type)[0]


def is_deleted(platform, raw_type):
    try:
        return int(raw_type) in DELETED_CODES.get(platform, set())
    except (TypeError, ValueError):
        return False


def add_on_description(t):
    try:
        return ADD_ON_TYPE.get(int(t), "Característica sin catalogar ({})".format(t))
    except (TypeError, ValueError):
        return "Característica desconocida ({!r})".format(t)


def system_action_description(t):
    try:
        return SYSTEM_ACTION_TYPE.get(int(t), "Acción de sistema sin catalogar ({})".format(t))
    except (TypeError, ValueError):
        return "Acción de sistema desconocida ({!r})".format(t)


def call_result_description(t):
    try:
        return CALL_RESULT.get(int(t), "Resultado sin catalogar ({})".format(t))
    except (TypeError, ValueError):
        return ""

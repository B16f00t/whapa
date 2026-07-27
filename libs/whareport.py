#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
whareport.py - Generacion de informes y motor de filtrado

COMETIDO DE ESTE ARCHIVO
    Convertir lo que ha leido whareader.py en algo que se pueda revisar:

      1. FILTRO (clase Filter): los criterios de seleccion de mensajes. Es el
         unico motor de filtrado del proyecto; lo usan la linea de ordenes, la
         interfaz grafica y, reimplementado en JavaScript, el propio informe.
         Asi los mismos criterios dan siempre el mismo resultado.

      2. INFORME INTERACTIVO (build_report): visor HTML que fragmenta los
         mensajes en archivos de datos y los carga al hacer scroll, con una
         ventana de DOM acotada. Aguanta conversaciones de cualquier tamano:
         el HTML inicial pesa lo mismo con 100 mensajes que con 5.000.000.

      3. INFORME IMPRIMIBLE (build_printable): documento estatico en tabla,
         pensado para papel o PDF, con numeracion correlativa, portada, los
         criterios aplicados y la verificacion SHA-256 de los origenes.

      4. EXPORTACION CSV (export_csv) de los resultados de una busqueda.

    NO lee bases de datos (de eso se encarga whareader.py) ni descifra
    (whacipher.py). No tiene linea de ordenes: la usa whapa.py.

** Author: Ivan Moreno a.k.a B16f00t
** Github: https://github.com/B16f00t
"""

import os
import re
import csv
import json
import html
import datetime
from dataclasses import dataclass, field
from typing import Optional, Set, List

import whacodes as codes
from whareader import fmt_ts, infer_device, short_jid, Message, Chat

UTC = datetime.timezone.utc


# ========================================================================
#  MOTOR DE FILTRADO Y BUSQUEDA
# ========================================================================




UTC = datetime.timezone.utc


def parse_date(v, end_of_day=False):
    """'AAAA-MM-DD' (con hora opcional) → Unix epoch UTC. None si está vacío."""
    if not v or not str(v).strip():
        return None
    v = str(v).strip()
    for f, is_day in (("%Y-%m-%d %H:%M:%S", False), ("%Y-%m-%d %H:%M", False),
                      ("%Y-%m-%d", True)):
        try:
            d = datetime.datetime.strptime(v, f).replace(tzinfo=UTC)
            if is_day and end_of_day:
                d = d.replace(hour=23, minute=59, second=59)
            return int(d.timestamp())
        except ValueError:
            continue
    raise ValueError("Fecha no válida: {} (formato AAAA-MM-DD)".format(v))


@dataclass
class Filter:
    """Criterios de selección de mensajes."""
    text: Optional[str] = None
    regex: bool = False
    case_sensitive: bool = False
    whole_word: bool = False
    chat: Optional[str] = None
    sender: Optional[str] = None
    date_from: Optional[int] = None
    date_to: Optional[int] = None
    direction: Optional[str] = None        # 'sent' | 'received' | 'system'
    kinds: Optional[Set[str]] = None       # valores de codes.Kind
    raw_types: Optional[Set[int]] = None   # códigos nativos de la plataforma
    only_deleted: bool = False
    only_starred: bool = False
    only_media: bool = False
    only_forwarded: bool = False
    only_edited: bool = False
    only_location: bool = False
    only_read: bool = False        # consta que el destinatario lo abrio
    only_unread: bool = False      # no consta que lo abriera

    _rx: object = field(default=None, repr=False, compare=False)

    # ------------------------------------------------------------------
    def _pattern(self):
        if self._rx is not None or not self.text:
            return self._rx
        flags = 0 if self.case_sensitive else re.IGNORECASE
        pat = self.text if self.regex else re.escape(self.text)
        if self.whole_word:
            pat = r"\b(?:{})\b".format(pat)
        object.__setattr__(self, "_rx", re.compile(pat, flags))
        return self._rx

    def is_empty(self):
        """True si no restringe nada."""
        return not any([
            self.text, self.chat, self.sender, self.date_from, self.date_to,
            self.direction, self.kinds, self.raw_types, self.only_deleted,
            self.only_starred, self.only_media, self.only_forwarded,
            self.only_edited, self.only_location, self.only_read,
            self.only_unread])

    # ------------------------------------------------------------------
    def searchable_text(self, m: Message) -> str:
        """Texto sobre el que busca: cuerpo, pie de foto, acción de sistema,
        nombre de archivo y texto citado."""
        parts = [m.text, m.media_caption, m.system_action, m.media_path]
        if m.quote and m.quote.text:
            parts.append(m.quote.text)
        return " ".join(p for p in parts if p)

    def match(self, m: Message, chat_label: str = "") -> bool:
        if self.date_from and (not m.timestamp or m.timestamp < self.date_from):
            return False
        if self.date_to and (not m.timestamp or m.timestamp > self.date_to):
            return False

        if self.direction:
            is_sys = m.kind is codes.Kind.SYSTEM or bool(m.system_action)
            if self.direction == "system" and not is_sys:
                return False
            if self.direction == "sent" and (not m.from_me or is_sys):
                return False
            if self.direction == "received" and (m.from_me or is_sys):
                return False

        if self.kinds and m.kind.value not in self.kinds:
            return False
        if self.raw_types and m.raw_type not in self.raw_types:
            return False

        if self.only_deleted and not m.is_deleted:
            return False
        if self.only_starred and not m.starred:
            return False
        if self.only_media and not m.media_path:
            return False
        if self.only_forwarded and not m.is_forwarded:
            return False
        if self.only_edited and not m.edited:
            return False
        if self.only_location and (m.latitude is None or m.longitude is None):
            return False
        if self.only_read and not m.leido:
            return False
        if self.only_unread and m.leido:
            return False

        if self.sender:
            s = (m.sender or "").lower()
            if self.sender.lower() not in s:
                return False

        if self.chat:
            c = self.chat.lower()
            if c not in (chat_label or "").lower() and c not in (m.chat_id or "").lower():
                return False

        rx = self._pattern()
        if rx and not rx.search(self.searchable_text(m)):
            return False
        return True

    def apply(self, messages: List[Message], chat_label: str = "") -> List[Message]:
        return [m for m in messages if self.match(m, chat_label)]

    # ------------------------------------------------------------------
    def describe(self) -> List[tuple]:
        """Criterios aplicados, en forma legible (etiqueta, valor)."""
        out = []
        if self.text:
            modo = []
            if self.regex:
                modo.append("expresión regular")
            if self.case_sensitive:
                modo.append("distingue mayúsculas")
            if self.whole_word:
                modo.append("palabra completa")
            out.append(("Texto buscado", "«{}»{}".format(
                self.text, " ({})".format(", ".join(modo)) if modo else "")))
        if self.chat:
            out.append(("Chat contiene", self.chat))
        if self.sender:
            out.append(("Remitente contiene", self.sender))
        if self.date_from:
            out.append(("Desde", fmt_ts(self.date_from) + " UTC"))
        if self.date_to:
            out.append(("Hasta", fmt_ts(self.date_to) + " UTC"))
        if self.direction:
            out.append(("Dirección", {"sent": "enviados por el usuario",
                                      "received": "recibidos",
                                      "system": "mensajes del sistema"}[self.direction]))
        if self.kinds:
            out.append(("Tipos incluidos", ", ".join(sorted(
                codes.KIND_LABEL.get(codes.Kind(k), k) for k in self.kinds))))
        if self.raw_types:
            out.append(("Códigos nativos", ", ".join(str(t) for t in sorted(self.raw_types))))
        for flag, label in ((self.only_deleted, "Solo mensajes borrados"),
                            (self.only_starred, "Solo mensajes destacados"),
                            (self.only_media, "Solo mensajes con archivo adjunto"),
                            (self.only_forwarded, "Solo mensajes reenviados"),
                            (self.only_edited, "Solo mensajes editados"),
                            (self.only_location, "Solo mensajes con coordenadas"),
                            (self.only_read, "Solo mensajes que consta que se leyeron"),
                            (self.only_unread, "Solo mensajes sin confirmacion de lectura")):
            if flag:
                out.append((label, "sí"))
        return out


# ===========================================================================
#  Búsqueda sobre una extracción completa
# ===========================================================================
@dataclass
class Hit:
    chat_id: str
    chat_label: str
    message: Message

    def snippet(self, flt: Filter, width=140) -> str:
        """Fragmento de texto alrededor de la coincidencia."""
        txt = flt.searchable_text(self.message)
        rx = flt._pattern()
        if not rx or not txt:
            return (txt or "")[:width]
        mo = rx.search(txt)
        if not mo:
            return txt[:width]
        a = max(0, mo.start() - width // 3)
        return ("…" if a else "") + txt[a:a + width] + ("…" if a + width < len(txt) else "")


def search(extraction, flt: Filter) -> List[Hit]:
    """Aplica el filtro a toda la extracción y devuelve las coincidencias."""
    hits = []
    for c in extraction.chats():
        for m in c.messages:
            if flt.match(m, c.label):
                hits.append(Hit(chat_id=c.chat_id, chat_label=c.label, message=m))
    hits.sort(key=lambda h: (h.message.timestamp or 0))
    return hits


CSV_COLUMNS = ["n", "chat", "chat_jid", "fecha_utc", "direccion", "remitente",
               "nombre_remitente", "estado", "leido",
               "entregado_a", "leido_por",
               "tipo", "codigo_tipo", "borrado", "destacado", "reenviado",
               "editado", "texto", "archivo", "latitud", "longitud",
               "key_id", "dispositivo_inferido"]


def export_csv(hits: List[Hit], path: str):
    """Vuelca las coincidencias a CSV, para cadena de análisis o anexo."""
    with open(path, "w", encoding="utf-8-sig", newline="") as fh:
        w = csv.writer(fh, delimiter=";", quoting=csv.QUOTE_MINIMAL)
        w.writerow(CSV_COLUMNS)
        for i, h in enumerate(hits, 1):
            m = h.message
            is_sys = m.kind is codes.Kind.SYSTEM or bool(m.system_action)
            w.writerow([
                i, h.chat_label, h.chat_id, fmt_ts(m.timestamp),
                "sistema" if is_sys else ("enviado" if m.from_me else "recibido"),
                m.sender or "", m.sender_name or "",
                m.status_desc or "", "si" if m.leido else "",
                m.delivered_to or "", m.read_by or "", m.type_desc,
                m.raw_type if m.raw_type is not None else "",
                "sí" if m.is_deleted else "", "sí" if m.starred else "",
                "sí" if m.is_forwarded else "", "sí" if m.edited else "",
                (m.text or m.media_caption or m.system_action or ""),
                m.media_path or "", m.latitude if m.latitude is not None else "",
                m.longitude if m.longitude is not None else "",
                m.key_id or "", infer_device(m.key_id),
            ])
    return path

# ========================================================================
#  RECURSOS DEL VISOR (CSS + JAVASCRIPT)
# ========================================================================


CSS = """
:root{--bg:#0b141a;--panel:#111b21;--in:#202c33;--out:#005c4b;--sys:#182229;
--txt:#e9edef;--muted:#8696a0;--accent:#00a884;--del:#f15c6d;--star:#f7c948;
--border:#222d34;}
*{box-sizing:border-box}
html,body{margin:0;height:100%}
body{font-family:'Segoe UI',system-ui,Helvetica,Arial,sans-serif;
background:var(--bg);color:var(--txt);font-size:14px}
a{color:var(--accent)}
header.top{background:var(--panel);padding:12px 20px;border-bottom:1px solid var(--border);
display:flex;align-items:center;gap:18px;flex-wrap:wrap}
header.top h1{margin:0;font-size:17px;color:var(--accent);white-space:nowrap}
header.top .meta{color:var(--muted);font-size:12px}
.layout{display:flex;height:calc(100vh - 53px)}
nav.chats{width:290px;min-width:290px;background:var(--panel);
border-right:1px solid var(--border);overflow-y:auto;display:flex;flex-direction:column}
nav.chats .navsearch{padding:10px}
nav.chats .navsearch input{width:100%;padding:7px 10px;border-radius:8px;
border:1px solid #2a3942;background:var(--in);color:var(--txt)}
nav.chats .item{display:block;padding:11px 15px;color:var(--txt);text-decoration:none;
border-bottom:1px solid #1c262c;cursor:pointer}
nav.chats .item:hover{background:var(--in)}
nav.chats .item.active{background:var(--in);border-left:3px solid var(--accent)}
nav.chats .item .nm{font-size:13px;display:block;overflow:hidden;
text-overflow:ellipsis;white-space:nowrap}
nav.chats .item .sub{color:var(--muted);font-size:11px}
main{flex:1;display:flex;flex-direction:column;overflow:hidden}
.toolbar{padding:10px 20px;border-bottom:1px solid var(--border);background:var(--panel);
display:flex;gap:10px;align-items:center;flex-wrap:wrap}
.toolbar h2{margin:0;font-size:15px;color:var(--accent)}
.toolbar input,.toolbar select{padding:6px 10px;border-radius:8px;
border:1px solid #2a3942;background:var(--in);color:var(--txt);font-size:13px}
.toolbar .grow{flex:1}
.toolbar .hint{color:var(--muted);font-size:11px}
#scroller{flex:1;overflow-y:auto;padding:16px 6%;scroll-behavior:auto}
.page{display:flow-root}
.msg{max-width:74%;margin:7px 0;padding:7px 11px;border-radius:10px;
clear:both;word-wrap:break-word;overflow-wrap:anywhere;line-height:1.42}
.msg.in{background:var(--in);float:left;border-top-left-radius:2px}
.msg.out{background:var(--out);float:right;border-top-right-radius:2px}
.msg.sys{background:var(--sys);color:var(--muted);margin:11px auto;text-align:center;
float:none;max-width:78%;font-size:12.5px}
.msg.del{border:1px dashed var(--del);font-style:italic;color:var(--del)}
.msg .sender{font-size:12px;color:var(--accent);font-weight:600;margin-bottom:2px}
.msg .body{white-space:pre-wrap}
.msg .quote{border-left:3px solid var(--accent);padding:3px 8px;margin-bottom:5px;
background:#0003;border-radius:4px;font-size:12.5px;color:var(--muted)}
.msg .extra{font-size:12px;color:var(--muted);margin-top:3px}
.msg.out .extra{color:#b9d8cf}
.msg .foot{margin-top:4px;font-size:10.5px;color:var(--muted);
display:flex;gap:7px;flex-wrap:wrap;align-items:center}
.msg.out .foot{color:#b9d8cf}
.badge{display:inline-block;padding:1px 6px;border-radius:6px;background:#0006;font-size:10px}
.badge.leido{color:#53bdeb}
.att{margin-top:6px}
.att img{max-width:280px;max-height:280px;border-radius:6px;display:block;cursor:pointer}
.att audio{width:270px;margin-top:3px}
.att video{max-width:300px;border-radius:6px;display:block}
.att a.doc{display:inline-block;background:#0006;border-radius:6px;padding:5px 10px;
color:var(--accent);text-decoration:none;font-size:12.5px}
.att a.doc:hover{background:#0009}
.miss{font-size:12px;color:var(--muted);font-style:italic}
.loc{margin-top:6px;background:#0004;border-radius:8px;padding:8px 10px;
border-left:3px solid var(--accent)}
.loc .co{font-family:ui-monospace,Consolas,monospace;font-size:13px;
color:var(--txt);user-select:all}
.loc .lk{margin-top:5px;display:flex;gap:10px;flex-wrap:wrap}
.loc .lk a{font-size:12px;color:var(--accent);text-decoration:none}
.loc .lk a:hover{text-decoration:underline}
.loc img{max-width:300px;border-radius:6px;margin-top:6px;display:block}
.loc .live{display:inline-block;background:var(--accent);color:#04160f;
border-radius:9px;padding:1px 8px;font-size:10.5px;font-weight:600;
margin-bottom:4px}
.react{display:inline-block;background:#0006;border-radius:10px;padding:1px 7px;
font-size:11px;margin-top:3px}
.star{color:var(--star)}
.loading{text-align:center;color:var(--muted);padding:14px;font-size:12px}
.results{padding:6px 0}
.results .hit{padding:8px 12px;border-bottom:1px solid var(--border);cursor:pointer}
.results .hit:hover{background:var(--in)}
.results .hit .w{color:var(--muted);font-size:11px}
mark{background:var(--star);color:#000;border-radius:2px}
.stats{padding:16px 6%}
.stats table{border-collapse:collapse;margin:10px 0;font-size:13px}
.stats td,.stats th{border:1px solid var(--border);padding:6px 12px;text-align:left}
.stats th{background:var(--panel);color:var(--accent)}
.pill{display:inline-block;background:var(--in);padding:4px 10px;
border-radius:14px;font-size:12px;margin:3px 4px 0 0}
.mono{font-family:ui-monospace,Consolas,monospace;font-size:11.5px;word-break:break-all}
.panel{background:var(--panel);border-bottom:1px solid var(--border);
padding:10px 20px;display:none}
.panel.open{display:block}
.panel .grid{display:flex;flex-wrap:wrap;gap:10px 16px;align-items:flex-end}
.panel .f{display:flex;flex-direction:column;gap:3px}
.panel .f label{font-size:10.5px;color:var(--muted);text-transform:uppercase;
letter-spacing:.4px}
.panel input[type=text],.panel input[type=date],.panel select{
padding:6px 9px;border-radius:7px;border:1px solid #2a3942;background:var(--in);
color:var(--txt);font-size:13px}
.panel .chk{display:flex;flex-wrap:wrap;gap:4px 14px;margin-top:8px}
.panel .chk label{font-size:12px;color:var(--txt);display:flex;gap:5px;
align-items:center;cursor:pointer}
.panel .acts{margin-top:10px;display:flex;gap:8px;flex-wrap:wrap;align-items:center}
.crit{background:var(--in);border-radius:8px;padding:9px 13px;margin:10px 0;
font-size:12px;color:var(--muted);line-height:1.7}
.crit b{color:var(--txt)}
.grp{margin:16px 0 6px;color:var(--accent);font-size:13px;font-weight:600;
border-bottom:1px solid var(--border);padding-bottom:4px}
.printview{display:none}
button{padding:6px 12px;border-radius:8px;border:1px solid #2a3942;
background:var(--in);color:var(--txt);cursor:pointer;font-size:13px}
button:hover{background:#2a3942}
#printWarn{position:fixed;inset:0;background:#000b;display:none;
align-items:center;justify-content:center;z-index:50}
#printWarn .box{background:var(--panel);padding:22px;border-radius:10px;
max-width:460px;border:1px solid var(--border)}
#printWarn h3{margin:0 0 10px;color:var(--accent)}
#printWarn p{color:var(--muted);font-size:13px;line-height:1.5}

/* ---- impresión desde el visor ----
   El scroll virtual deja huecos vacíos, así que antes de imprimir hay que
   expandir el chat entero (botón Imprimir). Este bloque solo se ocupa de que
   lo expandido salga legible en papel. */
@media print{
  @page{size:A4;margin:14mm}
  body{background:#fff;color:#000}
  header.top,nav.chats,.toolbar,.panel,#printWarn{display:none!important}
  .printview{display:block!important}
  .printview table{width:100%;border-collapse:collapse;font-size:9pt}
  .printview th,.printview td{border:1px solid #999;padding:3px 5px;
    vertical-align:top;text-align:left;color:#000}
  .printview th{background:#e8e8e8}
  .printview thead{display:table-header-group}
  .printview tr{page-break-inside:avoid}
  .printview h2,.printview h3{color:#000}
  .printview .crit{background:#f4f4f4;color:#000;border:1px solid #999}
  .printview .crit b{color:#000}
  #scroller.hidden-print{display:none!important}
  .layout{display:block;height:auto}
  main{overflow:visible}
  #scroller{overflow:visible;height:auto;padding:0}
  .msg{max-width:100%;float:none!important;page-break-inside:avoid;
       border:1px solid #bbb;background:#fff!important;color:#000!important;
       margin:4px 0;border-radius:4px}
  .msg.out{background:#f2f7f4!important;margin-left:12%}
  .msg.sys{background:#f4f4f4!important;font-style:italic}
  .msg.del{background:#fdeeee!important;color:#a00!important}
  .msg .foot,.msg .extra,.msg .quote{color:#444!important}
  .msg .sender{color:#000!important}
  .badge{background:#eee!important;color:#333!important;border:1px solid #ccc}
}
"""

JS = r"""
/* =====================================================================
   whapa2 — visor de informes con carga progresiva
   Formato de cada mensaje (array, para reducir el tamaño de los datos):
     0 rowid | 1 fromMe | 2 idxRemitente | 3 ts | 4 rawType | 5 texto
     6 keyId | 7 flags  | 8 rutaMedia    | 9 lat | 10 lon   | 11 cita
     12 reacciones
   flags: 1=borrado 2=destacado 4=reenviado 8=editado 16=sistema
   ===================================================================== */
var WHAPA = {
  meta: null, chats: [], types: {}, store: {}, pending: {},
  cur: -1, rendered: [], MAX_PAGES: 6, single: false,

  /* ---- recepción de datos (la llaman los archivos data/*.js) ---- */
  recv: function(ci, pi, rows){
    (this.store[ci] = this.store[ci] || {})[pi] = rows;
    var k = ci + ':' + pi, cbs = this.pending[k];
    if (cbs){ delete this.pending[k]; cbs.forEach(function(f){ f(rows); }); }
  },

  needPage: function(ci, pi, cb){
    var s = this.store[ci];
    if (s && s[pi]) { cb(s[pi]); return; }
    var k = ci + ':' + pi;
    if (this.pending[k]) { this.pending[k].push(cb); return; }
    this.pending[k] = [cb];
    var sc = document.createElement('script');
    sc.src = 'data/c' + pad(ci,4) + '_p' + pad(pi,4) + '.js';
    sc.onerror = function(){ WHAPA.recv(ci, pi, []); };
    document.body.appendChild(sc);
  },

  /* ---- utilidades ---- */
  typeDesc: function(t){ return this.types[t] || ('Tipo sin catalogar (' + t + ')'); },

  device: function(k){
    if(!k) return '';
    k = String(k).toUpperCase(); var n = k.length;
    if(n>=9 && n<=10 && /^[0-9]+$/.test(k)) return 'Sistema (grupo/comunidad)';
    if(n===18) return 'Windows / Wear OS';
    if(n===20){
      if(k.indexOf('3EB0')===0) return 'WhatsApp Web';
      if(k.indexOf('5E')===0) return 'iOS';
      if(k.indexOf('3A')===0) return 'iOS / iPadOS / macOS';
    }
    if(n===30 || n===32) return 'Android';
    return '';
  }
};

function pad(n,w){ n = String(n); while(n.length<w) n = '0'+n; return n; }
function esc(s){ return (s==null?'':String(s))
  .replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;'); }
function fmtTs(t){
  if(!t) return '';
  var d = new Date(t*1000);
  return d.toISOString().replace('T',' ').substring(0,19);
}

/* ---------------- render de un mensaje ---------------- */
function renderMsg(ci, m){
  var chat = WHAPA.chats[ci];
  var flags = m[7]||0;
  var isSys = (flags & 16) !== 0, isDel = (flags & 1) !== 0;
  var cls = isSys ? 'msg sys' : (m[1] ? 'msg out' : 'msg in');
  if(isDel) cls += ' del';
  var h = '<div class="'+cls+'" id="m'+ci+'_'+m[0]+'">';

  if(!m[1] && !isSys && m[2]!=null && chat.senders[m[2]])
    h += '<div class="sender">'+esc(chat.senders[m[2]])+'</div>';

  if(m[11]) h += '<div class="quote">'+esc(m[11])+'</div>';

  var body = m[5];
  if(!body) body = '['+WHAPA.typeDesc(m[4])+']';
  h += '<div class="body">'+esc(body)+'</div>';

  if(m[8] || m[13]) h += mediaHtml(m);
  if(m[9]!=null && m[10]!=null) h += locHtml(m);
  if(m[12]) h += '<div class="react">'+esc(m[12])+'</div>';

  var f = [];
  if(flags & 2) f.push('<span class="star">★</span>');
  if(flags & 4) f.push('<span class="badge">reenviado</span>');
  if(flags & 8) f.push('<span class="badge">editado</span>');
  f.push(fmtTs(m[3]));
  f.push('<span class="badge">'+esc(WHAPA.typeDesc(m[4]))+' ('+m[4]+')</span>');
  if(m[15]) f.push('<span class="badge' + (m[16] ? ' leido' : '') + '">' +
                   (m[16] ? '\u2713\u2713 ' : '') + esc(m[15]) + '</span>');
  var dev = WHAPA.device(m[6]);
  if(dev) f.push('<span class="badge">'+dev+'</span>');
  if(m[6]) f.push('<span class="badge mono">'+esc(m[6])+'</span>');
  h += '<div class="foot">'+f.join(' ')+'</div></div>';
  return h;
}

/* ---- ubicaciones ----
   No se carga ninguna imagen remota: un informe que pide un mapa a un tercero
   cada vez que se abre filtra las coordenadas del caso y deja de funcionar sin
   conexion. Se muestran las coordenadas y se ofrecen enlaces, que el usuario
   pulsa si quiere. Con la opcion -gm el mapa se descarga al generar el informe
   y se guarda dentro, asi que sigue viendose sin conexion. */
function locHtml(m){
  var la = m[9], lo = m[10];
  var vivo = WHAPA.typeDesc(m[4]).toLowerCase().indexOf('tiempo real') >= 0 ||
             WHAPA.typeDesc(m[4]).toLowerCase().indexOf('live') >= 0;
  var h = '<div class="loc">';
  if(vivo) h += '<span class="live">UBICACION EN TIEMPO REAL</span>';
  h += '<div class="co">\u{1F4CD} ' + la + ', ' + lo + '</div>';
  if(m[14]) h += '<img src="' + esc(m[14]) + '" loading="lazy" alt="mapa">';
  h += '<div class="lk">' +
       '<a href="https://www.google.com/maps?q=' + la + ',' + lo +
       '" target="_blank" rel="noreferrer">Google Maps</a>' +
       '<a href="https://www.openstreetmap.org/?mlat=' + la + '&mlon=' + lo +
       '#map=17/' + la + '/' + lo + '" target="_blank" rel="noreferrer">OpenStreetMap</a>' +
       '</div></div>';
  return h;
}

/* ---- adjuntos: se muestran si se localizo el archivo ---- */
function mediaKind(u){
  var e = (u||'').toLowerCase().split('?')[0];
  e = e.substring(e.lastIndexOf('.'));
  if('.jpg.jpeg.png.webp.gif.bmp'.indexOf(e)>=0 && e) return 'image';
  if('.opus.ogg.mp3.m4a.aac.wav.amr'.indexOf(e)>=0 && e) return 'audio';
  if('.mp4.3gp.mov.mkv.avi.webm'.indexOf(e)>=0 && e) return 'video';
  return 'file';
}

function mediaHtml(m){
  var url = m[13], ruta = m[8] || '';
  var h = '<div class="att">';
  if(!url){
    // No se aporto la carpeta, o el archivo no esta: se deja constancia igual
    h += '<div class="miss">\u{1F4CE} ' + esc(ruta) +
         ' <span class="badge">no localizado</span></div>';
    return h + '</div>';
  }
  var k = mediaKind(url), nombre = url.split('/').pop();
  if(k === 'image'){
    h += '<a href="'+esc(url)+'" target="_blank"><img src="'+esc(url)+
         '" loading="lazy" alt="'+esc(nombre)+'"></a>';
  } else if(k === 'audio'){
    h += '<audio controls preload="none" src="'+esc(url)+'"></audio>';
  } else if(k === 'video'){
    h += '<video controls preload="none" src="'+esc(url)+'"></video>';
  } else {
    h += '<a class="doc" href="'+esc(url)+'" target="_blank">\u{1F4C4} '+
         esc(nombre)+'</a>';
  }
  h += '<div class="miss">'+esc(ruta)+'</div></div>';
  return h;
}

/* ---------------- gestión de páginas y ventana de DOM ---------------- */
var io = null, scroller = null;

function pageEl(pi){ return document.getElementById('pg'+pi); }

function ensurePage(pi, then){
  var el = pageEl(pi);
  if(el && el.dataset.state === 'full'){ if(then) then(el); return; }
  WHAPA.needPage(WHAPA.cur, pi, function(rows){
    var e = pageEl(pi);
    if(!e) return;
    var buf = [];
    for(var i=0;i<rows.length;i++) buf.push(renderMsg(WHAPA.cur, rows[i]));
    var prevH = e.offsetHeight;
    e.innerHTML = buf.join('');
    e.style.height = '';
    e.dataset.state = 'full';
    // mantener la posición si el contenido crece por encima del viewport
    if(e.getBoundingClientRect().bottom < 0)
      scroller.scrollTop += (e.offsetHeight - prevH);
    trackRendered(pi);
    if(then) then(e);
  });
}

function trackRendered(pi){
  var r = WHAPA.rendered;
  var k = r.indexOf(pi);
  if(k >= 0) r.splice(k,1);
  r.push(pi);
  while(r.length > WHAPA.MAX_PAGES){
    var victim = r.shift();
    collapsePage(victim);
  }
}

function collapsePage(pi){
  var e = pageEl(pi);
  if(!e || e.dataset.state !== 'full') return;
  var h = e.offsetHeight;
  e.style.height = h + 'px';
  e.innerHTML = '';
  e.dataset.state = 'stub';
}

function openChat(ci){
  WHAPA.cur = ci; WHAPA.rendered = [];
  var chat = WHAPA.chats[ci];
  document.querySelectorAll('nav.chats .item').forEach(function(a){
    a.classList.toggle('active', +a.dataset.i === ci); });
  document.getElementById('chatTitle').textContent =
    chat.name + (chat.group ? ' · grupo' : '');
  document.getElementById('chatSub').textContent =
    chat.n + ' mensajes · ' + chat.pages + ' páginas de datos';
  document.getElementById('q').value = '';

  var frags = [];
  for(var p=0;p<chat.pages;p++)
    frags.push('<div class="page" id="pg'+p+'" data-p="'+p+'" data-state="stub" '+
               'style="height:'+(chat.est||600)+'px"></div>');
  scroller.innerHTML = frags.join('');
  scroller.scrollTop = 0;

  if(io) io.disconnect();
  io = new IntersectionObserver(function(entries){
    entries.forEach(function(en){
      if(en.isIntersecting) ensurePage(+en.target.dataset.p);
    });
  }, {root: scroller, rootMargin: '900px 0px'});
  document.querySelectorAll('#scroller .page').forEach(function(e){ io.observe(e); });
  ensurePage(0);
}

/* ---------------- búsqueda dentro del chat ---------------- */
function searchChat(){
  var q = document.getElementById('q').value.trim().toLowerCase();
  if(q.length < 2){ openChat(WHAPA.cur); return; }
  var chat = WHAPA.chats[WHAPA.cur], ci = WHAPA.cur;
  var hits = [], done = 0;
  scroller.innerHTML = '<div class="loading">Buscando en '+chat.pages+' páginas…</div>';
  for(var p=0;p<chat.pages;p++){
    (function(pi){
      WHAPA.needPage(ci, pi, function(rows){
        for(var i=0;i<rows.length;i++){
          var t = rows[i][5];
          if(t && t.toLowerCase().indexOf(q) >= 0 && hits.length < 1000)
            hits.push([pi, rows[i]]);
        }
        if(++done === chat.pages) showHits(hits, q);
      });
    })(p);
  }
}

function showHits(hits, q){
  hits.sort(function(a,b){ return (a[1][3]||0) - (b[1][3]||0); });
  if(!hits.length){ scroller.innerHTML = '<div class="loading">Sin coincidencias.</div>'; return; }
  var h = ['<div class="loading">'+hits.length+' coincidencia(s)</div><div class="results">'];
  hits.forEach(function(x){
    var m = x[1], txt = String(m[5]||'');
    var i = txt.toLowerCase().indexOf(q);
    var frag = esc(txt.substring(Math.max(0,i-60), i+120));
    h.push('<div class="hit" onclick="jumpTo('+x[0]+','+m[0]+')">'+
           '<div class="w">'+fmtTs(m[3])+' · '+(m[1]?'enviado':'recibido')+'</div>'+
           frag+'</div>');
  });
  h.push('</div>');
  scroller.innerHTML = h.join('');
}

function jumpTo(pi, rowid){
  var q = document.getElementById('q').value;
  document.getElementById('q').value = '';
  openChat(WHAPA.cur);
  setTimeout(function(){
    ensurePage(pi, function(){
      var el = document.getElementById('m'+WHAPA.cur+'_'+rowid);
      if(el){ el.scrollIntoView({block:'center'}); el.style.outline='2px solid var(--star)'; }
    });
  }, 60);
}


/* ===================================================================
   BÚSQUEDA AVANZADA
   Un único motor que replica el de whapa2/query.py, para que los mismos
   criterios den el mismo resultado en el visor y en la línea de órdenes.
   =================================================================== */
WHAPA.lastHits = [];
WHAPA.lastFilter = null;

function togglePanel(){
  var p = document.getElementById('panel');
  p.classList.toggle('open');
  if(p.classList.contains('open')) fillTypeSelect();
}

function fillTypeSelect(){
  var sel = document.getElementById('fType');
  if(sel.dataset.filled) return;
  var keys = Object.keys(WHAPA.types).sort(function(a,b){ return a-b; });
  keys.forEach(function(k){
    var o = document.createElement('option');
    o.value = k; o.textContent = WHAPA.types[k] + ' (' + k + ')';
    sel.appendChild(o);
  });
  sel.dataset.filled = '1';
}

function val(id){ var e = document.getElementById(id); return e ? e.value.trim() : ''; }
function chk(id){ var e = document.getElementById(id); return !!(e && e.checked); }

function buildFilter(){
  var txt = val('fText');
  var f = {
    text: txt, regex: chk('fRegex'), caseSens: chk('fCase'), whole: chk('fWord'),
    scope: val('fScope'), sender: val('fSender').toLowerCase(),
    from: val('fFrom') ? Date.parse(val('fFrom') + 'T00:00:00Z')/1000 : null,
    to:   val('fTo')   ? Date.parse(val('fTo')   + 'T23:59:59Z')/1000 : null,
    dir: val('fDir'), type: val('fType'),
    del: chk('fDel'), star: chk('fStar'), media: chk('fMedia'),
    fwd: chk('fFwd'), edit: chk('fEdit'), loc: chk('fLoc'), rx: null
  };
  if(txt){
    var pat = f.regex ? txt : txt.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    if(f.whole) pat = '\\b(?:' + pat + ')\\b';
    try { f.rx = new RegExp(pat, f.caseSens ? '' : 'i'); }
    catch(e){ alert('Expresión regular no válida: ' + e.message); return null; }
  }
  return f;
}

function filterEmpty(f){
  return !f.text && !f.sender && !f.from && !f.to && !f.dir && !f.type &&
         !f.del && !f.star && !f.media && !f.fwd && !f.edit && !f.loc;
}

function msgText(m){
  return [m[5], m[8], m[11]].filter(Boolean).join(' ');
}

function matchMsg(f, m){
  var flags = m[7] || 0;
  var isSys = (flags & 16) !== 0;
  if(f.from && (!m[3] || m[3] < f.from)) return false;
  if(f.to   && (!m[3] || m[3] > f.to))   return false;
  if(f.dir === 'system'   && !isSys) return false;
  if(f.dir === 'sent'     && (!m[1] || isSys)) return false;
  if(f.dir === 'received' && (m[1] || isSys))  return false;
  if(f.type !== '' && String(m[4]) !== String(f.type)) return false;
  if(f.del   && !(flags & 1))  return false;
  if(f.star  && !(flags & 2))  return false;
  if(f.fwd   && !(flags & 4))  return false;
  if(f.edit  && !(flags & 8))  return false;
  if(f.media && !m[8])         return false;
  if(f.loc   && (m[9] == null || m[10] == null)) return false;
  if(f.sender){
    var chat = WHAPA.chats[f._ci];
    var s = (m[2] != null && chat && chat.senders[m[2]]) ? chat.senders[m[2]].toLowerCase() : '';
    if(s.indexOf(f.sender) < 0) return false;
  }
  if(f.rx && !f.rx.test(msgText(m))) return false;
  return true;
}

function runSearch(){
  var f = buildFilter();
  if(!f) return;
  if(filterEmpty(f)){ alert('Indica al menos un criterio de búsqueda.'); return; }

  var targets = (f.scope === 'all')
      ? WHAPA.chats.map(function(c,i){ return i; })
      : [WHAPA.cur];
  var totalPages = targets.reduce(function(a,i){ return a + WHAPA.chats[i].pages; }, 0);
  var done = 0, hits = [];
  scroller.innerHTML = '<div class="loading" id="prog">Buscando… 0 / ' + totalPages + ' páginas</div>';

  targets.forEach(function(ci){
    var chat = WHAPA.chats[ci];
    for(var p = 0; p < chat.pages; p++){
      (function(ci, pi){
        WHAPA.needPage(ci, pi, function(rows){
          f._ci = ci;
          for(var i = 0; i < rows.length; i++)
            if(matchMsg(f, rows[i])) hits.push({ci: ci, pi: pi, m: rows[i]});
          done++;
          var pr = document.getElementById('prog');
          if(pr) pr.textContent = 'Buscando… ' + done + ' / ' + totalPages + ' páginas';
          if(done === totalPages){
            hits.sort(function(a,b){ return (a.m[3]||0) - (b.m[3]||0); });
            WHAPA.lastHits = hits; WHAPA.lastFilter = f;
            renderResults(hits, f);
          }
        });
      })(ci, p);
    }
  });
}

function critHtml(f){
  var c = [];
  if(f.text){
    var mo = [];
    if(f.regex) mo.push('expresión regular');
    if(f.caseSens) mo.push('distingue mayúsculas');
    if(f.whole) mo.push('palabra completa');
    c.push('Texto buscado: <b>«' + esc(f.text) + '»</b>' +
           (mo.length ? ' (' + mo.join(', ') + ')' : ''));
  }
  c.push('Ámbito: <b>' + (f.scope === 'all' ? 'todos los chats'
        : 'chat «' + esc(WHAPA.chats[WHAPA.cur].name) + '»') + '</b>');
  if(f.sender) c.push('Remitente contiene: <b>' + esc(f.sender) + '</b>');
  if(f.from) c.push('Desde: <b>' + fmtTs(f.from) + ' UTC</b>');
  if(f.to)   c.push('Hasta: <b>' + fmtTs(f.to) + ' UTC</b>');
  if(f.dir)  c.push('Dirección: <b>' + ({sent:'enviados', received:'recibidos',
                                         system:'del sistema'})[f.dir] + '</b>');
  if(f.type !== '') c.push('Tipo: <b>' + esc(WHAPA.typeDesc(f.type)) + ' (' + f.type + ')</b>');
  [[f.del,'solo borrados'],[f.star,'solo destacados'],[f.media,'solo con adjunto'],
   [f.fwd,'solo reenviados'],[f.edit,'solo editados'],[f.loc,'solo con coordenadas']
  ].forEach(function(x){ if(x[0]) c.push('<b>' + x[1] + '</b>'); });
  return '<div class="crit"><b>Criterios aplicados</b><br>' + c.join(' · ') + '</div>';
}

function renderResults(hits, f){
  var h = [critHtml(f)];
  h.push('<div class="loading">' + hits.length.toLocaleString('es') +
         ' coincidencia(s)</div>');
  if(!hits.length){ scroller.innerHTML = h.join(''); return; }

  var byChat = {};
  hits.forEach(function(x){ (byChat[x.ci] = byChat[x.ci] || []).push(x); });

  h.push('<div class="results">');
  Object.keys(byChat).forEach(function(ci){
    var lst = byChat[ci];
    h.push('<div class="grp">' + esc(WHAPA.chats[ci].name) + ' — ' +
           lst.length.toLocaleString('es') + ' coincidencia(s)</div>');
    lst.slice(0, 2000).forEach(function(x){
      var m = x.m, txt = msgText(m), frag;
      if(f.rx){
        var mo = f.rx.exec(txt); f.rx.lastIndex = 0;
        var a = mo ? Math.max(0, mo.index - 50) : 0;
        frag = esc(txt.substring(a, a + 170));
        if(mo) frag = frag.replace(esc(mo[0]), '<mark>' + esc(mo[0]) + '</mark>');
      } else { frag = esc(txt.substring(0, 170)); }
      var chat = WHAPA.chats[ci];
      var who = (m[2] != null && chat.senders[m[2]]) ? chat.senders[m[2]] : '';
      h.push('<div class="hit" onclick="jumpToHit(' + ci + ',' + x.pi + ',' + m[0] + ')">' +
             '<div class="w">' + fmtTs(m[3]) + ' · ' +
             (m[1] ? 'enviado' : 'recibido') + (who ? ' · ' + esc(who) : '') +
             ' · ' + esc(WHAPA.typeDesc(m[4])) + '</div>' + frag + '</div>');
    });
    if(lst.length > 2000)
      h.push('<div class="loading">… ' + (lst.length - 2000) +
             ' más no mostradas; usa la exportación CSV</div>');
  });
  h.push('</div>');
  scroller.innerHTML = h.join('');
}

function jumpToHit(ci, pi, rowid){
  if(ci !== WHAPA.cur) openChat(ci);
  setTimeout(function(){
    ensurePage(pi, function(){
      var el = document.getElementById('m' + ci + '_' + rowid);
      if(el){ el.scrollIntoView({block:'center'}); el.style.outline = '2px solid var(--star)'; }
    });
  }, 60);
}

function clearSearch(){
  ['fText','fSender','fFrom','fTo'].forEach(function(i){
    var e = document.getElementById(i); if(e) e.value = ''; });
  ['fRegex','fCase','fWord','fDel','fStar','fMedia','fFwd','fEdit','fLoc'].forEach(
    function(i){ var e = document.getElementById(i); if(e) e.checked = false; });
  document.getElementById('fDir').value = '';
  document.getElementById('fType').value = '';
  WHAPA.lastHits = [];
  if(WHAPA.cur >= 0) openChat(WHAPA.cur);
}

/* ---- impresión de los resultados de búsqueda ---- */
function printResults(){
  var hits = WHAPA.lastHits, f = WHAPA.lastFilter;
  if(!hits || !hits.length){ alert('Primero realiza una búsqueda con resultados.'); return; }
  var h = ['<h2>Resultados de búsqueda</h2>', critHtml(f),
           '<div class="crit">Total: <b>' + hits.length.toLocaleString('es') +
           '</b> coincidencia(s) · Documento generado ' +
           new Date().toISOString().substring(0,19).replace('T',' ') + ' UTC</div>',
           '<table><thead><tr><th>N.º</th><th>Chat</th><th>Fecha (UTC)</th>',
           '<th>Dir.</th><th>Remitente</th><th>Tipo (código)</th><th>Contenido</th>',
           '</tr></thead><tbody>'];
  hits.forEach(function(x, i){
    var m = x.m, chat = WHAPA.chats[x.ci];
    var who = (m[2] != null && chat.senders[m[2]]) ? chat.senders[m[2]] : '';
    var flags = m[7] || 0;
    var marks = [];
    if(flags & 1) marks.push('borrado');
    if(flags & 2) marks.push('destacado');
    if(flags & 4) marks.push('reenviado');
    if(flags & 8) marks.push('editado');
    h.push('<tr><td>' + (i+1) + '</td><td>' + esc(chat.name) + '</td><td>' +
           fmtTs(m[3]) + '</td><td>' +
           ((flags & 16) ? 'sis' : (m[1] ? 'env' : 'rec')) + '</td><td>' +
           esc(who) + '</td><td>' + esc(WHAPA.typeDesc(m[4])) + ' (' + m[4] + ')</td><td>' +
           esc(msgText(m)) + (marks.length ? ' [' + marks.join(', ') + ']' : '') +
           (m[6] ? '<br><small>ID: ' + esc(m[6]) + '</small>' : '') + '</td></tr>');
  });
  h.push('</tbody></table>');
  var pv = document.getElementById('printview');
  pv.innerHTML = h.join('');
  scroller.classList.add('hidden-print');
  setTimeout(function(){
    window.print();
    scroller.classList.remove('hidden-print');
    pv.innerHTML = '';
  }, 200);
}

/* ---- exportación CSV de los resultados ---- */
function exportCSV(){
  var hits = WHAPA.lastHits;
  if(!hits || !hits.length){ alert('Primero realiza una búsqueda con resultados.'); return; }
  var q = function(v){ return '"' + String(v == null ? '' : v).replace(/"/g,'""') + '"'; };
  var rows = [['n','chat','fecha_utc','direccion','remitente','tipo','codigo_tipo',
               'borrado','destacado','reenviado','editado','texto','archivo',
               'latitud','longitud','key_id','dispositivo_inferido'].join(';')];
  hits.forEach(function(x, i){
    var m = x.m, chat = WHAPA.chats[x.ci], flags = m[7] || 0;
    var who = (m[2] != null && chat.senders[m[2]]) ? chat.senders[m[2]] : '';
    rows.push([i+1, chat.name, fmtTs(m[3]),
               (flags & 16) ? 'sistema' : (m[1] ? 'enviado' : 'recibido'),
               who, WHAPA.typeDesc(m[4]), m[4],
               (flags & 1) ? 'sí' : '', (flags & 2) ? 'sí' : '',
               (flags & 4) ? 'sí' : '', (flags & 8) ? 'sí' : '',
               m[5] || '', m[8] || '', m[9] == null ? '' : m[9],
               m[10] == null ? '' : m[10], m[6] || '', WHAPA.device(m[6])
              ].map(q).join(';'));
  });
  var blob = new Blob(['\ufeff' + rows.join('\r\n')],
                      {type:'text/csv;charset=utf-8;'});
  var a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = 'whapa2_busqueda_' +
               new Date().toISOString().substring(0,10) + '.csv';
  document.body.appendChild(a); a.click();
  setTimeout(function(){ URL.revokeObjectURL(a.href); a.remove(); }, 500);
}

/* ---------------- impresión ----------------
   Expande TODAS las páginas del chat actual (desactivando la ventana de DOM
   acotada) y solo entonces llama a print(). Sin esto se imprimirían huecos. */
function printChat(){
  var chat = WHAPA.chats[WHAPA.cur];
  if(!chat) return;
  if(chat.n > 5000){
    var box = document.getElementById('printWarn');
    document.getElementById('pwText').innerHTML =
      'Este chat tiene <b>' + chat.n.toLocaleString('es') + ' mensajes</b>. ' +
      'Para imprimirlo hay que cargarlos todos en memoria, lo que puede tardar ' +
      'y ocupar del orden de ' + Math.ceil(chat.n/45) + ' páginas de papel.<br><br>' +
      'Para un documento manejable conviene generar el informe imprimible con ' +
      'filtros desde la línea de órdenes:<br>' +
      '<code>python3 whapa.py print --db ... --chat "' + chat.name +
      '" --from 2024-01-01 --to 2024-06-30</code>';
    box.style.display = 'flex';
    return;
  }
  doPrint();
}

function doPrint(){
  document.getElementById('printWarn').style.display = 'none';
  var chat = WHAPA.chats[WHAPA.cur], pending = chat.pages;
  var oldMax = WHAPA.MAX_PAGES;
  WHAPA.MAX_PAGES = Infinity;            // desactivar el recorte de DOM
  var sc = document.getElementById('scroller');
  var note = document.createElement('div');
  note.className = 'loading'; note.id = 'pnote';
  note.textContent = 'Preparando ' + chat.n + ' mensajes para imprimir…';
  sc.parentNode.insertBefore(note, sc);
  for(var p = 0; p < chat.pages; p++){
    (function(pi){
      WHAPA.needPage(WHAPA.cur, pi, function(rows){
        var e = pageEl(pi);
        if(e && e.dataset.state !== 'full'){
          var buf = [];
          for(var i=0;i<rows.length;i++) buf.push(renderMsg(WHAPA.cur, rows[i]));
          e.innerHTML = buf.join(''); e.style.height = ''; e.dataset.state = 'full';
        }
        if(--pending === 0){
          var nd = document.getElementById('pnote'); if(nd) nd.remove();
          setTimeout(function(){
            window.print();
            WHAPA.MAX_PAGES = oldMax;    // restaurar tras imprimir
          }, 250);
        }
      });
    })(p);
  }
}

/* ---------------- arranque ---------------- */
function boot(){
  scroller = document.getElementById('scroller');
  var nav = document.getElementById('navlist');
  nav.innerHTML = WHAPA.chats.map(function(c,i){
    return '<div class="item" data-i="'+i+'" onclick="openChat('+i+')">'+
      '<span class="nm">'+esc(c.name)+(c.group?' 👥':'')+'</span>'+
      '<span class="sub">'+c.n+' msgs · '+(c.last||'')+'</span></div>';
  }).join('');
  document.getElementById('navq').addEventListener('input', function(){
    var v = this.value.toLowerCase();
    document.querySelectorAll('nav.chats .item').forEach(function(a){
      a.style.display = a.textContent.toLowerCase().indexOf(v) >= 0 ? '' : 'none';
    });
  });
  document.getElementById('q').addEventListener('keydown', function(e){
    if(e.key === 'Enter') searchChat();
  });
  if(WHAPA.chats.length) openChat(0);
}
"""

# ========================================================================
#  INFORME INTERACTIVO
# ========================================================================




PAGE_SIZE = 500          # mensajes por archivo de datos
SINGLE_FILE_LIMIT = 20000


# ===========================================================================
#  Serialización compacta
# ===========================================================================
def _flags(m):
    f = 0
    if m.is_deleted:
        f |= 1
    if m.starred:
        f |= 2
    if m.is_forwarded:
        f |= 4
    if m.edited:
        f |= 8
    if m.kind is codes.Kind.SYSTEM or m.system_action:
        f |= 16
    return f


def _quote_text(m):
    if not m.quote:
        return None
    q = m.quote
    who = q.sender or ""
    body = q.text or (q.type_desc or "")
    return ("↩ {}: {}".format(who, body) if who else "↩ {}".format(body))[:300]


def _reactions_text(m):
    if not m.reactions:
        return None
    return " ".join("{}{}".format(r.emoji, "" if r.from_me else "")
                    for r in m.reactions)[:120]


def _serialize(m, sender_idx, href=None, maphref=None):
    """Mensaje -> array compacto. El orden está documentado en assets.JS."""
    body = m.text or m.media_caption or m.system_action
    si = None
    quien = m.sender_name or m.sender
    if quien:
        # Se guarda "Nombre (numero)" cuando hay nombre: el informe debe permitir
        # identificar a la persona sin perder el dato original de la base.
        if m.sender_name and m.sender and m.sender_name != m.sender:
            quien = "{} ({})".format(m.sender_name, m.sender)
        si = sender_idx.setdefault(quien, len(sender_idx))
    return [
        m.row_id,
        1 if m.from_me else 0,
        si,
        m.timestamp,
        m.raw_type if m.raw_type is not None else -1,
        body,
        m.key_id,
        _flags(m),
        m.media_path,
        m.latitude,
        m.longitude,
        _quote_text(m),
        _reactions_text(m),
        href,                       # 13: URL del adjunto, si se ha localizado
        maphref,                    # 14: URL del mapa local, si se ha descargado
        m.status_desc or None,      # 15: estado de entrega/lectura
        1 if m.leido else 0,        # 16: consta que se abrio
    ]


def _type_table(platform):
    """Diccionario rawType -> descripción, enviado una sola vez."""
    table = {codes.ANDROID: codes.ANDROID_MESSAGE_TYPE,
             codes.ANDROID_LEGACY: codes.ANDROID_MEDIA_WA_TYPE,
             codes.IOS: codes.IOS_ZMESSAGETYPE}.get(platform, {})
    return {str(k): v[1] for k, v in table.items()}


# ===========================================================================
#  Cabecera / estadísticas
# ===========================================================================
def _stats_html(stats, extraction, platform):
    rows = []
    rows.append(("Plataforma", codes.PLATFORM_LABEL.get(platform, platform)))
    rows.append(("Mensajes", "{:,}".format(stats["total"]).replace(",", ".")))
    rows.append(("Chats", stats["chats"]))
    rows.append(("Contactos", stats["contacts"]))
    rows.append(("Borrados", stats["deleted"]))
    rows.append(("Destacados", stats["starred"]))
    rows.append(("Con archivo adjunto", stats["with_media"]))
    if stats["first_ts"]:
        rows.append(("Primer mensaje", fmt_ts(stats["first_ts"]) + " UTC"))
    if stats["last_ts"]:
        rows.append(("Último mensaje", fmt_ts(stats["last_ts"]) + " UTC"))
    rows.append(("Informe generado",
                 datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + " UTC"))

    t1 = "".join("<tr><td>{}</td><td>{}</td></tr>".format(html.escape(str(k)),
                                                          html.escape(str(v)))
                 for k, v in rows)

    # cadena de custodia
    t2 = ""
    if extraction.source_files:
        t2 = ("<h3>Origen y verificación</h3><table>"
              "<tr><th>Archivo</th><th>Tamaño</th><th>SHA-256</th></tr>")
        for s in extraction.source_files:
            t2 += "<tr><td>{}</td><td>{:,} B</td><td class='mono'>{}</td></tr>".format(
                html.escape(s["name"]), s["size"], s["sha256"])
        t2 += "</table>"

    pills = "".join(
        '<span class="pill">{}: {}</span>'.format(
            html.escape(codes.KIND_LABEL.get(codes.Kind(k), k)), v)
        for k, v in stats["by_kind"].items())

    years = "".join('<span class="pill">{}: {}</span>'.format(y, n)
                    for y, n in stats["by_year"].items())

    return ("<h3>Resumen</h3><table>{}</table>{}"
            "<h3>Mensajes por tipo</h3>{}"
            "<h3>Mensajes por año</h3>{}").format(t1, t2, pills, years)


# Etiquetas del visor en los dos idiomas que admite whapa (-r EN|ES)
_T = {
    "ES": {"filter_chats": "Filtrar chats…", "search_chat": "Buscar en este chat (Intro)",
           "search": "Buscar", "filters": "Filtros", "print_chat": "Imprimir chat",
           "summary": "Ver resumen y verificación", "text": "Texto", "scope": "Ámbito",
           "this_chat": "Solo este chat", "all_chats": "Todos los chats",
           "sender": "Remitente", "from": "Desde", "to": "Hasta",
           "direction": "Dirección", "all": "Todas", "sent": "Enviados",
           "received": "Recibidos", "system": "Del sistema", "type": "Tipo de mensaje",
           "regex": "Expresión regular", "case": "Distinguir mayúsculas",
           "word": "Palabra completa", "only_del": "Solo borrados",
           "only_star": "Solo destacados", "only_media": "Solo con adjunto",
           "only_fwd": "Solo reenviados", "only_edit": "Solo editados",
           "only_loc": "Solo con coordenadas", "clear": "Limpiar",
           "print_res": "Imprimir resultados", "export": "Exportar CSV",
           "hint": "La búsqueda global recorre todas las páginas de datos; "
                   "en volcados grandes puede tardar unos segundos.",
           "ph_text": "contenido, pie de foto, archivo o cita",
           "ph_sender": "número o nombre", "messages": "mensajes", "chats": "chats"},
    "EN": {"filter_chats": "Filter chats…", "search_chat": "Search this chat (Enter)",
           "search": "Search", "filters": "Filters", "print_chat": "Print chat",
           "summary": "View summary and verification", "text": "Text", "scope": "Scope",
           "this_chat": "This chat only", "all_chats": "All chats",
           "sender": "Sender", "from": "From", "to": "To",
           "direction": "Direction", "all": "All", "sent": "Sent",
           "received": "Received", "system": "System", "type": "Message type",
           "regex": "Regular expression", "case": "Case sensitive",
           "word": "Whole word", "only_del": "Deleted only",
           "only_star": "Starred only", "only_media": "With attachment only",
           "only_fwd": "Forwarded only", "only_edit": "Edited only",
           "only_loc": "With coordinates only", "clear": "Clear",
           "print_res": "Print results", "export": "Export CSV",
           "hint": "Global search scans every data page; it may take a few "
                   "seconds on large dumps.",
           "ph_text": "content, caption, file name or quote",
           "ph_sender": "number or name", "messages": "messages", "chats": "chats"},
}

_SHELL = """<!DOCTYPE html>
<html lang="es"><head><meta charset="utf-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title><style>{css}</style></head><body>
<header class="top">
  <h1>{title}</h1>
  <div class="meta">{subtitle}</div>
  <div class="meta"><a href="#" onclick="showStats();return false;">{t_summary}</a></div>
</header>
<div class="layout">
  <nav class="chats">
    <div class="navsearch"><input id="navq" placeholder="{t_filter_chats}"></div>
    <div id="navlist"></div>
  </nav>
  <main>
    <div class="toolbar">
      <h2 id="chatTitle">—</h2>
      <span class="hint" id="chatSub"></span>
      <span class="grow"></span>
      <input id="q" placeholder="{t_search_chat}" size="26">
      <button onclick="searchChat()">{t_search}</button>
      <button onclick="togglePanel()" title="{t_filters}">{t_filters} ▾</button>
      <button onclick="printChat()" title="Expande el chat completo y abre el diálogo de impresión">{t_print_chat}</button>
    </div>

    <div class="panel" id="panel">
      <div class="grid">
        <div class="f" style="flex:1;min-width:230px">
          <label>{t_text}</label>
          <input type="text" id="fText" placeholder="{t_ph_text}">
        </div>
        <div class="f">
          <label>{t_scope}</label>
          <select id="fScope">
            <option value="chat">{t_this_chat}</option>
            <option value="all">{t_all_chats}</option>
          </select>
        </div>
        <div class="f">
          <label>{t_sender}</label>
          <input type="text" id="fSender" size="14" placeholder="{t_ph_sender}">
        </div>
        <div class="f"><label>{t_from}</label><input type="date" id="fFrom"></div>
        <div class="f"><label>{t_to}</label><input type="date" id="fTo"></div>
        <div class="f">
          <label>{t_direction}</label>
          <select id="fDir">
            <option value="">{t_all}</option>
            <option value="sent">{t_sent}</option>
            <option value="received">{t_received}</option>
            <option value="system">{t_system}</option>
          </select>
        </div>
        <div class="f">
          <label>{t_type}</label>
          <select id="fType"><option value="">{t_all}</option></select>
        </div>
      </div>
      <div class="chk">
        <label><input type="checkbox" id="fRegex"> {t_regex}</label>
        <label><input type="checkbox" id="fCase"> {t_case}</label>
        <label><input type="checkbox" id="fWord"> {t_word}</label>
        <label><input type="checkbox" id="fDel"> {t_only_del}</label>
        <label><input type="checkbox" id="fStar"> {t_only_star}</label>
        <label><input type="checkbox" id="fMedia"> {t_only_media}</label>
        <label><input type="checkbox" id="fFwd"> {t_only_fwd}</label>
        <label><input type="checkbox" id="fEdit"> {t_only_edit}</label>
        <label><input type="checkbox" id="fLoc"> {t_only_loc}</label>
      </div>
      <div class="acts">
        <button onclick="runSearch()" style="background:var(--accent);color:#04160f;
          border-color:var(--accent);font-weight:600">{t_search}</button>
        <button onclick="clearSearch()">{t_clear}</button>
        <button onclick="printResults()">{t_print_res}</button>
        <button onclick="exportCSV()">{t_export}</button>
        <span class="hint">{t_hint}</span>
      </div>
    </div>

    <div id="scroller"></div>
    <div class="printview" id="printview"></div>
  </main>
</div>
<div id="printWarn"><div class="box">
  <h3>Chat muy largo</h3><p id="pwText"></p>
  <p><button onclick="doPrint()">Imprimir de todas formas</button>
     <button onclick="document.getElementById('printWarn').style.display='none'">Cancelar</button></p>
</div></div>
<div id="statsData" style="display:none">{stats}</div>
<script>{js}</script>
<script>
function showStats(){{
  document.getElementById('scroller').innerHTML =
    '<div class="stats">' + document.getElementById('statsData').innerHTML + '</div>';
}}
</script>
<script src="{index_src}"></script>
{inline_data}
<script>boot();</script>
</body></html>"""


# ===========================================================================
#  Generación
# ===========================================================================
def _tvars(lang):
    """Traducciones del shell como variables t_<clave> para format()."""
    return {"t_" + k: v for k, v in _T.get(lang, _T["ES"]).items()}


def build_report(extraction, out_path, title="Informe forense WhatsApp",
                 single_file=False, page_size=PAGE_SIZE, lang="ES", flt=None,
                 media_root=None, copy_media=False, maps=False):
    """Genera el informe interactivo.

    out_path : carpeta, o archivo .html si single_file
    lang     : 'ES' o 'EN' (equivale al -r de whapa.py)
    flt      : Filter opcional; si se indica, el informe contiene solo los
               mensajes que lo cumplen, igual que el informe imprimible.
    media_root : carpeta WhatsApp copiada del terminal. Si se indica, los
               adjuntos se localizan y quedan enlazados en el informe: las
               imagenes se ven y los audios y videos se reproducen dentro.
    copy_media : ademas de enlazarlos, copia los adjuntos dentro del informe
               para poder entregarlo como un unico paquete.
    """
    lang = lang if lang in _T else "ES"
    chats = extraction.chats()
    if flt is not None and not flt.is_empty():
        recortados = []
        for c in chats:
            msgs = [m for m in c.messages if flt.match(m, c.label)]
            if msgs:
                recortados.append(Chat(chat_id=c.chat_id, name=c.name,
                                       is_group=c.is_group, messages=msgs))
        chats = recortados
    stats = extraction.summary()
    platform = extraction.platform

    base_dir = out_path if not single_file else os.path.dirname(
        os.path.abspath(out_path)) or "."
    resolver = MediaResolver(media_root, "media" if copy_media else None)
    mapas = MapDownloader(maps)
    if media_root or maps:
        os.makedirs(base_dir, exist_ok=True)

    chat_meta, pages_data = [], []      # pages_data: (ci, pi, json)
    for ci, c in enumerate(chats):
        sender_idx = {}
        rows = [_serialize(m, sender_idx,
                           resolver.resolve(m.media_path, base_dir)
                           if (media_root and m.media_path) else None,
                           mapas.fetch(m.latitude, m.longitude, base_dir))
                for m in c.messages]
        n_pages = max(1, (len(rows) + page_size - 1) // page_size)
        for pi in range(n_pages):
            chunk = rows[pi * page_size:(pi + 1) * page_size]
            pages_data.append((ci, pi, json.dumps(chunk, ensure_ascii=False,
                                                  separators=(",", ":"))))
        senders = [None] * len(sender_idx)
        for name, idx in sender_idx.items():
            senders[idx] = name
        chat_meta.append({
            "name": c.label, "group": c.is_group, "n": len(c.messages),
            "pages": n_pages, "senders": senders,
            "est": min(900, 60 * min(len(c.messages), 15)),
            "last": fmt_ts(c.last_ts)[:10] if c.last_ts else "",
        })

    incluidos = sum(len(c.messages) for c in chats)
    stats = dict(stats)
    stats["shown"] = incluidos
    stats["filter"] = flt.describe() if (flt is not None and not flt.is_empty()) else None

    index_js = ("WHAPA.meta={meta};WHAPA.types={types};WHAPA.chats={chats};"
                "WHAPA.single={single};").format(
        meta=json.dumps({"platform": platform, "title": title}, ensure_ascii=False),
        types=json.dumps(_type_table(platform), ensure_ascii=False),
        chats=json.dumps(chat_meta, ensure_ascii=False, separators=(",", ":")),
        single="true" if single_file else "false")

    stats_html = _stats_html(stats, extraction, platform)
    subtitle = "{} · {} {} · {} {}".format(
        codes.PLATFORM_LABEL.get(platform, platform), incluidos,
        _T[lang]["messages"], len(chats), _T[lang]["chats"])
    if stats.get("filter"):
        subtitle += " · " + " · ".join("{}: {}".format(k, v) for k, v in stats["filter"])

    if single_file:
        inline = ["<script>" + index_js + "</script>"]
        for ci, pi, payload in pages_data:
            inline.append("<script>WHAPA.recv({},{},{});</script>".format(ci, pi, payload))
        htmlout = _SHELL.format(
            title=html.escape(title), css=CSS, js=JS, stats=stats_html,
            subtitle=html.escape(subtitle), index_src="",
            inline_data="\n".join(inline), **_tvars(lang))
        htmlout = htmlout.replace('<script src=""></script>', "")
        with open(out_path, "w", encoding="utf-8") as fh:
            fh.write(htmlout)
        return {"mode": "single", "path": out_path,
                "size": os.path.getsize(out_path), "pages": len(pages_data),
                "media_found": resolver.found, "media_missing": resolver.missing,
                "maps_ok": mapas.ok, "maps_failed": mapas.failed}

    # --- modo carpeta ---
    os.makedirs(out_path, exist_ok=True)
    data_dir = os.path.join(out_path, "data")
    os.makedirs(data_dir, exist_ok=True)

    with open(os.path.join(data_dir, "index.js"), "w", encoding="utf-8") as fh:
        fh.write(index_js)
    for ci, pi, payload in pages_data:
        fn = os.path.join(data_dir, "c{:04d}_p{:04d}.js".format(ci, pi))
        with open(fn, "w", encoding="utf-8") as fh:
            fh.write("WHAPA.recv({},{},{});".format(ci, pi, payload))

    index_path = os.path.join(out_path, "index.html")
    with open(index_path, "w", encoding="utf-8") as fh:
        fh.write(_SHELL.format(
            title=html.escape(title), css=CSS, js=JS, stats=stats_html,
            subtitle=html.escape(subtitle), index_src="data/index.js",
            inline_data="", **_tvars(lang)))

    total = sum(os.path.getsize(os.path.join(data_dir, f))
                for f in os.listdir(data_dir))
    return {"mode": "folder", "path": index_path,
            "shell_size": os.path.getsize(index_path),
            "data_size": total, "pages": len(pages_data),
            "media_found": resolver.found, "media_missing": resolver.missing,
            "maps_ok": mapas.ok, "maps_failed": mapas.failed}

# ========================================================================
#  INFORME IMPRIMIBLE
# ========================================================================




PRINT_CSS = """
@page { size: A4; margin: 14mm 12mm 16mm 12mm; }
body{font-family:'Segoe UI',Helvetica,Arial,sans-serif;font-size:10.5pt;
color:#000;background:#fff;margin:0;padding:18px}
h1{font-size:17pt;margin:0 0 4px}
h2{font-size:13pt;margin:22px 0 6px;padding-bottom:3px;border-bottom:1.5px solid #000;
page-break-after:avoid}
h3{font-size:11pt;margin:14px 0 5px;page-break-after:avoid}
.cover{page-break-after:always}
.meta{color:#444;font-size:9.5pt;margin-bottom:2px}
table{border-collapse:collapse;width:100%;font-size:9pt}
th,td{border:1px solid #999;padding:3px 5px;vertical-align:top;text-align:left}
th{background:#e8e8e8;font-weight:600}
thead{display:table-header-group}
tr{page-break-inside:avoid}
td.n{width:42px;text-align:right;color:#555;font-variant-numeric:tabular-nums}
td.f{width:112px;white-space:nowrap;font-variant-numeric:tabular-nums}
td.d{width:56px;text-align:center}
td.r{width:118px;word-break:break-all}
td.t{width:118px}
td.c{word-wrap:break-word;overflow-wrap:anywhere}
.out{background:#f2f7f4}
.sys{background:#f4f4f4;font-style:italic;color:#333}
.del{background:#fdeeee;color:#a00;font-style:italic}
.q{border-left:2px solid #666;padding-left:5px;color:#444;font-size:8.5pt;
margin-bottom:2px;display:block}
.x{color:#444;font-size:8.5pt;display:block;margin-top:2px}
.k{font-family:ui-monospace,Consolas,monospace;font-size:7.5pt;color:#555;
word-break:break-all;display:block}
.sum td,.sum th{font-size:9.5pt}
.thumb{max-width:150px;max-height:150px;display:block;margin:3px 0;border:1px solid #bbb}
.pill{display:inline-block;border:1px solid #999;border-radius:9px;
padding:1px 8px;margin:2px 3px 0 0;font-size:8.5pt}
.note{border:1px solid #999;background:#f7f7f7;padding:8px 10px;margin:12px 0;
font-size:9pt}
@media print{ body{padding:0} .noprint{display:none} }
"""


def _dirn(m):
    if m.kind is codes.Kind.SYSTEM or m.system_action:
        return "sistema"
    return "enviado" if m.from_me else "recibido"


def _remitente(m):
    """Remitente para la tabla: nombre y numero, o solo lo que haya."""
    if m.from_me:
        return "—"
    if m.sender_name and m.sender and m.sender_name != m.sender:
        return "{} ({})".format(m.sender_name, m.sender)
    return m.sender or ""


def _row_class(m):
    if m.is_deleted:
        return "del"
    if m.kind is codes.Kind.SYSTEM or m.system_action:
        return "sys"
    return "out" if m.from_me else ""


def _content_cell(m, show_ids, href=None):
    parts = []
    if m.quote:
        q = m.quote
        who = (q.sender + ": ") if q.sender else ""
        parts.append('<span class="q">↩ {}{}</span>'.format(
            html.escape(who), html.escape((q.text or q.type_desc or "")[:300])))
    body = m.text or m.media_caption or m.system_action or ""
    if not body:
        body = "[{}]".format(m.type_desc)
    parts.append(html.escape(body))
    if m.media_path:
        if href and media_kind_from_name(href) == "image":
            parts.append('<img class="thumb" src="{}" alt="">'.format(html.escape(href)))
        elif href:
            parts.append('<span class="x">Adjunto: <a href="{}">{}</a></span>'.format(
                html.escape(href), html.escape(os.path.basename(href))))
        parts.append('<span class="x">Ruta en la base: {}{}{}</span>'.format(
            html.escape(str(m.media_path)),
            " ({} bytes)".format(m.media_size) if m.media_size else "",
            "" if href else " [archivo no localizado]"))
    if m.latitude is not None and m.longitude is not None:
        parts.append('<span class="x"><b>Coordenadas:</b> {}, {} &nbsp;'
                     '<a href="https://www.openstreetmap.org/?mlat={}&amp;mlon={}'
                     '#map=17/{}/{}">OpenStreetMap</a></span>'.format(
                         m.latitude, m.longitude, m.latitude, m.longitude,
                         m.latitude, m.longitude))
    if m.reactions:
        parts.append('<span class="x">Reacciones: {}</span>'.format(
            html.escape(" ".join(r.emoji for r in m.reactions))))
    if m.call_duration is not None:
        parts.append('<span class="x">Duración: {} s{}{}</span>'.format(
            m.call_duration, " · vídeo" if m.call_video else "",
            " · " + m.call_result if m.call_result else ""))
    if m.status_desc:
        extra = ""
        if m.delivered_to or m.read_by:
            extra = " (entregado a {}, leido por {})".format(m.delivered_to, m.read_by)
        parts.append('<span class="x"><b>Estado:</b> {}{}</span>'.format(
            html.escape(m.status_desc), extra))
    marks = []
    if m.starred:
        marks.append("destacado")
    if m.is_forwarded:
        marks.append("reenviado")
    if m.edited:
        marks.append("editado")
    if marks:
        parts.append('<span class="x">[{}]</span>'.format(", ".join(marks)))
    if show_ids and m.key_id:
        dev = infer_device(m.key_id)
        parts.append('<span class="k">ID: {}{}</span>'.format(
            html.escape(str(m.key_id)), " · " + dev if dev else ""))
    return "".join(parts)


def _criteria_block(flt):
    """Bloque de criterios aplicados. Sin esto el documento no es reproducible."""
    if flt is None or flt.is_empty():
        return ("<h3>Criterios de selección</h3>"
                "<table class='sum'><tr><th>Alcance</th>"
                "<td>Todos los mensajes de la extracción, sin filtrar</td></tr>"
                "</table>")
    filas = "".join("<tr><th>{}</th><td>{}</td></tr>".format(
        html.escape(str(k)), html.escape(str(v))) for k, v in flt.describe())
    return ("<h3>Criterios de selección</h3><table class='sum'>{}</table>"
            "<div class='note'>Este documento contiene <b>únicamente</b> los "
            "mensajes que cumplen los criterios anteriores. Aplicando esos mismos "
            "criterios sobre el origen verificado más abajo se obtiene el mismo "
            "conjunto de mensajes.</div>").format(filas)


def _cover(extraction, stats, title, case_ref, examiner, flt=None, shown=None):
    rows = [("Plataforma", codes.PLATFORM_LABEL.get(extraction.platform, extraction.platform))]
    if case_ref:
        rows.insert(0, ("Referencia", case_ref))
    if examiner:
        rows.append(("Instructor / analista", examiner))
    rows += [
        ("Mensajes analizados", "{:,}".format(stats["total"]).replace(",", ".")),
        ("Chats", stats["chats"]),
        ("Contactos", stats["contacts"]),
        ("Mensajes borrados", stats["deleted"]),
        ("Mensajes destacados", stats["starred"]),
        ("Mensajes con adjunto", stats["with_media"]),
    ]
    if stats["first_ts"]:
        rows.append(("Primer mensaje", fmt_ts(stats["first_ts"]) + " UTC"))
    if stats["last_ts"]:
        rows.append(("Último mensaje", fmt_ts(stats["last_ts"]) + " UTC"))
    rows.append(("Fecha de emisión",
                 datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d %H:%M:%S") + " UTC"))

    t = "".join("<tr><th>{}</th><td>{}</td></tr>".format(
        html.escape(str(k)), html.escape(str(v))) for k, v in rows)

    custody = ""
    if extraction.source_files:
        custody = ("<h3>Verificación de los orígenes</h3><table class='sum'>"
                   "<tr><th>Archivo</th><th>Tamaño</th><th>SHA-256</th></tr>")
        for s in extraction.source_files:
            custody += ("<tr><td>{}</td><td>{:,} B</td>"
                        "<td class='k'>{}</td></tr>").format(
                html.escape(s["name"]), s["size"], s["sha256"])
        custody += "</table>"

    pills = "".join('<span class="pill">{}: {}</span>'.format(
        html.escape(codes.KIND_LABEL.get(codes.Kind(k), k)), v)
        for k, v in stats["by_kind"].items())

    sel = ""
    if shown is not None:
        pct = (100.0 * shown / stats["total"]) if stats["total"] else 0
        sel = ("<h3>Alcance del documento</h3><table class='sum'>"
               "<tr><th>Mensajes en la extracción</th><td>{tot}</td></tr>"
               "<tr><th>Mensajes en este documento</th><td>{sh} ({pct:.1f} %)</td></tr>"
               "</table>").format(
            tot="{:,}".format(stats["total"]).replace(",", "."),
            sh="{:,}".format(shown).replace(",", "."), pct=pct)

    return ("<div class='cover'><h1>{}</h1>"
            "<div class='meta'>Documento generado para impresión</div>"
            "<h3>Datos del análisis</h3><table class='sum'>{}</table>"
            "{}{}{}"
            "<h3>Distribución por tipo de mensaje (extracción completa)</h3>{}"
            "<div class='note'>Todas las fechas se expresan en UTC. La columna "
            "«N.º» es una numeración correlativa de este documento, no el "
            "identificador interno de la base de datos.</div></div>").format(
        html.escape(title), t, _criteria_block(flt), sel, custody, pills)


def build_printable(extraction, out_path, title="Informe forense WhatsApp",
                    case_ref=None, examiner=None, flt=None, show_ids=True,
                    max_messages=None, chat_filter=None, date_from=None,
                    date_to=None, kinds=None, media_root=None, copy_media=False):
    """Genera un HTML estático listo para imprimir o convertir a PDF.

    flt : whapa2.query.Filter con los criterios. Los parámetros sueltos
          (chat_filter, date_from, date_to, kinds) se mantienen por
          compatibilidad y se fusionan en el filtro si no se pasa `flt`.
    """
    if flt is None:
        flt = Filter(chat=chat_filter, date_from=date_from, date_to=date_to,
                     kinds=set(kinds) if kinds else None)

    base_dir = os.path.dirname(os.path.abspath(out_path)) or "."
    resolver = MediaResolver(media_root, "media" if copy_media else None)

    stats = extraction.summary()
    chats = extraction.chats()
    if flt.chat:
        f = flt.chat.lower()
        chats = [c for c in chats
                 if f in (c.label or "").lower() or f in (c.chat_id or "").lower()]

    # Primero se selecciona, para poder anunciar el alcance en la portada
    seleccion = []
    total_sel = 0
    for c in chats:
        msgs = [m for m in c.messages if flt.match(m, c.label)]
        if msgs:
            seleccion.append((c, msgs))
            total_sel += len(msgs)

    shown = min(total_sel, max_messages) if max_messages else total_sel
    body = [_cover(extraction, stats, title, case_ref, examiner, flt, shown)]

    n = 0
    truncated = False
    for c, msgs in seleccion:
        if truncated:
            break
        ts = [m.timestamp for m in msgs if m.timestamp]
        body.append("<h2>{}{}</h2>".format(
            html.escape(c.label), " · grupo" if c.is_group else ""))
        body.append("<div class='meta'>{} · {} mensajes seleccionados · "
                    "rango {} a {} UTC</div>".format(
                        html.escape(c.chat_id or ""), len(msgs),
                        fmt_ts(min(ts)) if ts else "—",
                        fmt_ts(max(ts)) if ts else "—"))
        body.append("<table class='msgs'><thead><tr><th class='n'>N.º</th>"
                    "<th class='f'>Fecha (UTC)</th>"
                    "<th class='d'>Dir.</th><th class='r'>Remitente</th>"
                    "<th class='t'>Tipo (código)</th><th class='c'>Contenido</th>"
                    "</tr></thead><tbody>")
        for m in msgs:
            if max_messages and n >= max_messages:
                truncated = True
                break
            n += 1
            body.append(
                "<tr class='{cls}'><td class='n'>{n}</td><td class='f'>{f}</td>"
                "<td class='d'>{d}</td><td class='r'>{r}</td>"
                "<td class='t'>{t} ({rt})</td><td class='c'>{c}</td></tr>".format(
                    cls=_row_class(m), n=n, f=fmt_ts(m.timestamp),
                    d=_dirn(m)[:3], r=html.escape(_remitente(m)),
                    t=html.escape(m.type_desc),
                    rt=m.raw_type if m.raw_type is not None else "?",
                    c=_content_cell(m, show_ids,
                                     resolver.resolve(m.media_path, base_dir)
                                     if (media_root and m.media_path) else None)))
        body.append("</tbody></table>")
        if truncated:
            body.append("<div class='note'><b>Documento truncado</b> al alcanzar "
                        "el límite de {} mensajes. Afina los criterios o eleva "
                        "--max-messages.</div>".format(max_messages))

    if not seleccion:
        body.append("<div class='note'><b>Ningún mensaje cumple los criterios "
                    "indicados.</b></div>")

    doc = ("<!DOCTYPE html><html lang='es'><head><meta charset='utf-8'>"
           "<title>{t}</title><style>{css}</style></head><body>{b}</body></html>").format(
        t=html.escape(title), css=PRINT_CSS, b="".join(body))

    with open(out_path, "w", encoding="utf-8") as fh:
        fh.write(doc)
    return {"path": out_path, "messages": n, "chats": len(seleccion),
            "selected": total_sel, "truncated": truncated,
            "media_found": resolver.found, "media_missing": resolver.missing}


# ===========================================================================
#  RESOLUCION DE ARCHIVOS ADJUNTOS
# ===========================================================================
#  La base de datos guarda RUTAS, no archivos. Si el usuario ha copiado la
#  carpeta WhatsApp del terminal, aqui se localiza cada archivo y se enlaza
#  desde el informe, para que las imagenes se vean y los audios y videos se
#  reproduzcan sin salir del HTML, como hacia la version anterior.
#
#  Las rutas guardadas varian mucho:
#     Android antiguo : /storage/emulated/0/WhatsApp/Media/WhatsApp Images/IMG-x.jpg
#     Android actual  : Media/WhatsApp Images/IMG-x.jpg
#     iOS             : Message/Media/<jid>/7/A/AUDIO-x.opus
#  Por eso se prueba primero por ruta relativa y, si falla, por nombre de
#  archivo contra un indice de toda la carpeta.

MEDIA_EXT = {
    "image": {".jpg", ".jpeg", ".png", ".webp", ".gif", ".bmp"},
    "audio": {".opus", ".ogg", ".mp3", ".m4a", ".aac", ".wav", ".amr"},
    "video": {".mp4", ".3gp", ".mov", ".mkv", ".avi", ".webm"},
}


def media_kind_from_name(name):
    ext = os.path.splitext(name or "")[1].lower()
    for k, exts in MEDIA_EXT.items():
        if ext in exts:
            return k
    return "file"


class MediaResolver:
    """Localiza los adjuntos dentro de la carpeta que aporte el usuario."""

    def __init__(self, root, copy_to=None):
        self.root = os.path.abspath(root) if root else None
        self.copy_to = copy_to
        self.index = {}
        self.found = 0
        self.missing = 0
        self._copied = {}
        if self.root and os.path.isdir(self.root):
            self._build_index()

    def _build_index(self):
        """Indice por nombre de archivo de todo lo que cuelga de la carpeta."""
        for dirpath, _dirs, files in os.walk(self.root):
            for f in files:
                self.index.setdefault(f.lower(), os.path.join(dirpath, f))

    def _locate(self, stored_path):
        if not stored_path or not self.root:
            return None
        p = str(stored_path).replace("\\", "/")
        # 1) por ruta relativa, cortando en Media/ o Message/
        for marca in ("/Media/", "Media/", "/Message/", "Message/"):
            i = p.find(marca)
            if i >= 0:
                rel = p[i:].lstrip("/")
                for base in (self.root, os.path.dirname(self.root)):
                    cand = os.path.join(base, *rel.split("/"))
                    if os.path.isfile(cand):
                        return cand
                break
        # 2) tal cual, por si es una ruta ya valida en este equipo
        if os.path.isfile(p):
            return p
        # 3) por nombre de archivo
        return self.index.get(os.path.basename(p).lower())

    def resolve(self, stored_path, out_dir):
        """Devuelve la URL relativa al informe, o None si no se localiza.

        Con copy_to, el archivo se copia dentro del informe para que sea
        autocontenido y se pueda entregar en un solo paquete.
        """
        real = self._locate(stored_path)
        if not real:
            self.missing += 1
            return None
        self.found += 1
        if self.copy_to:
            destino_dir = os.path.join(out_dir, self.copy_to)
            nombre = os.path.basename(real)
            destino = os.path.join(destino_dir, nombre)
            if real not in self._copied:
                os.makedirs(destino_dir, exist_ok=True)
                # evitar pisar archivos distintos con el mismo nombre
                n = 1
                base, ext = os.path.splitext(nombre)
                while os.path.exists(destino) and self._copied.get(destino) != real:
                    destino = os.path.join(destino_dir, "{}_{}{}".format(base, n, ext))
                    n += 1
                try:
                    import shutil
                    shutil.copy2(real, destino)
                    self._copied[real] = destino
                except OSError:
                    self.found -= 1
                    self.missing += 1
                    return None
            else:
                destino = self._copied[real]
            return "{}/{}".format(self.copy_to, os.path.basename(destino))
        # enlace relativo desde el informe hasta el archivo original
        try:
            return os.path.relpath(real, out_dir).replace("\\", "/")
        except ValueError:   # unidades distintas en Windows
            return "file:///" + real.replace("\\", "/")


# ===========================================================================
#  MAPAS Y EXPORTACION DE UBICACIONES
# ===========================================================================
#  Un informe forense no deberia pedirle un mapa a un servidor ajeno cada vez
#  que alguien lo abre: filtraria las coordenadas del caso a un tercero y
#  dejaria de funcionar sin conexion. Por eso el mapa NO se enlaza en remoto.
#
#  Con la opcion -gm se descarga una vez, al generar el informe, y se guarda
#  dentro de la carpeta. A partir de ahi el informe es autonomo.

STATIC_MAP_URL = ("https://staticmap.openstreetmap.de/staticmap.php"
                  "?center={lat},{lon}&zoom={zoom}&size={size}"
                  "&markers={lat},{lon},red-pushpin")


class MapDownloader:
    """Descarga mapas estaticos y los guarda dentro del informe."""

    def __init__(self, enabled=False, zoom=16, size="300x180", subdir="maps"):
        self.enabled = enabled
        self.zoom = zoom
        self.size = size
        self.subdir = subdir
        self.cache = {}
        self.ok = 0
        self.failed = 0

    def fetch(self, lat, lon, out_dir):
        """Devuelve la ruta relativa del mapa, o None si no se pudo obtener."""
        if not self.enabled or lat is None or lon is None:
            return None
        clave = "{:.5f},{:.5f}".format(float(lat), float(lon))
        if clave in self.cache:
            return self.cache[clave]
        nombre = "map_{}.png".format(clave.replace(",", "_").replace("-", "m")
                                     .replace(".", "p"))
        destino_dir = os.path.join(out_dir, self.subdir)
        destino = os.path.join(destino_dir, nombre)
        rel = "{}/{}".format(self.subdir, nombre)
        if os.path.isfile(destino):
            self.cache[clave] = rel
            return rel
        try:
            import urllib.request
            os.makedirs(destino_dir, exist_ok=True)
            url = STATIC_MAP_URL.format(lat=lat, lon=lon, zoom=self.zoom,
                                        size=self.size)
            req = urllib.request.Request(url, headers={"User-Agent": "whapa/2.00"})
            with urllib.request.urlopen(req, timeout=15) as r:
                datos = r.read()
            if not datos.startswith(b"\x89PNG") and not datos.startswith(b"\xff\xd8"):
                raise ValueError("la respuesta no es una imagen")
            with open(destino, "wb") as fh:
                fh.write(datos)
            self.ok += 1
            self.cache[clave] = rel
            return rel
        except Exception:
            self.failed += 1
            self.cache[clave] = None
            return None


def export_kml(hits_or_messages, path, titulo="Ubicaciones WhatsApp"):
    """Exporta las ubicaciones a KML, para abrirlas en Google Earth o QGIS.

    Acepta una lista de Hit (resultado de search) o de Message.
    Devuelve el numero de puntos exportados.
    """
    puntos = []
    for x in hits_or_messages:
        m = getattr(x, "message", x)
        chat = getattr(x, "chat_label", "") or (m.chat_id or "")
        if m.latitude is None or m.longitude is None:
            continue
        puntos.append((chat, m))

    def esc(t):
        return html.escape(str(t or ""))

    partes = ['<?xml version="1.0" encoding="UTF-8"?>',
              '<kml xmlns="http://www.opengis.net/kml/2.2"><Document>',
              '<name>{}</name>'.format(esc(titulo))]
    for chat, m in puntos:
        cuando = fmt_ts(m.timestamp)
        desc = ("Chat: {}<br/>Fecha (UTC): {}<br/>Direccion: {}<br/>"
                "Tipo: {} ({})<br/>Remitente: {}<br/>Texto: {}<br/>"
                "ID: {}").format(
            esc(chat), esc(cuando),
            "enviado" if m.from_me else "recibido",
            esc(m.type_desc), m.raw_type if m.raw_type is not None else "?",
            esc(m.sender or ""), esc(m.text or m.media_caption or ""),
            esc(m.key_id or ""))
        partes.append(
            "<Placemark><name>{n}</name><description><![CDATA[{d}]]></description>"
            "{t}<Point><coordinates>{lon},{lat},0</coordinates></Point></Placemark>".format(
                n=esc("{} - {}".format(cuando, chat)), d=desc,
                t="<TimeStamp><when>{}Z</when></TimeStamp>".format(
                    cuando.replace(" ", "T")) if cuando else "",
                lon=m.longitude, lat=m.latitude))
    partes.append("</Document></kml>")

    with open(path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(partes))
    return len(puntos)

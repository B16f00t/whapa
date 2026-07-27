#!/usr/bin/python3
# -*- coding: utf-8 -*-
"""
whapa-gui.py - Interfaz grafica de WhaPa (CustomTkinter)

COMETIDO DE ESTE ARCHIVO
    Ser un lanzador de las herramientas de libs/, no una reimplementacion de
    ellas. Cada pestana corresponde a un archivo y compone sus argumentos:

        WhaPa      -> libs/whapa.py      analisis de la base de datos
        WhaCipher  -> libs/whacipher.py  descifrado y cifrado
        WhaMerge   -> libs/whamerge.py   fusion de bases
        WhaGoDri   -> libs/whagodri.py   descarga desde Google Drive
        WhaChat    -> libs/whachat.py    analisis de chats exportados
        WhaCloud   -> libs/whacloud.py   descarga desde iCloud

QUE CAMBIA RESPECTO A LA VERSION ANTERIOR
    * Reescrita con CustomTkinter (tema oscuro), compatible con Python 3.11+.
    * Las ordenes se lanzan con subprocess y una LISTA de argumentos, no con
      os.system() sobre una cadena montada a mano: aquello permitia inyeccion
      de ordenes a traves de los nombres de archivo.
    * La ejecucion corre en un hilo aparte y la salida se vuelca en directo en
      el panel inferior, de modo que la ventana no se congela.
    * Todo acceso a los widgets ocurre en el hilo principal (Tkinter no es
      seguro entre hilos); el hilo de trabajo solo escribe en una cola.

Requisitos:  pip install customtkinter

** Author: Ivan Moreno a.k.a B16f00t
** Github: https://github.com/B16f00t
"""

import os
import sys
import queue
import shlex
import threading
import subprocess
import webbrowser
from configparser import ConfigParser

try:
    import customtkinter as ctk
    from tkinter import filedialog, messagebox
except ImportError:
    sys.exit("Falta customtkinter.  Instalalo con:  pip install customtkinter")

APP_DIR = os.path.dirname(os.path.abspath(__file__))
LIBS = os.path.join(APP_DIR, "libs")
version = "2.00"

ACCENT, ACCENT_HOVER = "#00a884", "#01976e"
BG, PANEL, FIELD = "#0b141a", "#111b21", "#202c33"
MUTED, TEXT, ERROR = "#8696a0", "#e9edef", "#f15c6d"


# ===========================================================================
#  Idiomas de la interfaz
# ===========================================================================
LANG = {
 "ES": {
  "subtitle": "Analisis forense de WhatsApp - Android e iOS",
  "output": "Salida", "clear": "Limpiar", "browse": "Examinar",
  "deps": "Instalar dependencias", "settings": "Configuracion",
  "readme": "Manual", "about": "Acerca de", "lang": "English",
  "run": "Ejecutar", "hint_start": "Elige una pestana, completa los campos y pulsa el boton de accion.",
  "db": "Base de datos", "db_dec": "Base descifrada", "contacts": "Contactos (opcional)",
  "outdir": "Carpeta de salida", "wafolder": "Carpeta WhatsApp (opcional)",
  "copymedia": "Copiar los adjuntos dentro del informe (entregable en un solo paquete)",
  "mode": "Modo", "platform": "Plataforma", "auto": "Autodetectar",
  "m_msg": "Mensajes", "m_status": "Info: estados", "m_calls": "Info: llamadas",
  "m_chats": "Info: chats activos", "m_extract": "Extraer adjuntos", "m_carving": "Carving",
  "recipients": "Destinatarios", "scope": "Alcance", "all": "Todos", "user": "Usuario",
  "group": "Grupo", "byuser": "Mensajes de un numero", "broadcast": "Difusion",
  "target": "Numero o grupo", "filters": "Filtros", "text": "Texto",
  "sender": "Remitente", "from": "Desde", "to": "Hasta", "rawtypes": "Codigos nativos",
  "direction": "Direccion", "d_all": "Todas", "d_sent": "Enviados",
  "d_recv": "Recibidos", "d_sys": "Del sistema",
  "searchopts": "OPCIONES DE BUSQUEDA", "types": "TIPOS DE MENSAJE (si no marcas ninguno, se incluyen todos)",
  "outsec": "Salida", "report": "Informe interactivo", "none": "Ninguno",
  "print": "Informe imprimible", "csv": "Exportar CSV", "kml": "Exportar ubicaciones a KML",
  "maps": "Descargar mapas (necesita internet)", "single": "Informe en un solo archivo",
  "cipher_sec": "Descifrado y cifrado de bases de datos", "action": "Accion",
  "decrypt": "Descifrar", "encrypt": "Cifrar (crypt15)", "input": "Archivo de entrada",
  "isdir": "La entrada es un directorio (solo descifrado)", "key": "Clave",
  "keyhint": "La clave puede ser el archivo .key, encrypted_backup.key o los 64 caracteres hexadecimales de la clave raiz.",
  "outfile": "Salida", "merge_sec": "Fusion de bases de datos",
  "mergefolder": "Carpeta con las bases", "mergeout": "Base resultante",
  "gd_sec": "Google Drive", "gd_cred": "Las credenciales se leen de cfg/settings.cfg, seccion [google-auth].",
  "gd_info": "Informacion de copias", "gd_list": "Listar todo", "gd_listwa": "Listar copias de WhatsApp",
  "gd_pull": "Descargar un archivo", "gd_sync": "Sincronizar todo", "gd_img": "Solo imagenes",
  "gd_vid": "Solo videos", "gd_aud": "Solo audios", "gd_doc": "Solo documentos", "gd_db": "Solo bases",
  "remotefile": "Archivo a descargar", "threads": "Hilos",
  "noparallel": "Sin descargas en paralelo", "dryrun": "Simulacion (no descarga)",
  "chat_sec": "Chat exportado desde la aplicacion", "chatfile": "Archivo del chat",
  "system": "Sistema", "chatuser": "Usuario destinatario", "datemask": "Mascara de fecha",
  "onlypart": "Solo listar participantes", "ic_sec": "iCloud",
  "chatmedia": "Carpeta con los adjuntos exportados",
  "copymedia_short": "Copiar adjuntos al informe", "regex": "Regex",
  "ic_cred": "Las credenciales se leen de cfg/settings.cfg, seccion [icloud-auth].",
  "ic_list": "Listar", "ic_sync": "Sincronizar todo", "ic_img": "Solo imagenes",
  "ic_vid": "Solo videos y audios",
  "cfg_title": "Configuracion", "cfg_report": "Datos del informe",
  "cfg_google": "Google Drive", "cfg_icloud": "iCloud", "cfg_save": "Guardar",
  "cfg_cancel": "Cancelar", "cfg_saved": "Configuracion guardada en cfg/settings.cfg",
  "deps_title": "Instalar dependencias",
  "deps_q": "Se van a instalar las dependencias de doc/requirements.txt.\n\nRequiere conexion a internet y puede tardar un rato.\n\n Continuar?",
  "missing": "Faltan estas dependencias", "allok": "Todas las dependencias estan instaladas.",
  "ph_db": "msgstore.db (Android)  /  ChatStorage.sqlite (iOS)",
  "ph_wa": "wa.db (Android)  /  ContactsV2.sqlite (iOS)  -  da los nombres",
  "ph_enc": "msgstore.db.crypt15  /  .crypt14  /  .crypt12",
  "ph_key": "archivo key  /  encrypted_backup.key  /  64 caracteres hex",
  "ph_out": "carpeta donde se guardara el informe",
  "ph_outfile": "msgstore.db  (archivo que se generara)",
  "ph_media": "carpeta WhatsApp copiada del telefono (la que contiene Media)",
  "ph_chat": "Chat de WhatsApp con <nombre>.txt",
  "ph_chatmedia": "por defecto, la misma carpeta que el .txt",
  "ph_mergedir": "carpeta con varios msgstore.db",
  "ph_mergeout": "msgstore_merge.db  (archivo que se generara)",
  "f_read": "Leidos", "f_unread": "Sin confirmar lectura",
  "ph_case": "Diligencias 1234/2026  -  saldra en la portada",
  "ph_examiner": "quien firma el analisis",
  "warn_data": "Faltan datos", "warn_db": "Elige una base de datos.",
  "warn_in": "Entrada, clave y salida son obligatorias.",
  "warn_folder": "Elige la carpeta con las bases.", "warn_chat": "Elige el archivo del chat.",
  "warn_remote": "Indica el archivo a descargar.",
 },
 "EN": {
  "subtitle": "WhatsApp forensics - Android and iOS",
  "output": "Output", "clear": "Clear", "browse": "Browse",
  "deps": "Install requirements", "settings": "Settings",
  "readme": "Manual", "about": "About", "lang": "Espanol",
  "run": "Run", "hint_start": "Pick a tab, fill in the fields and press the action button.",
  "db": "Database", "db_dec": "Decrypted database", "contacts": "Contacts (optional)",
  "outdir": "Output folder", "wafolder": "WhatsApp folder (optional)",
  "copymedia": "Copy attachments into the report (single deliverable package)",
  "mode": "Mode", "platform": "Platform", "auto": "Autodetect",
  "m_msg": "Messages", "m_status": "Info: status", "m_calls": "Info: calls",
  "m_chats": "Info: active chats", "m_extract": "Extract attachments", "m_carving": "Carving",
  "recipients": "Recipients", "scope": "Scope", "all": "All", "user": "User",
  "group": "Group", "byuser": "Messages from a number", "broadcast": "Broadcast",
  "target": "Number or group", "filters": "Filters", "text": "Text",
  "sender": "Sender", "from": "From", "to": "To", "rawtypes": "Native type codes",
  "direction": "Direction", "d_all": "All", "d_sent": "Sent",
  "d_recv": "Received", "d_sys": "System",
  "searchopts": "SEARCH OPTIONS", "types": "MESSAGE TYPES (leave all unticked to include every type)",
  "outsec": "Output", "report": "Interactive report", "none": "None",
  "print": "Printable report", "csv": "Export CSV", "kml": "Export locations to KML",
  "maps": "Download maps (needs internet)", "single": "Single file report",
  "cipher_sec": "Database decryption and encryption", "action": "Action",
  "decrypt": "Decrypt", "encrypt": "Encrypt (crypt15)", "input": "Input file",
  "isdir": "Input is a folder (decryption only)", "key": "Key",
  "keyhint": "The key can be the .key file, encrypted_backup.key, or the 64 hex characters of the root key.",
  "outfile": "Output", "merge_sec": "Database merge",
  "mergefolder": "Folder with the databases", "mergeout": "Resulting database",
  "gd_sec": "Google Drive", "gd_cred": "Credentials are read from cfg/settings.cfg, section [google-auth].",
  "gd_info": "Backup information", "gd_list": "List everything", "gd_listwa": "List WhatsApp backups",
  "gd_pull": "Download a file", "gd_sync": "Sync everything", "gd_img": "Images only",
  "gd_vid": "Videos only", "gd_aud": "Audio only", "gd_doc": "Documents only", "gd_db": "Databases only",
  "remotefile": "File to download", "threads": "Threads",
  "noparallel": "No parallel downloads", "dryrun": "Dry run (no download)",
  "chat_sec": "Chat exported from the app", "chatfile": "Chat file",
  "system": "System", "chatuser": "Target user", "datemask": "Date mask",
  "onlypart": "List participants only", "ic_sec": "iCloud",
  "chatmedia": "Folder with the exported attachments",
  "copymedia_short": "Copy attachments into report", "regex": "Regex",
  "ic_cred": "Credentials are read from cfg/settings.cfg, section [icloud-auth].",
  "ic_list": "List", "ic_sync": "Sync everything", "ic_img": "Images only",
  "ic_vid": "Videos and audio only",
  "cfg_title": "Settings", "cfg_report": "Report details",
  "cfg_google": "Google Drive", "cfg_icloud": "iCloud", "cfg_save": "Save",
  "cfg_cancel": "Cancel", "cfg_saved": "Settings saved to cfg/settings.cfg",
  "deps_title": "Install requirements",
  "deps_q": "This will install everything in doc/requirements.txt.\n\nIt needs an internet connection and may take a while.\n\nContinue?",
  "missing": "These requirements are missing", "allok": "All requirements are installed.",
  "ph_db": "msgstore.db (Android)  /  ChatStorage.sqlite (iOS)",
  "ph_wa": "wa.db (Android)  /  ContactsV2.sqlite (iOS)  -  adds the names",
  "ph_enc": "msgstore.db.crypt15  /  .crypt14  /  .crypt12",
  "ph_key": "key file  /  encrypted_backup.key  /  64 hex characters",
  "ph_out": "folder where the report will be written",
  "ph_outfile": "msgstore.db  (file to be created)",
  "ph_media": "WhatsApp folder copied from the phone (the one holding Media)",
  "ph_chat": "WhatsApp Chat with <name>.txt",
  "ph_chatmedia": "defaults to the same folder as the .txt",
  "ph_mergedir": "folder holding several msgstore.db",
  "ph_mergeout": "msgstore_merge.db  (file to be created)",
  "f_read": "Read", "f_unread": "No read receipt",
  "ph_case": "Case 1234/2026  -  printed on the cover",
  "ph_examiner": "who signs the analysis",
  "warn_data": "Missing data", "warn_db": "Choose a database.",
  "warn_in": "Input, key and output are required.",
  "warn_folder": "Choose the folder with the databases.", "warn_chat": "Choose the chat file.",
  "warn_remote": "Enter the file to download.",
 },
}

ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("green")

F11 = dict(size=11)
F12 = dict(size=12)


def tool(name):
    return os.path.join(LIBS, name)


# Las herramientas se lanzan desde la raiz del proyecto, no desde libs/: si no,
# un informe sin ruta de salida acabaria dentro de libs/, que no es sitio.
# Los modulos de libs/ se importan igual porque cada herramienta anade su propio
# directorio a sys.path.


class Field:
    """Campo de texto con pista visible.

    CustomTkinter solo muestra el placeholder si el campo NO tiene textvariable
    (ver CTkEntry._activate_placeholder). Como aqui interesa mas que el usuario
    vea que archivo se espera, se prescinde de la variable de Tk y se habla
    directamente con el widget, manteniendo la misma interfaz .get() / .set()
    para que el resto del codigo no cambie.
    """

    def __init__(self, value=""):
        self._widget = None
        self._value = value

    def attach(self, widget):
        self._widget = widget
        if self._value:
            widget.insert(0, self._value)

    def get(self):
        if self._widget is not None:
            try:
                return self._widget.get()
            except Exception:
                pass
        return self._value

    def set(self, valor):
        self._value = valor or ""
        if self._widget is None:
            return
        try:
            self._widget.delete(0, "end")
            if valor:
                self._widget.insert(0, valor)
            else:
                # al vaciarlo, la pista debe volver a verse
                self._widget._activate_placeholder()
        except Exception:
            pass


class Row:
    """Ayudante para colocar controles en rejilla dentro de un marco."""

    def __init__(self, master):
        self.m = master
        self.r = 0
        master.grid_columnconfigure(1, weight=1)

    def file(self, label, var, title, types=None, save=False, folder=False,
             hint=None):
        """hint aparece dentro del campo mientras esta vacio, para que se vea
        que archivo se espera sin tener que abrir el dialogo."""
        ctk.CTkLabel(self.m, text=label, text_color=TEXT, anchor="w",
                     font=ctk.CTkFont(**F12)).grid(row=self.r, column=0, sticky="w",
                                                   padx=(12, 6), pady=4)
        e = ctk.CTkEntry(self.m, fg_color=FIELD, border_width=0,
                         placeholder_text=hint or "")
        e.grid(row=self.r, column=1, columnspan=2, sticky="ew", pady=4)
        var.attach(e)

        def pick():
            if folder:
                p = filedialog.askdirectory(title=title)
            elif save:
                p = filedialog.asksaveasfilename(title=title, filetypes=types or [("Todos", "*.*")])
            else:
                p = filedialog.askopenfilename(title=title, filetypes=types or [("Todos", "*.*")])
            if p:
                var.set(p)

        ctk.CTkButton(self.m, text="Examinar", width=86, command=pick,
                      fg_color=FIELD, hover_color="#2a3942", font=ctk.CTkFont(**F11)
                      ).grid(row=self.r, column=3, padx=(6, 12), pady=4)
        self.r += 1

    def entry(self, label, var, placeholder="", width=200):
        ctk.CTkLabel(self.m, text=label, text_color=TEXT, anchor="w",
                     font=ctk.CTkFont(**F12)).grid(row=self.r, column=0, sticky="w",
                                                   padx=(12, 6), pady=4)
        e = ctk.CTkEntry(self.m, fg_color=FIELD, border_width=0,
                         placeholder_text=placeholder, width=width)
        e.grid(row=self.r, column=1, sticky="w", pady=4)
        var.attach(e)
        self.r += 1

    def options(self, label, var, values, width=190):
        ctk.CTkLabel(self.m, text=label, text_color=TEXT, anchor="w",
                     font=ctk.CTkFont(**F12)).grid(row=self.r, column=0, sticky="w",
                                                   padx=(12, 6), pady=4)
        ctk.CTkOptionMenu(self.m, variable=var, values=values, width=width,
                          fg_color=FIELD, button_color=FIELD,
                          button_hover_color="#2a3942", font=ctk.CTkFont(**F12)
                          ).grid(row=self.r, column=1, sticky="w", pady=4)
        self.r += 1

    def checks(self, items, cols=5, label=None):
        """items: lista de (variable, texto)."""
        if label:
            ctk.CTkLabel(self.m, text=label, text_color=MUTED, anchor="w",
                         font=ctk.CTkFont(size=10)).grid(row=self.r, column=0,
                                                         columnspan=4, sticky="w",
                                                         padx=12, pady=(8, 0))
            self.r += 1
        box = ctk.CTkFrame(self.m, fg_color="transparent")
        box.grid(row=self.r, column=0, columnspan=4, sticky="w", padx=10, pady=2)
        for i, (var, txt) in enumerate(items):
            ctk.CTkCheckBox(box, text=txt, variable=var, text_color=TEXT,
                            fg_color=ACCENT, hover_color=ACCENT_HOVER,
                            checkbox_width=16, checkbox_height=16,
                            font=ctk.CTkFont(size=11)
                            ).grid(row=i // cols, column=i % cols, sticky="w",
                                   padx=6, pady=2)
        self.r += 1

    def section(self, text):
        ctk.CTkLabel(self.m, text=text, text_color=ACCENT,
                     font=ctk.CTkFont(size=12, weight="bold")
                     ).grid(row=self.r, column=0, columnspan=4, sticky="w",
                            padx=12, pady=(10, 2))
        self.r += 1

    def run(self, text, command):
        b = ctk.CTkButton(self.m, text=text, command=command, width=180,
                          fg_color=ACCENT, hover_color=ACCENT_HOVER,
                          text_color="#04160f",
                          font=ctk.CTkFont(size=13, weight="bold"))
        b.grid(row=self.r, column=0, columnspan=2, sticky="w", padx=12, pady=12)
        self.r += 1
        return b


class SettingsDialog(ctk.CTkToplevel):
    """Editor de cfg/settings.cfg: datos del informe y credenciales."""

    CAMPOS = [
        ("report", "company",   "Empresa / Organismo"),
        ("report", "record",    "Referencia del atestado"),
        ("report", "unit",      "Unidad"),
        ("report", "examiner",  "Instructor / analista"),
        ("report", "notes",     "Notas"),
        ("google-auth", "gmail",      "Cuenta de Gmail"),
        ("google-auth", "password",   "Contrasena (o de aplicacion si usas 2FA)"),
        ("google-auth", "oauth",      "Cookie oauth (opcional)"),
        ("google-auth", "android_id", "android_id"),
        ("google-auth", "celnumbr",   "Numeros a sincronizar (opcional)"),
        ("icloud-auth", "icloud", "Cuenta de iCloud"),
        ("icloud-auth", "passw",  "Contrasena"),
    ]
    SECCIONES = {"report": "cfg_report", "google-auth": "cfg_google",
                 "icloud-auth": "cfg_icloud"}

    def __init__(self, master):
        super().__init__(master)
        self.master_gui = master
        self.title(master.T("cfg_title"))
        self.geometry("640x620")
        self.configure(fg_color=BG)
        self.transient(master)
        self.ruta = os.path.join(APP_DIR, "cfg", "settings.cfg")
        self.vars = {}
        self._build()
        self.after(120, self.grab_set)     # tras dibujarse, para no fallar en Linux

    def _build(self):
        T = self.master_gui.T
        sc = ctk.CTkScrollableFrame(self, fg_color="transparent")
        sc.pack(fill="both", expand=True, padx=12, pady=12)
        sc.grid_columnconfigure(1, weight=1)

        cfg = ConfigParser()
        if os.path.exists(self.ruta):
            try:
                cfg.read(self.ruta, encoding="utf-8")
            except Exception:
                pass

        fila = 0
        seccion_actual = None
        for sec, clave, etiqueta in self.CAMPOS:
            if sec != seccion_actual:
                seccion_actual = sec
                ctk.CTkLabel(sc, text=T(self.SECCIONES[sec]), text_color=ACCENT,
                             font=ctk.CTkFont(size=13, weight="bold")
                             ).grid(row=fila, column=0, columnspan=2, sticky="w",
                                    pady=(14, 4))
                fila += 1
            valor = ""
            if cfg.has_option(sec, clave):
                valor = cfg.get(sec, clave).strip().strip('"')
            var = ctk.StringVar(value=valor)
            self.vars[(sec, clave)] = var
            ctk.CTkLabel(sc, text=etiqueta, text_color=TEXT, anchor="w",
                         font=ctk.CTkFont(**F12)).grid(row=fila, column=0,
                                                       sticky="w", padx=(0, 10), pady=3)
            oculta = "*" if clave in ("password", "passw") else ""
            ctk.CTkEntry(sc, textvariable=var, fg_color=FIELD, border_width=0,
                         show=oculta, width=330).grid(row=fila, column=1,
                                                      sticky="ew", pady=3)
            fila += 1

        barra = ctk.CTkFrame(self, fg_color="transparent")
        barra.pack(fill="x", padx=12, pady=(0, 12))
        ctk.CTkButton(barra, text=T("cfg_save"), command=self._save, width=130,
                      fg_color=ACCENT, hover_color=ACCENT_HOVER,
                      text_color="#04160f",
                      font=ctk.CTkFont(size=13, weight="bold")).pack(side="right")
        ctk.CTkButton(barra, text=T("cfg_cancel"), command=self.destroy, width=110,
                      fg_color=FIELD, hover_color="#2a3942").pack(side="right", padx=8)
        ctk.CTkLabel(barra, text=self.ruta, text_color=MUTED,
                     font=ctk.CTkFont(size=10)).pack(side="left")

    def _save(self):
        cfg = ConfigParser()
        if os.path.exists(self.ruta):
            try:
                cfg.read(self.ruta, encoding="utf-8")
            except Exception:
                pass
        for (sec, clave), var in self.vars.items():
            if not cfg.has_section(sec):
                cfg.add_section(sec)
            valor = var.get()
            # los datos del informe se guardan entrecomillados, como en el original
            if sec == "report":
                valor = '"{}"'.format(valor.replace('"', ""))
            cfg.set(sec, clave, valor)
        try:
            os.makedirs(os.path.dirname(self.ruta), exist_ok=True)
            with open(self.ruta, "w", encoding="utf-8") as fh:
                cfg.write(fh)
            self.master_gui._emit("[-] " + self.master_gui.T("cfg_saved"), "ok")
            self.destroy()
        except OSError as e:
            messagebox.showerror("whapa", str(e))


class WhapaGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("WhaPa {} - Whatsapp Parser".format(version))
        # El tamano inicial nunca debe superar la pantalla: en un equipo de
        # 1024x768 una ventana de 1060x860 se sale y no se ven los botones.
        try:
            _sw, _sh = self.winfo_screenwidth(), self.winfo_screenheight()
        except Exception:
            _sw, _sh = 1280, 800
        self.geometry("{}x{}".format(min(1060, _sw - 20), min(860, _sh - 80)))
        self.minsize(min(900, _sw - 40), min(640, _sh - 100))
        self.configure(fg_color=BG)
        self.q = queue.Queue()
        self.busy = False
        self.buttons = []
        self.lang = "ES"
        self._set_icon()
        self._build()
        # Se maximiza cuando la ventana ya existe: hacerlo dentro de __init__,
        # antes de que el gestor de ventanas la dibuje, no surte efecto.
        self.after(10, self._maximizar)
        self.after(100, self._drain)

    def _maximizar(self):
        """Abre la ventana maximizada, con el metodo que admita cada sistema.

        No hay uno que valga para todos: Windows entiende state("zoomed"),
        varios gestores de ventanas de Linux usan el atributo -zoomed, y en
        macOS no funciona ninguno, asi que se recurre a ajustar la geometria al
        tamano de la pantalla. Se prueban en ese orden y se comprueba el
        resultado, porque un metodo puede no dar error y aun asi no hacer nada.
        """
        try:
            pantalla_ancho = self.winfo_screenwidth()
            pantalla_alto = self.winfo_screenheight()
        except Exception:
            return

        def maximizada():
            try:
                return (self.winfo_width() >= pantalla_ancho * 0.92
                        and self.winfo_height() >= pantalla_alto * 0.80)
            except Exception:
                return False

        for metodo in (lambda: self.state("zoomed"),
                       lambda: self.attributes("-zoomed", True)):
            try:
                metodo()
                self.update_idletasks()
                if maximizada():
                    return
            except Exception:
                continue

        # Ultimo recurso: ocupar la pantalla a mano, dejando hueco para la
        # barra de tareas.
        try:
            self.geometry("{}x{}+0+0".format(pantalla_ancho,
                                             max(500, pantalla_alto - 70)))
        except Exception:
            pass

    # ------------------------------------------------------------------
    def T(self, clave):
        """Texto en el idioma activo."""
        return LANG[self.lang].get(clave, clave)

    def _set_icon(self):
        """Icono de la ventana, desde images/."""
        ico = os.path.join(APP_DIR, "images", "logo.ico")
        png = os.path.join(APP_DIR, "images", "logo.png")
        try:
            if sys.platform.startswith("win") and os.path.exists(ico):
                self.iconbitmap(ico)
            elif os.path.exists(png):
                import tkinter as tk
                self._icon_img = tk.PhotoImage(file=png)
                self.iconphoto(True, self._icon_img)
        except Exception:
            pass          # el icono es un detalle: nunca debe impedir arrancar

    def _switch_lang(self):
        self.lang = "EN" if self.lang == "ES" else "ES"
        registro = self.log.get("1.0", "end")
        for w in self.winfo_children():
            w.destroy()
        self.buttons = []
        self._build()
        if registro.strip():
            self.log.insert("end", registro)

    # ------------------------------------------------------------------
    def _build(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(1, weight=1)
        self.grid_rowconfigure(2, minsize=210)

        head = ctk.CTkFrame(self, fg_color="transparent")
        head.grid(row=0, column=0, sticky="ew", padx=14, pady=(12, 4))
        ctk.CTkLabel(head, text="WhaPa", text_color=ACCENT,
                     font=ctk.CTkFont(size=22, weight="bold")).pack(side="left")
        ctk.CTkLabel(head, text="   " + self.T("subtitle"),
                     text_color=MUTED, font=ctk.CTkFont(**F12)).pack(side="left")

        # barra de herramientas
        for txt, cmd in ((self.T("lang"), self._switch_lang),
                         (self.T("about"), self._about),
                         (self.T("readme"), self._readme),
                         (self.T("settings"), self._settings),
                         (self.T("deps"), self._install_deps)):
            ctk.CTkButton(head, text=txt, command=cmd, width=136,
                          fg_color=FIELD, hover_color="#2a3942",
                          font=ctk.CTkFont(**F11)).pack(side="right", padx=3)

        self.tabs = ctk.CTkTabview(self, fg_color=PANEL, segmented_button_fg_color=FIELD,
                                   segmented_button_selected_color=ACCENT,
                                   segmented_button_selected_hover_color=ACCENT_HOVER)
        self.tabs.grid(row=1, column=0, sticky="nsew", padx=14, pady=4)
        for name in ("WhaPa", "WhaCipher", "WhaMerge", "WhaGoDri", "WhaChat", "WhaCloud"):
            self.tabs.add(name)

        self._tab_whapa(self.tabs.tab("WhaPa"))
        self._tab_whacipher(self.tabs.tab("WhaCipher"))
        self._tab_whamerge(self.tabs.tab("WhaMerge"))
        self._tab_whagodri(self.tabs.tab("WhaGoDri"))
        self._tab_whachat(self.tabs.tab("WhaChat"))
        self._tab_whacloud(self.tabs.tab("WhaCloud"))

        bottom = ctk.CTkFrame(self, fg_color="transparent")
        bottom.grid(row=2, column=0, sticky="nsew", padx=14, pady=(4, 12))
        bottom.grid_columnconfigure(0, weight=1)
        bottom.grid_rowconfigure(1, weight=1)

        bar = ctk.CTkFrame(bottom, fg_color="transparent")
        bar.grid(row=0, column=0, sticky="ew")
        ctk.CTkLabel(bar, text=self.T("output"), text_color=ACCENT,
                     font=ctk.CTkFont(size=12, weight="bold")).pack(side="left")
        ctk.CTkButton(bar, text=self.T("clear"), width=80, command=self._clear,
                      fg_color=FIELD, hover_color="#2a3942",
                      font=ctk.CTkFont(**F11)).pack(side="right", padx=4)
        self.progress = ctk.CTkProgressBar(bar, width=160, mode="indeterminate",
                                           progress_color=ACCENT)
        self.progress.pack(side="right", padx=8)
        self.progress.set(0)

        self.log = ctk.CTkTextbox(bottom, fg_color=PANEL, text_color=TEXT,
                                  corner_radius=10, wrap="word",
                                  font=ctk.CTkFont(family="Consolas", size=12))
        self.log.grid(row=1, column=0, sticky="nsew", pady=(4, 0))
        self.log.tag_config("ok", foreground=ACCENT)
        self.log.tag_config("err", foreground=ERROR)
        self.log.tag_config("cmd", foreground=MUTED)
        self._emit(self.T("hint_start"), "cmd")


    # ------------------------------------------------------------------
    #  Barra de herramientas
    # ------------------------------------------------------------------
    def _install_deps(self):
        """Instala doc/requirements.txt con el pip del interprete en uso."""
        req = os.path.join(APP_DIR, "doc", "requirements.txt")
        if not os.path.exists(req):
            return messagebox.showerror("whapa", "No se encuentra {}".format(req))
        faltan = []
        try:
            sys.path.insert(0, LIBS)
            import whadeps
            faltan = whadeps.check("Crypto", "colorama", "customtkinter", "requests",
                                   "pandas", "numpy", "configobj", "click",
                                   "pyicloud", "selenium", "Cryptodome")
        except Exception:
            pass
        detalle = ("\n\n{}: {}".format(self.T("missing"), ", ".join(faltan))
                   if faltan else "\n\n" + self.T("allok"))
        if not messagebox.askyesno(self.T("deps_title"),
                                   self.T("deps_q") + detalle):
            return
        # se usa el pip del interprete que esta ejecutando la interfaz, para no
        # instalar en un Python distinto del que luego ejecuta las herramientas
        self._launch_raw([sys.executable, "-m", "pip", "install", "--upgrade",
                          "-r", req])

    def _settings(self):
        """Editor de cfg/settings.cfg."""
        SettingsDialog(self)

    def _readme(self):
        ruta = os.path.join(APP_DIR, "README.md")
        if os.path.exists(ruta):
            webbrowser.open("file://" + os.path.abspath(ruta))
        else:
            webbrowser.open("https://github.com/B16f00t/whapa")

    def _about(self):
        messagebox.showinfo(
            "WhaPa " + version,
            "WhaPa {} - Whatsapp Parser Toolset\n\n"
            "Android e iOS\n"
            "Ivan Moreno (B16f00t)\n"
            "https://github.com/B16f00t/whapa\n\n"
            "Licencia GPL-3.0".format(version))

    # ---------------- pestana WhaPa ----------------
    def _tab_whapa(self, tab):
        sc = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        sc.pack(fill="both", expand=True)
        r = Row(sc)
        self.p_db, self.p_wa, self.p_out = Field(), Field(), Field()
        r.section(self.T("db"))
        r.file(self.T("db_dec"), self.p_db, "msgstore.db / ChatStorage.sqlite",
               [("SQLite", "*.db *.sqlite"), ("Todos", "*.*")],
               hint=self.T("ph_db"))
        r.file(self.T("contacts"), self.p_wa, "wa.db / ContactsV2.sqlite",
               [("SQLite", "*.db *.sqlite"), ("Todos", "*.*")],
               hint=self.T("ph_wa"))
        r.file(self.T("outdir"), self.p_out, self.T("outdir"), folder=True,
               hint=self.T("ph_out"))
        self.p_media = Field()
        r.file(self.T("wafolder"), self.p_media, self.T("wafolder"), folder=True,
               hint=self.T("ph_media"))
        self.p_copymedia = ctk.BooleanVar()
        r.checks([(self.p_copymedia,
                   self.T("copymedia"))],
                 cols=1)

        r.section(self.T("mode"))
        self.p_mode = ctk.StringVar(value="Mensajes")
        r.options(self.T("mode"), self.p_mode, ["Mensajes", "Info: estados", "Info: llamadas",
                                        "Info: chats activos", "Extraer adjuntos", "Carving"])
        self.p_platform = ctk.StringVar(value="Autodetectar")
        r.options(self.T("platform"), self.p_platform,
                  ["Autodetectar", "Android actual", "Android antiguo", "iOS"])

        r.section(self.T("recipients"))
        self.p_recip = ctk.StringVar(value="Todos")
        r.options(self.T("scope"), self.p_recip, ["Todos", "Usuario", "Grupo",
                                            "Mensajes de un numero", "Difusion"])
        self.p_target = Field()
        r.entry(self.T("target"), self.p_target, "34123456789  /  1234-5678@g.us", 260)

        r.section(self.T("filters"))
        self.p_text, self.p_sender = Field(), Field()
        self.p_ts, self.p_te, self.p_raw = Field(), Field(), Field()
        r.entry(self.T("text"), self.p_text, "contenido, archivo o cita", 280)
        r.entry(self.T("sender"), self.p_sender, "numero o nombre", 200)
        r.entry(self.T("from"), self.p_ts, "dd-mm-aaaa HH:MM", 180)
        r.entry(self.T("to"), self.p_te, "dd-mm-aaaa HH:MM", 180)
        r.entry(self.T("rawtypes"), self.p_raw, "66,112", 140)
        self.p_dir = ctk.StringVar(value="Todas")
        r.options(self.T("direction"), self.p_dir, ["Todas", "Enviados", "Recibidos", "Del sistema"])

        self.p_flags = {}
        for k in ("regex", "case", "word", "web", "starred", "forwarded",
                  "edited", "media", "location", "read", "unread"):
            self.p_flags[k] = ctk.BooleanVar()
        r.checks([(self.p_flags["regex"], "Regex"), (self.p_flags["case"], "May/min"),
                  (self.p_flags["word"], "Palabra completa"),
                  (self.p_flags["web"], "WhatsApp Web"),
                  (self.p_flags["starred"], "Destacados"),
                  (self.p_flags["forwarded"], "Reenviados"),
                  (self.p_flags["edited"], "Editados"),
                  (self.p_flags["media"], "Con adjunto"),
                  (self.p_flags["location"], "Con coordenadas"),
                  (self.p_flags["read"], self.T("f_read")),
                  (self.p_flags["unread"], self.T("f_unread"))],
                 cols=5, label=self.T("searchopts"))

        self.p_types = {}
        tipos = [("tt", "Texto"), ("ti", "Imagen"), ("ta", "Audio"), ("tv", "Video"),
                 ("tc", "Contacto"), ("tl", "Ubicacion"), ("tx", "Llamada"),
                 ("tp", "Documento"), ("tg", "GIF"), ("td", "Borrado"),
                 ("tr", "Ubic. tiempo real"), ("tk", "Sticker"), ("tm", "Sistema"),
                 ("tn", "Encuesta"), ("tq", "Vision unica"), ("tj", "Nota de video"),
                 ("tz", "Evento")]
        for k, _ in tipos:
            self.p_types[k] = ctk.BooleanVar()
        r.checks([(self.p_types[k], t) for k, t in tipos], cols=6,
                 label=self.T("types"))

        r.section(self.T("output"))
        self.p_report = ctk.StringVar(value="Ninguno")
        r.options(self.T("report"), self.p_report, ["Ninguno", "ES", "EN"])
        self.p_out_flags = {k: ctk.BooleanVar()
                            for k in ("print", "csv", "kml", "maps", "single")}
        r.checks([(self.p_out_flags["print"], self.T("print")),
                  (self.p_out_flags["csv"], self.T("csv")),
                  (self.p_out_flags["kml"], self.T("kml")),
                  (self.p_out_flags["maps"], self.T("maps")),
                  (self.p_out_flags["single"], self.T("single"))], cols=3)
        self.buttons.append(r.run(self.T("run")+" WhaPa", self._run_whapa))

    def _run_whapa(self):
        if not self.p_db.get():
            return messagebox.showwarning("Faltan datos", "Elige una base de datos.")
        a = [tool("whapa.py"), self.p_db.get()]
        modo = self.p_mode.get()
        if modo == "Mensajes":
            a.append("-m")
        elif modo.startswith("Info"):
            a += ["-i", {"Info: estados": "1", "Info: llamadas": "2",
                         "Info: chats activos": "3"}[modo]]
        elif modo == "Extraer adjuntos":
            a.append("-e")
        else:
            a.append("-c")

        plat = {"Android actual": "android", "Android antiguo": "android_legacy",
                "iOS": "ios"}.get(self.p_platform.get())
        if plat:
            a += ["--platform", plat]
        if self.p_wa.get():
            a += ["-wa", self.p_wa.get()]
        if self.p_out.get():
            a += ["-o", self.p_out.get()]
        if self.p_media.get():
            a += ["-mp", self.p_media.get()]
            if self.p_copymedia.get():
                a.append("-cm")

        if modo == "Mensajes":
            alc, tgt = self.p_recip.get(), self.p_target.get().strip()
            if alc == "Todos":
                a.append("-a")
            elif alc == "Difusion":
                a += ["-a", "-b"]
            elif alc == "Usuario" and tgt:
                a += ["-u", tgt]
            elif alc == "Grupo" and tgt:
                a += ["-g", tgt]
            elif alc == "Mensajes de un numero" and tgt:
                a += ["-ua", tgt]
            else:
                a.append("-a")

            if self.p_text.get():
                a += ["-t", self.p_text.get()]
            if self.p_sender.get():
                a += ["-sn", self.p_sender.get()]
            if self.p_ts.get():
                a += ["-ts", self.p_ts.get()]
            if self.p_te.get():
                a += ["-te", self.p_te.get()]
            if self.p_raw.get():
                a += ["-rt", self.p_raw.get()]
            d = {"Enviados": "sent", "Recibidos": "received",
                 "Del sistema": "system"}.get(self.p_dir.get())
            if d:
                a += ["-d", d]
            for k, flag in (("regex", "-re"), ("case", "-cs"), ("word", "-ww"),
                            ("web", "-w"), ("starred", "-s"), ("forwarded", "-fw"),
                            ("edited", "-ed"), ("media", "-md"), ("location", "-gp"),
                            ("read", "-lr"), ("unread", "-lu")):
                if self.p_flags[k].get():
                    a.append(flag)
            for k, v in self.p_types.items():
                if v.get():
                    a.append("-" + k)
            if self.p_report.get() != "Ninguno":
                a += ["-r", self.p_report.get()]
            if self.p_out_flags["print"].get():
                a.append("-p")
            if self.p_out_flags["csv"].get():
                a.append("-x")
            if self.p_out_flags["kml"].get():
                a.append("-k")
            if self.p_out_flags["maps"].get():
                a.append("-gm")
            if self.p_out_flags["single"].get():
                a.append("-1")
        self._launch(a)

    # ---------------- pestana WhaCipher ----------------
    def _tab_whacipher(self, tab):
        r = Row(tab)
        self.c_mode = ctk.StringVar(value="Descifrar")
        self.c_in, self.c_key, self.c_out = Field(), Field(), Field()
        self.c_isdir = ctk.BooleanVar()
        r.section(self.T("cipher_sec"))
        r.options(self.T("action"), self.c_mode, ["Descifrar", "Cifrar (crypt15)"])
        r.file(self.T("input"), self.c_in, "Base cifrada o descifrada",
               [("Bases", "*.crypt12 *.crypt14 *.crypt15 *.db"), ("Todos", "*.*")],
               hint=self.T("ph_enc"))
        r.checks([(self.c_isdir, self.T("isdir"))], cols=1)
        r.file(self.T("key"), self.c_key, "Archivo de clave",
               hint=self.T("ph_key"))
        ctk.CTkLabel(tab, text="La clave puede ser el archivo .key, encrypted_backup.key "
                               "o los 64 caracteres hexadecimales de la clave raiz.",
                     text_color=MUTED, font=ctk.CTkFont(size=11), wraplength=820,
                     justify="left").grid(row=r.r, column=0, columnspan=4,
                                          sticky="w", padx=12, pady=(0, 4))
        r.r += 1
        r.file(self.T("output"), self.c_out, "Archivo o carpeta de salida", save=True)
        self.buttons.append(r.run(self.T("run")+" WhaCipher", self._run_whacipher))

    def _run_whacipher(self):
        if not (self.c_in.get() and self.c_key.get() and self.c_out.get()):
            return messagebox.showwarning("Faltan datos",
                                          "Entrada, clave y salida son obligatorias.")
        a = [tool("whacipher.py")]
        a += ["-p" if self.c_isdir.get() else "-f", self.c_in.get()]
        a += ["-d" if self.c_mode.get() == "Descifrar" else "-e", self.c_key.get()]
        a += ["-o", self.c_out.get()]
        self._launch(a)

    # ---------------- pestana WhaMerge ----------------
    def _tab_whamerge(self, tab):
        r = Row(tab)
        self.m_path, self.m_out = Field(), Field()
        r.section(self.T("merge_sec"))
        r.file(self.T("mergefolder"), self.m_path, "Carpeta con msgstore*.db",
               folder=True, hint=self.T("ph_mergedir"))
        r.file(self.T("mergeout"), self.m_out, "msgstore_merge.db", save=True,
               hint=self.T("ph_mergeout"))
        self.buttons.append(r.run(self.T("run")+" WhaMerge", self._run_whamerge))

    def _run_whamerge(self):
        if not self.m_path.get():
            return messagebox.showwarning("Faltan datos", "Elige la carpeta con las bases.")
        a = [tool("whamerge.py"), self.m_path.get()]
        if self.m_out.get():
            a += ["-o", self.m_out.get()]
        self._launch(a)

    # ---------------- pestana WhaGoDri ----------------
    def _tab_whagodri(self, tab):
        sc = ctk.CTkScrollableFrame(tab, fg_color="transparent")
        sc.pack(fill="both", expand=True)
        r = Row(sc)
        r.section(self.T("gd_sec"))
        ctk.CTkLabel(sc, text="Las credenciales se leen de cfg/settings.cfg, seccion "
                              "[google-auth].", text_color=MUTED,
                     font=ctk.CTkFont(size=11)).grid(row=r.r, column=0, columnspan=4,
                                                     sticky="w", padx=12, pady=(0, 6))
        r.r += 1
        self.g_action = ctk.StringVar(value="Informacion de copias")
        r.options(self.T("action"), self.g_action,
                  ["Informacion de copias", "Listar todo", "Listar copias de WhatsApp",
                   "Descargar un archivo", "Sincronizar todo", "Solo imagenes",
                   "Solo videos", "Solo audios", "Solo documentos", "Solo bases"], 250)
        self.g_file, self.g_out = Field(), Field()
        r.entry(self.T("remotefile"), self.g_file, "ruta remota", 260)
        r.file(self.T("outdir"), self.g_out, self.T("outdir"), folder=True,
               hint=self.T("ph_out"))
        self.g_threads = Field("12")
        r.entry(self.T("threads"), self.g_threads, "12", 80)
        self.g_np, self.g_dry = ctk.BooleanVar(), ctk.BooleanVar()
        r.checks([(self.g_np, self.T("noparallel")),
                  (self.g_dry, self.T("dryrun"))], cols=2)
        self.buttons.append(r.run(self.T("run")+" WhaGoDri", self._run_whagodri))

    def _run_whagodri(self):
        mapa = {"Informacion de copias": "-i", "Listar todo": "-l",
                "Listar copias de WhatsApp": "-lw", "Sincronizar todo": "-s",
                "Solo imagenes": "-si", "Solo videos": "-sv", "Solo audios": "-sa",
                "Solo documentos": "-sx", "Solo bases": "-sd"}
        a = [tool("whagodri.py")]
        acc = self.g_action.get()
        if acc == "Descargar un archivo":
            if not self.g_file.get():
                return messagebox.showwarning("Faltan datos", "Indica el archivo a descargar.")
            a += ["-p", self.g_file.get()]
        else:
            a.append(mapa[acc])
        if self.g_out.get():
            a += ["-o", self.g_out.get()]
        if self.g_np.get():
            a.append("-np")
        if self.g_dry.get():
            a.append("-dr")
        if self.g_threads.get().isdigit():
            a += ["-tc", self.g_threads.get()]
        self._launch(a)

    # ---------------- pestana WhaChat ----------------
    def _tab_whachat(self, tab):
        r = Row(tab)
        self.h_file, self.h_user = Field(), Field()
        self.h_fmt, self.h_ts, self.h_te = Field(), Field(), Field()
        r.section(self.T("chat_sec"))
        r.file(self.T("chatfile"), self.h_file, "Chat exportado (.txt)",
               [("Texto", "*.txt"), ("Todos", "*.*")], hint=self.T("ph_chat"))
        self.h_sys = ctk.StringVar(value="android")
        r.options(self.T("system"), self.h_sys, ["android", "ios"], 140)
        self.h_report = ctk.StringVar(value="Ninguno")
        r.options(self.T("report"), self.h_report, ["Ninguno", "ES", "EN"], 140)
        r.entry(self.T("chatuser"), self.h_user, "nombre tal y como aparece", 260)
        r.entry(self.T("datemask"), self.h_fmt, "%d/%m/%y %H:%M:%S", 200)
        r.entry(self.T("from"), self.h_ts, "dd-mm-aaaa HH:MM", 180)
        r.entry(self.T("to"), self.h_te, "dd-mm-aaaa HH:MM", 180)
        self.h_media = Field()
        r.file(self.T("chatmedia"), self.h_media, self.T("chatmedia"),
               folder=True, hint=self.T("ph_chatmedia"))
        self.h_out = Field()
        r.file(self.T("outdir"), self.h_out, self.T("outdir"), folder=True,
               hint=self.T("ph_out"))
        self.h_text = Field()
        r.entry(self.T("text"), self.h_text, "", 240)
        self.h_part = ctk.BooleanVar()
        self.h_flags = {k: ctk.BooleanVar() for k in ("print", "csv", "copy", "regex")}
        r.checks([(self.h_part, self.T("onlypart")),
                  (self.h_flags["print"], self.T("print")),
                  (self.h_flags["csv"], self.T("csv")),
                  (self.h_flags["copy"], self.T("copymedia_short")),
                  (self.h_flags["regex"], self.T("regex"))], cols=3)
        self.buttons.append(r.run(self.T("run")+" WhaChat", self._run_whachat))

    def _run_whachat(self):
        if not self.h_file.get():
            return messagebox.showwarning("Faltan datos", "Elige el archivo del chat.")
        a = [tool("whachat.py"), self.h_file.get()]
        if self.h_part.get():
            a.append("-p")
        if self.h_user.get():
            a += ["-u", self.h_user.get()]
        a += ["-s", self.h_sys.get()]
        if self.h_report.get() != "Ninguno":
            a += ["-r", self.h_report.get()]
        if self.h_fmt.get():
            a += ["-f", self.h_fmt.get()]
        if self.h_ts.get():
            a += ["-ts", self.h_ts.get()]
        if self.h_te.get():
            a += ["-te", self.h_te.get()]
        if self.h_out.get():
            a += ["-o", self.h_out.get()]
        if self.h_media.get():
            a += ["-mp", self.h_media.get()]
        if self.h_text.get():
            a += ["-t", self.h_text.get()]
        if self.h_flags["regex"].get():
            a.append("-re")
        if self.h_flags["print"].get():
            a.append("-pr")
        if self.h_flags["csv"].get():
            a.append("-x")
        if self.h_flags["copy"].get():
            a.append("-cm")
        self._launch(a)

    # ---------------- pestana WhaCloud ----------------
    def _tab_whacloud(self, tab):
        r = Row(tab)
        r.section(self.T("ic_sec"))
        ctk.CTkLabel(tab, text="Las credenciales se leen de cfg/settings.cfg, seccion "
                               "[icloud-auth].", text_color=MUTED,
                     font=ctk.CTkFont(size=11)).grid(row=r.r, column=0, columnspan=4,
                                                     sticky="w", padx=12, pady=(0, 6))
        r.r += 1
        self.k_action = ctk.StringVar(value="Listar")
        r.options(self.T("action"), self.k_action, ["Listar", "Descargar un archivo",
                                            "Sincronizar todo", "Solo imagenes",
                                            "Solo videos y audios"], 230)
        self.k_file, self.k_out = Field(), Field()
        r.entry(self.T("remotefile"), self.k_file, "ruta remota", 260)
        r.file(self.T("outdir"), self.k_out, self.T("outdir"), folder=True,
               hint=self.T("ph_out"))
        self.buttons.append(r.run(self.T("run")+" WhaCloud", self._run_whacloud))

    def _run_whacloud(self):
        mapa = {"Listar": "-l", "Sincronizar todo": "-s", "Solo imagenes": "-si",
                "Solo videos y audios": "-sv"}
        a = [tool("whacloud.py")]
        if self.k_action.get() == "Descargar un archivo":
            if not self.k_file.get():
                return messagebox.showwarning("Faltan datos", "Indica el archivo.")
            a += ["-p", self.k_file.get()]
        else:
            a.append(mapa[self.k_action.get()])
        if self.k_out.get():
            a += ["-o", self.k_out.get()]
        self._launch(a)

    # ------------------------------------------------------------------
    #  Ejecucion
    # ------------------------------------------------------------------
    def _emit(self, msg, tag=None):
        self.q.put((msg, tag))

    def _clear(self):
        self.log.delete("1.0", "end")

    def _drain(self):
        """Unico punto que toca la interfaz. Corre en el hilo principal."""
        try:
            while True:
                msg, tag = self.q.get_nowait()
                if tag == "__done__":
                    self._set_busy(False)
                    continue
                self.log.insert("end", msg + "\n", tag or ())
                self.log.see("end")
        except queue.Empty:
            pass
        self.after(120, self._drain)

    def _set_busy(self, busy):
        self.busy = busy
        for b in self.buttons:
            b.configure(state="disabled" if busy else "normal")
        if busy:
            self.progress.start()
        else:
            self.progress.stop()
            self.progress.set(0)

    def _launch_raw(self, argv):
        """Ejecuta una orden completa (ya incluye el interprete)."""
        if self.busy:
            return
        self._set_busy(True)
        self._emit("\n$ " + " ".join(shlex.quote(x) for x in argv), "cmd")
        threading.Thread(target=self._work_raw, args=(argv,), daemon=True).start()

    def _work_raw(self, argv):
        try:
            proc = subprocess.Popen(argv, stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT, text=True,
                                    bufsize=1, encoding="utf-8",
                                    errors="replace",
                                    env=dict(os.environ,
                                             PYTHONIOENCODING="utf-8:replace"))
            for line in proc.stdout:
                line = line.rstrip("\n")
                if line.strip():
                    self._emit(line)
            proc.wait()
            self._emit("[fin] {}".format(
                "OK" if proc.returncode == 0 else
                "codigo {}".format(proc.returncode)),
                "ok" if proc.returncode == 0 else "err")
        except Exception as e:
            self._emit("[e] {}".format(e), "err")
        finally:
            self.q.put(("", "__done__"))

    def _launch(self, argv):
        """Lanza una herramienta de libs/ en un hilo, con lista de argumentos."""
        if self.busy:
            return
        self._set_busy(True)
        self._emit("\n$ python3 " + " ".join(shlex.quote(x) for x in argv), "cmd")
        threading.Thread(target=self._work, args=(argv,), daemon=True).start()

    def _work(self, argv):
        try:
            entorno = dict(os.environ, PYTHONIOENCODING="utf-8:replace")
            proc = subprocess.Popen([sys.executable] + argv,
                                    stdout=subprocess.PIPE,
                                    stderr=subprocess.STDOUT,
                                    cwd=APP_DIR, text=True, bufsize=1,
                                    encoding="utf-8", errors="replace",
                                    env=entorno)
            for line in proc.stdout:
                line = line.rstrip("\n")
                if line.strip():
                    tag = "err" if line.startswith("[e]") else (
                        "ok" if line.startswith("[-]") else None)
                    self._emit(line, tag)
            proc.wait()
            if proc.returncode == 0:
                self._emit("[fin] Proceso terminado correctamente.", "ok")
            else:
                self._emit("[fin] Proceso terminado con codigo {}.".format(
                    proc.returncode), "err")
        except Exception as e:
            self._emit("[e] No se pudo ejecutar: {}".format(e), "err")
        finally:
            self.q.put(("", "__done__"))


if __name__ == "__main__":
    WhapaGUI().mainloop()

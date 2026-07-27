#!/usr/bin/python3
# -*- coding: utf-8 -*-

import os
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import re
import time
import calendar
import whadeps
whadeps.require("pandas", "colorama", tool="whachat")
import whacodes
import whareader
import whareport
whadeps.safe_console()

from colorama import init, Fore
from configparser import ConfigParser
import pandas as pd
import html
import argparse
import time
import sys
import os
import re
import shutil
import random


# Define global variable
arg_user = ""
message = ""
report_var = "None"
report_html = ""
version = "1.55"
names_dict = {}  # names wa.db
color = {}  # participants color
abs_path_file = os.path.abspath(__file__)    # C:\Users\Desktop\whapa\libs\whagodri.py
abs_path = os.path.split(abs_path_file)[0]   # C:\Users\Desktop\whapa\libs\
split_path = abs_path.split(os.sep)[:-1]     # ['C:', 'Users', 'Desktop', 'whapa']
whapa_path = os.path.sep.join(split_path)    # C:\Users\Desktop\whapa

def banner():
    """ Function Banner """
    print(r"""
     __      __.__           _________ .__            __   
    /  \    /  \  |__ _____  \_   ___ \|  |__ _____ _/  |_ 
    \   \/\/   /  |  \\__  \ /    \  \/|  |  \\__  \\   __\
     \        /|   Y  \/ __ \\     \___|   Y  \/ __ \|  |  
      \__/\  / |___|  (____  /\______  /___|  (____  /__|  
           \/       \/     \/        \/     \/     \/     
    ---------------- Whatsapp Chat Exporter -----------------
    """)


def help():
    """ Function show help """
    print("""    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t
    
    Usage: python3 whachat.py -h (for help)
    """)


def report(obj, html, local):
    """ Function that makes the report """

    # Copia los estilos
    try:
        os.makedirs(local + "cfg", exist_ok=True)
        shutil.copy("./cfg/chat.css", local + "cfg/chat.css")
        shutil.copy("./cfg/logo.png", local + "cfg/logo.png")
        shutil.copy("./images/background.png", local + "cfg/background.png")
        shutil.copy("./images/background-index.png", local + "cfg/background-index.png")
        shutil.copy("./images/app_icon.png", local + "cfg/app_icon.png")
        shutil.copy("./images/pdf_icon.png", local + "cfg/pdf_icon.png")
        shutil.copy("./images/vcard_icon.png", local + "cfg/vcard_icon.png")
    except:
        pass

    if report_var == 'EN':
        rep_ini = """<!DOCTYPE html>
<html lang='""" + report_var + """'>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Report makes with Whatsapp Parser Tool">
    <meta name="author" content="B16f00t">
    <link rel="shortcut icon" href="./cfg/logo.png">
    <title>Whatsapp Parser Tool v""" + version + """ Report</title>
    <!-- Bootstrap core CSS -->
    <link href="dist/css/bootstrap.css" rel="stylesheet">
    <!-- Bootstrap theme -->
    <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link href="./cfg/chat.css" rel="stylesheet">
</head>

<style>
table {
font-family: arial, sans-serif;
border-collapse: collapse;
width: 100%;
}
td, th {
border: 1px solid #000000;
text-align: left;
padding: 8px;
}
tr:nth-child(even) {
background-color: #cdcdcd;
}
#map {
    height: 100px;
    width: 100%;
}
</style>

<body background="./cfg/background.png">
<!-- Fixed navbar -->
    <div class="container theme-showcase">
        <div class="header">
            <table style="width:100%">
                <h1 align="left"><img src="./cfg/logo.png" height=128 width=128 align="center">&nbsp;""" + company + """</h1>
                <tr>
                    <th>Record</th>
                    <th>Unit / Company</th> 
                    <th>Examiner</th>
                    <th>Date</th>
                </tr>
                <tr>
                    <td>""" + record + """</td>
                    <td>""" + unit + """</td>
                    <td>""" + examiner + """</td>
                    <td>""" + time.strftime('%d-%m-%Y', time.localtime()) + """</td>
                </tr>
                <tr>
                    <th colspan="4">Notes</th>
                </tr>
                <tr>
                    <td colspan="4">""" + notes + """</td>
                </tr>
            </table>
            <h2 align=center> Chat </h2>
            <h3 align=center> """ + arg_user + """ </h3>
        </div>
        <ul>"""

    elif report_var == 'ES':
        rep_ini = """<!DOCTYPE html>
<html lang='""" + report_var + """'>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Informe creado por WhatsApp Parser Tool">
    <meta name="author" content="B16f00t">
    <link rel="shortcut icon" href="./cfg/logo.png">
    <title>Whatsapp Parser Tool v""" + version + """ Report</title>
    <!-- Bootstrap core CSS -->
    <link href="dist/css/bootstrap.css" rel="stylesheet">
    <!-- Bootstrap theme -->
    <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link href="./cfg/chat.css" rel="stylesheet">
</head>

<style>
table {
font-family: arial, sans-serif;
border-collapse: collapse;
width: 100%;
}
td, th {
border: 1px solid #000000;
text-align: left;
padding: 8px;
}
tr:nth-child(even) {
background-color: #cdcdcd;
}
#map {
    height: 100px;
    width: 100%;
}
</style>

<body  background="./cfg/background.png">
<!-- Fixed navbar -->
    <div class="container theme-showcase">
        <div class="header">
            <table style="width:100%">
                <h1 align="left"><img src="./cfg/logo.png" height=128 width=128 align="center">&nbsp;""" + company + """</h1>
                <tr>
                    <th>Registro</th>
                    <th>Unidad / Compañia</th> 
                    <th>Examinador</th>
                    <th>Fecha</th>
                </tr>
                <tr>
                    <td>""" + record + """</td>
                    <td>""" + unit + """</td>
                    <td>""" + examiner + """</td>
                    <td>""" + time.strftime('%d-%m-%Y', time.localtime()) + """</td>
                </tr>
                <tr>
                    <th colspan="4">Observaciones</th>
                </tr>
                <tr>
                    <td colspan="4">""" + notes + """</td>
                </tr>
            </table>
            <h2 align=center> Conversación </h2>
            <h3 align=center> """ + arg_user + """ </h3>
        </div>
        <ul>"""

    rep_end = """
            <li>
                <div class="bubble_empty">
                </div>
            </li>
        </ul>
    </div>
<!-- /container -->
<!-- Bootstrap core JavaScript
================================================== -->
<!-- Placed at the end of the document so the pages load faster -->
<script src="https://code.jquery.com/jquery-1.10.2.min.js"></script>
<script src="dist/js/bootstrap.min.js"></script>
<script src="docs-assets/js/holder.js"></script>
</body>
</html>
    """

    os.makedirs(os.path.dirname(local), exist_ok=True)
    with open(local + html, 'w', encoding="utf-8", errors="ignore") as f:
        f.write(rep_ini + obj + rep_end)


# ===========================================================================
#  PUENTE AL MOTOR DE INFORMES COMUN
# ===========================================================================
#  Un chat exportado no tiene base de datos, pero si tiene lo esencial: quien,
#  cuando y que. Aqui se traduce el DataFrame al mismo modelo que usa whapa.py,
#  para que los informes salgan identicos: visor interactivo, imprimible,
#  exportacion a CSV y a KML, y los mismos filtros.
#
#  Lo que un chat exportado NO trae, y por tanto no aparece: identificadores de
#  mensaje, mensajes borrados, reacciones, citas ni coordenadas. El informe lo
#  refleja tal cual en vez de inventarlo.

ADJUNTO_RX = re.compile(
    r"<(?:attached|adjunto):\s*([^>]+)>"          # iOS
    r"|^(.+?)\s*\((?:file attached|archivo adjunto)\)",   # Android
    re.IGNORECASE)

CIFRADO_RX = re.compile(
    r"end-to-end encrypted|cifrados de extremo a extremo", re.IGNORECASE)

OMITIDO_RX = re.compile(
    r"<Media omitted>|<Multimedia omitido>|<archivo omitido>", re.IGNORECASE)


def _tipo_por_nombre(nombre):
    """Deduce el tipo a partir del nombre del archivo adjunto."""
    n = (nombre or "").upper()
    ext = os.path.splitext(nombre or "")[1].lower()
    if "-STICKER-" in n or ext == ".webp":
        return whacodes.Kind.STICKER, "Sticker"
    if "-PHOTO-" in n or "-IMG-" in n or ext in (".jpg", ".jpeg", ".png", ".gif", ".bmp"):
        return whacodes.Kind.IMAGE, "Imagen"
    if "-AUDIO-" in n or "-PTT-" in n or ext in (".opus", ".ogg", ".mp3", ".m4a", ".aac", ".wav", ".amr"):
        return whacodes.Kind.AUDIO, "Audio o nota de voz"
    if "-VIDEO-" in n or "-VID-" in n or ext in (".mp4", ".3gp", ".mov", ".mkv", ".avi", ".webm"):
        return whacodes.Kind.VIDEO, "Video"
    if "-GIF-" in n:
        return whacodes.Kind.GIF, "GIF"
    return whacodes.Kind.DOCUMENT, "Documento"


FORMATOS = ["%d/%m/%y %H:%M:%S", "%d/%m/%y %H:%M", "%d/%m/%Y %H:%M:%S",
            "%d/%m/%Y %H:%M", "%m/%d/%y %H:%M:%S", "%m/%d/%y %H:%M",
            "%d.%m.%y %H:%M:%S", "%d.%m.%y %H:%M", "%Y-%m-%d %H:%M:%S"]


def _fecha_a_epoch(fecha, hora, preferido=None):
    """Convierte fecha y hora del chat a epoch UTC probando varios formatos."""
    if fecha is None or hora is None:
        return None
    marca = "{} {}".format(fecha, hora).strip()
    formatos = ([preferido] if preferido else []) + FORMATOS
    for f in formatos:
        if not f:
            continue
        try:
            return int(calendar.timegm(time.strptime(marca, f)))
        except (ValueError, TypeError):
            continue
    return None


def to_extraction(data, user, timeformat, operating_system, chat_name=None,
                  source_file=None):
    """DataFrame de whachat -> whareader.Extraction, para el motor comun."""
    plataforma = whacodes.IOS if operating_system == "ios" else whacodes.ANDROID
    chat_id = chat_name or "chat_exportado"
    mensajes = []
    autores = set()

    for i in data.index:
        autor = str(data["Author"][i]) if data["Author"][i] is not None else ""
        texto = str(data["Message"][i])

        # Fecha. WhatsApp exporta con formatos distintos segun idioma, region
        # y version, asi que se prueba el indicado y despues los habituales:
        # si falla, el mensaje se queda sin fecha, pero NO se pierde.
        ts = _fecha_a_epoch(data["Date"][i], data["Time"][i], timeformat)

        ruta = None
        if CIFRADO_RX.search(texto):
            kind, desc = whacodes.Kind.SYSTEM, "Aviso de cifrado de extremo a extremo"
            autor = ""
        elif OMITIDO_RX.search(texto):
            kind, desc = whacodes.Kind.UNKNOWN, "Archivo no incluido en la exportacion"
        else:
            m = ADJUNTO_RX.search(texto)
            if m:
                ruta = (m.group(1) or m.group(2) or "").strip()
                kind, desc = _tipo_por_nombre(ruta)
            elif not autor:
                kind, desc = whacodes.Kind.SYSTEM, "Mensaje del sistema"
            else:
                kind, desc = whacodes.Kind.TEXT, "Mensaje de texto"

        if autor:
            autores.add(autor)

        mensajes.append(whareader.Message(
            row_id=int(i) + 1, chat_id=chat_id,
            from_me=(autor == user), sender=autor or None, timestamp=ts,
            kind=kind, type_desc=desc, raw_type=None,
            text=texto, key_id=None, media_path=ruta,
            system_action=desc if kind is whacodes.Kind.SYSTEM else None,
            platform=plataforma))

    contactos = {chat_id: whareader.Contact(jid=chat_id,
                                            display_name=chat_name or "Chat exportado")}
    origenes = []
    if source_file and os.path.exists(source_file):
        origenes.append({"name": os.path.basename(source_file),
                         "size": os.path.getsize(source_file),
                         "sha256": whareader.sha256_file(source_file)})

    ext = whareader.Extraction(platform=plataforma, messages=mensajes,
                               contacts=contactos, source_files=origenes)
    ext.participants = sorted(autores)
    return ext


def informes(ext, salida, lang="ES", flt=None, media_root=None,
             copy_media=False, interactivo=True, imprimible=False,
             csv_out=False, titulo="Informe de chat exportado"):
    """Genera los mismos informes que whapa.py a partir de un chat exportado."""
    hechos = []
    os.makedirs(salida, exist_ok=True)
    if interactivo:
        destino = os.path.join(salida, "report")
        r = whareport.build_report(ext, destino, title=titulo, lang=lang, flt=flt,
                                   media_root=media_root, copy_media=copy_media)
        hechos.append(("interactivo", r))
    if imprimible:
        destino = os.path.join(salida, "report_print.html")
        r = whareport.build_printable(ext, destino, title=titulo, flt=flt,
                                      media_root=media_root, copy_media=copy_media)
        hechos.append(("imprimible", r))
    if csv_out:
        destino = os.path.join(salida, "messages.csv")
        whareport.export_csv(whareport.search(ext, flt or whareport.Filter()), destino)
        hechos.append(("csv", {"path": destino}))
    return hechos


def system_slash(string):
    """ Change / or \\ depend on the OS"""

    if sys.platform == "win32" or sys.platform == "win64" or sys.platform == "cygwin":
        return string.replace("/", "\\")

    else:
        return string.replace("\\", "/")


def get_configs():
    """ Function that gets report config"""
    global company, record, unit, examiner, notes
    config_report = ConfigParser()
    try:
        cfg_file = system_slash(r'{}/cfg/settings.cfg'.format(whapa_path))
        config_report.read(cfg_file)
        company = config_report.get('report', 'company')
        record = config_report.get('report', 'record')
        unit = config_report.get('report', 'unit')
        examiner = config_report.get('report', 'examiner')
        notes = config_report.get('report', 'notes')
    except Exception as e:
        print("The 'settings.cfg' file is missing or corrupt!")


def startsWithDateTimeiOS(s):
    pattern = r"^\[([0-9]*[/.][0-9]*[/.][0-9]*\W*[0-9]*.[0-9]*.[0-9]*)\]"  # [25/8/20, 19:52:23]
    result = re.match(pattern, s)
    if result:
        return True
    return False


def startsWithDateTimeAndroid(s):
    # pattern = "^([0-9]*/[0-9]*/[0-9]*\W*[0-9]*.[0-9]*.[0-9]*)-"  # 24/5/18 14:25 -
    pattern = r"^([0-9]*[/.][0-9]*[/.][0-9]*\W*[0-9]*.[0-9]*.[0-9]*) -" # 24.07.21, 10:15 -
    result = re.match(pattern, s)
    if result:
        return True
    return False


def startsWithAuthor(s):
    patterns = [
        r'([\w]+):',  # First Name
        r'([\w]+[\s]+[\w]+):',  # First Name + Last Name
        r'([\w]+[\s]+[\w]+[\s]+[\w]+):',  # First Name + Middle Name + Last Name
        r'([\w]+[\s]+[\w]+[\s]+[\w]+[\s]+[\w]+):',  # First Name + Middle Name + Last Name + other thing
        r'([\w]+[\s]+[\w]+[\s]+[\w]+[\s]+[\w]+[\s]+[\w]+):',  # First Name + Middle Name + Last Name + other thing + pufff
        r'(\W.*):'  # PhoneNumber
    ]
    pattern = '^' + '|'.join(patterns)
    result = re.match(pattern, s)
    if result:
        return True
    return False


def getDataPointiOS(line):
    # IOs - line = [25/8/20, 10:02:14] Jordi Subinspector Tecnologicos: Por qué no vieron los maniquiey
    splitLine = line.split('] ', 1)  # splitLine = '[25/8/20, 10:02:14', 'Jordi Subinspector Tecnologicos: Por qué no vieron los maniquiey']
    dateTime = splitLine[0].replace("[", "")  # dateTime = '25/8/20, 10:02:14'
    try:
        date, time = dateTime.split(', ')  # date = '25/8/20'; time = '10:02:14' # English mobile
    except:
        date, time = dateTime.split(' ')  # date = '25/8/20'; time = '10:02:14' # Spanish mobile

    message = ' '.join(splitLine[1:])  # message = 'Jordi Subinspector Tecnologicos: Por qué no vieron los maniquiey'
    if startsWithAuthor(message):  # True
        splitMessage = message.split(': ', 1)  # splitMessage = ['Jordi Subinspector Tecnologicos', 'Por qué no vieron los maniquiey']
        author = splitMessage[0]  # author = 'Jordi Subinspector Tecnologicos'
        message = ' '.join(splitMessage[1:])  # message = 'Por qué no vieron los maniquiey'
    else:
        author = None
    return date, time, author, message


def getDataPointAndroid(line):
    # Android - line = 23/5/18 15:24 - Sergio F: No se tío no le preguntao al final
    splitLine = line.split(' - ')  # splitLine = ['23/5/18 15:24', 'Sergio F: No se tío no le preguntao al final']
    dateTime = splitLine[0]  # dateTime = '23/5/18 15:24'                       / 24.07.21, 10:15
    try:
        date, time = dateTime.split(', ')  # date = '23/5/18'; time = '15:24' #  Unknow mobile
    except:
        date, time = dateTime.split(' ')  # date = '23/5/18'; time = '15:24' # English mobile

    message = ' '.join(splitLine[1:])  # message = 'Sergio F: No se tío no le preguntao al final'
    if startsWithAuthor(message):  # True
        splitMessage = message.split(': ')  # splitMessage = ['Sergio F', 'No se tío no le preguntao al final']
        author = splitMessage[0]  # author = 'Sergio F'
        message = ' '.join(splitMessage[1:])  # message = 'No se tío no le preguntao al final'
    else:
        author = None
    return date, time, author, message


def getDataFrame(conversationPath, operating_system):
    """ Extrqact information from the log """

    try:
        parsedData = []
        with open(conversationPath, encoding="utf-8", errors='ignore') as fp:
            messageBuffer = []  # Buffer to capture intermediate output for multi-line messages
            date, time, author = None, None, None  # Intermediate variables to keep track of the current message being processed
            while True:
                line = fp.readline()
                line = line.replace(u'\u200e', '')
                if not line:  # Stop reading further if end of file has been reached
                    parsedData.append([date, time, author, ' '.join(messageBuffer)])
                    break
                line = line.strip()  # Guarding against erroneous leading and trailing whitespaces
                if operating_system == "ios":
                    if startsWithDateTimeiOS(line):  # If a line starts with a Date Time pattern, then this indicates the beginning of a new message
                        if len(messageBuffer) > 0:  # Check if the message buffer contains characters from previous iterations
                            parsedData.append([date, time, author, ' '.join(messageBuffer)])  # Save the tokens from the previous message in parsedData

                        messageBuffer.clear()  # Clear the message buffer so that it can be used for the next message
                        date, time, author, message = getDataPointiOS(line)  # Identify and extract tokens from the line
                        messageBuffer.append(message)  # Append message to buffer
                    else:
                        messageBuffer.append(line)  # If a line doesn't start with a Date Time pattern, then it is part of a multi-line message. So, just append to buffer

                elif operating_system == "android":
                    if startsWithDateTimeAndroid(line):  # If a line starts with a Date Time pattern, then this indicates the beginning of a new message
                        if len(messageBuffer) > 0:  # Check if the message buffer contains characters from previous iterations
                            parsedData.append([date, time, author, ' '.join(messageBuffer)])  # Save the tokens from the previous message in parsedData

                        messageBuffer.clear()  # Clear the message buffer so that it can be used for the next message
                        date, time, author, message = getDataPointAndroid(line)  # Identify and extract tokens from the line
                        messageBuffer.append(message)  # Append message to buffer
                    else:
                        messageBuffer.append(line)  # If a line doesn't start with a Date Time pattern, then it is part of a multi-line message. So, just append to buffer

        df = pd.DataFrame(parsedData, columns=['Date', 'Time', 'Author', 'Message'])
        return df
    except Exception as e:
        print("[e] Error getting participants. Choose another operating system.")
        exit()


def getAttachediOS(message):
    pattern = ".*<attached: (.*)>|.*<adjunto: (.*)>"    #.*<adjunto: (.*)>
    result = re.match(pattern, message)
    if result:
        file = result.group(1)
        if not file:
            file = result.group(2)

        if re.match(".*-PHOTO-.*", file):
            if (report_var == 'EN') or (report_var == 'ES'):
                message = file + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='" + file + " 'width=\"100\" height=\"100\"/></a>"

        elif re.match(".*-AUDIO-.*", file):
            if (report_var == 'EN') or (report_var == 'ES'):
                message = file + '</br><audio controls> <source src="' + file + ' "</audio>'

        elif re.match(".*-VIDEO-.*", file):
            if (report_var == 'EN') or (report_var == 'ES'):
                message = file + '</br><video width="300" height="150" controls> <source src="' + file + ' "</video>'

        elif re.match(".*-STICKER-.*", file):
            message = file + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='" + file + " 'width=\"100\" height=\"100\"/></a>"

        elif re.match(".*-GIF-.*", file):
            message = file + '</br><video width="150" height="150" controls> <source src="' + file + ' "</video>'

        else:
            fileName, fileExtension = os.path.splitext(file)
            if fileExtension == ".vcf":
                # Parsear vcf
                message = file + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='./cfg/vcard_icon.png' width=\"100\" height=\"100\"/></a>"
            elif fileExtension == ".pdf":
                file_filter = (result.group(0).split('<attached')[0])
                message = file_filter + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='./cfg/pdf_icon.png' width=\"100\" height=\"100\"/></a>"
            else:
                message = file + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='./cfg/app_icon.png' width=\"100\" height=\"100\"/></a>"

        return message

    pattern = ".*Location:.*q=(.*)|.*Ubicación:.*q=(.*)"
    result = re.match(pattern, message)
    if result:
        file = result.group(1)
        if not file:
            file = result.group(2)

        location = file.split(",")
        lon = str(location[0])
        lat = str(location[1])
        if (report_var == 'EN') or (report_var == 'ES'):
            try:
                message = "<br> " + message.split('Location:')[1] + "</br><iframe width='300' height='150' id='gmap_canvas' src='https://maps.google.com/maps?q={}%2C{}&t=&z=15&ie=UTF8&iwloc=&output=embed' frameborder='0' scrolling='no' marginheight='0' marginwidth='0'></iframe>".format(lon, lat)
            except:
                message = "<br> " + message.split('Ubicación:')[1] + "</br><iframe width='300' height='150' id='gmap_canvas' src='https://maps.google.com/maps?q={}%2C{}&t=&z=15&ie=UTF8&iwloc=&output=embed' frameborder='0' scrolling='no' marginheight='0' marginwidth='0'></iframe>".format(lon, lat)

        return message

    return html.escape(message)


def getAttachedAndroid(message):
    pattern = r"(.*) \(attached file\)|(.*) \(archivo adjunto\)"
    result = re.match(pattern, message)
    if result:
        file = result.group(1)
        if not file:
            file = result.group(2)

        if re.match("IMG-.*", file):
            if (report_var == 'EN') or (report_var == 'ES'):
                message = file + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='" + file + " 'width=\"100\" height=\"100\"/></a>"

        elif re.match("PTT-.*", file):
            if (report_var == 'EN') or (report_var == 'ES'):
                message = file + '</br><audio controls> <source src="' + file + ' "</audio>'

        elif re.match("VID-.*", file):
            if (report_var == 'EN') or (report_var == 'ES'):
                message = file + '</br><video width="300" height="150" controls> <source src="' + file + ' "</video>'

        elif re.match("STK-.*", file):
            message = file + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='" + file + " 'width=\"100\" height=\"100\"/></a>"

        elif re.match("GIF-.*", file):
            message = file + '</br><video width="150" height="150" controls> <source src="' + file + ' "</video>'

        else:
            fileName, fileExtension = os.path.splitext(file)
            if fileExtension == ".vcf":
                # Parsear vcf
                message = file + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='./cfg/vcard_icon.png' width=\"100\" height=\"100\"/></a>"
            elif fileExtension == ".pdf":
                file_filter = (result.group(0).split('<attached')[0])
                message = file_filter + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='./cfg/pdf_icon.png' width=\"100\" height=\"100\"/></a>"
            else:
                message = file + "</br><a href=\"" + file + "\" target=\"_blank\"> <IMG SRC='./cfg/app_icon.png' width=\"100\" height=\"100\"/></a>"

        return message

    pattern = ".*location.*q=(.*)|.*ubicación.*q=(.*)"
    result = re.match(pattern, message)

    if result:
        file = result.group(1)
        if not file:
            file = result.group(2)
        location = file.split(",")
        lon = str(location[0])
        lat = str(location[1])
        if (report_var == 'EN') or (report_var == 'ES'):
            try:
                message = "<br> " + message.split('location')[1] + "</br><iframe width='300' height='150' id='gmap_canvas' src='https://maps.google.com/maps?q={}%2C{}&t=&z=15&ie=UTF8&iwloc=&output=embed' frameborder='0' scrolling='no' marginheight='0' marginwidth='0'></iframe>".format(lon, lat)
            except:
                message = "<br> " + message.split('ubicación')[1] + "</br><iframe width='300' height='150' id='gmap_canvas' src='https://maps.google.com/maps?q={}%2C{}&t=&z=15&ie=UTF8&iwloc=&output=embed' frameborder='0' scrolling='no' marginheight='0' marginwidth='0'></iframe>".format(lon, lat)

        return message

    return html.escape(message)


def messages(data, user, recipient, report_html, local, time_start, time_end, timeformat, operating_system):
    """ Function that show database messages """

    rep_med = ""  # Saves the complete chat
    rows = len(data.index)
    for i in data.index:
        try:
            report_msj = ""  # Saves each message
            report_name = ""  # Saves the chat sender
            message = ""  # Saves each msg
            sys.stdout.write("\rMessage {}/{}".format(str(i+1), str(rows)))
            sys.stdout.flush()
            # transform chat time in epoch local time
            time_parse = str(data['Date'][i]) + " " + str(data['Time'][i])
            utc_time = time.strptime(time_parse, timeformat)
            dt = time.mktime(utc_time)
            if time_start <= dt <= time_end:
                sender = str(data['Author'][i])
                if operating_system == "ios":
                    text = getAttachediOS(str(data['Message'][i]))
                else:
                    text = getAttachedAndroid(str(data['Message'][i]))

                if ("Los mensajes y las llamadas están cifrados de extremo a extremo. Nadie fuera de este chat, ni siquiera WhatsApp, puede leerlos ni escucharlos"
                    "" in text) or ("Messages and calls are end-to-end encrypted. No one outside of this chat, not even WhatsApp, can read or listen to them") in text:
                    sender = "None"
                if sender == user:
                    # The owner post a message
                    if (report_var == 'EN') or (report_var == 'ES'):
                        report_name = user
                    else:
                        message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                        message += Fore.GREEN + "From " + Fore.RESET + user + Fore.GREEN + " to " + Fore.RESET + recipient + "\n"

                elif sender == "None":
                    # The system post a message
                    if report_var == 'EN':
                        report_name = "System Message"
                    elif report_var == 'ES':
                        report_name = "Mensaje de Sistema"
                    else:
                        message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                        message += Fore.GREEN + "From " + Fore.RESET + "System\n"

                else:
                    # Other user post a message
                    if (report_var == 'EN') or (report_var == 'ES'):
                        report_name = "<font color='{}'> {} </font>".format(color.get(sender), sender)
                    else:
                        message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                        message += Fore.GREEN + "From " + Fore.RESET + sender + Fore.GREEN + " to" + Fore.RESET + " Me\n"

                if (report_var == 'EN') or (report_var == 'ES'):
                    report_msj += text
                else:
                    message += Fore.GREEN + "Message: " + Fore.RESET + html.unescape(text) + "\n"

                report_time = "{} - {}".format(str(data['Date'][i]), str(data['Time'][i]))
                if (report_var == 'EN') or (report_var == 'ES'):
                    if report_name == user:
                        rep_med += """
                <li>
                    <div class="bubble2">
                        <span class="personName2">""" + report_name + """</span><br>
                        <span class="personSay2">""" + report_msj + """</span><br>
                        <span class="time round2">""" + report_time + "&nbsp" + """</span><br>
                    </div>
                </li>"""
                    elif (report_name == "System Message") or (report_name == "Mensaje de Sistema"):
                        rep_med += """
                <li>
                    <div class="bubble-system"> 
                        <span class="time-system round">""" + report_time + "&nbsp" + """</span><br>
                        <span class="person-System">""" + report_msj + """</span><br>
                    </div>
                </li>"""
                    else:
                        rep_med += """
                <li>
                    <div class="bubble"> 
                        <span class="personName">""" + report_name + """</span><br>
                        <span class="personSay">""" + report_msj + """</span><br>
                        <span class="time round">""" + report_time + "&nbsp" + """</span><br>
                    </div>
                </li>"""
                elif report_var == 'None':
                    message += Fore.GREEN + "Timestamp: " + Fore.RESET + report_time + "\n"
                    print(message)

        except Exception as e:
            print("\nError showing message details: {}, Message ID {}, Timestamp {}".format(e, str(i), data['Date'][i] + ", " + data['Time'][i]))

        if report_var != "None":
            report(rep_med, report_html, local)


def participants_color(users):
    """ Function saves all participant in an group and it assign a colour"""
    for i in users:
        hexcolor = ["#FF0000", "#000000", "#5586e5", "#800000", "#00008B", "#006400", "#800080", "#8B4513", "#FF4500", "#2F4F4F", "#DC143C",
                     "#696969", "#008B8B", "#D2691E", "#CD5C5C", "#4682B4"]
        color[i] = random.choice(hexcolor)

    return color


#  Initializing
if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="To start unzip the Chat .zip file, if it includes medias")
    parser.add_argument('chat_file', help='Input the chat file')
    parser.add_argument("-p", "--participants", help="Get a chat participant list", action="store_true")
    parser.add_argument("-u", "--user", help="Choose the recipient user to start parsing")
    parser.add_argument("-s", "--system", help='Choose operating system \'Android\' or \'iOS\'.', const='android', nargs='?', choices=['android', 'ios'])
    parser.add_argument("-r", "--report", help='Make an html report in \'English\' or \'Spanish\'.', const='EN', nargs='?', choices=['EN', 'ES'])
    parser.add_argument("-f", "--format", help='Type a date-time mask "%%d/%%m/%%y %%H:%%M:%%S"', nargs='?')
    parser.add_argument("-ts", "--time_start", help="Show messages by start time (dd-mm-yyyy HH:MM)")
    parser.add_argument("-te", "--time_end", help="Show messages by end time (dd-mm-yyyy HH:MM)")
    parser.add_argument("-o", "--output", help="Output path for the reports")
    parser.add_argument("-pr", "--print_report", action="store_true",
                        help="Make a printable html report (paper / PDF)")
    parser.add_argument("-x", "--csv", action="store_true",
                        help="Export the messages to CSV")
    parser.add_argument("-mp", "--media_path",
                        help="Folder with the exported attachments, so the report "
                             "can show images and play audio/video "
                             "(usually the same folder as the chat file)")
    parser.add_argument("-cm", "--copy_media", action="store_true",
                        help="Copy the attachments into the report folder")
    parser.add_argument("-t", "--text", help="Show messages by text match")
    parser.add_argument("-re", "--regex", action="store_true",
                        help="Treat -t as a regular expression")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        help()

    else:
        init()
        path, file = os.path.split(args.chat_file)
        local = path + "/"
        conversationPath = args.chat_file
        report_var = "None"
        mobileOS = args.system
        epoch_start = 0.0
        epoch_end = time.time()
        if mobileOS == "ios":
            timeformat = "%d/%m/%y %H:%M:%S"

        elif mobileOS == "android":
            timeformat = "%d/%m/%y %H:%M"

        if args.format:
            timeformat = args.format

        if args.participants:
            dataframe = getDataFrame(conversationPath, mobileOS)
            participants = dataframe["Author"].unique().tolist()
            with open(local + '/participants.txt', 'w') as file_w:
                for i in participants:
                    if i is not None:
                        print(i)
                        file_w.write(i + "\n")
            exit()

        if args.user:
            if args.time_start:
                epoch_start = float(time.mktime(time.strptime(args.time_start, '%d-%m-%Y %H:%M')))

            if args.time_end:
                epoch_end = float(time.mktime(time.strptime(args.time_end, '%d-%m-%Y %H:%M')))

            if args.report:
                report_var = args.report
                get_configs()

            user = args.user
            dataframe = getDataFrame(conversationPath, mobileOS)

            # Get the name of the group or user
            i = 0
            while True:
                if dataframe.loc[i]['Author']:
                    recipient = dataframe.loc[i]['Author']
                    print(recipient)
                    break
                i += 1

            # Assign the report name
            if mobileOS == "ios":
                report_name = recipient

            elif mobileOS == "android":
                path, file = os.path.split(conversationPath)
                report_name, extension = os.path.splitext(file)

            # Get the full list of participants
            participants = dataframe["Author"].unique().tolist()
            final = []
            for i in participants:
                if i is not None:
                    final.append(i)

            color = participants_color(final)
            if report_var == 'EN':
                report_html = "report_" + report_name + ".html"

            elif report_var == 'ES':
                report_html = "informe_" + report_name + ".html"

            print("\nNumber of messages: {}".format(len(dataframe.index)))
            print(Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET)
            print(Fore.CYAN + "CHAT " + arg_user + Fore.RESET)
            if args.report or args.print_report or args.csv:
                # Mismo motor de informes que whapa.py
                # Sin -o, el informe va junto al chat analizado, que es donde
                # el usuario lo espera. Nunca dentro de libs/.
                salida = args.output or os.path.join(
                    os.path.dirname(os.path.abspath(conversationPath)),
                    "report_whachat")
                salida = os.path.abspath(salida)
                nombre_chat = os.path.splitext(os.path.basename(conversationPath))[0]
                ext = to_extraction(dataframe, user, timeformat, mobileOS,
                                    chat_name=nombre_chat,
                                    source_file=conversationPath)
                flt = whareport.Filter(
                    text=args.text, regex=args.regex,
                    date_from=epoch_start if epoch_start > 0 else None,
                    date_to=epoch_end if epoch_end < 9999999999 else None)
                media = args.media_path or os.path.dirname(
                    os.path.abspath(conversationPath))
                hechos = informes(ext, salida,
                                  lang=(args.report or "ES"),
                                  flt=flt, media_root=media,
                                  copy_media=args.copy_media,
                                  interactivo=bool(args.report),
                                  imprimible=args.print_report,
                                  csv_out=args.csv,
                                  titulo="Chat exportado - " + nombre_chat)
                s = ext.summary()
                print("\n[i] {} mensajes - {} participantes".format(
                    s["total"], len(getattr(ext, "participants", []))))
                for clase, r in hechos:
                    print("[-] Informe {}: {}".format(clase, r["path"]))
                    if r.get("media_found") is not None:
                        print("    Adjuntos: {} localizados, {} no encontrados".format(
                            r["media_found"], r["media_missing"]))
            else:
                messages(dataframe, user, recipient, report_html, local, epoch_start, epoch_end, timeformat, mobileOS)
            print("\n[i] Finished")

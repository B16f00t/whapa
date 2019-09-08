    #!/usr/bin/python3
# -*- coding: utf-8 -*-

from colorama import init, Fore
from configparser import ConfigParser
import html
import distutils.dir_util
import argparse
import sqlite3
import os
import time
import sys
import random

# Define global variable
arg_user = ""
arg_group = ""
message = ""
report_var = "None"
report_html = ""
report_group = ""
version = "1.0"
names_dict = {}            # names wa.db
color = {}                 # participants color
current_color = "#5586e5"  # default participant color


def banner():
    """ Function Banner """
    print("""
     __      __.__          __________         
    /  \    /  \  |__ _____ \______   \_____   
    \   \/\/   /  |  \\\\__  \ |     ___/\__  \  
     \        /|   Y  \/ __ \|    |     / __ \_
      \__/\  / |___|  (____  /____|    (____  /
           \/       \/     \/               \/ 
    ---------- Whatsapp Parser v""" + version + """ -----------
    """)


def help():
    """ Function show help """
    print("""    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t
    
    Usage: python3 whapa.py -h (for help)
    """)


def db_connect(db):
    """ Function connect to Database"""
    if os.path.exists(db):
        try:
            with sqlite3.connect(db) as conn:
                global cursor
                cursor = conn.cursor()
                cursor_rep = conn.cursor()
            print("msgstore.db connected\n")
            return cursor, cursor_rep
        except Exception as e:
            print("Error connecting to Database, ", e)
    else:
        print("msgstore.db doesn't exist")
        exit()


def status(st):
    """ Function message status"""
    if st == 0 or st == 5:  # 0 for me and 5 for target
        return "Received", "&#10004;&#10004;"
    elif st == 4:
        return Fore.RED + "Waiting in server" + Fore.RESET, "&#10004;"
    elif st == 6:
        return Fore.YELLOW + "System message" + Fore.RESET, "&#128187;"
    elif st == 8 or st == 10:
        return Fore.BLUE + "Audio played" + Fore.RESET, "<font color=\"#0000ff \">&#10004;&#10004;;</font>"   # 10 for me and 8 for target
    elif st == 13 or st == 12:
        return Fore.BLUE + "Seen" + Fore.RESET, "<font color=\"#0000ff \">&#10004;&#10004;</font>"
    else:
        return str(st), ""


def size_file(obj):
    """ Function objects size"""
    if obj > 1048576:
        obj = "(" + "{0:.2f}".format(obj / float(1048576)) + " MB)"
    else:
        obj = "(" + "{0:.2f}".format(obj / float(1024)) + " KB)"
    return obj


def duration_file(obj):
    """ Function duration tiMe"""
    hour = (int(obj / 3600))
    minu = int((obj - (hour * 3600)) / 60)
    seco = obj - ((hour * 3600) + (minu * 60))
    if obj >= 3600:
        obj = (str(hour) + "h " + str(minu) + "m " + str(seco) + "s")
    elif 60 < obj < 3600:
        obj = (str(minu) + "m " + str(seco) + "s")
    else:
        obj = (str(seco) + "s")
    return obj


def names(obj):
    """ Function saves a name list if exits wa.db"""
    # global names_dict
    # names_dict = {}  # jid : display_name
    if os.path.exists(obj):
        try:
            with sqlite3.connect(obj) as conn:
                cursor_name = conn.cursor()
                sql_names = "SELECT jid, display_name FROM wa_contacts"
                sql_names = cursor_name.execute(sql_names)
                print("wa.db connected")

                try:
                    for data in sql_names:
                        names_dict.update({data[0]: data[1]})
                except Exception as e:
                    print("Error adding items in the dictionary:", e)
        except Exception as e:
            print("Error connecting to Database, ", e)
    else:
        print("wa database doesn't exist")


def gets_name(obj):
    """ Function recover a name of the wa.db"""
    if names_dict == {}:  # No exists wa.db
        return " "
    else:  # Exists Wa.db
        if type(obj) is list:  # It's a list
            list_broadcast = []
            for i in obj:
                b = i + "@s.whatsapp.net"
                if b in names_dict:
                    if names_dict[b] is not None:
                        list_broadcast.append(names_dict[b])
                    else:
                        list_broadcast.append(i)
                else:
                    list_broadcast.append(i)
            return " (" + ", ".join(list_broadcast) + ")"
        else:  # It's a string
            if obj in names_dict:
                if names_dict[obj] is not None:
                    return " (" + names_dict[obj] + ")"
                else:
                    return ""
            else:
                return ""


def participants(obj):
    """ Function saves all participant in an group or broadcast"""
    sql_string_group = "SELECT jid, admin FROM group_participants WHERE gjid='" + str(obj) + "'"
    sql_consult_group = cursor.execute(sql_string_group)
    report_group = ""
    for i in sql_consult_group:
        if i[0]:  # Others
            hexcolor = ["#800000", "#00008B", "#006400", "#800080", "#8B4513", "#FF4500", "#2F4F4F", "#DC143C", "#696969", "#008B8B", "#D2691E", "#CD5C5C", "#4682B4"]
            color[i[0].split("@")[0]] = random.choice(hexcolor)
            global current_color
            current_color = color.get(i[0].split("@")[0])

            if i[1] and i[1] == 0:  # User
                if report_var == 'EN' or report_var == 'ES':
                    report_group += "<font color=\"{}\"> {} </font>, ".format(current_color, i[0].split("@")[0] + gets_name(i[0]))
                else:
                    report_group += i[0].split("@")[0] + " " + Fore.YELLOW + gets_name(i[0]) + Fore.RESET + ", "
            elif i[1] and i[1] > 0:  # Admin
                if report_var == 'EN' or report_var == 'ES':
                    report_group += "<font color=\"{}\"> {} </font> ***Admin***, ".format(current_color, i[0].split("@")[0] + gets_name(i[0]))

                else:
                    report_group += i[0].split("@")[0] + Fore.YELLOW + gets_name(i[0]) + Fore.RESET + Fore.RED + "(Admin)" + Fore.RESET + ", "
            else:
                if report_var == 'EN' or report_var == 'ES':
                    report_group += "<font color=\"{}\"> {} </font>, ".format(current_color, i[0].split("@")[0] + gets_name(i[0]))
                else:
                    report_group += i[0].split("@")[0] + " " + Fore.YELLOW + gets_name(i[0]) + Fore.RESET + ", "
        else:  # Me
            current_color = "#000000"
            if i[1] and i[1] == 0:  # User
                if report_var == 'EN':
                    report_group += "Phone user, "
                elif report_var == 'ES':
                    report_group += "Usuario del teléfono, "
                else:
                    report_group += "Me, "
            elif i[1] and i[1] > 0:  # Admin
                if report_var == 'EN':
                    report_group += "<font color='{}'> Phone user </font> *** Admin ***, ".format(current_color)
                elif report_var == 'ES':
                    report_group += "<font color='{}'> Usuario del teléfono </font> *** Admin ***, ".format(current_color)
                else:
                    report_group += "Me" + Fore.RED + " (Admin)" + Fore.RESET + ", "
            else:  # Broadcast no user, no admin
                if report_var == 'EN':
                    report_group += "<font color='{}'> Phone user </font>, ".format(current_color)
                elif report_var == 'ES':
                    report_group += "<font color='{}'> Usuario del teléfono </font>, ".format(current_color)
                else:
                    report_group += "Me, "

    if (report_var == 'EN') or (report_var == 'ES'):
        report_group = "<p style = 'border: 2px solid #CCCCCC; padding: 10px; background-color: #CCCCCC; color: black; font-family: arial,helvetica; font-size: 14px; font-weight: bold;'> " + report_group[:-2] + " </p>"

    return report_group, color


def report(obj, html):
    """ Function that makes the report """
    if report_var == 'EN':
        rep_ini = """<!DOCTYPE html>
<html lang='""" + report_var + """'>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Report makes with Whatsapp Parser Tool">
    <meta name="author" content="B16f00t">
    <link rel="shortcut icon" href="../images/logo.png">
    <title>Whatsapp Parser Tool v""" + version + """ Report</title>
    <!-- Bootstrap core CSS -->
    <link href="dist/css/bootstrap.css" rel="stylesheet">
    <!-- Bootstrap theme -->
    <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link href="../cfg/chat.css" rel="stylesheet">
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

<body background="../images/background.png">
<!-- Fixed navbar -->
    <div class="container theme-showcase">
        <div class="header">
            <table style="width:100%">
                <h1 align="left"><img src='.""" + logo + """' height=128 width=128 align="center">&nbsp;""" + company + """</h1>
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
            <h3 align=center> """ + arg_group + gets_name(arg_group) + arg_user + gets_name(arg_user + "@s.whatsapp.net") + """ </h3>
            """ + report_group + """
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
    <link rel="shortcut icon" href="../images/logo.png">
    <title>Whatsapp Parser Tool v""" + version + """ Report</title>
    <!-- Bootstrap core CSS -->
    <link href="dist/css/bootstrap.css" rel="stylesheet">
    <!-- Bootstrap theme -->
    <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link href="../cfg/chat.css" rel="stylesheet">
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

<body  background="../images/background.png">
<!-- Fixed navbar -->
    <div class="container theme-showcase">
        <div class="header">
            <table style="width:100%">
                <h1 align="left"><img src='.""" + logo + """' height=128 width=128 align="center">&nbsp;""" + company + """</h1>
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
            <h3 align=center> """ + arg_group + gets_name(arg_group) + arg_user + gets_name(arg_user + "@s.whatsapp.net") + """ </h3>
            """ + report_group + """
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

    if os.path.isfile("./reports") is False:
        distutils.dir_util.mkpath("./reports")

    f = open(html, 'w', encoding="utf-8")
    f.write(rep_ini + obj + rep_end)
    f.close()


def index_report(obj, html):
    """ Function that makes the index report """
    if report_var == "ES":
        rep_ini = """<!DOCTYPE html>
<html lang='""" + report_var + """'>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Informe realizado con Whatsapp Parser Tool">
    <meta name="author" content="B16f00t">
    <link rel="shortcut icon" href="../cfg/logo.png">
    <title>Whatsapp Parser Tool v""" + version + """ Report Index</title>
    <!-- Bootstrap core CSS -->
    <link href="dist/css/bootstrap.css" rel="stylesheet">
    <!-- Bootstrap theme -->
    <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link href="../cfg/chat.css" rel="stylesheet">
</head>
    
<style>
table {
font-family: arial, sans-serif;
border-collapse: collapse;
width: 100%;
}
td, th {
border: 1px solid #dddddd;
text-align: left;
padding: 8px;
}
tr:nth-child(even) {
background-color: #dddddd;
}
#map {
    height: 100px;
    width: 100%;
}
</style>
    
<body  background="../images/background-index.png">
    <!-- Fixed navbar -->
        <div class="containerindex theme-showcase">
            <h1 align="left"><img src='.""" + logo + """' height=128 width=128 align="center">&nbsp;""" + company + """</h1>
            <h2 align=center> Listado de conversaciones </h2>
            <div class="header">
                <table style="width:100%">
                    """ + obj + """
                </table>
            </div>
        </div>
<!-- /container -->
<!-- Bootstrap core JavaScript
    ================================================== -->
<!-- Placed at the end of the document so the pages load faster -->
<script src="https://code.jquery.com/jquery-1.10.2.min.js"></script>
<script src="dist/js/bootstrap.min.js"></script>
<script src="docs-assets/js/holder.js"></script>
</body>
</html>"""

    elif report_var == "EN":
        rep_ini = """<!DOCTYPE html>
<html lang='""" + report_var + """'>

<head>
    <meta charset="utf-8">
    <meta http-equiv="X-UA-Compatible" content="IE=edge">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <meta name="description" content="Report makes with Whatsapp Parser Tool">
    <meta name="author" content="B16f00t">
    <link rel="shortcut icon" href="../images/logo.png">
    <title>Whatsapp Parser Tool v""" + version + """ Report Index</title>
    <!-- Bootstrap core CSS -->
    <link href="dist/css/bootstrap.css" rel="stylesheet">
    <!-- Bootstrap theme -->
    <link href="dist/css/bootstrap-theme.min.css" rel="stylesheet">
    <!-- Custom styles for this template -->
    <link href="../cfg/chat.css" rel="stylesheet">
</head>

<style>
table {
font-family: arial, sans-serif;
border-collapse: collapse;
width: 100%;
}
td, th {
border: 1px solid #dddddd;
text-align: left;
padding: 8px;
}
tr:nth-child(even) {
background-color: #dddddd;
}
#map {
    height: 100px;
    width: 100%;
}
</style>

<body>
<!-- Fixed navbar -->
    <div class="containerindex theme-showcase">
        <h1 align="left"><img src=.""" + logo + """ height=128 width=128 align="center">&nbsp;""" + company + """</h1>
        <h2 align=center>  Chats list </h2>
        <div class="header">
            <table style="width:100%">
            """ + obj + """
            </table>
        </div>
    </div>
<!-- /container -->
<!-- Bootstrap core JavaScript
    ================================================== -->
<!-- Placed at the end of the document so the pages load faster -->
<script src="https://code.jquery.com/jquery-1.10.2.min.js"></script>
<script src="dist/js/bootstrap.min.js"></script>
<script src="docs-assets/js/holder.js"></script>
</body>
</html>"""

    if os.path.isfile("./reports") is False:
        distutils.dir_util.mkpath("./reports")

    f = open(html, 'w', encoding="utf-8")
    f.write(rep_ini)
    f.close()


def reply(id):
    """ Function look out answer messages """
    sql_reply_str = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, " \
                "remote_resource, edit_version, thumb_image, recipient_count, raw_data, starred, quoted_row_id, forwarded FROM messages_quotes WHERE _id = " + str(id)
    sql_answer = cursor_rep.execute(sql_reply_str)
    rep = sql_answer.fetchone()
    ans = ""
    reply_msj = ""
    if rep is not None:  # Message not deleted
        if (str(rep[0]).split('@'))[1] == "g.us":
            if int(rep[1]) == 1:  # I post a message in a group
                if report_var == 'EN':
                    reply_msj = "<font color=\"#FF0000\" > Me </font>"
                elif report_var == 'ES':
                    reply_msj = "<font color=\"#FF0000\" > Yo </font>"
                else:
                    ans = "Me"
            elif int(rep[1]) == 0:  # Somebody post a message in a group
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj = "<font color=\"#FF0000\" > " + (str(rep[15]).split('@'))[0] + gets_name(rep[15]) + " </font>"
                else:
                    ans = (str(rep[15]).split('@'))[0] + gets_name(rep[15])
        elif (str(rep[0]).split('@'))[1] == "s.whatsapp.net":
            if int(rep[1]) == 1:  # I send message to somebody
                if report_var == 'EN':
                    reply_msj = "<font color=\"#FF0000\" > Me </font>"
                elif report_var == 'ES':
                    reply_msj = "<font color=\"#FF0000\" > Yo </font>"
                else:
                    ans = "Me"
            elif int(rep[1]) == 0:  # Someone sends me a message
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj = "<font color=\"#FF0000\" > " + (str(rep[0]).split('@'))[0] + gets_name(rep[0]) + " </font>"
                else:
                    ans = (str(rep[0]).split('@'))[0] + gets_name(rep[0])
        elif str(rep[0]) == "status@broadcast":
            if os.path.isfile("./Media/.Statuses") is False:
                distutils.dir_util.mkpath("./Media/.Statuses")
                if int(rep[1]) == 1:  # I post a Status
                    if report_var == 'EN':
                        reply_msj = "<font color=\"#FF0000\" > Me </font>"
                    elif report_var == 'ES':
                        reply_msj = "<font color=\"#FF0000\" > Yo </font>"
                    else:
                        ans = "Me"
                elif int(rep[1]) == 0:  # Somebody posts a Status
                    if (report_var == 'EN') or (report_var == 'ES'):
                        reply_msj = "<font color=\"#FF0000\" > " + (str(rep[15]).split('@'))[0] + gets_name(rep[15]) + " </font>"
                    else:
                        ans = (str(rep[15]).split('@'))[0] + gets_name(rep[15])

        if rep[22] and int(rep[22]) > 0:  # Forwarded
                if report_var == 'EN':
                    reply_msj += "<br><font color=\"#8b8878\" > &#10150; Forwarded</font>"
                elif report_var == 'ES':
                    reply_msj += "<br><font color=\"#8b8878\" > &#10150; Reenviado</font>"
                else:
                    ans += Fore.RED + " - Forwarded" + Fore.RESET

        if int(rep[8]) == 0:  # media_wa_type 0, text message
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br>" + html.escape(rep[4])
            else:
                ans += Fore.RED + " - Message: " + Fore.RESET + rep[4]

        elif int(rep[8]) == 1:  # media_wa_type 1, Image
            chain = rep[17].split(b'\x77\x02')[0]
            i = chain.rfind(b"Media/")
            b = len(chain)
            if i == -1:  # Image doesn't exist
                thumb = "./Media/WhatsApp Images/IMG-" + str(rep[2]) + "-NotDownloaded.jpg"
            else:
                thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')
                if os.path.isfile(thumb) is False:
                    distutils.dir_util.mkpath("./Media/WhatsApp Images")
                    if rep[19]:  # raw_data exists
                        with open(thumb, 'wb') as profile_file:
                            profile_file.write(rep[19])
            if rep[11]:  # media_caption
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb + " - " + html.escape(rep[11])
                else:
                    ans += Fore.RED + " - Name: " + Fore.RESET + thumb + Fore.RED + " - Caption: " + Fore.RESET + rep[11] + "\n"
            else:
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb
                else:
                    ans += Fore.RED + " - Name: " + Fore.RESET + thumb + "\n"
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + "'width=\"100\" height=\"100\"/></a>"

        elif int(rep[8]) == 2:  # media_wa_type 2, Audio
            chain = rep[17].split(b'\x77\x02')[0]
            i = chain.rfind(b"Media/")
            b = len(chain)
            if i == -1:  # Image doesn't exist
                thumb = "Not downloaded"
            else:
                thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br>" + thumb + " " + size_file(rep[9]) + " - " + duration_file(rep[12]) + "<br></br><audio controls> <source src=\"." + thumb + "\" type=\"" + rep[7] + "\"</audio>"
            else:
                ans += Fore.RED + " - Name: " + Fore.RESET + thumb + "\n"
                ans += Fore.RED + "Type: " + Fore.RESET + rep[7] + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(rep[9]) + Fore.RED + " - Duration: " + Fore.RESET + duration_file(rep[12]) + "\n"

        elif int(rep[8]) == 3:  # media_wa_type 3 Video
            chain = rep[17].split(b'\x77\x02')[0]
            i = chain.rfind(b"Media/")
            b = len(chain)
            if i == -1:  # Video doesn't exist
                thumb = "./Media/WhatsApp Video/VID-" + str(rep[2]) + "-NotDownloaded.mp4"
            else:
                thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')

                if rep[19]:  # raw_data exists
                    if os.path.isfile(thumb) is False:
                        distutils.dir_util.mkpath("./Media/WhatsApp Video")
                        with open(thumb, 'wb') as profile_file:
                            profile_file.write(rep[19])
            if rep[11]:  # media_caption
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb + " - " + html.escape(rep[11])
                else:
                    ans += Fore.RED + " - Name: " + Fore.RESET + thumb + Fore.RED + " - Caption: " + Fore.RESET + rep[11] + "\n"
            else:
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb
                else:
                    ans += Fore.RED + " - Name: " + Fore.RESET + thumb + "\n"
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += " " + size_file(rep[9]) + " - " + duration_file(rep[12])
                reply_msj += "<br> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + "'width=\"100\" height=\"100\"/></a>"
            else:
                ans += Fore.RED + "Type: " + Fore.RESET + rep[7] + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(rep[9]) + Fore.RED + " - Duration: " + Fore.RESET + duration_file(rep[12]) + "\n"

        elif int(rep[8]) == 4:  # media_wa_type 4, Contact
            if report_var == 'EN':
                reply_msj += "<br>" + html.escape(rep[10]) + "<br>&#9742;  Contact vCard"
            if report_var == 'ES':
                reply_msj += "<br>" + html.escape(rep[10]) + "<br>&#9742;  Contacto vCard"
            else:
                ans += Fore.RED + " - Name: " + Fore.RESET + rep[10] + Fore.RED + " - Type:" + Fore.RESET + " Contact vCard\n"

        elif int(rep[8]) == 5:  # media_wa_type 5, Location
            if rep[6]:  # media_url exists
                if rep[10]:  # media_name exists
                    if (report_var == 'EN') or (report_var == 'ES'):
                        reply_msj += "<br>" + html.escape(rep[6]) + " - " + html.escape(rep[10]) + "<br>"
                    else:
                        ans += Fore.RED + " - Url: " + Fore.RESET + rep[6] + Fore.RED + " - Name: " + Fore.RESET + rep[10] + "\n"
                else:
                    if (report_var == 'EN') or (report_var == 'ES'):
                        reply_msj += "<br>" + html.escape(rep[6]) + "<br>"
                    else:
                        ans += Fore.RED + " - Url: " + Fore.RESET + rep[6] + "\n"
            else:
                if rep[10]:
                    if (report_var == 'EN') or (report_var == 'ES'):
                        reply_msj += "<br>" + html.escape(rep[10]) + "<br>"
                    else:
                        ans += Fore.RED + " - Name: " + Fore.RESET + rep[10] + "\n"
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br>" + "<iframe width='300' height='150' id='gmap_canvas' src='https://maps.google.com/maps?q={}%2C{}&t=&z=15&ie=UTF8&iwloc=&output=embed' frameborder='0' scrolling='no' marginheight='0' marginwidth='0'></iframe>".format(str(rep[13]), str(rep[14]))
            else:
                ans += Fore.RED + "Type: " + Fore.RESET + "Location" + Fore.RED + " - Lat: " + Fore.RESET + str(rep[13]) + Fore.RED + " - Long: " + Fore.RESET + str(rep[14]) + "\n"

        elif int(rep[8]) == 8:  # media_wa_type 8, Audio / Video Call
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br>" + "&#128222; " + str(rep[11]).capitalize() + " " + duration_file(rep[12])
            else:
                ans += Fore.RED + " - Call :" + Fore.RESET + str(rep[11]).capitalize() + Fore.RED + " - Duration: " + Fore.RESET + duration_file(rep[12]) + "\n"

        elif int(rep[8]) == 9:  # media_wa_type 9, Application
            chain = rep[17].split(b'\x77\x02')[0]
            i = chain.rfind(b"Media/")
            b = len(chain)
            if i == -1:  # App doesn't exist
                thumb = "./Media/WhatsApp Documents/DOC-" + str(rep[2]) + "-NotDownloaded"
            else:
                thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')
                if os.path.isfile(thumb) is False:
                    distutils.dir_util.mkpath("./Media/WhatsApp Documents")
                    if rep[19]:  # raw_data exists
                        with open(thumb +"jpg", 'wb') as profile_file:
                            profile_file.write(rep[19])
            if rep[11]:  # media_caption
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb + " - " + html.escape(rep[11])
                else:
                    ans += Fore.RED + " - Name: " + Fore.RESET + thumb + Fore.RED + " - Caption: " + Fore.RESET + rep[11] + "\n"
            else:
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb
                else:
                    ans += Fore.RED + " - Name: " + Fore.RESET + thumb + "\n"
            if rep[12] >= 0:
                if report_var == 'EN':
                    reply_msj += " " + size_file(rep[9]) + " - " + str(rep[12]) + " Pages"
                elif report_var == 'ES':
                    reply_msj += " " + size_file(rep[9]) + " - " + str(rep[12]) + " Páginas"
                else:
                    ans += Fore.RED + "Type: " + Fore.RESET + rep[7] + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(rep[9]) + Fore.RED + " - Pages: " + Fore.RESET + str(rep[12]) + "\n"
            else:
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += " " + size_file(rep[9])
                else:
                    ans += Fore.RED + "Type: " + Fore.RESET + rep[7] + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(rep[9]) + "\n"
            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + ".jpg' width=\"100\" height=\"100\"/></a>"

        elif int(rep[8]) == 10:  # media_wa_type 10, Video/Audio call lost
            if report_var == 'EN':
                reply_msj += "<br>" + "&#128222; Missed" + str(rep[11]).capitalize() + " call"
            elif report_var == 'ES':
                reply_msj += "<br>" + "&#128222; " + str(rep[11]).capitalize() + " llamada perdida"
            else:
                ans += Fore.RED + " - Message: " + Fore.RESET + "Missed " + str(rep[11]).capitalize() + " call\n"

        elif int(rep[8]) == 13:  # media_wa_type 13 Gif
            chain = rep[17].split(b'\x77\x02')[0]
            i = chain.rfind(b"Media/")
            b = len(chain)
            if i == -1:  # GIF doesn't exist
                thumb = "./Media/WhatsApp Animated Gifs/VID-" + str(rep[2]) + "-NotDownloaded.mp4"
            else:
                thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')
                if os.path.isfile(thumb) is False:
                    distutils.dir_util.mkpath("./Media/WhatsApp Animated Gifs")
                    if rep[19]:  # raw_data exists
                        with open(thumb, 'wb') as profile_file:
                            profile_file.write(rep[19])

            if rep[11]:  # media_caption
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb + " - " + html.escape(rep[11])
                else:
                    ans += Fore.RED + " - Name: " + Fore.RESET + thumb + Fore.RED + " - Caption: " + Fore.RESET + rep[11] + "\n"
            else:
                if (report_var == 'EN') or (report_var == 'ES'):
                    reply_msj += "<br>" + thumb
                else:
                    ans += Fore.RED + " - Name: " + Fore.RESET + thumb + "\n"

            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += " - Gif - " + size_file(rep[9]) + " " + duration_file(rep[12]) + "<br> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + "'width=\"100\" height=\"100\"/></a>"
            else:
                ans += Fore.RED + "Type: " + Fore.RESET + "Gif" + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(rep[9]) + Fore.RED + " - Duration: " + Fore.RESET + duration_file(rep[12]) + "\n"

        elif int(rep[8]) == 14:  # Vcard Multiple
            concat = ""
            chain = str(rep[19]).split('BEGIN:VCARD')
            for i in chain[1:]:
                concat += "BEGIN:VCARD"
                concat += i.split('END:VCARD')[0] + "END:VCARD"
            if report_var == 'EN':
                reply_msj += "<br>" + html.escape(rep[10]) + "<br>&#9742;  Contact vCard</br>" + html.escape(concat)
            elif report_var == 'ES':
                reply_msj += "<br>" + html.escape(rep[10]) + "<br>&#9742;  Contacto vCard</br>" + html.escape(concat)
            else:
                ans += Fore.RED + " - Name: " + Fore.RESET + rep[10] + Fore.RED + " - Type:" + Fore.RESET + " Contact vCard" + concat + "\n"

        elif int(rep[8]) == 15:  # media_wa_type 15, Deleted Object
            if int(rep[16]) == 5:  # edit_version 5, deleted for me
                if report_var == 'EN':
                    reply_msj += "<br>" + "Message deleted for Me"
                elif report_var == 'ES':
                    reply_msj += "<br>" + "Mensaje eliminado para mí"
                else:
                    ans += Fore.RED + " - Message: " + Fore.RESET + "Message deleted for Me\n"

            elif int(rep[16]) == 7:  # edit_version 7, deleted for all
                if report_var == 'EN':
                    reply_msj += "<br>" + "Message deleted for all participants"
                elif report_var == 'ES':
                    reply_msj += "<br>" + "Mensaje eliminado para todos los destinatarios"
                else:
                    ans += Fore.RED + " - Message: " + Fore.RESET + "Message deleted for all participants\n"

        elif int(rep[8]) == 16:  # media_wa_type 16, Share location
            caption = ""
            if rep[11]:
                caption = rep[11]
            if report_var == 'EN':
                reply_msj += "<br>" + "Real time location (" + str(rep[13]) + "," + str(rep[14]) + ") - " + html.escape(caption) + "\n"
                reply_msj += " <br><a href=\"https://www.google.es/maps/search/(" + str(rep[13]) + "," + str(rep[14]) + ")\" target=\"_blank\"> <img src=\"http://maps.google.com/maps/api/staticmap?center=" + str(rep[13]) + "," + str(rep[14]) + "&zoom=16&size=300x150&markers=size:mid|color:red|label:A|" + str(rep[13]) + "," + str(rep[14]) + "&sensor=false\"/></a>"
            elif report_var == 'ES':
                reply_msj += "<br>" + "Ubicación en tiempo real (" + str(rep[13]) + "," + str(rep[14]) + ") - " + html.escape(caption) + "\n"
                reply_msj += "<br><iframe width='300' height='150' id='gmap_canvas' src='https://maps.google.com/maps?q={}%2C{}&t=&z=15&ie=UTF8&iwloc=&output=embed' frameborder='0' scrolling='no' marginheight='0' marginwidth='0'></iframe>".format(str(rep[13]), str(rep[14]))
            else:
                ans += Fore.RED + " - Type: " + Fore.RESET + "Real time location " + Fore.RED + "- Caption: " + Fore.RESET + caption + Fore.RED + " - Lat: " + Fore.RESET + str(rep[13]) + Fore.RED + " - Long: " + Fore.RESET + str(rep[14]) + Fore.RED + " - Duration: " + Fore.RESET + duration_file(rep[12]) + "\n"

        elif int(rep[8]) == 20:  # media_wa_type 20 Sticker
            chain = rep[17].split(b'\x77\x02')[0]
            i = chain.rfind(b"Media/")
            b = len(chain)
            if i == -1:  # Sticker doesn't exist
                thumb = "Not downloaded"
            else:
                thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')

            if (report_var == 'EN') or (report_var == 'ES'):
                reply_msj += "<br>" + "Sticker - " + size_file(rep[9]) + "<br> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + "'width=\"100\" height=\"100\"/></a>"
            else:
                ans += Fore.RED + " - Type: " + Fore.RESET + "Sticker" + Fore.RED + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(rep[9]) + Fore.RED + "\n"

        else:  # Deleted Message
            if report_var == 'EN':
                reply_msj = "<br>" + "Deleted message"
            elif report_var == 'ES':
                reply_msj = "<br>" + "Mensaje eliminado"
            else:
                ans += " - Deleted message"

    return ans, reply_msj


def messages(consult, rows, report_html):
    """ Function that show database messages """
    try:
        n_mes = 0
        rep_med = ""  # Saves the complete chat

        if arg_group and report_var == "None":
            print(Fore.RED + "Participants" + Fore.RESET)
            print(report_group)

        for data in consult:
            try:
                report_msj = ""   # Saves each message
                report_name = ""  # Saves the chat sender
                message = ""      # Saves each msg
                sys.stdout.write("\rMessage {}/{} - ID {}".format(str(n_mes+1), str(rows), str(data[23])))
                sys.stdout.flush()

                if int(data[8]) != -1:   # media_wa_type -1 "Start DB"
                    # Groups
                    if (str(data[0]).split('@'))[1] == "g.us":
                        if int(data[1]) == 1:
                            if int(data[3]) == 6:  # Group System Message
                                if report_var == 'EN':
                                    report_name = "System Message"
                                elif report_var == 'ES':
                                    report_name = "Mensaje de Sistema"
                                else:
                                    message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                    message += Fore.GREEN + "From " + Fore.RESET + data[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + "\n"
                            else:  # I send message to a group
                                if report_var == 'EN':
                                    report_name = "Me"
                                elif report_var == 'ES':
                                    report_name = "Yo"
                                else:
                                    message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                    message += Fore.GREEN + "From " + Fore.RESET + "Me" + Fore.GREEN + " to " + Fore.RESET + data[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + "\n"
                        elif int(data[1]) == 0:  # Somebody post a message in a group
                            if (report_var == 'EN') or (report_var == 'ES'):
                                current_color = color.get((str(data[15]).split('@'))[0])
                                if not current_color:
                                    current_color = "#5586e5"
                                report_name = "<font color='{}'> {} </font>".format(current_color, (str(data[15]).split('@'))[0] + gets_name(data[15]))
                            else:
                                message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                message += Fore.GREEN + "From " + Fore.RESET + data[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + Fore.GREEN + ", participant " + Fore.RESET + (str(data[15]).split('@'))[0] + " " + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + "\n"
                    # Users
                    elif (str(data[0]).split('@'))[1] == "s.whatsapp.net":
                        if data[15] and (str(data[15]).split('@'))[1] == "broadcast":
                            if int(data[1]) == 1:  # I send to somebody message by broadcast
                                if report_var == 'EN':
                                    report_name = "&#128227; Me"
                                elif report_var == 'ES':
                                    report_name = "&#128227; Yo"
                                else:
                                    message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                    message += Fore.GREEN + "From" + Fore.RESET + " Me" + Fore.GREEN + " to " + Fore.RESET + (str(data[0]).split('@'))[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET +  Fore.GREEN + " by broadcast" + Fore.RESET + "\n"
                            elif int(data[1]) == 0:  # Someone sends me a message by broadcast

                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_name = "&#128227;" + (str(data[0]).split('@'))[0] + gets_name(data[0])
                                else:
                                    message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                    message += Fore.GREEN + "From " + Fore.RESET + (str(data[0]).split('@'))[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + Fore.GREEN + " to" + Fore.RESET + " Me" + Fore.GREEN + " by broadcast" + Fore.RESET + "\n"
                        else:
                            if int(data[1]) == 1:
                                if int(data[3]) == 6:  # User system message
                                    if report_var == 'EN':
                                        report_name = "System Message"
                                    elif report_var == 'ES':
                                        report_name = "Mensaje de Sistema"
                                    else:
                                        message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                        message += Fore.GREEN + "From " + Fore.RESET + (str(data[0]).split('@'))[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + "\n"
                                else:  # I send message to someone
                                    if report_var == 'EN':
                                        report_name = "Me"
                                    elif report_var == 'ES':
                                        report_name = "Yo"
                                    else:
                                        message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                        message += Fore.GREEN + "From" + Fore.RESET + " Me" + Fore.GREEN + " to " + Fore.RESET + (str(data[0]).split('@'))[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + "\n"
                            elif int(data[1]) == 0:  # Someone sends me a message
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_name = (str(data[0]).split('@'))[0] + gets_name(data[0])
                                else:
                                    message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                    message += Fore.GREEN + "From " + Fore.RESET + (str(data[0]).split('@'))[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + Fore.GREEN + " to" + Fore.RESET + " Me\n"
                    # Broadcast and Status
                    elif (str(data[0]).split('@'))[1] == "broadcast":
                        # Status
                        if str(data[0]) == "status@broadcast":
                            if os.path.isfile("./Media/.Statuses") is False:
                                distutils.dir_util.mkpath("./Media/.Statuses")
                            if int(data[1]) == 1:  # I post a Status
                                if report_var == 'EN':
                                    report_name = "Me"
                                elif report_var == 'ES':
                                    report_name = "Yo"
                                else:
                                    message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                    message += Fore.GREEN + "From " + Fore.RESET + "Me - Post status" + "\n"
                            elif int(data[1]) == 0:  # Somebody posts a Status
                                if report_var == 'EN':
                                    report_name = "Posts Status - " + (str(data[15]).split('@'))[0] + gets_name(data[15])
                                elif report_var == 'ES':
                                    report_name = "Publica Estado - " + (str(data[15]).split('@'))[0] + gets_name(data[15])
                                else:
                                    message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                    message += Fore.GREEN + "From " + Fore.RESET + (str(data[15]).split('@'))[0] + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + Fore.GREEN + " posts status" + Fore.RESET + "\n"
                        # Broadcast
                        else:
                            if int(data[3]) == 6:  # Broadcast system message
                                if report_var == 'EN':
                                    report_name = "System Message"
                                elif report_var == 'ES':
                                    report_name = "Mensaje de Sistema"
                                else:
                                    message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                    message += Fore.GREEN + "From " + Fore.RESET + (str(data[0]).split('@'))[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + "\n"
                            else:  # I send a message to a broadcast list
                                list_broadcast = (str(data[15])).replace(',', '').split('@s.whatsapp.net')
                                list_copy = []
                                for i in list_broadcast:
                                    list_copy.append(i + " " + Fore.YELLOW +  gets_name(i + "@s.whatsapp.net") + Fore.RESET)
                                list_copy.pop()
                                list_copy = ", ".join(list_copy)

                                if report_var == 'EN':
                                    report_name = "&#128227; Me"
                                elif report_var == 'ES':
                                    report_name = "&#128227; Yo"
                                else:
                                    message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"
                                    message += Fore.GREEN + "From" + Fore.RESET + " Me" + Fore.GREEN + " to " + Fore.RESET + list_copy + " " + Fore.YELLOW + gets_name(list_copy) + Fore.RESET + Fore.GREEN + " by broadcast" + Fore.RESET + "\n"

                    if int(data[8]) == 0:  # media_wa_type 0, text message
                        if int(data[3]) == 6:  # Status 6, system message
                            if data[9] == 1:  # if media_size value change
                                if report_var == 'EN':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + gets_name(data[15]) + " changed the subject from '" + html.escape(data[17][7:].decode('UTF-8', 'ignore')) + "' to '" + html.escape(data[4]) + "'"
                                elif report_var == 'ES':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + gets_name(data[15]) + " cambió el asunto de '" + html.escape(data[17][7:].decode('UTF-8', 'ignore')) + "' a '" + html.escape(data[4]) + "'"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " changed the subject from '" + data[17][7:].decode('UTF-8', 'ignore') + "' to '" + data[4] + "'\n"

                            elif data[9] == 4:
                                if report_var == 'EN':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + gets_name(data[15]) + " was added to the group"
                                elif report_var == 'ES':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + gets_name(data[15]) + " fue añadido al grupo"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " was added to the group\n"

                            elif data[9] == 5:
                                if report_var == 'EN':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + gets_name(data[15]) + " left the group"
                                elif report_var == 'ES':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + gets_name(data[15]) + " dejó el grupo"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " left the group\n"

                            elif data[9] == 6:
                                if report_var == 'EN':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + gets_name(data[15]) + " changed the group icon"
                                elif report_var == 'ES':
                                    report_msj += str(data[15].strip("@s.whatsapp.net")) + gets_name(data[15]) + " cambió el icono del grupo"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " changed the group icon\n"
                                    message += "The last picture is stored on the phone path '/data/data/com.whatsapp/cache/Profile Pictures/" + (data[0].split('@'))[0] + ".jpg'\n"

                                if data[17]:
                                    file_created = "./Media/WhatsApp Profile Pictures/" + (data[0].split('@'))[0] + "-" + str(data[2]) + ".jpg"
                                    if os.path.isfile(file_created) is False:
                                        distutils.dir_util.mkpath("./Media/WhatsApp Profile Pictures")
                                        thumb = data[17].split(b'\xFF\xD8\xFF\xE0')[1]
                                        with open(file_created, 'wb') as profile_file:
                                            profile_file.write(b'\xFF\xD8\xFF\xE0' + thumb)

                                    if (report_var == 'EN') or (report_var == 'ES'):
                                        report_msj += "<br>./Media/WhatsApp Profile Pictures/" + (data[0].split('@'))[0] + "-" + str(data[2]) + ".jpg"
                                        report_msj += "<br><a href=\"../Media/WhatsApp Profile Pictures/" + (data[0].split('@'))[0] + "-" + str(data[2]) + ".jpg\" target=\"_blank\"> <IMG SRC=\"../Media/WhatsApp Profile Pictures/" +  (data[0].split('@'))[0] + "-" + str(data[2]) + ".jpg\" width=\"100\" height=\"100\"/></a>"
                                    else:
                                        message += "Thumbnail stored on local path './Media/WhatsApp Profile Pictures/" + (data[0].split('@'))[0] + "-" + ".jpg'\n"

                            elif data[9] == 7:
                                if report_var == 'EN':
                                    report_msj += " Removed " + data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " from the list"
                                elif report_var == 'ES':
                                    report_msj += " Removío " + data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " de la lista"
                                else:
                                    message += Fore.GREEN + "Message:" + Fore.RESET + " Removed " + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " from the list\n"

                            elif data[9] == 9:
                                list_broadcast = (str(data[17][58:]).split("\\x00\\x1a"))[1:]
                                list_copy = []
                                for i in list_broadcast:
                                    list_copy.append(i.split("@")[0] + gets_name(i.split("@")[0] + "@s.whatsapp.net"))

                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " created a broadcast list with " + ", ".join(list_copy) + " recipients"
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " creó una lista de difusión con " + ", ".join(list_copy) + " destinatarios"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " created a broadcast list with " + ", ".join(list_copy) + " recipients\n"

                            elif data[9] == 10:
                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " changed to " + (data[17][7:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][7:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net")
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " cambió a " + (data[17][7:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][7:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net")
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " changed to " + (data[17][7:].decode('UTF-8', 'ignore').split('@'))[0] + Fore.YELLOW + gets_name((data[17][7:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + Fore.RESET + "\n"

                            elif data[9] == 11:
                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " created the group ' " + html.escape(data[4]) + " '"
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " creó el grupo ' " + html.escape(data[4]) + " '"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " created the group '" + data[4] + "'\n"

                            elif data[9] == 12:
                                if data[15]:  # If exists remote_resource  - Group
                                    if report_var == 'EN':
                                        report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " added " + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + " to the group"
                                    elif report_var == 'ES':
                                        report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " añadió " + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + " al grupo"
                                    else:
                                        message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " added " + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + Fore.YELLOW + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + Fore.RESET + " to the group\n"

                                else:  # User
                                    if report_var == 'EN':
                                        report_msj += "Added " + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + " to the group"
                                    elif report_var == 'ES':
                                        report_msj += "Se añadió " + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + " al grupo"
                                    else:
                                        message += Fore.GREEN + "Message: " + Fore.RESET + "Added " + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + Fore.YELLOW + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + Fore.RESET + "to the group\n"
                            elif data[9] == 13:
                                list_broadcast = (str(data[17][58:]).split("\\x00\\x1a"))[1:]
                                list_copy = []
                                for i in list_broadcast:
                                    list_copy.append(i.split("@")[0] + gets_name(i.split("@")[0] + "@s.whatsapp.net"))

                                if report_var == 'EN':
                                    report_msj += ", ".join(list_copy) + " left the group"
                                elif report_var == 'ES':
                                    report_msj += ", ".join(list_copy) + " dejaron el grupo"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + ", ".join(list_copy) + " left the group\n"

                            elif data[9] == 14:
                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " eliminated " + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + " from the group"
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " eliminó " + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + " del grupo"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " eliminated " + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + Fore.YELLOW + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + Fore.RESET + " from the group\n"

                            elif data[9] == 15:
                                if report_var == 'EN':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " made you administrator"
                                elif report_var == 'ES':
                                    report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " te hizo administrador"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + "made you administrator\n"

                            elif data[9] == 18:
                                if data[15]:
                                    if report_var == 'EN':
                                        report_msj += "The security code of " + data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " changed"
                                    elif report_var == 'ES':
                                        report_msj += "El código de seguridad de " + data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " cambió"
                                    else:
                                        message += Fore.GREEN + "Message: " + Fore.RESET + "The security code of " + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " changed\n"

                                else:
                                    if report_var == 'EN':
                                        report_msj += "The security code of " + data[0].strip("@s.whatsapp.net") + gets_name(data[0]) + " changed"
                                    elif report_var == 'ES':
                                        report_msj += "El código de seguridad de " + data[0].strip("@s.whatsapp.net") + gets_name(data[0]) + " cambió"
                                    else:
                                        message += Fore.GREEN + "Message: " + Fore.RESET + "The security code of " + data[0].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + " changed\n"

                            elif data[9] == 19:
                                if report_var == 'EN':
                                    report_msj += "Messages and calls in this chat are now protected with end-to-end encryption"
                                elif report_var == 'ES':
                                    report_msj += "Los mensajes y llamadas en este chat ahora están protegidos con cifrado de extremo a extremo"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + "Messages and calls in this chat are now protected with end-to-end encryption\n"

                            elif data[9] == 20:
                                if report_var == 'EN':
                                    report_msj += (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + " joined using an invitation link from this group"
                                elif report_var == 'ES':
                                    report_msj += (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + " se unió usando un enlace de invitación de este grupo"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + (data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + Fore.YELLOW + gets_name((data[17][60:].decode('UTF-8', 'ignore').split('@'))[0] + "@s.whatsapp.net") + Fore.RESET + " joined using an invitation link from this group\n"

                            elif data[9] == 22:
                                if report_var == 'EN':
                                    report_msj += "This chat could be with a company account"
                                elif report_var == 'ES':
                                    report_msj += "Este chat podría ser con una cuenta de empresa"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + "This chat could be with a company account\n"

                            elif data[9] == 27:
                                if data[4] != "":
                                    if report_var == 'EN':
                                        report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " changed the group description to ' " + html.escape(data[4]) + " '"
                                    elif report_var == 'ES':
                                        report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " cambió la descripción del grupo a ' " + html.escape(data[4]) + " '"
                                    else:
                                        message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " changed the group description to '" + data[4] + "'\n"

                                else:
                                    if report_var == 'EN':
                                        report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " deleted the group description"
                                    elif report_var == 'ES':
                                        report_msj += data[15].strip("@s.whatsapp.net") + gets_name(data[15]) + " borró la descripción del grupo"
                                    else:
                                        message += Fore.GREEN + "Message: " + Fore.RESET + data[15].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[15]) + Fore.RESET + " deleted the group description\n"
                            elif data[9] == 28:
                                if report_var == 'EN':
                                    report_msj += data[0].strip("@s.whatsapp.net") + gets_name(data[0]) + " changed his phone number"
                                elif report_var == 'ES':
                                    report_msj += data[0].strip("@s.whatsapp.net") + gets_name(data[0]) + " cambió su número de teléfono"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + data[0].strip("@s.whatsapp.net") + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + " changed his phone number\n"
                            elif data[9] == 46:
                                if report_var == 'EN':
                                    report_msj += "This chat is with a company account"
                                elif report_var == 'ES':
                                    report_msj += "Este chat es con una cuenta de empresa"
                                else:
                                    message += Fore.GREEN + "Message: " + Fore.RESET + "This chat is with a company account\n"
                        else:
                            if data[24] and int(data[24]) > 0:  # Forwarded
                                if report_var == 'EN':
                                    report_msj += "<font color=\"#8b8878\" >&#10150; Forwarded</font><br>"
                                elif report_var == 'ES':
                                    report_msj += "<font color=\"#8b8878\" >&#10150; Reenviado</font><br>"
                                else:
                                    message += Fore.GREEN + "Forwarded " + Fore.RESET + "\n"

                            if data[21] and int(data[21]) > 0:  # Reply
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_msj = "<p style=\"border-left: 6px solid blue; background-color: lightgrey;border-radius:5px;\"; > " + \
                                                 reply(data[21])[1] + "</p>"
                                else:
                                    message += Fore.RED + "Replying to: " + Fore.RESET + reply(data[21])[0] + "\n"

                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += html.escape(data[4])
                            else:
                                message += Fore.GREEN + "Message: " + Fore.RESET + data[4] + "\n"

                    elif int(data[8]) == 1:  # media_wa_type 1, Image
                        chain = data[17].split(b'\x77\x02')[0]
                        i = chain.rfind(b"Media/")
                        b = len(chain)
                        if i == -1:  # Image doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')

                        if data[11]:  # media_caption
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb + " - " + html.escape(data[11])
                            else:
                                message += Fore.GREEN + "Name: " + Fore.RESET + thumb + Fore.GREEN + " - Caption: " + Fore.RESET + data[11] + "\n"
                        else:
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb
                            else:
                                message += Fore.GREEN + "Name: " + Fore.RESET + thumb + "\n"

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += " " + size_file(data[9])
                        else:
                            message += Fore.GREEN + "Type: " + Fore.RESET + "image/jpeg" + Fore.GREEN + " - Size: " + Fore.RESET + str(data[9]) + " bytes " + size_file(data[9]) + "\n"

                        if os.path.isfile(thumb) is False:
                            distutils.dir_util.mkpath("./Media/WhatsApp Images/Sent")
                            if thumb == "Not downloaded":
                                if int(data[1]) == 1:
                                    thumb = "./Media/WhatsApp Images/Sent/IMG-" + str(data[2]) + "-NotDownloaded.jpg"
                                else:
                                    thumb = "./Media/WhatsApp Images/IMG-" + str(data[2]) + "-NotDownloaded.jpg"

                            with open(thumb, 'wb') as profile_file:
                                if data[19]:    # raw_data exists
                                    profile_file.write(data[19])
                                elif data[22]:  # Gets the thumbnail of the message_thumbnails
                                    profile_file.write(data[22])
                                else:
                                    profile_file.write(b"")

                            if report_var == 'None':
                                message += "Thumbnail was saved on local path '" + thumb + "'\n"

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + "'width=\"100\" height=\"100\"/></a>"

                    elif int(data[8]) == 2:  # media_wa_type 2, Audio
                        chain = data[17].split(b'\x77\x02')[0]
                        i = chain.rfind(b"Media/")
                        b = len(chain)
                        if i == -1:  # Audio doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br>" + thumb + " " + size_file(data[9]) + " - " + duration_file(data[12]) + "<br></br><audio controls> <source src=\"." + thumb + "\" type=\"" + data[7] + "\"</audio>"
                        else:
                            message += Fore.GREEN + "Name: " + Fore.RESET + thumb + "\n"
                            message += Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size: " + Fore.RESET + str(data[9]) + " bytes " + size_file(data[9]) + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(data[12]) + "\n"

                    elif int(data[8]) == 3:  # media_wa_type 3 Video
                        chain = data[17].split(b'\x77\x02')[0]
                        i = chain.rfind(b"Media/")
                        b = len(chain)
                        if i == -1:  # Video doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')

                        if data[11]:  # media_caption
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb + " - " + html.escape(data[11])
                            else:
                                message += Fore.GREEN + "Name: " + Fore.RESET + thumb + Fore.GREEN + " - Caption: " + Fore.RESET + data[11] + "\n"
                        else:
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb
                            else:
                                message += Fore.GREEN + "Name: " + Fore.RESET + thumb + "\n"

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += " " + size_file(data[9]) + " - " + duration_file(data[12])
                        else:
                            message += Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size: " + Fore.RESET + str(data[9]) + " bytes " + size_file(data[9]) + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(data[12]) + "\n"

                        if os.path.isfile(thumb) is False:
                            distutils.dir_util.mkpath("./Media/WhatsApp Video/Sent")
                            if thumb == "Not downloaded":
                                if int(data[1]) == 1:
                                    thumb = "./Media/WhatsApp Video/Sent/VID-" + str(data[2]) + "-NotDownloaded.mp4"
                                else:
                                    thumb = "./Media/WhatsApp Video/VID-" + str(data[2]) + "-NotDownloaded.mp4"

                            with open(thumb, 'wb') as profile_file:
                                if data[19]:  # raw_data exists
                                    profile_file.write(data[19])
                                elif data[22]:  # Gets the thumbnail of the message_thumbnails
                                    profile_file.write(data[22])
                                else:
                                    profile_file.write(b"")

                            if report_var == 'None':
                                message += "Thumbnail was saved on local path '" + thumb + "'\n"

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br/> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + "'width=\"100\" height=\"100\"/></a>"

                    elif int(data[8]) == 4:  # media_wa_type 4, Contact
                        if report_var == 'EN':
                            report_msj += html.escape(data[10]) + "<br>&#9742;  Contact vCard"
                        elif report_var == 'ES':
                            report_msj += html.escape(data[10]) + "<br>&#9742;  Contacto vCard"
                        else:
                            message += Fore.GREEN + "Name: " + Fore.RESET + data[10] + Fore.GREEN + " - Type:" + Fore.RESET + " Contact vCard\n"

                    elif int(data[8]) == 5:  # media_wa_type 5, Location
                        if data[6]:  # media_url exists
                            if data[10]:  # media_name exists
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_msj += html.escape(data[6]) + " - " + html.escape(data[10]) + "<br>"
                                else:
                                    message += Fore.GREEN + "Url: " + Fore.RESET + data[6] + Fore.GREEN + " - Name: " + Fore.RESET + data[10] + "\n"
                            else:
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_msj += html.escape(data[6]) + "<br>"
                                else:
                                    message += Fore.GREEN + "Url: " + Fore.RESET + data[6] + "\n"
                        else:
                            if data[10]:
                                if (report_var == 'EN') or (report_var == 'ES'):
                                    report_msj += html.escape(data[10]) + "<br>"
                                else:
                                    message += Fore.GREEN + "Name: " + Fore.RESET + data[10] + "\n"

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<iframe width='300' height='150' id='gmap_canvas' src='https://maps.google.com/maps?q={}%2C{}&t=&z=15&ie=UTF8&iwloc=&output=embed' frameborder='0' scrolling='no' marginheight='0' marginwidth='0'></iframe>".format(str(data[13]), str(data[14]))
                        else:
                            message += Fore.GREEN + "Type: " + Fore.RESET + "Location" + Fore.GREEN + " - Lat: " + Fore.RESET + str(data[13]) + Fore.GREEN + " - Long: " + Fore.RESET + str(data[14]) + "\n"

                    elif int(data[8]) == 8:  # media_wa_type 8, Audio / Video Call
                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "&#128222; " + str(data[11]).capitalize() + " " + duration_file(data[12])
                        else:
                            message += Fore.GREEN + "Call :" + Fore.RESET + str(data[11]).capitalize() + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(data[12]) + "\n"

                    elif int(data[8]) == 9:  # media_wa_type 9, Application
                        chain = data[17].split(b'\x77\x02')[0]
                        i = chain.rfind(b"Media/")
                        b = len(chain)
                        if i == -1:  # Image doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')

                        if data[11]:  # media_caption
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb + " - " + html.escape(data[11])
                            else:
                                message += Fore.GREEN + "Name: " + Fore.RESET + thumb + Fore.GREEN + " - Caption: " + Fore.RESET + data[11] + "\n"
                        else:
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb
                            else:
                                message += Fore.GREEN + "Name: " + Fore.RESET + thumb + "\n"

                        if data[12] >= 0:
                            if report_var == 'EN':
                                report_msj += " " + size_file(data[9]) + " - " + str(data[12]) + " Pages"
                            elif report_var == 'ES':
                                report_msj += " " + size_file(data[9]) + " - " + str(data[12]) + " Páginas"
                            else:
                                message += Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size: " + Fore.RESET + str(data[9]) + " bytes " + size_file(data[9]) + Fore.GREEN + " - Pages: " + Fore.RESET + str(data[12]) + "\n"
                        else:
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += " " + size_file(data[9])
                            else:
                                message += Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size: " + Fore.RESET + str(data[9]) + " bytes " + size_file(data[9]) + "\n"

                        if os.path.isfile(thumb + ".jpg") is False:
                            distutils.dir_util.mkpath("./Media/WhatsApp Documents/Sent")
                            if thumb == "Not downloaded":
                                if int(data[1]) == 1:
                                    thumb = "./Media/WhatsApp Documents/Sent/DOC-" + str(data[2]) + "-NotDownloaded"
                                else:
                                    thumb = "./Media/WhatsApp Documents/DOC-" + str(data[2]) + "-NotDownloaded"

                            with open(thumb + ".jpg", 'wb') as profile_file:
                                if data[19]:
                                    profile_file.write(data[19])
                                elif data[22]:
                                    profile_file.write(data[22])
                                else:
                                    profile_file.write(b"")

                            if report_var == 'None':
                                message += "Thumbnail was saved on local path '" + thumb + ".jpg'\n"

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + ".jpg' width=\"100\" height=\"100\"/></a>"

                    elif int(data[8]) == 10:  # media_wa_type 10, Video/Audio call lost
                        if report_var == 'EN':
                            report_msj += "&#128222; Missed" + str(data[11]).capitalize() + " call"
                        elif report_var == 'ES':
                            report_msj += "&#128222; " + str(data[11]).capitalize() + " llamada perdida"
                        else:
                            message += Fore.GREEN + "Message: " + Fore.RESET + "Missed " + str(data[11]).capitalize() + " call\n"

                    elif int(data[8]) == 11:  # media_wa_type 11, Waiting for message
                        if report_var == 'EN':
                            report_msj += "<p style=\"color:#FF0000\";>&#9842; Waiting for message. This may take time </p>"
                        elif report_var == 'ES':
                            report_msj += "<p style=\"color:#FF0000\";>&#9842; Esperando mensaje. Esto puede tomar tiempo</p>"
                        else:
                            message += Fore.GREEN + "Message: " + Fore.RESET + "Waiting for message. This may take time\n"

                    elif int(data[8]) == 13:  # media_wa_type 13 Gif
                        chain = data[17].split(b'\x77\x02')[0]
                        i = chain.rfind(b"Media/")
                        b = len(chain)
                        if i == -1:  # Gif doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')

                        if data[11]:  # media_caption
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb + " - " + html.escape(data[11])
                            else:
                                message += Fore.GREEN + "Name: " + Fore.RESET + thumb + Fore.GREEN + " - Caption: " + Fore.RESET + data[11] + "\n"
                        else:
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += thumb
                            else:
                                message += Fore.GREEN + "Name: " + Fore.RESET + thumb + "\n"

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += " - Gif - " + size_file(data[9]) + " " + duration_file(data[12])
                        else:
                            message += Fore.GREEN + "Type: " + Fore.RESET + "Gif" + Fore.GREEN + " - Size: " + Fore.RESET + str(data[9]) + " bytes " + size_file(data[9]) + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(data[12]) + "\n"

                        if os.path.isfile(thumb) is False:
                            distutils.dir_util.mkpath("./Media/WhatsApp Animated Gifs/Sent")
                            if thumb == "Not downloaded":
                                if int(data[1]) == 1:
                                    thumb = "./Media/WhatsApp Animated Gifs/Sent/VID-" + str(data[2]) + "-NotDownloaded.mp4"
                                else:
                                    thumb = "./Media/WhatsApp Animated Gifs/VID-" + str(data[2]) + "-NotDownloaded.mp4"

                            with open(thumb, 'wb') as profile_file:
                                if data[19]:  # raw_data exists
                                    profile_file.write(data[19])
                                elif data[22]:  # Gets the thumbnail of the message_thumbnails
                                    profile_file.write(data[22])
                                else:
                                    profile_file.write(b"")

                            if report_var == 'None':
                                message += "Thumbnail was saved on local path '" + thumb + "'\n"

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += "<br> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + "'width=\"100\" height=\"100\"/></a>"

                    elif int(data[8]) == 14:  # media_wa_type 14  Vcard multiples
                        concat = ""
                        chain = str(data[19]).split('BEGIN:VCARD')
                        for i in chain[1:]:
                            concat += "BEGIN:VCARD"
                            concat += i.split('END:VCARD')[0] + "END:VCARD"

                        if report_var == 'EN':
                            report_msj += html.escape(data[10]) + "<br>&#9742;  Contact vCard</br>" + html.escape(concat)
                        elif report_var == 'ES':
                            report_msj += html.escape(data[10]) + "<br>&#9742;  Contacto vCard</br>" + html.escape(concat)
                        else:
                            message += Fore.GREEN + "Name: " + Fore.RESET + data[10] + Fore.GREEN + " - Type:" + Fore.RESET + " Contact vCard" + concat + "\n"

                    elif int(data[8]) == 15:  # media_wa_type 15, Deleted Object
                        if int(data[16]) == 5:  # edit_version 5, deleted for me
                            if report_var == 'EN':
                                report_msj += "Message deleted for Me"
                            elif report_var == 'ES':
                                report_msj += "Mensaje eliminado para mí"
                            else:
                                message += Fore.GREEN + "Message: " + Fore.RESET + "Message deleted for Me\n"

                        elif int(data[16]) == 7:  # edit_version 7, deleted for all
                            if report_var == 'EN':
                                report_msj += "Message deleted for all participants"
                            elif report_var == 'ES':
                                report_msj += "Mensaje eliminado para todos los destinatarios"
                            else:
                                message += Fore.GREEN + "Message: " + Fore.RESET + "Message deleted for all participants\n"

                    elif int(data[8]) == 16:  # media_wa_type 16, Share location
                        caption = ""
                        if data[11]:
                            caption = data[11]

                        if report_var == 'EN':
                            report_msj += "Real time location (" + str(data[13]) + "," + str(data[14]) + ") - " + html.escape(caption) + "\n"
                            report_msj += " <br><a href=\"https://www.google.es/maps/search/(" + str(data[13]) + "," + str(data[14]) + ")\" target=\"_blank\"> <img src=\"http://maps.google.com/maps/api/staticmap?center=" + str(data[13]) + "," + str(data[14]) + "&zoom=16&size=300x150&markers=size:mid|color:red|label:A|" + str(data[13]) + "," + str(data[14]) + "&sensor=false\"/></a>"
                        elif report_var == 'ES':
                            report_msj += "Ubicación en tiempo real (" + str(data[13]) + "," + str(data[14]) + ") - " + html.escape(caption) + "\n"
                            report_msj += "<br><iframe width='300' height='150' id='gmap_canvas' src='https://maps.google.com/maps?q={}%2C{}&t=&z=15&ie=UTF8&iwloc=&output=embed' frameborder='0' scrolling='no' marginheight='0' marginwidth='0'></iframe>".format(str(data[13]), str(data[14]))
                        else:
                            message += Fore.GREEN + "Type: " + Fore.RESET + "Real time location " + Fore.GREEN + "- Caption: " + Fore.RESET + caption + Fore.GREEN + " - Lat: " + Fore.RESET + str(data[13]) + Fore.GREEN + " - Long: " + Fore.RESET + str(data[14]) + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(data[12]) + "\n"

                    elif int(data[8]) == 20:  # media_wa_type 20 Sticker
                        chain = data[17].split(b'\x77\x02')[0]
                        i = chain.rfind(b"Media/")
                        b = len(chain)
                        if i == -1:  # Audio doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = (b"./" + chain[i:b]).decode('UTF-8', 'ignore')

                        if (report_var == 'EN') or (report_var == 'ES'):
                            report_msj += " Sticker - " + size_file(data[9]) + "<br> <a href=\"." + thumb + "\" target=\"_blank\"> <IMG SRC='." + thumb + "'width=\"100\" height=\"100\"/></a>"
                        else:
                            message += Fore.GREEN + "Type: " + Fore.RESET + "Sticker" + Fore.GREEN + " - Size: " + Fore.RESET + str(data[9]) + " bytes " + size_file(data[9]) + Fore.GREEN + "\n"

                    if data[20]:
                        if int(data[20]) == 1:
                            if (report_var == 'EN') or (report_var == 'ES'):
                                report_msj += "<br> &#127775;"
                            else:
                                message += Fore.YELLOW + "Starred message " + Fore.RESET + "\n"

                    main_status, report_status = status(int(data[3]))

                    if (report_var == 'EN') or (report_var == 'ES'):
                        report_time = time.strftime('%d-%m-%Y %H:%M', time.localtime(data[5] / 1000))
                        if (report_name == "Me") or (report_name == "&#128227; Me") or (report_name == "Yo") or (report_name == "&#128227; Yo"):
                            rep_med += """
            <li>
                <div class="bubble2">
                    <span class="personSay2">""" + report_msj + """</span><br>
                    <span class="time2 round">""" + report_time + "&nbsp" + report_status + """</span><br>
                </div>
            </li>"""
                        elif (report_name == "System Message") or (report_name == "Mensaje de Sistema"):
                            rep_med += """
            <li>
                <div class="bubble-system"> 
                    <span class="time-system round">""" + report_time + "&nbsp" + report_status + """</span><br>
                    <span class="person-System">""" + report_msj + """</span><br>
                </div>
            </li>"""
                        else:
                            rep_med += """
            <li>
                <div class="bubble"> 
                    <span class="personName">""" + report_name + """</span><br>
                    <span class="personSay">""" + report_msj + """</span><br>
                    <span class="time round">""" + report_time + "&nbsp" + report_status + """</span><br>
                </div>
            </li>"""
                    elif report_var == 'None':
                        message += Fore.GREEN + "Timestamp: " + Fore.RESET + time.strftime('%d-%m-%Y %H:%M', time.localtime(data[5] / 1000)) + Fore.GREEN + " - Status: " + Fore.RESET + main_status + "\n"
                        print(message)
                n_mes += 1

            except Exception as e:
                print("\nError showing message details: {}, Message ID {}, Timestamp {}".format(e, str(data[23]), time.strftime('%d-%m-%Y %H:%M', time.localtime(data[5] / 1000))))
                n_mes += 1
                continue

        if report_var != "None":
            report(rep_med, report_html)

    except Exception as e:
        print("\nAn error occurred connecting to the database", e)


def info(opt):
    """ Function that show info """
    if opt == '1':  # Status
        print(Fore.RED + "Status" + Fore.RESET)
        rep_med = ""
        sql_string = " SELECT messages.key_remote_jid, messages.key_from_me, messages.key_id, messages.status, messages.data, messages.timestamp, messages.media_url, messages.media_mime_type," \
                     " messages.media_wa_type, messages.media_size, messages.media_name, messages.media_caption, messages.media_duration, messages.latitude, messages.longitude, " \
                     " messages.remote_resource, messages.edit_version, messages.thumb_image, messages.recipient_count, messages.raw_data, messages.starred, messages.quoted_row_id, " \
                     " message_thumbnails.thumbnail, messages._id, messages.forwarded  FROM messages LEFT JOIN message_thumbnails ON messages.key_id = message_thumbnails.key_id WHERE messages.key_remote_jid='status@broadcast'"
        sql_count = "SELECT COUNT(*) FROM messages WHERE key_remote_jid='status@broadcast'"
        print("Loading data ...")
        result = cursor.execute(sql_count)
        result = cursor.fetchone()
        print("Number of messages: {}".format(str(result[0])))
        sql_consult = cursor.execute(sql_string)
        report_html = "./reports/report_status.html"
        messages(sql_consult, result[0], report_html)
        print("[i] Finished")

    elif opt == '2':  # Calls
        print(Fore.RED + "Calls" + Fore.RESET)
        rep_med = ""
        epoch_start = "0"
        epoch_end = str(1000 * int(time.mktime(time.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M'))))

        if args.time_start:
            epoch_start = 1000 * int(time.mktime(time.strptime(args.time_start, '%d-%m-%Y %H:%M')))
        if args.time_end:
            epoch_end = 1000 * int(time.mktime(time.strptime(args.time_end, '%d-%m-%Y %H:%M')))

        sql_string = "SELECT jid.raw_string, call_log.from_me, call_log.timestamp, call_log.video_call, call_log.duration FROM call_log LEFT JOIN jid ON call_log.jid_row_id = jid._id WHERE " \
                     " call_log.timestamp BETWEEN " + str(epoch_start) + " AND " + str(epoch_end) + ";"
        sql_count = "SELECT count(*) FROM call_log WHERE timestamp BETWEEN " + str(epoch_start) + " AND " + str(epoch_end) + ";"
        print("Loading data ...")
        result = cursor.execute(sql_count)
        result = cursor.fetchone()
        print("Number of messages: {}".format(str(result[0])))
        consult = cursor.execute(sql_string)
        for data in consult:
            if report_var == 'None':
                message = Fore.RED + "\n--------------------------------------------------------------------------------" + Fore.RESET + "\n"

            if data[1] == 1:  # I Call
                if report_var == 'EN':
                    report_name = "Me"
                elif report_var == 'ES':
                    report_name = "Yo"
                else:
                    message += Fore.GREEN + "From:" + Fore.RESET + " Me " + Fore.GREEN + "to " + Fore.RESET +  str(data[0]).split('@')[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + "\n"

            else:  # Somebody calls me
                if report_var == 'EN' or report_var == 'ES':
                    report_name = str(data[0]).split('@')[0] + gets_name(data[0])
                else:
                    message += Fore.GREEN + "From: " + Fore.RESET + str(data[0]).split('@')[0] + Fore.YELLOW + gets_name(data[0]) + Fore.RESET + Fore.GREEN + " to " + Fore.RESET + "Me\n"

            if data[3] == 0:   # Audio
                if report_var == 'EN':
                    report_msj = "&#127897; Incoming audio call<br>"
                elif report_var == 'ES':
                    report_msj = "&#127897; Audio llamada entrante<br>"
                else:
                    message += Fore.GREEN + "Message: " + Fore.RESET + "Incoming audio call\n"

            else:   # Video
                if report_var == 'EN':
                    report_msj = "&#127909; Incoming video call<br>"
                elif report_var == 'ES':
                    report_msj = "&#127909; Video llamada entrante<br>"
                else:
                    message += Fore.GREEN + "Message: " + Fore.RESET + "Incoming video call\n"

            if report_var == 'None':
                message += Fore.GREEN + "Timestamp: " + Fore.RESET + time.strftime('%d-%m-%Y %H:%M', time.localtime(data[2] / 1000))

            if data[4] > 0:
                if report_var == 'EN':
                    report_msj += "Established - Duration: " + duration_file(data[4]) + "<br>"
                elif report_var == 'ES':
                    report_msj += "Establecida - Duración: " + duration_file(data[4]) + "<br>"
                else:
                    message += Fore.GREEN + " - Status: " + Fore.RESET + "Established" + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(data[4])

            else:
                if report_var == 'EN':
                    report_msj += "Lost <br>"
                elif report_var == 'ES':
                    report_msj += "Perdida <br>"
                else:
                    message += Fore.GREEN + " - Status: " + Fore.RESET + "Lost"

            report_status = ""
            if report_var == 'EN':
                report_time = time.strftime('%d-%m-%Y %H:%M', time.localtime(data[2] / 1000))
                if report_name == "Me":
                    rep_med += """
                                       <li>
                                       <div class="bubble2"> <span class="personName">""" + report_name + """</span> <br>
                                           <span class="personSay2">""" + report_msj + """</span> </div>
                                       <span class=" time2 round ">""" + report_time + "&nbsp" + report_status + """</span> </li>"""
                else:
                    rep_med += """
                                       <li>
                                       <div class="bubble"> <span class="personName2">""" + report_name + """</span> <br>
                                           <span class="personSay">""" + report_msj + """</span> </div>
                                       <span class=" time round ">""" + report_time + "&nbsp" + report_status + """</span> </li>"""
            elif report_var == 'ES':
                report_time = time.strftime('%d-%m-%Y %H:%M', time.localtime(data[2] / 1000))
                if report_name == "Yo":
                    rep_med += """
                                       <li>
                                       <div class="bubble2"> <span class="personName">""" + report_name + """</span> <br>
                                           <span class="personSay2">""" + report_msj + """</span> </div>
                                       <span class=" time2 round ">""" + report_time + "&nbsp" + report_status + """</span> </li>"""
                else:
                    rep_med += """
                                       <li>
                                       <div class="bubble"> <span class="personName2">""" + report_name + """</span> <br>
                                           <span class="personSay">""" + report_msj + """</span> </div>
                                       <span class=" time round ">""" + report_time + "&nbsp" + report_status + """</span> </li>"""
            else:
                print(message)

        if report_var != "None":
            report_html = "./reports/report_calls.html"
            print("[+] Creating report ...")
            report(rep_med, report_html)
        print("\n[i] Finished")

    elif opt == '3':  # Chat list
        print(Fore.RED + "Actives chat list" + Fore.RESET)

        sql_string_consult = "SELECT key_remote_jid FROM chat_list ORDER BY sort_timestamp DESC"
        sql_consult_chat = cursor.execute(sql_string_consult)
        for i in sql_consult_chat:
            show = i[0]
            if str(i[0]).split('@')[1] == 's.whatsapp.net':
                show = str(i[0]).split('@')[0]
            print("{} {}".format(show, Fore.YELLOW + gets_name(i[0]) + Fore.RESET))


def get_configs():
    """ Function that gets report config"""
    global logo, company, record, unit, examiner, notes
    config_report = ConfigParser()
    try:
        config_report.read('./cfg/settings.cfg')
        logo = config_report.get('report', 'logo')
        company = config_report.get('report', 'company')
        record = config_report.get('report', 'record')
        unit = config_report.get('report', 'unit')
        examiner = config_report.get('report', 'examiner')
        notes = config_report.get('report', 'notes')
    except Exception as e:
        print("The 'settings.cfg' file is missing or corrupt!")


def extract(obj, total):
    """ Functions that extracts thumbnails"""
    i = 1
    for data in obj:
        try:
            chain = str(data[2]).split('w\\x02')[0]
            a = chain.rfind("Media/")
            if a == -1:  # Image doesn't exist
                thumb = "Not downloaded"
            else:
                a = chain.rfind("/")
                b = len(chain)
                thumb = "./thumbnails" + (str(data[2]))[a:b]

            if os.path.isfile(thumb) is False:
                distutils.dir_util.mkpath("./thumbnails")

            if thumb == "Not downloaded":
                epoch = time.strftime("%Y%m%d", time.localtime((int(data[4]) / 1000)))
                thumb = "./thumbnails/IMG-" + epoch + "-" + str(int(data[4]) / 1000) + "-NotDownloaded.jpg"
            if int(data[1]) == 9:
                thumb += ".jpg"

            with open(thumb, 'wb') as profile_file:
                if data[3]:  # raw_data exists
                    profile_file.write(data[3])
                elif data[5]:  # Gets the thumbnail of the message_thumbnails
                    profile_file.write(data[5])
                else:
                    profile_file.write(b"")

            sys.stdout.write("\rExtracting thumbnail " + str(i) + " / " + str(total))
            sys.stdout.flush()
            i += 1
        except Exception as e:
            print("\nError extracting: {}, Message ID {}".format(e, str(data[8])))

    print("\n")
    print("Extraction Complete. Thumbnails save in './thumbnails' path")


#  Initializing
if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="To start choose a database and a mode with options")
    parser.add_argument("database", help="Database file path - './msgstore.db' by default", metavar="DATABASE", nargs='?', default="./msgstore.db")
    mode_parser = parser.add_mutually_exclusive_group()
    mode_parser.add_argument("-m", "--messages", help="*** Message Mode ***", action="store_true")
    mode_parser.add_argument("-i", "--info", help="*** Info Mode *** 1 Status - 2 Calls log - 3 Actives chat list")
    mode_parser.add_argument("-e", "--extract", help="*** Extract Mode ***", action="store_true")
    user_parser = parser.add_mutually_exclusive_group()
    user_parser.add_argument("-u", "--user", help="Show chat with a phone number, ej. 34123456789")
    user_parser.add_argument("-ua", "--user_all", help="Show messages made by a phone number")
    user_parser.add_argument("-g", "--group", help="Show chat with a group number, ej. 34123456-14508@g.us")
    user_parser.add_argument("-a", "--all", help="Show all chat messages classified by phone number, group number and broadcast list", action="store_true")
    parser.add_argument("-wa", "--wa_file", help="Show names along with numbers")
    parser.add_argument("-t", "--text", help="Show messages by text match")
    parser.add_argument("-w", "--web", help="Show messages made by Whatsapp Web", action="store_true")
    parser.add_argument("-s", "--starred", help="Show messages starred by owner", action="store_true")
    parser.add_argument("-b", "--broadcast", help="Show messages send by broadcast", action="store_true")
    parser.add_argument("-ts", "--time_start", help="Show messages by start time (dd-mm-yyyy HH:MM)")
    parser.add_argument("-te", "--time_end", help="Show messages by end time (dd-mm-yyyy HH:MM)")
    parser.add_argument("-r", "--report", help='Make an html report in \'EN\' English or \'ES\' Spanish. If specified together with flag -a, makes a report for each chat', const='EN', nargs='?', choices=['EN', 'ES'])
    filter_parser = parser.add_mutually_exclusive_group()
    filter_parser.add_argument("-tt", "--type_text", help="Show text messages", action="store_true")
    filter_parser.add_argument("-ti", "--type_image", help="Show image messages", action="store_true")
    filter_parser.add_argument("-ta", "--type_audio", help="Show audio messages", action="store_true")
    filter_parser.add_argument("-tv", "--type_video", help="Show video messages", action="store_true")
    filter_parser.add_argument("-tc", "--type_contact", help="Show contact messages", action="store_true")
    filter_parser.add_argument("-tl", "--type_location", help="Show location messages", action="store_true")
    filter_parser.add_argument("-tx", "--type_call", help="Show audio/video call messages", action="store_true")
    filter_parser.add_argument("-tp", "--type_application", help="Show application messages", action="store_true")
    filter_parser.add_argument("-tg", "--type_gif", help="Show GIF messages", action="store_true")
    filter_parser.add_argument("-td", "--type_deleted", help="Show deleted object messages", action="store_true")
    filter_parser.add_argument("-tr", "--type_share", help="Show Real time location messages", action="store_true")
    filter_parser.add_argument("-tk", "--type_stickers", help="Show Stickers messages", action="store_true")
    filter_parser.add_argument("-tm", "--type_system", help="Show system messages", action="store_true")
    args = parser.parse_args()
    init()

    if len(sys.argv) == 1:
        help()
    else:
        if args.messages:
            if args.wa_file:
                names(args.wa_file)
            cursor, cursor_rep = db_connect(args.database)
            sql_string = "SELECT messages.key_remote_jid, messages.key_from_me, messages.key_id, messages.status, messages.data, messages.timestamp, messages.media_url, messages.media_mime_type," \
                         " messages.media_wa_type, messages.media_size, messages.media_name, messages.media_caption, messages.media_duration, messages.latitude, messages.longitude, " \
                         " messages.remote_resource, messages.edit_version, messages.thumb_image, messages.recipient_count, messages.raw_data, messages.starred, messages.quoted_row_id, " \
                         " message_thumbnails.thumbnail, messages._id, messages.forwarded  FROM messages LEFT JOIN message_thumbnails ON messages.key_id = message_thumbnails.key_id WHERE messages.timestamp BETWEEN '"
            sql_count = "SELECT COUNT(*) FROM messages LEFT JOIN message_thumbnails ON messages.key_id = message_thumbnails.key_id WHERE messages.timestamp BETWEEN '"
            try:
                epoch_start = "0"
                """ current date in Epoch milliseconds string """
                epoch_end = str(1000 * int(time.mktime(time.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M'))))

                if args.time_start:
                    epoch_start = 1000 * int(time.mktime(time.strptime(args.time_start, '%d-%m-%Y %H:%M')))
                if args.time_end:
                    epoch_end = 1000 * int(time.mktime(time.strptime(args.time_end, '%d-%m-%Y %H:%M')))
                sql_string += str(epoch_start) + "' AND '" + str(epoch_end) + "'"
                sql_count += str(epoch_start) + "' AND '" + str(epoch_end) + "'"

                if args.text:
                    sql_string += " AND messages.data LIKE '%" + str(args.text) + "%'"
                    sql_count += " AND messages.data LIKE '%" + str(args.text) + "%'"
                if args.web:
                    sql_string += " AND messages.key_id LIKE '3EB0%'"
                    sql_count += " AND messages.key_id LIKE '3EB0%'"
                if args.starred:
                    sql_string += " AND messages.starred = 1"
                    sql_count += " AND messages.starred = 1"
                if args.broadcast:
                    sql_string += " AND messages.remote_resource LIKE '%broadcast%'"
                    sql_count += " AND messages.remote_resource LIKE '%broadcast%'"
                if args.report:
                    report_var = args.report
                    get_configs()
                if args.type_text:
                    sql_string += " AND messages.media_wa_type = 0"
                    sql_count += " AND messages.media_wa_type = 0"
                if args.type_image:
                    sql_string += " AND messages.media_wa_type = 1"
                    sql_count += " AND messages.media_wa_type = 1"
                if args.type_audio:
                    sql_string += " AND messages.media_wa_type = 2"
                    sql_count += " AND messages.media_wa_type = 2"
                if args.type_video:
                    sql_string += " AND messages.media_wa_type = 3"
                    sql_count += " AND messages.media_wa_type = 3"
                if args.type_contact:
                    sql_string += " AND messages.media_wa_type = 4 OR messages.media_wa_type = 14"
                    sql_count += " AND messages.media_wa_type = 4 OR messages.media_wa_type = 14"
                if args.type_location:
                    sql_string += " AND messages.media_wa_type = 5"
                    sql_count += " AND messages.media_wa_type = 5"
                if args.type_call:
                    sql_string += " AND messages.media_wa_type = 8 OR messages.media_wa_type = 10"
                    sql_count += " AND messages.media_wa_type = 8 OR messages.media_wa_type = 10"
                if args.type_application:
                    sql_string += " AND messages.media_wa_type = 9"
                    sql_count += " AND messages.media_wa_type = 9"
                if args.type_gif:
                    sql_string += " AND messages.media_wa_type = 13"
                    sql_count += " AND messages.media_wa_type = 13"
                if args.type_deleted:
                    sql_string += " AND messages.media_wa_type = 15"
                    sql_count += " AND messages.media_wa_type = 15"
                if args.type_share:
                    sql_string += " AND messages.media_wa_type = 16"
                    sql_count += " AND messages.media_wa_type = 16"
                if args.type_stickers:
                    sql_string += " AND messages.media_wa_type = 20"
                    sql_count += " AND messages.media_wa_type = 20"
                if args.type_system:
                    sql_string += " AND messages.media_wa_type = 0 AND messages.status = 6"
                    sql_count += " AND messages.media_wa_type = 0 AND messages.status = 6"

                if args.user_all:
                    sql_string += " AND (messages.key_remote_jid LIKE '%" + str(args.user_all) + "%@s.whatsapp.net' OR messages.remote_resource LIKE '%" + str(args.user_all) + "%')"
                    sql_count += " AND (messages.key_remote_jid LIKE '%" + str(args.user_all) + "%@s.whatsapp.net' OR messages.remote_resource LIKE '%" + str(args.user_all) + "%')"
                    arg_user = args.user_all
                    report_html = "./reports/report_user_all_" + args.user_all + ".html"

                elif args.user:
                    sql_string += " AND messages.key_remote_jid LIKE '%" + str(args.user) + "%@s.whatsapp.net'"
                    sql_count += " AND messages.key_remote_jid LIKE '%" + str(args.user) + "%@s.whatsapp.net'"
                    report_html = "./reports/report_user_chat_" + args.user + ".html"
                    arg_user = args.user

                elif args.group:
                    sql_string += " AND messages.key_remote_jid LIKE '%" + str(args.group) + "%'"
                    sql_count += " AND messages.key_remote_jid LIKE '%" + str(args.group) + "%'"
                    arg_group = args.group
                    if arg_group.split("@")[1] == "g.us":
                        report_html = "./reports/report_group_chat_" + args.group + ".html"
                        report_group, color = participants(args.group)
                    else:
                        report_html = "./reports/report_broadcast_chat_" + args.group + ".html"
                        report_group, color = participants(args.group)

                elif args.all:
                    get_configs()
                    sql_string_consult = "SELECT key_remote_jid FROM chat_list ORDER BY sort_timestamp DESC"
                    sql_consult_chat = cursor.execute(sql_string_consult)
                    chats_live = []
                    for i in sql_consult_chat:
                        chats_live.append(i[0])
                    report_med = " "
                    print("Loading data ...")
                    for i in chats_live:
                        sql_string_copy = sql_string
                        sql_count_copy = sql_count

                        if i.split('@')[1] == "g.us":
                            if report_var == 'EN':
                                report_html = "./reports/report_group_chat_" + i + ".html"
                                report_med += "<tr><th>Group</th><th><a href=\"report_group_chat_" + i + ".html" + "\" target=\"_blank\"> " + i + gets_name(i) + "</a></th></tr>"
                            elif report_var == 'ES':
                                report_html = "./reports/report_group_chat_" + i + ".html"
                                report_med += "<tr><th>Grupo</th><th><a href=\"report_group_chat_" + i + ".html" + "\" target=\"_blank\"> " + i + gets_name(i) + "</a></th></tr>"
                            sql_string_copy += " AND messages.key_remote_jid LIKE '%" + i + "%'"
                            sql_count_copy += " AND messages.key_remote_jid LIKE '%" + i + "%'"
                            arg_group = i
                            arg_user = ""
                            result = cursor.execute(sql_count_copy)
                            result = cursor.fetchone()
                            print("\nNumber of messages: {}".format(str(result[0])))
                            print(Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET)
                            print(Fore.CYAN + "GROUP CHAT " + i + Fore.RESET + Fore.YELLOW + gets_name(i) + Fore.RESET)
                            report_group, color = participants(arg_group)

                        elif i.split('@')[1] == "s.whatsapp.net":
                            if report_var == 'EN':
                                report_med += "<tr><th>User</th><th><a href=\"report_user_chat_" + i.split('@')[0] + ".html" + "\" target=\"_blank\"> " + i.split('@')[0] + gets_name(i) + "</a></th></tr>"
                                report_html = "./reports/report_user_chat_" + i.split('@')[0] + ".html"
                            elif report_var == 'ES':
                                report_med += "<tr><th>Usuario</th><th><a href=\"report_user_chat_" + i.split('@')[0] + ".html" + "\" target=\"_blank\"> " + i.split('@')[0] + gets_name(i) + "</a></th></tr>"
                                report_html = "./reports/report_user_chat_" + i.split('@')[0] + ".html"
                            sql_string_copy += " AND messages.key_remote_jid LIKE '%" + i + "%'"
                            sql_count_copy += " AND messages.key_remote_jid LIKE '%" + i + "%'"
                            arg_group = ""
                            arg_user = i.split('@')[0]
                            result = cursor.execute(sql_count_copy)
                            result = cursor.fetchone()
                            print("\nNumber of messages: {}".format(str(result[0])))
                            print(Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET)
                            print(Fore.CYAN + "USER CHAT " + arg_user + Fore.RESET + Fore.YELLOW + gets_name(i) + Fore.RESET)
                            report_group = ""

                        elif i.split('@')[1] == "broadcast":
                            if report_var == 'EN':
                                report_med += "<tr><th>Broadcast</th><th><a href=\"report_broadcast_chat_" + i.split('@')[0] + ".html" + "\" target=\"_blank\"> " + i + gets_name(i) + "</a></th></tr>"
                                report_html = "./reports/report_broadcast_chat_" + i.split('@')[0] + ".html"
                            elif report_var == 'ES':
                                report_med += "<tr><th>Difusión</th><th><a href=\"report_broadcast_chat_" + i.split('@')[0] + ".html" + "\" target=\"_blank\"> " + i + gets_name(i) + "</a></th></tr>"
                                report_html = "./reports/report_broadcast_chat_" + i.split('@')[0] + ".html"
                            sql_string_copy += " AND messages.key_remote_jid LIKE '%" + i + "%'"
                            sql_count_copy += " AND messages.key_remote_jid LIKE '%" + i + "%'"
                            arg_group = ""
                            arg_user = i
                            result = cursor.execute(sql_count_copy)
                            result = cursor.fetchone()
                            print("\nNumber of messages: {}".format(str(result[0])))
                            print(Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET)
                            print(Fore.CYAN + "BROADCAST CHAT " + i + Fore.RESET + Fore.YELLOW + gets_name(i) + Fore.RESET)
                            report_group, color = participants(arg_user)

                        sql_consult = cursor.execute(sql_string_copy)
                        messages(sql_consult, result[0], report_html)
                        print()

                    if args.report:
                        index_report(report_med, "./reports/index.html")
                    print("\n[i] Finished")
                    exit()

                print("Loading data ...")
                result = cursor.execute(sql_count)
                result = cursor.fetchone()
                print("Number of messages: {}".format(str(result[0])))
                sql_consult = cursor.execute(sql_string)
                messages(sql_consult, result[0], report_html)
                print("\n[i] Finished")

            except Exception as e:
                print("Error:", e)

        elif args.info:
            if args.wa_file:
                names(args.wa_file)
            cursor, cursor_rep = db_connect(args.database)
            if args.report:
                report_var = args.report
                get_configs()
            else:
                report_var = "None"
            info(args.info)

        elif args.extract:
            try:
                cursor, cursor_rep = db_connect(args.database)
                print("Calculating number of images to extract")
                epoch_start = "0"
                """ current date in Epoch milliseconds string """
                epoch_end = str(1000 * int(time.mktime(time.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M'))))

                if args.time_start:
                    epoch_start = 1000 * int(time.mktime(time.strptime(args.time_start, '%d-%m-%Y %H:%M')))
                if args.time_end:
                    epoch_end = 1000 * int(time.mktime(time.strptime(args.time_end, '%d-%m-%Y %H:%M')))

                sql_string = ""
                if args.user_all:
                    sql_string += " AND (messages.key_remote_jid LIKE '%" + str(args.user_all) + "%@s.whatsapp.net' OR messages.remote_resource LIKE '%" + str(args.user_all) + "%@s.whatsapp.net' )"
                elif args.user:
                    sql_string += " AND (messages.key_remote_jid LIKE '%" + str(args.user) + "%@s.whatsapp.net')"
                elif args.group:
                    sql_string += " AND messages.key_remote_jid LIKE '%" + str(args.group) + "%'"

                sql_count = "SELECT COUNT(*) FROM messages LEFT JOIN message_thumbnails ON messages.key_id = message_thumbnails.key_id WHERE messages.timestamp" \
                            " BETWEEN " + str(epoch_start) + " AND " + str(epoch_end) + " AND messages.media_wa_type IN (1, 3, 9, 13) " + sql_string + ";"
                cursor.execute(sql_count)
                result = cursor.fetchone()
                print(result[0], "Images found")
                sql_string_extract = "SELECT messages.key_id, messages.media_wa_type, messages.thumb_image, messages.raw_data, messages.timestamp, message_thumbnails.thumbnail, messages.key_remote_jid, messages.remote_resource, messages._id FROM messages LEFT JOIN message_thumbnails " \
                                     "ON messages.key_id = message_thumbnails.key_id WHERE messages.timestamp BETWEEN " + str(epoch_start) + " AND " + str(epoch_end) + " AND messages.media_wa_type IN (1, 3, 9, 13) " + sql_string + ";"
                sql_consult_extract = cursor.execute(sql_string_extract)
                extract(sql_consult_extract, result[0])
            except Exception as e:
                print("Error extracting:", e)

        elif args.database:
            if args.wa_file:
                names(args.wa_file)
                db_connect(args.database)





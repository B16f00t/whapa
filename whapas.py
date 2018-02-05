#!/usr/bin/python
# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
from colorama import init, Fore
import distutils.dir_util
import argparse
import sqlite3
import os
import time
import zlib
import sys


def banner():
    """ Función Banner """
    print """
     __      __.__                                
    /  \    /  \  |__ _____  ___________    ______
    \   \/\/   /  |  \\\\__  \ \____ \__  \  /  ___/
     \        /|   Y  \/ __ \|  |_> > __ \_\___ \ 
      \__/\  / |___|  (____  /   __(____  /____  >
           \/       \/     \/|__|       \/     \/  
    ---------- Whatsapp Parser Spanish v0.1 -----------
    """


def help():
    """ Función que muestra la ayuda """
    print """    ** Autor: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t
    
    Uso: python whapa.py -h (para ayuda)
    """


def decrypt(db_file, key_file):
    """ Función para descifrar base datos Crypto12 """
    try:
        with open(key_file, "rb") as fh:
            key_data = fh.read()

        key = key_data[126:]
        with open(db_file, "rb") as fh:
            db_data = fh.read()

        iv = db_data[51:67]
        aes = AES.new(key, mode=AES.MODE_GCM, nonce=iv)
        with open("msgstore.db", "wb") as fh:
            fh.write(zlib.decompress(aes.decrypt(db_data[67:-20])))

        print "msgstore.db.crypt12 descifrado, msgstore.db creado."
    except Exception as e:
        print "Ocurrío un error descifrando la base de datos", e


def db_connect(db):
    """ Función para conectar con la base de datos """
    if os.path.exists(db):
        try:
            with sqlite3.connect(db) as conn:
                global cursor
                cursor = conn.cursor()
            print args.database, "Conectado a la base de datos\n"
            return cursor
        except Exception as e:
            print "Error conectando con la base de datos, ", e
    else:
        print "La base de datos no existe"
        exit()


def reply(txt):
    """ Función que busca los mensajes respuesta"""
    sql_reply_str = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, remote_resource, edit_version, thumb_image, recipient_count, raw_data, starred, quoted_row_id FROM messages_quotes WHERE _id = " + str(txt) + ";"
    sql_answer = cursor.execute(sql_reply_str)
    rep = sql_answer.fetchone()
    ans = ""
    if int(rep[1]) == 1 and (str(rep[0]).split('@'))[1] == "g.us":
        ans = "Mí"
    elif int(rep[1]) == 1 and (str(rep[0]).split('@'))[1] == "s.whatsapp.net":
        ans = "Mí"
    elif int(rep[1]) == 1 and (str(rep[0]).split('@'))[1] == "broadcast":
        ans = "Mí"
    elif int(rep[1]) == 0 and (str(rep[0]).split('@'))[1] == "g.us":
        ans = (str(rep[15]).split('@'))[0]
    elif int(rep[1]) == 0 and (str(rep[0]).split('@'))[1] == "s.whatsapp.net":
        ans = (str(rep[0]).split('@'))[0]
    elif int(rep[1]) == 0 and (str(rep[0]).split('@'))[1] == "broadcast":
        ans = (str(rep[15]).split('@'))[0]

    if int(rep[8]) == 0:
        ans = ans.decode('utf-8') + Fore.GREEN + " - Mensaje: " + Fore.RESET + rep[4]

    elif int(rep[8]) == 1:
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:
            thumb = "No descargado"
        else:
            thumb = "/" + (str(rep[17]))[i:b]
        if rep[11]:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + thumb + Fore.GREEN + " - Titulo: " + Fore.RESET + rep[11]
        else:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + thumb
        ans = ans + Fore.GREEN + " - Tipo: " + Fore.RESET + "imagen/jpeg" + Fore.GREEN + " - Tamaño: ".decode('utf-8') + Fore.RESET + str(rep[9]) + " bytes " + str(size_file(int(rep[9])))

    elif int(rep[8]) == 2:
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:
            thumb = "No descargado"
        else:
            thumb = "/" + (str(rep[17]))[i:b]
        ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + thumb + Fore.GREEN + " - Tipo: " + Fore.RESET + rep[7] + Fore.GREEN + " - Tamaño: ".decode('utf-8') + Fore.RESET + str(rep[9]) + " bytes " + str(size_file(int(rep[9]))) + Fore.GREEN + " - Duración: ".decode('utf-8') + Fore.RESET + str(duration_file(rep[12]))

    elif int(rep[8]) == 3:
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:
            thumb = "No descargado"
        else:
            thumb = "/" + (str(rep[17]))[i:b]
        if rep[11]:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + thumb + Fore.GREEN + " - Titulo: " + Fore.RESET + rep[11]
        else:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + thumb
            print ans
        ans = ans + Fore.GREEN + " - Tipo: " + Fore.RESET + str(rep[7]) + Fore.GREEN + " - Tamaño: ".decode('utf-8') + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9])) + Fore.GREEN + " - Duración: ".decode('utf-8') + Fore.RESET + duration_file(rep[12])

    elif int(rep[8]) == 4:
        ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + rep[10] + Fore.GREEN + " - Tipo:" + Fore.RESET + " Contacto vCard"

    elif int(rep[8]) == 5:
        if rep[6]:
            if rep[10]:
                ans = ans.decode('utf-8') + Fore.GREEN + " - Url: " + Fore.RESET + rep[6] + Fore.GREEN + " - Nombre: " + Fore.RESET + rep[10]
            else:
                ans = ans.decode('utf-8') + Fore.GREEN + " - Url: " + Fore.RESET + rep[6]
        else:
            if rep[10]:
                ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + rep[10]
        ans = ans + Fore.GREEN + " - Tipo:" + Fore.RESET + " Localización".decode('utf-8') + Fore.GREEN + " - Lat: " + Fore.RESET + str(rep[13]) + Fore.GREEN + " - Long: " + Fore.RESET + str(rep[14])

    elif int(rep[8]) == 8:
        ans = ans.decode('utf-8') + Fore.GREEN + " - Llamada: " + Fore.RESET + rep[11] + Fore.GREEN + " - Duración: ".decode('utf-8') + Fore.RESET + str(duration_file(rep[12]))

    elif int(rep[8]) == 9:
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:
            thumb = "No descargado"
        else:
            thumb = "/" + chain[i:b]
        if rep[11]:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + thumb + Fore.GREEN + " - Titulo: " + Fore.RESET + rep[11]
        else:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + thumb
        if int(rep[12]) > 0:
            ans = ans + Fore.GREEN + " - Tipo: " + Fore.RESET + rep[7] + Fore.GREEN + " - Tamaño: ".decode('utf-8') + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9])) + Fore.GREEN + " - Páginas: ".decode('utf-8') + Fore.RESET + str(rep[12])
        else:
            ans = ans + Fore.GREEN + " - Tipo: " + Fore.RESET + rep[7] + Fore.GREEN + " - Tamaño: ".decode('utf-8') + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9]))

    elif int(rep[8]) == 10:
        ans = ans.decode('utf-8') + Fore.GREEN + " - Mensaje: " + Fore.RESET + rep[11] + " llamada perdida"

    elif int(rep[8]) == 13:
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:
            thumb = "No descargado"
        else:
            thumb = "/" + (str(rep[17]))[i:b]
        if rep[11]:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + thumb + Fore.GREEN + " - Titulo: " + Fore.RESET + rep[11]
        else:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Nombre: " + Fore.RESET + thumb
        ans = ans + Fore.GREEN + " - Tipo: " + Fore.RESET + "Gif" + Fore.GREEN + " - Tamaño: ".decode('utf-8') + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9])) + Fore.GREEN + " - Duración: ".decode('utf-8') + Fore.RESET + str(duration_file(rep[12]))

    elif int(rep[8]) == 15:
        if int(rep[16]) == 5:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Mensaje:" + Fore.RESET + " Mensaje eliminado para mi"
        elif int(rep[16]) == 7:
            ans = ans.decode('utf-8') + Fore.GREEN + " - Mensaje:" + Fore.RESET + " Mensaje eliminado para todos los participantes"

    elif int(rep[8]) == 16:
        ans = ans.decode('utf-8') + Fore.GREEN + " - Tipo:" + Fore.RESET + " Localización en tiempo real ".decode('utf-8') + Fore.GREEN + "- Titulo: " + Fore.RESET + rep[11] + Fore.GREEN + " - Lat: " + Fore.RESET + str(rep[13]) + Fore.GREEN + " - Long: " + Fore.RESET + str(rep[14]) + Fore.GREEN + " - Duración: ".decode('utf-8') + Fore.RESET + str(duration_file(rep[12]))
    return ans


def status(st):
    """ Función estado de mensajes"""
    if st == 0 or st == 5:
        return "Recibido"
    elif st == 4:
        return Fore.RED + "Esperando en servidor" + Fore.RESET
    elif st == 6:
        return Fore.YELLOW + "Mensaje de sistema" + Fore.RESET
    elif st == 8 or st == 10:
        return Fore.BLUE + "Audio reproducido" + Fore.RESET
    elif st == 13:
        return Fore.BLUE + "Visto" + Fore.RESET
    else:
        return st


def size_file(obj):
    """ Función tamaño de objeto """
    if obj > 1048576:
        obj = "(" + "{0:.2f}".format(obj / float(1048576)) + " MB)"
    else:
        obj = "(" + "{0:.2f}".format(obj / float(1024)) + " KB)"
    return obj


def duration_file(obj):
    """ Función Tiempo de Duración"""
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


def messages(consult):
    """ Función que muestra mensajes"""
    try:
        n = 0
        for data in consult:
            try:
                if int(data[8]) != -1:
                    print Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET
                    if int(data[1]) == 1 and (str(data[0]).split('@'))[1] == "g.us":
                        if int(data[3]) == 6:
                            print Fore.GREEN + "De" + Fore.RESET,  data[0]
                        else:
                            print Fore.GREEN + "De" + Fore.RESET + " mí" + Fore.GREEN + " a" + Fore.RESET, data[0]

                    elif int(data[1]) == 1 and (str(data[0]).split('@'))[1] == "s.whatsapp.net":
                        if int(data[3]) == 6:
                            print Fore.GREEN + "De" + Fore.RESET, (str(data[0]).split('@'))[0]
                        else:
                            print Fore.GREEN + "De" + Fore.RESET + " mí" + Fore.GREEN + " a" + Fore.RESET, (str(data[0]).split('@'))[0]

                    elif int(data[1]) == 1 and (str(data[0]).split('@'))[1] == "broadcast":
                        if int(data[3]) == 6:
                            print Fore.GREEN + "De" + Fore.RESET, data[0]
                        else:
                            list_broadcast = (str(data[15])).split('@')
                            list_copy = []
                            for i in list_broadcast:
                                list_copy.append("".join([x for x in i if x.isdigit()]))
                            list_copy.pop()
                            print Fore.GREEN + "De" + Fore.RESET + " mí" + Fore.GREEN + " a" + Fore.RESET, list_copy, Fore.GREEN + "por difusión" + Fore.RESET

                    elif int(data[1]) == 0 and (str(data[0]).split('@'))[1] == "g.us":
                        print Fore.GREEN + "De" + Fore.RESET, data[0] + Fore.GREEN + ", participante" + Fore.RESET, (str(data[15]).split('@'))[0]

                    elif int(data[1]) == 0 and (str(data[0]).split('@'))[1] == "s.whatsapp.net":
                        if data[15]:
                            print Fore.GREEN + "De" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.GREEN + "por difusión a" + Fore.RESET + " mí"
                        else:
                            if int(data[8]) == 10:
                                print Fore.GREEN + "De" + Fore.RESET, (str(data[0]).split('@'))[0]
                            else:
                                print Fore.GREEN + "De" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.GREEN + "a" + Fore.RESET + " mí"

                    elif int(data[1]) == 0 and (str(data[0]).split('@'))[1] == "broadcast":
                        print Fore.GREEN + "De" + Fore.RESET, (str(data[15]).split('@'))[0], Fore.GREEN + "publica estado" + Fore.RESET

                    if data[21] or int(data[21]) > 0:
                        print Fore.GREEN + "Respondiendo a:" + Fore.RESET, reply(data[21])
                        consult = cursor.execute(sql_string)
                        for x in range(n + 1):
                            consult = cursor.fetchone()

                    if int(data[8]) == 0:
                        if int(data[3]) == 6:
                            if int(data[9]) == 1:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "cambió el asunto de '", str(data[17])[7:].decode('utf-8', 'ignore'), "' a '", data[4], "'"
                            elif int(data[9]) == 4:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "fué añadido al grupo"
                            elif int(data[9]) == 5:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "dejó el grupo"
                            elif int(data[9]) == 6:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip(
                                    "@s.whatsapp.net"), "cambió el icono del grupo"
                                if data[17]:
                                    print "La última imagen esta almacenada en la ruta del teléfono '/data/data/com.whatsapp/cache/Profile Pictures/" + str(
                                        (data[0].split('@'))[0]) + ".jpg'"
                                    print "La miniatura fue grabada en la ruta local '" + os.getcwd() + "/Media/profiles/" + \
                                          (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg'"
                                else:
                                    print "Miniatura nula"
                                if not os.path.isdir("./Media/profiles"):
                                    os.mkdir("./Media/profiles")
                                with open("buffer", 'wb') as buffer_copy:
                                    buffer_copy.write(str(data[17]))
                                with open("buffer", 'rb') as buffer_copy:
                                    i = 0
                                    if data[17]:
                                        while True:
                                            x = buffer_copy.read(1)
                                            x = hex(ord(x))
                                            if x == "0xd8":
                                                break
                                            else:
                                                i += 1
                                        buffer_copy.seek(0, 0)
                                        buffer_copy.seek(i - 1)
                                        new_file = buffer_copy.read()
                                        file_created = "./Media/profiles/" + (data[0].split('@'))[0] + "(" + str(
                                            int(data[5]) / 1000) + ").jpg"
                                        with open(file_created, 'wb') as profile_file:
                                            profile_file.write(new_file)
                            elif int(data[9]) == 7:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET + " Se eliminó", data[15].strip("@s.whatsapp.net"), "de la lista"
                            elif int(data[9]) == 9:
                                list_broadcast = (str(data[17])).split('@')
                                list_copy = []
                                for i in list_broadcast:
                                    list_copy.append("".join([x for x in i if x.isdigit()]))
                                list_copy.pop()
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "creó una lista de difusión con", list_copy, "destinatarios"
                            elif int(data[9]) == 10:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "cambió a", ((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0]
                            elif int(data[9]) == 11:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "creó el grupo '", data[4], "'"
                            elif int(data[9]) == 12:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "añadió".decode('utf-8'), ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "al grupo"
                            elif int(data[9]) == 14:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "eliminó", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "del grupo"
                            elif int(data[9]) == 15:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "te hizo administrador"
                            elif int(data[9]) == 18:
                                if data[15]:
                                    print Fore.GREEN + "Mensaje:" + Fore.RESET + " El código de seguridad de", data[15].strip("@s.whatsapp.net"), "cambió"
                                else:
                                    print Fore.GREEN + "Mensaje:" + Fore.RESET + " El código de seguridad de", data[0].strip("@s.whatsapp.net"), "cambió"
                            elif int(data[9]) == 19:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET + " Los mensajes y llamadas en este chat están ahora protegidos con cifrado de extremo a extremo"
                            elif int(data[9]) == 20:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET, ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "se unió usando un enlace de invitación al grupo"
                        else:
                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[4]

                    elif int(data[8]) == 1:
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:
                            thumb = "No descargado"
                        else:
                            thumb = "/" + (str(data[17]))[i:b]
                        if data[11]:
                            print Fore.GREEN + "Nombre:" + Fore.RESET, thumb + Fore.GREEN + " - Título:" + Fore.RESET, data[11]
                        else:
                            print Fore.GREEN + "Nombre:" + Fore.RESET, thumb
                        print Fore.GREEN + "Tipo: " + Fore.RESET + "imagen/jpeg" + Fore.GREEN + " - Tamaño:".decode('utf-8') + Fore.RESET, data[9], "bytes " + size_file(int(data[9]))
                        if data[19]:  # raw_data
                            distutils.dir_util.mkpath("./Media/WhatsApp Images/Sent")
                            if thumb == "No descargado":
                                if int(data[1]) == 1:
                                    thumb = "/Media/WhatsApp Images/Sent/IMG-" + str((int(data[5]) / 1000)) + ".jpg"
                                else:
                                    thumb = "/Media/WhatsApp Images/IMG-" + str((int(data[5]) / 1000)) + ".jpg"
                            print "Miniatura fue grabada en la ruta local '" + os.getcwd() + thumb + "'"
                            file_created = "." + thumb
                            with open(file_created, 'wb') as profile_file:
                                profile_file.write(str(data[19]))

                    elif int(data[8]) == 2: 
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  
                            thumb = "No descargado"
                        else:
                            thumb = "/" + (str(data[17]))[i:b]
                        print Fore.GREEN + "Nombre:" + Fore.RESET, thumb
                        print Fore.GREEN + "Tipo:" + Fore.RESET, data[7], Fore.GREEN + "- Tamaño:".decode('utf-8') + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duración:" + Fore.RESET, duration_file(data[12])

                    elif int(data[8]) == 3:
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:
                            thumb = "No descargado"
                        else:
                            thumb = "/" + (str(data[17]))[i:b]
                        if data[11]:
                            print Fore.GREEN + "Nombre:" + Fore.RESET, thumb + Fore.GREEN + " - Título:" + Fore.RESET, data[11]
                        else:
                            print Fore.GREEN + "Nombre:" + Fore.RESET, thumb
                        print Fore.GREEN + "Tipo: " + Fore.RESET + data[7] + Fore.GREEN + " - Tamaño:".decode('utf-8') + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duración:" + Fore.RESET, duration_file(data[12])
                        if data[19]:
                            distutils.dir_util.mkpath("./Media/WhatsApp Video/Sent")
                            if thumb == "No descargado":
                                if int(data[1]) == 1:
                                    thumb = "/Media/WhatsApp Video/Sent/VID-" + str((int(data[5]) / 1000)) + ".mp4"
                                else:
                                    thumb = "/Media/WhatsApp Video/VID-" + str((int(data[5]) / 1000)) + ".mp4"
                            print "Minitatura fue grabada en la ruta local '" + os.getcwd() + thumb + "'"
                            file_created = "." + thumb
                            with open(file_created, 'wb') as profile_file:
                                profile_file.write(str(data[19]))

                    elif int(data[8]) == 4:
                        print Fore.GREEN + "Nombre:" + Fore.RESET, data[10], Fore.GREEN + "- Tipo:" + Fore.RESET + " Contacto vCard"

                    elif int(data[8]) == 5:
                        if data[6]:
                            if data[10]:
                                print Fore.GREEN + "Url:" + Fore.RESET, data[6], Fore.GREEN + "- Nombre:" + Fore.RESET, data[10]
                            else:
                                print Fore.GREEN + "Url:" + Fore.RESET, data[6]
                        else:
                            if data[10]:
                                print Fore.GREEN + "Nombre:" + Fore.RESET, data[10]
                        print Fore.GREEN + "Tipo:" + Fore.RESET + " Localización" + Fore.GREEN + " - Lat:" + Fore.RESET, data[13], Fore.GREEN + "- Long:" + Fore.RESET, data[14]

                    elif int(data[8]) == 8:
                        print Fore.GREEN + "Call:" + Fore.RESET, data[11], Fore.GREEN + "- Duración:" + Fore.RESET, duration_file(data[12])

                    elif int(data[8]) == 9:
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:
                            thumb = "No descargado"
                        else:
                            thumb = "/" + chain[i:b]
                        if data[11]:
                            print Fore.GREEN + "Nombre:" + Fore.RESET, thumb + Fore.GREEN + " - Título:" + Fore.RESET, data[11]
                        else:
                            print Fore.GREEN + "Nombre:" + Fore.RESET, thumb
                        if int(data[12]) > 0:
                            print Fore.GREEN + "Tipo: " + Fore.RESET + data[7] + Fore.GREEN + " - Tamaño:".decode('utf-8') + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Páginas:" + Fore.RESET, data[12]
                        else:
                            print Fore.GREEN + "Tipo: " + Fore.RESET + data[7] + Fore.GREEN + " - Tamaño:".decode('utf-8') + Fore.RESET, data[9], "bytes " + size_file(int(data[9]))
                        if data[19]:
                            distutils.dir_util.mkpath("./Media/WhatsApp Documents/Sent")
                            if thumb == "No descargado":
                                if int(data[1]) == 1:
                                    thumb = "/Media/WhatsApp Animated Documents/Sent/DOC-" + str((int(data[5]) / 1000))
                                else:
                                    thumb = "/Media/WhatsApp Animated Documents/DOC-" + str((int(data[5]) / 1000))
                            print "Miniatura fue grabada en la ruta local '" + os.getcwd() + thumb + ".jpg'"
                            file_created = "." + thumb + ".jpg"
                            with open(file_created, 'wb') as profile_file:
                                profile_file.write(str(data[19]))

                    elif int(data[8]) == 10:
                        print Fore.GREEN + "Mensaje:" + Fore.RESET, str(data[11]).capitalize() + " llamada perdida"

                    elif int(data[8]) == 13:
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:
                            thumb = "No descargado"
                        else:
                            thumb = "/" + (str(data[17]))[i:b]
                        if data[11]:
                            print Fore.GREEN + "Nombre:" + Fore.RESET, thumb + Fore.GREEN + " - Título:" + Fore.RESET, data[11]
                        else:
                            print Fore.GREEN + "Nombre:" + Fore.RESET, thumb
                        print Fore.GREEN + "Tipo: " + Fore.RESET + "Gif" + Fore.GREEN + " - Tamaño:".decode('utf-8') + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duración:" + Fore.RESET, duration_file(data[12])
                        if data[19]:
                            distutils.dir_util.mkpath("./Media/WhatsApp Animated Gifs/Sent")
                            if thumb == "No descargado":
                                if int(data[1]) == 1:
                                    thumb = "/Media/WhatsApp Animated Gifs/Sent/VID-" + str((int(data[5]) / 1000)) + ".mp4"
                                else:
                                    thumb = "/Media/WhatsApp Animated Gifs//VID-" + str((int(data[5]) / 1000)) + ".mp4"
                            print "Miniatura fue grabada en la ruta local'" + os.getcwd() + thumb + "'"
                            file_created = "." + thumb
                            with open(file_created, 'wb') as profile_file:
                                profile_file.write(str(data[19]))

                    elif int(data[8]) == 15:
                        if int(data[16]) == 5:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET + " Mensaje eliminado para mí"
                        elif int(data[16]) == 7:
                                print Fore.GREEN + "Mensaje:" + Fore.RESET + " Mensaje eliminado para todos los participantes"

                    elif int(data[8]) == 16:
                        print Fore.GREEN + "Tipo:" + Fore.RESET + " Localización en tiempo real " + Fore.GREEN + "- Título:" + Fore.RESET, data[11], Fore.GREEN + "- Lat:" + Fore.RESET, data[13], Fore.GREEN + "- Long:" + Fore.RESET, data[14], Fore.GREEN + "- Duración:" + Fore.RESET, duration_file(data[12])

                    if data[20]:
                        if int(data[20]) == 1:
                            print Fore.YELLOW + "Mensaje destacado" + Fore.RESET
                    print Fore.GREEN + "Sello de tiempo:" + Fore.RESET, time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000)), Fore.GREEN + "- Estado:" + Fore.RESET, status(int(data[3]))
                n += 1

            except Exception as e:
                print "Error mostrando detalles de mensaje:", e
                continue
    except Exception as e:
        print "Ocurrió un error conectando con la base de datos", e


def info(consult):
    """ Función que muestra información"""
    info_dic = {}
    i = 1
    try:
        for data in consult:
            try:
                if int(data[3]) == 6:
                    if int(data[9]) == 11:
                        i += 1
                        info_dic.update({i: [data[0], data[4], 'group']})
                    elif int(data[9]) == 9:
                        i += 1
                        info_dic.update({i: [data[0], data[4], 'broadcast']})

            except Exception as e:
                print "Error agregando artículos en el diccionario:", e
                continue

        for dic_key, dic_value in info_dic.items():
            sql_key = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, \
                      remote_resource FROM messages WHERE (key_remote_jid = '" + dic_value[0] + "' and status = 6 and media_size = 1);"
            consult_key = cursor.execute(sql_key)
            for data in consult_key:
                if data[4]:
                    info_dic.update({dic_key: [data[0], data[4], 'group']})

    except Exception as e:
        print "Un error ocurrió conectando con la base de datos", e

    while True:
        print "\n-------------------------- MODO INFORMACION ----------------------------"
        print "0  ) Salir"
        print "1  ) Estados"
        for key, value in info_dic.items():
            i = key
            if key < 10:
                if value[2] == "group":
                    print key, " )", value[0], "-", value[1]
                else:
                    print key, " )", value[0], "-", value[2]
            else:
                if value[2] == "group":
                    print key, ")", value[0], "-", value[1]
                else:
                    print key, ")", value[0], "-", value[2]
        print "-------------------------------------------------------------------------"
        try:
            opt = int(input("\nElige una opción númerica: "))
            if opt == 0:
                break
            elif opt == 1:
                sql_string = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, \
                             remote_resource, edit_version,thumb_image, recipient_count, raw_data FROM messages WHERE key_remote_jid = 'status@broadcast';"
                consult = cursor.execute(sql_string)
                print "\n\n\t*** Estados ***\n"
                for data in consult:
                    try:
                        print Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET
                        if data[17]: 
                            print Fore.GREEN + "De" + Fore.RESET, data[15].strip("@s.whatsapp.net")
                            chain = str(data[17]).split('w')[0]
                            i = chain.rfind("Media/")
                            b = len(chain)
                            if i == -1:
                                thumb = "No visualizado"
                            else:
                                thumb = "/" + (str(data[17]))[i:b]
                            if data[11]:
                                print Fore.GREEN + "Nombre:" + Fore.RESET, thumb + Fore.GREEN + " - Título:" + Fore.RESET, data[11]
                            else:
                                print Fore.GREEN + "Nombre:" + Fore.RESET, thumb
                            if int(data[12]) > 0:
                                print Fore.GREEN + "Tipo: " + Fore.RESET + data[7] + Fore.GREEN + " - Tamaño:".decode('utf-8') + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duración:" + Fore.RESET, duration_file(data[12])
                            else:
                                print Fore.GREEN + "Tipo: " + Fore.RESET + data[7] + Fore.GREEN + " - Tamaño:".decode('utf-8') + Fore.RESET, data[9], "bytes " + size_file(int(data[9]))
                            if thumb != "No visualizado":
                                print "La imagen esta almacenada en la ruta del teléfono '" + thumb + "'"
                            print Fore.GREEN + "Sello de tiempo:" + Fore.RESET, str(time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000))), Fore.GREEN + "- Estado:" + Fore.RESET, status(int(data[3]))
                    except Exception as e:
                        print "Error de estado", e
                        continue

            elif opt > i:
                print "Opción inválida"
            else:  # Select a valid option
                while True:
                    if info_dic[opt][1]:
                        print "\n\n\t***", info_dic[opt][1], "***\n"
                    else:
                        print "\n\n\t*** Difusión ***\n"
                    print "0 ) Atrás"
                    print "1 ) Creador y fecha de creación"
                    print "2 ) Participantes"
                    print "3 ) Registro\n"
                    try:
                        opt2 = int(input("Elige una opción numérica: "))
                        if opt2 == 0:
                            break

                        elif opt2 == 1:
                            if info_dic[opt][1]:
                                a = info_dic[opt][0].split("-")
                                b = a[1].split("@")
                                print "\n    Usuario creador          Sello de tiempo"
                                print "--------------------------------------------"
                                print "   ", a[0], "\t", time.strftime('%d-%m-%Y %H:%M', time.localtime(int(b[0])))
                            else:
                                a, b = info_dic[opt][0].split("@")
                                print "\n    Usuario creador          Sello de tiempo"
                                print "--------------------------------------------"
                                print "       Me \t\t", time.strftime('%d-%m-%Y %H:%M', time.localtime(int(a)))

                        elif opt2 == 2:
                            sql_string_info = "SELECT gjid, jid, admin, pending,sent_sender_key FROM group_participants WHERE gjid = '" + info_dic[opt][0] + "';"
                            consult_info = cursor.execute(sql_string_info)
                            i = 0
                            if info_dic[opt][1]:  # if it's a group
                                print "\n Teléfono de usuario    Administrador"
                                print "----------------------------------------------"
                                for data in consult_info:
                                    if data[1]:
                                        i += 1
                                        if i > 9:
                                            print i, ")", data[1].strip("@s.whatsapp.net"),\
                                                '\tSí' if int(data[2]) == 1 else '\tNo'
                                        else:
                                            print i, " )", data[1].strip("@s.whatsapp.net"),\
                                                '\tSí' if int(data[2]) == 1 else '\tNo'
                                    else:
                                        i += 1
                                        print i, " ) Yo\t\t\t", 'Sí' if int(data[2]) == 1 else 'No'
                            else:  # if it's a broadcast
                                print "\n     Teléfono de usuario"
                                print "-----------------------------"
                                for data in consult_info:
                                    i += 1
                                    print i, ")", data[1].strip("@s.whatsapp.net")

                        elif opt2 == 3:
                            sql_string_info = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, \
                                              latitude, longitude, remote_resource, edit_version, thumb_image, recipient_count FROM messages WHERE key_remote_jid = '" + info_dic[opt][0] + "';"
                            consult_info = cursor.execute(sql_string_info)
                            try:
                                for data in consult_info:
                                    if (int(data[8]) == 0) and (int(data[3]) == 6):
                                        print Fore.RED + "---------------------------------------------------------------------" + Fore.RED

                                        if int(data[9]) == 1:  # if media_size value change
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "cambió el asunto de '", str(data[17])[7:].decode('utf-8', 'ignore'), "' a '", data[4], "'"
                                        elif int(data[9]) == 4:
                                            if info_dic[opt][1]:
                                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "fue añadido al grupo"
                                            else:
                                                print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "fue añadido a la lista"
                                        elif int(data[9]) == 5:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "dejó el grupo"
                                        elif int(data[9]) == 6:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "cambió el icono del grupo"
                                            if data[17]:
                                                print "La última imagen esta almacenada en la ruta del teléfono '/data/data/com.whatsapp/cache/Profile Pictures/" + str((data[0].split('@'))[0]) + ".jpg'"
                                                print "La miniatura fue grabada en la ruta local '" + os.getcwd() + "/Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg'"
                                            else:
                                                print "Miniatura nula"
                                            if not os.path.isdir("./Media/profiles"):
                                                os.mkdir("./Media/profiles")
                                            with open("buffer", 'wb') as buffer_copy:
                                                buffer_copy.write(str(data[17]))
                                            with open("buffer", 'rb') as buffer_copy:
                                                i = 0
                                                if data[17]:
                                                    while True:
                                                        x = buffer_copy.read(1)
                                                        x = hex(ord(x))
                                                        if x == "0xd8":
                                                            break
                                                        else:
                                                            i += 1
                                                    buffer_copy.seek(0, 0)
                                                    buffer_copy.seek(i-1)
                                                    new_file = buffer_copy.read()
                                                    file_created = "./Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg"
                                                    with open(file_created, 'wb') as profile_file:
                                                        profile_file.write(new_file)

                                        elif int(data[9]) == 7:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET + " Eliminó", data[15].strip("@s.whatsapp.net"), "de la lista"
                                        elif int(data[9]) == 9:
                                            list_broadcast = (str(data[17])).split('@')
                                            list_copy = []
                                            for i in list_broadcast:
                                                list_copy.append("".join([x for x in i if x.isdigit()]))
                                            list_copy.pop()
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "creó una lista de difusión con", list_copy, "destinatarios"
                                        elif int(data[9]) == 10:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "cambió a ", ((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0]
                                        elif int(data[9]) == 11:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "creó el grupo '", data[4], "'"
                                        elif int(data[9]) == 12:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "añadió", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "al grupo"
                                        elif int(data[9]) == 14:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "eliminó", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "del grupo"
                                        elif int(data[9]) == 15:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "te hizo administrador"
                                        elif int(data[9]) == 18:
                                            if data[15]:
                                                print Fore.GREEN + "Mensaje:" + Fore.RESET + " El código de seguridad de", data[15].strip("@s.whatsapp.net"), "cambió"
                                            else:
                                                print Fore.GREEN + "Mensaje:" + Fore.RESET + " El código de seguridad de", data[0].strip("@s.whatsapp.net"), "cambió"
                                        elif int(data[9]) == 19:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET + " Los mensajes y llamadas en este chat ahora están protegidos con cifrado de extremo a extremo"
                                        elif int(data[9]) == 20:
                                            print Fore.GREEN + "Mensaje:" + Fore.RESET, ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "se unió usando un enlace de invitación de este grupo"
                                        print Fore.GREEN + "Sello de tiempo:" + Fore.RESET , time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000))

                            except Exception as e:
                                print "Error mostrando detalles del mensaje", e
                                continue
                        else:
                            print "Opción inválida"

                    except Exception as e:
                        print "Error introduciendo datos", e

        except Exception as e:
            print "Error introduciendo datos", e


# Initializing
if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Para empezar elige una base de datos y un modo con sus opciones")
    group_parser = parser.add_mutually_exclusive_group()
    parser.add_argument("database", help="Ruta del archivo de la base de datos - './msgstore.db' por defecto", metavar="DATABASE", nargs='?', default="./msgstore.db")
    group_parser.add_argument("-k", "--key", help="*** Modo Descifrar *** - Ruta del archivo 'key'")
    group_parser.add_argument("-i", "--info", help="*** Modo Información ***", action="store_true")
    group_parser.add_argument("-m", "--messages", help="*** Modo Mensaje ***", action="store_true")
    parser.add_argument("-t", "--text", help="filtrar mensajes por coincidencia de texto")
    parser.add_argument("-u", "--user", help="filtrar mensajes por número de usuario")
    parser.add_argument("-g", "--group", help="filtrar mensajes por número de grupo")
    parser.add_argument("-w", "--web", help="filtrar mensajes realizados por Whatsapp Web", action="store_true")
    parser.add_argument("-s", "--starred", help="filtrar mensajes destacados por el usuario", action="store_true")
    parser.add_argument("-b", "--broadcast", help="filtrar mensajes realizados por difusión", action="store_true")
    parser.add_argument("-tS", "--time_start", help="filtrat mensajes por hora de comienzo(dd-mm-yyyy HH:MM)")
    parser.add_argument("-tE", "--time_end", help="filtrar mensajes por hora de finalización(dd-mm-yyyy HH:MM)")
    filter_parser = parser.add_mutually_exclusive_group()
    filter_parser.add_argument("-tT", "--type_text", help="filtrar mensajes de texto", action="store_true")
    filter_parser.add_argument("-tI", "--type_image", help="filtrar mensajes de imagen", action="store_true")
    filter_parser.add_argument("-tA", "--type_audio", help="filtrar mensajes de audio", action="store_true")
    filter_parser.add_argument("-tV", "--type_video", help="filtrar mensajes de video", action="store_true")
    filter_parser.add_argument("-tC", "--type_contact", help="filtrar mensajes de contacto", action="store_true")
    filter_parser.add_argument("-tL", "--type_location", help="filtrar mensajes de localización", action="store_true")
    filter_parser.add_argument("-tX", "--type_call", help="filtrar mensajes de audio/video llamada", action="store_true")
    filter_parser.add_argument("-tP", "--type_application", help="filtrar mensajes de aplicación", action="store_true")
    filter_parser.add_argument("-tG", "--type_gif", help="filtrar mensajes GIF", action="store_true")
    filter_parser.add_argument("-tD", "--type_deleted", help="filtrar mensajes de objeto eliminado", action="store_true")
    filter_parser.add_argument("-tR", "--type_share", help="filtrar mensajes de ubicación en tiempo real", action="store_true")

    args = parser.parse_args()
    init()
    if len(sys.argv) == 1:
        help()
    else:
        if args.messages:
            db_connect(args.database)
            sql_string = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, remote_resource, edit_version, thumb_image, recipient_count, raw_data, starred, quoted_row_id FROM messages WHERE timestamp BETWEEN '"
            try:
                epoch_start = "0"
                epoch_end = str(1000 * int(time.mktime(time.strptime(time.strftime('%d-%m-%Y %H:%M'), '%d-%m-%Y %H:%M'))))

                if args.time_start:
                    epoch_start = 1000 * int(time.mktime(time.strptime(args.time_start, '%d-%m-%Y %H:%M')))
                if args.time_end:
                    epoch_end = 1000 * int(time.mktime(time.strptime(args.time_end, '%d-%m-%Y %H:%M')))

                sql_string = sql_string + str(epoch_start) + "' AND '" + str(epoch_end) + "'"

                if args.text:
                    sql_string = sql_string + " AND data LIKE '%" + str(args.text) + "%'"
                if args.user:
                    sql_string = sql_string + " AND (key_remote_jid LIKE '%" + str(args.user) + "%@s.whatsapp.net' OR remote_resource LIKE '%" + str(args.user) + "%')"
                if args.group:
                    sql_string = sql_string + " AND key_remote_jid LIKE '%" + str(args.group) + "%'"
                if args.web:
                    sql_string = sql_string + " AND key_id LIKE '3EB0%'"
                if args.starred:
                        sql_string = sql_string + " AND starred = 1"
                if args.broadcast:
                    sql_string = sql_string + " AND remote_resource LIKE '%broadcast%'"
                if args.type_text:
                    sql_string = sql_string + " AND media_wa_type = 0"
                if args.type_image:
                    sql_string = sql_string + " AND media_wa_type = 1"
                if args.type_audio:
                    sql_string = sql_string + " AND media_wa_type = 2"
                if args.type_video:
                    sql_string = sql_string + " AND media_wa_type = 3"
                if args.type_contact:
                    sql_string = sql_string + " AND media_wa_type = 4"
                if args.type_location:
                    sql_string = sql_string + " AND media_wa_type = 5"
                if args.type_call:
                    sql_string = sql_string + " AND media_wa_type = 8"
                if args.type_application:
                    sql_string = sql_string + " AND media_wa_type = 9"
                if args.type_gif:
                    sql_string = sql_string + " AND media_wa_type = 13"
                if args.type_deleted:
                    sql_string = sql_string + " AND media_wa_type = 15"
                if args.type_share:
                    sql_string = sql_string + " AND media_wa_type = 16"

                sql_consult = cursor.execute(sql_string + ";")
                messages(sql_consult)
            except Exception as e:
                print "Error:", e

        elif args.key:
            decrypt(args.database, args.key)

        elif args.info:
            db_connect(args.database)
            sql_string = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, \
                         latitude, longitude, remote_resource FROM messages;"
            sql_consult = cursor.execute(sql_string)
            info(sql_consult)
            
        elif args.database:
            db_connect(args.database)


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
    """ Function Banner """
    print """
     __      __.__          __________         
    /  \    /  \  |__ _____ \______   \_____   
    \   \/\/   /  |  \\\\__  \ |     ___/\__  \  
     \        /|   Y  \/ __ \|    |     / __ \_
      \__/\  / |___|  (____  /____|    (____  /
           \/       \/     \/               \/ 
    ---------- Whatsapp Parser v0.2 -----------
    """


def help():
    """ Function show help """
    print """    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t
    
    Usage: python whapa.py -h (for help)
    """


def decrypt(db_file, key_file):
    """ Function decrypt Crypt12 Database """
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

        print "msgstore.db.crypt12 decrypted, msgstore.db created."
    except Exception as e:
        print "An error has ocurred decrypting the Database:", e


def db_connect(db):
    """ Function connect to Database"""
    if os.path.exists(db):
        try:
            with sqlite3.connect(db) as conn:
                global cursor
                cursor = conn.cursor()
            print args.database, "Database connected\n"
            return cursor
        except Exception as e:
            print "Error connecting to Database, ", e
    else:
        print "Database doesn't exist"
        exit()


def reply(txt):
    """ Function look out answer messages """
    sql_reply_str = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, remote_resource, edit_version, thumb_image, recipient_count, raw_data, starred, quoted_row_id FROM messages_quotes WHERE _id = " + str(txt) + ";"
    sql_answer = cursor.execute(sql_reply_str)
    rep = sql_answer.fetchone()
    ans = ""
    if int(rep[1]) == 1 and (str(rep[0]).split('@'))[1] == "g.us":  # I send message to group
        ans = "Me"
    elif int(rep[1]) == 1 and (str(rep[0]).split('@'))[1] == "s.whatsapp.net":  # I send message to somebody
        ans = "Me"
    elif int(rep[1]) == 1 and (str(rep[0]).split('@'))[1] == "broadcast":  # I send broadcast
        ans = "Me"
    elif int(rep[1]) == 0 and (str(rep[0]).split('@'))[1] == "g.us":  # Group send me a message
        ans = (str(rep[15]).split('@'))[0]
    elif int(rep[1]) == 0 and (str(rep[0]).split('@'))[1] == "s.whatsapp.net":  # Somebody sends me a message (normal and broadcast)
        ans = (str(rep[0]).split('@'))[0]
    elif int(rep[1]) == 0 and (str(rep[0]).split('@'))[1] == "broadcast":  # Somebody posts a Status
        ans = (str(rep[15]).split('@'))[0]

    if int(rep[8]) == 0:  # media_wa_type 0, text message
        ans += Fore.GREEN + " - Message: " + Fore.RESET + rep[4]

    elif int(rep[8]) == 1:  # media_wa_type 1, Image
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:  # Image doesn't exist
            thumb = "Not downloaded"
        else:
            thumb = "/" + (str(rep[17]))[i:b]
        if rep[11]:  # media_caption
            ans += Fore.GREEN + " - Name: " + Fore.RESET + thumb + Fore.GREEN + " - Caption: " + Fore.RESET + rep[11]
        else:
            ans += Fore.GREEN + " - Name: " + Fore.RESET + thumb
        ans += Fore.GREEN + " - Type: " + Fore.RESET + "image/jpeg" + Fore.GREEN + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + str(size_file(int(rep[9])))

    elif int(rep[8]) == 2:  # media_wa_type 2, Audio
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:  # Audio doesn't exist
            thumb = "Not downloaded"
        else:
            thumb = "/" + (str(rep[17]))[i:b]
        ans += Fore.GREEN + " - Name: " + Fore.RESET + thumb + Fore.GREEN + " - Type: " + Fore.RESET + rep[7] + Fore.GREEN + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + str(size_file(int(rep[9]))) + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(rep[12])

    elif int(rep[8]) == 3:  # media_wa_type 3 Video
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:  # Video doesn't exist
            thumb = "Not downloaded"
        else:
            thumb = "/" + (str(rep[17]))[i:b]
        if rep[11]:  # media_caption
            ans += Fore.GREEN + " - Name: " + Fore.RESET + thumb + Fore.GREEN + " - Caption: " + Fore.RESET + rep[11]
        else:
            ans += Fore.GREEN + "Name: " + Fore.RESET + thumb
        ans += Fore.GREEN + " - Type: " + Fore.RESET + rep[7] + Fore.GREEN + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + str(size_file(int(rep[9]))) + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(rep[12])

    elif int(rep[8]) == 4:  # media_wa_type 4, Contact
        ans += Fore.GREEN + " - Name: " + Fore.RESET + rep[10] + Fore.GREEN + " - Type:" + Fore.RESET + " Contact vCard"

    elif int(rep[8]) == 5:  # media_wa_type 5, Location
        if rep[6]:  # media_url exists
            if rep[10]:  # media_name exists
                ans += Fore.GREEN + " - Url: " + Fore.RESET + rep[6] + Fore.GREEN + " - Name: " + Fore.RESET + rep[10]
            else:
                ans += Fore.GREEN + " - Url: " + Fore.RESET + rep[6]
        else:
            if rep[10]:
                ans += Fore.GREEN + " - Name: " + Fore.RESET + rep[10]
        ans += Fore.GREEN + " - Type:" + Fore.RESET + " Location" + Fore.GREEN + " - Lat: " + Fore.RESET + rep[13] + Fore.GREEN + " - Long: " + Fore.RESET + rep[14]

    elif int(rep[8]) == 8:  # media_wa_type 8, Audio / Video Call
        ans += Fore.GREEN + " - Call: " + Fore.RESET + rep[11] + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(rep[12])

    elif int(rep[8]) == 9:  # media_wa_type 9, Application
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:  # Image doesn't exist
            thumb = "Not downloaded"
        else:
            thumb = "/" + chain[i:b]
        if rep[11]:  # media_caption
            ans += Fore.GREEN + " - Name: " + Fore.RESET + thumb + Fore.GREEN + " - Caption: " + Fore.RESET + rep[11]
        else:
            ans += Fore.GREEN + " - Name: " + Fore.RESET + thumb
        if int(rep[12]) > 0:
            ans += Fore.GREEN + " - Type: " + Fore.RESET + rep[7] + Fore.GREEN + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9])) + Fore.GREEN + " - Pages: " + Fore.RESET + str(rep[12])
        else:
            ans += Fore.GREEN + " - Type: " + Fore.RESET + rep[7] + Fore.GREEN + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9]))

    elif int(rep[8]) == 10:  # media_wa_type 10, Video/Audio call lost
        ans += Fore.GREEN + " - Message: " + Fore.RESET + " Missed " + rep[11] + " call"

    elif int(rep[8]) == 13:  # media_wa_type 13 Gif
        chain = str(rep[17]).split('w')[0]
        i = chain.rfind("Media/")
        b = len(chain)
        if i == -1:  # Video doesn't exist
            thumb = "Not downloaded"
        else:
            thumb = "/" + (str(rep[17]))[i:b]
        if rep[11]:  # media_caption
            ans += Fore.GREEN + " - Name: " + Fore.RESET + thumb + Fore.GREEN + " - Caption: " + Fore.RESET + rep[11]
        else:
            ans += Fore.GREEN + " - Name: " + Fore.RESET + thumb
        ans += Fore.GREEN + " - Type: " + Fore.RESET + "Gif" + Fore.GREEN + " - Size: " + Fore.RESET + str(rep[9]) + " bytes " + size_file(int(rep[9])) + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(rep[12])

    elif int(rep[8]) == 15:  # media_wa_type 15, Deleted Object
        if int(rep[16]) == 5:  # edit_version 5, deleted for me
            ans += Fore.GREEN + " - Message:" + Fore.RESET + " Message deleted for me"
        elif int(rep[16]) == 7:  # edit_version 7, deleted for all
            ans += Fore.GREEN + " - Message:" + Fore.RESET + " Message deleted for all participants"

    elif int(rep[8]) == 16:  # media_wa_type 16, Share location
        ans += Fore.GREEN + " - Type:" + Fore.RESET + " Real time location " + Fore.GREEN + "- Caption: " + Fore.RESET + rep[11] + Fore.GREEN + " - Lat: " + Fore.RESET + rep[13] + Fore.GREEN + " - Long: " + Fore.RESET + rep[14] + Fore.GREEN + " - Duration: " + Fore.RESET + duration_file(rep[12])
    return ans


def status(st):
    """ Function message status"""
    if st == 0 or st == 5:  # 0 for me and 5 for target
        return "Received"
    elif st == 4:
        return Fore.RED + "Waiting in server" + Fore.RESET
    elif st == 6:
        return Fore.YELLOW + "System message" + Fore.RESET
    elif st == 8 or st == 10:
        return Fore.BLUE + "Audio played" + Fore.RESET # 10 for me and 8 for target
    elif st == 13:
        return Fore.BLUE + "Seen" + Fore.RESET
    else:
        return st


def size_file(obj):
    """ Function objects size"""
    if obj > 1048576:
        obj = "(" + "{0:.2f}".format(obj / float(1048576)) + " MB)"
    else:
        obj = "(" + "{0:.2f}".format(obj / float(1024)) + " KB)"
    return obj


def duration_file(obj):
    """ Function duration time"""
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
    """ Function that show database messages """
    try:
        n = 0
        for data in consult:
            try:
                if int(data[8]) != -1:   # media_wa_type -1 "Start DB"
                    print Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET
                    if int(data[1]) == 1 and (str(data[0]).split('@'))[1] == "g.us":
                        if int(data[3]) == 6:  # Group system message
                            print Fore.GREEN + "From" + Fore.RESET,  data[0]
                        else:  # I send message to group
                            print Fore.GREEN + "From" + Fore.RESET + " me" + Fore.GREEN + " to" + Fore.RESET, data[0]

                    elif int(data[1]) == 1 and (str(data[0]).split('@'))[1] == "s.whatsapp.net":  # I send message to somebody
                        if int(data[3]) == 6:  # sender system message
                            print Fore.GREEN + "From" + Fore.RESET, (str(data[0]).split('@'))[0]
                        else:  # I send a message to somebody
                            print Fore.GREEN + "From" + Fore.RESET + " me" + Fore.GREEN + " to" + Fore.RESET, (str(data[0]).split('@'))[0]

                    elif int(data[1]) == 1 and (str(data[0]).split('@'))[1] == "broadcast":  # I send broadcast
                        if int(data[3]) == 6:  # broadcast system message
                            print Fore.GREEN + "From" + Fore.RESET, data[0]
                        else:  # I send to somebody by broadcast
                            list_broadcast = (str(data[15])).split('@')
                            list_copy = []
                            for i in list_broadcast:
                                list_copy.append("".join([x for x in i if x.isdigit()]))
                            list_copy.pop()
                            print Fore.GREEN + "From" + Fore.RESET + " me" + Fore.GREEN + " to" + Fore.RESET, list_copy, Fore.GREEN + "by broadcast" + Fore.RESET

                    elif int(data[1]) == 0 and (str(data[0]).split('@'))[1] == "g.us":  # Group send me a message
                        print Fore.GREEN + "From" + Fore.RESET, data[0] + Fore.GREEN + ", participant" + Fore.RESET, (str(data[15]).split('@'))[0]

                    elif int(data[1]) == 0 and (str(data[0]).split('@'))[1] == "s.whatsapp.net":
                        if data[15]:  # Somebody sends me a message by broadcast
                            print Fore.GREEN + "From" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.GREEN + "by broadcast to" + Fore.RESET + " me"
                        else:  # Somebody sends me a message
                            if int(data[8]) == 10:
                                print Fore.GREEN + "From" + Fore.RESET, (str(data[0]).split('@'))[0]  # sender system message
                            else:
                                print Fore.GREEN + "From" + Fore.RESET, (str(data[0]).split('@'))[0], Fore.GREEN + "to" + Fore.RESET + " me"

                    elif int(data[1]) == 0 and (str(data[0]).split('@'))[1] == "broadcast":  # Somebody posts a Status
                        print Fore.GREEN + "From" + Fore.RESET, (str(data[15]).split('@'))[0], Fore.GREEN + "posts status" + Fore.RESET

                    if data[21] or int(data[21]) > 0:
                        print Fore.GREEN + "Replying to:" + Fore.RESET, reply(data[21])
                        consult = cursor.execute(sql_string)
                        for x in range(n + 1):
                            consult = cursor.fetchone()

                    if int(data[8]) == 0:  # media_wa_type 0, text message
                        if int(data[3]) == 6:  # Status 6, system message
                            if int(data[9]) == 1:  # if media_size value change
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "changed the subject from '", str(data[17])[7:].decode('utf-8', 'ignore'), "' to '", data[4], "'"
                            elif int(data[9]) == 4:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "was added to the group"
                            elif int(data[9]) == 5:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "left the group"
                            elif int(data[9]) == 6:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "changed the group icon"
                                if data[17]:
                                    print "The last picture is stored on the phone path '/data/data/com.whatsapp/cache/Profile Pictures/" + (data[0].split('@'))[0] + ".jpg'"
                                    print "Thumbnail was saved on local path '" + os.getcwd() + "/Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg'"
                                else:
                                    print "Thumbnail null"
                                distutils.dir_util.mkpath("./Media/profiles")
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
                                        file_created = "./Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg"
                                        with open(file_created, 'wb') as profile_file:
                                            profile_file.write(new_file)
                            elif int(data[9]) == 7:
                                print Fore.GREEN + "Message:" + Fore.RESET + " Removed", data[15].strip("@s.whatsapp.net"), "from the list"
                            elif int(data[9]) == 9:
                                list_broadcast = (str(data[17])).split('@')
                                list_copy = []
                                for i in list_broadcast:
                                    list_copy.append("".join([x for x in i if x.isdigit()]))
                                list_copy.pop()
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "created a broadcast list with", list_copy, "recipients"
                            elif int(data[9]) == 10:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "changed to", ((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0]
                            elif int(data[9]) == 11:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "created the group '", data[4], "'"
                            elif int(data[9]) == 12:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "added", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "to the group"
                            elif int(data[9]) == 14:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "eliminated", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "from the group"
                            elif int(data[9]) == 15:
                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "made you administrator"
                            elif int(data[9]) == 18:
                                if data[15]:
                                    print Fore.GREEN + "Message:" + Fore.RESET + " The security code of", data[15].strip("@s.whatsapp.net"), "changed"
                                else:
                                    print Fore.GREEN + "Message:" + Fore.RESET + " The security code of", data[0].strip("@s.whatsapp.net"), "changed"
                            elif int(data[9]) == 19:
                                print Fore.GREEN + "Message:" + Fore.RESET + " Messages and calls in this chat are now protected with end-to-end encryption"
                            elif int(data[9]) == 20:
                                print Fore.GREEN + "Message:" + Fore.RESET, ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "Joined using an invitation link from this group"
                        else:
                            print Fore.GREEN + "Message:" + Fore.RESET, data[4]

                    elif int(data[8]) == 1:  # media_wa_type 1, Image
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Image doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "/" + (str(data[17]))[i:b]
                        if data[11]:  # media_caption
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                        else:
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb
                        print Fore.GREEN + "Type: " + Fore.RESET + "image/jpeg" + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9]))
                        if data[19]:  # raw_data
                            distutils.dir_util.mkpath("./Media/WhatsApp Images/Sent")
                            if thumb == "Not downloaded":
                                if int(data[1]) == 1:
                                    thumb = "/Media/WhatsApp Images/Sent/IMG-" + str((int(data[5]) / 1000)) + ".jpg"
                                else:
                                    thumb = "/Media/WhatsApp Images/IMG-" + str((int(data[5]) / 1000)) + ".jpg"
                            print "Thumbnail was saved on local path '" + os.getcwd() + thumb + "'"
                            file_created = "." + thumb
                            with open(file_created, 'wb') as profile_file:
                                profile_file.write(str(data[19]))

                    elif int(data[8]) == 2:  # media_wa_type 2, Audio
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Audio doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "/" + (str(data[17]))[i:b]
                        print Fore.GREEN + "Name:" + Fore.RESET, thumb
                        print Fore.GREEN + "Type:" + Fore.RESET, data[7], Fore.GREEN + "- Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duration:" + Fore.RESET, duration_file(data[12])

                    elif int(data[8]) == 3:  # media_wa_type 3 Video
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Video doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "/" + (str(data[17]))[i:b]
                        if data[11]:  # media_caption
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                        else:
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb
                        print Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duration:" + Fore.RESET, duration_file(data[12])
                        if data[19]:
                            distutils.dir_util.mkpath("./Media/WhatsApp Video/Sent")
                            if thumb == "Not downloaded":
                                if int(data[1]) == 1:
                                    thumb = "/Media/WhatsApp Video/Sent/VID-" + str((int(data[5]) / 1000)) + ".mp4"
                                else:
                                    thumb = "/Media/WhatsApp Video/VID-" + str((int(data[5]) / 1000)) + ".mp4"
                            print "Thumbnail was saved on local path '" + os.getcwd() + thumb + "'"
                            file_created = "." + thumb
                            with open(file_created, 'wb') as profile_file:
                                profile_file.write(str(data[19]))

                    elif int(data[8]) == 4:  # media_wa_type 4, Contact
                        print Fore.GREEN + "Name:" + Fore.RESET, data[10], Fore.GREEN + "- Type:" + Fore.RESET + " Contact vCard"

                    elif int(data[8]) == 5:  # media_wa_type 5, Location
                        if data[6]:  # media_url exists
                            if data[10]:  # media_name exists
                                print Fore.GREEN + "Url:" + Fore.RESET, data[6], Fore.GREEN + "- Name:" + Fore.RESET, data[10]
                            else:
                                print Fore.GREEN + "Url:" + Fore.RESET, data[6]
                        else:
                            if data[10]:
                                print Fore.GREEN + "Name:" + Fore.RESET, data[10]
                        print Fore.GREEN + "Type:" + Fore.RESET + " Location" + Fore.GREEN + " - Lat:" + Fore.RESET, data[13], Fore.GREEN + "- Long:" + Fore.RESET, data[14]

                    elif int(data[8]) == 8:  # media_wa_type 8, Audio / Video Call
                        print Fore.GREEN + "Call:" + Fore.RESET, data[11], Fore.GREEN + "- Duration:" + Fore.RESET, duration_file(data[12])

                    elif int(data[8]) == 9:  # media_wa_type 9, Application
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Image doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "/" + chain[i:b]
                        if data[11]:  # media_caption
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                        else:
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb
                        if int(data[12]) > 0:
                            print Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Pages:" + Fore.RESET, data[12]
                        else:
                            print Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9]))
                        if data[19]:
                            distutils.dir_util.mkpath("./Media/WhatsApp Documents/Sent")
                            if thumb == "Not downloaded":
                                if int(data[1]) == 1:
                                    thumb = "/Media/WhatsApp Animated Documents/Sent/DOC-" + str((int(data[5]) / 1000))
                                else:
                                    thumb = "/Media/WhatsApp Animated Documents/DOC-" + str((int(data[5]) / 1000))
                            print "Thumbnail was saved on local path '" + os.getcwd() + thumb + ".jpg'"
                            file_created = "." + thumb + ".jpg"
                            with open(file_created, 'wb') as profile_file:
                                profile_file.write(str(data[19]))

                    elif int(data[8]) == 10:  # media_wa_type 10, Video/Audio call lost
                        print Fore.GREEN + "Message:" + Fore.RESET, "Missed " + data[11] + " call"

                    elif int(data[8]) == 13:  # media_wa_type 13 Gif
                        chain = str(data[17]).split('w')[0]
                        i = chain.rfind("Media/")
                        b = len(chain)
                        if i == -1:  # Video doesn't exist
                            thumb = "Not downloaded"
                        else:
                            thumb = "/" + (str(data[17]))[i:b]
                        if data[11]:  # media_caption
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                        else:
                            print Fore.GREEN + "Name:" + Fore.RESET, thumb
                        print Fore.GREEN + "Type: " + Fore.RESET + "Gif" + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duration:" + Fore.RESET, duration_file(data[12])
                        if data[19]:
                            distutils.dir_util.mkpath("./Media/WhatsApp Animated Gifs/Sent")
                            if thumb == "Not downloaded":
                                if int(data[1]) == 1:
                                    thumb = "/Media/WhatsApp Animated Gifs/Sent/VID-" + str((int(data[5]) / 1000)) + ".mp4"
                                else:
                                    thumb = "/Media/WhatsApp Animated Gifs//VID-" + str((int(data[5]) / 1000)) + ".mp4"
                            print "Thumbnail was saved on local path '" + os.getcwd() + thumb + "'"
                            file_created = "." + thumb
                            with open(file_created, 'wb') as profile_file:
                                profile_file.write(str(data[19]))

                    elif int(data[8]) == 15:  # media_wa_type 15, Deleted Object
                        if int(data[16]) == 5:  # edit_version 5, deleted for me
                                print Fore.GREEN + "Message:" + Fore.RESET + " Message deleted for me"
                        elif int(data[16]) == 7:  # edit_version 7, deleted for all
                                print Fore.GREEN + "Message:" + Fore.RESET + " Message deleted for all participants"

                    elif int(data[8]) == 16:  # media_wa_type 16, Share location
                        print Fore.GREEN + "Type:" + Fore.RESET + " Real time location " + Fore.GREEN + "- Caption:" + Fore.RESET, data[11], Fore.GREEN + "- Lat:" + Fore.RESET, data[13], Fore.GREEN + "- Long:" + Fore.RESET, data[14], Fore.GREEN + "- Duration:" + Fore.RESET, duration_file(data[12])

                    if data[20]:
                        if int(data[20]) == 1:
                            print Fore.YELLOW + "Starred message" + Fore.RESET
                    print Fore.GREEN + "Timestamp:" + Fore.RESET, time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000)), Fore.GREEN + "- Status:" + Fore.RESET, status(int(data[3]))
                n += 1

            except Exception as e:
                print "Error showing message details:", e
                continue
    except Exception as e:
        print "An error occurred connecting to the database", e


def info(consult):
    """ Function that show info """
    info_dic = {}  # i:[Key_Remote_jid, data, type]
    i = 1
    try:
        for data in consult:
            try:
                if int(data[3]) == 6:  # Status 6, control message
                    if int(data[9]) == 11:  # media size 11 --> Group
                        i += 1
                        info_dic.update({i: [data[0], data[4], 'group']})
                    elif int(data[9]) == 9:  # media size 9 --> Broadcast
                        i += 1
                        info_dic.update({i: [data[0], data[4], 'broadcast']})

            except Exception as e:
                print "Error adding items in the dictionary:", e
                continue

        for dic_key, dic_value in info_dic.items():  # A group create with the last name
            sql_key = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, \
                      remote_resource FROM messages WHERE (key_remote_jid = '" + dic_value[0] + "' and status = 6 and media_size = 1);"
            consult_key = cursor.execute(sql_key)
            for data in consult_key:
                if data[4]:
                    info_dic.update({dic_key: [data[0], data[4], 'group']})

    except Exception as e:
        print "An error occurred connecting to the database", e

    while True:
        print "\n-------------------------- INFO MODE ----------------------------"
        print "0  ) Exit"
        print "1  ) Statuses"
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
        print "------------------------------------------------------------------"
        try:
            opt = int(input("\nChoose a number option: "))
            if opt == 0:
                break
            elif opt == 1:
                sql_string = "SELECT key_remote_jid, key_from_me, key_id, status, data, timestamp, media_url, media_mime_type, media_wa_type, media_size, media_name, media_caption, media_duration, latitude, longitude, \
                             remote_resource, edit_version,thumb_image, recipient_count, raw_data FROM messages WHERE key_remote_jid = 'status@broadcast';"
                consult = cursor.execute(sql_string)
                print "\n\n\t*** Statuses ***\n"
                for data in consult:
                    try:
                        print Fore.RED + "--------------------------------------------------------------------------------" + Fore.RESET
                        if data[17]:  # thumb_image
                            print Fore.GREEN + "From" + Fore.RESET, data[15].strip("@s.whatsapp.net")
                            chain = str(data[17]).split('w')[0]
                            i = chain.rfind("Media/")
                            b = len(chain)
                            if i == -1:  # Image doesn't exist
                                thumb = "Not displayed"
                            else:
                                thumb = "/" + (str(data[17]))[i:b]
                            if data[11]:  # media_caption
                                print Fore.GREEN + "Name:" + Fore.RESET, thumb + Fore.GREEN + " - Caption:" + Fore.RESET, data[11]
                            else:
                                print Fore.GREEN + "Name:" + Fore.RESET, thumb
                            if int(data[12]) > 0:
                                print Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9])) + Fore.GREEN + " - Duration:" + Fore.RESET, duration_file(data[12])
                            else:
                                print Fore.GREEN + "Type: " + Fore.RESET + data[7] + Fore.GREEN + " - Size:" + Fore.RESET, data[9], "bytes " + size_file(int(data[9]))
                            if thumb != "Not displayed":
                                print "The picture is stored on the phone path '" + thumb + "'"
                            print Fore.GREEN + "Timestamp:" + Fore.RESET, time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000)), Fore.GREEN + "- Status:" + Fore.RESET, status(int(data[3]))
                    except Exception as e:
                        print "Status error", e
                        continue

            elif opt > i:
                print "Bad option"
            else:  # Select a valid option
                while True:
                    if info_dic[opt][1]:
                        print "\n\n\t***", info_dic[opt][1], "***\n"
                    else:
                        print "\n\n\t*** Broadcast ***\n"
                    print "0 ) Back"
                    print "1 ) Creator and creation timestamp"
                    print "2 ) Participants"
                    print "3 ) Log\n"
                    try:
                        opt2 = int(input("Choose a number option: "))
                        if opt2 == 0:
                            break

                        elif opt2 == 1:
                            if info_dic[opt][1]:  # if it's a group
                                a = info_dic[opt][0].split("-")
                                b = a[1].split("@")
                                print "\n    Creator User          Timestamp"
                                print "--------------------------------------------"
                                print "   ", a[0], "\t", time.strftime('%d-%m-%Y %H:%M', time.localtime(int(b[0])))
                            else:  # if it's a broadcast
                                a, b = info_dic[opt][0].split("@")
                                print "\n    Creator User          Timestamp"
                                print "--------------------------------------------"
                                print "       Me \t\t", time.strftime('%d-%m-%Y %H:%M', time.localtime(int(a)))

                        elif opt2 == 2:
                            sql_string_info = "SELECT gjid, jid, admin, pending,sent_sender_key FROM group_participants WHERE gjid = '" + info_dic[opt][0] + "';"
                            consult_info = cursor.execute(sql_string_info)
                            i = 0
                            if info_dic[opt][1]:  # if it's a group
                                print "\n     Phone User        Admin"
                                print "---------------------------------------"
                                for data in consult_info:
                                    if data[1]:
                                        i += 1
                                        if i > 9:
                                            print i, ")", data[1].strip("@s.whatsapp.net"),\
                                                '\tYes' if int(data[2]) == 1 else '\tNo'
                                        else:
                                            print i, " )", data[1].strip("@s.whatsapp.net"),\
                                                '\tYes' if int(data[2]) == 1 else '\tNo'
                                    else:
                                        i += 1
                                        print i, " ) Me\t\t\t", 'Yes' if int(data[2]) == 1 else 'No'
                            else:  # if it's a broadcast
                                print "\n     Phone User"
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
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "changed the subject from '", str(data[17])[7:].decode('utf-8', 'ignore'), "' to '", data[4], "'"
                                        elif int(data[9]) == 4:
                                            if info_dic[opt][1]:
                                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "was added to the group"
                                            else:
                                                print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "was added to the list"
                                        elif int(data[9]) == 5:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "left the group"
                                        elif int(data[9]) == 6:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "changed the group icon"
                                            if data[17]:
                                                print "The last picture is stored on the phone path '/data/data/com.whatsapp/cache/Profile Pictures/" + (data[0].split('@'))[0] + ".jpg'"
                                                print "Thumbnail was saved on local path '" + os.getcwd() + "/Media/profiles/" + (data[0].split('@'))[0] + "(" + str(int(data[5]) / 1000) + ").jpg'"
                                            else:
                                                print "Thumbnail null"
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
                                            print Fore.GREEN + "Message:" + Fore.RESET + " Removed", data[15].strip("@s.whatsapp.net"), "from the list"
                                        elif int(data[9]) == 9:
                                            list_broadcast = (str(data[17])).split('@')
                                            list_copy = []
                                            for i in list_broadcast:
                                                list_copy.append("".join([x for x in i if x.isdigit()]))
                                            list_copy.pop()
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "created a broadcast list with", list_copy, "recipients"
                                        elif int(data[9]) == 10:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "changed to", ((str(data[17])[7:].decode('utf-8', 'ignore')).split('@'))[0]
                                        elif int(data[9]) == 11:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "created the group '", data[4], "'"
                                        elif int(data[9]) == 12:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "added", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "to the group"
                                        elif int(data[9]) == 14:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "eliminated", ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "from the group"
                                        elif int(data[9]) == 15:
                                            print Fore.GREEN + "Message:" + Fore.RESET, data[15].strip("@s.whatsapp.net"), "made you administrator"
                                        elif int(data[9]) == 18:
                                            if data[15]:
                                                print Fore.GREEN + "Message:" + Fore.RESET + " The security code of", data[15].strip("@s.whatsapp.net"), "changed"
                                            else:
                                                print Fore.GREEN + "Message:" + Fore.RESET + " The security code of", data[0].strip("@s.whatsapp.net"), "changed"
                                        elif int(data[9]) == 19:
                                            print Fore.GREEN + "Message:" + Fore.RESET + " Messages and calls in this chat are now protected with end-to-end encryption"
                                        elif int(data[9]) == 20:
                                            print Fore.GREEN + "Message:" + Fore.RESET, ((str(data[17])[60:].decode('utf-8', 'ignore')).split('@'))[0], "Joined using an invitation link from this group"
                                        print Fore.GREEN + "Timestamp:" + Fore.RESET , time.strftime('%d-%m-%Y %H:%M', time.localtime(int(data[5]) / 1000))

                            except Exception as e:
                                print "Error showing message details:", e
                                continue
                        else:
                            print "Bad option"

                    except Exception as e:
                        print "Error input data", e

        except Exception as e:
            print "Error input data", e


# Initializing
if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="To start choose a database and a mode with options")
    group_parser = parser.add_mutually_exclusive_group()
    parser.add_argument("database", help="database file path - './msgstore.db' by default", metavar="DATABASE", nargs='?', default="./msgstore.db")
    group_parser.add_argument("-k", "--key", help="*** Decrypt Mode *** - key file path")
    group_parser.add_argument("-i", "--info", help="*** Info Mode ***", action="store_true")
    group_parser.add_argument("-m", "--messages", help="*** Message Mode ***", action="store_true")
    parser.add_argument("-t", "--text", help="filter messages by text match")
    parser.add_argument("-u", "--user", help="filter messages made by a phone number")
    parser.add_argument("-g", "--group", help="filter messages made in a group number")
    parser.add_argument("-w", "--web", help="filter messages made by Whatsapp Web", action="store_true")
    parser.add_argument("-s", "--starred", help="filter messages starred by user", action="store_true")
    parser.add_argument("-b", "--broadcast", help="filter messages send by broadcast", action="store_true")
    parser.add_argument("-tS", "--time_start", help="filter messages by start time (dd-mm-yyyy HH:MM)")
    parser.add_argument("-tE", "--time_end", help="filter messages by end time (dd-mm-yyyy HH:MM)")
    filter_parser = parser.add_mutually_exclusive_group()
    filter_parser.add_argument("-tT", "--type_text", help="filter text messages", action="store_true")
    filter_parser.add_argument("-tI", "--type_image", help="filter image messages", action="store_true")
    filter_parser.add_argument("-tA", "--type_audio", help="filter audio messages", action="store_true")
    filter_parser.add_argument("-tV", "--type_video", help="filter video messages", action="store_true")
    filter_parser.add_argument("-tC", "--type_contact", help="filter contact messages", action="store_true")
    filter_parser.add_argument("-tL", "--type_location", help="filter location messages", action="store_true")
    filter_parser.add_argument("-tX", "--type_call", help="filter audio/video call messages", action="store_true")
    filter_parser.add_argument("-tP", "--type_application", help="filter application messages", action="store_true")
    filter_parser.add_argument("-tG", "--type_gif", help="filter GIF messages", action="store_true")
    filter_parser.add_argument("-tD", "--type_deleted", help="filter deleted object messages", action="store_true")
    filter_parser.add_argument("-tR", "--type_share", help="filter Real time location messages", action="store_true")

    #parser.add_argument("-o", "--output", help="create a PDF report")
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
                """ current date in Epoch milliseconds string """
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


#!/usr/bin/python
# -*- coding: utf-8 -*-

from gpsoauth import google
from configparser import ConfigParser
import json
import os
import re
import requests
import sys
import Queue as queue
import threading
import time
import argparse


# Define global variable
version = "0.1"
exitFlag = 0
bearer = ""
now = 0
nfiles = 0
queueLock = threading.Lock()
workQueue = queue.Queue(9999999)

def banner():
    """ Function Banner """
    print """
     __      __.__             ________      ________        .__ 
    /  \    /  \  |__ _____   /  _____/  ____\______ \_______|__|
    \   \/\/   /  |  \\\\__  \ /   \  ___ /  _ \|    |  \_  __ \  |
     \        /|   Y  \/ __ \\\\    \_\  (  <_> )    `   \  | \/  |
      \__/\  / |___|  (____  /\______  /\____/_______  /__|  |__|
           \/       \/     \/        \/              \/          

    ------------ Whatsapp Google Drive Extractor v""" + version + """ ------------
    """


def help():
    """ Function show help """
    print """    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t
    ** Fork from WhatsAppGDExtract by TripCode and forum.xda-developers.com
    
    Usage: python whagodri.py -h (for help)
    """


def create_settings_file():
    """ Function that creates the settings file """
    with open('./cfg/settings.cfg'.replace("/", os.path.sep), 'w') as cfg:
        cfg.write('[report]\nlogo = ./cfg/logo.png\ncompany =\nrecord =\nunit =\nexaminer =\nnotes =\n\n[auth]\ngmail = alias@gmail.com\npassw = yourpassword\ndevid = 1234567887654321\ncelnumbr = BackupPhoneNunmber\n\n[app]\npkg = com.whatsapp\nsig = 38a0f7d505fe18fec64fbf343ecaaaf310dbd799\n\n[client]\npkg = com.google.android.gms\nsig = 38918a453d07199354f8b19af05ec6562ced5788\nver = 9877000'.replace("/", os.path.sep))


def getConfigs():
    global gmail, passw, devid, pkg, sig, client_pkg, client_sig, client_ver, celnumbr
    config = ConfigParser()
    try:
        config.read('./cfg/settings.cfg'.replace("/", os.path.sep))
        gmail = config.get('auth', 'gmail')
        passw = config.get('auth', 'passw')
        devid = config.get('auth', 'devid')
        celnumbr = config.get('auth', 'celnumbr')
        pkg = config.get('app', 'pkg')
        sig = config.get('app', 'sig')
        client_pkg = config.get('client', 'pkg')
        client_sig = config.get('client', 'sig')
        client_ver = config.get('client', 'ver')
    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        quit('The "./cfg/settings.cfg" file is missing or corrupt!'.replace("/", os.path.sep))


def size(obj):
            if obj > 1048576:
                return "(" + "{0:.2f}".format(obj / float(1048576)) + " MB)"
            else:
                return "(" + "{0:.2f}".format(obj / float(1024)) + " KB)"


def getGoogleAccountTokenFromAuth():
 
    b64_key_7_3_29 = (b"AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveWLEwo6prwgi3"
                      b"iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3baEVGcmEgqaLZUNBjm057pK"
                      b"RI16kB0YppeGx5qIQ5QjKzsR8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/"
                      b"6rmf5AAAAAwEAAQ==")
 
    android_key_7_3_29 = google.key_from_b64(b64_key_7_3_29)
    encpass = google.signature(gmail, passw, android_key_7_3_29)
    payload = {'Email':gmail, 'EncryptedPasswd':encpass, 'app':client_pkg, 'client_sig':client_sig, 'parentAndroidId':devid}
    request = requests.post('https://android.clients.google.com/auth', data=payload)
    token = re.search('Token=(.*?)\n', request.text)
    
    if token:
        return token.group(1)
    else:
        quit(request.text)
 

def getGoogleDriveToken(token):
    payload = {'Token':token, 'app':pkg, 'client_sig':sig, 'device':devid, 'google_play_services_version':client_ver, 'service':'oauth2:https://www.googleapis.com/auth/drive.appdata https://www.googleapis.com/auth/drive.file', 'has_permission':'1'}
    request = requests.post('https://android.clients.google.com/auth', data=payload)
    token = re.search('Auth=(.*?)\n', request.text)
    if token:
        return token.group(1)
    else:
        quit(request.text)


def rawGoogleDriveRequest(bearer, url):
    headers = {'Authorization': 'Bearer '+bearer}
    request = requests.get(url, headers=headers)
    return request.text


def gDriveFileMapRequest(bearer):
    header = {'Authorization': 'Bearer '+bearer}
    url = "https://www.googleapis.com/drive/v2/files?mode=restore&spaces=appDataFolder&maxResults=1000&fields=items(description%2Cid%2CfileSize%2Ctitle%2Cmd5Checksum%2CmimeType%2CmodifiedDate%2Cparents(id)%2Cproperties(key%2Cvalue))%2CnextPageToken&q=title%20%3D%20'"+celnumbr+"-invisible'%20or%20title%20%3D%20'gdrive_file_map'%20or%20title%20%3D%20'Databases%2Fmsgstore.db.crypt12'%20or%20title%20%3D%20'Databases%2Fmsgstore.db.crypt11'%20or%20title%20%3D%20'Databases%2Fmsgstore.db.crypt10'%20or%20title%20%3D%20'Databases%2Fmsgstore.db.crypt9'%20or%20title%20%3D%20'Databases%2Fmsgstore.db.crypt8'"
    request = requests.get(url, headers=header)
    return request.text
 

def downloadFileGoogleDrive(bearer, url, local, m):
    if not os.path.exists(os.path.dirname(local)):
        os.makedirs(os.path.dirname(local))
    headers = {'Authorization': 'Bearer '+bearer}
    request = requests.get(url, headers=headers, stream=True)
    request.raw.decode_content = True
    if request.status_code == 200:
        with open(local, 'wb') as asset:
            for chunk in request.iter_content(1024):
                asset.write(chunk)
        print('    [-] Downloaded: "'+local+'".\n')
        logfile = 'cfg' + os.path.sep + 'files.log'
        if not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        with open(logfile, 'a') as log:
            log.write(m + '\n')
    else:
        print('    [-] Not Downloaded: "'+local+'".\n')


def gDriveFileMap():
    global bearer
    data = gDriveFileMapRequest(bearer)
    jres = json.loads(data)
    backups = []
    for result in jres['items']:
        try:
            if result['title'] == 'gdrive_file_map':
                backups.append((result['description'], rawGoogleDriveRequest(bearer, 'https://www.googleapis.com/drive/v2/files/'+result['id']+'?alt=media')))
        except Exception as e:
            print("[e] Error", e)
            pass
    if len(backups) == 0:
        print '[e] Unable to locate google drive file map for: '+pkg
    return backups


def localFileList():
    lmd5 = []
    logfile = 'cfg' + os.path.sep + 'files.log'
    if os.path.isfile(logfile):
        flist = open(logfile, 'r')
        for line in flist:
            lmd5.append(line.strip("\n"))
    return lmd5


class myThread(threading.Thread):

    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q

    def run(self):
        process_data(self.name, self.q)


def process_data(threadName, q):
    while not exitFlag:
        queueLock.acquire()
        if not workQueue.empty():
            data = q.get()
            queueLock.release()
            getMultipleFilesThread(data['bearer'], data['entries_r'], data['local'], data['entries_m'], threadName)
        else:
            queueLock.release()
            time.sleep(1)


def getMultipleFilesThread(bearer, entries_r, local, entries_m, threadName):
    global nfiles, now
    url = 'https://www.googleapis.com/drive/v2/files/'+entries_r+'?alt=media'
    if not os.path.exists(os.path.dirname(local)):
        os.makedirs(os.path.dirname(local))
    headers = {'Authorization': 'Bearer '+bearer}
    request = requests.get(url, headers=headers, stream=True)
    request.raw.decode_content = True
    time.sleep(1)
    if request.status_code == 200:
        with open(local, 'wb') as asset:
            for chunk in request.iter_content(1024):
                asset.write(chunk)
        now += 1
        print "    [+] Number: " + str(now) + " / " + str(nfiles)
        print "        [-] " + threadName + "=> Downloaded: '" + local + "'\n"

        logfile = 'cfg' + os.path.sep + 'files.log'
        if not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        with open(logfile, 'a') as log:
            log.write(entries_m + '\n')
    else:
        now += 1
        print "    [+] Number: " + str(now)
        print "        [-] " + threadName + "=> Not Downloaded: '" + local + "'\n"


def getMultipleFiles(data, folder, i):
    global nfiles, now
    threadList = ["Thread-01", "Thread-02", "Thread-03", "Thread-04", "Thread-05", "Thread-06", "Thread-07", "Thread-08", "Thread-09", "Thread-10",
                  "Thread-11", "Thread-12", "Thread-13", "Thread-14", "Thread-15", "Thread-16", "Thread-17", "Thread-18", "Thread-19", "Thread-20",
                  "Thread-21", "Thread-22", "Thread-23", "Thread-24", "Thread-25", "Thread-26", "Thread-27", "Thread-28", "Thread-29", "Thread-30",
                  "Thread-31", "Thread-32", "Thread-33", "Thread-34", "Thread-35", "Thread-36", "Thread-37", "Thread-38", "Thread-39", "Thread-40"]
    threads = []
    threadID = 1
    print "[i] Generating threads..."
    print "[+] Backup ID: " + str(i)
    for tName in threadList:
        thread = myThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1
    files = localFileList()
    data = json.loads(data)
    nfiles = len(data)
    #  print(json.dumps(data, indent=4, sort_keys=True))
    #  exit()
    now = 0
    queueLock.acquire()
    for entries in data:
        local = folder + os.path.sep + entries['f'].replace("/", os.path.sep)
        if entries['m'] in files:
            if os.path.isfile(local) or 'WhatsApp/Backups/chatsettingsbackup.db.crypt1' in local:
                now += 1
                print "    [+] Number: " + str(now)
                print "        [-] Skipped: '" + local + "'\n"
        else:
            workQueue.put({'bearer':bearer, 'entries_r':entries['r'], 'local':local, 'entries_m':entries['m']})
    queueLock.release()
    while not workQueue.empty():
        pass
    global exitFlag
    exitFlag = 1
    for t in threads:
        t.join()
    print "[i] Downloads finished"


# Initializing


if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Extract your Whatsapp files from Google Drive")
    user_parser = parser.add_mutually_exclusive_group()
    user_parser.add_argument("-i", "--info", help="Show information about Whatsapp backups", action="store_true")
    user_parser.add_argument("-l", "--list", help="List all available files", action="store_true")
    user_parser.add_argument("-lw", "--list_whatsapp", help="List Whatsapp backups", action="store_true")
    user_parser.add_argument("-p", "--pull", help="Pull a file from Google Drive", nargs=2, metavar=("FilePath", "BackupID"))
    user_parser.add_argument("-s", "--sync", help="Sync all files locally", action="store_true")
    parser.add_argument("-f", "--flush", help="Flush log file to sync from the beginning", action="store_true")
    args = parser.parse_args()
    if os.path.isfile('./cfg/settings.cfg'.replace("/", os.path.sep)) is False:
        create_settings_file()
    if len(sys.argv) == 1:
        help()
    else:
        print "[i] Searching...\n"
        getConfigs()
        bearer = getGoogleDriveToken(getGoogleAccountTokenFromAuth())
        drives = gDriveFileMap()

        if args.flush:
            logfile = 'cfg' + os.path.sep + 'files.log'
            if not os.path.exists(os.path.dirname(logfile)):
                os.makedirs(os.path.dirname(logfile))
            with open(logfile, 'w') as log:
                log.write("")
            print "[i] Log flushed\n"

        if args.info: # Test if exists more backups ID?????
            for i, drive in enumerate(drives):
                if len(drives) > 0:
                    print "[+] Backup ID: " + str(i)
                    data = drive[0]
                    data_json = json.loads(data)
                    # print data_json  # To check if there are more data
                    print "    [-] Backup Frequency        : " + str(data_json['backupFrequency'])
                    print "    [-] Backup Network Settings : " + str(data_json['backupNetworkSettings'])
                    print "    [-] Backup Version          : " + str(data_json['backupVersion'])
                    print "    [-] Include Videos In Backup: " + str(data_json['includeVideosInBackup'])
                    print "    [-] Backup Size             : " + str(data_json['backupSize']) + " Bytes " + size(int(data_json['backupSize']))
                    print "    [-] Media Size              : " + str(data_json['mediaSize']) + " Bytes " +  size(int(data_json['mediaSize']))
                    print "    [-] Chat DB Size            : " + str(data_json['chatdbSize']) + " Bytes " + size(int(data_json['chatdbSize']))
                    print "    [-] Num Of Messages         : " + str(data_json['numOfMessages'])
                    print "    [-] Num Of Media Files      : " + str(data_json['numOfMediaFiles'])
                    print "    [-] Num Of Photos           : " + str(data_json['numOfPhotos'])
                    print "    [-] Video Size              : " + str(data_json['videoSize']) + " Bytes " + size(int(data_json['videoSize']))
                    print "    [+] Local Settings          : "
                    print "        [-] Conversation Sound    : " + str(data_json['localSettings']['conversation_sound'])
                    print "        [-] Input Enter Send      : " + str(data_json['localSettings']['input_enter_send'])
                    print "        [-] Interface Font Size   : " + str(data_json['localSettings']['interface_font_size'])
                    print "        [-] Security Notifications: " + str(data_json['localSettings']['security_notifications'])
                    print "        [-] Settings Language     : " + str(data_json['localSettings']['settings_language'])
                    print "        [-] VoIP Low Data Usage   : " + str(data_json['localSettings']['voip_low_data_usage'])
                    print ""

        elif args.list:
            nfile = 0
            for i, drive in enumerate(drives):
                if len(drives) > 0:
                    print("[+] Backup ID: " + str(i))
                    data = drive[1]
                    data_json = json.loads(data)
                    for entries in data_json:
                        nfile += 1
                        print "    [+] Number: " + str(nfile) + " / " + str(nfiles)
                        print "        [-] File    : " + entries['f']
                        print "        [-] Hash MD5: " + entries['m']
                        print "        [-] Request : " + entries['r']
                        print "        [-] Size    : " + entries['s'] + " Bytes " + size(int(entries['s'])) + "\n"

        if args.list_whatsapp:
            nfile = 0
            for i, drive in enumerate(drives):
                if len(drives) > 0:
                    print("[+] Backup ID: " + str(i))
                    data = drive[1]
                    data_json = json.loads(data)
                    for entries in data_json:
                        nfile += 1
                        if entries['f'] == "Databases/msgstore.db.crypt12":
                            target = entries['f'], entries['m'], entries['r'], entries['s']
                    print "    [+] Number: " + str(nfile) + " / " + str(nfiles)
                    print "        [-] File    : " + target[0]
                    print "        [-] Hash MD5: " + target[1]
                    print "        [-] Request : " + target[2]
                    print "        [-] Size    : " + target[3] + " Bytes " + size(int(target[3])) + "\n"

        if args.sync:
            logfile = 'cfg' + os.path.sep + 'files.log'
            if not os.path.exists(os.path.dirname(logfile)):
                os.makedirs(os.path.dirname(logfile))
            for i, drive in enumerate(drives):
                folder = 'WhatsApp'
                if len(drives) > 1:
                    folder = 'WhatsApp-' + str(i)  #  Check with more backupsID
                getMultipleFiles(drive[1], folder, i)
                """data = drive[1]
                data_json = json.loads(data)
                for entries in data_json:
                    logfile = 'cfg' + os.path.sep + 'files2.log'
                    if not os.path.exists(os.path.dirname(logfile)):
                        os.makedirs(os.path.dirname(logfile))
                    with open(logfile, 'a') as log:
                        log.write(entries['m']+"\n")"""

        if args.pull:
            FilePath = str(sys.argv[2])
            BackupID = int(sys.argv[3])
            try:
                drive = drives[BackupID]
            except IndexError:
                print "[e] Invalid backup ID: " + str(BackupID) + "\n"

            data = drive[1]
            data_json = json.loads(data)
            for entries in data_json:
                if entries['f'] == FilePath:
                    target = entries['f'], entries['m'], entries['r'], entries['s']
            try:
                f = target[0]  # File
                m = target[1]  # Md5
                r = target[2]  # Request
                local = 'WhatsApp' + os.path.sep + f.replace("/", os.path.sep)
                if os.path.isfile(local):
                    print('[+] Backup: ' + str(BackupID))
                    print('    [-] Skipped: "' + local + '"\n')
                else:
                    print('[+] Backup: ' + str(BackupID))
                    downloadFileGoogleDrive(bearer, 'https://www.googleapis.com/drive/v2/files/' + r + '?alt=media',local, m)
            except NameError:
                print '[e] Unable to locate: "' + FilePath + '"\n'

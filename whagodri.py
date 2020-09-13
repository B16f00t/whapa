from gpsoauth import google
from configparser import ConfigParser
import json
import os
import re
import requests
import sys
import queue as queue
import threading
import time
import argparse


# Define global variable
auth_url = 'https://android.clients.google.com/auth'
header = {'User-Agent': 'WhatsApp/2.20.200 Android/Device/Whapa'}
devid = '1234567887654321'    # Android Device ID
exitFlag = 0
nextPageToken = ""
backups = []
bearer = ""
queueLock = threading.Lock()
workQueue = queue.Queue(9999999)


def banner():
    """ Function Banner """
    print("""
     __      __.__             ________      ________        .__ 
    /  \    /  \  |__ _____   /  _____/  ____\______ \_______|__|
    \   \/\/   /  |  \\\\__  \ /   \  ___ /  _ \|    |  \_  __ \  |
     \        /|   Y  \/ __ \\\\    \_\  (  <_> )    `   \  | \/  |
      \__/\  / |___|  (____  /\______  /\____/_______  /__|  |__|
           \/       \/     \/        \/              \/          

    -------------- Whatsapp Google Drive Extractor --------------""")


def help():
    """ Function show help """
    print("""    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t
    ** Fork from WhatsAppGDExtract by TripCode and forum.xda-developers.com
    
    Usage: python3 whagodri.py -h (for help)
    """)


def create_settings_file():
    """ Function that creates the settings file """
    with open('./cfg/settings.cfg'.replace("/", os.path.sep), 'w') as cfg:
        cfg.write('[report]\nlogo = ./cfg/logo.png\ncompany =\nrecord =\nunit =\nexaminer =\nnotes =\n\n[auth]\ngmail = alias@gmail.com\npassw = yourpassword\ncelnumbr = BackupPhoneNunmber')


def getConfigs():
    global gmail, passw, celnumbr
    config = ConfigParser()
    try:
        config.read('./cfg/settings.cfg'.replace("/", os.path.sep))
        gmail = config.get('auth', 'gmail')
        passw = config.get('auth', 'passw')
        celnumbr = config.get('auth', 'celnumbr').lstrip('+0')

    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        quit('The "./cfg/settings.cfg" file is missing or corrupt!'.replace("/", os.path.sep))


def size(obj):
    if obj > 1048576:
        return "(" + "{0:.2f}".format(obj / float(1048576)) + " MB)"
    else:
        return "(" + "{0:.2f}".format(obj / float(1024)) + " KB)"


def getGoogleAccountTokenFromAuth():
    b64_key_7_3_29 = (b"AAAAgMom/1a/v0lblO2Ubrt60J2gcuXSljGFQXgcyZWveWLEwo6prwgi3iJIZdodyhKZQrNWp5nKJ3srRXcUW+F1BD3baEVGcmEgqaLZUNBjm057pKRI16kB0YppeGx5qIQ5QjKzsR8ETQbKLNWgRY0QRNVz34kMJR3P/LgHax/6rmf5AAAAAwEAAQ==")
    android_key_7_3_29 = google.key_from_b64(b64_key_7_3_29)
    encpass = google.signature(gmail, passw, android_key_7_3_29)
    pkg = 'com.google.android.gms' 	                    # APK package name Google Play Services
    sig = '38918a453d07199354f8b19af05ec6562ced5788'    # APK Google Play Services certificate fingerprint SHA-1
    payload = {'Email':gmail, 'EncryptedPasswd':encpass, 'app':pkg, 'client_sig':sig, 'parentAndroidId':devid}
    request = requests.post(auth_url, data=payload, headers=header)
    print("Requesting Auth for Google....")
    #print(request.text)
    token = re.search('Token=(.*)', request.text)
    if token:
        print("Granted\n")
        return token.group(1)
    else:
        print("Failed\n")
        print(request.text)
        if "BadAuthentication" in request.text:
            print("\n   Workaround\n-----------------")
            print("1. Check that your email and password are correct, if so change your google password and try again.\n"
                  "2. Your are using a old python version. Works > 3.7.7.\n"
                  "3. Update the gpsoauth dependency to its latest version, use in a terminal: 'pip install -U gpsoauth' or 'pip3 install -U gpsoauth'")

        elif "NeedsBrowser" in request.text:
            print("\n   Workaround\n-----------------")
            print("1. You have double factor authentication enabled, so disable it in this URL: https://myaccount.google.com/security")
            print("2. If you want to use 2FA, you will have to go to the URL: https://myaccount.google.com/apppasswords\n"
                  "   Then select Application: Other. Write down: Whapa, and a password will be display, then you must write the password in your settings.cfg.")

        elif "DeviceManagementRequiredOrSyncDisabled" in request.text:
            print("\n   Workaround\n-----------------")
            print("1. You are using a GSuite account.  The reason for this is, that for this google-apps account, the enforcement of policies on mobile clients is enabled in admin console (enforce_android_policy).\n"
                  "   If you disable this in admin-console, the authentication works.")

        quit()


def getGoogleDriveToken(token):
    pkg = 'com.whatsapp'                              # APK package name Whatsapp
    sig = '38a0f7d505fe18fec64fbf343ecaaaf310dbd799'  # APK Whatsapp certificate fingerprint SHA-1
    ver = '203315028'                                 # APK Google Play Services Version: 20.33.15
    payload = {'Token':token, 'app':pkg, 'client_sig':sig, 'device':devid, 'google_play_services_version':ver, 'service':'oauth2:https://www.googleapis.com/auth/drive.appdata https://www.googleapis.com/auth/drive.file', 'has_permission':'1'}
    request = requests.post(auth_url, data=payload, headers=header)
    print("Getting Token from Google....")
    token = re.search('Auth=(.*)', request.text)
    #print(request.text)
    if token:
        print("Granted\n")
        return token.group(1)
    else:
        print("Failed\n")
        quit(request.text)


def gDriveFileMap(bearer, nextPageToken):
    header = {'Authorization': 'Bearer ' + bearer, 'User-Agent': 'WhatsApp/2.20.200 Android/Device/Whapa'}
    url_data = "https://backup.googleapis.com/v1/clients/wa/backups/{}".format(celnumbr)
    url_files = "https://backup.googleapis.com/v1/clients/wa/backups/{}/files?{}pageSize=5000".format(celnumbr, "pageToken=" + nextPageToken + "&")
    request_data = requests.get(url_data, headers=header)
    request_files = requests.get(url_files, headers=header)
    data_data = json.loads(request_data.text)
    data_files = json.loads(request_files.text)
    try:
        try:
            nextPageToken = data_files['nextPageToken']
        except Exception as e:
            nextPageToken = ""

        for result in data_files['files']:
            backups.append(result['name'])
        if nextPageToken:
            gDriveFileMap(bearer, nextPageToken)

    except Exception as e:
        print('[e]', data_files['error']['message'])
        if  data_files['error']['details'][0]['resourceName'] and data_files['error']['details'][0]['description']:
            print('[e]', data_files['error']['details'][0]['resourceName'] + ' - ' + data_files['error']['details'][0]['description'])

        if "entity was not found" in data_files['error']['message']:
            print("\n   Workaround\n-----------------")
            print("1. The phone number may be misspelled. Try to set country code + phone number.")
            print("2. No backup for that phone number in that gmail account or a bad backup has been made.\n   Check your backup in this URL: https://drive.google.com/drive/backups\n"
                  "   If there is a backup for that phone number, overwriting it may not work so manually delete the backup and do it again through WhatsApp..")

        elif "Backup " in data_files['error']['message']:
            print("\n   Workaround\n-----------------")
            print("1. The phone number for that google account does not have backup enabled. ")

        quit()

    return data_data, backups


def downloadFileGoogleDrive(bearer, url, local):
    os.makedirs(os.path.dirname(local), exist_ok=True)
    header = {'Authorization': 'Bearer ' + bearer, 'User-Agent': 'WhatsApp/2.19.244 Android/Device/Whapa'}
    request = requests.get(url, headers=header, stream=True)
    request.raw.decode_content = True
    if request.status_code == 200:
        with open(local, 'wb') as asset:
            for chunk in request.iter_content(1024):
                asset.write(chunk)
        print("    [-] Downloaded     : {}".format(local))
    else:
        print("    [-] Not downloaded : {}".format(local))


def getMultipleFiles(drives, bearer, files):
    threadList = ["Thread-01", "Thread-02", "Thread-03", "Thread-04", "Thread-05", "Thread-06", "Thread-07", "Thread-08", "Thread-09", "Thread-10",
                  "Thread-11", "Thread-12", "Thread-13", "Thread-14", "Thread-15", "Thread-16", "Thread-17", "Thread-18", "Thread-19", "Thread-20",
                  "Thread-21", "Thread-22", "Thread-23", "Thread-24", "Thread-25", "Thread-26", "Thread-27", "Thread-28", "Thread-29", "Thread-30",
                  "Thread-31", "Thread-32", "Thread-33", "Thread-34", "Thread-35", "Thread-36", "Thread-37", "Thread-38", "Thread-39", "Thread-40"]
    threads = []
    threadID = 1
    print("[i] Generating threads...")
    print("[+] Backup name : {}".format(drives["name"]))
    for tName in threadList:
        thread = myThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1

    n = 1
    lenfiles = len(files)
    queueLock.acquire()
    if args.output:
        output = args.output
    else:
        output = ""

    for entries in files:
        file = entries.split('files/')[1]
        local_store = (output + file).replace("/", os.path.sep)
        if os.path.isfile(local_store):
            print("    [-] Number: {}/{}  => {} Skipped".format(n, lenfiles, local_store))
        else:
            url = "https://backup.googleapis.com/v1/clients/wa/backups/{}/files/{}?alt=media".format(celnumbr, file)
            workQueue.put({'bearer': bearer, 'url': url, 'local': local_store, 'now': n, 'lenfiles': lenfiles})
        n += 1

    queueLock.release()
    while not workQueue.empty():
        pass

    global exitFlag
    exitFlag = 1
    for t in threads:
        t.join()
    print("[i] Downloads finished")


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
            getMultipleFilesThread(data['bearer'], data['url'], data['local'], data['now'], data['lenfiles'], threadName)
            time.sleep(1)

        else:
            queueLock.release()
            time.sleep(1)


def getMultipleFilesThread(bearer, url, local, now, lenfiles, threadName):
    os.makedirs(os.path.dirname(local), exist_ok=True)
    header = {'Authorization': 'Bearer ' + bearer, 'User-Agent': 'WhatsApp/2.19.244'}
    request = requests.get(url, headers=header, stream=True)
    request.raw.decode_content = True
    if request.status_code == 200:
        with open(local, 'wb') as asset:
            for chunk in request.iter_content(1024):
                asset.write(chunk)
        print("    [-] Number: {}/{} - {} => Downloaded: {}".format(now, lenfiles,  threadName, local))

    else:
        print("    [-] Number: {}/{} - {} => Not downloaded: {}".format(now, lenfiles,  threadName, local))


# Initializing
if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Extract your Whatsapp files from Google Drive")
    user_parser = parser.add_mutually_exclusive_group()
    user_parser.add_argument("-i", "--info", help="Show information about Whatsapp backups", action="store_true")
    user_parser.add_argument("-l", "--list", help="List all available files", action="store_true")
    user_parser.add_argument("-lw", "--list_whatsapp", help="List Whatsapp backups", action="store_true")
    user_parser.add_argument("-p", "--pull", help="Pull a file from Google Drive")
    user_parser.add_argument("-s", "--sync", help="Sync all files locally", action="store_true")
    user_parser.add_argument("-si", "--s_images", help="Sync Images files locally", action="store_true")
    user_parser.add_argument("-sv", "--s_videos", help="Sync Videos files locally", action="store_true")
    user_parser.add_argument("-sa", "--s_audios", help="Sync Audios files locally", action="store_true")
    user_parser.add_argument("-sx", "--s_documents", help="Sync Documents files locally", action="store_true")
    user_parser.add_argument("-sd", "--s_databases", help="Sync Databases files locally", action="store_true")
    parser.add_argument("-o", "--output", help="Output path to save files")
    args = parser.parse_args()
    if os.path.isfile('./cfg/settings.cfg'.replace("/", os.path.sep)) is False:
        create_settings_file()

    if len(sys.argv) == 0:
        help()
    else:
        print("[i] Searching...\n")
        getConfigs()
        bearer = getGoogleDriveToken(getGoogleAccountTokenFromAuth())
        #print("Your Google Access Token: {}\n".format(bearer))
        drives, files = gDriveFileMap(bearer, nextPageToken)

        if args.info:
            try:
                print("[-] Backup name   : {}".format(drives["name"]))
                print("[-] Backup upload : {}".format(drives["updateTime"]))
                print("[-] Backup size   : {} Bytes {}".format(drives["sizeBytes"], size(int(drives["sizeBytes"]))))
                print("[+] Backup metadata")
                print("    [-] Backup Frequency         : {} ".format(json.loads(drives["metadata"])["backupFrequency"]))
                print("    [-] Backup Network Settings  : {} ".format(json.loads(drives["metadata"])["backupNetworkSettings"]))
                print("    [-] Backup Version           : {} ".format(json.loads(drives["metadata"])["backupVersion"]))
                print("    [-] Include Videos In Backup : {} ".format(json.loads(drives["metadata"])["includeVideosInBackup"]))
                print("    [-] Num Of Photos            : {}".format(json.loads(drives["metadata"])["numOfPhotos"]))
                print("    [-] Num Of Media Files       : {}".format(json.loads(drives["metadata"])["numOfMediaFiles"]))
                print("    [-] Num Of Messages          : {}".format(json.loads(drives["metadata"])["numOfMessages"]))
                print("    [-] Video Size               : {} Bytes {}".format(json.loads(drives["metadata"])["videoSize"], size(int(json.loads(drives["metadata"])["videoSize"]))))
                print("    [-] Backup Size              : {} Bytes {}".format(json.loads(drives["metadata"])["backupSize"], size(int(json.loads(drives["metadata"])["backupSize"]))))
                print("    [-] Media Size               : {} Bytes {}".format(json.loads(drives["metadata"])["mediaSize"], size(int(json.loads(drives["metadata"])["mediaSize"]))))
                print("    [-] Chat DB Size             : {} Bytes {}".format(json.loads(drives["metadata"])["chatdbSize"], size(int(json.loads(drives["metadata"])["chatdbSize"]))))

            except Exception as e:
                print("[e] Error {}".format(e))

        elif args.list:
            print("[+] Backup name : {}".format(drives["name"]))
            lenfiles = len(files)
            n = 1
            for i in files:
                print("    [-] File {}/{}  : {}".format(n, lenfiles, i.split('files/')[1]))
                n += 1

        if args.list_whatsapp:
            print("[+] Backup name : {}".format(drives["name"]))
            lenfiles = len(files)
            n = 1
            for i in files:
                i = i.split('files/')[1]
                if i == "Databases/msgstore.db.crypt12":
                    print("    [-] File {}/{}   : {}".format(n, lenfiles, i))
                    print("    [-] Chat DB Size : {} Bytes {}".format(json.loads(drives["metadata"])["chatdbSize"], size(int(json.loads(drives["metadata"])["chatdbSize"]))))
                    exit()
                n += 1

        if args.sync:
            getMultipleFiles(drives, bearer, files)

        if args.s_images:
            filter = []
            for i in files:
                try:
                    if i.split("/")[6] == ".Statuses" or i.split("/")[6] == "WhatsApp Images" or i.split("/")[6] == "WhatsApp Stickers" or i.split("/")[6] == "WhatsApp Profile Photos" or i.split("/")[6] == "WallPaper":
                        filter.append(i)
                except Exception as e:
                    pass
            getMultipleFiles(drives, bearer, filter)

        if args.s_videos:
            filter = []
            for i in files:
                try:
                    if i.split("/")[6] == ".Statuses" or i.split("/")[6] == "WhatsApp Animated Gifs" or i.split("/")[6] == "WhatsApp Video":
                        filter.append(i)
                except Exception as e:
                    pass
            getMultipleFiles(drives, bearer, filter)

        if args.s_audios:
            filter = []
            for i in files:
                try:
                    if i.split("/")[6] == "WhatsApp Voice Notes" or i.split("/")[6] == "WhatsApp Audio":
                        filter.append(i)
                except Exception as e:
                    pass
            getMultipleFiles(drives, bearer, filter)

        if args.s_documents:
            filter = []
            for i in files:
                try:
                    if i.split("/")[6] == "WhatsApp Documents":
                        filter.append(i)
                except Exception as e:
                    pass
            getMultipleFiles(drives, bearer, filter)

        if args.s_databases:
            filter = []
            for i in files:
                try:
                    if i.split("/")[5] == "Databases" or i.split("/")[5] == "Backups" or i.split("/")[5] == "gdrive_file_map":
                        filter.append(i)
                except Exception as e:
                    pass
            getMultipleFiles(drives, bearer, filter)

        if args.pull:
            try:
                file = str(args.pull)
                local_store = file.replace("/", os.path.sep)

                if args.output:
                    local_store = args.output + local_store
                if os.path.isfile(local_store):
                    print("[+] Backup name : {}".format(drives["name"]))
                    print("    [-] Skipped : {}".format(local_store))
                else:
                    print("[+] Backup name        : {}".format(drives["name"]))
                    downloadFileGoogleDrive(bearer, "https://backup.googleapis.com/v1/clients/wa/backups/{}/files/{}?alt=media".format(celnumbr, file), local_store)
            except Exception as e:
                print("[e] Unable to locate: {}".format(file))

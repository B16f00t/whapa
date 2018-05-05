#!/usr/bin/python3
# -*- coding: utf-8 -*-

from configparser import ConfigParser
import json
import os
import re
import requests
import sys
import queue
import threading
import time
from pyportify.gpsoauth import google
exitFlag = 0


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
        print("https://accounts.google.com/DisplayUnlockCaptcha")
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
 
def downloadFileGoogleDrive(bearer, url, local):
    if not os.path.exists(os.path.dirname(local)):
        os.makedirs(os.path.dirname(local))
    if os.path.isfile(local):
        os.remove(local)
    headers = {'Authorization': 'Bearer '+bearer}
    request = requests.get(url, headers=headers, stream=True)
    request.raw.decode_content = True
    if request.status_code == 200:
        with open(local, 'wb') as asset:
            for chunk in request.iter_content(1024):
                asset.write(chunk)
    print('Downloaded: "'+local+'".')
 
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
            print("Error", e)
            pass
    if len(backups) == 0:
        quit('Unable to locate google drive file map for: '+pkg)
    return backups
 
def getConfigs():
    global gmail, passw, devid, pkg, sig, client_pkg, client_sig, client_ver, celnumbr
    config = ConfigParser()
    try:
        config.read('./cfg/settings.cfg')
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
        quit('The "./cfg/settings.cfg" file is missing or corrupt!')
 
def jsonPrint(data):
    print(json.dumps(json.loads(data), indent=4, sort_keys=True))
 
def localFileLog(md5):
    logfile = 'logs'+os.path.sep+'files.log'
    if not os.path.exists(os.path.dirname(logfile)):
        os.makedirs(os.path.dirname(logfile))
    with open(logfile, 'a') as log:
        log.write(md5+'\n')
 
def localFileList():
    logfile = 'logs'+os.path.sep+'files.log'
    if os.path.isfile(logfile):
        flist = open(logfile, 'r')
        return [line.split('\n') for line in flist.readlines()]
    else:
        open(logfile, 'w')
        return localFileList()

 
def getSingleFile(data, asset):
    data = json.loads(data)
    for entries in data:
        if entries['f'] == asset:
            return entries['f'], entries['m'], entries['r'], entries['s']

class myThread (threading.Thread):
    def __init__(self, threadID, name, q):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.q = q
    def run(self):
        print ('a：' + self.name)
        process_data(self.name, self.q)
        print ('b：' + self.name)

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
        url = 'https://www.googleapis.com/drive/v2/files/'+entries_r+'?alt=media'
        if not os.path.exists(os.path.dirname(local)):
            os.makedirs(os.path.dirname(local))
        if os.path.isfile(local):
            os.remove(local)
        headers = {'Authorization': 'Bearer '+bearer}
        request = requests.get(url, headers=headers, stream=True)
        request.raw.decode_content = True
        if request.status_code == 200:
            with open(local, 'wb') as asset:
                for chunk in request.iter_content(1024):
                    asset.write(chunk)
        print(threadName + '=> Downloaded: "'+local+'".')
        logfile = 'logs'+os.path.sep+'files.log'
        if not os.path.exists(os.path.dirname(logfile)):
            os.makedirs(os.path.dirname(logfile))
        with open(logfile, 'a') as log:
            log.write(entries_m+'\n')

queueLock = threading.Lock()
workQueue = queue.Queue(9999999)

 
def getMultipleFiles(data, folder):
    threadList = ["Thread-1", "Thread-2", "Thread-3", "Thread-4", "Thread-5", "Thread-6", "Thread-7", "Thread-8", "Thread-9", "Thread-10", "Thread-11", "Thread-12", "Thread-13", "Thread-14", "Thread-15", "Thread-16", "Thread-17", "Thread-18", "Thread-19", "Thread-20"]
    threads = []
    threadID = 1
    for tName in threadList:
        thread = myThread(threadID, tName, workQueue)
        thread.start()
        threads.append(thread)
        threadID += 1
    files = localFileList()
    data = json.loads(data)
    queueLock.acquire()
    for entries in data:
        if any(entries['m'] in lists for lists in files) is False or 'database' in entries['f'].lower():
            local = folder+os.path.sep+entries['f'].replace("/", os.path.sep)
            if os.path.isfile(local) and 'database' not in local.lower():
                quit('Skipped: "'+local+'".')
            else:
                workQueue.put({'bearer':bearer, 'entries_r':entries['r'], 'local':local, 'entries_m':entries['m']})
    queueLock.release()
    while not workQueue.empty():
        pass
    exitFlag = 1
    for t in threads:
        t.join()
    print ("Exit the main thread")


def runMain(mode, asset, bID):
    global bearer
    getConfigs()
    bearer = getGoogleDriveToken(getGoogleAccountTokenFromAuth())
    drives = gDriveFileMap()
    if mode == 'info':
        for i, drive in enumerate(drives):
            if len(drives) > 1:
                print("Backup: "+str(i))
            jsonPrint(drive[0])
    elif mode == 'list':
        for i, drive in enumerate(drives):
            if len(drives) > 1:
                print("Backup: "+str(i))
            jsonPrint(drive[1])
    elif mode == 'pull':
        try:
            drive = drives[bID]
        except IndexError:
            quit("Invalid backup ID: " + bID)
        target = getSingleFile(drive[1], asset)
        try:
            f = target[0]
            m = target[1]
            r = target[2]
            s = target[3]
        except TypeError:
            quit('Unable to locate: "'+asset+'".')
        local = 'WhatsApp'+os.path.sep+f.replace("/", os.path.sep)
        if os.path.isfile(local) and 'database' not in local.lower():
            quit('Skipped: "'+local+'".')
        else:
            downloadFileGoogleDrive(bearer, 'https://www.googleapis.com/drive/v2/files/'+r+'?alt=media', local)
            localFileLog(m)
    elif mode == 'sync':
        for i, drive in enumerate(drives):
            folder = 'WhatsApp'
            if len(drives) > 1:
                print('Backup: '+str(i))
                folder = 'WhatsApp-' + str(i)
            getMultipleFiles(drive[1], folder)
 
def main():
    args = len(sys.argv)
    if  args < 2 or str(sys.argv[1]) == '-help' or str(sys.argv[1]) == 'help':
        print('\nUsage: '+str(sys.argv[0])+' -help|-vers|-info|-list|-sync|-pull file [backupID]\n\nExamples:\n')
        print('python '+str(sys.argv[0])+' -help (this help screen)')
        print('python '+str(sys.argv[0])+' -vers (version information)')
        print('python '+str(sys.argv[0])+' -info (google drive app settings)')
        print('python '+str(sys.argv[0])+' -list (list all availabe files)')
        print('python '+str(sys.argv[0])+' -sync (sync all files locally)')
        print('python '+str(sys.argv[0])+' -pull "Databases/msgstore.db.crypt12" [backupID] (download)\n')
    elif str(sys.argv[1]) == '-info' or str(sys.argv[1]) == 'info':
        runMain('info', 'settings', 0)
    elif str(sys.argv[1]) == '-list' or str(sys.argv[1]) == 'list':
        runMain('list', 'all', 0)
    elif str(sys.argv[1]) == '-sync' or str(sys.argv[1]) == 'sync':
        runMain('sync', 'all', 0)
    elif str(sys.argv[1]) == '-vers' or str(sys.argv[1]) == 'vers':
        print('\nFork from WhatsAppGDExtract by TripCode\nWhatsapp Google Extractor Tool for whapa.py v0.5')
    elif args < 3:
        quit('\nUsage: python '+str(sys.argv[0])+' -help|-vers|-info|-list|-sync|-pull file [backupID]\n')
    elif str(sys.argv[1]) == '-pull' or str(sys.argv[1]) == 'pull':
        try:
            bID = int(sys.argv[3])
        except (IndexError, ValueError):
            bID = 0
        runMain('pull', str(sys.argv[2]), bID)
    else:
        quit('\nUsage: python '+str(sys.argv[0])+' -help|-vers|-info|-list|-sync|-pull file [backupID]\n')


if __name__ == "__main__":
    if os.path.isfile("./logs") is False:
        distutils.dir_util.mkpath("./logs")
    main()

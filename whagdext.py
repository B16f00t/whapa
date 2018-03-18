#!/usr/bin/env python

from configparser import ConfigParser
import json
import os
import re
import requests
import sys

import requests

from pyportify.gpsoauth import google

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
        print("If you have a problem press this link https://accounts.google.com/b/0/DisplayUnlockCaptcha")
        return token.group(1)
    else:
        quit(request.text)

def rawGoogleDriveRequest(bearer, url):
    headers = {'Authorization': 'Bearer '+bearer}
    request = requests.get(url, headers=headers)
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
    data = rawGoogleDriveRequest(bearer, 'https://www.googleapis.com/drive/v2/files')
    jres = json.loads(data)
    backups = []
    for result in jres['items']:
        try:
            if result['title'] == 'gdrive_file_map':
                backups.append((result['description'], rawGoogleDriveRequest(bearer, result['downloadUrl'])))
        except:
            pass
    if len(backups) == 0:
        quit('Unable to locate google drive file map for: '+pkg)
    return backups

def getConfigs():
    global gmail, passw, devid, pkg, sig, client_pkg, client_sig, client_ver
    config = ConfigParser()
    try:
        config.read('./cfg/settings.cfg')
        gmail = config.get('auth', 'gmail')
        passw = config.get('auth', 'passw')
        devid = config.get('auth', 'devid')
        pkg = config.get('app', 'pkg')
        sig = config.get('app', 'sig')
        client_pkg = config.get('client', 'pkg')
        client_sig = config.get('client', 'sig')
        client_ver = config.get('client', 'ver')
    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        quit('The "settings.cfg" file is missing or corrupt!')

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

def createSettingsFile():
    with open('./cfg/settings.cfg', 'w') as cfg:
        cfg.write('[report]\nlogo = ./cfg/logo.png\ncompany =\nrecord =\nunit =\nexaminer =\nnotes=\n\n[auth]\ngmail = alias@gmail.com\npassw = yourpassword\ndevid = 0000000000000000\n\n[app]\npkg = com.whatsapp\nsig = 38a0f7d505fe18fec64fbf343ecaaaf310dbd799\n\n[client]\npkg = com.google.android.gms\nsig = 38918a453d07199354f8b19af05ec6562ced5788\nver = 9877000')

def getSingleFile(data, asset):
    data = json.loads(data)
    for entries in data:
        if entries['f'] == asset:
            return entries['f'], entries['m'], entries['r'], entries['s']

def getMultipleFiles(data, folder):
    files = localFileList()
    data = json.loads(data)
    for entries in data:
        if any(entries['m'] in lists for lists in files) == False or 'database' in entries['f'].lower():
            local = folder+os.path.sep+entries['f'].replace("/", os.path.sep)
            if os.path.isfile(local) and 'database' not in local.lower():
                quit('Skipped: "'+local+'".')
            else:
                downloadFileGoogleDrive(bearer, 'https://www.googleapis.com/drive/v2/files/'+entries['r']+'?alt=media', local)
                localFileLog(entries['m'])

def runMain(mode, asset, bID):
    global bearer
    if os.path.isfile('./cfg/settings.cfg') == False:
        createSettingsFile()
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
            quit("Invalid backup ID: " + str(bID))
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
        print('python3 '+str(sys.argv[0])+' -help (this help screen)')
        print('python3 '+str(sys.argv[0])+' -vers (version information)')
        print('python3 '+str(sys.argv[0])+' -info (google drive app settings)')
        print('python3 '+str(sys.argv[0])+' -list (list all availabe files)')
        print('python3 '+str(sys.argv[0])+' -sync (sync all files locally)')
        print('python3 '+str(sys.argv[0])+' -pull "Databases/msgstore.db.crypt12" [backupID] (download)\n')
    elif str(sys.argv[1]) == '-info' or str(sys.argv[1]) == 'info':
        runMain('info', 'settings', 0)
    elif str(sys.argv[1]) == '-list' or str(sys.argv[1]) == 'list':
        runMain('list', 'all', 0)
    elif str(sys.argv[1]) == '-sync' or str(sys.argv[1]) == 'sync':
        runMain('sync', 'all', 0)
    elif str(sys.argv[1]) == '-vers' or str(sys.argv[1]) == 'vers':
        print('\nFork of WhatsAppGDExtract Version 1.1 Copyright (C) 2016 by TripCode\n')
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
    main()
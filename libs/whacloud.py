from pyicloud import PyiCloudService
from configparser import ConfigParser
from os.path import splitext
import sys
import queue as queue
import threading
import os
import argparse
import click
import time

# Define global variable
exitFlag = 0
queueLock = threading.Lock()
workQueue = queue.Queue(9999999)


def banner():
    """ Function Banner """
    print(r"""
     __      __.__           _________ .__                   .___
    /  \    /  \  |__ _____  \_   ___ \|  |   ____  __ __  __| _/
    \   \/\/   /  |  \\__  \ /    \  \/|  |  /  _ \|  |  \/ __ | 
     \        /|   Y  \/ __ \\     \___|  |_(  <_> )  |  / /_/ | 
      \__/\  / |___|  (____  /\______  /____/\____/|____/\____ | 
           \/       \/     \/        \/                       \/ 

    ------------------ Whatsapp iCloud Extractor ----------------""")


def help():
    """ Function show help """

    print("""    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t

    Usage: python3 whacloud.py -h (for help)
    """)


def create_settings_file():
    """ Function that creates the settings file """
    with open('./cfg/settings.cfg'.replace("/", os.path.sep), 'w') as cfg:
        cfg.write(
            '[report]\ncompany =\nrecord =\nunit =\nexaminer =\nnotes =\n\n[google-auth]\ngmail = alias@gmail.com\npassw = yourpassword\ncelnumbr = BackupPhoneNunmber\n\n[icloud-auth]\nicloud  = alias@icloud.com\npassw = yourpassword')


def getMultipleFiles(api, files):
    threadList = ["Thread-01", "Thread-02", "Thread-03", "Thread-04", "Thread-05", "Thread-06", "Thread-07", "Thread-08", "Thread-09", "Thread-10",
                  "Thread-11", "Thread-12", "Thread-13", "Thread-14", "Thread-15", "Thread-16", "Thread-17", "Thread-18", "Thread-19", "Thread-20",
                  "Thread-21", "Thread-22", "Thread-23", "Thread-24", "Thread-25", "Thread-26", "Thread-27", "Thread-28", "Thread-29", "Thread-30",
                  "Thread-31", "Thread-32", "Thread-33", "Thread-34", "Thread-35", "Thread-36", "Thread-37", "Thread-38", "Thread-39", "Thread-40"]
    threads = []
    threadID = 1
    print("[i] Generating threads...")
    print("[+] Backup name : {}".format(api))
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
        file = entries.filename
        local = (output + file).replace("/", os.path.sep)
        if os.path.isfile(local):
            print("    [-] Number: {}/{}  => {} Skipped".format(n, lenfiles, local))
        else:
             workQueue.put({'photo': entries, 'local': local, 'now': n, 'lenfiles': lenfiles})
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
            getMultipleFilesThread(data['photo'], data['local'], data['now'], data['lenfiles'], threadName)
            time.sleep(1)

        else:
            queueLock.release()
            time.sleep(1)


def getMultipleFilesThread(photo, local, now, lenfiles, threadName):
    os.makedirs(os.path.dirname(local), exist_ok=True)
    if not os.path.isfile(local):
        download = photo.download()
        with open(local, 'wb') as opened_file:
            opened_file.write(download.raw.read())

        print("    [-] Number: {}/{} - {} => Downloaded: {}".format(now, lenfiles, threadName, local))

    else:
        print("    [-] Number: {}/{} - {} => Skipped: {}".format(now, lenfiles, threadName, local))


def login():
    """ Get access to Icloud """

    api = PyiCloudService(icloud, passw)
    if api.requires_2sa:
        print("Two-step authentication required. Your trusted devices are:")

        devices = api.trusted_devices
        for i, device in enumerate(devices):
            print("  %s: %s" % (i, device.get('deviceName', "SMS to %s" % device.get('phoneNumber'))))

        device = click.prompt('Which device would you like to use?', default=0)
        device = devices[device]
        if not api.send_verification_code(device):
            print("Failed to send verification code")
            sys.exit(1)

        code = click.prompt('Please enter validation code')
        if not api.validate_verification_code(device, code):
            print("Failed to verify verification code")
            sys.exit(1)

    print("Devices available:\n {}".format(api.devices))
    device = click.prompt('Which device would you like to select?', default=0)
    api.devices[device]

    return api


def getConfigs():
    global icloud, passw
    config = ConfigParser(interpolation=None)
    try:
        config.read('./cfg/settings.cfg'.replace("/", os.path.sep))
        icloud = config.get('icloud-auth', 'icloud')
        passw = config.get('icloud-auth', 'passw')

    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        quit('The "./cfg/settings.cfg" file is missing or corrupt!'.replace("/", os.path.sep))


# Initializing
if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Extract your Whatsapp files from ICloud")
    user_parser = parser.add_mutually_exclusive_group()
    user_parser.add_argument("-l", "--list", help="List of all ICloud medias", action="store_true")
    user_parser.add_argument("-p", "--pull", help="Pull a file from Google Drive")
    user_parser.add_argument("-s", "--sync", help="Sync all files locally", action="store_true")
    user_parser.add_argument("-si", "--s_images", help="Sync Images files locally", action="store_true")
    user_parser.add_argument("-sv", "--s_videos", help="Sync Videos/Audios files locally", action="store_true")
    parser.add_argument("-o", "--output", help="Output path to save files")
    args = parser.parse_args()

    files = []
    if os.path.isfile('./cfg/settings.cfg'.replace("/", os.path.sep)) is False:
        create_settings_file()

    if len(sys.argv) == 0:
        help()
    else:
        getConfigs()
        api = login()
        print("[i] Searching...")
        if args.sync:
            for entries in api.photos.albums['WhatsApp']:
                files.append(entries)

            getMultipleFiles(api, files)

        elif args.list:
            for photo in api.photos.albums['WhatsApp']:
                print(photo, photo.filename)

        elif args.s_images:
            for entries in api.photos.albums['WhatsApp']:
                file_name, extension = splitext(entries.filename)
                if (extension == ".jpg") or (extension == ".png"):
                    files.append(entries)

            getMultipleFiles(api, files)

        elif args.s_videos:
            for entries in api.photos.albums['WhatsApp']:
                file_name, extension = splitext(entries.filename)
                if (extension == ".mp4") or (extension == ".3gp") or (extension == ".mp3"):
                    files.append(entries)

            getMultipleFiles(api, files)

        elif args.pull:
            if args.output:
                file = args.output + str(args.pull)
                local = file.replace("/", os.path.sep)
                os.makedirs(os.path.dirname(local), exist_ok=True)
                if not os.path.isfile(local):
                    for photo in api.photos.albums['WhatsApp']:
                        if photo.filename == args.pull:
                            download = photo.download()
                            with open(local, 'wb') as opened_file:
                                opened_file.write(download.raw.read())
                                print("    [-] Downloaded: {}".format(local))

                else:
                    print("    [-] Skipped: {}".format(local))

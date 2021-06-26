from configparser import ConfigParser
from base64 import b64decode
from getpass import getpass
from multiprocessing.pool import ThreadPool
from textwrap import dedent
import json
import os
import requests
import sys
import argparse
import gpsoauth
import hashlib


def banner():
    """ Function Banner """
    print(r"""
     __      __.__             ________      ________        .__ 
    /  \    /  \  |__ _____   /  _____/  ____\______ \_______|__|
    \   \/\/   /  |  \\__  \ /   \  ___ /  _ \|    |  \_  __ \  |
     \        /|   Y  \/ __ \\    \_\  (  <_> )    `   \  | \/  |
      \__/\  / |___|  (____  /\______  /\____/_______  /__|  |__|
           \/       \/     \/        \/              \/          

    -------------- Whatsapp Google Drive Extractor --------------""")


def help():
    """ Function show help """

    print("""    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t
    ** Fork from WhatsAppGDExtract by TripCode and forum.xda-developers.com
    ** Fork from WhatsAppGDExtract by YuriCosta
    Usage: python3 whagodri.py -h (for help)
    """)


def createSettingsFile():
    """ Function that creates the settings file """

    with open('./cfg/settings.cfg'.replace("/", os.path.sep), 'w') as cfg:
        cfg.write(dedent("""
            [report]
            company =
            record =
            unit =
            examiner =
            notes =
            
            [google-auth]
            gmail = alias@gmail.com
            # Optional. The account password or app password when using 2FA.
            password  = 
            # Optional. The result of "adb shell settings get secure android_id".
            android_id = 0000000000000000
            # Optional. Enter the backup country code + phonenumber be synchronized, otherwise it synchronizes all backups.
            # You can specify a list of celnumbr = BackupNumber1, BackupNumber2, ...
            celnumbr = 
            
            [icloud-auth] 
            icloud  = alias@icloud.com
            passw = yourpassword
            """).lstrip())


def getConfigs():
    config = ConfigParser(interpolation=None)
    try:
        config.read('./cfg/settings.cfg'.replace("/", os.path.sep))
        gmail = config.get('google-auth', 'gmail')
        password = config.get('google-auth', 'password', fallback="")
        celnumbr = config.get('google-auth', 'celnumbr').lstrip('+0')
        if not password:
            try:
                password = getpass("Enter your password for {}: ".format(gmail))
            except KeyboardInterrupt:
                quit('\nCancelled!')

        android_id = config.get("google-auth", "android_id")
        return {
            "gmail": gmail,
            "password": password,
            "android_id": android_id,
            "celnumbr": celnumbr,
        }

    except(ConfigParser.NoSectionError, ConfigParser.NoOptionError):
        quit('The "./cfg/settings.cfg" file is missing or corrupt!'.replace("/", os.path.sep))


def human_size(size):
    for s in ["B", "kB", "MB", "GB", "TB", "PB", "EB", "ZB", "YB"]:
        if abs(size) < 1024:
            break
        size = int(size / 1024)
    return "({} {})".format(size, s)


def have_file(file, size, md5):
    """
    Determine whether the named file's contents have the given size and hash.
    """

    if not os.path.exists(file) or size != os.path.getsize(file):
        return False

    digest = hashlib.md5()
    with open(file, "br") as input:
        while True:
            b = input.read(8 * 1024)
            if not b:
                break
            digest.update(b)

    return md5 == digest.digest()


def download_file(file, stream):
    """
    Download a file from the given stream.
    """

    file = output + file
    os.makedirs(os.path.dirname(file), exist_ok=True)
    with open(file, "bw") as dest:
        for chunk in stream.iter_content(chunk_size=None):
            dest.write(chunk)


def backup_info(backup):

    print("[i] Backup name     : {}".format(backup["name"]))
    print("[-] Whatsapp version: {}".format(json.loads(backup["metadata"])["versionOfAppWhenBackup"]))
    try:
        print("[-] Backup protected: {}".format(json.loads(backup["metadata"])["passwordProtectedBackupEnabled"]))
    except:
        pass

    print("[-] Backup upload   : {}".format(backup["updateTime"]))
    print("[-] Backup size     : {} Bytes {}".format(backup["sizeBytes"], human_size(int(backup["sizeBytes"]))))
    print("[+] Backup metadata")
    print("    [-] Backup Frequency         : {} ".format(json.loads(backup["metadata"])["backupFrequency"]))
    print("    [-] Backup Network Settings  : {} ".format(json.loads(backup["metadata"])["backupNetworkSettings"]))
    print("    [-] Backup Version           : {} ".format(json.loads(backup["metadata"])["backupVersion"]))
    print("    [-] Include Videos In Backup : {} ".format(json.loads(backup["metadata"])["includeVideosInBackup"]))
    print("    [-] Num Of Photos            : {}".format(json.loads(backup["metadata"])["numOfPhotos"]))
    print("    [-] Num Of Media Files       : {}".format(json.loads(backup["metadata"])["numOfMediaFiles"]))
    print("    [-] Num Of Messages          : {}".format(json.loads(backup["metadata"])["numOfMessages"]))
    print("    [-] Video Size               : {} Bytes {}".format(json.loads(backup["metadata"])["videoSize"], human_size(int(json.loads(backup["metadata"])["videoSize"]))))
    print("    [-] Backup Size              : {} Bytes {}".format(json.loads(backup["metadata"])["backupSize"], human_size(int(json.loads(backup["metadata"])["backupSize"]))))
    print("    [-] Media Size               : {} Bytes {}".format(json.loads(backup["metadata"])["mediaSize"], human_size(int(json.loads(backup["metadata"])["mediaSize"]))))
    print("    [-] Chat DB Size             : {} Bytes {}".format(json.loads(backup["metadata"])["chatdbSize"], human_size(int(json.loads(backup["metadata"])["chatdbSize"]))))


def error(token):
    print("Failed\n")
    print(token)
    failed = token.get("Error")
    if "BadAuthentication" in failed:
        print("\n   Workaround\n-----------------")
        print(
            "1. Check that your email and password are correct in the settings file.\n"
            "2. Your are using a old python version. Works >= 3.8.\n"
            "3. Update requirements, use in a terminal: 'pip3 install --upgrade -r ./doc/requirements.txt' or 'pip install --upgrade -r ./doc/requirements.txt")

    elif "NeedsBrowser" in failed:
        print("\n   Workaround\n-----------------")
        print(
            "1. Maybe you need unlock captcha in your account, If you request it, log in to your browser and then click here, https://accounts.google.com/b/0/DisplayUnlockCaptcha")
        print(
            "2. Or you have double factor authentication enabled, so disable it in this URL: https://myaccount.google.com/security")
        print("3. If you want to use 2FA, you will have to go to the URL: https://myaccount.google.com/apppasswords\n"
              "   Then select Application: Other. Write down: Whapa, and a password will be display, then you must write the password in your settings.cfg.")

    elif "DeviceManagementRequiredOrSyncDisabled" in failed:
        print("\n   Workaround\n-----------------")
        print(
            "1. You are using a GSuite account.  The reason for this is, that for this google-apps account, the enforcement of policies on mobile clients is enabled in admin console (enforce_android_policy).\n"
            "   If you disable this in admin-console, the authentication works.")

    quit()


class WaBackup:
    """
    Provide access to WhatsApp backups stored in Google drive.
    """

    def __init__(self, gmail, password, android_id, celnumbr):
        print("Requesting Auth for Google Drive....")
        token = gpsoauth.perform_master_login(gmail, password, android_id)
        if "Token" not in token:
            error(token)
        print("Granted\n")
        self.auth = gpsoauth.perform_oauth(
            gmail,
            token["Token"],
            android_id,
            "oauth2:https://www.googleapis.com/auth/drive.appdata",
            "com.whatsapp",
            "38a0f7d505fe18fec64fbf343ecaaaf310dbd799",
        )
        global Auth, phone
        Auth = self.auth
        phone = celnumbr

    def get(self, path, params=None, **kwargs):
        response = requests.get(
            "https://backup.googleapis.com/v1/{}".format(path),
            headers={"Authorization": "Bearer {}".format(self.auth["Auth"])},
            params=params,
            **kwargs,
        )
        response.raise_for_status()
        return response

    def get_page(self, path, page_token=None):
        return self.get(
            path,
            None if page_token is None else {"pageToken": page_token},
        ).json()

    def list_path(self, path):
        last_component = path.split("/")[-1]
        page_token = None
        while True:
            page = self.get_page(path, page_token)
            for item in page[last_component]:
                yield item
            if "nextPageToken" not in page:
                break
            page_token = page["nextPageToken"]

    def backups(self):
        return self.list_path("clients/wa/backups")

    def backup_files(self, backup):
        return self.list_path("{}/files".format(backup["name"]))

    def fetch(self, file):
        name = os.path.sep.join(file["name"].split("/")[3:])
        md5Hash = b64decode(file["md5Hash"], validate=True)
        if not have_file(name, int(file["sizeBytes"]), md5Hash):
            file_path = output + name
            if not os.path.isfile(file_path):
                download_file(
                    name,
                    self.get(file["name"].replace("%", "%25").replace("+", "%2B"), {"alt": "media"}, stream=True)
                )

        return name, int(file["sizeBytes"]), md5Hash

    def fetch_all(self, backup, cksums):
        num_files = 0
        total_size = 0
        with ThreadPool(10) as pool:
            downloads = pool.imap_unordered(
                lambda file: self.fetch(file),
                self.backup_files(backup)
            )
            for name, size, md5Hash in downloads:
                num_files += 1
                total_size += size
                print(
                    "\rProgress: {:7.2f}% {:60}".format(
                        100 * total_size / int(backup["sizeBytes"]),
                        os.path.basename(name)[-60:]
                    ),
                    end="",
                    flush=True,
                )

                cksums.write("{md5Hash} *{name}\n".format(
                    name=name,
                    md5Hash=md5Hash.hex(),
                ))

        print("\n{} files {}".format(num_files, human_size(total_size)))


def download_partial(filter):
    """ Sync by category """

    output = args.output
    if not output:
        output = os.getcwd()
    else:
        output = args.output

    for file in filter:
        file_short = os.path.sep.join(file.split("/")[3:])
        response = requests.get(
            "https://backup.googleapis.com/v1/{}?alt=media".format(file),
            headers={"Authorization": "Bearer {}".format(Auth["Auth"])},
            stream=True
        )
        if response.status_code == 200:
            file = output + file_short
            if not os.path.isfile(file):
                os.makedirs(os.path.dirname(file), exist_ok=True)
                with open(file, "bw") as dest:
                    for chunk in response.iter_content(chunk_size=None):
                        dest.write(chunk)
                print("    [-] Downloaded: {}".format(file))

            else:
                print("    [-] Skipped: {}".format(file))

        else:
            print("    [-] Not downloaded: {}".format(file))


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
    if not os.path.isfile('./cfg/settings.cfg'):
        createSettingsFile()

    if len(sys.argv) == 0:
        help()

    else:
        print("[i] Searching...\n")
        wa_backup = WaBackup(**getConfigs())
        backups = wa_backup.backups()

        if args.info:
            try:
                for backup in backups:
                    backup_info(backup)

            except Exception as e:
                print("[e] Error {}".format(e))

        elif args.list:
            num_files = 0
            total_size = 0
            for backup in backups:
                print("[i] Backup name: {}".format(backup["name"]))
                for file in wa_backup.backup_files(backup):
                    num_files += 1
                    total_size += int(file["sizeBytes"])
                    print("    [-] {}".format(file["name"]))

            print("[i] {} files {}".format(num_files, human_size(total_size)))

        elif args.list_whatsapp:
            num_files = 0
            total_size = 0
            for backup in backups:
                print("[i] Backup name: {}".format(backup["name"]))
                for file in wa_backup.backup_files(backup):
                    num_files += 1
                    total_size += int(file["sizeBytes"])
                    if os.path.sep.join(file["name"].split("/")[6:]) == "msgstore.db.crypt14":
                        print("    [-] {}".format(file["name"]))
                        print("    [-] Size {} {}".format(file["sizeBytes"], human_size((int(file["sizeBytes"])))))

        elif args.sync:
            output = args.output
            if not output:
                output = os.getcwd()
            else:
                output = args.output

            with open(output + "md5sum.txt", "w", encoding="utf-8", buffering=1) as cksums:
                for backup in backups:
                    number_backup = backup["name"].split("/")[3]
                    if (number_backup in phone) or (phone == ""):
                        print("[+] Backup {} {}:".format(backup["name"], human_size(int(backup["sizeBytes"])),))
                        wa_backup.fetch_all(backup, cksums)

                    else:
                        print("[i] Backup {} omitted".format(number_backup))

        elif args.s_images:
            num_files = 0
            total_size = 0
            for backup in backups:
                number_backup = backup["name"].split("/")[3]
                if (number_backup in phone) or (phone == ""):
                    filter = []
                    print("[+] Backup name: {}".format(backup["name"]))
                    for file in wa_backup.backup_files(backup):

                        i = os.path.splitext(file["name"])[1]
                        if "jpg" in i:
                            num_files += 1
                            total_size += int(file["sizeBytes"])
                            filter.append(file["name"])

                    download_partial(filter)
                else:
                    print("[i] Backup {} omitted".format(number_backup))

        elif args.s_videos:
            num_files = 0
            total_size = 0
            for backup in backups:
                number_backup = backup["name"].split("/")[3]
                if (number_backup in phone) or (phone == ""):
                    filter = []
                    print("[+] Backup name: {}".format(backup["name"]))
                    for file in wa_backup.backup_files(backup):

                        i = os.path.splitext(file["name"])[1]
                        if "mp4" in i:
                            num_files += 1
                            total_size += int(file["sizeBytes"])
                            filter.append(file["name"])

                    download_partial(filter)
                else:
                    print("[i] Backup {} omitted".format(number_backup))

        elif args.s_audios:
            num_files = 0
            total_size = 0
            for backup in backups:
                number_backup = backup["name"].split("/")[3]
                if (number_backup in phone) or (phone == ""):
                    filter = []
                    print("[+] Backup name: {}".format(backup["name"]))
                    for file in wa_backup.backup_files(backup):
                        i = os.path.splitext(file["name"])[1]
                        if ("mp3" in i) or ("opus" in i):
                            num_files += 1
                            total_size += int(file["sizeBytes"])
                            print("    [-] {}".format(file["name"]))
                            filter.append(file["name"])

                    download_partial(filter)
                else:
                    print("[i] Backup {} omitted".format(number_backup))

        elif args.s_documents:
            num_files = 0
            total_size = 0
            for backup in backups:
                number_backup = backup["name"].split("/")[3]
                if (number_backup in phone) or (phone == ""):
                    filter = []
                    print("[i] Backup name: {}".format(backup["name"]))
                    for file in wa_backup.backup_files(backup):
                        if file["name"].split("/")[6] == "WhatsApp Documents":
                            num_files += 1
                            total_size += int(file["sizeBytes"])
                            print("    [-] {}".format(file["name"]))
                            filter.append(file["name"])

                    download_partial(filter)
                else:
                    print("[i] Backup {} omitted".format(number_backup))

        elif args.s_databases:
            num_files = 0
            total_size = 0
            for backup in backups:
                number_backup = backup["name"].split("/")[3]
                if (number_backup in phone) or (phone == ""):
                    filter = []
                    print("[+] Backup name: {}".format(backup["name"]))
                    for file in wa_backup.backup_files(backup):
                        i = os.path.splitext(file["name"])[1]
                        if "crypt14" in i:
                            num_files += 1
                            total_size += int(file["sizeBytes"])
                            print("    [-] {}".format(file["name"]))
                            filter.append(file["name"])

                    download_partial(filter)
                else:
                    print("[i] Backup {} omitted".format(number_backup))

        elif args.pull:
            file = args.pull
            output = args.output
            print("[+] Backup name: {}".format(os.path.sep.join(file.split("/")[:4])))
            download_partial([file])

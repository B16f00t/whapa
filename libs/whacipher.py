#!/usr/bin/python
# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
import argparse
import zlib
import sys
import os


# Define global variable
output = ""


def banner():
    """ Function Banner """

    print(r"""
     __      __.__                  .__       .__                  
    /  \    /  \  |__ _____    ____ |__|_____ |  |__   ___________ 
    \   \/\/   /  |  \\__  \ _/ ___\|  \____ \|  |  \_/ __ \_  __ \
     \        /|   Y  \/ __ \\  \___|  |  |_> >   Y  \  ___/|  | \/
      \__/\  / |___|  (____  /\___  >__|   __/|___|  /\___  >__|   
           \/       \/     \/     \/   |__|        \/     \/               
    --------------- Whatsapp Encryption and Decryption -----------------
    """)


def help():
    """ Function show help """

    print("""
    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t

    Usage: python3 whacipher.py -h (for help)
    """)


def encrypt12(db_file, key_file, db_cript, output):
    """ Function encrypt msgstore Database """
    try:
        with open(key_file, "rb") as fh:
            key_data = fh.read()

        key = key_data[126:]
        with open(db_cript, "rb") as fh:
            db_cript_data = fh.read()

        header = db_cript_data[:51]
        iv = db_cript_data[51:67]
        footer = db_cript_data[-20:]
        with open(db_file, "rb") as fh:
            data = fh.read()

        aes = AES.new(key, mode=AES.MODE_GCM, nonce=iv)
        with open(output, "wb") as fh:
            fh.write(header + iv + aes.encrypt(zlib.compress(data)) + footer)

        print("[-] " + db_file + " encrypted, '" + output + "' created")

    except Exception as e:
        print("[e] An error has ocurred encrypting '" + db_file + "' - ", e)


def decrypt14(db_file, key_file, path, offset):
    """ Function decrypt Crypt14 Database """
    try:
        print("Trying offset {}".format(offset))
        if os.path.getsize(key_file) != 158:
            quit('[e] The specified input key file is invalid.')

        with open(key_file, "rb") as fh:
            key_data = fh.read()

        key = key_data[126:]
        with open(db_file, "rb") as fh:
            db_data = fh.read()

        data = db_data[offset:]  #191
        iv = db_data[67:83]
        aes = AES.new(key, mode=AES.MODE_GCM, nonce=iv)
        with open(path, "wb") as fh:
            fh.write(zlib.decompress(aes.decrypt(data)))
        print("[-] " + db_file + " decrypted, '" + path + "' created")
        return True

    except Exception as e:
        print("[e] An error has ocurred decrypting '" + db_file + "' - ", e)
        return False


def decrypt12(db_file, key_file, path):
    """ Function decrypt Crypt12 Database """
    try:
        if os.path.getsize(key_file) != 158:
            quit('[e] The specified input key file is invalid.')

        with open(key_file, "rb") as fh:
            key_data = fh.read()

        key = key_data[126:]
        with open(db_file, "rb") as fh:
            db_data = fh.read()

        data = db_data[67:-20]
        iv = db_data[51:67]
        aes = AES.new(key, mode=AES.MODE_GCM, nonce=iv)
        with open(path, "wb") as fh:
            fh.write(zlib.decompress(aes.decrypt(data)))
        print("[-] " + db_file + " decrypted, '" + path + "' created")

    except Exception as e:
        print("[e] An error has ocurred decrypting '" + db_file + "' - ", e)


if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Choose a file or path to decrypt or encrypt")
    mode_parser = parser.add_mutually_exclusive_group()
    mode_parser.add_argument("-f", "--file", help="Database file to encrypt o decrypt", nargs='?')
    mode_parser.add_argument("-p", "--path", help="Database path to decrypt", nargs='?')
    parser.add_argument("-d", "--decrypt", help="Whatsapp Key path (Decrypt database)")
    parser.add_argument("-e", "--encrypt", help="'Whatsapp Key path' + 'msgstore.db.crypt14' (Encrypt database)", nargs=2)
    parser.add_argument("-o", "--output", help="Database output file or path")
    args = parser.parse_args()

    if len(sys.argv) == 1:
        help()

    elif args.file:
        if args.encrypt:
            if os.path.exists(args.file):
                if os.path.exists(args.encrypt[0]) and os.path.exists(args.encrypt[1]):
                    print("[i] Starting to encrypt in Crypt12...")
                    encrypt12(args.file, args.encrypt[0], args.encrypt[1], args.output)
                else:
                    print("[e] '" + args.encrypt[0] + "' or '" + args.encrypt[1] + "' doesn't exist")
            else:
                print("[e] " + args.file + " doesn't exist")

        elif args.decrypt:
            if os.path.exists(args.file):
                if os.path.exists(args.decrypt):
                    print("[i] Starting to decrypt...")
                    if ".crypt12" == os.path.splitext(args.file)[1]:
                        decrypt12(args.file, args.decrypt, args.output)

                    elif ".crypt14" == os.path.splitext(args.file)[1]:
                        for offset in range(185, 195):
                            if decrypt14(args.file, args.decrypt, args.output, offset):
                                break
                else:
                    print("[e] " + args.decrypt + " doesn't exist")
            else:
                print("[e] " + args.file + " doesn't exist")

    elif args.path:
        if args.decrypt:
            if os.path.exists(args.path):
                if os.path.exists(args.decrypt):
                    print("[i] Starting to decrypt...")
                    dir, subdirs, files = next(os.walk(args.path))
                    for crypt_file in files:
                        if ".crypt14" == os.path.splitext(crypt_file)[1]:
                            output = args.output + os.path.splitext(crypt_file)[0]
                            for offset in range(185, 195):
                                if decrypt14(dir + crypt_file, args.decrypt, output, offset):
                                    break

                        elif ".crypt12" == os.path.splitext(crypt_file)[1]:
                                output = args.output + os.path.splitext(crypt_file)[0]
                                decrypt12(dir + crypt_file, args.decrypt, output)
                    print("[i] Decryption completed")

                else:
                    print("[e] " + args.decrypt + " doesn't exist")

            else:
                print("[e] " + args.file + " doesn't exist")

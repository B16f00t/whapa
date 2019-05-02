#!/usr/bin/python
# -*- coding: utf-8 -*-

from Crypto.Cipher import AES
import argparse
import zlib
import sys
import shutil
import os
import re


# Define global variable
version = "0.1"

def banner():
    """ Function Banner """

    print """
     __      __        _________ .__       .__                  
    /  \    /  \_____  \_   ___ \|__|_____ |  |__   ___________ 
    \   \/\/   /\__  \ /    \  \/|  \____ \|  |  \_/ __ \_  __ \\
     \        /  / __ \\\\     \___|  |  |_> >   Y  \  ___/|  | \/
      \__/\  /  (____  /\______  /__|   __/|___|  /\___  >__|   
           \/        \/        \/   |__|        \/     \/             
    ---------- Whatsapp Encryption and Decryption v""" + version + """ ----------
    """


def help():
    """ Function show help """

    print"""
    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t

    Usage: python wacipher.py -h (for help)
    """


def encrypt(db_file, key_file, db_cript):
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

        file_encripted = db_file + '.crypt12'
        aes = AES.new(key, mode=AES.MODE_GCM, nonce=iv)
        with open(file_encripted, "wb") as fh:
            fh.write(header + iv + aes.encrypt(zlib.compress(data)) + footer)

        print "[-] " + db_file + " encrypted, '" + file_encripted + "' created"
    except Exception as e:
        print "[e] An error has ocurred encrypting '" + db_file + "' - ", e


def decrypt(db_file, key_file):
    """ Function decrypt Crypt12 Database """
    try:
        with open(key_file, "rb") as fh:
            key_data = fh.read()
        key = key_data[126:]

        with open(db_file, "rb") as fh:
            db_data = fh.read()

        iv = db_data[51:67]
        data = db_data[67:-20]
        aes = AES.new(key, mode=AES.MODE_GCM, nonce=iv)

        with open(os.path.splitext(db_file)[0], "wb") as fh:
            fh.write(zlib.decompress(aes.decrypt(data)))

        print "[-] " + db_file + " decrypted, '" + os.path.splitext(db_file)[0] + "' created"

    except Exception as e:
        print "[e] An error has ocurred decrypting '" + db_file + "' - ", e


if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Choose a file or path to decrypt or encrypt")
    mode_parser = parser.add_mutually_exclusive_group()
    mode_parser.add_argument("-f", "--file", help="Database file to encrypt o decrypt", nargs='?')
    mode_parser.add_argument("-p", "--path", help="Database path to decrypt", nargs='?')
    parser.add_argument("-d", "--decrypt", help="Whatsapp Key path (Decrypt database)")
    parser.add_argument("-e", "--encrypt", help="'Whatsapp Key path' + 'msgstore.db.crypt12' (Encrypt database)", nargs=2)
    args = parser.parse_args()

    if len(sys.argv) == 1:
        help()

    elif args.file:
        if args.encrypt:
            if os.path.exists(args.file):
                if os.path.exists(args.encrypt[0]) and os.path.exists(args.encrypt[1]):
                    print "[i] Starting to decrypt..."
                    encrypt(args.file, args.encrypt[0], args.encrypt[1])
                else:
                    print "[e] '" + args.encrypt[0] + "' or '" + args.encrypt[1] + "' don't exist"

            else:
                print "[e] " + args.file + " doesn't exist"

        elif args.decrypt:
            if os.path.exists(args.file):
                if os.path.exists(args.decrypt):
                    print "[i] Starting to decrypt..."
                    decrypt(args.file, args.decrypt)

                else:
                    print "[e] " + args.decrypt + " doesn't exist"

            else:
                print "[e] " + args.file + " doesn't exist"

    elif args.path:
        if args.decrypt:
            if os.path.exists(args.path):
                if os.path.exists(args.decrypt):
                    print "[i] Starting to decrypt..."

                    for crypt_file in sorted(os.listdir(args.path), reverse=True):
                        if ".crypt12" == os.path.splitext(crypt_file)[1]:
                            crypt_file = args.path + crypt_file
                            decrypt(crypt_file, args.decrypt)
                    print "[i] Decryption completed"

                else:
                    print "[e] " + args.decrypt + " doesn't exist"

            else:
                print "[e] " + args.file + " doesn't exist"


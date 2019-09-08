#!/usr/bin/python3
# -*- coding: utf-8 -*-

import argparse
import shutil
import sqlite3
import os
import sys


# Define global variable

version = "1.0"
message_columns = [
    '_id', 'key_remote_jid','key_from_me','key_id','status','needs_push','data','timestamp','media_url','media_mime_type',
    'media_wa_type','media_size','media_name','media_caption','media_hash','media_duration','origin','latitude',
    'longitude','thumb_image','remote_resource','received_timestamp','send_timestamp','receipt_server_timestamp',
    'receipt_device_timestamp','read_device_timestamp','played_device_timestamp','raw_data','recipient_count',
    'participant_hash','starred','quoted_row_id','mentioned_jids','multicast_id','edit_version','media_enc_hash',
    'payment_transaction_id','forwarded'
    ]
chatlist_columns = [
    '_id','key_remote_jid','message_table_id','subject','creation','last_read_message_table_id','last_read_receipt_sent_message_table_id',
    'archived','sort_timestamp','mod_tag','gen','my_messages','plaintext_disabled','last_message_table_id','unseen_message_count',
    'unseen_missed_calls_count','unseen_row_count','vcard_ui_dismissed','deleted_message_id','deleted_starred_message_id',
    'deleted_message_categories','change_number_notified_message_id','last_important_message_table_id','show_group_description'
    ]
quote_columns = [
    '_id', 'key_remote_jid','key_from_me','key_id','status','needs_push','data','timestamp','media_url','media_mime_type',
    'media_wa_type','media_size','media_name','media_caption','media_hash','media_duration','origin','latitude',
    'longitude','thumb_image','remote_resource','received_timestamp','send_timestamp','receipt_server_timestamp',
    'receipt_device_timestamp','read_device_timestamp','played_device_timestamp','raw_data','recipient_count',
    'participant_hash','starred','quoted_row_id','mentioned_jids','multicast_id','edit_version','media_enc_hash',
    'payment_transaction_id','forwarded'
    ]
thumbnail_columns = [
    'rowid','thumbnail','timestamp','key_remote_jid','key_from_me','key_id'
    ]


def banner():
    """ Function Banner """

    print("""
     __      __.__                                               
    /  \    /  \  |__ _____    _____   ___________  ____   ____  
    \   \/\/   /  |  \\\\__  \  /     \_/ __ \_  __ \/ ___\_/ __ \ 
     \        /|   Y  \/ __ \|  Y Y  \  ___/|  | \/ /_/  >  ___/ 
      \__/\  / |___|  (____  /__|_|  /\___  >__|  \___  / \___  >
           \/       \/     \/      \/     \/     /_____/      \/ 
    ------------------- Whatsapp Merger v""" + version + """ -----------------
    """)

def help():
    """ Function show help """

    print("""
    ** Author: Ivan Moreno a.k.a B16f00t
    ** Github: https://github.com/B16f00t
    
    Usage: python whamerge.py -h (for help)
    """)


def merge(db_path, db_name):
    """ Function merges database """

    if os.path.isdir(db_path):
        # catch all databases and sort
        list_dbs = []

        for db_file in os.listdir(args.path):
            if ".db" == os.path.splitext(db_file)[1]:
                list_dbs.append(db_file)

        list_dbs = sorted(list_dbs, reverse=True)
        if len(list_dbs) < 2:
            print("[e] No databases to merge")
            exit()

        if not list_dbs:
            print("[e] Database not found in the path")
            exit()
        print("[i] {} database found - make sure they are all msgstore databases".format(len(list_dbs)))
        # Copy first 'db' in db_name and open write connection
        if list_dbs[0] != db_name:
            try:
                print("\n[i] Copying " + list_dbs[0] + " to " + db_name)
                shutil.copy(db_path + list_dbs[0], db_name)
                print("   [+] Created " + db_name)

            except Exception as e:
                print("[e] Error copying: ", e)

        num_message_cols = len(message_columns)
        str_message_cols = ",".join(message_columns[:num_message_cols])
        total_message = 0

        num_chatlist_cols = len(chatlist_columns)
        str_chatlist_cols = ",".join(chatlist_columns[:num_chatlist_cols])
        total_chatlist = 0

        num_quote_cols = len(quote_columns)
        str_quote_cols = ",".join(quote_columns[:num_quote_cols])
        total_quote = 0

        num_thumb_cols = len(thumbnail_columns)
        str_thumb_cols = ",".join(thumbnail_columns[:num_thumb_cols])
        total_thumb = 0

        # Scrolls through each file to merge, skipping the first and last
        for filename in list_dbs:
            if (filename != list_dbs[0]) and (filename != db_name):
                print("[+] Merging: " + filename)

                # Open write connection
                with sqlite3.connect(db_name) as output:
                    cursor_write = output.cursor()
                    
                cursor_write.execute("SELECT _id FROM messages;")
                ids_message_write = cursor_write.fetchall()
                
                cursor_write.execute("SELECT _id FROM chat_list;")
                ids_chatlist_write = cursor_write.fetchall()

                cursor_write.execute("SELECT _id FROM messages_quotes;")
                ids_quote_write = cursor_write.fetchall()

                cursor_write.execute("SELECT rowid FROM message_thumbnails;")
                ids_thumb_write = cursor_write.fetchall()

                print("   [-] " + db_name + " --> " + str(len(ids_message_write)) + " messages, " + str(len(ids_chatlist_write)) + " chats, " + str(len(ids_quote_write)) + " replies, " + str(len(ids_thumb_write)) + " thumbnails")
                # Open read connection
                with sqlite3.connect(db_path + filename) as orig:
                    cursor_read = orig.cursor()
                    
                cursor_read.execute("SELECT _id FROM messages;")
                ids_message_read = cursor_read.fetchall()
                
                cursor_read.execute("SELECT _id FROM chat_list;")
                ids_chatlist_read = cursor_read.fetchall()

                cursor_read.execute("SELECT _id FROM messages_quotes;")
                ids_quote_read = cursor_read.fetchall()

                cursor_read.execute("SELECT rowid FROM message_thumbnails;")
                ids_thumb_read = cursor_read.fetchall()
                print("   [-] " + filename + " --> " + str(len(ids_message_read)) + " messages, " + str(len(ids_chatlist_read)) + " chats, " + str(len(ids_quote_read)) + " replies, " + str(len(ids_thumb_read)) + " thumbnails")

                # Searches for messages, chatlist that are not there and inserts them into a list
                print("[+] Looking for new messages")
                ids_message_insert = []
                for item in ids_message_read:
                    if item not in ids_message_write:
                        ids_message_insert.append(str(item[0]))
                print("   [-] New messages", len(ids_message_insert))

                print("[+] Looking for new chats")
                ids_chatlist_insert = []
                for item in ids_chatlist_read:
                    if item not in ids_chatlist_write:
                        ids_chatlist_insert.append(str(item[0]))
                print("   [-] New chats", len(ids_chatlist_insert))

                print("[+] Looking for new replies")
                ids_quote_insert = []
                for item in ids_quote_read:
                    if item not in ids_quote_write:
                        ids_quote_insert.append(str(item[0]))
                print("   [-] New replies", len(ids_quote_insert))

                print("[+] Looking for new Thumbnails")
                ids_thumb_insert = []
                for item in ids_thumb_read:
                    if item not in ids_thumb_write:
                        ids_thumb_insert.append(str(item[0]))
                print("   [-] New Thumbnails", len(ids_thumb_insert))

                num_ids_message_cols = len(ids_message_insert)
                str_id_message_cols = ",".join(ids_message_insert[:num_ids_message_cols])
                elements_message_cursor = cursor_read.execute("SELECT " + str_message_cols + " FROM messages WHERE _id IN (" + str_id_message_cols + ");")
                elements_message_insert = elements_message_cursor.fetchall()

                num_ids_chatlist_cols = len(ids_chatlist_insert)
                str_id_chatlist_cols = ",".join(ids_chatlist_insert[:num_ids_chatlist_cols])
                elements_chatlist_cursor = cursor_read.execute("SELECT " + str_chatlist_cols + " FROM chat_list WHERE _id IN (" + str_id_chatlist_cols + ");")
                elements_chatlist_insert = elements_chatlist_cursor.fetchall()

                num_ids_quote_cols = len(ids_quote_insert)
                str_id_quote_cols = ",".join(ids_quote_insert[:num_ids_quote_cols])
                elements_quote_cursor = cursor_read.execute("SELECT " + str_quote_cols + " FROM messages_quotes WHERE _id IN (" + str_id_quote_cols + ");")
                elements_quote_insert = elements_quote_cursor.fetchall()

                num_ids_thumb_cols = len(ids_thumb_insert)
                str_id_thumb_cols = ",".join(ids_thumb_insert[:num_ids_thumb_cols])
                elements_thumb_cursor = cursor_read.execute("SELECT " + str_thumb_cols + " FROM message_thumbnails WHERE rowid IN (" + str_id_thumb_cols + ");")
                elements_thumb_insert = elements_thumb_cursor.fetchall()

                # Insert the elements into the database
                try:
                    for msg in elements_message_insert:
                        insert_query = "INSERT INTO messages(" + str_message_cols + ") VALUES (" + ','.join('?' for x in range(0, len(message_columns))) + ")"
                        cursor_write.execute(insert_query, msg)
                        output.commit()

                    for msg in elements_chatlist_insert:
                        insert_query = "INSERT INTO chat_list(" + str_chatlist_cols + ") VALUES (" + ','.join('?' for x in range(0, len(chatlist_columns))) + ")"
                        cursor_write.execute(insert_query, msg)
                        output.commit()

                    for msg in elements_quote_insert:
                        insert_query = "INSERT INTO messages_quotes(" + str_quote_cols + ") VALUES (" + ','.join('?' for x in range(0, len(quote_columns))) + ")"
                        cursor_write.execute(insert_query, msg)
                        output.commit()

                    for msg in elements_thumb_insert:
                        insert_query = "INSERT INTO message_thumbnails(" + str_thumb_cols + ") VALUES (" + ','.join('?' for x in range(0, len(thumbnail_columns))) + ")"
                        cursor_write.execute(insert_query, msg)
                        output.commit()

                except sqlite3.IntegrityError as e:
                    print("   [e] Error inserting elements: ", e)

                print("   [i] " + str(len(ids_message_insert)) + " new messages, " + str(len(ids_chatlist_insert)) + " new chats, " + str(len(ids_quote_insert)) + " new replies, " + str(len(ids_thumb_insert)) + " new thumbnails")

                total_message += len(ids_message_insert)
                total_chatlist += len(ids_chatlist_insert)
                total_quote += len(ids_quote_insert)
                total_thumb += len(ids_thumb_insert)

        print("\n[i] Added " + str(total_message) + " new messages, " + str(total_chatlist) + " new chats, " + str(total_quote) + " new replies, " + str(total_thumb) + " new thumbnails to " + db_name)


def merge_win(db_path, db_name):
    """ Function merges database """
    if os.path.isdir(db_path):
        # catch all databases and sort
        list_dbs = []

        for db_file in os.listdir(args.path):
            if ".db" == os.path.splitext(db_file)[1]:
                list_dbs.append(db_file)

        list_dbs = sorted(list_dbs, reverse=True)
        if len(list_dbs) < 2:
            print("[e] No databases to merge")
            exit()

        if not list_dbs:
            print("[e] Database not found in the path")
            exit()
        print("[i] {} database found - make sure they are all msgstore databases".format(len(list_dbs)))
        # Copy first 'db' in db_name and open write connection

        if list_dbs[0] != db_name:
            try:
                print("\n[i] Copying " + list_dbs[0] + " to " + db_name)
                shutil.copy(db_path + list_dbs[0], db_name)
                print("   [+] Created " + db_name)
            except Exception as e:
                print("[e] Error copying: ", e)

        num_message_cols = len(message_columns)
        str_message_cols = ",".join(message_columns[:num_message_cols])
        total_message = 0

        num_chatlist_cols = len(chatlist_columns)
        str_chatlist_cols = ",".join(chatlist_columns[:num_chatlist_cols])
        total_chatlist = 0

        num_quote_cols = len(quote_columns)
        str_quote_cols = ",".join(quote_columns[:num_quote_cols])
        total_quote = 0

        num_thumb_cols = len(thumbnail_columns)
        str_thumb_cols = ",".join(thumbnail_columns[:num_thumb_cols])
        total_thumb = 0

        # Scrolls through each file to merge, skipping the first and last
        for filename in list_dbs:
            if (filename != list_dbs[0]) and (filename != db_name):
                print("[+] Merging: " + filename)

                # Open write connection
                with sqlite3.connect(db_name) as output:
                    cursor_write = output.cursor()

                cursor_write.execute("SELECT _id FROM messages;")
                ids_message_write = cursor_write.fetchall()

                cursor_write.execute("SELECT _id FROM chat_list;")
                ids_chatlist_write = cursor_write.fetchall()

                cursor_write.execute("SELECT _id FROM messages_quotes;")
                ids_quote_write = cursor_write.fetchall()

                cursor_write.execute("SELECT rowid FROM message_thumbnails;")
                ids_thumb_write = cursor_write.fetchall()

                print("   [-] " + db_name + " --> " + str(len(ids_message_write)) + " messages, " + str(
                    len(ids_chatlist_write)) + " chats, " + str(len(ids_quote_write)) + " replies, " + str(
                    len(ids_thumb_write)) + " thumbnails")
                # Open read connection
                with sqlite3.connect(db_path + filename) as orig:
                    cursor_read = orig.cursor()

                cursor_read.execute("SELECT _id FROM messages;")
                ids_message_read = cursor_read.fetchall()

                cursor_read.execute("SELECT _id FROM chat_list;")
                ids_chatlist_read = cursor_read.fetchall()

                cursor_read.execute("SELECT _id FROM messages_quotes;")
                ids_quote_read = cursor_read.fetchall()

                cursor_read.execute("SELECT rowid FROM message_thumbnails;")
                ids_thumb_read = cursor_read.fetchall()
                print("   [-] " + filename + " --> " + str(len(ids_message_read)) + " messages, " + str(
                    len(ids_chatlist_read)) + " chats, " + str(len(ids_quote_read)) + " replies, " + str(
                    len(ids_thumb_read)) + " thumbnails")

                # Searches for messages, chatlist that are not there and inserts them into a list
                print("[+] Looking for new messages")
                ids_message_insert = []
                for item in ids_message_read:
                    if item not in ids_message_write:
                        ids_message_insert.append(str(item[0]))
                print("   [-] New messages", len(ids_message_insert))

                print("[+] Looking for new chats")
                ids_chatlist_insert = []
                for item in ids_chatlist_read:
                    if item not in ids_chatlist_write:
                        ids_chatlist_insert.append(str(item[0]))
                print("   [-] New chats", len(ids_chatlist_insert))

                print("[+] Looking for new replies")
                ids_quote_insert = []
                for item in ids_quote_read:
                    if item not in ids_quote_write:
                        ids_quote_insert.append(str(item[0]))
                print("   [-] New replies", len(ids_quote_insert))

                print("[+] Looking for new Thumbnails")
                ids_thumb_insert = []
                for item in ids_thumb_read:
                    if item not in ids_thumb_write:
                        ids_thumb_insert.append(str(item[0]))
                print("   [-] New Thumbnails", len(ids_thumb_insert))

                num_ids_message_cols = len(ids_message_insert)
                str_id_message_cols = ",".join(ids_message_insert[:num_ids_message_cols])
                elements_message_cursor = cursor_read.execute(
                    "SELECT " + str_message_cols + " FROM messages WHERE _id IN (" + str_id_message_cols + ");")
                elements_message_insert = elements_message_cursor.fetchall()

                num_ids_chatlist_cols = len(ids_chatlist_insert)
                str_id_chatlist_cols = ",".join(ids_chatlist_insert[:num_ids_chatlist_cols])
                elements_chatlist_cursor = cursor_read.execute(
                    "SELECT " + str_chatlist_cols + " FROM chat_list WHERE _id IN (" + str_id_chatlist_cols + ");")
                elements_chatlist_insert = elements_chatlist_cursor.fetchall()

                num_ids_quote_cols = len(ids_quote_insert)
                str_id_quote_cols = ",".join(ids_quote_insert[:num_ids_quote_cols])
                elements_quote_cursor = cursor_read.execute(
                    "SELECT " + str_quote_cols + " FROM messages_quotes WHERE _id IN (" + str_id_quote_cols + ");")
                elements_quote_insert = elements_quote_cursor.fetchall()

                num_ids_thumb_cols = len(ids_thumb_insert)
                str_id_thumb_cols = ",".join(ids_thumb_insert[:num_ids_thumb_cols])
                elements_thumb_cursor = cursor_read.execute(
                    "SELECT " + str_thumb_cols + " FROM message_thumbnails WHERE rowid IN (" + str_id_thumb_cols + ");")
                elements_thumb_insert = elements_thumb_cursor.fetchall()

                # Insert the elements into the database
                try:
                    for msg in elements_message_insert:
                        insert_query = "INSERT INTO messages(" + str_message_cols + ") VALUES (" + ','.join(
                            '?' for x in range(0, len(message_columns))) + ")"
                        cursor_write.execute(insert_query, msg)
                        output.commit()

                    for msg in elements_chatlist_insert:
                        insert_query = "INSERT INTO chat_list(" + str_chatlist_cols + ") VALUES (" + ','.join(
                            '?' for x in range(0, len(chatlist_columns))) + ")"
                        cursor_write.execute(insert_query, msg)
                        output.commit()

                    for msg in elements_quote_insert:
                        insert_query = "INSERT INTO messages_quotes(" + str_quote_cols + ") VALUES (" + ','.join(
                            '?' for x in range(0, len(quote_columns))) + ")"
                        cursor_write.execute(insert_query, msg)
                        output.commit()

                    for msg in elements_thumb_insert:
                        insert_query = "INSERT INTO message_thumbnails(" + str_thumb_cols + ") VALUES (" + ','.join(
                            '?' for x in range(0, len(thumbnail_columns))) + ")"
                        cursor_write.execute(insert_query, msg)
                        output.commit()

                except sqlite3.IntegrityError as e:
                    print("   [e] Error inserting elements: ", e)

                print("   [i] " + str(len(ids_message_insert)) + " new messages, " + str(
                    len(ids_chatlist_insert)) + " new chats, " + str(len(ids_quote_insert)) + " new replies, " + str(
                    len(ids_thumb_insert)) + " new thumbnails")

                total_message += len(ids_message_insert)
                total_chatlist += len(ids_chatlist_insert)
                total_quote += len(ids_quote_insert)
                total_thumb += len(ids_thumb_insert)

        print("\n[i] Added " + str(total_message) + " new messages, " + str(total_chatlist) + " new chats, " + str(
            total_quote) + " new replies, " + str(total_thumb) + " new thumbnails to " + db_name)


# Initializing
if __name__ == "__main__":
    banner()
    parser = argparse.ArgumentParser(description="Choose a database files path to merge")
    parser.add_argument("path", help="Database path", metavar="PATH", nargs='?', default=".")
    parser.add_argument("-o", "--output", help="Database output file 'msgstore_merge.db'")
    args = parser.parse_args()
    if len(sys.argv) == 1:
        help()
    else:
        if args.output:
            merge(args.path, args.output)

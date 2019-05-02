![alt tag](https://github.com/B16f00t/whapa/blob/master/doc/whapa.png)


Whatsapp Parser Toolset
====
Updated: May 2019

WhatsApp Messenger Version 2.19.115

Whapa is a toolset to analyze whatsapp app for android. All tools are written in Python 2.X.
Whapa toolset is divided in three tools:
* **Whapa**     (Whatsapp Parser)
* **Whamerge**  (Whatsapp Merger)
* **Whagodri**  (Whataspp Google Drive Extractor)
* **Whacipher** (Whatsapp Encryption/Decryption)


Changelog
====
https://github.com/B16f00t/whapa/blob/master/doc/CHANGELOG.md	

Installation
====
You can download the latest version of whapa by cloning the GitHub repository:

	git clone https://github.com/B16f00t/whapa.git
then:

	pip install -r ./doc/requirements.txt

WHAPA
====
whapa.py is an android whatsapp database parser which automates the process and presents the data handled by the Sqlite database in a way that is comprehensible to the analyst.
The software is divided into three modes:
* **Message Mode**   : Analyzes all messages in the database, applying different filters. It extracts thumbnails when they're availables.
		       "./Media" is the directory where thumbnails are being written. The rows are sorted by timestamp not by id.
* **Decryption Mode**: Decryptes the crypto12 databases as long as it has the key.
* **Extract Mode**   : Extracts all thumbnails from the database

If you copy the "wa.db" database into the same directory as the script, the phone number will be displayed along with the name.

Please note that this project is an early stage. As such, you could find errors. Use it at your own risk!

Usage
=====
	     __      __.__          __________         
	    /  \    /  \  |__ _____ \______   \_____   
	    \   \/\/   /  |  \\__  \ |     ___/\__  \  
	     \        /|   Y  \/ __ \|    |     / __ \_
	      \__/\  / |___|  (____  /____|    (____  /
	           \/       \/     \/               \/ 
	    ---------- Whatsapp Parser v0.5 -----------
    	
	usage: whapa.py [-h] [-i | -m | -e] [--update]
        [-u USER | -ua USER_ALL | -g GROUP | -a] [-t TEXT] [-w] [-s]
        [-b] [-ts TIME_START] [-te TIME_END] [-r [{EN,ES}]]
        [-tt | -ti | -ta | -tv | -tc | -tl | -tx | -tp | -tg | -td | -tr]
        [DATABASE]

	To start choose a database and a mode with options
	
	positional arguments:
  	  DATABASE              Database file path - './msgstore.db' by default

	optional arguments:
  	  -h, --help            show this help message and exit
  	  -i, --info            *** Info Mode ***
  	  -m, --messages        *** Message Mode ***
	  -e, --extract         *** Extract Mode ***
  	  --update              Update Whatsapp Parser Tool
  	  -u USER, --user USER  Show chat with a phone number, ej. 34123456789
  	  -ua USER_ALL, --user_all USER_ALL
         	                Show messages made by a phone number
  	  -g GROUP, --group GROUP
          	                Show chat with a group number, ej. 34123456-14508@g.us
  	  -a, --all             Show all chat messages classified by phone number,
           	                group number and broadcast list
  	  -t TEXT, --text TEXT  Show messages by text match
  	  -w, --web             Show messages made by Whatsapp Web
  	  -s, --starred         Show messages starred by owner
  	  -b, --broadcast       Show messages send by broadcast
  	  -ts TIME_START, --time_start TIME_START
          	                Show messages by start time (dd-mm-yyyy HH:MM)
  	  -te TIME_END, --time_end TIME_END
          			Show messages by end time (dd-mm-yyyy HH:MM)
  	  -r [{EN,ES}], --report [{EN,ES}]
          			Make an html report in 'EN' English or 'ES' Spanish.
                	        If specified together with flag -a, makes a report for
                        	each chat
  	  -tt, --type_text      Show text messages
  	  -ti, --type_image     Show image messages
  	  -ta, --type_audio     Show audio messages
  	  -tv, --type_video     Show video messages
  	  -tc, --type_contact   Show contact messages
  	  -tl, --type_location  Show location messages
  	  -tx, --type_call      Show audio/video call messages
  	  -tp, --type_application
          	                Show application messages
  	  -tg, --type_gif       Show GIF messages
  	  -td, --type_deleted   Show deleted object messages
  	  -tr, --type_share     Show Real time location messages
  
Examples
=====

* Message mode:
	Show all messages from the database
		python whapa.py -m 

	Show all messages from 12-12-2017 12:00 to 13-12-2017 12:00
		python whapa.py -m -tS "12-12-2017 12:00" -tE "13-12-2017 12:00"

	Show all images send by Whatsapp Web
		python whapa.py -m -w -tI

	Show all messages send by that group
		python whapa.py -m -g 34XXXXXXXXX-1345475288@g.us	

	Show all chats of the phone and makes English reports (recommended)
		python whapa.py -m -a -r EN


* Info mode:

	Show a stage with options about groups, broadcast lists and statuses.
		python whapa.py -i

* Extract mode:

	Extract all thumbnails from '01-01-2018 00:00' so far. 
		python whapa.py -e -ts "01-01-2018 00:00"


Reports
=====
To create reports the first thing we need to do is to configure the file"./cfg/settings.cfg". For example:

	[report]
	logo =./cfg/logo.png
	company = Foo S.L
	record = 1337
	unit = Research group
	examiner = B16f00t
	notes = Chat maintained between the murderer and the victim
	
Here we must put our company logo, company or unit name, as well as the assigned registration number, unit or group where we belong, who is the examiner and we can also specify notes on the report.

To generate the report we must specify the flag "-r" or "-r EN" if we want the report in English, as well as "-r ES" if we want the report in Spanish.

Usage example: python -m -r -u 34XXX230775 (Creates a report of the conversation with the user 34XXX230775)

Note that to create a report that makes sense to the reader you must always specify a user with the flag "-u" or a group with the flag "-g". (To know the group number we want to use in our report we can first use the command "python whapa.py -i" and then copy and paste it into the command "python -m -r -g PASTE-HERE-GROUPNUMBER@g.us"), or the flag "-a", which creates a report of all conversations held (slow option).

If you copy the "wa.db" database into the same directory as the script, the phone number will be displayed along with the name.

For the report to contains the images, videos, documents... you must copy the "WhatsApp/Media" folder of your phone to the whapa directory.

If we want to print the document or create the report in pdf, I recommend in the print option -> scale the view <= 70%, otherwise the report will be displayed too large.

WHAMERGE
====
whamerge is a tool to joins backups in a new database, to be able to be analyzed and obtain more information, such as deleted groups, messages, etc...
Warning: Do not join restored databases with old copies, since they repeat the same ids and the copy will not be done correctly.

Usage
=====
     __      __            _____                              
    /  \    /  \_____     /     \   ___________  ____   ____  
    \   \/\/   /\__  \   /  \ /  \_/ __ \_  __ \/ ___\_/ __ \ 
     \        /  / __ \_/    Y    \  ___/|  | \/ /_/  >  ___/ 
      \__/\  /  (____  /\____|__  /\___  >__|  \___  / \___  >
           \/        \/         \/     \/     /_____/      \/ 
    ------------------- Whatsapp Merger v0.1 -----------------
    
usage: wamerge.py [-h] [-o OUTPUT] [PATH]

Choose a database files path to merge

positional arguments:
  PATH                  Database path

optional arguments:
  -h, --help            show this help message and exit
  -o OUTPUT, --output OUTPUT
                        Database output file 'msgstore_merge.db'



WHAGODRI
=====
whagodri.py is a tool which allows WhatsApp users on Android to extract their backed up WhatsApp data from Google Drive.


Usage
=====
    	 __      __.__             ________      ________        .__ 
    	/  \    /  \  |__ _____   /  _____/  ____\______ \_______|__|
    	\   \/\/   /  |  \\__  \ /   \  ___ /  _ \|    |  \_  __ \  |
    	 \        /|   Y  \/ __ \\    \_\  (  <_> )    `   \  | \/  |
    	  \__/\  / |___|  (____  /\______  /\____/_______  /__|  |__|
    	       \/       \/     \/        \/              \/          
	
    	------------ Whatsapp Google Drive Extractor v0.1 ------------
    
	usage: whagodri.py [-h] [-i | -l | -lw | -p FilePath BackupID | -s] [-f]

	Extract your Whatsapp files from Google Drive

	optional arguments:
  	-h, --help            show this help message and exit
  	-i, --info            Show information about Whatsapp backups
  	-l, --list            List all available files
  	-lw, --list_whatsapp  List Whatsapp backups
  	-p FilePath BackupID, --pull FilePath BackupID
      	                      Pull a file from Google Drive
  	-s, --sync            Sync all files locally
  	-f, --flush           Flush log file to sync from the beginning


WHACIPHER
=====
whacipher.py is a tool which allows decrypt or encrypt WhatsApp database. You must have the key of your phone to decrypt, and additionally a encrypted database as reference to encrypt a new database.


Usage
=====

     __      __        _________ .__       .__                  
    /  \    /  \_____  \_   ___ \|__|_____ |  |__   ___________ 
    \   \/\/   /\__  \ /    \  \/|  \____ \|  |  \_/ __ \_  __ \
     \        /  / __ \\     \___|  |  |_> >   Y  \  ___/|  | \/
      \__/\  /  (____  /\______  /__|   __/|___|  /\___  >__|   
           \/        \/        \/   |__|        \/     \/             
    ---------- Whatsapp Encryption and Decryption v0.1 ----------
    
usage: wacipher.py [-h] [-f [FILE] | -p [PATH]] [-d DECRYPT]
                   [-e ENCRYPT ENCRYPT]

Choose a file or path to decrypt or encrypt

optional arguments:
  -h, --help            show this help message and exit
  -f [FILE], --file [FILE]
                        Database file to encrypt o decrypt
  -p [PATH], --path [PATH]
                        Database path to decrypt
  -d DECRYPT, --decrypt DECRYPT
                        Whatsapp Key path (Decrypt database)
  -e ENCRYPT ENCRYPT, --encrypt ENCRYPT ENCRYPT
                        'Whatsapp Key path' + 'msgstore.db.crypt12' (Encrypt
                        database)

Examples
=====

	Decrypt a Whatsapp database
		python wacipher.py -f msgstore.db.crypt12 -d key

	Decrypt all Whatsapp database in a path
		python wacipher.py -p ./ -d key

	Encrypt a Whatsapp database (you must provide a encrypted database and the key to generate the new encrypted database)
		python wacipher.py -f msgstore.db -e key msgstore.db.crypt12

Get in touch
=====
Acknowledgements, suggestions, languages, improvements...

https:/t.me/B16f00t
  
	
Disclaimer
=====
The developer is not responsible, and expressly disclaims all liability for damages of any kind arising from the use, reference or reliance on the software. The information provided by the software is not guaranteed to be correct, complete and up-to-date.

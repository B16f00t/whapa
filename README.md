![alt tag](https://github.com/B16f00t/whapa/blob/master/doc/whapa.png)


Whatsapp Parser
==================================
Updated: April 2018 - Version 0.5

WhatsApp Messenger Version 2.18.105

Whapa is an android whatsapp database parser that automates the process. The main purpose of whapa is to present the data handled by the Sqlite database in a way that is comprehensible to the analyst.
The Script is written in Python 2.x

The software is divided into three modes:
* **Message Mode**: Analyzes all messages in the database, applying different filters. It extracts thumbnails when they're availables.
		    "./Media" is the directory where thumbnails are being written. The rows are sorted by timestamp not by id.
* **Decryption Mode**: Decryptes the crypto12 databases as long as it has the key.
* **Info Mode**: Displays different information about statuses, broadcasts list and groups.
* **Extract Mode**: Extracts all thumbnails from the database

If you copy the "wa.db" database into the same directory as the script, the phone number will be displayed along with the name.

Please note that this project is an early stage. As such, you could find errors. Use it at your own risk!

**Bonus**: It also comes with a tool to download the backup copies of google drive associated with a smartphone.

Changelog
=====
https://github.com/B16f00t/whapa/blob/master/doc/CHANGELOG.md	

Installation
=====
 whapa.py (Whatsapp parser)
---------
You can download the latest version of whapa by cloning the GitHub repository:

	git clone https://github.com/B16f00t/whapa.git
then:

	pip install -r ./doc/requirements.txt
	
 whagdext.py (Extracts whatsapp datas from google drive account)
-------------
	To install:
	sudo apt-get update
	sudo apt-get install -y python3-pip
	sudo pip3 install pyportify
	
	To config:
	edit only the values of the file ./cfg/settings.cfg
		[auth]
		gmail = alias@gmail.com
		passw = yourpassword
		devid = Device ID (optional, if specified get more information)
		
	To usage:
		whagdext.py -help|-vers|-info|-list|-sync|-pull file [backupID]


Usage
=====
	     __      __.__          __________         
	    /  \    /  \  |__ _____ \______   \_____   
	    \   \/\/   /  |  \\__  \ |     ___/\__  \  
	     \        /|   Y  \/ __ \|    |     / __ \_
	      \__/\  / |___|  (____  /____|    (____  /
	           \/       \/     \/               \/ 
	    ---------- Whatsapp Parser v0.5 -----------
    	
	usage: whapa.py [-h] [-k KEY | -i | -m | -e] [--update]
        [-u USER | -ua USER_ALL | -g GROUP | -a] [-t TEXT] [-w] [-s]
        [-b] [-ts TIME_START] [-te TIME_END] [-r [{EN,ES}]]
        [-tt | -ti | -ta | -tv | -tc | -tl | -tx | -tp | -tg | -td | -tr]
        [DATABASE]

	To start choose a database and a mode with options
	
	positional arguments:
  	  DATABASE              Database file path - './msgstore.db' by default

	optional arguments:
  	  -h, --help            show this help message and exit
  	  -k KEY, --key KEY     *** Decrypt Mode *** - key file path
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

		python whapa.py -m 
	Show all messages from the database.

		python whapa.py -m -tS "12-12-2017 12:00" -tE "13-12-2017 12:00"
	Show all messages from 12-12-2017 12:00 to 13-12-2017 12:00.

		python whapa.py -m -w -tI
	Show all images send by Whatsapp Web.
	
		python whapa.py -m -g 34XXXXXXXXX-1345475288@g.us	
	Show all messages send by that group.
		
		python whapa.py -m -a -r EN
	Show all chats of the phone and makes English reports.

* Decrypt mode:

		python whapa.py msgstore.db.crypt12 -k key
	Decrypt msgstore.dbcrypt12, creating msgstore.db

* Info mode:

		python whapa.py -i
	Show a stage with options about groups, broadcast lists and statuses.

* Extract mode:

		python whapa.py -e -ts "01-01-2018 00:00"
	Extract all thumbnails from '01-01-2018 00:00' so far. 

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

Upcoming update
=====
Recover deleted messages.

Get in touch
=====
Acknowledgements, suggestions, languages, improvements...

https:/t.me/B16F00T
  
	
Disclaimer
=====
The developer is not responsible, and expressly disclaims all liability for damages of any kind arising from the use, reference or reliance on the software. The information provided by the software is not guaranteed to be correct, complete and up-to-date.

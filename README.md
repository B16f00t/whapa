![alt tag](https://github.com/B16f00t/whapa/blob/master/doc/whapa.png)


Whatsapp Parser
==================================
Updated: March 2018 - Version 0.3

WhatsApp Messenger Version 2.18.79

Whapa is an android whatsapp database parser that automates the process. The main purpose of whapa is to present the data handled by the Sqlite database in a way that is comprehensible to the analyst.
The Script is written in Python 2.x

The software is divided into three modes:
* **Message Mode**: It analyzes all messages in the database, applying different filters. It extracts thumbnails when they're availables.
		    "./Media" is the directory where thumbnails are being written. The rows are sorted by timestamp not by id.
* **Decryption Mode**: Decrypt crypto12 databases as long as we have the key.
* **Info Mode**: Displays different information about statuses, broadcasts list and groups.

If you copy the "wa.db" database into the same directory as the script, the phone number will be displayed along with the name.

Please note that this project is an early stage. As such, you could find errors. Use it at your own risk!

**Bonus**: It also comes with a tool to download the backup copies of google drive associated with a smartphone.

Changelog
=====
https://github.com/B16f00t/whapa/doc/CHANGELOG.md	

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
		
	To usage:
	python3 whagdext.py "arguments"

Usage
=====
	     __      __.__          __________         
	    /  \    /  \  |__ _____ \______   \_____   
	    \   \/\/   /  |  \\__  \ |     ___/\__  \  
	     \        /|   Y  \/ __ \|    |     / __ \_
	      \__/\  / |___|  (____  /____|    (____  /
	           \/       \/     \/               \/ 
	    ---------- Whatsapp Parser v0.3 -----------
    	
	usage: whapa.py [-h] [-k KEY | -i | -m] [-t TEXT] [-u USER] [-g GROUP] [-w]
	                [-s] [-b] [-tS TIME_START] [-tE TIME_END] [-r [{EN,ES}]]
	                [-tT | -tI | -tA | -tV | -tC | -tL | -tX | -tP | -tG | -tD | -tR]
	                [DATABASE]
	
	To start choose a database and a mode with options
	
	positional arguments:
  	DATABASE              database file path - './msgstore.db' by default
	
	optional arguments:
	  -h, --help            Show this help message and exit
	  -k KEY, --key KEY     *** Decrypt Mode *** - key file path
	  -i, --info            *** Info Mode ***
	  -m, --messages        *** Message Mode ***
	  -t TEXT, --text TEXT  Filter messages by text match
	  -u USER, --user USER  Filter messages made by phone number
	  -g GROUP, --group GROUP
	                        Filter messages made by group number
	  -w, --web             Filter messages made by Whatsapp Web
	  -s, --starred         Filter messages starred by owner
	  -b, --broadcast       Filter messages send by broadcast
	  -tS TIME_START, --time_start TIME_START
	                        Filter messages by start time (dd-mm-yyyy HH:MM)
	  -tE TIME_END, --time_end TIME_END
	  -r, --report,         Make html report in 'EN' English or 'ES' Spanish
	  -tT, --type_text      Filter text messages
	  -tI, --type_image     Filter image messages
	  -tA, --type_audio     Filter audio messages
	  -tV, --type_video     Filter video messages
	  -tC, --type_contact   Filter contact messages
	  -tL, --type_location  Filter location messages
	  -tX, --type_call      Filter audio/video call messages
	  -tP, --type_application
	                        Filter application messages
	  -tG, --type_gif       Filter GIF messages
	  -tD, --type_deleted   Filter deleted object messages
	  -tR, --type_share     Filter Real time location messages	 
	  
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


* Decrypt mode:

		python whapa.py msgstore.db.crypt12 -k key
	Decrypt msgstore.dbcrypt12, creating msgstore.db

* Info mode:

		python whapa.py -i
	Show a stage with options about groups, broadcast lists and statuses.

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

To generate the report we must specify the flag"-r" or -r EN" if we want the report in English, as well as"-r ES" if we want the report in Spanish.

Usage example: python -m -r -u 34XXX230775 (Creates a report of the conversation with the user 34XXX230775)

Note that to create a report that makes sense to the reader you must always specify a user with the flag"-u" or a group with the flag"-g". (To know the group number we want to use in our report we can first use the command "python whapa.py -i" and then copy and paste it into the command"python -m -r -g PASTE-HERE-GROUPNUMBER@g.us").

If we want to print the document or create the report in pdf, I recommend in the print option -> scale the view <= 70%, otherwise the report will be displayed too large.

Upcoming update
=====
Recover deleted messages.
  
	
Disclaimer
=====
The developer is not responsible, and expressly disclaims all liability for damages of any kind arising from the use, reference or reliance on the software. The information provided by the software is not guaranteed to be correct, complete and up-to-date.

![alt tag](https://github.com/B16f00t/whapa/blob/master/whapa.png)


Whatsapp Parser
==================================
Updated: February 2018 - Version 0.2

WhatsApp Messenger Version 2.18.29

Whapa is a whatsapp database parser that automates the process. The main purpose of whapa is to present the data handled by the Sqlite database in a way that is comprehensible to the analyst.
The Script is written in Python 2.x

The software is divided into three modes:
* **Message Mode**: It analyzes all messages in the database, applying different filters. It extracts thumbnails when they're availables.
* **Decryption Mode**: Decrypt crypto12 databases as long as we have the key.
* **Info Mode**: Displays different information about statuses, broadcasts list and groups.

Please note that this project is an early stage. As such, you could find errors. Use it at your own risk!

**Bonus**: It also comes with a tool to download the backup copies of google drive associated with a smartphone.

* "Whapas.py" is the spanish version of "whapa.py"


Installation
=====
 whapa.py (Whatsapp parser)
---------
You can download the latest version of whapa by cloning the GitHub repository:

	git clone https://github.com/B16f00t/whapa.git
then:

	pip install -r requirements.txt
	
 whagdext.py (Extracts datas from Google Drive Account)
-------------

	sudo apt-get update
	sudo apt-get install -y python3-pip
	sudo pip3 install pyportify
	To usage:
	config settings.cfg
		[auth]
		gmail = alias@gmail.com
		passw = yourpassword
	python3 whagdext.py "arguments"


Usage
=====
	     __      __.__          __________         
	    /  \    /  \  |__ _____ \______   \_____   
	    \   \/\/   /  |  \\__  \ |     ___/\__  \  
	     \        /|   Y  \/ __ \|    |     / __ \_
	      \__/\  / |___|  (____  /____|    (____  /
	           \/       \/     \/               \/ 
	    ---------- Whatsapp Parser v0.2 -----------
    	
	usage: whapa.py [-h] [-k KEY | -i | -m] [-t TEXT] [-u USER] [-g GROUP] [-w]
	                [-s] [-b] [-tS TIME_START] [-tE TIME_END]
	                [-tT | -tI | -tA | -tV | -tC | -tL | -tX | -tP | -tG | -tD | -tR]
	                [DATABASE]
	
	To start choose a database and a mode with options
	
	positional arguments:
  	DATABASE              database file path - './msgstore.db' by default
	
	optional arguments:
	  -h, --help            show this help message and exit
	  -k KEY, --key KEY     *** Decrypt Mode *** - key file path
	  -i, --info            *** Info Mode ***
	  -m, --messages        *** Message Mode ***
	  -t TEXT, --text TEXT  filter messages by text match
	  -u USER, --user USER  filter messages made by a phone number
	  -g GROUP, --group GROUP
	                        filter messages made in a group number
	  -w, --web             filter messages made by Whatsapp Web
	  -s, --starred         filter messages starred by user
	  -b, --broadcast       filter messages send by broadcast
	  -tS TIME_START, --time_start TIME_START
	                        filter messages by start time (dd-mm-yyyy HH:MM)
	  -tE TIME_END, --time_end TIME_END
	                        filter messages by end time (dd-mm-yyyy HH:MM)
	  -tT, --type_text      filter text messages
	  -tI, --type_image     filter image messages
	  -tA, --type_audio     filter audio messages
	  -tV, --type_video     filter video messages
	  -tC, --type_contact   filter contact messages
	  -tL, --type_location  filter location messages
	  -tX, --type_call      filter audio/video call messages
	  -tP, --type_application
	                        filter application messages
	  -tG, --type_gif       filter GIF messages
	  -tD, --type_deleted   filter deleted object messages
	  -tR, --type_share     filter Real time location messages	 

Examples
=====
("./Media" is the directory where thumbnails is being written)

* Message mode:

		python whapa.py -m 
	Show all messages from the database.

		python whapa.py -m -tS "12-12-2017 12:00" -tE "13-12-2017 12:00"
	Show all messages from 12-12-2017 12:00 to 13-12-2017 12:00.

		python whapa.py -m -w -tI
	Show all images send by Whatsapp Web.


* Decrypt mode:

		python whapa.py msgstore.db.crypt12 -k key
	Decrypt msgstore.dbcrypt12, creating msgstore.db

* Info mode:

		python whapa.py -i
	Show a stage with options about groups, broadcast lists and statuses.


Upcoming update
=====
Creating reports of the information displayed by the script.
  
	
Disclaimer
=====
The developer is not responsible, and expressly disclaims all liability for damages of any kind arising from the use, reference or reliance on the software. The information provided by the software is not guaranteed to be correct, complete and up-to-date.

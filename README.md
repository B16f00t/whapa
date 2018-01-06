![alt tag](https://github.com/B16f00t/whapa/blob/master/whapa.png)

Whatsapp Parser
==================================
Updated: January 2018 - Version 0.1

Whapa is a whatsapp database parser that automates the process. The main purpose of whapa is to present the data handled by the Sqlite database in a way that is comprehensible to the analyst.

The software is divided into three modes:
* **Message Mode**: It analyzes all messages in the database, applying different filters.
* **Decryption Mode**: Decrypt crypto12 databases, as long as we have the key.
* **Info Mode**: Displays different information about statuses, broadcasts list and groups.

Please note that this project is an early stage. As such, you could find errors. Use it at your own risk!

**Bonus**: It also comes with a tool to download the backup copies of google drive associated with a smartphone.



Installation
=====
You can download the latest version of whapa by cloning the GitHub repository:

	git clone https://github.com/B16f00t/whapa.git


Usage
=====
     __      __.__          __________
    /  \    /  \  |__ _____ \______   \_____
    \   \/\/   /  |  \\__  \ |     ___/\__  \
     \        /|   Y  \/ __ \|    |     / __ \_
      \__/\  / |___|  (____  /____|    (____  /
           \/       \/     \/               \/
    ---------- Whatsapp Parser v0.1 -----------

	usage: whapa.py [-h] [-k KEY | -i | -m] [-tS TIME_START] [-tE TIME_END] [-t TEXT] [-u USER] [-g GROUP] [-w] [DATABASE]

	To start choose a database and a mode with options

	positional arguments:
  		DATABASE              database file path - './msgstore.db' by default

	optional arguments:
  		-h, --help          			  show this help message and exit
  		-k KEY, --key KEY     			  *** Decrypt Mode *** - key file path
  		-i, --info       			  *** Info Mode ***
  		-m, --messages      			  *** Message Mode ***
  		-tS TIME_START, --time_start TIME_START   show messages by start time (dd-mm-yyyy HH:MM)
  		-tE TIME_END, --time_end TIME_END         show messages by end time (dd-mm-yyyy HH:MM)
  		-t TEXT, --text TEXT  			  show messages by text match
  		-u USER, --user USER  			  show messages made by a phone number
  		-g GROUP, --group GROUP                   show messages made in a group number
  		-w, --web   			          show messages made by Whatsapp Web

		 

Upcoming update
=====
Creating reports of the information displayed by the software
  
	
Disclaimer
=====
The developer is not responsible, and expressly disclaims all liability for damages of any kind arising from the use, reference or reliance on the software. The information provided by the software is not guaranteed to be correct, complete and up-to-date.

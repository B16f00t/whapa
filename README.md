<p align="center">
  <img  src="https://github.com/B16f00t/whapa/blob/master/doc/whapa.png">
</p>

Whatsapp Parser Toolset
====
Updated: May 2022

WhatsApp Messenger Version 2.21.9.14

Whapa is a set of graphical forensic tools to analyze whatsapp from Android and soon iOS devices. All the tools have been written in Python 3.8 and have been tested on linux, windows and macOS systems.

Note: Whapa provides 10x more performance and fewer bugs on linux systems than on windows. 

Whapa is included as standard in distributions such as Tsurugi Linux (Digital Forensics) and BlackArch Linux (Penetration Testing).

Whapa toolset is divided in five tools:

**Android**
======
* **Whapa**     (Whatsapp Parser)(Only working with old database, Working in Progress...)
* **Whacipher** (Whatsapp Encryption/Decryption) *** Not support Crypt15 ***
* **Whagodri**  (Whataspp Google Drive Extractor)
* **Whamerge**  (Whatsapp Merger) (Only working with old database, Working in Progress...)
* **Whachat**   (Whatsapp Chat Exporter)

**IPhone**
====
* **Whacloud**  (Whatsapp ICloud Extractor) (Not working)
* **Whachat**   (Whatsapp Chat Exporter)


**Do you like this project? Support it by donating**
- ![Paypal](https://raw.githubusercontent.com/reek/anti-adblock-killer/gh-pages/images/paypal.png) Paypal: [Donate](https://paypal.me/b16f00t?locale.x=es_ES)


Changelog
====
https://github.com/B16f00t/whapa/blob/master/doc/CHANGELOG.md	

Installation
====
You can download the latest version of whapa by cloning the GitHub repository:

	git clone https://github.com/B16f00t/whapa.git && cd whapa
then (Linux or macOS):

	pip3 install --upgrade -r ./doc/requirements.txt
	
or (Windows):
	
	pip install --upgrade -r ./doc/requirements.txt


Start
====
if you use Linux system:

	python3 whapa-gui.py

if you use Windows system:
	
	python whapa-gui.py
	or 
	click on whapa-gui.bat

if you use macOS system (2 install options):
1) Install (Thanks to XuluWarrior):
		
		brew install python-tk


2) Install a later version of TK (Thanks to FetchFast):
		
		brew install tcl-tk
    
* Uninstall python3 and then download and reinstall python 3.9x from python.org

		brew uninstall python3
		https://www.python.org/downloads/
	
* Install requirements
	
		pip3 install --upgrade -r ./doc/requirements.txt
	
* Run with python3.9x whapa-gui.py

And a window like this will be displayed on the screen:

<p align="center">
  <img src="https://raw.githubusercontent.com/B16f00t/whapa/master/doc/software.png" width="720" height="576">
</p>

WHAPA
====
whapa.py is an Android whatsapp database parser which automates the process and presents the data handled by the SQLite database in a way that is comprehensible to the analyst.
If you copy the "wa.db" database into the same directory as the script, the phone number will be displayed along with the name.

Please note that this project is an early stage. As such, you could find errors. Use it at your own risk!

Reports
=====
To create reports the first thing we need to do is to configure the file"./cfg/settings.cfg". For example:

	[report]
	company = Foo S.L
	record = 1337
	unit = Research group
	examiner = B16f00t
	notes = Chat maintained between the murderer and the victim
	
If we want to put the logo of our company, we must replace the file './cfg/logo.png' by the one of our choice.
In the file './cfg/settings.cfg', the name of the company or unit must be specified, as well as the assigned registration number, the unit or group we belong to, who the examiner is and we can also specify notes in the report.

To generate the report we must specify the option "English" whether we want the report in English, as well as "ES" whether we want the report in Spanish.

If you specify the "wa.db" database, the phone number will be displayed along with the name.
For the report to contains the images, videos, documents... you must copy the "WhatsApp/Media" folder of your phone to the report directory, otherwise the program will generate thumbnails.

If we want to print the document or create the report in pdf, It recommends in the print option -> scale the view <= 60% or 70%, otherwise the report will be displayed too large.


WHACIPHER
=====
whacipher.py is a tool which allows decrypt or encrypt WhatsApp database. You must have the key of your phone to decrypt, and additionally a encrypted database as reference to encrypt a new database.


WHAMERGE
====
whamerge is a tool to joins backups in a new database, to be able to be analyzed and obtain more information, such as deleted groups, messages, etc...

Warning: Do not join restored databases with old copies, since they repeat the same ids and the copy will not be done correctly.


WHAGODRI
=====
whagodri.py is a tool which allows WhatsApp users on Android to extract their backed up WhatsApp data from Google Drive.

Make sure of:
* Download the latest version of whapa
* Install the requirements
* Settings:

Edit only the values of the./cfg/settings.cfg file

		[google-auth]
		gmail = alias@gmail.com
		# Optional. The account password or app password when using 2FA.
		password  = 
		# Optional. The result of "adb shell settings get secure android_id".
		android_id = 0000000000000000
		# Optional. Enter the backup country code + phonenumber be synchronized, otherwise it synchronizes all backups.
		# You can specify a list of celnumbr = BackupNumber1, BackupNumber2, ...
		celnumbr = 

* New Method: Login by OAuth, this method is not valid for accounts without a phone number or alternative email associated to the account.
* If you request it, log in to your browser and then click here. https://accounts.google.com/b/0/DisplayUnlockCaptcha
* If you want to use 2FA (Two Factor Authentication), you will have to go to the URL: https://myaccount.google.com/apppasswords Then select Application: Other. Write down: Whapa, and a password will be display, then you must write the password in your settings.cfg.
(Thanks to YuriCosta) or Login by OAuth.

WHACLOUD
=====
whacloud.py is a tool which allows WhatsApp users on Iphone to extract their backed up WhatsApp data from ICloud.
BETA TOOL May contain bugs.

Make sure of:
* Download the latest version of whapa
* Install the requirements
* Settings:

Edit only the values of the./cfg/settings.cfg file

		[icloud-auth]
		icloud = alias@icloud.com
		passw = yourpassword
	
	
WHACHAT
=====
whachat.py is a tool to make an interactive report from whatsapp's export chat functionality.

To export chats on an Android phone, here are the steps:
   1. Open the individual or group chat.
   2. Press the Menu button.
   3. Press More.
   4. Select Export chat.
   5. Choose Include or Exclude files.
   
To export chats on an iOS phone, here are the steps:
   1. Open the individual or group chat.
   2. Press on the name (Chat information).
   3. Slide down.
   4. Select Export chat.
   5. Choose Include or Exclude files.
   
		
Get in touch
=====
Acknowledgements, suggestions, languages, improvements...

Telegram Channel and discuss group

	https://t.me/bigfoot_whapa
	
Disclaimer
=====
The developer is not responsible, and expressly disclaims all liability for damages of any kind arising from the use, reference or reliance on the software. The information provided by the software is not guaranteed to be correct, complete and up-to-date.

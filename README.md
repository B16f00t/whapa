<p align="center">
  <img  src="https://github.com/B16f00t/whapa/blob/master/doc/whapa.png">
</p>

Whatsapp Parser Toolset
====
Updated: Sep 2019

WhatsApp Messenger Version 2.19.244

Whapa is a forensic graphical toolset for analyzing whatsapp in android. All the tools have been written in Python 3.X and have been tested on linux and windows 10 systems.

Note: Whapa provides 10x more performance and fewer bugs on linux systems than on windows. 

Whapa is included as standard in distributions such as Tsurugi Linux (Digital Forensics) and BlackArch Linux (Penetration Testing).

Whapa toolset is divided in four tools:

* **Whapa**     (Whatsapp Parser)
* **Whamerge**  (Whatsapp Merger)
* **Whagodri**  (Whataspp Google Drive Extractor)
* **Whacipher** (Whatsapp Encryption/Decryption)


**Do you like this project? Support it by donating**
- ![Paypal](https://raw.githubusercontent.com/reek/anti-adblock-killer/gh-pages/images/paypal.png) Paypal: [Donate](https://paypal.me/b16f00t?locale.x=es_ES)
- ![btc](https://github.com/nullablebool/crypto-icons/blob/master/16x16/BTC-16.png) Bitcoin: 13h2rupiKBr8bFygKdCunfXrn2pAaVoaTQ


Changelog
====
https://github.com/B16f00t/whapa/blob/master/doc/CHANGELOG.md	

Installation
====
You can download the latest version of whapa by cloning the GitHub repository:

	git clone https://github.com/B16f00t/whapa.git
then:

	pip3 install -r ./doc/requirements.txt

Start
====
if you use Linux system:
* python3 whapa-gui.py

if you use Windows system:
* python whapa-gui.py
	or 
* click on whapa-gui.bat

<p align="center">
  <img src="https://raw.githubusercontent.com/B16f00t/whapa/master/doc/software.jpg" width="720" height="576">
</p>

WHAPA
====
whapa.py is an android whatsapp database parser which automates the process and presents the data handled by the Sqlite database in a way that is comprehensible to the analyst.
If you copy the "wa.db" database into the same directory as the script, the phone number will be displayed along with the name.

Please note that this project is an early stage. As such, you could find errors. Use it at your own risk!

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

To generate the report we must specify the option "English" whether we want the report in English, as well as "ES" whether we want the report in Spanish.

If you copy the "wa.db" database into the same directory as the script, the phone number will be displayed along with the name.
For the report to contains the images, videos, documents... you must copy the "WhatsApp/Media" folder of your phone to the whapa directory, otherwise the program will generate thumbnails.

If we want to print the document or create the report in pdf, It recommends in the print option -> scale the view <= 60% or 70%, otherwise the report will be displayed too large.


WHAMERGE
====
whamerge is a tool to joins backups in a new database, to be able to be analyzed and obtain more information, such as deleted groups, messages, etc...

Warning: Do not join restored databases with old copies, since they repeat the same ids and the copy will not be done correctly.


WHAGODRI
=====
whagodri.py is a tool which allows WhatsApp users on Android to extract their backed up WhatsApp data from Google Drive.

Make sure of:
* Disable 2FA in your Google Account
* Download the latest version of whapa
* Install the requirements
* Settings:

Edit only the values of the./cfg/settings.cfg file

		[auth]
		gmail = alias@gmail.com
		passw = yourpassword
		devid = Device ID (optional, if specified get more information)
		celnumbr = BackupPhoneNumber (ex. 3466666666666)
* If you request it, log in to your browser and then click here, https://accounts.google.com/DisplayUnlockCaptcha.


WHACIPHER
=====
whacipher.py is a tool which allows decrypt or encrypt WhatsApp database. You must have the key of your phone to decrypt, and additionally a encrypted database as reference to encrypt a new database.


Get in touch
=====
Acknowledgements, suggestions, languages, improvements...

https://t.me/B16f00t
  
	
Disclaimer
=====
The developer is not responsible, and expressly disclaims all liability for damages of any kind arising from the use, reference or reliance on the software. The information provided by the software is not guaranteed to be correct, complete and up-to-date.

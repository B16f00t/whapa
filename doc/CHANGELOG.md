Changelog
====
All notable changes to this project will be documented in this file.

May 2022

	[+] whapa-gui.py v1.58
	[+] whacipher.py
		[-] Fixed Decrypt crypt14 files.
	[+] whagodri.py
		[-] Fixed bug connecting with Google.
		[-] Added No parallel downloads
		[-] Added support for jpeg files with option "-si"

Nov 2021

	[+] whapa-gui.py v1.56
	[+] whagodri.py
		[-] Support Multiaccount. You can download accounts with more than two numbers.
Agu 2021

	[+] whapa-gui.py v1.55
	[+] whapa.py
		[-] Fixed bug with settings file
	[+] whachat.py
		[-] New time formats
		
Jul 2021

	[+] whapa-gui.py v1.54
		[-] Full compatibility with Linux and Windows (Gui and Commnad Line)
	[+] whapa.py
		[-] Enabled data carving for linux
	[+] whagodri.py
		[-] Fixed minor bugs

	[+] whapa-gui.py v1.53
	[+] whagodri.py
		[-] Fixed Linux problem

	[+] whapa-gui.py v1.52
	[+] Whapa
		[-] Fixed command line execution problem
	[+] whagodri.py
		[-] Fixed command line execution problem
		[-] Show more information about downloads
		

Jun 2021

	[+] whapa-gui.py v1.51
	[+] whagodri.py
		[-] Speed improvement
		
	[+] whapa-gui.py v1.5
	[+] whacipher.py
		[-] Decrypt error fixed
	[+] whagodri.py
		[-] Need browser error fixed

Feb 2021

	[+] whapa-gui.py v1.43
		[-] Media not mapped correctly in the HTML report fixed
	[+] whacipher.py
		[-] script improved
		
	[+] whapa-gui.py v1.42
	[+] whachat.py
		[-] Error parsing phonenumber fixed
		
	[+] whapa-gui.py v1.41
		[-] Settings file fixed
	
	[+] whapa-gui.py v1.40
		[-] New minimal design
		[-] New tool WhaChat
	[+] whachat.py
		[-] New tool to export chat from IOs and Android
	[+] whapa.py
		[-] Many bugs Fixed
					
Jan 2021

	[+] whapa-gui.py v1.3
		[-] New tool WhaCloud
	[+] whacloud.py
		[-] New tool to download your backup from ICloud
	[+] whapa.py
		[-] New SQLite data carving option
		[-] You can choose the report output file
	[+] update.py
		[-] Bug Fixed
		
Sep 2020

	[+] whapa-gui.py v1.2
		[-] Fix problem with requests library, now there is a button to update
		[-] You can search for a text string inside whapa tab
	[+] whagodri.py
		[-] Enabled two factor authentication
		[-] More debugs and workaround messages
		[-] settings.cfg file easier
		
Jun 2020

	[+] whapa-gui.py v1.16
	[+] whagodri.py
		[-] Fixed Google Drive crash when check update
	
Mar 2020
	
	[+] whapa-gui.py v1.15
	[+] whagodri.py
		[-] Fixed Google Drive crash

Oct 2019

	[+] whapa-gui.py v1.14
		[-] Fixed bug in downloading files individually
		
	[+] whapa-gui.py v1.13
		[-] whagodri tab changes, Only one download method and new options for downloading files
	[+] whagodri.py
		[-] Removed restriction from '00' or '+' in the settings file
		[-] Videos, images, audios, backups, documents can be recovered independently
	
Sep 2019

	[+] The whole project has been updated and improved to python3, now it is managed from a graphical interface
	[+] Fixed major bugs
	[+] whapa-gui.py v1.12
		[-] Check at the beginning if there is any update
		[-] whagodri tab changes, Add two method to download (Original and Alternative)
		[-] whagodri tab changes, It's added option to choose an output path
	[+] whagodri.py v1.11
		[-] Fixed Limit of 5000 files to download
		[-] It works with new google drive backup

May 2019

	[+] whapa.py v0.6
		[-] Disappears the option to decrypt database (new tool)
	[+] whamerge.py v0.1 (replaces to a whademe.py)
		[-] Merge new fields
	[+] whacipher.py is added

May 2018

	[+] whapa.py v0.5
		[-] Improved parses speed
		[-] When parse the database extracts all thumbnails
		[-] Reports are sorted in "./reports" path
		[-] Make an index of the reports ("index.hml"), when you use the -a -r flag 
		[-] Added flag "-e", Extract mode, extracts all media thumbnails of the database in "./thumbnails" path
		[-] Fix minor bugs
	[+] whademe.py v0.1
	[+] whagodri.py v0.1 (replaces to a whagdext3.py)

April 2018

    [+] whapa.py v0.4
    	[-] Added flag "--update" to update Whatsapp Parser Tool
    	[-] Added flag in message mode, "-ua" Show all messages mades by a number phone
    	[-] Added flag in message mode, "-a" Show all chat messages classified by phone number, group number and broadcast list 
    	[-] Added System Message, when the number is a company
    	[-] Added System Message, group description
    [+] whapa.py v0.3
    	[-] Added in info mode, the phone numbers with which the user have interacted
    	[-] Changed the format of some flags, now they are all in lowercase
    	[-] Fix minor bugs
    
March 2018

	[+] whapa.py v0.2
		[-] Added interactive html report
		[-] Added pdf report
		[-] Added making reports in spanish or english language
		[-] If you have "wa.db" database translates the phone numbers with name
		[-] Fixed minor bugs
		[-] Removed whapas.py 
    
February 2018

	[i] whapa.py v0.1
		[-] Fixed minor bugs
		[-] Added whapas.py

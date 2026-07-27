Changelog
====
All notable changes to this project will be documented in this file.

## 2.00 - July 2026

### Added
- **iOS support**: reads `ChatStorage.sqlite` (27 message types).
- **Current Android schema**: `message` / `message_type` table, alongside the
  legacy `messages` / `media_wa_type`. Which one is in use is detected
  automatically.
- **28 Android message types**, up from 15: polls, video notes, view-once media,
  events, albums, channel admin invitations, status mentions, advanced chat
  privacy, Meta AI feedback, and more.
- **crypt15** in whacipher.py, with real protobuf header parsing and
  HMAC-SHA256 key derivation. Accepts a `.key` file, `encrypted_backup.key`, or
  64 hexadecimal characters.
- System messages, quoted messages, reactions, edits, locations and the call log.
- Contacts from `wa.db` (Android) and `ContactsV2.sqlite` (iOS).
- **Full search engine**: literal text or regular expression, whole word, case
  sensitivity, sender, date range, direction, canonical type, native type code,
  and flags (deleted, starred, with attachment, forwarded, edited, with
  coordinates). Available from the command line, the graphical interface, and
  inside the report itself.
- **Printable report** (`-p`): table-based document for paper or PDF, with
  sequential numbering, a cover page carrying the case details, the search
  criteria applied, and SHA-256 verification of the sources.
- **CSV export** (`-x`) with 18 columns.
- **Attachment linking** (`-mp`): point at the `WhatsApp` folder copied from the
  handset and the report locates each file, showing images inline and playing
  audio and video in place, as the previous release did. `-cm` copies the
  attachments into the report folder so it can be handed over as one package.
  Files that cannot be located are still listed and flagged.
- **Location handling**: coordinates are shown in a dedicated block with a
  live-location badge and links to Google Maps and OpenStreetMap. The report
  makes no remote requests when opened. `-gm` downloads a static map per
  location while generating and stores it inside the report, keeping it usable
  offline.
- **KML export** (`-k`) of every location, for Google Earth or QGIS, with
  timestamp, chat, direction and message type on each placemark.
- **`whachat.py` now produces the same reports as `whapa.py`**: an exported chat
  is translated to the shared message model, so it gets the interactive viewer,
  the printable document, CSV export, the same filters and the same attachment
  handling. Attachments are picked up from the chat's own folder by default.
  Date parsing tries several export formats instead of a single mask, so
  messages no longer lose their timestamp when the mask does not match.
- SHA-256 of every source file, for chain of custody.
- Three new libraries in `libs/`: `whacodes.py` (code catalogue),
  `whareader.py` (database reading) and `whareport.py` (filtering and reports).

### Fixed
- **A single emoji in a message aborted the run.** WhatsApp messages carry
  emoji and symbols that the Windows console (cp1252) cannot represent, and
  printing one raised `UnicodeEncodeError` after the whole database had already
  been read. Every tool now sets up its output at startup: UTF-8 when the output
  is piped (the graphical interface reads it as UTF-8 too), and the console's own
  encoding with unrepresentable characters replaced when running in a real
  terminal, so accents keep working.
- **LID identifiers were shown as if they were phone numbers.** Since 2024
  WhatsApp identifies group participants with a LID (`...@lid`), an opaque id.
  It is now translated to the phone number when the database carries the
  mapping table, and marked as `LID:` when it does not, instead of passing for
  a number it is not.

### Fixed in the other tools
- `whacloud.py`, `whagodri.py`, `whachat.py` and `whamerge.py` now report a
  missing dependency in one line instead of a Python traceback, naming the pip
  package to install.
- The bundled copy of `gpsoauth` in `libs/` raised `PackageNotFoundError`
  because, not being pip-installed, it has no package metadata. `whagodri` could
  not start at all.
- `pycryptodomex`, needed by `gpsoauth`, was missing from `requirements.txt`.
- `whachat.py -h` crashed with `TypeError: %d format` because a help string
  contained an unescaped `%`.
- Removed every `SyntaxWarning: invalid escape sequence` across `libs/`.

### Fixed in the other tools
- **Graphical interface rewritten with CustomTkinter**, dark theme, one tab per
  tool. Work runs in the background and output is streamed live without
  freezing the window.
- The interactive report no longer embeds every message inside the HTML: it
  splits them into data files loaded on scroll and caps how many are held on
  screen. A 150,000-message conversation went from producing a 38.8 MB file that
  locked up the browser to opening instantly.
- Requires Python 3.11 or later.
- The graphical interface gains a top bar: **Install requirements** (uses the
  same Python that runs the interface), **Settings** (edits `cfg/settings.cfg`
  in place, including the Google and iCloud credentials), **Manual**, and a
  **Spanish / English** switch. The window now carries the whapa icon.
- `images/` trimmed from 43 files to 8: the old icon set belonged to the
  previous Tkinter interface and nothing referenced it any more.
- `whapa.py` keeps all its existing options and adds the new ones.

### Fixed
- The parser was reading the `messages` table, deprecated since 2021, which is
  why it stopped working with any recent backup.
- whacipher.py located the start of the data by trying fixed offsets blindly; it
  now parses the backup header.
- The graphical interface built commands as a string and ran them through
  `os.system()`, allowing command injection via file names. It now uses
  `subprocess` with an argument list.
- The graphical interface read Tkinter variables from the worker thread. Tk is
  not thread-safe; all interface access now happens on the main thread.
- Replaced `datetime.utcnow()` and `utcfromtimestamp()`, deprecated since
  Python 3.12.

### Known limitations
- Not yet validated against real-world dumps from either platform.
- Polls are detected but their options and votes are not parsed; channels and
  communities are not modelled as separate entities.
- `CallHistory.sqlite` (iOS call log) and `ZWAMESSAGEINFO` (per-participant read
  receipts) are not read.
- Attachments are linked, not embedded as base64: the report folder and the
  media folder must travel together, unless `-cm` is used.
- `whachat.py` shares the report engine now, but its chat parsing is unchanged.
  `whamerge.py`, `whagodri.py` and `whacloud.py` keep their original logic.

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

Whatsapp Parser Tool
==================================
ManTech Triage and Analysis System, Forensics Workflow Automation Suite

Update: July 2016 - Mantarayforensics.com has been decommissioned.  GitHub is now the main portal for MantaRay.

![alt tag](http://www.datarecovery.institute/wp-content/uploads/2016/08/whatsApp-forensics-Need1.png)

CMSmap is a python open source CMS scanner that automates the process of detecting security flaws of the most popular CMSs. The main purpose of CMSmap is to integrate common vulnerabilities 
for different types of CMSs in a single tool. 

At the moment, CMSs supported by CMSmap are WordPress, Joomla and Drupal.

Please note that this project is an early state. As such, you might find bugs, flaws or mulfunctions.
Use it at your own risk!


Installation
=====
You can download the latest version of CMSmap by cloning the GitHub repository:

	git clone https://github.com/Dionach/CMSmap.git


Usage
=====
	CMSmap tool v0.6 - Simple CMS Scanner
	Author: Mike Manzotti mike.manzotti@dionach.com
	Usage: cmsmap.py -t <URL>
	Targets:
		 -t, --target    target URL (e.g. 'https://example.com:8080/')
		 -f, --force     force scan (W)ordpress, (J)oomla or (D)rupal
		 -F, --fullscan  full scan using large plugin lists. False positives and slow!
		 -a, --agent     set custom user-agent
		 -T, --threads   number of threads (Default: 5)
		 -i, --input     scan multiple targets listed in a given text file
		 -o, --output    save output in a file
		 --noedb         enumerate plugins without searching exploits

	Brute-Force:
		 -u, --usr       username or file
		 -p, --psw       password or file
		 --noxmlrpc      brute forcing WordPress without XML-RPC

	Post Exploitation:
		 -k, --crack     password hashes file (Require hashcat installed. For WordPress and Joomla only)
		 -w, --wordlist  wordlist file

	Others:
		 -v, --verbose   verbose mode (Default: false)
		 -U, --update    (C)MSmap, (W)ordpress plugins and themes, (J)oomla components, (D)rupal modules, (A)ll
		 -h, --help      show this help

	Examples:
		 cmsmap.py -t https://example.com
		 cmsmap.py -t https://example.com -f W -F --noedb
		 cmsmap.py -t https://example.com -i targets.txt -o output.txt
		 cmsmap.py -t https://example.com -u admin -p passwords.txt
		 cmsmap.py -k hashes.txt -w passwords.txt


Notes
=====
30/03/2015: Created a new repo to remove big wordlist. Users who have originally cloned the previous repo are invited to clone the new one.
  
	
Disclaimer
=====
Usage of CMSmap for attacking targets without prior mutual consent is illegal. 
It is the end user's responsibility to obey all applicable local, state and federal laws. 
Developers assume NO liability and are NOT responsible f

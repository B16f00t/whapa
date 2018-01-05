MantaRay Forensics
==================================
ManTech Triage and Analysis System, Forensics Workflow Automation Suite

Update: July 2016 - Mantarayforensics.com has been decommissioned.  GitHub is now the main portal for MantaRay.

![alt tag](https://raw.githubusercontent.com/mantarayforensics/mantaray/master/mantaray/images/Mantaray_Logo_Template_Full_Screen.gif)

Overview
==================================

MantaRay is designed to automate the processing of forensic images, 
directories and individual files with open source tools. With 
support for numerous image formats, this tool provides a scalable 
base to utilize open source and custom exploitation tools.

Dependencies
==================================

See https://launchpad.net/~mantaray/+archive/stable for a full list

* BulkExtractor
* ENT – Calculate Entropy
* KML from JPG EXIF Data
* fdupes
* EXIF Tool
* Foremost
* Jumplist Parser
* Sleuth Kit tools
* Regripper
* Log2Timeline
* Volatility

Installation of MantaRay
==================================

SIFT 3.0 Workstation - (https://digital-forensics.sans.org/community/downloads):

    Download the virtual machine from SANS
    Update SIFT 3.0: 
    sudo apt-get update
    sudo apt-get upgrade
    sudo update-sift
    update to newest code found on GitHub (SIFT 3.0 --> /usr/share/mantaray)

Using bootstrap to install Mantaray:

    wget -q https://raw.githubusercontent.com/mantarayforensics/mantaray/master/mrbootstrap.sh && sh mrbootstrap.sh -i

Using bootstrap to install Mantaray, and the MantaRay Skin:

    wget -q https://raw.githubusercontent.com/mantarayforensics/mantaray/master/mrbootstrap.sh && sh mrbootstrap.sh -s -i


####PPA:

    sudo apt-add-repository ppa:mantaray/stable
    sudo apt-add-repository ppa:sift/stable
    sudo apt-get update && sudo apt-get upgrade -y
    sudo apt-get install mantaray
        
####Source from PPA:

    sudo apt-add-repository ppa:mantaray/stable
    apt-get source mantaray
    
####GitHub:

    git clone https://github.com/mantarayforensics/mantaray.git
    cd mantaray
    
Follow PPA directions to install dependencies

How To Run MantaRay
==================================
From command line (as user with sudo privileges) in PPA:

    sudo mantaray


A popup window should appear. Pressing continue will begin running the script.

Check For Updates
==================================
Using apt-get:

    sudo apt-get update && sudo apt-get upgrade

Using mantaray-updater:

    sudo mantaray-updater
    
GitHub:

    git pull origin master

Errors and Bugs
==================================
If MantaRay crashes, please re-run it in debug mode and send a screenshot
of the crash along with any other details you can report to our GitHub https://github.com/mantarayforensics/mantaray/issues

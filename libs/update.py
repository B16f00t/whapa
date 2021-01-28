import requests
import re
import webbrowser
import sys


def start(version):
    """Check if there is a new version"""
    request = requests.get("https://github.com/B16f00t/whapa")
    pattern = r'WhatsApp Parser Toolset v(\d.\d*)'
    matches = re.findall(pattern, request.text)
    for match in matches:
        if match:
            update = match
            break

    if float(update) > float(version):
        print("New version available: {}".format(update))
        webbrowser.open_new_tab("https://github.com/B16f00t/whapa")
    else:
        print("You have the latest version")


# Initializing
if __name__ == "__main__":
    if len(sys.argv) == 1:
        print("[i] Whapa Updater")
    else:
        start(sys.argv[1])

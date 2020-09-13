import requests
import re
import webbrowser
from tkinter import messagebox


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
        messagebox.showinfo("Update", "New version available\n{}".format(update))
        webbrowser.open_new_tab("https://github.com/B16f00t/whapa")
    else:
        messagebox.showinfo("Update", "You have the latest version")

import os
import time
import re
import sys
import subprocess
import webbrowser
from textwrap import dedent
from tkinter import *
from tkinter import ttk
from tkinter import messagebox
from tkinter import filedialog

""" Global vars"""
author = 'B16f00t'
title = 'WhatsApp Parser Toolset'
contact = "https://t.me/bigfoot_whapa"
version = '1.55'
system = ""
abs_path_file = os.path.abspath(__file__)     # C:\Users\Desktop\whapa\whapa-gui.py
whapa_path = os.path.split(abs_path_file)[0]  # C:\Users\Desktop\whapa


class ToolTip(object):
    """ Create a tooltip for a given widget """

    def __init__(self, widget, text='widget info'):
        self.widget = widget
        self.text = text
        self.widget.bind("<Enter>", self.enter)
        self.widget.bind("<Leave>", self.close)

    def enter(self, event=None):
        x = y = 0
        x, y, cx, cy = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 20

        # creates a toplevel window
        self.tw = Toplevel(self.widget)

        # Leaves only the label and removes the app window
        self.tw.wm_overrideredirect(True)
        self.tw.wm_geometry("+%d+%d" % (x, y))
        label = Label(self.tw, text=self.text, justify='left', background='yellow', relief='solid', borderwidth=1, font=("times", "8", "normal"))
        label.pack(ipadx=1)

    def close(self, event=None):
        if self.tw:
            self.tw.destroy()


class Whapa:
    """Menu Class"""

    def __init__(self, img_folder, icons):
        """ Defines windows, menu, submenus, shortcuts"""
        self.img_folder = img_folder
        self.icons = icons
        self.root = Tk()
        self.iconlogo = PhotoImage(file=self.icons[0])
        self.iconbg = PhotoImage(file=self.icons[1])
        self.iconabout = PhotoImage(file=self.icons[2])
        self.iconsetting = PhotoImage(file=self.icons[3])
        self.iconexit = PhotoImage(file=self.icons[4])
        self.iconsearh = PhotoImage(file=self.icons[5])
        self.iconmanual = PhotoImage(file=self.icons[6])
        self.iconreport = PhotoImage(file=self.icons[7])
        self.iconfile = PhotoImage(file=self.icons[8])
        self.icontabwhapa = PhotoImage(file=self.icons[9])
        self.icontabdrive = PhotoImage(file=self.icons[10])
        self.icontabcipher = PhotoImage(file=self.icons[11])
        self.icontabmerge = PhotoImage(file=self.icons[12])
        self.iconinfowhagodri = PhotoImage(file=self.icons[13])
        self.icondownwhagodri = PhotoImage(file=self.icons[14])
        self.iconmerge = PhotoImage(file=self.icons[15])
        self.icondecrypt = PhotoImage(file=self.icons[16])
        self.iconencrypt = PhotoImage(file=self.icons[17])
        self.icones = PhotoImage(file=self.icons[18])
        self.iconen = PhotoImage(file=self.icons[19])
        self.iconparser = PhotoImage(file=self.icons[20])
        self.iconone = PhotoImage(file=self.icons[21])
        self.iconextract = PhotoImage(file=self.icons[22])
        self.iconcall = PhotoImage(file=self.icons[23])
        self.iconstatus = PhotoImage(file=self.icons[24])
        self.iconrequire = PhotoImage(file=self.icons[25])
        self.iconupdate = PhotoImage(file=self.icons[26])
        self.iconcarving = PhotoImage(file=self.icons[27])
        self.icontabwhacloud = PhotoImage(file=self.icons[28])
        self.icontabwhachat = PhotoImage(file=self.icons[29])
        self.iconandroid = PhotoImage(file=self.icons[30])
        self.iconios = PhotoImage(file=self.icons[31])


        # Menu Windows Property
        self.root.title(title + " v" + version)
        self.root.iconphoto(self.root, self.iconlogo)
        self.root.option_add("*Font", "Helvetica 10")
        self.root.option_add('*tearOff', False)
        self.root.geometry('930x640+' + str(int((self.root.winfo_screenwidth()/2) - (975/2))) + '+' + str(int(self.root.winfo_screenheight()/2 - (810/2))))
        self.root.resizable(0, 0)
        self.root.grid_rowconfigure(1, weight=1)
        self.root.grid_columnconfigure(0, weight=1)


        # Variables
        """ Function that gets report config"""
        self.wagodri_box_value = StringVar()
        self.whacipher_box_value = StringVar()
        self.wacloud_box_value = StringVar()
        self.label_status = StringVar()
        self.whapa_box_value = StringVar()
        self.whapa_user = StringVar()
        self.whapa_box_filter = StringVar()
        self.whapa_box_rep = StringVar()
        self.whachat_box_rep = StringVar()
        self.whachat_box_os = StringVar()
        self.whapa_text = StringVar(value="0")
        self.whapa_ts = StringVar(value="0")
        self.whapa_te = StringVar(value="0")
        self.whapa_w = StringVar(value="0")
        self.whapa_s = StringVar(value="0")
        self.whapa_b = StringVar(value="0")

        if system == "Linux":
            self.whamerge_path = StringVar(value=os.getcwd() + "/")
            self.whagodri_path = StringVar(value=os.getcwd() + "/")
            self.whacloud_path = StringVar(value=os.getcwd() + "/")
            self.whacipher_path = StringVar(value=os.getcwd() + "/")
            self.whapa_out = StringVar(value=os.getcwd() + "/report/")
            self.whamerge_file = StringVar(value=os.getcwd() + "/msgstore_merge.db")
            self.whacipher_file = StringVar(value=os.getcwd() + "/msgstore.db.crypt14")
            self.whacipher_key = StringVar(value=os.getcwd() + "/key")
            self.whachat_file = StringVar(value=os.getcwd() + "/chat.txt")
            self.whacipher_out = StringVar(value=os.getcwd() + "/msgstore.db")
            self.whacipher_out_en = StringVar(value=os.getcwd() + "/msgstore.db.crypt14")
            self.whacipher_file_en = StringVar(value=os.getcwd() + "/msgstore.db")
            self.whacipher_crypt_en = StringVar(value=os.getcwd() + "/msgstore.db.crypt14")
            self.whacipher_key_en = StringVar(value=os.getcwd() + "/key")
            self.whapa_file = StringVar(value=os.getcwd() + "/msgstore.db")
            self.whapa_wa = StringVar(value=os.getcwd() + "/wa.db")

        else:
            self.whamerge_path = StringVar(value=os.getcwd() + "\\")
            self.whagodri_path = StringVar(value=os.getcwd() + "\\")
            self.whacloud_path = StringVar(value=os.getcwd() + "\\")
            self.whacipher_path = StringVar(value=os.getcwd() + "\\")
            self.whapa_out = StringVar(value=os.getcwd() + "\\report\\")
            self.whamerge_file = StringVar(value=os.getcwd() + r"\msgstore_merge.db")
            self.whacipher_file = StringVar(value=os.getcwd() + r"\msgstore.db.crypt14")
            self.whacipher_key = StringVar(value=os.getcwd() + r"\key")
            self.whachat_file = StringVar(value=os.getcwd() + "\\chat.txt")
            self.whacipher_out = StringVar(value=os.getcwd() + r"\msgstore.db")
            self.whacipher_out_en = StringVar(value=os.getcwd() + r"\msgstore.db.crypt14")
            self.whacipher_file_en = StringVar(value=os.getcwd() + r"\msgstore.db")
            self.whacipher_crypt_en = StringVar(value=os.getcwd() + r"\msgstore.db.crypt14")
            self.whacipher_key_en = StringVar(value=os.getcwd() + r"\key")
            self.whapa_file = StringVar(value=os.getcwd() + r"\msgstore.db")
            self.whapa_wa = StringVar(value=os.getcwd() + r"\wa.db")

        self.instructions_wachat = StringVar(value="""To export chats on an Android phone, here are the steps:
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
        """)

        # Toolbar
        self.toolbar = Frame(self.root, relief=RAISED, bd=2)
        self.toolbar.grid(row=0, sticky="ew", columnspan=5)
        self.toolbar_but1 = Button(self.toolbar, image=self.iconsearh, command=self.open_folder)
        self.toolbar_but1.grid(row=0, column=0)
        ToolTip(self.toolbar_but1, "Open Folder")
        self.toolbar_but2 = Button(self.toolbar, image=self.iconreport, command=self.report)
        self.toolbar_but2.grid(row=0, column=1)
        ToolTip(self.toolbar_but2, "Open Report")
        self.toolbar_but3 = Button(self.toolbar, image=self.iconsetting, command=self.api)
        self.toolbar_but3.grid(row=0, column=2)
        ToolTip(self.toolbar_but3, "Configuration")
        self.toolbar_but4 = Button(self.toolbar, image=self.iconmanual, command=self.manual)
        self.toolbar_but4.grid(row=0, column=3)
        ToolTip(self.toolbar_but4, "Readme")
        self.toolbar_but5 = Button(self.toolbar, image=self.iconrequire, command=self.requirements)
        self.toolbar_but5.grid(row=0, column=4)
        ToolTip(self.toolbar_but5, "Install requirements")
        self.toolbar_but6 = Button(self.toolbar, image=self.iconupdate, command=self.update)
        self.toolbar_but6.grid(row=0, column=5)
        ToolTip(self.toolbar_but6, "Update")
        self.toolbar_but7 = Button(self.toolbar, image=self.iconabout, command=self.about)
        self.toolbar_but7.grid(row=0, column=6)
        ToolTip(self.toolbar_but7, "About")
        self.toolbar_but8 = Button(self.toolbar, image=self.iconexit, command=self.exit)
        self.toolbar_but8.grid(row=0, column=7)
        ToolTip(self.toolbar_but8, "Exit")

        # Top
        #self.label_bg = Label(self.root, image=self.iconbg, bg="#A0A0A0", font=("times", "8", "normal"))
        #self.label_bg.grid(row=1, padx=5, pady=5)

        # Main Frame
        self.frame_main = Frame(self.root)
        self.frame_main.grid(row=1, sticky="ewn")

        # Tab Panel
        self.note = ttk.Notebook(self.root)
        self.tab1 = Frame(self.note)
        self.tab2 = Frame(self.note)
        self.tab3 = Frame(self.note)
        self.tab4 = Frame(self.note)
        self.tab5 = Frame(self.note)
        self.tab6 = Frame(self.note)
        self.note.add(self.tab1, text="WhaPa", image=self.icontabwhapa, compound='left', padding=0)
        self.note.add(self.tab2, text="WhaCipher", image=self.icontabcipher, compound='left', padding=0)
        self.note.add(self.tab3, text="WhaMerge", image=self.icontabmerge, compound='left', padding=0)
        self.note.add(self.tab4, text="WhaGoDri", image=self.icontabdrive, compound='left', padding=0)
        self.note.add(self.tab5, text="WhaChat", image=self.icontabwhachat, compound='left', padding=0)
        self.note.add(self.tab6, text="WhaCloud", image=self.icontabwhacloud, compound='left', padding=0)
        self.note.grid(row=2, padx=10, pady=0, sticky="nwes")

        # Tab 1 Whapa
        self.label_whapa = Label(self.tab1, text="Whatsapp Parser", font=('courier', 15, 'bold'))
        self.label_whapa.grid(row=0, column=0, sticky="we", padx=5, pady=5, columnspan=2)

        self.frame_whapa_db = LabelFrame(self.tab1, text="Database")
        self.frame_whapa_db.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.label_whapa_file = Label(self.frame_whapa_db, text="Database file")
        self.label_whapa_file.grid(row=0, column=0, sticky="we", padx=5, pady=15)
        self.entry_whapa_file = Entry(self.frame_whapa_db, textvariable=self.whapa_file, width=70)
        self.entry_whapa_file.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        self.buttonwhapa_file = Button(self.frame_whapa_db, image=self.iconfile, command=self.search_whapa_file, borderwidth=0, highlightthickness=0)
        self.buttonwhapa_file.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.buttonwhapa_file, "Database file to parser")

        self.label_whapa_wa = Label(self.frame_whapa_db, text="WA file")
        self.label_whapa_wa.grid(row=1, column=0, sticky="we", padx=5, pady=5, columnspan=1)
        self.entry_whapa_wa = Entry(self.frame_whapa_db, textvariable=self.whapa_wa, width=70)
        self.entry_whapa_wa.grid(row=1, column=1, sticky="we", padx=5, pady=5, columnspan=1)
        self.button_whapa_wa = Button(self.frame_whapa_db, image=self.iconfile, command=self.search_whapa_wa, borderwidth=0, highlightthickness=0)
        self.button_whapa_wa.grid(row=1, column=2, sticky="w", padx=5, pady=5, columnspan=1)
        ToolTip(self.button_whapa_wa, "Wa file, optionally to get names")

        self.label_whapa_out = Label(self.frame_whapa_db, text="Output path")
        self.label_whapa_out.grid(row=2, column=0, sticky="we", padx=5, pady=15, columnspan=1)
        self.entry_whapa_out = Entry(self.frame_whapa_db, textvariable=self.whapa_out, width=70)
        self.entry_whapa_out.grid(row=2, column=1, sticky="we", padx=5, pady=5, columnspan=1)
        self.button_whapa_out = Button(self.frame_whapa_db, image=self.iconfile, command=self.search_whapa_out, borderwidth=0, highlightthickness=0)
        self.button_whapa_out.grid(row=2, column=2, sticky="w", padx=5, pady=5, columnspan=1)
        ToolTip(self.button_whapa_out, "Output path to save the information")

        self.frame_whapa_repo = LabelFrame(self.tab1, text="Report")
        self.frame_whapa_repo.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.whapa_but_rep_none = Radiobutton(self.frame_whapa_repo, text='  Terminal', image=self.iconone, variable=self.whapa_box_rep, value='None', anchor="w", compound='left')
        self.whapa_but_rep_none.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_rep_none.grid(row=0, column=0, padx=5, pady=(15,5), sticky="nswe")
        self.whapa_but_rep_es = Radiobutton(self.frame_whapa_repo, text='  Spanish', image=self.icones, variable=self.whapa_box_rep, value='ES', anchor="w", compound='left')
        self.whapa_but_rep_es.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_rep_es.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.whapa_but_rep_en = Radiobutton(self.frame_whapa_repo, text='  English', image=self.iconen, variable=self.whapa_box_rep, value='EN', anchor="w", compound='left')
        self.whapa_but_rep_en.config(bd=4, borderwidth=0, highlightthickness=0,)
        self.whapa_but_rep_en.grid(row=2, column=0, padx=5, pady=5, sticky="nswe")
        self.whapa_box_rep.set("None")

        self.frame_whapa_filter = LabelFrame(self.tab1, text="Filters")
        self.frame_whapa_filter.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        self.check_whapa_text = Checkbutton(self.frame_whapa_filter, text="Text", borderwidth=0, highlightthickness=0, variable=self.whapa_text)
        self.check_whapa_text.grid(row=0, column=0, sticky="w", padx=5, pady=5)
        self.entry_whapa_text = Entry(self.frame_whapa_filter, width=20)
        self.entry_whapa_text.grid(row=0, column=1, sticky="we", padx=5, pady=5, columnspan=1)
        self.check_whapa_ts = Checkbutton(self.frame_whapa_filter, text="Start time", borderwidth=0, highlightthickness=0, variable=self.whapa_ts)
        self.check_whapa_ts.grid(row=1, column=0, sticky="w", padx=5, pady=5)
        self.entry_whapa_ts = Entry(self.frame_whapa_filter, width=20)
        self.entry_whapa_ts.grid(row=1, column=1, sticky="we", padx=5, pady=5, columnspan=1)
        self.check_whapa_te = Checkbutton(self.frame_whapa_filter, text="End time", borderwidth=0, highlightthickness=0, variable=self.whapa_te)
        self.check_whapa_te.grid(row=2, column=0, sticky="w", padx=5, pady=5)
        self.entry_whapa_te = Entry(self.frame_whapa_filter, width=20)
        self.entry_whapa_te.grid(row=2, column=1, sticky="we", padx=5, pady=5, columnspan=1)
        self.check_whapa_w = Checkbutton(self.frame_whapa_filter, text="Whatsapp web", borderwidth=0, highlightthickness=0, variable=self.whapa_w)
        self.check_whapa_w.grid(row=3, column=0, sticky="w", padx=5, pady=5)
        self.check_whapa_s = Checkbutton(self.frame_whapa_filter, text="Starred", borderwidth=0, highlightthickness=0, variable=self.whapa_s)
        self.check_whapa_s.grid(row=4, column=0, sticky="w", padx=5, pady=5)
        self.check_whapa_b = Checkbutton(self.frame_whapa_filter, text="Broadcast", borderwidth=0, highlightthickness=0, variable=self.whapa_b)
        self.check_whapa_b.grid(row=5, column=0, sticky="w", padx=5, pady=5)
        self.whapa_but_allme = Radiobutton(self.frame_whapa_filter, text='All', variable=self.whapa_box_filter, value='All', anchor="w", compound='left')
        self.whapa_but_allme.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_allme.grid(row=0, column=2, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tt = Radiobutton(self.frame_whapa_filter, text='Texts', variable=self.whapa_box_filter, value='Text', anchor="w", compound='left')
        self.whapa_but_tt.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tt.grid(row=1, column=2, padx=5, pady=5, sticky="nswe")
        self.whapa_but_ti = Radiobutton(self.frame_whapa_filter, text='Images', variable=self.whapa_box_filter, value='Images', anchor="w", compound='left')
        self.whapa_but_ti.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_ti.grid(row=2, column=2, padx=5, pady=5, sticky="nswe")
        self.whapa_but_ta = Radiobutton(self.frame_whapa_filter, text='Audios', variable=self.whapa_box_filter, value='Audios', anchor="w", compound='left')
        self.whapa_but_ta.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_ta.grid(row=3, column=2, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tv = Radiobutton(self.frame_whapa_filter, text='Videos', variable=self.whapa_box_filter, value='Videos', anchor="w", compound='left')
        self.whapa_but_tv.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tv.grid(row=4, column=2, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tc = Radiobutton(self.frame_whapa_filter, text='Contacts', variable=self.whapa_box_filter, value='Contacts', anchor="w", compound='left')
        self.whapa_but_tc.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tc.grid(row=5, column=2, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tl = Radiobutton(self.frame_whapa_filter, text='Locations', variable=self.whapa_box_filter, value='Locations', anchor="w", compound='left')
        self.whapa_but_tl.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tl.grid(row=0, column=3, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tx = Radiobutton(self.frame_whapa_filter, text='Calls', variable=self.whapa_box_filter, value='Calls', anchor="w", compound='left')
        self.whapa_but_tx.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tx.grid(row=1, column=3, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tp = Radiobutton(self.frame_whapa_filter, text='Applications', variable=self.whapa_box_filter, value='Applications', anchor="w", compound='left')
        self.whapa_but_tp.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tp.grid(row=2, column=3, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tg = Radiobutton(self.frame_whapa_filter, text='GIFs', variable=self.whapa_box_filter, value='GIFs', anchor="w", compound='left')
        self.whapa_but_tg.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tg.grid(row=3, column=3, padx=5, pady=5, sticky="nswe")
        self.whapa_but_td = Radiobutton(self.frame_whapa_filter, text='Deleted objects', variable=self.whapa_box_filter, value='Deleted', anchor="w", compound='left')
        self.whapa_but_td.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_td.grid(row=4, column=3, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tr = Radiobutton(self.frame_whapa_filter, text='Realtime Locations', variable=self.whapa_box_filter, value='Realtime', anchor="w", compound='left')
        self.whapa_but_tr.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tr.grid(row=5, column=3, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tk = Radiobutton(self.frame_whapa_filter, text='Stickers', variable=self.whapa_box_filter, value='Stickers', anchor="w", compound='left')
        self.whapa_but_tk.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tk.grid(row=0, column=4, padx=5, pady=5, sticky="nswe")
        self.whapa_but_tm = Radiobutton(self.frame_whapa_filter, text='System', variable=self.whapa_box_filter, value='System', anchor="w", compound='left')
        self.whapa_but_tm.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_tm.grid(row=1, column=4, padx=5, pady=5, sticky="nswe")
        self.whapa_box_filter.set("All")

        self.frame_whapa_recip = LabelFrame(self.tab1, text="Recipients")
        self.frame_whapa_recip.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        self.whapa_but_all = Radiobutton(self.frame_whapa_recip, text='All', variable=self.whapa_box_value, value='All', anchor="w", compound='left')
        self.whapa_but_all.config(bd=4, borderwidth=0, highlightthickness=0)
        ToolTip(self.whapa_but_all, "All chats")
        self.whapa_but_all.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")
        self.whapa_but_group = Radiobutton(self.frame_whapa_recip, text='Group or Broadcast', variable=self.whapa_box_value, value='Group', anchor="w", compound='left')
        self.whapa_but_group.config(bd=4, borderwidth=0, highlightthickness=0)
        ToolTip(self.whapa_but_group, "All messages in a group or broadcast")
        self.whapa_but_group.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.whapa_but_user = Radiobutton(self.frame_whapa_recip, text='Chat', variable=self.whapa_box_value, value='User', anchor="w", compound='left')
        self.whapa_but_user.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_user.grid(row=2, column=0, padx=5, pady=5, sticky="nswe")
        ToolTip(self.whapa_but_user, "Chat with the user")
        self.whapa_but_user_all = Radiobutton(self.frame_whapa_recip, text='User', variable=self.whapa_box_value, value='User_all', anchor="w", compound='left')
        self.whapa_but_user_all.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whapa_but_user_all.grid(row=3, column=0, padx=5, pady=5, sticky="nswe")
        ToolTip(self.whapa_but_user_all, "All messages where the user participates individually or in groups.\nCreating reports with this option may not make sense")
        self.whapa_box_value.set("All")
        self.entry_whapa_user = Entry(self.frame_whapa_recip, textvariable=self.whapa_user, width=33)
        self.entry_whapa_user.grid(row=4, column=0, sticky="we", padx=5, pady=5)
        self.button_whapa_extract = Button(self.frame_whapa_recip, image=self.iconinfowhagodri, command=self.whapa_info, height=32, width=64)
        self.button_whapa_extract.grid(row=5, column=0, padx=5, pady=5)
        ToolTip(self.button_whapa_extract, "Actives Chat list")

        self.frame_whapa_info = LabelFrame(self.tab1, text="Options")
        self.frame_whapa_info.grid(row=3, column=0, padx=5, pady=5, sticky="we", columnspan="2")

        self.label_whapa_sep = Label(self.frame_whapa_info, width=25)
        self.label_whapa_sep.grid(row=0, column=0, padx=5, pady=5)
        self.button_whapa_parser = Button(self.frame_whapa_info, image=self.iconparser, command=self.whapa_messages, height=32, width=64)
        self.button_whapa_parser.grid(row=0, column=1, padx=5, pady=5)
        ToolTip(self.button_whapa_parser, "Parser database")
        self.button_whapa_extract = Button(self.frame_whapa_info, image=self.iconstatus, command=self.whapa_status, height=32, width=64)
        self.button_whapa_extract.grid(row=0, column=2, padx=5, pady=5)
        ToolTip(self.button_whapa_extract, "Status")
        self.button_whapa_extract = Button(self.frame_whapa_info, image=self.iconcall, command=self.whapa_call, height=32, width=64)
        self.button_whapa_extract.grid(row=0, column=3, padx=5, pady=5)
        ToolTip(self.button_whapa_extract, "Calls log")
        self.button_whapa_extract = Button(self.frame_whapa_info, image=self.iconextract, command=self.whapa_extract, height=32, width=64)
        self.button_whapa_extract.grid(row=0, column=4, padx=5, pady=5)
        ToolTip(self.button_whapa_extract, "Extract Thumbnails")
        self.button_whapa_carv = Button(self.frame_whapa_info, image=self.iconcarving, command=self.whapa_carving, height=32, width=64)
        self.button_whapa_carv.grid(row=0, column=5, padx=5, pady=5)
        ToolTip(self.button_whapa_carv, "Database Carving")


        # Tab 2 Whacipher
        self.label_whacipher = Label(self.tab2, text="Whatsapp Encryption and Decryption", font=('courier', 15, 'bold'))
        self.label_whacipher.grid(row=0, column=0, sticky="we", padx=5, pady=5, columnspan=2)

        self.notewhacipher = ttk.Notebook(self.tab2)
        self.tabwhacipher1 = Frame(self.notewhacipher)
        self.tabwhacipher2 = Frame(self.notewhacipher)
        self.notewhacipher.add(self.tabwhacipher1, text="Decrypt", compound='left', padding=0)
        self.notewhacipher.add(self.tabwhacipher2, text="Encrypt", compound='left', padding=0)
        self.notewhacipher.grid(row=1, padx=5, pady=5, sticky="we")

            # Decrypt
        self.whacipher_but_file = Radiobutton(self.tabwhacipher1, text='File', variable=self.whacipher_box_value, value='File', anchor="w", compound='left', command=self.estate_assets_whacipher)
        self.whacipher_but_file.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whacipher_but_file.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")
        self.entry_whacipher_file = Entry(self.tabwhacipher1, textvariable=self.whacipher_file, width=100)
        self.entry_whacipher_file.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        self.button_whacipher_file = Button(self.tabwhacipher1, image=self.iconfile, command=self.search_file_whacypher, borderwidth=0, highlightthickness=0)
        self.button_whacipher_file.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.button_whacipher_file, "Database file to decrypt")

        self.whacipher_but_path = Radiobutton(self.tabwhacipher1, text='Path', variable=self.whacipher_box_value, value='Path', anchor="w", compound='left', command=self.estate_assets_whacipher)
        self.whacipher_but_path.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whacipher_but_path.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.entry_whacipher_path = Entry(self.tabwhacipher1, textvariable=self.whacipher_path, width=100)
        self.entry_whacipher_path.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        self.button_whacipher_path = Button(self.tabwhacipher1, image=self.iconfile, command=self.search_path_whacypher, borderwidth=0, highlightthickness=0)
        self.button_whacipher_path.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.button_whacipher_path, "Database Path to decrypt")

        self.whacipher_box_value.set('File')
        self.label_cipher_key = Label(self.tabwhacipher1, text="Key")
        self.label_cipher_key.grid(row=2, column=0, sticky="we", padx=5, pady=5)
        self.entry_whacipher_key = Entry(self.tabwhacipher1, textvariable=self.whacipher_key, width=100)
        self.entry_whacipher_key.grid(row=2, column=1, sticky="we", padx=5, pady=5)
        self.button_whacipher_key = Button(self.tabwhacipher1, image=self.iconfile, command=self.search_key_whacypher, borderwidth=0, highlightthickness=0)
        self.button_whacipher_key.grid(row=2, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.button_whacipher_key, "Encryption Key")

        self.label_cipher_out = Label(self.tabwhacipher1, text="Output")
        self.label_cipher_out.grid(row=3, column=0, sticky="we", padx=5, pady=5)
        self.entry_whacipher_out = Entry(self.tabwhacipher1, textvariable=self.whacipher_out, width=100)
        self.entry_whacipher_out.grid(row=3, column=1, sticky="we", padx=5, pady=5)
        self.button_whacipher_out = Button(self.tabwhacipher1, image=self.iconfile, command=self.search_out_whacypher, borderwidth=0, highlightthickness=0)
        self.button_whacipher_out.grid(row=3, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.button_whacipher_out, "Output file")

        self.button_whacipher = Button(self.tabwhacipher1, image=self.icondecrypt, command=self.decrypt_whacypher, height=32, width=64)
        self.button_whacipher.grid(row=4, column=0, padx=10, pady=10, columnspan=2)
        ToolTip(self.button_whacipher, "Decrypt")

        # Encrypt
        self.label_cipher_key_en = Label(self.tabwhacipher2, text="File")
        self.label_cipher_key_en.grid(row=0, column=0, sticky="we", padx=5, pady=5)
        self.entry_whacipher_file_en = Entry(self.tabwhacipher2, textvariable=self.whacipher_file_en, width=100)
        self.entry_whacipher_file_en.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        self.button_whacipher_file_en = Button(self.tabwhacipher2, image=self.iconfile, command=self.search_file_whacypher_en, borderwidth=0, highlightthickness=0)
        self.button_whacipher_file_en.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.button_whacipher_file_en, "File to encrypt")

        self.label_cipher_key_en = Label(self.tabwhacipher2, text="Crypto")
        self.label_cipher_key_en.grid(row=1, column=0, sticky="we", padx=5, pady=5)
        self.entry_whacipher_path_en = Entry(self.tabwhacipher2, textvariable=self.whacipher_crypt_en, width=100)
        self.entry_whacipher_path_en.grid(row=1, column=1, sticky="we", padx=5, pady=5)
        self.button_whacipher_path_en = Button(self.tabwhacipher2, image=self.iconfile, command=self.search_criptofile_whacypher_en, borderwidth=0, highlightthickness=0)
        self.button_whacipher_path_en.grid(row=1, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.button_whacipher_path_en, "Cryptofile to copy the header")

        self.label_cipher_key_en = Label(self.tabwhacipher2, text="Key")
        self.label_cipher_key_en.grid(row=2, column=0, sticky="we", padx=5, pady=5)
        self.entry_whacipher_key_en = Entry(self.tabwhacipher2, textvariable=self.whacipher_key_en, width=100)
        self.entry_whacipher_key_en.grid(row=2, column=1, sticky="we", padx=5, pady=5)
        self.button_whacipher_key_en = Button(self.tabwhacipher2, image=self.iconfile, command=self.search_key_whacypher_en, borderwidth=0, highlightthickness=0)
        self.button_whacipher_key_en.grid(row=2, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.button_whacipher_key_en, "Encryption Key")

        self.label_cipher_out_en = Label(self.tabwhacipher2, text="Output")
        self.label_cipher_out_en.grid(row=3, column=0, sticky="we", padx=5, pady=5)
        self.entry_whacipher_out_en = Entry(self.tabwhacipher2, textvariable=self.whacipher_out_en, width=100)
        self.entry_whacipher_out_en.grid(row=3, column=1, sticky="we", padx=5, pady=5)
        self.button_whacipher_out_en = Button(self.tabwhacipher2, image=self.iconfile, command=self.search_out_whacypher_en, borderwidth=0, highlightthickness=0)
        self.button_whacipher_out_en.grid(row=3, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.button_whacipher_out_en, "Output File")

        self.button_whacipher_en = Button(self.tabwhacipher2, image=self.iconencrypt, command=self.encrypt_whacypher,  height=32, width=64)
        self.button_whacipher_en.grid(row=4, column=0, padx=10, pady=10, columnspan=2)
        ToolTip(self.button_whacipher_en, "Encrypt")

        # Tab 3 Whamerge
        self.label_whamerge = Label(self.tab3, text="Whatsapp Merger", font=('courier', 15, 'bold'))
        self.label_whamerge.grid(row=0, column=0, padx=5, pady=5, columnspan=5)
        self.frame_whamerge = LabelFrame(self.tab3)
        self.frame_whamerge.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.label_whamerge = Label(self.frame_whamerge, text="Path")
        self.label_whamerge.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.entry_whamerge = Entry(self.frame_whamerge, textvariable=self.whamerge_path, width=115)
        self.entry_whamerge.grid(row=1, column=0, sticky="we", padx=5, pady=5,)
        self.button_whamerge_file = Button(self.frame_whamerge, image=self.iconfile, command=self.search_path_whamerge, borderwidth=0, highlightthickness=0)
        self.button_whamerge_file.grid(row=1, column=1, sticky="w", padx=5, pady=5,)
        ToolTip(self.button_whamerge_file, "Database path to merge")

        self.label_whamerge_out = Label(self.frame_whamerge, text="Output")
        self.label_whamerge_out.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.entry_whamerge_out = Entry(self.frame_whamerge, textvariable=self.whamerge_file, width=115)
        self.entry_whamerge_out.grid(row=3, column=0, sticky="we", padx=5, pady=5,)
        self.button_whamerge_fileout = Button(self.frame_whamerge, image=self.iconfile, command=self.search_file_whamerge, borderwidth=0, highlightthickness=0)
        self.button_whamerge_fileout.grid(row=3, column=1, sticky="w", padx=5, pady=5,)
        ToolTip(self.button_whamerge_fileout, "Database output file")

        self.button_whamerge_run = Button(self.frame_whamerge, image=self.iconmerge, command=self.whamerge, height=32, width=64)
        self.button_whamerge_run.grid(row=4, column=0, padx=5, pady=15)
        ToolTip(self.button_whamerge_run, "Click to merge")

        self.label_box_whamerge_info = Label(self.tab3, image=self.iconabout)
        self.label_box_whamerge_info.grid(row=0, column=3, padx=5, pady=5)
        ToolTip(self.label_box_whamerge_info, "The generated file is for analysis purposes, not for restoring on the phone,\n due to the fact that many tables have been omitted.")

        # Tab 4 Whagodri
        self.label_wagodri = Label(self.tab4, text="Whatsapp Google Drive Extractor", font=('courier', 15, 'bold'))
        self.label_wagodri.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        self.frame_whagodri = LabelFrame(self.tab4, text="Information")
        self.frame_whagodri.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        self.wagodri_but_info = Radiobutton(self.frame_whagodri, text='Info about account', variable=self.wagodri_box_value,  value='Info', anchor="w", compound='left')
        self.wagodri_but_info.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_but_info.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")
        self.wagodri_but_list = Radiobutton(self.frame_whagodri, text='List all files', variable=self.wagodri_box_value, value='List', anchor="w", compound='left')
        self.wagodri_but_list.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_but_list.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.wagodri_but_listw = Radiobutton(self.frame_whagodri, text='List Whatsapp database file', variable=self.wagodri_box_value, value='ListW', anchor="w", compound='left')
        self.wagodri_but_listw.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_but_listw.grid(row=2, column=0, padx=5, pady=5, sticky="nswe")
        self.wagodri_box_value.set('Info')

        self.frame_method_whagodri = LabelFrame(self.tab4, text="Download")
        self.frame_method_whagodri.grid(row=1, column=1, padx=5, pady=5, sticky="nsw")

        self.wagodri_sync = Radiobutton(self.frame_method_whagodri, text='All', variable=self.wagodri_box_value, value='All', anchor="w", compound='left')
        self.wagodri_sync.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_sync.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")
        self.wagodri_si = Radiobutton(self.frame_method_whagodri, text='Images', variable=self.wagodri_box_value, value='Images', anchor="w", compound='left')
        self.wagodri_si.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_si.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.wagodri_vi = Radiobutton(self.frame_method_whagodri, text='Videos', variable=self.wagodri_box_value, value='Videos', anchor="w", compound='left')
        self.wagodri_vi.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_vi.grid(row=2, column=0, padx=5, pady=5, sticky="nswe")
        self.wagodri_au = Radiobutton(self.frame_method_whagodri, text='Audios', variable=self.wagodri_box_value, value='Audios', anchor="w", compound='left')
        self.wagodri_au.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_au.grid(row=3, column=0, padx=5, pady=5, sticky="nswe")
        self.wagodri_sx = Radiobutton(self.frame_method_whagodri, text='Documents', variable=self.wagodri_box_value, value='Documents', anchor="w", compound='left')
        self.wagodri_sx.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_sx.grid(row=4, column=0, padx=5, pady=5, sticky="nswe")
        self.wagodri_db = Radiobutton(self.frame_method_whagodri, text='Databases', variable=self.wagodri_box_value, value='Databases', anchor="w", compound='left')
        self.wagodri_db.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_db.grid(row=5, column=0, padx=5, pady=5, sticky="nswe")
        self.wagodri_file = Radiobutton(self.frame_method_whagodri, text='File', variable=self.wagodri_box_value, value='File', anchor="w", compound='left')
        self.wagodri_file.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wagodri_file.grid(row=6, column=0, padx=5, pady=5, sticky="nswe")
        self.entry_whagodri_down = Entry(self.frame_method_whagodri, width=70)
        self.entry_whagodri_down.grid(row=6, column=1, sticky="w", pady=5, padx=5)

        self.frame_whagodri_out = LabelFrame(self.tab4, text="Output path")
        self.frame_whagodri_out.grid(row=2, column=0, padx=5, pady=10, sticky="nsew", columnspan=2)
        self.entry_whagodri_output = Entry(self.frame_whagodri_out, textvariable=self.whagodri_path, width=110)
        self.entry_whagodri_output.grid(row=0, column=0, sticky="we", padx=5, pady=5 )
        self.whagodri_button_path = Button(self.frame_whagodri_out, image=self.iconfile, command=self.search_path_whagodri, borderwidth=0, highlightthickness=0)
        self.whagodri_button_path.grid(row=0, column=1, sticky="w", padx=5, pady=5,)
        ToolTip(self.whagodri_button_path, "Output path to save files")

        self.button_whagodri_exec = Button(self.frame_whagodri_out, image=self.icondownwhagodri, command=self.wagodri_down, height=32, width=64)
        self.button_whagodri_exec.grid(row=1, column=0, columnspan=2, padx=185, pady=10)

        self.label_box_whagodri_info = Label(self.tab4, image=self.iconabout)
        self.label_box_whagodri_info.grid(row=0, column=3, padx=5, pady=5)
        ToolTip(self.label_box_whagodri_info, "1. Install the requirements.\n2. Edit the values of the ./cfg/settings.cfg file.\n    [google-auth]\n        gmail = alias@gmail.com\n        passw = yourpassword\n3. Click here, https://accounts.google.com/DisplayUnlockCaptcha.\n    Log into your browser and then allow access to your Google account.")

        # Tab 5 WhaChat
        self.label_wachat = Label(self.tab5, text="Whatsapp Chat Exporter", font=('courier', 15, 'bold'))
        self.label_wachat.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        self.label_box_whachat_info = Label(self.tab5, image=self.iconabout)
        self.label_box_whachat_info.grid(row=0, column=3, padx=5, pady=5)
        ToolTip(self.label_box_whachat_info,self.instructions_wachat.get())
        self.frame_whachat = LabelFrame(self.tab5, text="Chat")
        self.frame_whachat.grid(row=1, column=0, padx=5, pady=5, rowspan=2, sticky="nsew")
        self.label_whachat_file = Label(self.frame_whachat, text="Chat file")
        self.label_whachat_file.grid(row=0, column=0, sticky="we", padx=5, pady=(15,5))
        self.entry_whachat_output = Entry(self.frame_whachat, textvariable=self.whachat_file, width=70)
        self.entry_whachat_output.grid(row=0, column=1, sticky="we", padx=5, pady=5)
        self.whachat_button_path = Button(self.frame_whachat, image=self.iconfile, command=self.search_file_whachat, borderwidth=0, highlightthickness=0)
        self.whachat_button_path.grid(row=0, column=2, sticky="w", padx=5, pady=5)
        ToolTip(self.whachat_button_path, "Chat file to parser")
        self.label_whachat_user = Label(self.frame_whachat, text="Recipient")
        self.label_whachat_user.grid(row=1, column=0, sticky="we", padx=5, pady=5)
        self.combo_whachat_user = ttk.Combobox(self.frame_whachat, width=50, state="readonly")
        self.combo_whachat_user.grid(row=1, column=1, sticky="w", padx=5, pady=5)
        self.label_whachat_user = Label(self.frame_whachat, text="Start time")
        self.label_whachat_user.grid(row=2, column=0, sticky="we", padx=5, pady=5)
        self.entry_whachat_ts = Entry(self.frame_whachat, width=20)
        self.entry_whachat_ts.grid(row=2, column=1, sticky="w", padx=5, pady=5, columnspan=1)
        self.label_whachat_user = Label(self.frame_whachat, text="End time")
        self.label_whachat_user.grid(row=3, column=0, sticky="we", padx=5, pady=5)
        self.entry_whachat_te = Entry(self.frame_whachat, width=20)
        self.entry_whachat_te.grid(row=3, column=1, sticky="w", padx=5, pady=5, columnspan=1)

        self.frame_whacha_repo = LabelFrame(self.tab5, text="Report")
        self.frame_whacha_repo.grid(row=1, column=1, padx=5, pady=5, sticky="nsew")
        self.whacha_but_rep_none = Radiobutton(self.frame_whacha_repo, text='  Terminal', image=self.iconone, variable=self.whachat_box_rep, value='None', anchor="w", compound='left')
        self.whacha_but_rep_none.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whacha_but_rep_none.grid(row=0, column=0, padx=5, pady=(15,5), sticky="nswe")
        self.whacha_but_rep_es = Radiobutton(self.frame_whacha_repo, text='  Spanish', image=self.icones, variable=self.whachat_box_rep, value='ES', anchor="w", compound='left')
        self.whacha_but_rep_es.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whacha_but_rep_es.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.whacha_but_rep_en = Radiobutton(self.frame_whacha_repo, text='  English', image=self.iconen, variable=self.whachat_box_rep, value='EN', anchor="w", compound='left')
        self.whacha_but_rep_en.config(bd=4, borderwidth=0, highlightthickness=0,)
        self.whacha_but_rep_en.grid(row=2, column=0, padx=5, pady=5, sticky="nswe")
        self.whachat_box_rep.set("None")

        self.frame_whacha_os = LabelFrame(self.tab5, text="Operating System")
        self.frame_whacha_os.grid(row=2, column=1, padx=5, pady=5, sticky="nsew")
        self.whacha_but_rep_es = Radiobutton(self.frame_whacha_os, text='  Android', image=self.iconandroid, variable=self.whachat_box_os, value='android', anchor="w", compound='left', command=self.estate_assets_whachat)
        self.whacha_but_rep_es.config(bd=4, borderwidth=0, highlightthickness=0)
        self.whacha_but_rep_es.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")
        self.whacha_but_rep_en = Radiobutton(self.frame_whacha_os, text='  iOS', image=self.iconios, variable=self.whachat_box_os, value='ios', anchor="w", compound='left', command=self.estate_assets_whachat)
        self.whacha_but_rep_en.config(bd=4, borderwidth=0, highlightthickness=0,)
        self.whacha_but_rep_en.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.whachat_box_os.set("android")

        self.label_whachat_format = Label(self.frame_whachat, text="Time format")
        self.label_whachat_format.grid(row=4, column=0, sticky="we", padx=5, pady=5)
        self.combo_whachat_format = ttk.Combobox(self.frame_whachat, width=25, state="readonly")
        self.combo_whachat_format["values"] = ["%d/%m/%y %H:%M:%S", "%d/%m/%Y %H:%M:%S", "%d/%m/%y %H:%M", "%d/%m/%Y %H:%M",
                                               "%m/%d/%y %H:%M:%S", "%m/%d/%Y %H:%M:%S", "%m/%d/%y %H:%M", "%m/%d/%Y %H:%M"]
        self.combo_whachat_format.current(2)
        self.combo_whachat_format.grid(row=4, column=1, sticky="w", padx=5, pady=5)

        self.button_whachat_exec = Button(self.frame_whachat, image=self.iconparser, command=self.whachat_run, height=32, width=64)
        self.button_whachat_exec.grid(row=5, column=1, columnspan=2, padx=185, pady=10)

        # Tab 5 WhaCloud
        self.label_wacloud = Label(self.tab6, text="Whatsapp ICloud Extractor", font=('courier', 15, 'bold'))
        self.label_wacloud.grid(row=0, column=0, columnspan=2, sticky="we", padx=5, pady=5)

        self.frame_whacloud = LabelFrame(self.tab6, text="Download")
        self.frame_whacloud.grid(row=1, padx=5, pady=5, sticky="nsew", columnspan=3)

        self.wacloud_list = Radiobutton(self.frame_whacloud, text='List all files', variable=self.wacloud_box_value, value='List', anchor="w", compound='left')
        self.wacloud_list.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wacloud_list.grid(row=0, column=0, padx=5, pady=5, sticky="nswe")
        self.wacloud_box_value.set("List")
        self.wacloud_sync = Radiobutton(self.frame_whacloud, text='Sync', variable=self.wacloud_box_value, value='Sync', anchor="w", compound='left')
        self.wacloud_sync.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wacloud_sync.grid(row=1, column=0, padx=5, pady=5, sticky="nswe")
        self.wacloud_img = Radiobutton(self.frame_whacloud, text='Images', variable=self.wacloud_box_value, value='Images', anchor="w", compound='left')
        self.wacloud_img.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wacloud_img.grid(row=2, column=0, padx=5, pady=5, sticky="nswe")
        self.wacloud_vid = Radiobutton(self.frame_whacloud, text='Videos / Audios', variable=self.wacloud_box_value, value='Videos', anchor="w", compound='left')
        self.wacloud_vid.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wacloud_vid.grid(row=3, column=0, padx=5, pady=5, sticky="nswe")
        self.wacloud_file = Radiobutton(self.frame_whacloud, text='File', variable=self.wacloud_box_value, value='File', anchor="w", compound='left')
        self.wacloud_file.config(bd=4, borderwidth=0, highlightthickness=0)
        self.wacloud_file.grid(row=4, column=0, padx=5, pady=5, sticky="nswe")
        self.entry_whacloud_down = Entry(self.frame_whacloud, width=77)
        self.entry_whacloud_down.grid(row=4, column=1, sticky="w", pady=5, padx=5)

        self.frame_whacloud_out = LabelFrame(self.tab6, text="Output path")
        self.frame_whacloud_out.grid(row=2, padx=5, pady=10, sticky="nsew", columnspan=2)

        self.entry_whacloud_output = Entry(self.frame_whacloud_out, textvariable=self.whacloud_path, width=114)
        self.entry_whacloud_output.grid(row=0, column=0, sticky="we", padx=5, pady=(15,5))
        self.whacloud_button_path = Button(self.frame_whacloud_out, image=self.iconfile, command=self.search_path_whacloud, borderwidth=0, highlightthickness=0)
        self.whacloud_button_path.grid(row=0, column=1, sticky="w", padx=5, pady=5,)
        ToolTip(self.whacloud_button_path, "Output path to save files")

        self.button_whacloud_exec = Button(self.frame_whacloud_out, image=self.icondownwhagodri, command=self.wacloud_down, height=32, width=64)
        self.button_whacloud_exec.grid(row=1, column=0, columnspan=2, padx=185, pady=10)


        # Status Bar
        self.label_status.set(time.strftime("%d-%m-%Y %H:%M"))
        self.statusbar = Frame(self.root, bd=1, relief="sunken")
        self.statusbar.grid(sticky="ensw", columnspan=5)
        self.status_bar_label = Label(self.statusbar, text=self.label_status, textvariable=self.label_status,  wraplength=975)
        self.status_bar_label.grid(columnspan=2)

        # Define Shortcut keys
        self.root.bind("<Control-q>", lambda event: self.exit())
        #self.label_bg.bind("<Button-1>", lambda event: webbrowser.open_new_tab("https://github.com/B16f00t/whapa"))
        self.label_box_whagodri_info.bind("<Button-1>", lambda event: webbrowser.open_new_tab("https://accounts.google.com/DisplayUnlockCaptcha"))

        # Run GUI
        self.button_whacipher_path.config(state=DISABLED)
        self.entry_whacipher_path.config(state=DISABLED)
        self.entry_whapa_ts.insert(0, 'dd-mm-yyyy HH:MM')
        self.entry_whapa_ts.bind('<FocusIn>', self.on_entry_click_whapa)
        self.entry_whapa_ts.bind('<FocusOut>', self.on_focusout_whapa)
        self.entry_whapa_ts.config(fg='grey')
        self.entry_whapa_te.insert(0, 'dd-mm-yyyy HH:MM')
        self.entry_whapa_te.bind('<FocusIn>', self.on_entry_click_out_whapa)
        self.entry_whapa_te.bind('<FocusOut>', self.on_focusout_out_whapa)
        self.entry_whapa_te.config(fg='grey')

        self.entry_whachat_ts.insert(0, 'dd-mm-yyyy HH:MM')
        self.entry_whachat_ts.bind('<FocusIn>', self.on_entry_click_whachat)
        self.entry_whachat_ts.bind('<FocusOut>', self.on_focusout_whachat)
        self.entry_whachat_ts.config(fg='grey')
        self.entry_whachat_te.insert(0, 'dd-mm-yyyy HH:MM')
        self.entry_whachat_te.bind('<FocusIn>', self.on_entry_click_out_whachat)
        self.entry_whachat_te.bind('<FocusOut>', self.on_focusout_out_whachat)
        self.entry_whachat_te.config(fg='grey')

        self.root.mainloop()

    def on_entry_click_whapa(self, event):
        """function that gets called whenever entry is clicked"""
        if self.entry_whapa_ts.get() == "dd-mm-yyyy HH:MM":
            self.entry_whapa_ts.delete(0, "end")  # delete all the text in the entry
            self.entry_whapa_ts.insert(0, '')  # Insert blank for user input
            self.entry_whapa_ts.config(fg='black')

    def on_entry_click_out_whapa(self, event):
        """function that gets called whenever entry is clicked"""
        if self.entry_whapa_te.get() == "dd-mm-yyyy HH:MM":
            self.entry_whapa_te.delete(0, "end")  # delete all the text in the entry
            self.entry_whapa_te.insert(0, '')  # Insert blank for user input
            self.entry_whapa_te.config(fg='black')

    def on_focusout_whapa(self, event):
        """Function that's called every time the focus is lost"""
        if self.entry_whapa_ts.get() == '':
            self.entry_whapa_ts.insert(0, "dd-mm-yyyy HH:MM")
            self.entry_whapa_ts.config(fg='grey')

    def on_focusout_out_whapa(self, event):
        """Function that's called every time the focus is lost"""
        if self.entry_whapa_te.get() == '':
            self.entry_whapa_te.insert(0, "dd-mm-yyyy HH:MM")
            self.entry_whapa_te.config(fg='grey')

    def on_entry_click_whachat(self, event):
        """function that gets called whenever entry is clicked"""
        if self.entry_whachat_ts.get() == "dd-mm-yyyy HH:MM":
            self.entry_whachat_ts.delete(0, "end")  # delete all the text in the entry
            self.entry_whachat_ts.insert(0, '')  # Insert blank for user input
            self.entry_whachat_ts.config(fg='black')

    def on_entry_click_out_whachat(self, event):
        """function that gets called whenever entry is clicked"""
        if self.entry_whachat_te.get() == "dd-mm-yyyy HH:MM":
            self.entry_whachat_te.delete(0, "end")  # delete all the text in the entry
            self.entry_whachat_te.insert(0, '')  # Insert blank for user input
            self.entry_whachat_te.config(fg='black')

    def on_focusout_whachat(self, event):
        """Function that's called every time the focus is lost"""
        if self.entry_whachat_ts.get() == '':
            self.entry_whachat_ts.insert(0, "dd-mm-yyyy HH:MM")
            self.entry_whachat_ts.config(fg='grey')

    def on_focusout_out_whachat(self, event):
        """Function that's called every time the focus is lost"""
        if self.entry_whachat_te.get() == '':
            self.entry_whachat_te.insert(0, "dd-mm-yyyy HH:MM")
            self.entry_whachat_te.config(fg='grey')

    def api(self):
        """Open settings file"""

        cfg_file = Whapa.system_slash("", r'{}/cfg/settings.cfg'.format(whapa_path))
        if system == "Linux":
            os.system('xdg-open "{}"'.format(cfg_file))
        else:
            os.startfile(cfg_file)

    def manual(self):
        """Open the manual"""

        readme_file = Whapa.system_slash("", r'{}/README.md'.format(whapa_path))
        if system == "Linux":
            os.system('xdg-open "{}"'.format(readme_file))
        else:
            os.startfile(readme_file)

    def report(self):
        """Open the report"""

        self.path = filedialog.askopenfilename(title="Select file", filetypes=(("html files", "*.html"), ), initialdir = "report")
        if not self.path:
            return

        if system == "Linux":
            os.system('xdg-open "{}"'.format(self.path))
        else:
            os.startfile(self.path)

    def about(self):
        """ About dialog"""

        messagebox.showinfo("About", title + " v" + version + "\nAuthor: " + author + "\nContact: " + contact)

    def system_slash(self, string):
        """ Change / or \ depend on the OS"""

        if sys.platform == "win32" or sys.platform == "win64" or sys.platform == "cygwin":
            return string.replace("/", "\\")

        else:
            return string.replace("\\", "/")

    def update(self):
        """ About dialog"""

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/update.py" {}'.format(whapa_path, version))
        else:
            exec = self.system_slash(r'python "{}/libs/update.py" {}'.format(whapa_path, version))

        self.label_status.set(exec)
        os.system(exec)

    def exit(self):
        """Exit the App"""
        self.root.destroy()

    def search_whapa_file(self):
        """Search a file"""

        self.path = filedialog.askopenfilename(title="Select file", filetypes=(("Db files", "*.db"),))
        if system == "Linux":
            self.whapa_file.set(self.path)
        else:
            self.whapa_file.set(self.path)

    def search_whapa_wa(self):
        """Search a file"""

        self.path = filedialog.askopenfilename(title="Select file", filetypes=(("Db files", "*.db"),))
        if system == "Linux":
            self.whapa_wa.set(self.path)
        else:
            self.whapa_wa.set(self.path.replace("/", "\\"))

    def search_whapa_out(self):
        """Search a path"""

        self.path = filedialog.askdirectory()
        if system == "Linux":
            self.whapa_out.set(self.path + '/report/')
        else:
            self.whapa_out.set((self.path + "\\report\\").replace("/", "\\"))

    def whapa_messages(self):
        """ Run whapa message command"""

        self.cmd = '-m "{}"'.format(self.whapa_file.get()).strip("\n")
        if self.whapa_wa.get():
            self.cmd += ' -wa "{}"'.format(self.whapa_wa.get()).strip("\n")

        if self.whapa_box_value.get() == "All":
            self.cmd += " -a"
        elif self.whapa_box_value.get() == "User_all":
            self.cmd += " -ua {}".format(self.whapa_user.get()).strip("\n")
        elif self.whapa_box_value.get() == "Group":
            self.cmd += " -g {}".format(self.whapa_user.get()).strip("\n")
        elif self.whapa_box_value.get() == "User":
            self.cmd += " -u {}".format(self.whapa_user.get()).strip("\n")

        if self.whapa_text.get() == "1":
            self.cmd += ' -t "{}"'.format(self.entry_whapa_text.get()).strip("\n")
        else:
            pass

        if self.whapa_ts.get() == "1":
            self.cmd += ' -ts "{}"'.format(self.entry_whapa_ts.get()).strip("\n")
        else:
            pass
        if self.whapa_te.get() == "1":
            self.cmd += ' -te "{}"'.format(self.entry_whapa_te.get()).strip("\n")
        else:
            pass
        if self.whapa_w.get() == "1":
            self.cmd += " -w"
        if self.whapa_s.get() == "1":
            self.cmd += " -s"
        if self.whapa_b.get() == "1":
            self.cmd += " -b"

        if self.whapa_box_filter.get() == "Text":
            self.cmd += " -tt"
        elif self.whapa_box_filter.get() == "Images":
            self.cmd += " -ti"
        elif self.whapa_box_filter.get() == "Audios":
            self.cmd += " -ta"
        elif self.whapa_box_filter.get() == "Videos":
            self.cmd += " -tv"
        elif self.whapa_box_filter.get() == "Contacts":
            self.cmd += " -tc"
        elif self.whapa_box_filter.get() == "Locations":
            self.cmd += " -tl"
        elif self.whapa_box_filter.get() == "Calls":
            self.cmd += " -tx"
        elif self.whapa_box_filter.get() == "Applications":
            self.cmd += " -tp"
        elif self.whapa_box_filter.get() == "GIFs":
            self.cmd += " -tg"
        elif self.whapa_box_filter.get() == "Deleted":
            self.cmd += " -td"
        elif self.whapa_box_filter.get() == "Realtime":
            self.cmd += " -tr"
        elif self.whapa_box_filter.get() == "Stickers":
            self.cmd += " -tk"
        elif self.whapa_box_filter.get() == "System":
            self.cmd += " -tm"
        else:
            pass

        if self.whapa_box_rep.get() == "ES":
            self.cmd += " -r ES"
        elif self.whapa_box_rep.get() == "EN":
            self.cmd += " -r EN"
        else:
            pass

        if self.whapa_out.get():
            self.cmd += ' -o "{}/"'.format(self.whapa_out.get())
        else:
            self.cmd += ' -o "{}/"'.format(os.getcwd())

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
        self.label_status.set(exec)
        os.system(exec)

    def whapa_extract(self):
        """ Run whapa extract command"""
        self.cmd = '-e "{}"'.format(self.whapa_file.get()).strip("\n")
        if self.whapa_ts.get() == "1":
            self.cmd += ' -ts "{}"'.format(self.entry_whapa_ts.get()).strip("\n")
        else:
            pass
        if self.whapa_te.get() == "1":
            self.cmd += ' -te "{}"'.format(self.entry_whapa_te.get()).strip("\n")
        else:
            pass

        if self.whapa_box_value.get() == "User_all":
            self.cmd += " -ua {}".format(self.whapa_user.get()).strip("\n")

        elif self.whapa_box_value.get() == "Group":
            self.cmd += " -g {}".format(self.whapa_user.get()).strip("\n")

        elif self.whapa_box_value.get() == "User":
            self.cmd += " -u {}".format(self.whapa_user.get()).strip("\n")

        if self.whapa_out.get():
            self.cmd += ' -o "{}/"'.format(self.whapa_out.get())
        else:
            self.cmd += ' -o "{}/"'.format(os.getcwd())

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
        self.label_status.set(exec)
        os.system(exec)

    def whapa_status(self):
        """ Run whapa status command"""

        self.cmd = '-i 1 -wa "{}"'.format(self.whapa_wa.get()).strip("\n")
        self.cmd += ' "{}"'.format(self.whapa_file.get()).strip("\n")

        if self.whapa_box_rep.get() == "ES":
            self.cmd += " -r ES"
        elif self.whapa_box_rep.get() == "EN":
            self.cmd += " -r EN"
        else:
            pass

        if self.whapa_out.get():
            self.cmd += ' -o "{}/"'.format(self.whapa_out.get())
        else:
            self.cmd += ' -o "{}/"'.format(os.getcwd())

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
        self.label_status.set(exec)
        os.system(exec)

    def whapa_call(self):
        """ Run whapa call log command"""

        self.cmd = '-i 2 -wa "{}"'.format(self.whapa_wa.get()).strip("\n")
        self.cmd += ' "{}"'.format(self.whapa_file.get()).strip("\n")

        if self.whapa_ts.get() == "1":
            self.cmd += ' -ts "{}"'.format(self.entry_whapa_ts.get()).strip("\n")
        else:
            pass
        if self.whapa_te.get() == "1":
            self.cmd += ' -te "{}"'.format(self.entry_whapa_te.get()).strip("\n")
        else:
            pass

        if self.whapa_box_rep.get() == "ES":
            self.cmd += " -r ES"
        elif self.whapa_box_rep.get() == "EN":
            self.cmd += " -r EN"
        else:
            pass

        if self.whapa_out.get():
            self.cmd += ' -o "{}/"'.format(self.whapa_out.get())
        else:
            self.cmd += ' -o "{}/"'.format(os.getcwd())

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
            print(exec)

        self.label_status.set(exec)
        os.system(exec)

    def whapa_info(self):
        """ Run whapa info command"""

        self.cmd = '-i 3 -wa "{}"'.format(self.whapa_wa.get()).strip("\n")
        self.cmd += ' "{}"'.format(self.whapa_file.get()).strip("\n")

        if self.whapa_box_rep.get() == "ES":
            self.cmd += " -r ES"
        elif self.whapa_box_rep.get() == "EN":
            self.cmd += " -r EN"
        else:
            pass

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whapa.py" {}'.format(whapa_path, self.cmd))
        self.label_status.set(exec)
        os.system(exec)

    def whapa_carving(self):
        """ Run whapa carving database"""

        self.cmd = '"{}"'.format
        print("[i] Database carving starts...")
        print("[i] The process can be slow, be patient!")
        if self.whapa_out.get():
            local = self.whapa_out.get()
        else:
            local = os.getcwd()

        os.makedirs(os.path.dirname(local), exist_ok=True)
        log_file = local + "/msgstore.csv"
        msgstore_file = (self.whapa_file.get()).strip("\n")
        if system == "Linux":
            print("[i] Make sure the undark file has execute permissions")
            exec_command = self.system_slash(r'"{}/libs/undark" -i "{}" --no-blobs --freespace > "{}"'.format(whapa_path, msgstore_file, log_file))
            os.system(exec_command)

        else:
            log = open(log_file, 'w')
            exec = self.system_slash(r'{}/libs/undark.exe'.format(whapa_path))
            c = subprocess.Popen([exec, "-i", msgstore_file, "--no-blobs", "--freespace"], stdout=log, shell=True)
            c.wait()
            log.close()
            exec_command = self.system_slash(r'{}/libs/undark.exe -i "{}" --no-blobs --freespace > "{}"'.format(whapa_path, msgstore_file, log_file))

        self.label_status.set(exec_command)
        print("[i] Finished")

    def estate_assets_whacipher(self):
        """Check that radiobutton is marked"""
        if self.whacipher_box_value.get() == "File":
            self.entry_whacipher_path.config(state=DISABLED)
            self.entry_whacipher_file.config(state=NORMAL)
            self.button_whacipher_path.config(state=DISABLED)
            self.button_whacipher_file.config(state=NORMAL)
            self.entry_whacipher_out.delete(0, END)
            try:
                if system == "Linux":
                    self.entry_whacipher_out.insert(0, self.whacipher_out.set(os.getcwd() + "/msgstore.db"))
                else:
                    self.entry_whacipher_out.insert(0, self.whacipher_out.set(os.getcwd() + r"\msgstore.db"))
            except:
                pass

        elif self.whacipher_box_value.get() == "Path":
            self.entry_whacipher_file.config(state=DISABLED)
            self.entry_whacipher_path.config(state=NORMAL)
            self.button_whacipher_file.config(state=DISABLED)
            self.button_whacipher_path.config(state=NORMAL)
            self.entry_whacipher_out.delete(0, END)
            try:
                if system == "Linux":
                    self.entry_whacipher_out.insert(0, self.whacipher_out.set(os.getcwd() + "/"))
                else:
                    self.entry_whacipher_out.insert(0, self.whacipher_out.set(os.getcwd() + "\\"))
            except:
                pass

    def checkNumberOnly(self, action, value_if_allowed):
        """Check that only numbers are entered"""
        if action != '1':
            return True
        try:
            return value_if_allowed.isnumeric()
        except ValueError:
            return False

    def search_path_whacypher(self):
        """Search a path"""
        self.path = filedialog.askdirectory()
        if system == "Linux":
            self.whacipher_path.set(self.path + '/')
        else:
            self.whacipher_path.set((self.path + "\\").replace("/", "\\"))

    def search_file_whacypher(self):
        """Search a path file"""
        self.path = filedialog.askopenfilename(title="Select file", filetypes=(("Db crypt files", "*.crypt*"),))
        if system == "Linux":
            self.whacipher_file.set(self.path)
        else:
            self.whacipher_file.set(self.path.replace("/", "\\"))

    def search_key_whacypher(self):
        """Search a key file"""
        self.path = filedialog.askopenfilename(title="Select file", filetypes=(("All files", "*"),))
        if system == "Linux":
            self.whacipher_key.set(self.path)
        else:
            self.whacipher_key.set(self.path.replace("/", "\\"))

    def search_out_whacypher(self):
        """Search a output file or path"""

        self.path = filedialog.askdirectory()
        if self.whacipher_box_value.get() == "File":
            if system == "Linux":
                self.whacipher_out.set(self.path + '/msgstore.db')
            else:
                self.whacipher_out.set((self.path + "\\msgstore.db").replace("/", "\\"))
        else:
            if system == "Linux":
                self.whacipher_out_en.set((self.path + "/"))
            else:
                self.whacipher_out_en.set((self.path + "\\").replace("/", "\\"))

    def search_out_whacypher_en(self):
        """Search a output file or path"""
        self.path = filedialog.askdirectory()
        if system == "Linux":
            self.whacipher_out_en.set((self.path + "/msgstore.db.crypt14"))
        else:

            self.whacipher_out_en.set((self.path + "\\msgstore.db.crypt14").replace("/", "\\"))

    def search_criptofile_whacypher_en(self):
        """Search a file"""
        self.path = filedialog.askopenfilename(title="Select file", filetypes=(("Db crypt files", "*.crypt*"),))
        if system == "Linux":
            self.whacipher_crypt_en.set(self.path)
        else:
            self.whacipher_crypt_en.set(self.path.replace("/", "\\"))

    def search_file_whacypher_en(self):
        """Search a file"""
        self.path = filedialog.askopenfilename(title="Select file", filetypes=(("Db files", "*.db"),))
        if system == "Linux":
            self.whacipher_file_en.set(self.path)
        else:
            self.whacipher_file_en.set(self.path.replace("/", "\\"))

    def search_key_whacypher_en(self):
        """Search a key file"""
        self.path = filedialog.askopenfilename(title="Select file", filetypes=(("All files", "*"),))
        if system == "Linux":
            self.whacipher_key_en.set(self.path)
        else:
            self.whacipher_key_en.set(self.path.replace("/", "\\"))

    def decrypt_whacypher(self):
        """Run decrypt command"""
        if self.whacipher_box_value.get() == "File":
            self.cmd = '-f "{}"'.format(self.whacipher_file.get()).strip("\n")
            self.cmd += ' -d "{}"'.format(self.whacipher_key.get()).strip("\n")
            self.cmd += ' -o "{}"'.format(self.whacipher_out.get()).strip("\n")
        else:
            if system == "Linux":
                self.cmd = '-p "{}"'.format(self.whacipher_path.get()).strip("\n")
                self.cmd += ' -d "{}"'.format(self.whacipher_key.get()).strip("\n")
                self.cmd += ' -o "{}"'.format(self.whacipher_out.get()).strip("\n")
            else:
                self.cmd = '-p "{}\\"'.format(self.whacipher_path.get()).strip("\n")
                self.cmd += ' -d "{}"'.format(self.whacipher_key.get()).strip("\n")
                self.cmd += ' -o "{}\\"'.format(self.whacipher_out.get()).strip("\n")

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whacipher.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whacipher.py" {}'.format(whapa_path, self.cmd))
        self.label_status.set(exec)
        os.system(exec)

    def encrypt_whacypher(self):
        """Run encrypt command"""
        self.cmd = '-f "{}"'.format(self.whacipher_file_en.get()).strip("\n")
        self.cmd += ' -e "{}" "{}"'.format(self.whacipher_key_en.get(), self.whacipher_crypt_en.get()).strip("\n")
        self.cmd += ' -o "{}"'.format(self.whacipher_out_en.get()).strip("\n")

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whacipher.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whacipher.py" {}'.format(whapa_path, self.cmd))
        self.label_status.set(exec)
        os.system(exec)

    def search_path_whamerge(self):
        """Search a path file to merge"""
        self.path = filedialog.askdirectory()
        if system == "Linux":
            self.whamerge_path.set(self.path + "/")
        else:
            self.whamerge_path.set((self.path + "\\").replace("/", "\\"))

    def search_file_whamerge(self):
        """Search a output file to merge"""
        self.path = filedialog.askdirectory()
        if system == "Linux":
            self.whamerge_file.set(self.path)
        else:
            self.whamerge_file.set((self.path + "\\msgstore_merge.db").replace("/", "\\"))

    def whamerge(self):
        """Run merge command"""

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whamerge.py" "{}" -o "{}"'.format(whapa_path, self.whamerge_path.get(), self.whamerge_file.get()))
        else:
            exec = self.system_slash(r'python "{}/libs/whamerge.py" "{}" -o "{}"'.format(whapa_path, self.whamerge_path.get(), self.whamerge_file.get()))

        self.label_status.set(exec)
        os.system(exec)

    def search_file_whachat(self):
        """Search a file and load participants"""
        try:
            self.path = filedialog.askopenfilename(title="Select file", filetypes=(("txt files", "*.txt"),))
            if system == "Linux":
                self.whachat_file.set(self.path)
            else:
                self.whachat_file.set(self.path.replace("/", "\\"))

            if system == "Linux":
                exec = self.system_slash(r'python3 "{}/libs/whachat.py" "{}" -p -s {}'.format(whapa_path, self.whachat_file.get(), self.whachat_box_os.get()))
            else:
                exec = self.system_slash(r'python "{}/libs/whachat.py" "{}" -p -s {}'.format(whapa_path, self.whachat_file.get(), self.whachat_box_os.get()))

            self.label_status.set(exec)
            os.system(exec)
            path, file = os.path.split(self.whachat_file.get())
            participants = path + "/participants.txt"
            with open(participants, "r", errors="ignore") as file_r:
                list_participant = []
                for i in file_r:
                    list_participant.append(i)
                self.combo_whachat_user["values"] = list_participant
                self.combo_whachat_user.current(0)
        except Exception as e:
            self.label_status.set("Did not get the list of participants choose another operating system and load the file back")
            print("Could not load the list of participants, choose another operating system and load the file back")

    def on_entry_click(self, event):
        """function that gets called whenever entry is clicked"""
        if self.entry_whachat_ts.get() == "dd-mm-yyyy HH:MM":
            self.entry_whachat_ts.delete(0, "end")  # delete all the text in the entry
            self.entry_whachat_ts.insert(0, '')  # Insert blank for user input
            self.entry_whachat_ts.config(fg='black')

    def on_entry_click_out(self, event):
        """function that gets called whenever entry is clicked"""
        if self.entry_whachat_te.get() == "dd-mm-yyyy HH:MM":
            self.entry_whachat_te.delete(0, "end")  # delete all the text in the entry
            self.entry_whachat_te.insert(0, '')  # Insert blank for user input
            self.entry_whachat_te.config(fg='black')

    def on_focusout(self, event):
        """Function that's called every time the focus is lost"""
        if self.entry_whachat_ts.get() == '':
            self.entry_whachat_ts.insert(0, "dd-mm-yyyy HH:MM")
            self.entry_whachat_ts.config(fg='grey')

    def on_focusout_out(self, event):
        """Function that's called every time the focus is lost"""
        if self.entry_whachat_te.get() == '':
            self.entry_whachat_te.insert(0, "dd-mm-yyyy HH:MM")
            self.entry_whachat_te.config(fg='grey')

    def estate_assets_whachat(self):
        """Check that radiobutton is marked"""

        if self.whachat_box_os.get() == "android":
            self.combo_whachat_format.current(2)
        else:
            self.combo_whachat_format.current(0)

    def whachat_run(self):
        """Run WhaChat command"""

        self.cmd = '"{}" -s {} -f "{}"'.format(self.whachat_file.get(), self.whachat_box_os.get(), self.combo_whachat_format.get())
        if self.entry_whachat_ts.get() != "dd-mm-yyyy HH:MM":
            self.cmd += ' -ts "{}"'.format(self.entry_whachat_ts.get())

        if self.entry_whachat_te.get() != "dd-mm-yyyy HH:MM":
            self.cmd += ' -te "{}"'.format(self.entry_whachat_te.get())

        if self.whachat_box_rep.get() == "ES":
            self.cmd += " -r ES"

        elif self.whachat_box_rep.get() == "EN":
            self.cmd += " -r EN"

        if self.combo_whachat_user.get():
            self.cmd += ' -u "{}"'.format(self.combo_whachat_user.get().rstrip("\n"))

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whachat.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whachat.py" {}'.format(whapa_path, self.cmd))

        self.label_status.set(exec)
        os.system(exec)

    def search_path_whagodri(self):
        """Search a output path """

        self.path = filedialog.askdirectory()
        if system == "Linux":
            self.whagodri_path.set(self.path + "/")
        else:
            self.whagodri_path.set((self.path + "\\").replace("/", "\\"))

    def wagodri_down(self):
        """Run Google Drive command"""
        if self.wagodri_box_value.get() == "Info":
            self.cmd = "-i"

        elif self.wagodri_box_value.get() == "List":
            self.cmd = "-l"

        elif self.wagodri_box_value.get() == "ListW":
            self.cmd = "-lw"

        elif self.wagodri_box_value.get() == "All":
            self.cmd = "-s"

        elif self.wagodri_box_value.get() == "Images":
            self.cmd = "-si"

        elif self.wagodri_box_value.get() == "Videos":
            self.cmd = "-sv"

        elif self.wagodri_box_value.get() == "Audios":
            self.cmd = "-sa"

        elif self.wagodri_box_value.get() == "Documents":
            self.cmd = "-sx"

        elif self.wagodri_box_value.get() == "Databases":
            self.cmd = "-sd"

        elif self.wagodri_box_value.get() == "File":
            self.cmd = '-p "{}"'.format(self.entry_whagodri_down.get()).strip("\n")

        if self.whagodri_path.get():
            self.cmd += ' -o "{}/"'.format(self.whagodri_path.get()).strip("\n")

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whagodri.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whagodri.py" {}'.format(whapa_path, self.cmd))

        self.label_status.set(exec)
        os.system(exec)

    def search_path_whacloud(self):
        """Search a output path """

        self.path = filedialog.askdirectory()
        if system == "Linux":
            self.whacloud_path.set(self.path + "/")
        else:
            self.whacloud_path.set((self.path + "\\").replace("/", "\\"))

    def wacloud_down(self):
        """ Run Icloud command"""

        if self.wacloud_box_value.get() == "List":
            self.cmd = " -l"

        elif self.wacloud_box_value.get() == "Sync":
            self.cmd = " -s"

        elif self.wacloud_box_value.get() == "Images":
            self.cmd = " -si"

        elif self.wacloud_box_value.get() == "Videos":
            self.cmd = " -sv"

        elif self.wacloud_box_value.get() == "File":
            self.cmd = " -p {}".format(self.entry_whacloud_down.get()).strip("\n")

        if self.whacloud_path.get():
            if system == "Linux":
                self.cmd += ' -o "{}/"'.format(self.whagodri_path.get()).strip("\n")

        if system == "Linux":
            exec = self.system_slash(r'python3 "{}/libs/whacloud.py" {}'.format(whapa_path, self.cmd))
        else:
            exec = self.system_slash(r'python "{}/libs/whacloud.py" {}'.format(whapa_path, self.cmd))

        self.label_status.set(exec)
        os.system(exec)

    def open_folder(self):
        """Open current folder"""

        webbrowser.open('.')

    def requirements(self):
        """Install dependencies"""

        if system == "Linux":
            exec = self.system_slash(r'sudo pip3 install --upgrade -r "{}/doc/requirements.txt"'.format(whapa_path))
        else:
            exec = self.system_slash(r'pip install --upgrade -r "{}/doc/requirements.txt"'.format(whapa_path))
        self.label_status.set(exec)
        os.system(exec)


if __name__ == '__main__':
    """Initialize"""

    if system == "Linux":
        exec = Whapa.system_slash("", r'python3 "{}/libs/update.py" {}'.format(whapa_path, version))
    else:
        exec = Whapa.system_slash("", r'python "{}/libs/update.py" {}'.format(whapa_path, version))

    cfg_file = Whapa.system_slash("", r'{}/cfg/settings.cfg'.format(whapa_path))
    if not os.path.isfile(cfg_file):
        # It creates the settings file
        with open(cfg_file, 'w') as cfg:
            cfg.write(dedent("""
                [report]
                company =
                record =
                unit =
                examiner =
                notes =

                [google-auth]
                gmail = alias@gmail.com
                # Optional. The account password or app password when using 2FA.
                password  = 
                # Optional. The result of "adb shell settings get secure android_id".
                android_id = 0000000000000000
                # Optional. Enter the backup country code + phonenumber be synchronized, otherwise it synchronizes all backups.
                # You can specify a list of celnumbr = BackupNumber1, BackupNumber2, ...
                celnumbr = 
                
                [icloud-auth] 
                icloud  = alias@icloud.com
                passw = yourpassword
                """).lstrip())

    error_icon = False
    img_folder = Whapa.system_slash("", "{}/images/".format(whapa_path))
    icons = (img_folder + "logo.png",
             img_folder + "whapa.png",
             img_folder + "about.png",
             img_folder + "setting.png",
             img_folder + "out.png",
             img_folder + "search.png",
             img_folder + "manual.png",
             img_folder + "report.png",
             img_folder + "file.png",
             img_folder + "tabwhapa.png",
             img_folder + "tabwhagodri.png",
             img_folder + "tabwhacipher.png",
             img_folder + "tabwhamerge.png",
             img_folder + "infowhagodri.png",
             img_folder + "downwhagodri.png",
             img_folder + "merge.png",
             img_folder + "decrypt.png",
             img_folder + "encrypt.png",
             img_folder + "spanish.png",
             img_folder + "english.png",
             img_folder + "parser.png",
             img_folder + "terminal.png",
             img_folder + "extract.png",
             img_folder + "callslog.png",
             img_folder + "status.png",
             img_folder + "requirements.png",
             img_folder + "update.png",
             img_folder + "carving.png",
             img_folder + "tabwhacloud.png",
             img_folder + "tabwhachat.png",
             img_folder + "android.png",
             img_folder + "ios.png"
             )

    for icon in icons:
        if not os.path.exists(icon):
            print('Icon not found:', icon)
            error_icon = True

    if not error_icon:
        if sys.platform == "win32" or sys.platform == "win64" or sys.platform == "cygwin":
            system = "Windows"
        else:
            system = "Linux"
        Whapa(img_folder, icons)

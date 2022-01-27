# Stream Buddy Icon derived from original work by Azmianshori - https://www.flaticon.com/authors/azmianshori
# Play Icon - Icon derived from original work by Freepik - https://www.freepik.com/
# Folder Icon - Icon derived from original work by Freepik - https://www.freepik.com/
# Gear Icon - Icon derived from original work by Freepik - https://www.freepik.com/
# Feedback Icon - Icon derived from original work by Those Icons - https://www.flaticon.com/authors/those-icons
# Exit Door Icon - Icon derived from original work by Freepik - https://www.freepik.com/

# Stream Buddy - A powerful Twitch clip downloader and viewer.
# Copyright (C) 2021 Zachary Goreczny
# Stream Buddy is disributed under the GPL-3 open source license.

from genericpath import exists
from importlib.resources import path
from mailbox import mbox
from random import random
import sys
from PyQt5 import QtCore
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
from PyQt5.QtGui import *
from twitchAPI.twitch import Twitch
import json
from os import makedirs, startfile, system, walk, listdir, path, add_dll_directory
from pathlib import Path
import time
import random
from selenium import webdriver
from bs4 import BeautifulSoup
import urllib
from datetime import datetime
from windows_tools.installed_software import get_installed_software
import zipfile
import tempfile
from shutil import rmtree
import ssl
import smtplib
import warnings
from win32gui import DestroyWindow
from screeninfo import get_monitors
from mutagen.mp4 import *

### Checks for a VLC installation, if True, VLC is imported.
for app in get_installed_software():
            if app["name"].__contains__("VLC"):
                vlc_installed = True
                try:
                    add_dll_directory(r"C:\Program Files\VideoLAN\VLC")
                except:
                    add_dll_directory(r"C:\Program Files (x86)\VideoLAN\VLC")
                import vlc
            else:
                pass

### Declaring Twitch API variables and settings dict.
client_id = "yaoela7u57wifm4kom77dfsi7ki8nj"
client_secret = "bwkl2lzihxbj6dmma2v5n6h4hpov10"
settings = {}

### Window hex values, may add more customization in the future.
background_color = "#424242"
text_color = "#FFFFFF"
header_text_color ="#FFFFFF"

### Declaring download list for if the list downloader is used, list of monitors, 
# download code to stop download of clips.
dl_list = []
mons_list = []
dcode = 0

### Get all monitors of computer.
monitors = get_monitors()
app_data = str(Path.home() / "Documents\\Stream Buddy")

### Checks to see if there is a folder called "Stream Buddy" in the user's
# documents folder. If there is none, it is created and default settings
# are set. If the path does exsist, the json file is read and the saved
# settings are set as the program variables.
if not path.exists(app_data):
    makedirs(app_data)

if path.exists(app_data+"\\sb_settings.json") == False:
    accounts_list = ["My Twitch Channel"]
    random_clips = False
    loop_clips = False
    overlay_active = True
    save_loc = ""
    save_loc_count = "0"
    app_icon = "sb-logo.png"
    overlay_img = "sb-logo.png"
    overlay_size = "100x100"
    disp_monitor = -1
    controller_pos = "100,100"
    overlay_pos = "100,100"

else:
    with open(app_data+"\\sb_settings.json", "r") as f:
        content = json.load(f)
        try:
            accounts_list = content["accounts-list"]
        except:
            accounts_list = ["My Twitch Channel"]

        try:
            disp_monitor = content["disp-monitor"]
        except:
            disp_monitor = -1

        try:
            if content["random-clips"] == "0":
                random_clips = False
            else:
                random_clips = True
        except:
            random_clips = False

        try:
            if content["loop-clips"] == "0":
                loop_clips = False
            else:
                loop_clips = True
        except:
            loop_clips = False

        try:
            if content["overlay-active"] == "0":
                overlay_active = False
            else:
                overlay_active = True
        except:
            overlay_active = True

        try:
            save_loc = content["save-loc"]
        except:
            save_loc = ""

        try:
            save_loc_count = content["save-loc-count"]
        except:
            save_loc_count = "0"

        try:
            app_icon = content["app-icon"]
            icon_dir = Path(app_icon)
            if icon_dir.exists() == True:
                app_icon = str(icon_dir)
            else:
                app_icon = "sb-logo.png"
        except:
            app_icon = "sb-logo.png"

        try:
            overlay_img = content["overlay-img"]
        except:
            overlay_img = "sb-logo.png"
        try:
            overlay_size = content["overlay-size"]
        except:
            overlay_size = "100x100"
        try:
            controller_pos = content["controller-pos"]
        except:
            controller_pos = "100,100"
        try:
            overlay_pos = content["overlay-pos"]
        except:
            overlay_pos = "100,100"

### Creating setup window class that checks to see if VLC is installed, if
# it is not, than the VLC installer runs. If it is, the user is prompted
# to restart Stream Buddy. This will run on first app startup.
class setup(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stream Buddy")
        self.setWindowIcon(QIcon(app_icon))
        self.setStyleSheet("color: {}; background-color: {};".format(text_color, background_color))
        self.setup_ui()

    def setup_ui(self):
        for app in get_installed_software():
            if app["name"].__contains__("VLC"):
                vlc_installed = True
                break
            else:
                vlc_installed = False
        if vlc_installed == True:
            mbox = QMessageBox.information(self, "Thanks for installing Stream Buddy!","""
Thanks for installing Stream Buddy!
Stream Buddy uses VLC Media Player to play and contol videos,
which you already have installed! To begin using Stream Buddy,
click 'OK' and start Stream Buddy again. Enjoy!""")
        if vlc_installed == False:
            mbox = QMessageBox.information(self, "Thanks for installing Stream Buddy!", """
In order to complete setup, we need to install VLC. This is
an open source video player that Stream Buddy uses to play
your videos. After clicking 'OK', the installer will run.
When VLC is installed, close the installer and restart
Stream Buddy. Enjoy!""")
            system("start vlc-3.0.16-win32.exe")

        downloads_path = str(Path.home() / "Downloads")

        settings["save-loc"] = downloads_path
        temp_json = json.dumps(settings, indent=4)

        with open(app_data+"\\sb_settings.json", "w") as f:
            f.write(temp_json)

### The main app window.
class Window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Stream Buddy")
        self.setGeometry(100,100,650,300)
        self.setWindowIcon(QIcon(app_icon))
        self.setStyleSheet("color: {}; background-color: {};".format(text_color, background_color))
        self.UI()

    def UI(self):
        global status_text, pbar
        self.main_layout = QGridLayout()
        self.tb_layout = QHBoxLayout()
        main_text_layout = QHBoxLayout()

        main_tb = QToolBar()
        main_tb.setIconSize(QSize(60,60))
        main_tb.setStyleSheet("color: #000000")
        
        stream_logo = QAction(QIcon(app_icon), "Stream Buddy", self)
        main_tb.addAction(stream_logo)

        play_icon = QAction(QIcon(r"sb-play.png"), "Play Clips", self)
        play_icon.triggered.connect(play_clips)
        play_icon.triggered.connect(player_button)
        if overlay_active == False:
            pass
        else:
            play_icon.triggered.connect(overlay_button)
        main_tb.addAction(play_icon)

        download_icon = QAction(QIcon(r"sb-download.png"), "Quick Download", self)
        download_icon.triggered.connect(self.download_clips)
        main_tb.addAction(download_icon)

        download_icon = QAction(QIcon(r"sb-dlist.png"), "Download List", self)
        download_icon.triggered.connect(downloader_list)
        main_tb.addAction(download_icon)

        folder_icon = QAction(QIcon(r"sb-folder.png"), "Open Clips", self)
        folder_icon.triggered.connect(self.open_folder)
        main_tb.addAction(folder_icon)

        settings_icon = QAction(QIcon(r"sb-setting.png"), "Settings", self)
        settings_icon.triggered.connect(settings_button)
        main_tb.addAction(settings_icon)

        feedback_icon = QAction(QIcon(r"sb-feedback.png"), "Feedback", self)
        feedback_icon.triggered.connect(feedback_button)
        main_tb.addAction(feedback_icon)

        exit_icon = QAction(QIcon(r"sb-exit.png"), "Exit", self)
        exit_icon.triggered.connect(self.closeEvent)
        main_tb.addAction(exit_icon)

        status_text = QLabel("Welcome to Stream Buddy!\nClick an icon to get started!")
        status_text.setFont(QFont("Times", 13, QFont.Bold))
        status_text.setAlignment(Qt.AlignCenter)

        pbar = QProgressBar()
        pbar.setMaximum(100)
        pbar.hide()

        self.stop_button = QPushButton("Stop Download!")
        self.stop_button.setStyleSheet("""
                                  QPushButton{color: #11052C; background-color: #914148;
                                  border-style: solid; border-width: 2px; border-radius: 10px;
                                  border-color: #0030ff; padding: 6px;}
                                  QPushButton:hover{background-color: #FF0015; font-weight: 900;}""")
        self.stop_button.clicked.connect(self.stop_download)
        self.stop_button.hide()

        help_button = QPushButton("Help!")
        help_button.setStyleSheet("""
                                  QPushButton{color: #11052C; background-color: #BDBDBD;
                                  border-style: solid; border-width: 2px; border-radius: 10px;
                                  border-color: #0030ff; padding: 6px;}
                                  QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        help_button.clicked.connect(self.help_func)

        close_button = QPushButton("Quit!")
        close_button.setStyleSheet("""
                                  QPushButton{color: #11052C; background-color: #BDBDBD;
                                  border-style: solid; border-width: 2px; border-radius: 10px;
                                  border-color: #0030ff; padding: 6px;}
                                  QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        close_button.clicked.connect(self.closeEvent)

        self.tb_layout.addStretch()
        self.tb_layout.addWidget(main_tb)
        self.tb_layout.addStretch()

        main_text_layout.addStretch()
        main_text_layout.addWidget(status_text)
        main_text_layout.addStretch()

        self.main_layout.addLayout(self.tb_layout,0,0,1,2)
        self.main_layout.addLayout(main_text_layout,1,0,1,2)
        self.main_layout.addWidget(pbar,2,0,1,2)
        self.main_layout.addWidget(self.stop_button,3,0,1,2)
        self.main_layout.addWidget(help_button,4,0)
        self.main_layout.addWidget(close_button,4,1)

        self.setLayout(self.main_layout)
        self.show()

    def help_func(self):
        system("start https://www.ztdapps.com/?p=150")

    def open_folder(self):
        try:
            comd = startfile(r'"{}"'.format(save_loc))
            if comd == 1:
              mbox = QMessageBox.warning(self, "Error!", "Could not open the download directory.\nTry restarting Stream Buddy and try again.")  
        except:
            mbox = QMessageBox.warning(self, "Error!", "Could not open the download directory.\nTry restarting Stream Buddy and try again.")

### Using QThread for downloading clips as its a long process and WILL crash the UI.
    def download_clips(self):
        self.dworker = clip_downloader()
        self.dthread = QThread()
        self.dthread.setTerminationEnabled(True)
        self.dworker.send_progress.connect(self.download_update)
        self.dworker.moveToThread(self.dthread)
        self.dthread.started.connect(self.dworker.clip_grabber)
        self.dworker.dfinished.connect(self.finished_downloading)
        self.dthread.start()
        pbar.show()
        self.stop_button.show()

    def download_update(self, percent):
        try:
            pb_status = (percent/numclips_count)*100
            pbar.setValue(pb_status)
            status_text.setText("Downloading clip {} of {}...".format(percent,numclips_count))
        except:
            status_text.setText("The clips you selected have already been downloaded.\nCheck your clips folder.")

    def finished_downloading(self):
        if len(accounts_list) == 0:
            status_text.setText("No valid accounts are selected.\nPlease check settings and try again.")
            pbar.hide()
            self.stop_button.hide()
            self.dthread.quit()
        else:
            if dcode == 1:
                pass
            else:
                if numclips_count == 0:
                    status_text.setText("The clips you selected have already been downloaded.\nCheck your clips folder.")
                    pbar.hide()
                    dl_list.clear()
                    self.stop_button.hide()
                    self.dthread.quit()
                else:
                    status_text.setText("{} clips downloaded!".format(numclips_count))
                    pbar.hide()
                    self.stop_button.hide()
                    self.dthread.quit()

    def stop_download(self):
        global dcode
        dcode = 1
        pbar.hide()
        self.stop_button.hide()
        self.dthread.terminate()
        status_text.setText("Stopped clips downloader!")
        mbox = QMessageBox.information(self, "Download Stopped!", "Stream Buddy has stopped downloading clips.")

### Overrides default PyQt closeEvent method to close all open Stream Buddy windows
# when the main window is closed.
    def closeEvent(self, event):
        if QCloseEvent():
            try:
                self.dthread.quit()
            except:
                pass
            App.closeAllWindows()
            sys.exit()

### Declaring each window that is opened as a global variable so trash collector
# does not scoop it up and the window closes immediately.
def settings_button():
    global settings_win
    settings_win = settings_window()
    return settings_win

def custom_button():
    global custom_win
    custom_win = custom_window()
    return custom_win

def overlay_button():
    global overlay_win
    overlay_win = overlay_window()
    return overlay_win

def player_button():
    global player_cont
    player_cont = player_controller()
    return player_cont

def downloader_list():
    global dlist
    dlist = list_window()
    return dlist

def play_clips():
    global cplayer
    cplayer = play_window()
    return cplayer

def feedback_button():
    global feedback_win
    feedback_win = feedback_window()
    return feedback_win

### The play window where all the magic happens. A VLC instance is loaded into
# a PyQt window to allow software such as OBS to broadcast a window, instead
# of each seperate VLC instance. Also allows for smoother playback.    
class play_window(QMainWindow):
    def __init__(self, master=None):
        QMainWindow.__init__(self, master)
        global media_player, py2, player
        self.setWindowTitle("Clip Player")
        self.setWindowIcon(QIcon(app_icon))
        self.setStyleSheet("color: {}; background-color: {};".format(text_color, background_color))

        try:
            player = vlc.Instance()
            media_player = vlc.MediaListPlayer()
            py2 = vlc.MediaPlayer()
            self.media_list = player.media_list_new()
            self.list_creator()
        except:
            mbox = QMessageBox.critical(self, "Crtical Error!", """
Could not start VLC Media Player!
Try restarting Stream Buddy and checking your VLC installation.
If you still have an error, use the Feedback feature to send a message""")

### Creates media playlist based on user settings of the loop_clips and
# random_clips variables. Sets the created list into the instance of
# VLC MediaListPlayer.
    def list_creator(self):
        clips = []
        folder_loc = save_loc
        dir_list = listdir(folder_loc)
        for item in dir_list:
            if item.endswith(".mp4"):
                ls_item = folder_loc+"/"+item
                clips.append(ls_item)

        if loop_clips == False and random_clips == False:
            for item in clips:
                media = player.media_new(item)
                self.media_list.add_media(media)
                media_player.set_media_list(self.media_list)
                media_player.set_media_player(py2)
        if loop_clips == True and random_clips == False:
            loop_list = []
            while len(loop_list) < 5000:
                for item in clips:
                    loop_list.append(item)
            for item in loop_list:
                media = player.media_new(item)
                self.media_list.add_media(media)
                media_player.set_media_list(self.media_list)
                media_player.set_media_player(py2)
        if loop_clips == False and random_clips == True:
            random.shuffle(clips)
            for item in clips:
                media = player.media_new(item)
                self.media_list.add_media(media)
                media_player.set_media_list(self.media_list)
                media_player.set_media_player(py2)
        if loop_clips == True and random_clips == True:
            loop_list = []
            while len(loop_list) < 5000:
                for item in clips:
                    loop_list.append(item)
            random_set = set(loop_list)
            n_loop_list = random.choices(list(random_set), k=5000)
            for item in n_loop_list:
                media = player.media_new(item)
                self.media_list.add_media(media)
                media_player.set_media_list(self.media_list)
                media_player.set_media_player(py2)
        self.player_ui()

    def player_ui(self):
        global invis_text, videoframe, vframe_id
        self.widget = QWidget(self)
        self.setCentralWidget(self.widget)

        if sys.platform == "darwin":
            from PyQt5.QtWidgets import QMacCocoaViewContainer	
            videoframe = QMacCocoaViewContainer(0)
        else:
            videoframe = QFrame()
        self.palette = videoframe.palette()
        self.palette.setColor (QPalette.Window,
                               QColor(0,0,0))
        videoframe.setPalette(self.palette)
        videoframe.setAutoFillBackground(True)

        if sys.platform.startswith('linux'):
            py2.set_xwindow(videoframe.winId())
        elif sys.platform == "win32":
            py2.set_hwnd(videoframe.winId())
        elif sys.platform == "darwin":
            py2.set_nsobject(int(videoframe.winId()))
        vframe_id = self.winId()
        media_player.play()

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        
        self.vboxlayout = QVBoxLayout()
        self.vboxlayout.setContentsMargins(0,0,0,0)
        self.vboxlayout.addWidget(videoframe)
        self.widget.setLayout(self.vboxlayout)

        monitor = QDesktopWidget().screenGeometry(disp_monitor)
        self.move(monitor.left()+1, monitor.top())

        self.showMaximized()

### A feedback window for easy and instant in-app feedback.
class feedback_window(QWidget):
    def __init__(self):
        super().__init__()
        self.setGeometry(100,100,700,500)
        self.setWindowTitle("Feedback")
        self.setWindowIcon(QIcon(app_icon))
        self.setStyleSheet("color: {}; background-color: {};".format(text_color, background_color))
        self.feedback_ui()

    def feedback_ui(self):
        feedback_ui_layout = QGridLayout()
        self.setLayout(feedback_ui_layout)

        hbox = QHBoxLayout()
        close_hbox = QHBoxLayout()

        feed_text = QLabel("Feedback")
        feed_text.setFont(QFont("Times", 14, QFont.Bold))

        help_text = QLabel("Hi there! Hope you're enjoying Stream Buddy! Feedback is always welcome and helps me improve the app for you.\
            \nFeel free to send feature requests, bugs or words of inspiration. All messages are anonymous unless you choose to add personal info.")

        self.subject_input = QLineEdit()
        self.subject_input.setPlaceholderText("Subject")

        self.body_input = QTextEdit()
        self.body_input.setPlaceholderText("Use this space for comments, suggestions, and ways I can improve Stream Buddy!")

        send_button = QPushButton("Send Feedback")
        send_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                border-style: solid; border-width: 2px; border-radius: 10px;
                                border-color: #0030ff; padding: 6px;}
                                QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        send_button.clicked.connect(self.send_feedback)

        clear_button = QPushButton("Clear All")
        clear_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                border-style: solid; border-width: 2px; border-radius: 10px;
                                border-color: #0030ff; padding: 6px;}
                                QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        clear_button.clicked.connect(self.clear_all)

        close_button = QPushButton("        Close Feedback      ")
        close_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                border-style: solid; border-width: 2px; border-radius: 10px;
                                border-color: #0030ff; padding: 6px;}
                                QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        close_button.clicked.connect(self.close_window)

        hbox.addWidget(send_button)
        hbox.addWidget(clear_button)

        close_hbox.addStretch()
        close_hbox.addWidget(close_button)
        close_hbox.addStretch()

        feedback_ui_layout.addWidget(feed_text)
        feedback_ui_layout.addWidget(help_text)
        feedback_ui_layout.addWidget(self.subject_input)
        feedback_ui_layout.addWidget(self.body_input)
        feedback_ui_layout.addLayout(hbox,4,0)
        feedback_ui_layout.addLayout(close_hbox,5,0)

        self.show()

    def clear_all(self):
        self.subject_input.clear()
        self.body_input.clear()

    def close_window(self):
        self.close()

    def send_feedback(self):
        warnings.simplefilter("ignore")
        port = 587
        smtp_server = "smtp.gmail.com"
        sender_email = "ztdapps@zachgoreczny.com"
        recieve_email = "ztdapps@zachgoreczny.com"
        password = "rwyothjxwyhkfpjp"

        subject = self.subject_input.text()
        message = self.body_input.toPlainText()

        message = """\
Subject:Stream Buddy Feedback - {}

{}

""".format(subject, message)
        if subject and message != "":
            try:
                context = ssl.create_default_context()
                with smtplib.SMTP(smtp_server, port) as server:
                    server.starttls(context=context)
                    server.login(sender_email, password)
                    server.sendmail(sender_email, recieve_email, message)
                self.subject_input.clear()
                self.body_input.clear()
                mbox = QMessageBox.information(self, "Feedback Recieved!", "Thanks for your feedback! I'll make sure to read it as soon as possible!")
            except:
                mbox = QMessageBox.warning(self, "Feedback Not Sent!", "Make sure to include both a subject and message.")
        else:
            mbox = QMessageBox.warning(self, "Feedback Not Sent!", "Make sure to include both a subject and message.")

### The list window where users can add specific clips to thier clips player.
class list_window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Download Clips")
        self.setGeometry(100,100,500,400)
        self.setWindowIcon(QIcon(app_icon))
        self.setStyleSheet("color: {}; background-color: {};".format(text_color, background_color))
        self.dl_ui()

    def dl_ui(self):
        dl_layout = QGridLayout()
        self.setLayout(dl_layout)

        dl_label = QLabel("Create Download List")
        dl_label.setFont(QFont("Times", 14, QFont.Bold))

        dl_text = QLabel("")

        self.dl_listbox = QListWidget()

        dl_add = QPushButton("Add Clip")
        dl_add.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                border-style: solid; border-width: 2px; border-radius: 10px;
                                border-color: #0030ff; padding: 6px;}
                                QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        dl_add.clicked.connect(self.add_clip)

        dl_remove = QPushButton("Remove Clip")
        dl_remove.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                border-style: solid; border-width: 2px; border-radius: 10px;
                                border-color: #0030ff; padding: 6px;}
                                QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        dl_remove.clicked.connect(self.remove_clip)

        dl_download = QPushButton("Download Clips")
        dl_download.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                border-style: solid; border-width: 2px; border-radius: 10px;
                                border-color: #0030ff; padding: 6px;}
                                QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        dl_download.clicked.connect(self.download_clips)

        dl_cancel = QPushButton("Close List Creator Box")
        dl_cancel.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                border-style: solid; border-width: 2px; border-radius: 10px;
                                border-color: #0030ff; padding: 6px;}
                                QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        dl_cancel.clicked.connect(self.close_win)

        dl_layout.addWidget(dl_label,0,0,1,2)
        dl_layout.addWidget(dl_text,1,0,1,2)
        dl_layout.addWidget(self.dl_listbox,2,0,1,2)
        dl_layout.addWidget(dl_add,3,0)
        dl_layout.addWidget(dl_remove,3,1)
        dl_layout.addWidget(dl_download,4,0,1,2)
        dl_layout.addWidget(dl_cancel,5,0,1,2)

        self.show()

    def add_clip(self):
        url_input, ok = QInputDialog.getText(self, "Add Clip URL", "Paste Clip URL")
        if url_input.__contains__("twitch") and ok:
            self.dl_listbox.addItem(url_input)
            dl_list.append(url_input)
        else:
            mbox = QMessageBox.warning(self, "Paste a valid clip link!", "Paste a valid Twitch clip link.\nExample: https://www.twitch.tv/steeldrifter/clip/LongPatientAardvarkSoBayed-lDOLVLFiwWXD0gVW")
    
    def remove_clip(self):
        try:
            curr_item = self.dl_listbox.currentRow()
            self.dl_listbox.takeItem(curr_item)
            dl_list.pop(curr_item)
        except:
            mbox = QMessageBox.warning(self, "Selection Error!", "Please select a link then click 'Remove'.")

    def close_win(self):
        self.close()

    def download_clips(self):
        self.close()
        self.dlworker = clip_downloader()
        self.dlthread = QThread()
        self.dlworker.send_progress.connect(self.download_update)
        self.dlworker.moveToThread(self.dlthread)
        self.dlthread.started.connect(self.dlworker.clip_grabber)
        self.dlworker.dfinished.connect(self.finished_downloading)
        self.dlthread.start()
        pbar.show()

    def download_update(self, percent):
        try:
            pb_status = (percent/numclips_count)*100
            pbar.setValue(pb_status)
            status_text.setText("Downloading clip {} of {}...".format(percent,numclips_count))
        except:
            status_text.setText("The clips you selected have already been downloaded.\nCheck your clips folder.")

    def finished_downloading(self):
        if len(dl_list) == 0:
            status_text.setText("No valid accounts are selected.\nPlease check settings and try again.")
            pbar.hide()
            dl_list.clear()
            self.dlthread.quit()
        else:
            if numclips_count == 0:
                status_text.setText("The clips you selected have already been downloaded.\nCheck your clips folder.")
                pbar.hide()
                dl_list.clear()
                self.dlthread.quit()
            else:
                status_text.setText("{} Clips Pulled from Twitch!".format(numclips_count))
                pbar.hide()
                dl_list.clear()
                self.dlthread.quit()

### A seperate window that pops up when the clips player is started.
# This allows the user to pause, skip, reverse, hide/show overlay,
# and close the clip player when finished.
class player_controller(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Player Controller")
        win_splits = controller_pos.split(",")
        xwin = int(win_splits[0])
        ywin = int(win_splits[1])
        self.setGeometry(xwin,ywin,250,150)
        self.setWindowIcon(QIcon(app_icon))
        self.setStyleSheet("color: {}; background-color: {};".format(text_color, background_color))
        self.cc_ui()

    def cc_ui(self):
        global ccwin_id

        cc_layout = QGridLayout()
        self.setLayout(cc_layout)
        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)

        controller_label = QLabel("Media Controller")
        controller_label.setFont(QFont("Times", 11, QFont.Bold))

        self.pause_play_button = QPushButton("Pause")
        self.pause_play_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                            border-style: solid; border-width: 2px; border-radius: 10px;
                                            border-color: #0030ff; padding: 6px;}
                                            QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        self.pause_play_button.clicked.connect(self.pause_player)

        skip_button = QPushButton("Next")
        skip_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        skip_button.clicked.connect(self.skip_player)

        last_button = QPushButton("Previous")
        last_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        last_button.clicked.connect(self.last_player)

        overlay_hide = QPushButton("Hide Overlay")
        overlay_hide.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        overlay_hide.clicked.connect(overlay_window.hide_overlay)

        overlay_show = QPushButton("Show Overlay")
        overlay_show.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        overlay_show.clicked.connect(overlay_window.show_overlay)

        close_button = QPushButton("Stop Player")
        close_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        close_button.clicked.connect(self.stop_player)

        cc_layout.addWidget(controller_label,0,0,1,2)
        cc_layout.addWidget(self.pause_play_button,1,0,1,2)
        cc_layout.addWidget(skip_button,2,1)
        cc_layout.addWidget(last_button,2,0)
        cc_layout.addWidget(overlay_show,3,0)
        cc_layout.addWidget(overlay_hide,3,1)
        cc_layout.addWidget(close_button,4,0,1,2)
        self.oldpos = self.pos()

        if overlay_active == False:
            overlay_hide.hide()
            overlay_show.hide()

        self.show()

        ccwin_id = self.winId()

    def pause_player(self):
        if media_player.is_playing():
            media_player.pause()
            self.pause_play_button.setText("Play")
            self.isPaused = True
        else:
            media_player.play()
            self.pause_play_button.setText("Pause")
            self.isPaused = False

    def last_player(self):
        media_player.previous()
        self.pause_play_button.setText("Pause")

    def skip_player(self):
        media_player.next()

    def stop_player(self):
        xwin = self.pos().x()
        ywin = self.pos().y()
        try:
            xoverlay = overlay_pos.x()
        except:
            xoverlay = overlay_pos.split(',')[0]
        try:
            yoverlay = overlay_pos.y()
        except:
            yoverlay = overlay_pos.split(",")[1]
        media_player.stop()
        try:
            DestroyWindow(vframe_id)
        except:
            pass
        try:
            DestroyWindow(ccwin_id)
        except:
            pass
        try:
            DestroyWindow(customwin_id)
        except:
            pass

        ### Writes the last location of the controller and overlay windows,
        # allowing the user to keep a specific layout for the next run.
        with open(app_data+"\\sb_settings.json", "r+") as f:
            fdata = json.load(f)
            fdata["controller-pos"] = (str(xwin)+","+str(ywin))
            fdata["overlay-pos"] = (str(xoverlay)+","+str(yoverlay))
            temp_json = json.dumps(fdata, indent=4)
            f.close()

        with open(app_data+"\\sb_settings.json", "w+") as f:
            f.write(temp_json)

    def close_win(self):
        self.close()

    def center (self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldpos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldpos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldpos = event.globalPos()

### The overlay image that is displayed when the player is started, if
# the "Overlay Active" button is not checked, this will not display.
class overlay_window(QWidget):
    def __init__(self):
        super().__init__()
        win_splits = overlay_pos.split(",")
        xwin = int(win_splits[0])
        ywin = int(win_splits[1])
        splits = overlay_size.split("x")
        self.osize1 = int(splits[0])
        self.osize2 = int(splits[1])
        self.setWindowTitle("Overlay")
        self.setGeometry(xwin,ywin,self.osize1+5,self.osize2+5)
        self.setWindowIcon(QIcon(app_icon))
        self.custom_ui()

    def custom_ui(self):
        global user_overlay, customwin_id
        custom_layout = QGridLayout()
        self.setLayout(custom_layout)

        hbox = QHBoxLayout()

        user_overlay = QLabel("")
        user_overlay.setPixmap(QPixmap(overlay_img).scaled(self.osize1,self.osize2, Qt.KeepAspectRatio))

        self.setWindowFlag(QtCore.Qt.FramelessWindowHint)
        self.setWindowFlag(QtCore.Qt.WindowStaysOnTopHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        hbox.addStretch()
        hbox.addWidget(user_overlay)
        hbox.addStretch()

        custom_layout.addLayout(hbox,0,0)

        self.oldpos = self.pos()

        self.show()

        customwin_id = self.winId()

    def hide_overlay():
        user_overlay.hide()

    def show_overlay():
        user_overlay.show()

    def close_win(self):
        self.close()

    def center (self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldpos = event.globalPos()

    def mouseMoveEvent(self, event):
        global overlay_pos
        delta = QPoint(event.globalPos() - self.oldpos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldpos = event.globalPos()
        overlay_pos = self.pos()

### A test window showing the user what the overlay will look like.
# Can only be called upon in settings, also may be removed and 
# integrated with the overlay_window class in a future release as
# this code is redundant.
class custom_window(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100,100,500,300)
        self.setWindowIcon(QIcon(app_icon))
        self.setStyleSheet("color: {};".format(text_color))
        self.custom_ui()

    def custom_ui(self):

        custom_layout = QGridLayout()
        self.setLayout(custom_layout)

        hbox = QHBoxLayout()

        splits = overlay_size.split("x")
        osize1 = int(splits[0])
        osize2 = int(splits[1])

        overlay = QLabel("")
        overlay.setPixmap(QPixmap(overlay_img).scaled(osize1,osize2, Qt.KeepAspectRatio))

        self.setWindowFlags(QtCore.Qt.FramelessWindowHint)
        self.setAttribute(QtCore.Qt.WA_TranslucentBackground)

        close_button = QPushButton("Close Overlay")
        close_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        close_button.clicked.connect(self.close)

        hbox.addStretch()
        hbox.addWidget(overlay)
        hbox.addStretch()

        custom_layout.addLayout(hbox,0,0)
        custom_layout.addWidget(close_button)
        self.oldpos = self.pos()

        self.show()

    def center (self):
        qr = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        qr.moveCenter(cp)
        self.move(qr.topLeft())

    def mousePressEvent(self, event):
        self.oldpos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint(event.globalPos() - self.oldpos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldpos = event.globalPos()

### The settings window allows for full editing and customization of
# all Stream Buddy's settings. 
class settings_window(QWidget):
    global app_icon, overlay_img

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Settings")
        self.setGeometry(100,100,600,200)
        self.setWindowIcon(QIcon(app_icon))
        self.setStyleSheet("color: {}; background-color: {}".format(text_color, background_color))
        self.settings_ui()

    def settings_ui(self):
        global accounts_list

        self.main_layout = QGridLayout()
        self.setLayout(self.main_layout)

        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("color: #000000;")
        self.tab1 = QWidget()
        self.tab1.setStyleSheet("color: #FFFFFF;")
        self.tab2 = QWidget()
        self.tab2.setStyleSheet("color: #FFFFFF;")
        self.tab3 = QWidget()
        self.tab3.setStyleSheet("color: #FFFFFF;")
        self.tab4 = QWidget()
        self.tab4.setStyleSheet("color: #FFFFFF;")
        self.tab5 = QWidget()
        self.tab5.setStyleSheet("color: #FFFFFF;")
        self.tabs.resize(475,175)

        self.tabs.addTab(self.tab1, "Player Settings")
        self.tabs.addTab(self.tab2, "File Manager")
        self.tabs.addTab(self.tab3, "Change Apperance")
        self.tabs.addTab(self.tab4, "Overlay Window")
        self.tabs.addTab(self.tab5, "About Stream Buddy")

        sett_label = QLabel("Settings")
        sett_label.setFont(QFont("Times", 14, QFont.Bold))
        sett_label.setStyleSheet("color: {}".format(header_text_color))

        sett_text = QLabel("Change the app icon to your channel logo, change Twitch users to download clips from, and more! Make sure to click 'Save Settings' before closing this window!")
        sett_text.setWordWrap(True)

        save_button = QPushButton("Save Settings")
        save_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #52F76A;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #00FF26; font-weight: 900;}""")
        save_button.clicked.connect(self.save_settings)

        close_button = QPushButton("Close Settings")
        close_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        close_button.clicked.connect(self.close_win)

        self.main_layout.addWidget(sett_label)
        self.main_layout.addWidget(sett_text)
        self.main_layout.addWidget(self.tabs)
        self.main_layout.addWidget(save_button)
        self.main_layout.addWidget(close_button)

        self.tab1UI()
        self.tab2UI()
        self.tab3UI()
        self.tab4UI()
        self.tab5UI()

        self.oldpos = self.pos()

        self.show()

    def tab1UI(self):
        layout = QGridLayout()
        self.tab1.setLayout(layout)
        player_label = QLabel("Player Settings")
        player_label.setFont(QFont("Times", 12, QFont.Bold))

        ui_list = ", ".join(accounts_list)

        self.accounts_text = QLabel("Current Account(s) Selected: {}".format(ui_list))
        self.accounts_text.setWordWrap(True)

        account_change = QPushButton("Change Accounts")
        account_change.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        account_change.clicked.connect(self.change_accounts)

        monitor_text = QLabel("Select An Output Monitor: ")

        mon_num = 1
        while len(mons_list) < len(monitors):
            mons_list.append("Monitor {}".format(mon_num))
            mon_num = mon_num + 1

        if disp_monitor == -1:
            currindex = "Monitor 1"
        else:
            currindex = "Monitor {}".format(str(disp_monitor+ 1))

        self.playback_monitor_select = QComboBox()
        self.playback_monitor_select.addItems(mons_list)
        self.playback_monitor_select.setCurrentText(currindex)

        self.random_check = QCheckBox("Randomize Clips")
        if random_clips == False:
            self.random_check.setChecked(False)
        else:
            self.random_check.setChecked(True)

        self.loop_check = QCheckBox("Loop Clips")
        if loop_clips == False:
            self.loop_check.setChecked(False)
        else:
            self.loop_check.setChecked(True)

        self.overlay_check = QCheckBox("Overlay Active")
        if overlay_active == False:
            self.overlay_check.setChecked(False)
        else:
            self.overlay_check.setChecked(True)

        self.reset_locs = QPushButton("Reset Overlay and Controller Locations")
        self.reset_locs.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        self.reset_locs.clicked.connect(self.reset_pos)

        self.spacer = QLabel(" ")
        
        layout.addWidget(player_label,0,0)
        layout.addWidget(self.accounts_text,1,0)
        layout.addWidget(account_change,1,1)
        layout.addWidget(monitor_text,2,0)
        layout.addWidget(self.playback_monitor_select,2,1)
        layout.addWidget(self.random_check,3,0)
        layout.addWidget(self.loop_check,3,1)
        layout.addWidget(self.overlay_check,4,0)
        layout.addWidget(self.reset_locs,5,0,1,2)
        layout.addWidget(self.spacer,6,0,1,2)

    def tab2UI(self):
        layout = QGridLayout()
        self.tab2.setLayout(layout)

        file_label = QLabel("File Manager")
        file_label.setFont(QFont("Times", 12, QFont.Bold))

        self.count_text = QLabel("Files in Download Folder: {}".format(save_loc_count))

        self.file_text = QLabel("Current Download Folder:\n{}".format(save_loc))

        file_change = QPushButton("Change Download Folder")
        file_change.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        file_change.clicked.connect(self.change_downloads)

        layout.addWidget(file_label)
        layout.addWidget(self.count_text)
        layout.addWidget(self.file_text)
        layout.addWidget(file_change)

    def tab3UI(self):
        layout = QGridLayout()
        self.tab3.setLayout(layout)

        icon_hbox = QHBoxLayout()

        color_label = QLabel("Change Appearance")
        color_label.setFont(QFont("Times", 12, QFont.Bold))

        self.icon_text = QLabel("Current Icon: {}".format(app_icon))

        icon_change = QPushButton("Change App Icon")
        icon_change.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        icon_change.clicked.connect(self.change_icon)
        
        self.app_icon_temp = QLabel("")
        self.app_icon_temp.setPixmap(QPixmap(app_icon).scaled(50,50))

        icon_hbox.addStretch()
        icon_hbox.addWidget(self.app_icon_temp)
        icon_hbox.addStretch()

        layout.addWidget(color_label,0,0)
        layout.addWidget(self.icon_text,1,0)
        layout.addLayout(icon_hbox,3,0)
        layout.addWidget(icon_change,4,0)

    def tab4UI(self):
        layout = QGridLayout()
        self.tab4.setLayout(layout)

        overlay_hbox = QHBoxLayout()

        overlay_label = QLabel("Edit Overlay Window")
        overlay_label.setFont(QFont("Times", 12, QFont.Bold))

        self.overlay_text = QLabel("Current Image: {}".format(overlay_img))
        
        self.ui_overlay_img = QLabel("")
        self.ui_overlay_img.setPixmap(QPixmap(overlay_img).scaled(75,75,Qt.KeepAspectRatio))

        overlay_change = QPushButton("Change Overlay Image")
        overlay_change.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                        border-style: solid; border-width: 2px; border-radius: 10px;
                                        border-color: #0030ff; padding: 6px;}
                                        QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        overlay_change.clicked.connect(self.change_overlay)

        overlay_size_text = QLabel("""
Use the box to the right to change the size (in pixels) of your
overlay image. Type a width and height seperated by an 'x'.
Example (300x300)""")

        self.overlay_size_edit = QLineEdit()
        self.overlay_size_edit.setText(overlay_size)
        
        overlay_view = QPushButton("View Overlay")
        overlay_view.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        overlay_view.clicked.connect(custom_button)

        overlay_hbox.addStretch()
        overlay_hbox.addWidget(self.ui_overlay_img)
        overlay_hbox.addStretch()

        layout.addWidget(overlay_label,0,0)
        layout.addWidget(self.overlay_text,1,0,1,2)
        layout.addLayout(overlay_hbox,2,0,1,2)
        layout.addWidget(overlay_change,3,0,1,2)
        layout.addWidget(overlay_size_text,4,0)
        layout.addWidget(self.overlay_size_edit,4,1)
        layout.addWidget(overlay_view,5,0,1,2)

    def tab5UI(self):
        layout = QGridLayout()
        self.tab5.setLayout(layout)

        update_label = QLabel("Update Stream Buddy")
        update_label.setFont(QFont("Times", 12, QFont.Bold))

        wdupdate_text = QLabel("""
NOTE: Clicking the button below does not update Stream Buddy. This will only update the software used to download your clips.""")
        wdupdate_text.setWordWrap(True)

        wd_update = QPushButton("Update Webdriver")
        wd_update.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        wd_update.clicked.connect(self.driver_updater)

        about_label = QLabel("About Stream Buddy")
        about_label.setFont(QFont("Times", 12, QFont.Bold))

        about_text = QLabel("Stream Buddy is a 100% Python based desktop app that allows content creators to play and download their clips to use as a BRB screen or whatever they may choose. This project was inspired by and built for my brother @SteelDrifter.")
        about_text.setWordWrap(True)

        donate_button = QPushButton("Donate!")
        donate_button.setStyleSheet("""QPushButton{color: #11052C; background-color: #BDBDBD;
                                    border-style: solid; border-width: 2px; border-radius: 10px;
                                    border-color: #0030ff; padding: 6px;}
                                    QPushButton:hover{background-color: #FFFFFF; font-weight: 900;}""")
        donate_button.clicked.connect(self.donations)

        version_text = QLabel("Stream Buddy v1.1.0 - ZTD Apps")

        layout.addWidget(update_label)
        layout.addWidget(wdupdate_text)
        layout.addWidget(wd_update)
        layout.addWidget(about_label)
        layout.addWidget(about_text)
        layout.addWidget(donate_button)
        layout.addWidget(version_text)

    def change_accounts(self):
        acc_box, ok = QInputDialog.getText(self, "Change Accounts", "Add multiple accounts, seperated by commas, or just one.\nNOTE: Using this box will result in all accounts being reset!")

        if ok and acc_box:
            self.accounts_input = acc_box
            self.accounts_text.setText("Current Account(s) Selected: {}".format(self.accounts_input))

            settings["accounts-list"] = self.accounts_input

    def reset_pos(self):
        global overlay_pos, controller_pos
        overlay_pos = "100,100"
        controller_pos = "100,100"
        self.save_settings()

    def donations(self):
        system("start https://www.paypal.com/donate/?hosted_button_id=272K99TCEWJCJ")

    def change_downloads(self):
        self.fbrowse = QFileDialog().getExistingDirectory()

        if self.fbrowse != "":
            path, dirs, files = next(walk(self.fbrowse))
            self.fcount = len(files)

            self.count_text.setText("Files in Download Folder: {}".format(self.fcount))
            self.file_text.setText("Current Download Folder:\n{}".format(self.fbrowse))

            settings["save-loc"] = self.fbrowse
            settings["save-loc-count"] = self.fcount
        else:
            mbox = QMessageBox.warning(self, "No valid folder selected.", "Please select a valid folder.")

    def change_icon(self):
        self.icon_diag = QFileDialog().getOpenFileName()
        self.ibrowse = self.icon_diag[0]
        
        if self.ibrowse.endswith((".jpeg",".png",".PNG","ico",".jpg",".tiff")):
            self.icon_text.setText("Current Icon:\n{}".format(self.ibrowse))
            self.app_icon_temp.setPixmap(QPixmap(self.ibrowse).scaled(50,50))
            settings["app-icon"] = self.ibrowse

        else:
            mbox = QMessageBox.warning(self, "Error", "Please select a valid image file.")

    def change_overlay(self):
        global overlay_img
        self.over_diag = QFileDialog().getOpenFileName()
        self.obrowse = self.over_diag[0]
        
        if self.obrowse.endswith((".jpeg",".png",".PNG","ico",".jpg",".tiff")):
            self.overlay_text.setText("Current Icon:\n{}".format(self.obrowse))
            self.ui_overlay_img.setPixmap(QPixmap(self.obrowse).scaled(75,75))
            overlay_img = self.obrowse
            settings["overlay-img"] = self.obrowse

        else:
            mbox = QMessageBox.warning(self, "Error", "Please select a valid image file.")

    def driver_updater(self):
        try:
            rmtree(app_data+"\\WebDrivers")
        except:
            pass
        soft_list = []
        for software in get_installed_software():
            if str(software["name"]).__contains__("Chrome") or str(software["name"]).__contains__("Firefox"):
                entry = software["name"], software["version"]
                soft_list.append(entry)
        
        with tempfile.TemporaryDirectory() as temp_dir:
            try:
                if not exists(app_data+"\\WebDrivers"):
                    makedirs(app_data+"\\WebDrivers")        
                for item in soft_list:
                    if str(item[0]).__contains__("Chrome"):
                        version = str(item[1])
                        url_one = "https://chromedriver.storage.googleapis.com/"
                        url_two = "/chromedriver_win32.zip"
                        comp_url = url_one+version+url_two
                        urllib.request.urlretrieve(comp_url, temp_dir+"\\chromedriver_win32.zip")
                        filepath = temp_dir+"\\chromedriver_win32.zip"
                        with zipfile.ZipFile(filepath, "r") as zip_ref:
                            zip_ref.extractall(app_data+"\\WebDrivers")
                    if str(item[0]).__contains__("Firefox"):
                        fire_link = "https://github.com/mozilla/geckodriver/releases/download/v0.30.0/geckodriver-v0.30.0-win64.zip"
                        urllib.request.urlretrieve(fire_link, temp_dir+"\\geckodriver-v0.30.0-win64.zip")
                        file_path = temp_dir+"\\geckodriver-v0.30.0-win64.zip"
                        with zipfile.ZipFile(file_path, "r") as zip_ref:
                            zip_ref.extractall(app_data+"\\WebDrivers")
                mbox = QMessageBox.information(self, "Web Drivers Updated!", "Your web drivers have sucessfully been updated.\nRestart Stream Buddy and try downloading clips again.")
            except:
                mbox = QMessageBox.warning(self, "Error!", "Web drivers were not updated.\nTry again or refer to the help manual.")

    ### The "settings" dict is called and all settings in this window are appended.
    # The dict is then encoded to a json file where it is saved until the user calls
    # the app again. This results in the user needing to restart the app after 
    # changes are made to the file.
    def save_settings(self):
        global overlay_size, random_num, loop_num, random_clips, loop_clips

        accounts_list = []
        try:
            splits = self.accounts_input.split(",")
            for temp_item in splits:
                item = temp_item.replace(" ","")
                accounts_list.append(item)
        except:
            pass

        if self.playback_monitor_select.currentText() == "Monitor 1":
            disp_monitor = -1
        else:
            monitor_num = int(self.playback_monitor_select.currentText().split(" ")[1])-1
            disp_monitor = monitor_num

        if self.random_check.isChecked():
            random_num = "1"
            random_clips = True
        else:
            random_num = "0"
            random_clips = False

        if self.loop_check.isChecked():
            loop_num = "1"
            loop_clips = False
        else:
            loop_num = "0"
            loop_clips = False

        if self.overlay_check.isChecked():
            overlay_num = "1"
            overlay_active = True
        else:
            overlay_num = "0"
            overlay_active = False

        if self.overlay_size_edit.text().__contains__("x"):
            overlay_size = self.overlay_size_edit.text()
        else:
            mbox = QMessageBox.warning(self, "Format Error!", "Please make sure your overlay size has an 'x' to seperate the two values.\n(300x300)")
        
        if len(accounts_list) == 0:
            temp_str = self.accounts_text.text()
            new_str = temp_str.replace("Current Account(s) Selected: ","")
            str_splits = new_str.split(",")
            settings["accounts-list"] = str_splits
        else:
            settings["accounts-list"] = accounts_list
        settings["disp-monitor"] = disp_monitor
        settings["random-clips"] = random_num
        settings["loop-clips"] = loop_num
        settings["overlay-active"] = overlay_num
        settings["controller-pos"] = controller_pos
        settings["overlay-size"] = overlay_size
        settings["overlay-pos"] = overlay_pos
        try:
            settings["save-loc-count"] = self.fcount
        except:
            settings["save-loc-count"] = save_loc_count
        try:
            settings["save-loc"] = self.fbrowse
        except:
            settings["save-loc"] = save_loc
        try:
            settings["app-icon"] = self.ibrowse
        except:
            settings["app-icon"] = app_icon
        try:
            settings["overlay-img"] = self.obrowse
        except:
            settings["overlay-img"] = overlay_img


        temp_json = json.dumps(settings, indent=4)
        with open(app_data+"\\sb_settings.json", "w+") as f:
            f.write(temp_json)

        if overlay_size.__contains__("x"):
            mbox = QMessageBox.information(self, "Settings Saved!", "Your new settings have been saved!")
        else:
            pass

    def close_win(self):
        self.close()
        mbox = QMessageBox.information(self, "Restart Stream Buddy!", "In order for changes to take effect, make sure to restart Stream Buddy!")

### The QThread class that connects to download buttons in Stream Buddy.
# Based on the window this is called from, either the top 100 most viewed
# clips are downloaded or the list of clips set in the list creator. If a
# clip is already in the selected directory, it is skipped, removing dups.
class clip_downloader(QThread):
    global dcode
    send_progress = pyqtSignal(int)
    curr_num = pyqtSignal(int)
    dfinished = pyqtSignal()
    dcode = 0

    @pyqtSlot()
    def clip_grabber(self):
        global save_loc, loc_count, numclips_count
        folder_loc = save_loc

        curr_clips = []
        path, dirs, files = next(walk(folder_loc))
        for file in files:
            clip = MP4(folder_loc+"\\"+file)
            try:
                clip_id = clip["©nam"]
                curr_clips.append(clip_id[0])
            except:
                pass
        try:
            if folder_loc != "" and len(dl_list) == 0:
                temp_ids = []
                clip_num = 0
                status_text.setText("Grabbing clips from Twitch. You may want to make a cup of coffee...")
                twitch = Twitch(client_id,client_secret, authenticate_app=True)
                try:
                    get_ids = twitch.get_users(logins=accounts_list)
                    iresponse = get_ids["data"]

                    for item in iresponse:
                        twid = str(item["id"])
                        temp_ids.append(twid)

                    numclips_count = 0
                    for item in temp_ids:
                        numclips = twitch.get_clips(item, first=100)
                        response = numclips["data"]
                        
                        for item in response:
                            vid_id = str(item["id"])
                            if (vid_id not in curr_clips):
                                numclips_count = 1 + numclips_count
                            else:
                                pass
                    clip_num = 1
                    for item in temp_ids:
                        clips = twitch.get_clips(item, first=100)
                        response = clips["data"]
                        try:
                            doptions = webdriver.ChromeOptions()
                            doptions.add_argument("--headless")
                            doptions.add_argument("--mute-audio")
                            doptions.set_headless(True)
                            try:
                                driver = webdriver.Chrome(executable_path="WebDrivers\\chromedriver.exe", options=doptions)
                            except:
                                driver = webdriver.Chrome(options=doptions)
                            driver.create_options()
                        except:
                            doptions = webdriver.FirefoxOptions()
                            doptions.add_argument("--headless")
                            doptions.add_argument("--mute-audio")
                            doptions.set_headless(True)
                            try:
                                driver = webdriver.Firefox(executable_path="WebDrivers\\geckodriver.exe", firefox_options=doptions)
                            except:
                                driver = webdriver.Firefox(options=doptions)
                            
                        driver.set_window_position(-4000,-4000)
                        
                        for item in response:
                            if dcode == 1:
                                break
                            self.send_progress.emit(clip_num)
                            self.curr_num.emit(clip_num)
                            vid_id = str(item["id"])
                            if (vid_id not in curr_clips):
                                driver.get(str(item["url"]))
                                
                                time.sleep(2)
                                source = driver.page_source

                                soup = BeautifulSoup(source, "html.parser")
                                links = []
                                for link in soup.find_all("video"):
                                    links.append(link)
                                vid = str(links[0]).split("\"")
                                vid_link = vid[3]
                                
                                vid_url = vid_link.replace("amp;","")
                                folder_loc = save_loc
                                curr_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
                                file_name = "/clip-"+str(curr_time)+".mp4"
                                save_dir = folder_loc+file_name

                                try:
                                    urllib.request.urlretrieve(vid_url, save_dir)
                                except:
                                    pass
                                mp4_file = MP4(save_dir)
                                mp4_file["©nam"] = vid_id
                                mp4_file.save()
                            clip_num = clip_num + 1
                    direct = listdir(folder_loc)
                    loc_count = str(len([name for name in direct]))
                    self.dfinished.emit()
                    driver.close()
                except:
                    loc_count = 0
                    self.dfinished.emit()
            if len(dl_list) != 0:
                clip_num = 1
                numclips_count = 0
                try:
                    doptions = webdriver.ChromeOptions()
                    doptions.add_argument("--headless")
                    doptions.add_argument("--mute-audio")
                    doptions.set_headless(True)
                    try:
                        driver = webdriver.Chrome(executable_path="WebDrivers\\chromedriver.exe", options=doptions)
                    except:
                        driver = webdriver.Chrome(options=doptions)
                    driver.create_options()
                except:
                    doptions = webdriver.FirefoxOptions()
                    doptions.add_argument("--headless")
                    doptions.add_argument("--mute-audio")
                    doptions.set_headless(True)
                    try:
                        driver = webdriver.Firefox(executable_path="WebDrivers\\geckodriver.exe", firefox_options=doptions)
                    except:
                        driver = webdriver.Firefox(options=doptions)
                            
                        
                for item in dl_list:
                    if item.__contains__("?"):
                        url = item.split("/")
                        url_string = (url[5]).split("?")
                        vid_id = url_string[0]
                    else:
                        vid_id = item
                    if (vid_id not in curr_clips):
                        numclips_count = 1 + numclips_count
                    else:
                        pass
                    if dcode == 1:
                        break
                    self.send_progress.emit(clip_num)
                    if (vid_id not in curr_clips):
                        driver.get(item)
                    
                        time.sleep(2)
                        
                        source = driver.page_source
                    
                        soup = BeautifulSoup(source, "html.parser")

                        links = []
                        for link in soup.find_all("video"):
                            links.append(link)

                        vid = str(links[0]).split("\"")
                        vid_link = vid[3]
                        
                        vid_url = vid_link.replace("amp;","")
                        
                        folder_loc = save_loc
                        curr_time = datetime.now().strftime("%m-%d-%Y-%H-%M-%S")
                        file_name = "/clip-"+str(curr_time)+".mp4"
                        save_dir = folder_loc+file_name

                        try:
                            urllib.request.urlretrieve(vid_url, save_dir)
                        except:
                            pass
                        mp4_file = MP4(save_dir)
                        mp4_file["©nam"] = vid_id
                        mp4_file.save()
                    clip_num = clip_num + 1
                direct = listdir(folder_loc)
                loc_count = str(len([name for name in direct]))
                self.dfinished.emit()
                driver.close()
        except:            
            status_text.setText("Could not download clips. Please update Webdrivers in Settings or check the documentation by clicking Help!")      

### The PyQT main loop. This checks to see if the save_loc var is a
# blank string. If TRUE, the app will run the VLC setup prompt.
def main():
    global App
    App = QApplication(sys.argv)
    if save_loc == "":
        setup()
    else:
        window = Window()
        sys.exit(App.exec_())

if __name__ == "__main__":
    main()

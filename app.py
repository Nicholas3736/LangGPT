#This code brings together all of the code from the other files, 
#creates the needed directories, and runs the app.

#Written by Nicholas Baker
import os
import sqlite3
import sys
sys.path.append(os.path.dirname(__file__) + "/assets/gui")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow, QStackedLayout, QWidget
from assets.gui.Main_Screen import MainScreen
from assets.gui.settings_screen import SettingsScreen


class App(QMainWindow):
    def __init__(self):    
        super().__init__()
        self.setWindowTitle("LangGPT")
        self.resize(QSize(500, 400))
        self.setMinimumSize(200, 300)
        
        self.stackLayout = QStackedLayout()
        self.mainScreen = MainScreen()
        self.settingsScreen = SettingsScreen()
        self.stackLayout.addWidget(self.mainScreen)
        self.stackLayout.addWidget(self.settingsScreen)
        
        w = QWidget()
        w.setLayout(self.stackLayout)
        self.setCentralWidget(w)
    
    def displaySettings(self, chatName):

        #retrieve the settings for the chat to display them on the settings screen
        languageSetting = ""
        responseLengthSetting = ""
        
        try:
            os.chdir(os.path.dirname(__file__) + "/assets")
            conn = sqlite3.connect(os.getcwd() + "/SettingsDB.db")
            cursor = conn.cursor()

            settings = cursor.execute("SELECT * FROM ChatSettings WHERE name = ?", (chatName,))
            settings = settings.fetchall()

            languageSetting = settings[0][1]
            responseLengthSetting = settings[0][2]
            print(settings)
        except sqlite3.Error as e:
            print(e)

        self.settingsScreen.chatName = chatName
        self.settingsScreen.languageBox.setCurrentText(languageSetting)
        
        if responseLengthSetting == "short":
            self.settingsScreen.responseLengthButtonGroup.button(1).setChecked(True)
        elif responseLengthSetting == "medium":
            self.settingsScreen.responseLengthButtonGroup.button(2).setChecked(True)
        else:
            self.settingsScreen.responseLengthButtonGroup.button(3).setChecked(True) 

        self.stackLayout.setCurrentIndex(1)

    def displayMainScreen(self):
        self.stackLayout.setCurrentIndex(0)

#Set up and run the app.
os.chdir(os.path.dirname(__file__))

app = QApplication([])
program = App()
program.show()
app.exec()
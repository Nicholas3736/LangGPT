#This code brings together all of the code from the other files, 
#creates the needed directories, and runs the app.

#Written by Nicholas baker
import os
import sys
sys.path.append(os.path.dirname(__file__) + "/assets/gui")

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow
from assets.gui.Main_Screen import MainScreen


class App(QMainWindow):
    def __init__(self):    
        super().__init__()
        self.setWindowTitle("LangGPT")
        self.resize(QSize(500, 400))
        self.setMinimumSize(200, 300)
        w = MainScreen()
        self.setCentralWidget(w)

#Set up and run the app.
os.chdir(os.path.dirname(__file__) + "/assets")
folders = os.listdir()
if "chats" not in folders: os.mkdir("chats")
if "prompts" not in folders: os.mkdir("prompts")
os.chdir(os.path.dirname(__file__))

app = QApplication([])
program = App()
program.show()
app.exec()
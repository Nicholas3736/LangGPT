#This code brings together all of the code from the other files, 
#creates the needed directories, and runs the app.

#Written by Nicholas baker

from PySide6.QtCore import QSize
from PySide6.QtWidgets import QApplication, QMainWindow
from main_screen import MainScreen

class App(QMainWindow):
    def __init__(self):    
        super().__init__()
        self.setWindowTitle("LangGPT")
        self.resize(QSize(500, 400))
        self.setMinimumSize(200, 300)
        w = MainScreen()
        self.setCentralWidget(w)

#Set up and run the app.
app = QApplication([])
program = App()
program.show()
app.exec()
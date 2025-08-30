#This code implements the main screen that you see when using the app 
#(The chat and the chat selection menu on the left).

#Written by Nicholas baker
import os
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import QWidget, QHBoxLayout
from Chat_Panel import ChatPanel
from key_input_screen import KeyInputScreen
from Chat_Select_Panel import ChatSelectPanel
import random

#Temporary function to color whatever widget is passed in a random color.
#This is so that we can see the borders for the widgets easier.
def colorRandom(w):
    red = random.randint(0, 255)
    green = random.randint(0, 255)
    blue = random.randint(0, 255)
    w.setAutoFillBackground(True)
    palette = w.palette()
    palette.setColor(QPalette.ColorRole.Window, QColor(red, green, blue))
    w.setPalette(palette)

#This class represents the entire screen that the user sees while chatting
class MainScreen(QWidget):
    def __init__(self):
        super().__init__()
        print("DIRECTORY: " + os.path.dirname(__file__))
        self.currentChat = ""

        #Prompt for the API key to be used
        keyInput = KeyInputScreen()
        keyInput.exec()

        self.chatPanel = ChatPanel(keyInput.getInput())
        chatSelectPanel = ChatSelectPanel()

        layout = QHBoxLayout()
        layout.addWidget(chatSelectPanel, stretch = 4)
        layout.addWidget(self.chatPanel, stretch = 10)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def setChat(self, chatName):
        self.currentChat = chatName
        self.chatPanel.loadChat(self.currentChat)
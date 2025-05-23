#This code implements the main screen that you see when using the app 
#(The chat and the chat selection menu).

#Written by Nicholas baker

from groq import Groq
from key_input_screen import KeyInputScreen
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QLineEdit, 
    QPushButton,
    QScrollArea
)
import os
import random

#This class represents the entire screen that the user sees while chatting
class MainScreen(QWidget):
    def __init__(self):
        super().__init__()

        #Prompt for the API key to be used
        keyInput = KeyInputScreen()
        keyInput.exec()

        scrollArea = QScrollArea()

        chatPanel = ChatPanel(keyInput.getInput())
        chatSelectPanel = ChatSelectPanel()
        scrollArea.setWidget(chatSelectPanel)

        layout = QHBoxLayout()        
        layout.addWidget(chatSelectPanel, stretch = 4)
        layout.addWidget(chatPanel, stretch = 10)
        self.setLayout(layout)


#The panel to the left on the MainScreen, where the user
#can select and swtich between chats.
class ChatSelectPanel(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()
        for i in range(5):
            widget = QWidget()
            widget.setAutoFillBackground(True)
            red = random.randint(0, 255)
            green = random.randint(0, 255)
            blue = random.randint(0, 255)
            layout.addWidget(ChatIcon(red, green, blue))
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)
        

#This class represents an icon for an individual chat that the user can
#select on the left hand side.
class ChatIcon(QWidget):
    def __init__(self, r, g, b):
        super().__init__()
        layout = QHBoxLayout()
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(r, g, b))
        self.setPalette(palette)
        self.setLayout(layout)

#The panel where the chatting takes place. This is also where the API is run.
class ChatPanel(QWidget):
    def __init__(self, apiKey):
        super().__init__()
        self.APIConnection = Groq(api_key = apiKey)
        print("API key: " + apiKey)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        self.setPalette(palette)

        self.displayArea = ChatDisplayArea()
        scrollArea = QScrollArea()
        scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        scrollArea.setWidgetResizable(True)
        scrollArea.setStyleSheet('background: transparent;')
        scrollArea.setLayout(QVBoxLayout())
        scrollArea.setWidget(self.displayArea)

        layout = QVBoxLayout()
        layout.addWidget(scrollArea, stretch = 1)
        layout.addWidget(ChatInputArea(self))

        self.setLayout(layout)

    #Receives a message from the input panel, sends it to the
    #Groq API, and displays both the user message and response
    def sendMessage(self, msg):
        chat_completion = self.APIConnection.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": msg,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        self.displayArea.displayMessage("User: " + msg + "\n\nBot: " 
                                        + chat_completion.choices[0].message.content)

#This class represents the area where the messages in the chat are displayed. This is the
#middle section of the MainScreen.  
class ChatDisplayArea(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.setLayout(layout)
    
    #Displays the massage passed in on the chat screen.
    def displayMessage(self, msg):
        text = QLabel(msg)
        text.setStyleSheet("color: #000000; background-color: #f5f5f5;")
        self.layout().addWidget(text)

        #Adds a stretch at the end of the layout if displaying the bot's message.
        #This is to ensure that the messages are spaced properly.
        if msg[0] == 'B':
            self.layout().addStretch(5)

#This class represents the section of the MainScreen where the 
#user types their messages during a chat
class ChatInputArea(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        layout = QHBoxLayout()
        
        self.inputArea = QLineEdit()
        layout.addWidget(self.inputArea)

        button = QPushButton("Send")
        button.clicked.connect(self.sendMessage)
        layout.addWidget(button)
        
        self.setLayout(layout)

    #When the send button is pressed, pass the input from the
    #input box to the ChatPanel for processing.
    def sendMessage(self):
        msg = self.inputArea.text()
        self.inputArea.clear()
        self.parent.sendMessage(msg)
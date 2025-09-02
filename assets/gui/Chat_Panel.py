from groq import Groq, APIConnectionError
import math
import os
from PySide6.QtCore import Qt
from PySide6.QtGui import QColor, QPalette, QFont
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QLineEdit, 
    QPushButton,
    QScrollArea,
    QTextEdit
)
import sqlite3


#The panel where the chatting takes place. This is also where the API is run.
class ChatPanel(QWidget):
    def __init__(self, apiKey):
        super().__init__()
        self.language = ""
        self.responseLength = ""
        self.APIConnection = Groq(api_key = apiKey)
        print("API key: " + apiKey)

        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        self.setPalette(palette)

        self.header = chatHeaderArea("")
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.Window, QColor(245, 245, 245))
        self.setPalette(palette)

        self.displayArea = ChatDisplayArea()
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setStyleSheet('background: transparent;')
        self.scrollArea.setLayout(QVBoxLayout())
        self.scrollArea.setWidget(self.displayArea)

        self.mainlayout = QVBoxLayout()
        self.mainlayout.addWidget(self.header, stretch = 1)
        self.mainlayout.addWidget(self.scrollArea, stretch = 5)
        self.mainlayout.addWidget(ChatInputArea(self))

        self.setLayout(self.mainlayout)

    def loadChat(self, chatName):
        print("Loading " + chatName)

        #Insert a new header panel to reflect the new chat
        self.layout().removeWidget(self.header)
        self.header.setParent(None)
        newHeader = chatHeaderArea(chatName)
        self.layout().insertWidget(0, newHeader)
        self.header = newHeader

        #Show the new chat itself by replacing the chat display area
        newDisplay = ChatDisplayArea(chatName)
        self.layout().removeWidget(self.scrollArea)
        self.displayArea.setParent(None)
        self.scrollArea.setWidget(newDisplay)
        self.layout().insertWidget(1, self.scrollArea)
        self.displayArea = newDisplay

        try:
            os.chdir(os.path.dirname(__file__)[:-4])
            conn = sqlite3.connect("SettingsDB.db")
            cursor = conn.cursor()

            settings = cursor.execute("SELECT * FROM ChatSettings WHERE name = ?", (chatName,))
            settings = settings.fetchone()
            self.language = settings[0][1]
            self.responseLength = settings[0][2]
        except sqlite3.Error as e:
            print(e)

    #Receives a message from the input panel, sends it to the
    #Groq API, and displays both the user message and response.
    #Also saves the user's and the AI's messages.
    def sendMessage(self, msg):
        print(self.displayArea.msgNum)
        userMessage = "User: " + msg
        self.displayArea.displayMessage(userMessage)
        try:
            chat_completion = self.APIConnection.chat.completions.create(
                messages=[
                    {
                        "role": "system",
                        "content": "You must give your answer in " + self.language + " and keep it at " 
                        + self.responseLength + " length."
                    },
                    {
                        "role": "user",
                        "content": msg,
                    }
                ],
                model="llama-3.3-70b-versatile",
            )
            response = "Bot: " + chat_completion.choices[0].message.content
        except APIConnectionError:
            print("Error connecting with the API. Displaying dummy message for the bot instead.")
            response = "Bot: API connection failed. This is a dummy response."
        self.displayArea.displayMessage(response)

        #record the messages in the message log
        os.chdir(os.path.dirname(__file__)[:-4] + "/chats/" + self.parent().currentChat)
        
        try:
            outFile = open(str(self.displayArea.msgNum + 1) + ".txt", encoding = "utf-16", mode = "w")
            outFile.write(userMessage)
            outFile.close()

            outFile = open(str(self.displayArea.msgNum + 2) + ".txt", encoding = "utf-16", mode = "w")
            outFile.write(response)
            outFile.close()
        except Exception as e:
            print(e)
        os.chdir(os.path.dirname(__file__))

        self.displayArea.msgNum += 2

class chatHeaderArea(QWidget):
    def __init__(self, chatName):
        super().__init__()
        layout = QHBoxLayout()

        self.title = QLabel(chatName)
        self.title.setStyleSheet("color: #000000;")
        layout.addWidget(self.title)

        button = QPushButton("...")
        layout.addWidget(button)

        
        self.setLayout(layout)

#This class represents the area where the messages in the chat are displayed. This is the
#middle section of the MainScreen. 
class ChatDisplayArea(QWidget):
    def __init__(self, chatName = ""):
        super().__init__()
        self.setLayout(QVBoxLayout())

        #Load the chat into the display
        if chatName != "":
            os.chdir(os.path.dirname(__file__)[:-4] + "/chats/" + chatName)
            messages = os.listdir()

            if len(messages):
                print(messages)
                messages = sorted(messages, key = lambda x: int(x[:-4:]))
                self.msgNum = int(messages[-1][:-4:])
            else:
                self.msgNum = 0

            for msg in messages:
                try:
                    print("Reading " + msg + " in " + chatName)
                    outFile = open(msg, encoding = "utf-16", mode = "r")
                    content = outFile.read()
                    
                    self.displayMessage(content)
                    outFile.close()
                except Exception as e:
                    print(e)
            os.chdir(os.path.dirname(__file__))
        else:
            self.msgNum = 0
    
    #Displays the massage passed in on the chat screen.
    def displayMessage(self, msg):
        print("Displaying " + msg)
        text = QTextEdit(msg)
        text.setReadOnly(True)

        rows = math.ceil(len(msg) / 46)
        text.setMinimumHeight(80 + (rows - 3) * 20)

        text.setFont(QFont("Calibri", 11))
        text.setStyleSheet("color: #000000; background-color: #f5f5f5;")
        self.layout().addWidget(text, stretch = 1)

        #Adds a stretch at the end of the layout if displaying the bot's message.
        #This is to ensure that the messages are spaced properly.
        # if msg[0] == 'B':
        #     self.layout().addStretch(5)


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
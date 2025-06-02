#This code implements the main screen that you see when using the app 
#(The chat and the chat selection menu).

#Written by Nicholas baker

from groq import Groq
from key_input_screen import KeyInputScreen
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QLineEdit, 
    QPushButton,
    QScrollArea,
    QInputDialog,
    QSizePolicy
)
import os
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

#This class represents the entire screen that the user sees while chattin
class MainScreen(QWidget):
    def __init__(self):
        super().__init__()

        self.currentChat = ""

        #Prompt for the API key to be used
        keyInput = KeyInputScreen()
        keyInput.exec()

        self.chatPanel = ChatPanel(self, keyInput.getInput())
        chatSelectPanel = ChatSelectPanel(self)

        layout = QHBoxLayout()
        layout.addWidget(chatSelectPanel, stretch = 4)
        layout.addWidget(self.chatPanel, stretch = 10)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def setChat(self, chatName):
        self.currentChat = chatName
        self.chatPanel.loadChat(self.currentChat)


#The panel to the left on the MainScreen, where the user
#can select and swtich between chats.
class ChatSelectPanel(QWidget):
    def __init__(self, parent):
        super().__init__()
        self.parent = parent
        self.currentChat = None
        self.layout = QVBoxLayout()

        #Top panel (where the "new chat" button is)
        upperPanel = QHBoxLayout()
        newChatButton = QPushButton("New Chat")
        newChatButton.clicked.connect(self.createChat)
        upperPanel.addWidget(newChatButton)
        self.layout.addLayout(upperPanel)

        #Create ChatIcons for all of the existing chats
        rootwd = os.getcwd()
        os.chdir("assets/chats")
        chats = os.listdir()
        lowerPanel = QVBoxLayout()

        for chat in chats:
            lowerPanel.addWidget(ChatIcon(chat, self))
        os.chdir(rootwd)

        lowerPanel.addStretch()
        lowerPanel.setSpacing(0)
        lowerPanel.setContentsMargins(0, 0, 0, 0)

        w = QWidget()
        w.setLayout(lowerPanel)
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(w)
        self.layout.addWidget(self.scrollArea)

        self.setLayout(self.layout)
    
    def createChat(self):
        rootDir = os.getcwd()
        os.chdir("assets/chats")
        name, ok = QInputDialog.getText(self, "New Chat",
                                    "Enter the name of the chat:", QLineEdit.Normal)
        chats = os.listdir()

        while ok and (name.strip() == "" or name in chats):
            name, ok = QInputDialog.getText(self, "New Chat",
                                    "Invalid name\n\nEnter the name of " \
                                    "the chat:", QLineEdit.Normal)
        
        if ok:
            os.mkdir(name)
            layout = self.scrollArea.widget().layout()
            layout.insertWidget(layout.count() - 1, ChatIcon(name, self))
        os.chdir(rootDir)

        

#This class represents an icon for an individual chat that the user can
#select on the left hand side.
class ChatIcon(QWidget):
    def __init__(self, name, parent):
        super().__init__()
        self.parent = parent
        layout = QHBoxLayout()
        self.link = ClickableText(name)

        self.link.clicked.connect(self.selected)
        
        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(50)
        colorRandom(self.link)
        layout.addWidget(self.link)
        layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(layout)

    def selected(self):
        self.parent.parent.setChat(self.link.text())

#This represents the text on each chatIcon.
#This is needed to make the text clickable.
class ClickableText(QLabel):
    clicked = Signal(str)

    def __init__(self, text):
        super().__init__(text)
        self.mousePressed = False

    def mousePressEvent(self, ev):
        self.mousePressed = True

    def mouseReleaseEvent(self, ev):
        if self.mousePressed:
            self.mousePressed = False
            self.clicked.emit("clicked")
            colorRandom(self)
    
#The panel where the chatting takes place. This is also where the API is run.
class ChatPanel(QWidget):
    def __init__(self, parent, apiKey):
        super().__init__()
        self.parent = parent
        self.APIConnection = Groq(api_key = apiKey)
        print("API key: " + apiKey)

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
        self.mainlayout.addWidget(self.scrollArea, stretch = 1)
        self.mainlayout.addWidget(ChatInputArea(self))

        self.setLayout(self.mainlayout)

    def loadChat(self, chatName):
        print("Loading " + chatName)
        newDisplay = ChatDisplayArea(chatName)
        self.layout().removeWidget(self.scrollArea)
        self.displayArea.setParent(None)
        self.scrollArea.setWidget(newDisplay)
        self.layout().insertWidget(0, self.scrollArea)
        self.displayArea = newDisplay

    #Receives a message from the input panel, sends it to the
    #Groq API, and displays both the user message and response.
    #Also saves the user's and the AI's messages.
    def sendMessage(self, msg):
        print(self.displayArea.msgNum)
        userMessage = "User: " + msg
        self.displayArea.displayMessage(userMessage)
        chat_completion = self.APIConnection.chat.completions.create(
            messages=[
                {
                    "role": "user",
                    "content": msg,
                }
            ],
            model="llama-3.3-70b-versatile",
        )
        response = "Bot: " + chat_completion.choices[0].message.content
        self.displayArea.displayMessage(response)

        #record the messages in the message log
        cwd = os.getcwd()
        os.chdir("assets/chats/" + self.parent.currentChat)
        
        try:
            outFile = open(str(self.displayArea.msgNum + 1) + ".txt", "w")
            outFile.write(userMessage)
            outFile.close()

            outFile = open(str(self.displayArea.msgNum + 2) + ".txt", "w")
            outFile.write(response)
            outFile.close()
        except Exception as e:
            print(e)
        os.chdir(cwd)

        self.displayArea.msgNum += 2

#This class represents the area where the messages in the chat are displayed. This is the
#middle section of the MainScreen.  
class ChatDisplayArea(QWidget):
    def __init__(self, chatName = ""):
        super().__init__()
        self.setLayout(QVBoxLayout())

        #Load the chat into the display
        if chatName != "":
            cwd = os.getcwd()
            os.chdir("assets/chats/" + chatName)
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
                    outFile = open(msg)
                    content = outFile.read()
                    
                    text = QLabel(content)
                    text.setStyleSheet("color: #000000; background-color: #f5f5f5;")
                    self.layout().addWidget(text)
                    outFile.close()

                    if content[0] == 'B':
                        self.layout().addStretch(5)
                except:
                    print("Something bad happened")
            os.chdir(cwd)
        else:
            self.msgNum = 0
    
    #Displays the massage passed in on the chat screen.
    def displayMessage(self, msg):
        print("Displaying " + msg)
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
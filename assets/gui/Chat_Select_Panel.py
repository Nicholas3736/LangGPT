import os
import random
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPalette, QAction, QCursor
from PySide6.QtWidgets import (
    QWidget, 
    QVBoxLayout, 
    QHBoxLayout, 
    QLabel, 
    QLineEdit,
    QMenu, 
    QPushButton,
    QScrollArea,
    QInputDialog,
    QSizePolicy
)
import shutil
import sqlite3


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

#The panel to the left on the MainScreen, where the user
#can select and swtich between chats.
class ChatSelectPanel(QWidget):
    def __init__(self):
        super().__init__()
        
        self.currentChat = None
        layout = QVBoxLayout()

        #Top panel (where the "new chat" button is)
        upperPanel = QHBoxLayout()
        newChatButton = QPushButton("New Chat")
        newChatButton.clicked.connect(self.createChat)
        upperPanel.addWidget(newChatButton)
        layout.addLayout(upperPanel)

        #Create ChatIcons for all of the existing chats
        os.chdir(os.path.dirname(__file__)[:-4] + "/chats")
        chats = os.listdir()
        lowerPanel = QVBoxLayout()

        for chat in chats:
            lowerPanel.addWidget(ChatIcon(chat))
        os.chdir(os.path.dirname(__file__)[:-4])

        lowerPanel.addStretch()
        lowerPanel.setSpacing(0)
        lowerPanel.setContentsMargins(0, 0, 0, 0)

        w = QWidget()
        w.setLayout(lowerPanel)
        self.scrollArea = QScrollArea()
        self.scrollArea.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scrollArea.setWidgetResizable(True)
        self.scrollArea.setWidget(w)
        layout.addWidget(self.scrollArea)

        self.setLayout(layout)
    
    def createChat(self):
        os.chdir(os.path.dirname(__file__)[:-4] + "/chats")
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
            layout.insertWidget(layout.count() - 1, ChatIcon(name))
            self.parent().currentChat = name

            os.chdir(os.path.dirname(__file__)[:-4])

            try:
                conn = sqlite3.connect("SettingsDB.db")
                cursor = conn.cursor()
                
                cursor.execute("INSERT into ChatSettings \
                               (name, language, response_length) VALUES (?, ?, ?)", (name, "English", "medium"))
                conn.commit()
                conn.close()
            except sqlite3.Error as e:
                print(e)
        os.chdir(os.path.dirname(__file__)[:-4])


#This class represents an icon for an individual chat that the user can
#select on the left hand side.
class ChatIcon(QWidget):
    def __init__(self, name):
        super().__init__()
        layout = QHBoxLayout()

        self.link = ClickableText(name)
        self.link.clicked.connect(self.selected)
        
        self.actionsButton = QPushButton("...")
        self.actionsButton.clicked.connect(self.showMenu)

        self.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self.setFixedHeight(50)
        colorRandom(self.link)

        
        layout.addWidget(self.link, stretch = 4)
        layout.addWidget(self.actionsButton)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        self.setLayout(layout)

    def selected(self):
        mainScreen = self.parent()

        while mainScreen.__class__.__name__ != "MainScreen":
            mainScreen = mainScreen.parent()
        mainScreen.setChat(self.link.text())

    #Shows the options menu when the button is clicked
    def showMenu(self):
        menu = QMenu()

        renameAction = QAction("Rename")
        renameAction.triggered.connect(self.renameChat)
        menu.addAction(renameAction)

        deleteAction = QAction("Delete chat")
        deleteAction.triggered.connect(self.deleteChat)
        menu.addAction(deleteAction)

        settingsAction = QAction("Chat settings")
        settingsAction.triggered.connect(self.displaySettings)
        menu.addAction(settingsAction)

        menu.exec(QCursor.pos())

    def displaySettings(self):
        self.parent().parent().parent().parent().parent().parent().parent().displaySettings(self.link.text())

    def renameChat(self):
        os.chdir(os.path.dirname(__file__)[:-4] + "/chats")
        newName, ok = QInputDialog.getText(self, "New Chat",
                                    "Enter the new name of the chat:", QLineEdit.Normal)
        chats = os.listdir()

        while ok and (newName.strip() == "" or newName in chats):
            newName, ok = QInputDialog.getText(self, "New Chat",
                                    "Invalid name\n\nEnter the new name of " \
                                    "the chat:", QLineEdit.Normal)
        
        if ok:
            oldName = self.link.text()
            os.rename(os.getcwd() + "/" + oldName, os.getcwd() + "/" + newName)
            self.link.setText(newName)

            os.chdir(os.path.dirname(__file__)[:-4])

            try:
                conn = sqlite3.connect("SettingsDB.db")
                cursor = conn.cursor()
                
                cursor.execute("UPDATE ChatSettings SET name = ? where name = ?", (newName, oldName))
                conn.commit()
                conn.close()
            except sqlite3.Error as e:
                print(e)

    def deleteChat(self):
        chatName = self.link.text()
        os.chdir(os.path.dirname(__file__)[:-4] + "/chats")
        shutil.rmtree(os.getcwd() + "/" + chatName)
        self.parent().layout().removeWidget(self)
        self.deleteLater()

        os.chdir(os.path.dirname(__file__)[:-4])

        try:
            conn = sqlite3.connect("SettingsDB.db")
            cursor = conn.cursor()
            
            cursor.execute("DELETE from ChatSettings where name = ?", (chatName,))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(e)



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
#This code implements the settings screen.

import os
from PySide6.QtWidgets import(
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QRadioButton,
    QVBoxLayout,
    QWidget,
)
import sqlite3

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.chatName = ""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Language"))

        #Retrieve the supported languages from the database and place them in the combo box
        os.chdir(os.path.dirname(__file__)[:-4])
        supportedLanguages = list()

        try:
            conn = sqlite3.connect("SettingsDB.db")
            cursor = conn.cursor()
            query = cursor.execute("SELECT language from Languages")
            
            currLang = ""
            currLang = query.fetchone()
            
            while currLang != None:
                supportedLanguages.append(currLang[0])
                currLang = query.fetchone()

            conn.close()
        except sqlite3.Error as e:
            print(e)

        self.languageBox = QComboBox()
        self.languageBox.addItems(supportedLanguages)
        layout.addWidget(self.languageBox)

        #Options for setting the length of the AI's responses
        layout.addWidget(QLabel("Reponse Length"))
        self.responseLengthButtonGroup = QButtonGroup()
        responseLengthLayout = QVBoxLayout()
        
        shortResponseButton = QRadioButton("Short")
        responseLengthLayout.addWidget(shortResponseButton)
        self.responseLengthButtonGroup.addButton(shortResponseButton, 1)
        
        mediumResponseButton = QRadioButton("Medium")
        responseLengthLayout.addWidget(mediumResponseButton)
        self.responseLengthButtonGroup.addButton(mediumResponseButton, 2)

        longResponseButton = QRadioButton("Long")
        responseLengthLayout.addWidget(longResponseButton)
        self.responseLengthButtonGroup.addButton(longResponseButton, 3)

        layout.addLayout(responseLengthLayout)

        #Save and cancel buttons at the bottom
        saveCancelLayout = QHBoxLayout()

        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.saveSettings)
        saveCancelLayout.addWidget(saveButton)

        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.cancel)
        saveCancelLayout.addWidget(cancelButton)
        layout.addLayout(saveCancelLayout)

        layout.addStretch()
        layout.setSpacing(10)
        self.setLayout(layout)

    #Updates the chat's settings to those chosen on the settings screen
    def saveSettings(self):
        newLanguage = self.languageBox.currentText()
        newResponseLength = "short"

        checkedResponseButton = self.responseLengthButtonGroup.checkedButton()

        if checkedResponseButton != None:
            newResponseLength = checkedResponseButton.text()

        #The ChatPanel stores the settings for the current chat.
        #Get the ChatPanel and update the settings for the chat as it is happening.
        app = self.parent()

        while app.__class__.__name__ != "App":
            app = app.parent()
        chat = app.mainScreen.chatPanel
        chat.language = newLanguage
        chat.responseLength = newResponseLength

        #Update the chat's settings in the database    
        try:
            conn = sqlite3.connect("SettingsDB.db")
            cursor = conn.cursor()
            cursor.execute("UPDATE ChatSettings SET language = ?, response_length = ? WHERE name = ?", 
                                   (newLanguage, newResponseLength, self.chatName))
            conn.commit()
            conn.close()
        except sqlite3.Error as e:
            print(e)
        app.displayMainScreen()

    def cancel(self):
        app = self.parent()

        while app.__class__.__name__ != "App":
            app = app.parent()
        app.displayMainScreen()
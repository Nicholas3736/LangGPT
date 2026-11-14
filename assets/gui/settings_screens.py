#This file implements every screen where settings can be configured in the app.
#Written by Nicholas Baker

import os
from PySide6.QtWidgets import(
    QButtonGroup,
    QComboBox,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QRadioButton,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)
import sys
sys.path.append(os.path.dirname(__file__)[:-4])
import assets.utilities as util

class SettingsScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.chatName = ""
        layout = QVBoxLayout()
        layout.addWidget(QLabel("Language"))

        #Retrieve the supported languages from the database and place them in the combo box
        langsAndPrompts = util.executeQueries([["SELECT language from Languages", ()], 
                                               ["SELECT name FROM Prompts", ()]])

        supportedLanguages = langsAndPrompts[0] 
        prompts = langsAndPrompts[1]

        self.languageBox = QComboBox()
        self.languageBox.addItems(l[0] for l in supportedLanguages)
        layout.addWidget(self.languageBox)

        #Setting for the prompt that will be used in the chat.
        layout.addWidget(QLabel("Chat Prompt"))
        self.promptBox = QComboBox()
        self.promptBox.addItems(p[0] for p in prompts)

        newPromptButton = QPushButton("New Prompt")
        newPromptButton.clicked.connect(self.showPromptCreationWindow)

        promptLayout = QHBoxLayout()
        promptLayout.addWidget(self.promptBox)
        promptLayout.addWidget(newPromptButton)
        layout.addLayout(promptLayout)

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

        self.saveButton = QPushButton("Save")
        self.saveButton.clicked.connect(self.saveSettings)
        saveCancelLayout.addWidget(self.saveButton)

        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.cancel)
        saveCancelLayout.addWidget(cancelButton)
        layout.addLayout(saveCancelLayout)

        layout.addStretch()
        layout.setSpacing(10)
        self.setLayout(layout)

    #Triggered when the user clicks the "New Prompt" button
    def showPromptCreationWindow(self):
        self.promptCreationWindow = CreatePromptWindow()
        self.promptCreationWindow.show()
        
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
        util.executeQueries([["UPDATE ChatSettings SET language = ?, response_length = ? WHERE name = ?", 
                              (newLanguage, newResponseLength, self.chatName)]])
        app.displayMainScreen()

    def cancel(self):
        app = self.parent()

        while app.__class__.__name__ != "App":
            app = app.parent()
        app.displayMainScreen()

#The screen that comes up when configuring the settings for a new chat.
#It is nearly identical to SettingsScreen.
class NewChatScreen(SettingsScreen):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("New Chat")
        self.layout().insertWidget(0, QLabel("Chat Name"))
        self.chatNameInput = QLineEdit()
        self.layout().insertWidget(1, self.chatNameInput)

        self.saveButton.setText("Create Chat")
        self.saveButton.clicked.connect(self.createChat)

    #Executes when the "Create Chat" button is clicked.
    def createChat(self):

        #prompt for chat name and get the names of all other chats
        name = self.chatNameInput.text()
        chats = util.executeQueries([["SELECT name FROM ChatSettings", ()]])[0]
        for i in range(0, len(chats)):
            chats[i] = chats[i][0]

        #Verify that the name is not already taken
        dlg = QMessageBox()
        
        if name.strip() == "":
            dlg.setText("Please enter a name.")
        elif name in chats:
            dlg.setText("This name is already taken. Please enter a different one.")
        else:
            dlg.setText("Chat created succesfully.")
            util.executeQueries([["INSERT into ChatSettings \
                                  (name, language, response_length) VALUES (?, ?, ?)", 
                                  (name, self.languageBox.currentText(), 
                                   self.responseLengthButtonGroup.checkedButton().text())]])
            
            app = util.getAncestor(self, "App")
            app.mainScreen.chatSelectPanel.createChatIcon(name)
            app.mainScreen.setChat(name)
            app.displayMainScreen()
            
        dlg.exec()


#Window that contains the GUI to create a new chat prompt. 
#Used by SettingsScreen and CreateChatScreen
class CreatePromptWindow(QWidget):
    def __init__(self):
        super().__init__()
        winLayout = QVBoxLayout()
        winLayout.addWidget(QLabel("Prompt name: "))
        self.nameBox = QLineEdit()
        winLayout.addWidget(self.nameBox)
        winLayout.addWidget(QLabel("Type your prompt in the box below."))
        self.promptBox = QTextEdit()
        winLayout.addWidget(self.promptBox)
        
        buttonLayout = QHBoxLayout()
        saveButton = QPushButton("Save")
        saveButton.clicked.connect(self.createPrompt)
        cancelButton = QPushButton("Cancel")
        cancelButton.clicked.connect(self.cancel)
        buttonLayout.addWidget(saveButton)
        buttonLayout.addWidget(cancelButton)
        
        winLayout.addLayout(buttonLayout)
        self.setLayout(winLayout)

    def createPrompt(self):
        os.chdir(os.path.dirname(__file__)[:-4])

        util.executeQueries([["INSERT INTO Prompts (name, prompt) VALUES (?, ?)", 
                              (self.nameBox.text(), self.promptBox.toPlainText())]])
        self.close()

    def cancel(self):
        self.close()
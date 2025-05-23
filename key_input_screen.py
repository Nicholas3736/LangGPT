#This code implements the dialog where you input your 
#Groq API key when first starting the program

#Written by Nicholas baker

from PySide6.QtWidgets import ( 
    QVBoxLayout, 
    QDialog, 
    QDialogButtonBox, 
    QLabel, 
    QLineEdit
)

class KeyInputScreen(QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Enter Groq API key")
        
        prompt = QLabel("Enter your Groq API key to begin")
        self.inputBox = QLineEdit()
        self.key = ""
        
        button = QDialogButtonBox.Ok
        self.buttonBox = QDialogButtonBox(button)
        self.buttonBox.accepted.connect(self.setInput)

        layout = QVBoxLayout()
        layout.addWidget(prompt)
        layout.addWidget(self.inputBox)
        layout.addWidget(self.buttonBox)
        self.setLayout(layout)

    #Stores the key that is inputted so the main screen can retrive it.
    def setInput(self):
        self.key = self.inputBox.text()
        print("Set the API key to " + self.key)
        self.close()

    #For use by the main screen to retrieve the API key inputted. 
    def getInput(self):
        return self.key
         
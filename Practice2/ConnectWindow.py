import sys
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLineEdit, QPushButton, QLabel, QMainWindow

from db import Database
from MainWindow import MyWindow

class ConnectWindow(QMainWindow):
    def __init__(self, db: Database):
        super().__init__()
        self.db = db
        self.initUI()

    def initUI(self):
        self.setWindowTitle('SQL Connection')
        self.setFixedSize(380, 420)

        self.setStyleSheet("""
                    QLineEdit { 
                        padding: 8px; 
                        border: 1px solid #ccc; 
                        border-radius: 4px; 
                    }
                    QPushButton { 
                        padding: 10px; 
                        background-color: #2b8a3e; 
                        color: white; 
                        border: none; 
                        border-radius: 4px; 
                        font-weight: bold; 
                    }
                    QPushButton:hover { 
                        background-color: #237032; 
                    }
                """)

        central_widget = QWidget(self)
        self.setCentralWidget(central_widget)

        layout = QVBoxLayout(central_widget)
        layout.setContentsMargins(30, 20, 30, 20)
        layout.setSpacing(10)

        self.DB_HOST = QLineEdit(self)
        self.DB_HOST.setPlaceholderText("Input HOST")
        self.DB_HOST.setText('127.0.0.1')

        self.DB_PORT = QLineEdit(self)
        self.DB_PORT.setPlaceholderText("Input PORT")
        self.DB_PORT.setText('5432')

        self.DB_NAME = QLineEdit(self)
        self.DB_NAME.setPlaceholderText("Input NAME")
        self.DB_NAME.setText('postgres')

        self.DB_USER = QLineEdit(self)
        self.DB_USER.setPlaceholderText("Input USER")
        self.DB_USER.setText('postgres')

        self.DB_PASS = QLineEdit(self)
        self.DB_PASS.setPlaceholderText("Input PASS")
        self.DB_PASS.setEchoMode(QLineEdit.Password)
        self.DB_PASS.setText('mysecretpassword')

        self.DB_DRIVER = QLineEdit(self)
        self.DB_DRIVER.setPlaceholderText("Input DRIVER")
        self.DB_DRIVER.setText('/opt/homebrew/lib/psqlodbcw.so')

        layout.addWidget(self.DB_HOST)
        layout.addWidget(self.DB_PORT)
        layout.addWidget(self.DB_NAME)
        layout.addWidget(self.DB_USER)
        layout.addWidget(self.DB_PASS)
        layout.addWidget(self.DB_DRIVER)

        self.btn = QPushButton('Connect', self)
        self.btn.clicked.connect(self.on_click)

        layout.addWidget(self.btn)

        self.connetcion = QLabel('', self)
        layout.addWidget(self.connetcion)

    def on_click(self):
        DB_HOST = self.DB_HOST.text()
        DB_PORT = self.DB_PORT.text()
        DB_NAME = self.DB_NAME.text()
        DB_USER = self.DB_USER.text()
        DB_PASS = self.DB_PASS.text()
        DB_DRIVER = self.DB_DRIVER.text()

        c = self.db.connect(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASS, DB_DRIVER)
        if c:
            self.connetcion.setStyleSheet("color: green; font-weight: bold;")
            self.connetcion.setText('Connected!')

            self.main_window = MyWindow(self.db)
            self.main_window.show()
            self.close()
        else:
            self.connetcion.setStyleSheet("color: red; font-weight: bold;")
            self.connetcion.setText('Failed to connect!')





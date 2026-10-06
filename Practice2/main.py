from db import Database
from ConnectWindow import ConnectWindow

import sys
from PyQt5.QtWidgets import QApplication

if __name__ == "__main__":
    db = Database()
    app = QApplication(sys.argv)
    window = ConnectWindow(db)
    window.show()
    sys.exit(app.exec_())

from PyQt5.QtWidgets import QApplication
from UI.mainPage import MainPage

import sys

if __name__ == '__main__':
    app = QApplication(sys.argv)
    initialPage = MainPage()
    initialPage.show()
    sys.exit(app.exec_()) 
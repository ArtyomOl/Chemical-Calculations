import PyQt5.QtWidgets
import sys

from screens.mainWindow import MainWindow

if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication(sys.argv)

    window = MainWindow()
    window.show()

    app.exec()
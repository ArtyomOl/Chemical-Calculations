import PyQt5.QtWidgets
import sys

import Front

if __name__ == '__main__':
    app = PyQt5.QtWidgets.QApplication(sys.argv)

    window = Front.MainWindow()
    window.show()

    app.exec()
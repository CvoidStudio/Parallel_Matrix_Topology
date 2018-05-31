import sys

from PyQt5.QtWidgets import (
	QApplication, QMainWindow
)

from Prog_Logic import my_EvLoop
from CNUI import Ui_MainWnd

class CN_MainWnd(QMainWindow):
	def __init__(self, *args):
		super(CN_MainWnd,self).__init__()
		self.setMouseTracking(True)
		self.mousepos = [0,0]

	def mousePressEvent(self, event):
		self.mousepos[0] = event.x()
		self.mousepos[1] = event.y()

	def mouseMoveEvent(self, event):
		self.mousepos[0] = event.x()
		self.mousepos[1] = event.y()


if __name__ == '__main__':
	app = QApplication(sys.argv)
	MainWindow = CN_MainWnd()
	MainWindow.setFixedSize(1080,800)

	ui = Ui_MainWnd()
	ui.setupUi(MainWindow)

	# Add activities
	EVENT_Loop = my_EvLoop(MainWindow,ui)
	EVENT_Loop.exec()
	#EVENT_Loop.exec()

	MainWindow.show()
	sys.exit(app.exec_())

from PyQt5.QtCore import QDateTime,QTimer,QCoreApplication
from PyQt5.QtGui import QIcon
_translate = QCoreApplication.translate
import PagesDev as PD
from PyQt5.QtGui import QMouseEvent

class my_EvLoop():
	def __init__(self, Main_Wnd, Main_UI, countgap = 1000):
		self.UI = Main_UI
		self.timer = QTimer()
		self.timer.start(countgap)
		self.dtime = QDateTime.currentDateTime()
		self.string_info = []
		# Message Center Base
		self.Msg_Center = PD.Msg_Center(Main_Wnd)

		# Custom Pages
		self.page_Login = PD.Page_LOGIN(Main_UI)
		self.page_terminal = PD.Page_Terminal(Main_UI,
		                                      self.page_Login.SSHclient,
		                                      self.Msg_Center)
		# Quick command
		self.Qcomm = PD.Quick_Comm(Main_UI,self.page_terminal)
		self.Qcomm.ReadfromFile('./commlib/comm_list.comm')

		# Database
		self.page_Table = PD.Page_DataBase(Main_UI)
		self.page_terminal.CMD2DB.Link2DB(self.page_Table)

		# Main Menu
		self.page_Menu = PD.My_Menu(Main_UI.Menu_Btn, Main_UI.Main_Menu)

		# initialize some widgets
		self.UI.LOGIN.setGeometry(0,0,1080,762)


	def exec(self):
		self.timer.timeout.connect(self.Main_Loop)

	def get_DateTime(self):
		return self.dtime.toString()

	def Main_Loop(self):
		# Get Date & Time
		self.dtime = QDateTime.currentDateTime()
		self.UI.Clock_Text.setText(_translate("MainWindow", self.get_DateTime()))
		#if self.UI.progressBar.value() > 0:
		#	self.UI.progressBar.setVisible(True)
		#else:
		#	self.UI.progressBar.hide()




	def Get_Input(self):
		self.UI.TEXT_Terminal.setHtml(_translate("MainWindow",
		                                      self.string_info[0]))
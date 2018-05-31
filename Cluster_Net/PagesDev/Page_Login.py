from PagesDev.SSH_Connect import *
from PyQt5.QtCore import QCoreApplication
from copy import copy

from PyQt5.QtWidgets import QAction

_translate = QCoreApplication.translate

class Login_item:
	def __init__(self, user_id, host_id, password):
		self.user_id = user_id
		self.host_id = host_id
		self.pwd = None if password == '*None*' else password

class Page_LOGIN():
	def __init__(self, Main_UI):
		self.UI = Main_UI

		self.UI.Btn_login.clicked.connect(self.fetch_login_info)

		# setup ssh client
		self.SSHclient = SSH_Agent(timeout=5)

		self.ListFile = open('ipConfigList.list','r+')
		lines = self.ListFile.readlines()
		# skip header
		self.IP_List = []
		if (len(lines) > 1):
			for line in lines[1:]:
				_h,_u,_p = line[:-1].split(' ')
				self.IP_List.append(Login_item(_u,_h,_p)) # const info

			# add to list
			for info in self.IP_List:
				self.Add_preconfigList(info.user_id,info.host_id,info.pwd)


		# quick paste
		self.UI.List_IP.itemDoubleClicked.connect(self.Paste2Panel)

	def Paste2Panel(self):
		info = self.UI.List_IP.selectedItems()[0].text()
		RawI = info.split(' ')
		_u,_h = RawI[0].split('@')
		_p = RawI[-1]

		self.UI.TextEdit_UserID.setText(_u)
		self.UI.TextEdit_HostID.setText(_h)
		if _p != '<hiden>':
			self.UI.TextEdit_PWD.setText(_p)

	def __del__(self):
		self.ListFile.close()

	def fetch_login_info(self):
		info = Login_item(
			copy(self.UI.TextEdit_UserID.text()),
			copy(self.UI.TextEdit_HostID.text()),
			copy(self.UI.TextEdit_PWD.text())
		)
		self.IP_List.append(info)

		warning = ''
		if len(info.user_id) == 0:
			warning += "user ID "

		if len(info.host_id) == 0:
			warning += "host ID "

		# show message
		if len(warning) > 0:
			self.UI.Text_loginwarn.setText(_translate("Text_loginwarn",
			                                          "<html><head/><body><p><span style=\" color:#ff0000;\">"+\
			                                          warning +\
			                                          "</span></p></body></html>"))
		else:
			self.UI.Text_loginwarn.setText(_translate("Text_loginwarn",
			                                          "<html><head/><body><p><span style=\" color:#ffffff;\">"
			                                          "login..."
			                                          "</span></p></body></html>"))
			warning = self.SSHclient.connect(user_id=info.user_id,
			                                 host_id=info.host_id,
			                                 pwd=info.pwd)
			# Add & save info
			if warning == "Login Successful!":
				if self.UI.Check_AddIP.isChecked():
					if self.UI.Check_Savepwd.isChecked():
						self.Add_preconfigList(info.user_id,info.host_id,info.pwd)
						self.ListFile.write('%s %s %s\n'%(
							info.host_id,info.user_id,info.pwd
						))
					else:
						self.Add_preconfigList(info.user_id, info.host_id)
						self.ListFile.write('%s %s *None*\n' % (
							info.host_id, info.user_id
						))
				# enable CMD input
				self.UI.CMD.addItem('SSH CONNECTED TO %s' % self.IP_List[-1].host_id)
				self.UI.CMD.addItem('-----------------------------------------------------')
				self.UI.CMD_Line.setEnabled(True)
				self.UI.CMD_Line.setText('')

				self.UI.LOGIN.hide()


			# print login result
			self.UI.Text_loginwarn.setText(_translate("Text_loginwarn",
			                                          "<html><head/><body><p><span style=\" color:#ffffff;\">"+\
			                                          warning +\
			                                          "</span></p></body></html>"))

	def Add_preconfigList(self, user_id, host_id, pwd = None):
		# add info
		self.UI.List_IP.addItem('%s@%s | password: %s'%(user_id,host_id,
		                                 '<hiden>' if pwd==None else pwd))
		# add apply/del

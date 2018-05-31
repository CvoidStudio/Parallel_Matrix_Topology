from copy import copy
_seperate = '-----------------------------------------------------'

from PyQt5.QtCore import QCoreApplication
from PagesDev.CN_Command import *

class CMD2DB_Panel():
	def __init__(self, UI, Msg_Center):
		self.panel = UI.CMD2DB
		self.panel.setVisible(False)

		self.my_List = UI.CMD2DB_List
		self.my_List.itemDoubleClicked.connect(self.paste2Line)

		self.DB_list = UI.DB_list

		self.inLine = UI.CMD2DB_line

		self.Btn_DRAG = UI.CMD2DB_DRAG
		self.Btn_DRAG.clicked.connect(self.move)
		self.isDrag = False

		self.Btn_OK = UI.CMD2DB_OK
		self.Btn_OK.clicked.connect(self.confirm_AddDB)

		self.Btn_NO = UI.CMD2DB_NO
		self.Btn_NO.clicked.connect(self.hide)

		self.Btn_VIEW = UI.CMD2DB_VIEW
		self.isListOn = False
		self.Btn_VIEW.clicked.connect(self.switch_list)

		self.MSG = Msg_Center

		# exterior interfaces
		self.fromCMD = UI.CMD
		self.warning = UI.CMD2DB_info
		self.is2ind = UI.CMD2DB_is2Ind
		self.dlm = UI.CMD2DB_dlm
		self._toDB = None

	def Link2DB(self, DataBase):
		self._toDB = DataBase

	def switch_list(self):
		if self.isListOn:
			self.panel.setGeometry(582, 510, 312, 160)
			self.isListOn = False
		else:
			self.panel.setGeometry(582, 304, 312, 366)
			self.isListOn = True

	def show(self):
		if not self.panel.isVisible():
			self.refresh()
			self.panel.setGeometry(582, 304, 312, 366)
			self.panel.setVisible(True)
	def hide(self):
		if self.panel.isVisible():
			#self.my_List.clear()
			self.panel.setVisible(False)

	def move(self):
		if self.isListOn:
			self.panel.setGeometry(582,630,312,41)
			self.isListOn = False
		else:
			self.panel.setGeometry(582, 304, 312, 366)
			self.isListOn = True

	def refresh(self):
		self.my_List.clear()
		for i in range(self.DB_list.count()):
			self.my_List.addItem(self.DB_list.item(i).text())

	def paste2Line(self):
		info = self.my_List.selectedItems()[0].text()
		self.inLine.setText(info)

	# ADD Table
	def confirm_AddDB(self):
		name = self.inLine.text()
		if len(name) == 0:
			self.warning.setText('Please enter the name of the table')
			return

		# check if there is any <out> item selected
		if self.MSG.get_Buffer_CMD() != None:
			CATCHyou = self.MSG.buffer_CMD.split('\n')
			if CATCHyou[0] == '<out>':
				# get delimiter
				dlm = self.dlm.text()
				if len(dlm) == 0:
					dlm = ' '
				else:
					dlm = dlm[0]

				# deal with the rows
				if self.is2ind.isChecked(): # 1st col as ind
					self.warning.setText(self._add2DB(name, CATCHyou[1:], True, dlm))
				else:
					self.warning.setText(self._add2DB(name, CATCHyou[1:], False,dlm))
			else:
				self.warning.setText('Please selected one <out> block!')
				return
		else:
			self.warning.setText('Please selected one nonempty <out> block!')
		return

	def _add2DB(self, name, rows, if_indices, delimiter):
		# check if the name has existed
		if name in self._toDB.database:
			return 'Warning: Overwriting Detected!'

		# get dimensions
		num_R = len(rows)
		num_C = 1
		# set CN table
		index = []
		data = []

		for line in rows:
			row = line.split(delimiter)
			if len(row) > num_C:
				num_C = len(row)

			data.append([])
			if if_indices:
				index.append(row[0])
			else:
				data[-1].append(row[0])

			if len(row) > 1:
				for I in row[1:]:
					data[-1].append(row[0])

		# Add to DataBase


		return "Table <%s> Added!"%name


_translate = QCoreApplication.translate
class Page_Terminal():
	def __init__(self, MainUI, SSH_Client, Msg_Center):
		self.CMD = MainUI.CMD
		self.CMD_line = MainUI.CMD_Line
		self.clearBtn = MainUI.CMD_Clear
		self.stopbtn = MainUI.CMD_Stop
		self.addbtn = MainUI.CMD_Add

		self.CMD_line.setText('<SSH Client Connected Required>')
		self.CMD_line.setEnabled(False)
		self.CMD.addItem(
		"Hello! This is CLUSTER NET (ALPHA) V0.01 -- 05-23-2018")
		self.CMD.addItem(_seperate)
		self.CMD_line.returnPressed.connect(self.enter_cmd)
		self.MSG = Msg_Center
		# SSH clients info
		self.SSH = SSH_Client

		# CMD to DataBase Panel
		self.CMD2DB = CMD2DB_Panel(MainUI, Msg_Center)

		# Cluster Net Command System
		self.CNCOMM = CN_command()

		# clear button
		self.clearBtn.clicked.connect(self.clearScreen)

		# Terminate button
		self.stopbtn.clicked.connect(self.STOPcomm)

		# Call CMD2DB Panel
		# Terminate button
		self.addbtn.clicked.connect(self.callCDM2DB)

		# quick paste
		self.CMD.itemDoubleClicked.connect(self.Paste2Line)

	def enter_cmd(self):
		T =  self.CMD_line.text()
		self.exec_comm(T)

	def exec_comm(self, T):
		if len(T) > 0:
			self.CMD_line.setText('')
			if T[:4] == '@CN ':
				self.filter_special(T[4:])
				return

			# check ssh client address
			# self.check_SSH(T)

			self.CMD.addItem('<command> ' + T)

			O = self.SSH.exec(T)
			if len(O) > 0:
				self.CMD.addItem('<out>\n' + O)

			self.CMD.addItem(_seperate)
			self.CMD.scrollToBottom()
			return

	def check_SSH(self, T):
		pass
		"""if T[:4] == 'exit':
			self.MSG.pop_ssh()
		elif 'ssh ' in T:"""


	def Paste2Line(self):
		info = self.CMD.selectedItems()[0].text()
		if info[:10] == '<command> ':
			self.CMD_line.setText(info[10:])
		elif info[:5] == '<out>':
			self.MSG.buffer_CMD = copy(info)

	def clearScreen(self):
		self.CMD.clear()

	def STOPcomm(self):
		self.CMD.addItem('<terminated>')
		O = self.SSH.exec('\x03')
		if len(O) > 0:
			self.CMD.addItem('<out>\n' + O)

		self.CMD.addItem(_seperate)
		self.CMD.scrollToBottom()  # ctrl+c

	def callCDM2DB(self):
		self.CMD2DB.refresh()
		self.CMD2DB.show()

	def filter_special(self,T):
		print('Build-in Command')

class Quick_Comm():
	def __init__(self, MainUI, toCMD):
		self.COMM = MainUI.Q_comm
		self.commlist = {}
		self.CMD = toCMD
		self.outfile = None
		# double click to execute
		self.COMM.itemDoubleClicked.connect(self.exec)

	def __del__(self):
		if self.outfile:
			self.outfile.close()
			self.outfile = None

	def exec(self):
		name = self.COMM.selectedItems()[0].text()
		for line in self.commlist[name]:
			self.CMD.exec_comm(line)

	def ReadfromFile(self, filepath):
		self.outfile = open(filepath, 'r+')
		Lines = self.outfile.readlines()
		start_block = None
		for line in Lines:
			if line[:5] == '#comm':
				comm_name = line[6:-1]
				self.COMM.addItem(comm_name)
				self.commlist[comm_name] = []
				start_block = comm_name

			elif line[:4] == '#end':
				start_block = None
			else:
				if start_block != None and len(line) > 1:
					self.commlist[start_block].append(line[:-1])

		self.outfile.close()
		self.outfile = None
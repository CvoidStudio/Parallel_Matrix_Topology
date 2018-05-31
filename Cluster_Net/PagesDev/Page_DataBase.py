from PagesDev.CN_Table import *

class Page_DataBase():
	def __init__(self, MainUI):
		self.DB_list = MainUI.DB_list
		self.DB_list.itemDoubleClicked.connect(self.print_Table)

		# Command Buttons
		self.Btn_save = MainUI.DB_save
		self.Btn_load = MainUI.DB_load
		self.Btn_paint = MainUI.DB_paint

		# save Tables (name : CN_Table)
		self.database = {}

		# table GUI
		self.table = MainUI.DB_table

	def add_Table(self, name, nRow, nCol, data, header = None):
		self.database[name] = CN_Table(nRow,nCol,header,Data=data)

	def print_Table(self):
		name = self.DB_list.selectedItems()[0].text()
		if name in self.database:
			tarT = self.database[name]
			self.table.clear()
			self.table.setRowCount(tarT.num_Rows)
			self.table.setColumnCount(tarT.num_Cols)
		else:
			print('Table %s does not exist!')

	def open_CSV(self, filepath):
		pass
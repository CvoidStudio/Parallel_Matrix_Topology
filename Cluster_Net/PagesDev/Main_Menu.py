class My_Menu:
	def __init__(self, MenuBtn, MenuWidget):
		self.MenuBtn = MenuBtn
		self.MENU = MenuWidget

		self.MENU.setVisible(False)
		self.MenuBtn.clicked.connect(self.switch_MENU)
		self.MENU.setGeometry(0,452,340,312)

	def switch_MENU(self):
		self.MENU.setVisible(False if self.MENU.isVisible() else True)
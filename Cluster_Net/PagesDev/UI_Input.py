from PyQt5.QtWidgets import QAction

class new_Event(QAction):
	def __init__(self, Action_ID, bind_to, act_key):
		super(new_Event,self).__init__()

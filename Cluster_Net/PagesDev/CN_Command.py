def CN_command():
	def __init__(self, Msg_Center):
		self.MSG = Msg_Center
		self.CList = {
			'reset': self.Reset(),
			'start': {
				'-time' : Set_Property(),
			}
		}

	def Reset(self):
		self.MSG.CN_Reset()

	def Set_Property(self):
		pass
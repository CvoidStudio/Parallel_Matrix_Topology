from numpy import zeros
from pandas import DataFrame
class CN_Table():
	def __init__(self, num_Rows = 1, num_Cols = 1,
	             headers = None, indices = None, Data = None):
		self.num_Rows = num_Rows
		self.num_Cols = num_Cols

		if not headers:
			headers = [i for i in range(num_Cols)]

		self._data = zeros([num_Rows,num_Cols],dtype='str').tolist()
		self.table = DataFrame(data=self._data,columns=headers,index=indices)

		if not Data:
			self.import_data(Data)

	def import_data(self, Data):
		for r in range(len(Data)):
			for c in range(len(Data[r])):
				self._data[r][c] = Data[r][c]

	def export_CSV(self, path):
		self.table.to_csv(path)

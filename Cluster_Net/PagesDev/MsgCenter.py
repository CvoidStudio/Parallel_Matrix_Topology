import pandas as pd

class CN_Node():
	def __init__(self, name, channel = None):
		self.name = name
		self.channel = channel
		self.isConnected = self.check_connection()
		self.nextNode = set()

	def check_connection(self):
		if self.channel == None:
			return False
		return True

class CN_Table():
	def __init__(self, name):
		self.name = name


class Msg_Center():
	def __init__(self, MainWnd):
		self.SSH_Connecting = {}    # host_id : CN_Node
		self.nowAtSSH = None
		self.mousepos = MainWnd.mousepos

		self.OBJ_Node = {}
		self.OBJ_Table = {}

		# BUFFERS
		self.buffer_CMD = None


	def add_node(self, node_name, channel = None):
		if node_name in self.OBJ_Node:
			return 'node (%s) has already existed!'%node_name
		self.OBJ_Node[node_name] = CN_Node(node_name,channel)
		return ''

	def add_table(self, table_name, string = None):
		if table_name in self.OBJ_Table:
			return 'node (%s) has already existed!'%table_name
		self.OBJ_Table[table_name] = CN_Node(table_name)
		return ''

	def push_ssh(self, adr):
		self.SSH_Connecting[adr] = None
	def pop_ssh(self):
		self.SSH_Connecting.pop(self.nowAtSSH)

	def get_mousepos(self):
		return self.mousepos

	def clear_buffer(self):
		self.buffer_CMD = None

	def get_Buffer_CMD(self):
		return self.buffer_CMD
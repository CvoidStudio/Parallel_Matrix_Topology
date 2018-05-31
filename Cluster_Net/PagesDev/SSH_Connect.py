import paramiko
from time import sleep
import re

class SSH_Agent():
	def __init__(self, timeout = 10):
		self.agent = None
		self.timeout = timeout

	def __del__(self):
		#for a in self.agent.values():
		#	a.close()
		if self.agent != None:
			self.agent.close()
		self.agent = None
		self.transport = None
		self.chan = None

	def connect(self, user_id, host_id, pwd):
		#if agent_name == None:
		#	agent_name = "SSH_%i"%(len(self.agent))

		# create ssh agent
		self.agent = paramiko.SSHClient()
		try:
			# allow to connect the hosts not in the certicated list
			self.agent.set_missing_host_key_policy(paramiko.AutoAddPolicy())

			# connect to host
			self.transport = paramiko.Transport((host_id, 22))
			self.transport.start_client()
			self.transport.auth_password(username=user_id, password=pwd)

			#self.agent.connect(hostname = host_id,
			#                port = 22,
			#                username = user_id,
			#                password = pwd,
			#                timeout = self.timeout)
			self.agent._transport = self.transport
			# invoke shell
			self.chan = self.transport.open_session()
			self.chan.settimeout(self.timeout)
			self.chan.get_pty()
			self.chan.invoke_shell()
			#self.agent = ssh_now    # add to agent list
			return "Login Successful!"
		except:
			return "Error Occurs while Logining into: %s@%s"%(user_id,host_id)

	def exec(self, cmd):
		self.chan.send(cmd + '\r')
		RMSG = ''
		sleep(0.1)
		_wait = 0
		while _wait < 50000:
			_wait += 1
			if self.chan.recv_ready():
				RMSG += self.chan.recv((2<<16)).decode('utf-8')
				_wait = 0
		RMSG = re.sub(r'\x1b\[([0-9,A-Z]{1,2}(;[0-9]{1,2})?(;[0-9]{3})?)?[m|K]?',
		              '', RMSG)
		GM = RMSG.split('\n')

		return ''.join('%s\n'%l for l in GM[1:])[:-1]


	def disconect(self):
		self.chan.close()
		self.transport.close()
		self.agent.close()

	#def get_agentid_list(self):
	#	return list(self.agent.keys())
import csv
import numpy as np
from collections import namedtuple as Ntuple

class HyperCube():
	def __init__(self, P, m, l, n):
		# basic properties
		self.num_P = P
		self.dim_M = m
		self.dim_L = l
		self.dim_N = n

		# total area involved
		self.whole_area_A = np.zeros((m, l, P), dtype='int8')
		self.whole_area_B = np.zeros((l, n, P), dtype='int8')
		# initialized buffers
		self.buffer_area_A = np.zeros((m, l, P), dtype='int8')
		self.buffer_area_B = np.zeros((l, n, P), dtype='int8')

		# Rings along Columns
		self.Ring = Ntuple('Ring',['area','length','members'])
		#self.Columns_A = {}
		#self.Columns_B = {}
		#self.Columns_Core = {}
		# Raw Columns
		self.Col_dict_A = {}
		self.Col_dict_B = {}

	# Draw Hypercube
	def Draw_HCube(param):
		# Whole computation volumes
		if param == 'whole':
			pass
		elif param == 'buffer':
			pass

	# compressed series key
	@staticmethod
	def Encode_Key(col):
		Key = []
		ind = 0
		for i in col:
			if i == 2: # sender
				Key.append(ind+1)
			elif i == 1: # reciever
				Key.append(-ind-1)
			ind += 1
		return tuple(Key)


	def __import_info(self, P, info):
		x, y, z, L, W, H, \
		LA_x, LA_y, LA_L, LA_H, \
		LB_x, LB_y, LB_L, LB_H = info  # unpack

		LA_x += x
		LA_y += z
		LB_x += y
		LB_y += z

		# shading areas
		self.whole_area_A[z:z + H,x:x + L,P] += 1
		self.whole_area_B[z:z + H,y:y + W,P] += 1
		self.buffer_area_A[LA_y:LA_y + LA_H,LA_x:LA_x + LA_L,P] += 1
		self.buffer_area_B[LB_y:LB_y + LB_H,LB_x:LB_x + LB_L,P] += 1

	def Shade_from_HBC(self, file_path, separator=','):
		F = open(file_path+'.hbc', 'r')
		FC = csv.reader(F, delimiter=separator)

		for line in FC:
			# get core description
			if line[0][0] == '@':
				Now_at = (int)(line[0][1:])

				# block desc:
				# x,y,z,Length,Width,Height,
				# localA_x,localA_y, localA_L,localA_H
				# localB_x,localB_y, localB_L,localB_H
				num_ele = 0  # for double-check
				info = [0, 0, 0, 0, 0, 0,
				        0, 0, 0, 0,
				        0, 0, 0, 0]
				for ele in line[1:]:
					if ele.isdigit():  # get number
						info[num_ele] = (int)(ele)
						num_ele += 1
					# import proper info
					if num_ele == 14:
						self.__import_info(Now_at, info)
						num_ele = 0

					# Redundant info
				if num_ele != 0:  # non-formatted info
					print('Error in info with core#%i...\n' % (Now_at))
					break

		F.close()
		return

	# Optimizing Plan
	def get_Potentials(self, Col_dict, Potentials):
		# DFS
		layer = 0
		for col in Col_dict.keys():
			recievers = []      # Candidates to be added into the rings
			senders = []        # Candidates as sources
			for core in col:
				if core < 0:
					recievers.append(-core-1)
				elif core > 0:
					senders.append(core-1)

			# Add to potentials
			for s in senders:
				for r in recievers:
					Potentials[s,r,layer] += Col_dict[col] # area -> weight

			# Next Layer
			layer += 1

	def Calculate_Potentials(self):
		# Merge Identical Columns -> Get Cross-section areas
		for l in range(self.dim_L):
			# Columns on A
			for m in range(self.dim_M):
				# hash key
				Key = HyperCube.Encode_Key(
					self.buffer_area_A[m,l,:] + self.whole_area_A[m,l,:])
				# Count members
				# Accumulate Cross-Section Area
				if Key in self.Col_dict_A:
					self.Col_dict_A[Key] += 1
				else:
					self.Col_dict_A[Key] = 1

			# Columns on B
			for n in range(self.dim_N):
				# hash key
				Key = HyperCube.Encode_Key(
					self.buffer_area_B[l,n,:] + self.whole_area_B[l,n,:])
				# Accumulate Cross-Section Area
				if Key in self.Col_dict_B:
					self.Col_dict_B[Key] += 1
				else:
					self.Col_dict_B[Key] = 1

		Potential_Mat_A = np.zeros([self.num_P,self.num_P,len(self.Col_dict_A)])
		Potential_Mat_B = np.zeros([self.num_P,self.num_P,len(self.Col_dict_B)])
		# Merge distinct columns : optimized plan
		self.get_Potentials(self.Col_dict_A,Potential_Mat_A)
		self.get_Potentials(self.Col_dict_B,Potential_Mat_B)
		#self.Columns_A = self.__merge_Columns(Col_A)
		#self.Columns_B = self.__merge_Columns(Col_B)
		# Statistics: Rings resp. to each core

		return Potential_Mat_A,Potential_Mat_B


	def Get_Linprog_Map(self):
		# Return Pack
		Constrains = Ntuple('Constrains',
		                    ['map', 'length', 'area', 'volume','reciever'])

		# get targets
		K_A = len(self.Col_dict_A)
		K_B = len(self.Col_dict_B)  # height


		# get constrains
		Lin_map_A = Constrains([],
		                       np.zeros(K_A, dtype = 'int32'),
		                       np.zeros(K_A, dtype = 'int32'),
		                       np.zeros(K_A, dtype = 'int32'),
		                       [])
		i = 0
		for (Col,area) in self.Col_dict_A.items():
			Lin_map_A.area[i] = area
			Lin_map_A.length[i] = len(Col)
			Lin_map_A.volume[i] = Lin_map_A.area[i]*Lin_map_A.length[i]

			Lin_map_A.map.append([])
			Lin_map_A.reciever.append([])
			for core in Col:
				if core > 0:  # source
					Lin_map_A.map[-1].append(core-1)
				elif core < 0:
					Lin_map_A.reciever[-1].append(-core-1)

			i += 1

		Lin_map_B = Constrains([],
		                       np.zeros(K_B, dtype = 'int32'),
		                       np.zeros(K_B, dtype = 'int32'),
		                       np.zeros(K_B, dtype = 'int32'),
		                       [])
		i = 0
		for (Col,area) in self.Col_dict_B.items():
			Lin_map_B.area[i] = area
			Lin_map_B.length[i] = len(Col)
			Lin_map_B.volume[i] = Lin_map_B.area[i] * Lin_map_B.length[i]

			Lin_map_B.map.append([])
			Lin_map_B.reciever.append([])
			for core in Col:
				if core > 0:  # source
					Lin_map_B.map[-1].append(core - 1)
				elif core < 0:
					Lin_map_B.reciever[-1].append(-core - 1)

			i += 1

		return Lin_map_A, Lin_map_B

	def Check_Area(self):
		# Overlap
		if np.max(self.whole_area_A) != 1:
			print('Overlapping Calculating Volume detected in A...')
		if np.max(self.whole_area_B) != 1:
			print('Overlapping Calculating Volume detected in B...')

		if np.max(self.buffer_area_A) != 1:
			print('Overlapping Buffer Area detected in A...')
		if np.max(self.buffer_area_B) != 1:
			print('Overlapping Buffer Area detected in B...')

		# Uncovered Area
		# Calculating Area
		if np.min(np.sum(self.whole_area_A,axis=2)) == 0:
			print('Uncovered Calculating Volume detected in A...')
		if np.min(np.sum(self.whole_area_B,axis=2)) == 0:
			print('Uncovered Calculating Volume detected in B...')

		if np.min(np.sum(self.buffer_area_A,axis=2)) == 0:
			print('Uncovered Buffer Area detected in A...')
		if np.min(np.sum(self.buffer_area_B,axis=2)) == 0:
			print('Uncovered Buffer Area detected in B...')
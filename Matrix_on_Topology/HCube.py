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
		self.Columns_A = {}
		self.Columns_B = {}
		self.Columns_Core = {}

	# Draw Hypercube
	def Draw_HCube(param):
		# Whole computation volumes
		if param == 'whole':
			pass
		elif param == 'buffer':
			pass

	def __import_info(self, P, info):
		x, y, z, L, W, H, \
		LA_x, LA_y, LA_L, LA_H, \
		LB_x, LB_y, LB_L, LB_H = info  # unpack

		# shading areas
		self.whole_area_A[x:x + L][z:z + H][P] += 1
		self.whole_area_B[y:y + W][z:z + H][P] += 1
		self.buffer_area_A[LA_x:LA_x + LA_L][LA_y:LA_y + LB_H][P] += 1
		self.buffer_area_B[LB_x:LB_x + LB_L][LB_y:LB_y + LB_H][P] += 1

	def Shade_from_HBC(self, file_path, separator=','):
		F = open(file_path+'.hbc', 'r')
		FC = csv.reader(F, delimiter=separator)

		Now_at = -1
		for line in FC:
			# get core description
			if line[0][0] == '@':
				Now_at = (int)(line[0][1])

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
						print(info)
						self.__import_info(Now_at, info)
						num_ele = 0

					# Redundant info
				if num_ele != 0:  # non-formatted info
					print('Error in info with core#%i...\n' % (Now_at))
					break

		F.close()
		return

	# Optimizing Plan
	def get_Potentials(self, Col_dict):
		# Hash key : (area, length)
		Result = {}
		#Potentials = {p:[] for p in range(self.num_P)}
		Potentials = np.zeros([self.num_P,self.num_P], dtype='int32')  # potential rings

		# DFS
		for col in Col_dict:
			recievers = []      # Candidates to be added into the rings
			senders = []        # Candidates as sources
			for core in range(self.num_P):
				if col[core] == 0:
					recievers.append(core)
				else:
					senders.append(core)

			# Add to potentials
			for s in senders:
				for r in recievers:
					Potentials[s][r] += Col_dict[col] # area -> weight

			return Potentials

	def Calculate_Cycles(self):
		# Merge Identical Columns -> Get Cross-section areas
		Col_A = {}
		Col_B = {}

		for l in range(self.dim_L):
			# Columns on A
			for m in range(self.dim_M):
				# hash key
				Key = tuple(self.buffer_area_A[m][l][:])
				# Count members
				# Accumulate Cross-Section Area
				if Key in Col_A:
					Col_A[Key] += 1
				else:
					Col_A[Key] = 1

			# Columns on B
			for n in range(self.dim_N):
				# hash key
				Key = tuple(self.whole_area_B[l][n][:])
				# Accumulate Cross-Section Area
				if Key in Col_B:
					Col_B[Key] += 1
				else:
					Col_B[Key] = 1

		# Merge distinct columns : optimized plan
		#Potential_A = self.get_Potentials(Col_A)
		#Potential_B = self.get_Potentials(Col_B)
		#self.Columns_A = self.__merge_Columns(Col_A)
		#self.Columns_B = self.__merge_Columns(Col_B)
		# Statistics: Rings resp. to each core

		return Col_A,Col_B
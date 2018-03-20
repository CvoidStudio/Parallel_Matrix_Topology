//#pragma once
#include <iostream>
#include <mpi.h>
#include <fstream>
#include <memory>
#include <string>
#include <sstream>
#include <vector>

#define kill(a) if(a) delete[] a; a = 0

#define comp_id 99
#define reduce_id 100

#define Mat_A 0
#define Mat_B 1

#define Reduce_To	0
#define Reduce_From 1

enum Command
{
	send = 0, recv = 1, comp = 2, reduce = 3
};
struct comm {
	Command type;
	int i1, i2, i3, i4;

	comm() {
		type = comp;
	}

	comm(Command _comm) {
		type = _comm;
	}

	~comm() {
	}
};

class HCube
{
public:
	HCube() {}
	HCube(int size_m, int size_l, int size_n,
		int _buffer_limit);
	~HCube();

	void get_route(const char* filepath);
	void get_data(const char* filepath, float* buffer, bool flip,
		int y, int x, int H, int W);

	void comp_chunk(int A_low, int A_strech, int B_low, int B_strech);

	void send_chunk(float* data_at, int size, int dest);
	void recv_chunk(float* data_at, int size, int src);

	void reduce_to(int dest);
	void reduce_from(int src);

	void Excute();

	void dispose();

public:
	int position_x,
		position_y,
		position_z;

	int cubesize_m,
		cubesize_l,
		cubesize_n;

	int buffer_limit;

	int my_rank;

public:
	float* L_data;	 // Buffer in LHS
	int L_len;   // involved indices

	float* R_data;	 // Buffer in RHS
	int R_len;   // involved indices

	float* Result;	// computing result
	int C_Len;

public:
	std::vector<comm> Command_Series;
};


using namespace std;

static void set_zero(float* ptr, int size) {
	for (int i = 0; i < size; ++i)
		ptr[i] = 0;
}


HCube::HCube(int size_m, int size_l, int size_n,
	int _buffer_limit)
{
	buffer_limit = _buffer_limit;
}

HCube::~HCube()
{
	dispose();
}

void HCube::get_route(const char * filepath)
{
	char* templine = new char[2 << 13];

	ifstream F(filepath, ios::in);
	if (F.good()) {
		string word;
		while (!F.eof()) {
			F >> word;
			// Check if it is my_rank
			if (word[0] == '@' &&
				atoi(word.substr(1).c_str()) == my_rank) {
				// Get Matrix Data
				// cube shape
				F >> cubesize_m >> cubesize_l >> cubesize_n;
				// cout << cubesize_m << cubesize_l << cubesize_n;
				// Set Result Buffer
				L_data = new float[cubesize_m * cubesize_l];
				set_zero(L_data, cubesize_m * cubesize_l);

				R_data = new float[cubesize_l * cubesize_n];
				set_zero(R_data, cubesize_l * cubesize_n);

				Result = new float[cubesize_m * cubesize_n];
				set_zero(Result, cubesize_m * cubesize_n);

				// Read Matrix Data
				int x_A, x_B, y_A, y_B;
				F >> x_A >> y_A >> x_B >> y_B;
				get_data("mat_A.csv", L_data, true,
					y_A, x_A, cubesize_m, cubesize_l);
				get_data("mat_B.csv", R_data, false,
					y_B, x_B, cubesize_l, cubesize_n);
				// cout << x_A << y_A << x_B << y_B;
				// Get Command Series
				int l = 0;
				while (word[0] != '#') {
					F >> word;
					// cout << word << ' ';
					l++;

					if (word == "C") {
						comm m_COM(comp);
						F >> m_COM.i1;
						F >> m_COM.i2;
						F >> m_COM.i3;
						F >> m_COM.i4;
						Command_Series.push_back(m_COM);
					}
					else if (word == "S") {
						comm m_COM(send);
						F >> m_COM.i1;
						F >> word;
						if (word == "A")
							m_COM.i2 = Mat_A;
						else if (word == "B")
							m_COM.i2 = Mat_B;
						F >> m_COM.i3;
						F >> m_COM.i4;
						Command_Series.push_back(m_COM);
					}
					else if (word == "R") {
						comm m_COM(recv);
						F >> m_COM.i1;
						F >> word;
						if (word == "A")
							m_COM.i2 = Mat_A;
						else if (word == "B")
							m_COM.i2 = Mat_B;
						F >> m_COM.i3;
						F >> m_COM.i4;
						Command_Series.push_back(m_COM);
					}
					else if (word == "Red") {
						comm m_COM(reduce);
						F >> word;
						if (word == "t")
							m_COM.i1 = Reduce_To;
						else if (word == "f")
							m_COM.i1 = Reduce_From;

						F >> m_COM.i2;
						m_COM.i3 = m_COM.i4 = -1;
						Command_Series.push_back(m_COM);
					}
				}

				break;
			}
			// Skip the line
			F.getline(templine, 2 << 13);


		}
	}
	// Fail to Access Data File
	else
	{
		cerr << "Fail to open file: " << filepath << endl;
		F.close();
		exit(-1);
	}

	F.close();

	kill(templine);
}

void HCube::get_data(const char * filepath, float* buffer, bool flip,
	int y, int x, int H, int W)
{
	ifstream F(filepath, ios::in);
	if (F.good()) {
		int id = 0;
		float temp_val;

		// line-by-line
		// skip the empty lines
		char* empty_line = new char[2 << 13];
		for (int i = 0; i < y; ++i) {
			F.getline(empty_line, 2 << 13);
		}

		// read the data lines
		int id1 = 0;
		for (int i = 0; i < H; ++i) {
			// skip the left brim
			for (int j = 0; j < x; ++j) {
				F >> temp_val;
			}

			// A or B 
			if (flip) { // AT
						// Read in
				id1 = i;
				for (int k = 0; k < W; ++k) {
					F >> L_data[id1];
					id1 += cubesize_m;
				}

				F.getline(empty_line, 2 << 13);
			}
			else {		// B
						// Read in
				for (int k = 0; k < W; ++k) {
					F >> R_data[id1];
					id1++;
				}

				F.getline(empty_line, 2 << 13);
			}

		}

		delete[] empty_line;

	}
	// Fail to Access Data File
	else
	{
		cerr << "Fail to open file: " << filepath << endl;
		F.close();
		exit(-1);
	}

	F.close();
}

void HCube::comp_chunk(int A_low, int A_strech, int B_low, int B_strech)
{
	float* A0 = &L_data[A_low*cubesize_m];
	float* B0 = &R_data[B_low*cubesize_n];
	int lM = 0, lN = 0;
	for (int l = 0; l < A_strech; ++l) {
		int mN = 0;
		for (int m = 0; m < cubesize_m; ++m) {
			for (int n = 0; n < cubesize_n; ++n) {
				Result[mN] +=
					A0[lM + m] * B0[lN + n];
				mN++;
			}
		}
		lM += cubesize_m;
		lN += cubesize_n;
	}
}

void HCube::send_chunk(float * data_at, int size, int dest)
{
	MPI_Send(data_at, size, MPI_FLOAT, dest, comp_id, MPI_COMM_WORLD);
}

void HCube::recv_chunk(float * data_at, int size, int src)
{
	MPI_Recv(data_at, size, MPI_FLOAT, src, comp_id, MPI_COMM_WORLD, MPI_STATUSES_IGNORE);
}

void HCube::reduce_to(int dest)
{
	MPI_Send(Result, cubesize_m*cubesize_n, MPI_FLOAT,
		dest, reduce_id, MPI_COMM_WORLD);
}

void HCube::reduce_from(int src)
{
	float* temp_C = new float[cubesize_m*cubesize_n];
	//memset(temp_C, 0, sizeof(float)*cubesize_m * cubesize_n);
	MPI_Recv(temp_C, cubesize_m*cubesize_n, MPI_FLOAT,
		src, reduce_id, MPI_COMM_WORLD, MPI_STATUSES_IGNORE);

	// Reduce res += temp_C
	int iN = 0;
	for (int i = 0; i < cubesize_m; ++i) {
		for (int j = 0; j < cubesize_n; ++j) {
			Result[iN] += temp_C[iN];
			iN++;
		}
	}

	delete[] temp_C;
}

void HCube::Excute()
{
	for (comm& C : Command_Series) {
		switch (C.type)
		{
			// ---------- Compute ---------- //
		case comp:
			comp_chunk(C.i1, C.i2, C.i3, C.i4);
			break;
			// ------------ Send ----------- //
		case send:
			if (C.i2 == Mat_A) {
				send_chunk(&(L_data[C.i3*cubesize_m]),
					C.i4 * cubesize_m, C.i1);
			}
			else if (C.i2 == Mat_B) {
				send_chunk(&(R_data[C.i3*cubesize_n]),
					C.i4 * cubesize_n, C.i1);
			}
			break;
			// ------------ Recv ----------- //
		case recv:
			if (C.i2 == Mat_A) {
				recv_chunk(&(L_data[C.i3*cubesize_m]),
					C.i4 * cubesize_m, C.i1);
			}
			else if (C.i2 == Mat_B) {
				recv_chunk(&(R_data[C.i3*cubesize_n]),
					C.i4 * cubesize_n, C.i1);
			}
			break;
			// ---------- Reduce ----------- //
		case reduce:
			if (C.i1 == Reduce_To) {
				reduce_to(C.i2);
			}
			else if (C.i1 == Reduce_From) {
				reduce_from(C.i2);
			}
			break;
			// ------------ None ----------- //
		default:	break;
		}
	}
}


void HCube::dispose()
{
	kill(Result);
	kill(L_data);
	kill(R_data);

	Command_Series.clear();
}

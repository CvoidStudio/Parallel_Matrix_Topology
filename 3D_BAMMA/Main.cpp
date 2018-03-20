#include "hypercube.hpp"

using namespace std;

static int num_P;
static int m_rank;

int main(int argc, char* argv[]) {
	HCube my_Cube;

	// MPI Initialize

	MPI_Init(&argc, &argv);
	MPI_Comm_rank(MPI_COMM_WORLD, &m_rank);
	MPI_Comm_size(MPI_COMM_WORLD, &num_P);

	my_Cube.my_rank = m_rank;
	// cout << my_Cube.my_rank << endl;

	// Initialize
	// get target file
	string target("Experiments/");
	target += argv[argc - 1];
	target += ".comm";
	my_Cube.get_route(target.c_str());

	// test barrier
	if (m_rank == 0)
	{
		double Sstart = MPI_Wtime();
		while (MPI_Wtime() - Sstart < 1.0)
		{
			;
		}
	}

	// Sync
	MPI_Barrier(MPI_COMM_WORLD);

	// Count the time
	double Time = MPI_Wtime();
	my_Cube.Excute();
	double Time2 = MPI_Wtime();

	MPI_Barrier(MPI_COMM_WORLD);

	// Report
	if (m_rank == num_P - 1) {
		double max_time = Time2-Time;
		cout << "Time cost for last (" << argv[argc - 1] << ") -> ";
		printf("%.4f sec.\n", max_time);
		double tmp_time = 0.0;
		for (int i = 0; i < num_P - 1; ++i){
			MPI_Recv(&tmp_time, 1, MPI_DOUBLE, i, 50, MPI_COMM_WORLD, MPI_STATUSES_IGNORE);
			if (tmp_time > max_time)  max_time = tmp_time;
			
			tmp_time = 0.0;
		}
		
		cout << "Time cost for (" << argv[argc - 1] << ") -> ";
		printf("%.4f sec.\n", max_time);	
	}
	else{
		double my_Time = Time2-Time;
		MPI_Send(&my_Time, 1, MPI_DOUBLE, num_P - 1, 50, MPI_COMM_WORLD);
	}
	
	// Finish
	MPI_Finalize();
	return 0;
}


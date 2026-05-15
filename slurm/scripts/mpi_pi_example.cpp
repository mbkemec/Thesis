#define OMPI_SKIP_MPICXX
#include <mpi.h>
#include <iostream>
#include <iomanip>

int main(int argc, char** argv) {
    const long long N = 1000000000LL;
    const double step = 1.0 / (double)N;

    MPI_Init(&argc, &argv);

    int rank, size, len;
    char name[MPI_MAX_PROCESSOR_NAME];

    MPI_Comm_rank(MPI_COMM_WORLD, &rank);
    MPI_Comm_size(MPI_COMM_WORLD, &size);
    MPI_Get_processor_name(name, &len);

    std::cout << "Rank " << rank << "/" << size
              << " running on " << name << std::endl;

    double local_sum = 0.0;
    for (long long i = rank; i < N; i += size) {
        double x = (i + 0.5) * step;
        local_sum += 4.0 / (1.0 + x * x);
    }

    double global_sum = 0.0;
    MPI_Reduce(&local_sum, &global_sum, 1, MPI_DOUBLE, MPI_SUM, 0, MPI_COMM_WORLD);

    if (rank == 0) {
        double pi = step * global_sum;
        std::cout << std::setprecision(15) << "pi = " << pi << std::endl;
    }

    MPI_Finalize();
    return 0;
}

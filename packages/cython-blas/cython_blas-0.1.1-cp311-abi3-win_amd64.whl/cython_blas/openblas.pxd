

cpdef int sgemm(
    float alpha,
    const float [:, :] A,
    const float [:, :] B,
    float beta,
    float [:, :] C
) except -1


cpdef int dgemm(
    double alpha,
    const double [:, :] A,
    const double [:, :] B,
    double beta,
    double [:, :] C
) except -1


cpdef int cgemm(
    float complex alpha,
    bint conjugate_a,
    const float complex [:, :] A,
    bint conjugate_b,
    const float complex [:, :] B,
    float complex beta,
    float complex [:, :] C,
) except -1


cpdef int cgemm3m(
    float complex alpha,
    bint conjugate_a,
    const float complex [:, :] A,
    bint conjugate_b,
    const float complex [:, :] B,
    float complex beta,
    float complex [:, :] C,
) except -1


cpdef int zgemm(
    double complex alpha,
    bint conjugate_a,
    const double complex [:, :] A,
    bint conjugate_b,
    const double complex [:, :] B,
    double complex beta,
    double complex [:, :] C,
) except -1


cpdef int zgemm3m(
    double complex alpha,
    bint conjugate_a,
    const double complex [:, :] A,
    bint conjugate_b,
    const double complex [:, :] B,
    double complex beta,
    double complex [:, :] C,
) except -1


cpdef int get_num_threads() noexcept nogil


cpdef void set_num_threads(int num_threads) noexcept nogil


cpdef str get_config()


cpdef str get_corename()


cpdef int get_parallel() noexcept nogil

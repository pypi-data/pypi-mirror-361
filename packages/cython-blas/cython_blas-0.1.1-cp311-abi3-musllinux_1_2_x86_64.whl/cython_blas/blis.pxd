
from numpy cimport ndarray

from cython_blas cimport _blis
from cython_blas._blis cimport dim_t


cpdef enum Precision:
    DefaultPrecision = -99
    DoublePrecision = _blis.BLIS_DOUBLE_PREC
    SinglePrecision = _blis.BLIS_SINGLE_PREC


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


cpdef int zgemm(
    double complex alpha,
    bint conjugate_a,
    const double complex [:, :] A,
    bint conjugate_b,
    const double complex [:, :] B,
    double complex beta,
    double complex [:, :] C,
) except -1


cpdef int gemm(
    double alpha,
    bint conjugate_a,
    ndarray A,
    bint conjugate_b,
    ndarray B,
    double complex beta,
    ndarray C,
    Precision precision = ?,
) except -1


cpdef str get_int_type_size()


cpdef str get_version()


cpdef str get_arch()


cpdef void set_num_threads(dim_t n_threads) noexcept nogil


cpdef dim_t get_num_threads() noexcept nogil

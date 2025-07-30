
cimport cython

from cython_blas cimport _cblas
from cython_blas._cblas cimport blasint


cpdef enum Order:
    RowMajor = _cblas.CblasRowMajor
    ColMajor = _cblas.CblasColMajor

cpdef enum Transpose:
    NoTrans = _cblas.CblasNoTrans
    Trans = _cblas.CblasTrans
    ConjNoTrans = _cblas.CblasConjNoTrans
    ConjTrans = _cblas.CblasConjTrans

cpdef enum UpperLower:
    Upper = _cblas.CblasUpper
    Lower = _cblas.CblasLower

cpdef enum Diagonal:
    NonUnitDiag = _cblas.CblasNonUnit
    UnitDiag = _cblas.CblasUnit

cpdef enum Side:
    LeftSide = _cblas.CblasLeft
    RightSide = _cblas.CblasRight


@cython.cdivision(True)
@cython.embedsignature(True)
@cython.wraparound(False)
cpdef int sgemm(
    float alpha,
    const float [:, :] A,
    const float [:, :] B,
    float beta,
    float [:, :] C
) except -1:
    r"""Matrix multiplication of single precision matrices.

    .. math::

        C = \alpha A B + \beta C

    Args:
        alpha: Scalar multiplier for A @ B
        A: The A matrix.
        B: The B matrix. The number of rows in this matrix must equal the number of columns
            in `A`.
        beta: Scalar multiplier for C
        C: The C matrix. This matrix must have the same number of rows as `A` and the same
            number of columns as `B`. The result will be written to this matrix.
    """
    cdef Order order_a = ColMajor if A.strides[0] == sizeof(float) else RowMajor
    cdef Order order_b = ColMajor if B.strides[0] == sizeof(float) else RowMajor
    cdef Order order_c = ColMajor if C.strides[0] == sizeof(float) else RowMajor
    cdef blasint m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)
    if order_a == RowMajor and A.strides[1] != sizeof(float):
        msg = "matrix A must be contiguous along one dimension"
        raise ValueError(msg)
    if order_b == RowMajor and B.strides[1] != sizeof(float):
        msg = "matrix B must be contiguous along one dimension"
        raise ValueError(msg)
    if order_c == RowMajor and C.strides[1] != sizeof(float):
        msg = "matrix C must be contiguous along one dimension"
        raise ValueError(msg)
    cdef blasint lda = A.strides[1] / sizeof(float) if order_a == ColMajor else A.strides[0] / sizeof(float)
    cdef blasint ldb = B.strides[1] / sizeof(float) if order_b == ColMajor else B.strides[0] / sizeof(float)
    cdef blasint ldc = C.strides[1] / sizeof(float) if order_c == ColMajor else C.strides[0] / sizeof(float)
    cdef Transpose trans_a = NoTrans if order_a == order_c else Trans
    cdef Transpose trans_b = NoTrans if order_b == order_c else Trans

    with nogil, cython.boundscheck(False):
        _cblas.scipy_cblas_sgemm64_(
            <_cblas.CBLAS_ORDER> order_c, <_cblas.CBLAS_TRANSPOSE> trans_a, <_cblas.CBLAS_TRANSPOSE> trans_b,
            m, n, k,
            alpha, &A[0, 0], lda, &B[0, 0], ldb, beta, &C[0, 0], ldc
        )
    return 0


@cython.cdivision(True)
@cython.embedsignature(True)
@cython.wraparound(False)
cpdef int dgemm(
    double alpha,
    const double [:, :] A,
    const double [:, :] B,
    double beta,
    double [:, :] C
) except -1:
    r"""Matrix multiplication of double precision matrices.

    .. math::

        C = \alpha A B + \beta C

    Args:
        alpha: Scalar multiplier for A @ B
        A: The A matrix.
        B: The B matrix. The number of rows in this matrix must equal the number of columns
            in `A`.
        beta: Scalar multiplier for C
        C: The C matrix. This matrix must have the same number of rows as `A` and the same
            number of columns as `B`. The result will be written to this matrix.
    """
    cdef Order order_a = ColMajor if A.strides[0] == sizeof(double) else RowMajor
    cdef Order order_b = ColMajor if B.strides[0] == sizeof(double) else RowMajor
    cdef Order order_c = ColMajor if C.strides[0] == sizeof(double) else RowMajor
    cdef blasint m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)
    if order_a == RowMajor and A.strides[1] != sizeof(double):
        msg = "matrix A must be contiguous along one dimension"
        raise ValueError(msg)
    if order_b == RowMajor and B.strides[1] != sizeof(double):
        msg = "matrix B must be contiguous along one dimension"
        raise ValueError(msg)
    if order_c == RowMajor and C.strides[1] != sizeof(double):
        msg = "matrix C must be contiguous along one dimension"
        raise ValueError(msg)
    cdef blasint lda = A.strides[1] / sizeof(double) if order_a == ColMajor else A.strides[0] / sizeof(double)
    cdef blasint ldb = B.strides[1] / sizeof(double) if order_b == ColMajor else B.strides[0] / sizeof(double)
    cdef blasint ldc = C.strides[1] / sizeof(double) if order_c == ColMajor else C.strides[0] / sizeof(double)
    cdef Transpose trans_a = NoTrans if order_a == order_c else Trans
    cdef Transpose trans_b = NoTrans if order_b == order_c else Trans

    with nogil, cython.boundscheck(False):
        _cblas.scipy_cblas_dgemm64_(
            <_cblas.CBLAS_ORDER> order_c, <_cblas.CBLAS_TRANSPOSE> trans_a, <_cblas.CBLAS_TRANSPOSE> trans_b,
            m, n, k,
            alpha, &A[0, 0], lda, &B[0, 0], ldb, beta, &C[0, 0], ldc
        )
    return 0


@cython.cdivision(True)
@cython.embedsignature(True)
@cython.wraparound(False)
cpdef int cgemm(
    float complex alpha,
    bint conjugate_a,
    const float complex [:, :] A,
    bint conjugate_b,
    const float complex [:, :] B,
    float complex beta,
    float complex [:, :] C,
) except -1:
    r"""Matrix multiplication of single precision complex matrices.

    .. math::
        C = \alpha A B + \beta C

    If `conjugate_a` is True, then matrix :math:`A` is implicitly conjugated before performing
    the multiplication. Similarly for `conjugate_b`.

    Args:
        alpha: Scalar multiplier for A @ B
        conjugate_a: If True, matrix `A` will be conjugated.
        A: The A matrix.
        conjugate_b: If True, matrix `B` will be conjugated.
        B: The B matrix. The number of rows in this matrix must equal the number of columns
            in `A`.
        beta: Scalar multiplier for C
        C: The C matrix. This matrix must have the same number of rows as `A` and the same
            number of columns as `B`. The result will be written to this matrix.
    """
    cdef Order order_a = ColMajor if A.strides[0] == sizeof(float complex) else RowMajor
    cdef Order order_b = ColMajor if B.strides[0] == sizeof(float complex) else RowMajor
    cdef Order order_c = ColMajor if C.strides[0] == sizeof(float complex) else RowMajor
    cdef blasint m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)
    if order_a == RowMajor and A.strides[1] != sizeof(float complex):
        msg = "matrix A must be contiguous along one dimension"
        raise ValueError(msg)
    if order_b == RowMajor and B.strides[1] != sizeof(float complex):
        msg = "matrix B must be contiguous along one dimension"
        raise ValueError(msg)
    if order_c == RowMajor and C.strides[1] != sizeof(float complex):
        msg = "matrix C must be contiguous along one dimension"
        raise ValueError(msg)
    cdef blasint lda = (A.strides[1] / sizeof(float complex)
                        if order_a == ColMajor else A.strides[0] / sizeof(float complex))
    cdef blasint ldb = (B.strides[1] / sizeof(float complex)
                        if order_b == ColMajor else B.strides[0] / sizeof(float complex))
    cdef blasint ldc = (C.strides[1] / sizeof(float complex)
                        if order_c == ColMajor else C.strides[0] / sizeof(float complex))
    cdef Transpose trans_a
    if conjugate_a:
        trans_a = ConjNoTrans if order_a == order_c else ConjTrans
    else:
        trans_a = NoTrans if order_a == order_c else Trans
    cdef Transpose trans_b
    if conjugate_b:
        trans_b = ConjNoTrans if order_b == order_c else ConjTrans
    else:
        trans_b = NoTrans if order_b == order_c else Trans

    with nogil, cython.boundscheck(False):
        _cblas.scipy_cblas_cgemm64_(
            <_cblas.CBLAS_ORDER> order_c, <_cblas.CBLAS_TRANSPOSE> trans_a, <_cblas.CBLAS_TRANSPOSE> trans_b,
            m, n, k,
            &alpha, &A[0, 0], lda, &B[0, 0], ldb, &beta, &C[0, 0], ldc
        )
    return 0


@cython.cdivision(True)
@cython.embedsignature(True)
@cython.wraparound(False)
cpdef int cgemm3m(
    float complex alpha,
    bint conjugate_a,
    const float complex [:, :] A,
    bint conjugate_b,
    const float complex [:, :] B,
    float complex beta,
    float complex [:, :] C,
) except -1:
    r"""Matrix multiplication of single precision complex matrices, using an approximate algorithm.

    This function is roughly 20% faster than `cgemm`, but is less accurate.

    .. math::
        C = \alpha A B + \beta C

    If `conjugate_a` is True, then matrix :math:`A` is implicitly conjugated before performing
    the multiplication. Similarly for `conjugate_b`.

    Args:
        alpha: Scalar multiplier for A @ B
        conjugate_a: If True, matrix `A` will be conjugated.
        A: The A matrix.
        conjugate_b: If True, matrix `B` will be conjugated.
        B: The B matrix. The number of rows in this matrix must equal the number of columns
            in `A`.
        beta: Scalar multiplier for C
        C: The C matrix. This matrix must have the same number of rows as `A` and the same
            number of columns as `B`. The result will be written to this matrix.
    """
    cdef Order order_a = ColMajor if A.strides[0] == sizeof(float complex) else RowMajor
    cdef Order order_b = ColMajor if B.strides[0] == sizeof(float complex) else RowMajor
    cdef Order order_c = ColMajor if C.strides[0] == sizeof(float complex) else RowMajor
    cdef blasint m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)
    if order_a == RowMajor and A.strides[1] != sizeof(float complex):
        msg = "matrix A must be contiguous along one dimension"
        raise ValueError(msg)
    if order_b == RowMajor and B.strides[1] != sizeof(float complex):
        msg = "matrix B must be contiguous along one dimension"
        raise ValueError(msg)
    if order_c == RowMajor and C.strides[1] != sizeof(float complex):
        msg = "matrix C must be contiguous along one dimension"
        raise ValueError(msg)
    cdef blasint lda = (A.strides[1] / sizeof(float complex)
                        if order_a == ColMajor else A.strides[0] / sizeof(float complex))
    cdef blasint ldb = (B.strides[1] / sizeof(float complex)
                        if order_b == ColMajor else B.strides[0] / sizeof(float complex))
    cdef blasint ldc = (C.strides[1] / sizeof(float complex)
                        if order_c == ColMajor else C.strides[0] / sizeof(float complex))
    cdef Transpose trans_a
    if conjugate_a:
        trans_a = ConjNoTrans if order_a == order_c else ConjTrans
    else:
        trans_a = NoTrans if order_a == order_c else Trans
    cdef Transpose trans_b
    if conjugate_b:
        trans_b = ConjNoTrans if order_b == order_c else ConjTrans
    else:
        trans_b = NoTrans if order_b == order_c else Trans

    with nogil, cython.boundscheck(False):
        _cblas.scipy_cblas_cgemm3m64_(
            <_cblas.CBLAS_ORDER> order_c, <_cblas.CBLAS_TRANSPOSE> trans_a, <_cblas.CBLAS_TRANSPOSE> trans_b,
            m, n, k,
            &alpha, &A[0, 0], lda, &B[0, 0], ldb, &beta, &C[0, 0], ldc
        )
    return 0


@cython.cdivision(True)
@cython.embedsignature(True)
@cython.wraparound(False)
cpdef int zgemm(
    double complex alpha,
    bint conjugate_a,
    const double complex [:, :] A,
    bint conjugate_b,
    const double complex [:, :] B,
    double complex beta,
    double complex [:, :] C,
) except -1:
    r"""Matrix multiplication of double precision complex matrices.

    .. math::
        C = \alpha A B + \beta C

    If `conjugate_a` is True, then matrix :math:`A` is implicitly conjugated before performing
    the multiplication. Similarly for `conjugate_b`.

    Args:
        alpha: Scalar multiplier for A @ B
        conjugate_a: If True, matrix `A` will be conjugated.
        A: The A matrix.
        conjugate_b: If True, matrix `B` will be conjugated.
        B: The B matrix. The number of rows in this matrix must equal the number of columns
            in `A`.
        beta: Scalar multiplier for C
        C: The C matrix. This matrix must have the same number of rows as `A` and the same
            number of columns as `B`. The result will be written to this matrix.
    """
    cdef Order order_a = ColMajor if A.strides[0] == sizeof(double complex) else RowMajor
    cdef Order order_b = ColMajor if B.strides[0] == sizeof(double complex) else RowMajor
    cdef Order order_c = ColMajor if C.strides[0] == sizeof(double complex) else RowMajor
    cdef blasint m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)
    if order_a == RowMajor and A.strides[1] != sizeof(double complex):
        msg = "matrix A must be contiguous along one dimension"
        raise ValueError(msg)
    if order_b == RowMajor and B.strides[1] != sizeof(double complex):
        msg = "matrix B must be contiguous along one dimension"
        raise ValueError(msg)
    if order_c == RowMajor and C.strides[1] != sizeof(double complex):
        msg = "matrix C must be contiguous along one dimension"
        raise ValueError(msg)
    cdef blasint lda = (A.strides[1] / sizeof(double complex)
                        if order_a == ColMajor else A.strides[0] / sizeof(double complex))
    cdef blasint ldb = (B.strides[1] / sizeof(double complex)
                        if order_b == ColMajor else B.strides[0] / sizeof(double complex))
    cdef blasint ldc = (C.strides[1] / sizeof(double complex)
                        if order_c == ColMajor else C.strides[0] / sizeof(double complex))
    cdef Transpose trans_a
    if conjugate_a:
        trans_a = ConjNoTrans if order_a == order_c else ConjTrans
    else:
        trans_a = NoTrans if order_a == order_c else Trans
    cdef Transpose trans_b
    if conjugate_b:
        trans_b = ConjNoTrans if order_b == order_c else ConjTrans
    else:
        trans_b = NoTrans if order_b == order_c else Trans

    with nogil, cython.boundscheck(False):
        _cblas.scipy_cblas_zgemm64_(
            <_cblas.CBLAS_ORDER> order_c, <_cblas.CBLAS_TRANSPOSE> trans_a, <_cblas.CBLAS_TRANSPOSE> trans_b,
            m, n, k,
            &alpha, &A[0, 0], lda, &B[0, 0], ldb, &beta, &C[0, 0], ldc
        )
    return 0


@cython.cdivision(True)
@cython.embedsignature(True)
@cython.wraparound(False)
cpdef int zgemm3m(
    double complex alpha,
    bint conjugate_a,
    const double complex [:, :] A,
    bint conjugate_b,
    const double complex [:, :] B,
    double complex beta,
    double complex [:, :] C,
) except -1:
    r"""Matrix multiplication of double precision complex matrices, using an approximate algorithm.

    This function is roughly 20% faster than `zgemm`, but is less accurate.

    .. math::
        C = \alpha A B + \beta C

    If `conjugate_a` is True, then matrix :math:`A` is implicitly conjugated before performing
    the multiplication. Similarly for `conjugate_b`.

    Args:
        alpha: Scalar multiplier for A @ B
        conjugate_a: If True, matrix `A` will be conjugated.
        A: The A matrix.
        conjugate_b: If True, matrix `B` will be conjugated.
        B: The B matrix. The number of rows in this matrix must equal the number of columns
            in `A`.
        beta: Scalar multiplier for C
        C: The C matrix. This matrix must have the same number of rows as `A` and the same
            number of columns as `B`. The result will be written to this matrix.
    """
    cdef Order order_a = ColMajor if A.strides[0] == sizeof(double complex) else RowMajor
    cdef Order order_b = ColMajor if B.strides[0] == sizeof(double complex) else RowMajor
    cdef Order order_c = ColMajor if C.strides[0] == sizeof(double complex) else RowMajor
    cdef blasint m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)
    if order_a == RowMajor and A.strides[1] != sizeof(double complex):
        msg = "matrix A must be contiguous along one dimension"
        raise ValueError(msg)
    if order_b == RowMajor and B.strides[1] != sizeof(double complex):
        msg = "matrix B must be contiguous along one dimension"
        raise ValueError(msg)
    if order_c == RowMajor and C.strides[1] != sizeof(double complex):
        msg = "matrix C must be contiguous along one dimension"
        raise ValueError(msg)
    cdef blasint lda = (A.strides[1] / sizeof(double complex)
                        if order_a == ColMajor else A.strides[0] / sizeof(double complex))
    cdef blasint ldb = (B.strides[1] / sizeof(double complex)
                        if order_b == ColMajor else B.strides[0] / sizeof(double complex))
    cdef blasint ldc = (C.strides[1] / sizeof(double complex)
                        if order_c == ColMajor else C.strides[0] / sizeof(double complex))
    cdef Transpose trans_a
    if conjugate_a:
        trans_a = ConjNoTrans if order_a == order_c else ConjTrans
    else:
        trans_a = NoTrans if order_a == order_c else Trans
    cdef Transpose trans_b
    if conjugate_b:
        trans_b = ConjNoTrans if order_b == order_c else ConjTrans
    else:
        trans_b = NoTrans if order_b == order_c else Trans

    with nogil, cython.boundscheck(False):
        _cblas.scipy_cblas_zgemm3m64_(
            <_cblas.CBLAS_ORDER> order_c, <_cblas.CBLAS_TRANSPOSE> trans_a, <_cblas.CBLAS_TRANSPOSE> trans_b,
            m, n, k,
            &alpha, &A[0, 0], lda, &B[0, 0], ldb, &beta, &C[0, 0], ldc
        )
    return 0


@cython.cdivision(True)
@cython.embedsignature(True)
@cython.wraparound(False)
cpdef int dsymm_ab(
    double alpha,
    UpperLower upper_lower,
    const double [:, :] A,
    const double [:, :] B,
    double beta,
    double [:, :] C
) except -1:
    """Symmetric matrix multiplication."""
    cdef Order order_a = ColMajor if A.strides[0] == sizeof(double) else RowMajor
    cdef Order order_b = ColMajor if B.strides[0] == sizeof(double) else RowMajor
    cdef Order order_c = ColMajor if C.strides[0] == sizeof(double) else RowMajor
    cdef blasint m = C.shape[0], n = C.shape[1]
    if A.shape[0] != m or A.shape[1] != m or B.shape[0] != m or B.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)
    if order_b != order_c:
        msg = "memory order not compatible, matrices B and C must have the same memory layout"
        raise ValueError(msg)
    cdef blasint lda = (A.strides[1] / sizeof(double)
                        if order_a == ColMajor else A.strides[0] / sizeof(double))
    cdef blasint ldb = (B.strides[1] / sizeof(double)
                        if order_b == ColMajor else B.strides[0] / sizeof(double))
    cdef blasint ldc = (C.strides[1] / sizeof(double)
                        if order_c == ColMajor else C.strides[0] / sizeof(double))
    cdef Side side = LeftSide
    if order_a != order_c:
        upper_lower = Upper if upper_lower == Lower else Lower

    with nogil, cython.boundscheck(False):
        _cblas.scipy_cblas_dsymm64_(
            <_cblas.CBLAS_ORDER> order_c, <_cblas.CBLAS_SIDE> side, <_cblas.CBLAS_UPLO> upper_lower,
            m, n,
            alpha, &A[0, 0], lda, &B[0, 0], ldb, beta, &C[0, 0], ldc)
    return 0


@cython.embedsignature(True)
cpdef int get_num_threads() noexcept nogil:
    """Return the number of threads currently used by OpenBLAS."""
    return _cblas.scipy_openblas_get_num_threads64_()


@cython.embedsignature(True)
cpdef void set_num_threads(int num_threads) noexcept nogil:
    """Set the number of threads used by OpenBLAS."""
    _cblas.scipy_openblas_set_num_threads64_(num_threads)


@cython.embedsignature(True)
cpdef str get_config():
    """Return configuration information specified when OpenBLAS was compiled."""
    cdef char* cstring = _cblas.scipy_openblas_get_config64_()
    cdef bytes bstring = cstring
    return bstring.decode('ascii')


@cython.embedsignature(True)
cpdef str get_corename():
    """Return the core name currently used by OpenBLAS."""
    cdef char* cstring = _cblas.scipy_openblas_get_corename64_()
    cdef bytes bstring = cstring
    return bstring.decode('ascii')


@cython.embedsignature(True)
cpdef int get_parallel() noexcept nogil:
    """Return the type of parallelism specified when OpenBLAS was compiled.

    A return value of 0 means no parallelism.
    A return value of 1 means the normal threading model.
    A return value of 2 means the OpenMP threading model.
    """
    return _cblas.scipy_openblas_get_parallel64_()

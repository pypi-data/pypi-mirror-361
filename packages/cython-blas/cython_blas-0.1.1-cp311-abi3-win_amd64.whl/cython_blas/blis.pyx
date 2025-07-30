
cimport cython
cimport numpy as np
from numpy cimport ndarray

from cython_blas cimport _blis
from cython_blas._blis cimport dim_t, obj_t

np.import_array()

cdef extern from * nogil:
    cdef void static_assert(bint)


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
    cdef dim_t m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)

    cdef obj_t bli_a, bli_b, bli_c, bli_alpha, bli_beta
    with nogil, cython.boundscheck(False):
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_FLOAT,
            &alpha,
            &bli_alpha,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_FLOAT,
            m,
            k,
            <void*> &A[0, 0],
            A.strides[0] / sizeof(float),
            A.strides[1] / sizeof(float),
            &bli_a,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_FLOAT,
            k,
            n,
            <void*> &B[0, 0],
            B.strides[0] / sizeof(float),
            B.strides[1] / sizeof(float),
            &bli_b,
        )
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_FLOAT,
            &beta,
            &bli_beta,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_FLOAT,
            m,
            n,
            <void*> &C[0, 0],
            C.strides[0] / sizeof(float),
            C.strides[1] / sizeof(float),
            &bli_c,
        )

        _blis.bli_gemm(&bli_alpha, &bli_a, &bli_b, &bli_beta, &bli_c)
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
    cdef dim_t m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)

    cdef obj_t bli_a, bli_b, bli_c, bli_alpha, bli_beta
    with nogil, cython.boundscheck(False):
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_DOUBLE,
            &alpha,
            &bli_alpha,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_DOUBLE,
            m,
            k,
            <void*> &A[0, 0],
            A.strides[0] / sizeof(double),
            A.strides[1] / sizeof(double),
            &bli_a,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_DOUBLE,
            k,
            n,
            <void*> &B[0, 0],
            B.strides[0] / sizeof(double),
            B.strides[1] / sizeof(double),
            &bli_b,
        )
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_DOUBLE,
            &beta,
            &bli_beta,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_DOUBLE,
            m,
            n,
            <void*> &C[0, 0],
            C.strides[0] / sizeof(double),
            C.strides[1] / sizeof(double),
            &bli_c,
        )

        _blis.bli_gemm(&bli_alpha, &bli_a, &bli_b, &bli_beta, &bli_c)
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
    cdef dim_t m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)

    cdef obj_t bli_a, bli_b, bli_c, bli_alpha, bli_beta
    with nogil, cython.boundscheck(False):
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_SCOMPLEX,
            &alpha,
            &bli_alpha,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_SCOMPLEX,
            m,
            k,
            <void*> &A[0, 0],
            A.strides[0] / sizeof(float complex),
            A.strides[1] / sizeof(float complex),
            &bli_a,
        )
        if conjugate_a:
            _blis.bli_obj_set_conj(_blis.BLIS_CONJUGATE, &bli_a)
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_SCOMPLEX,
            k,
            n,
            <void*> &B[0, 0],
            B.strides[0] / sizeof(float complex),
            B.strides[1] / sizeof(float complex),
            &bli_b,
        )
        if conjugate_b:
            _blis.bli_obj_set_conj(_blis.BLIS_CONJUGATE, &bli_b)
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_SCOMPLEX,
            &beta,
            &bli_beta,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_SCOMPLEX,
            m,
            n,
            <void*> &C[0, 0],
            C.strides[0] / sizeof(float complex),
            C.strides[1] / sizeof(float complex),
            &bli_c,
        )

        _blis.bli_gemm(&bli_alpha, &bli_a, &bli_b, &bli_beta, &bli_c)
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
    cdef dim_t m = A.shape[0], n = B.shape[1], k = A.shape[1]
    if B.shape[0] != k or C.shape[0] != m or C.shape[1] != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)

    cdef obj_t bli_a, bli_b, bli_c, bli_alpha, bli_beta
    with nogil, cython.boundscheck(False):
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_DCOMPLEX,
            &alpha,
            &bli_alpha,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_DCOMPLEX,
            m,
            k,
            <void*> &A[0, 0],
            A.strides[0] / sizeof(double complex),
            A.strides[1] / sizeof(double complex),
            &bli_a,
        )
        if conjugate_a:
            _blis.bli_obj_set_conj(_blis.BLIS_CONJUGATE, &bli_a)
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_DCOMPLEX,
            k,
            n,
            <void*> &B[0, 0],
            B.strides[0] / sizeof(double complex),
            B.strides[1] / sizeof(double complex),
            &bli_b,
        )
        if conjugate_b:
            _blis.bli_obj_set_conj(_blis.BLIS_CONJUGATE, &bli_b)
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_DCOMPLEX,
            &beta,
            &bli_beta,
        )
        _blis.bli_obj_create_with_attached_buffer(
            _blis.BLIS_DCOMPLEX,
            m,
            n,
            <void*> &C[0, 0],
            C.strides[0] / sizeof(double complex),
            C.strides[1] / sizeof(double complex),
            &bli_c,
        )

        _blis.bli_gemm(&bli_alpha, &bli_a, &bli_b, &bli_beta, &bli_c)
    return 0


# verify -99 is not used and is valid as an error flag
static_assert(_blis.BLIS_FLOAT != -99)
static_assert(_blis.BLIS_DOUBLE != -99)
static_assert(_blis.BLIS_SCOMPLEX != -99)
static_assert(_blis.BLIS_DCOMPLEX != -99)


cdef int _convert_type(ndarray arr) except -99:
    """Convert from NumPy type to BLIS type."""
    cdef int npy_type = np.PyArray_TYPE(arr)
    if npy_type == np.NPY_FLOAT32:
        return _blis.BLIS_FLOAT
    if npy_type == np.NPY_FLOAT64:
        return _blis.BLIS_DOUBLE
    if npy_type == np.NPY_COMPLEX64:
        return _blis.BLIS_SCOMPLEX
    if npy_type == np.NPY_COMPLEX128:
        return _blis.BLIS_DCOMPLEX
    msg = 'unsupported type'
    raise ValueError(msg)


# verify -99 is not used and is valid for DefaultPrecision
static_assert(_blis.BLIS_DOUBLE_PREC != -99)
static_assert(_blis.BLIS_SINGLE_PREC != -99)


@cython.cdivision(True)
@cython.embedsignature(True)
cpdef int gemm(
    double alpha,
    bint conjugate_a,
    ndarray A,
    bint conjugate_b,
    ndarray B,
    double complex beta,
    ndarray C,
    Precision precision = Precision.DefaultPrecision,
) except -1:
    r"""Matrix multiplication of matrices, any precision and domain.

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
        precision: The precision to use in the calculation. This parameter is optional. If not
            specified, it defaults to the precision of `C`.
    """
    if np.PyArray_NDIM(A) != 2 or np.PyArray_NDIM(B) != 2 or np.PyArray_NDIM(C) != 2:
        msg = 'matrices A, B, and C must be two-dimensional'
        raise ValueError(msg)
    cdef dim_t m = np.PyArray_DIM(A, 0)
    cdef dim_t n = np.PyArray_DIM(B, 1)
    cdef dim_t k = np.PyArray_DIM(A, 1)
    if np.PyArray_DIM(B, 0) != k or np.PyArray_DIM(C, 0) != m or np.PyArray_DIM(C, 1) != n:
        msg = (
            "matrix dimensions not compatible: "
            f"({A.shape[0]}, {A.shape[1]}) @ ({B.shape[0], B.shape[1]}) = ({C.shape[0]}, {C.shape[1]})"
        )
        raise ValueError(msg)

    cdef obj_t bli_a, bli_b, bli_c, bli_alpha, bli_beta
    cdef _blis.num_t blis_type_A = <_blis.num_t> _convert_type(A)
    cdef _blis.num_t blis_type_B = <_blis.num_t> _convert_type(B)
    cdef _blis.num_t blis_type_C = <_blis.num_t> _convert_type(C)
    with nogil, cython.boundscheck(False):
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_DOUBLE,
            &alpha,
            &bli_alpha,
        )
        _blis.bli_obj_create_with_attached_buffer(
            blis_type_A,
            m,
            k,
            np.PyArray_DATA(A),
            np.PyArray_STRIDE(A, 0) / np.PyArray_ITEMSIZE(A),
            np.PyArray_STRIDE(A, 1) / np.PyArray_ITEMSIZE(A),
            &bli_a,
        )
        if conjugate_a:
            _blis.bli_obj_set_conj(_blis.BLIS_CONJUGATE, &bli_a)
        _blis.bli_obj_create_with_attached_buffer(
            blis_type_B,
            k,
            n,
            np.PyArray_DATA(B),
            np.PyArray_STRIDE(B, 0) / np.PyArray_ITEMSIZE(B),
            np.PyArray_STRIDE(B, 1) / np.PyArray_ITEMSIZE(B),
            &bli_b,
        )
        if conjugate_b:
            _blis.bli_obj_set_conj(_blis.BLIS_CONJUGATE, &bli_b)
        _blis.bli_obj_create_1x1_with_attached_buffer(
            _blis.BLIS_DCOMPLEX,
            &beta,
            &bli_beta,
        )
        _blis.bli_obj_create_with_attached_buffer(
            blis_type_C,
            m,
            n,
            np.PyArray_DATA(C),
            np.PyArray_STRIDE(C, 0) / np.PyArray_ITEMSIZE(C),
            np.PyArray_STRIDE(C, 1) / np.PyArray_ITEMSIZE(C),
            &bli_c,
        )
        if precision != Precision.DefaultPrecision:
            _blis.bli_obj_set_comp_prec(<_blis.prec_t> precision, &bli_c)

        _blis.bli_gemm(&bli_alpha, &bli_a, &bli_b, &bli_beta, &bli_c)
    return 0


@cython.embedsignature(True)
cpdef str get_int_type_size():
    """Return the integer size used by BLIS."""
    cdef const char* cstring = _blis.bli_info_get_int_type_size_str()
    cdef bytes bstring = cstring
    return bstring.decode('ascii')


@cython.embedsignature(True)
cpdef str get_version():
    """Return the version of BLIS."""
    cdef const char* cstring = _blis.bli_info_get_version_str()
    cdef bytes bstring = cstring
    return bstring.decode('ascii')


@cython.embedsignature(True)
cpdef str get_arch():
    """Return the architecture name currently used by BLIS."""
    cdef _blis.arch_t id = _blis.bli_arch_query_id()
    cdef const char* cstring = _blis.bli_arch_string(id)
    cdef bytes bstring = cstring
    return bstring.decode('ascii')


@cython.embedsignature(True)
cpdef void set_num_threads(dim_t n_threads) noexcept nogil:
    """Set the number of threads used by BLIS."""
    _blis.bli_thread_set_num_threads(n_threads)


@cython.embedsignature(True)
cpdef dim_t get_num_threads() noexcept nogil:
    """Return the number of threads currently used by BLIS."""
    return _blis.bli_thread_get_num_threads()

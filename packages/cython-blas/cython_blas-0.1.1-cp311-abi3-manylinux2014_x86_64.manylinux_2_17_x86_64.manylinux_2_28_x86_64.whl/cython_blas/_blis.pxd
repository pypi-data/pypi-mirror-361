
cdef extern from "blis.h" nogil:

    ctypedef int dim_t  # dimension type
    ctypedef int inc_t  # increment/stride type

    ctypedef enum arch_t:  # architecture ID type
        pass

    ctypedef enum trans_t:
        BLIS_NO_TRANSPOSE
        BLIS_TRANSPOSE
        BLIS_CONJ_NO_TRANSPOSE
        BLIS_CONJ_TRANSPOSE

    ctypedef enum conj_t:
        BLIS_NO_CONJUGTE
        BLIS_CONJUGATE

    ctypedef enum num_t:
        BLIS_FLOAT
        BLIS_DOUBLE
        BLIS_SCOMPLEX
        BLIS_DCOMPLEX

    ctypedef enum dom_t:
        BLIS_REAL
        BLIS_COMPLEX

    ctypedef enum prec_t:
        BLIS_SINGLE_PREC
        BLIS_DOUBLE_PREC

    ctypedef struct obj_t:  # matrix object
        pass

    const char* bli_info_get_int_type_size_str()
    const char* bli_info_get_version_str()
    arch_t bli_arch_query_id()
    const char* bli_arch_string(arch_t id)

    void bli_thread_set_num_threads(dim_t n_threads)
    dim_t bli_thread_get_num_threads()

    void bli_obj_create_with_attached_buffer(
        num_t dt,   # type
        dim_t m,    # number of rows
        dim_t n,    # number of columns
        void* p,    # buffer
        inc_t rs,   # row stride
        inc_t cs,   # column stride
        obj_t* obj  # matrix object initialized
    )

    void bli_obj_create_1x1_with_attached_buffer(
        num_t dt,    # type
        void* p,     # buffer
        obj_t* obj,  # matrix object initialized
    )

    void bli_obj_set_conj(conj_t conj, obj_t* obj)

    void bli_obj_set_comp_prec(prec_t dt, obj_t* obj)

    void bli_gemm(
        const obj_t* alpha,
        const obj_t* a,
        const obj_t* b,
        const obj_t* beta,
        obj_t* c,
    )

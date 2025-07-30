"""Tests of the openblas module."""

import itertools

import numpy as np
import pytest

from cython_blas import openblas
from cython_blas.tests.utils import conjugate_if, create_array, create_symmetric_array

_shape_error_params_gemm = (
    ("mat_a_shape", "mat_b_shape", "mat_c_shape", "match"),
    [
        ((3, 9), (4, 4), (3, 4), r"matrix dim.*not compat.*\(3, 9\).*\(4, 4\).*\(3, 4\)"),
        ((3, 4), (4, 4), (9, 4), r"matrix dim.*not compat.*\(3, 4\).*\(4, 4\).*\(9, 4\)"),
        ((3, 4), (4, 4), (3, 9), r"matrix dim.*not compat.*\(3, 4\).*\(4, 4\).*\(3, 9\)"),
    ],
)

_strided_error_params_gemm = (
    ("array", "axis", "order", "match"),
    [
        (0, 1, "C", r"matrix A must.*contiguous.*one dimension"),
        (0, 0, "F", r"matrix A must.*contiguous.*one dimension"),
        (1, 1, "C", r"matrix B must.*contiguous.*one dimension"),
        (1, 0, "F", r"matrix B must.*contiguous.*one dimension"),
        (2, 1, "C", r"matrix C must.*contiguous.*one dimension"),
        (2, 0, "F", r"matrix C must.*contiguous.*one dimension"),
    ],
)

_strided_params_gemm = (
    ("array", "axis", "order"),
    [
        (0, 0, "C"),
        (0, 1, "F"),
        (1, 0, "C"),
        (1, 1, "F"),
        (2, 0, "C"),
        (2, 1, "F"),
    ],
)

_real_params_gemm = (
    ("alpha", "beta", "m", "n", "k", "a_order", "b_order", "c_order"),
    [
        (alpha, beta, 8, 9, 10, a_order, b_order, c_order)
        for alpha, beta, a_order, b_order, c_order in itertools.product(
            [0.0, 1.0, 2.2], [0.0, 1.0, 2.2], ["C", "F"], ["C", "F"], ["C", "F"]
        )
    ],
)

_complex_params_gemm = (
    ("alpha", "conjugate_a", "beta", "conjugate_b", "m", "n", "k", "a_order", "b_order", "c_order"),
    [
        (alpha, conjugate_a, beta, conjugate_b, 8, 9, 10, a_order, b_order, c_order)
        for alpha, conjugate_a, beta, conjugate_b, a_order, b_order, c_order in itertools.product(
            [0.0 + 0.0j, 1.0 + 1.2j, 2.1 + 1.0j],
            [True, False],
            [0.0 + 0.0j, 1.0 + 1.2j, 2.1 + 1.0j],
            [True, False],
            ["C", "F"],
            ["C", "F"],
            ["C", "F"],
        )
    ],
)


@pytest.mark.parametrize(*_shape_error_params_gemm)
def test_sgemm_shape_error(
    mat_a_shape: tuple[int, int], mat_b_shape: tuple[int, int], mat_c_shape: tuple[int, int], match: str
):
    """Test the sgemm function, with incompatible matrix shapes."""
    alpha, beta = 1.0, 0.0
    mat_a = np.zeros(mat_a_shape, dtype="f4", order="C")
    mat_b = np.zeros(mat_b_shape, dtype="f4", order="C")
    mat_c = np.zeros(mat_c_shape, dtype="f4", order="C")
    with pytest.raises(ValueError, match=match):
        openblas.sgemm(alpha, mat_a, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_strided_error_params_gemm)
def test_sgemm_strided_error(array: int, axis: int, order: str, match: str):
    """Test the sgemm function, with strides along the contiguous dimension, which is an error."""
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "f4"
    mats = [np.zeros(shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    with pytest.raises(ValueError, match=match):
        openblas.sgemm(alpha, mat_a, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_real_params_gemm)
def test_sgemm(  # noqa: PLR0913
    alpha: float,
    beta: float,
    m: int,
    n: int,
    k: int,
    a_order: str,
    b_order: str,
    c_order: str,
):
    """Test the sgemm function."""
    rng = np.random.default_rng(seed=1)
    mat_a = create_array(rng, (m, k), "f4", a_order)
    mat_b = create_array(rng, (k, n), "f4", b_order)
    mat_c = create_array(rng, (m, n), "f4", c_order)
    expected = alpha * mat_a @ mat_b + beta * mat_c
    openblas.sgemm(alpha, mat_a, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=5e-7, rtol=5e-7)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_sgemm_strided(array: int, axis: int, order: str):
    """Test the sgemm function, with strides along the non-contiguous dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "f4"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    openblas.sgemm(alpha, mat_a, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=5e-7, rtol=5e-7)


@pytest.mark.parametrize(*_shape_error_params_gemm)
def test_dgemm_shape_error(
    mat_a_shape: tuple[int, int], mat_b_shape: tuple[int, int], mat_c_shape: tuple[int, int], match: str
):
    """Test the dgemm function, with incompatible matrix shapes."""
    alpha, beta = 1.0, 0.0
    mat_a = np.zeros(mat_a_shape, dtype="f8", order="C")
    mat_b = np.zeros(mat_b_shape, dtype="f8", order="C")
    mat_c = np.zeros(mat_c_shape, dtype="f8", order="C")
    with pytest.raises(ValueError, match=match):
        openblas.dgemm(alpha, mat_a, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_strided_error_params_gemm)
def test_dgemm_strided_error(array: int, axis: int, order: str, match: str):
    """Test the dgemm function, with invalid strided matrix shapes."""
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "f8"
    mats = [np.zeros(shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    with pytest.raises(ValueError, match=match):
        openblas.dgemm(alpha, mat_a, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_real_params_gemm)
def test_dgemm(  # noqa: PLR0913
    alpha: float,
    beta: float,
    m: int,
    n: int,
    k: int,
    a_order: str,
    b_order: str,
    c_order: str,
):
    """Test the dgemm function."""
    rng = np.random.default_rng(seed=1)
    mat_a = create_array(rng, (m, k), "f8", a_order)
    mat_b = create_array(rng, (k, n), "f8", b_order)
    mat_c = create_array(rng, (m, n), "f8", c_order)
    expected = alpha * mat_a @ mat_b + beta * mat_c
    openblas.dgemm(alpha, mat_a, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_dgemm_strided(array: int, axis: int, order: str):
    """Test the dgemm function, with strides along the non-contiguous dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "f8"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    openblas.dgemm(alpha, mat_a, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)


@pytest.mark.parametrize(*_shape_error_params_gemm)
def test_cgemm_shape_error(
    mat_a_shape: tuple[int, int], mat_b_shape: tuple[int, int], mat_c_shape: tuple[int, int], match: str
):
    """Test the cgemm function, with incompatible matrix shapes."""
    alpha, beta = 1.0, 0.0
    conjugate_a, conjugate_b = False, False
    mat_a = np.zeros(mat_a_shape, dtype="c8", order="C")
    mat_b = np.zeros(mat_b_shape, dtype="c8", order="C")
    mat_c = np.zeros(mat_c_shape, dtype="c8", order="C")
    with pytest.raises(ValueError, match=match):
        openblas.cgemm(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_strided_error_params_gemm)
def test_cgemm_strided_error(array: int, axis: int, order: str, match: str):
    """Test the cgemm function, with strides along the contiguous dimension, which is an error."""
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c8"
    mats = [np.zeros(shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    with pytest.raises(ValueError, match=match):
        openblas.cgemm(alpha, False, mat_a, False, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_complex_params_gemm)
def test_cgemm(  # noqa: PLR0913
    alpha: complex,
    conjugate_a: bool,
    beta: complex,
    conjugate_b: bool,
    m: int,
    n: int,
    k: int,
    a_order: str,
    b_order: str,
    c_order: str,
):
    """Test the cgemm function."""
    rng = np.random.default_rng(seed=1)
    mat_a = create_array(rng, (m, k), "c8", a_order)
    mat_b = create_array(rng, (k, n), "c8", b_order)
    mat_c = create_array(rng, (m, n), "c8", c_order)
    expected = alpha * conjugate_if(mat_a, conjugate_a) @ conjugate_if(mat_b, conjugate_b) + beta * mat_c
    openblas.cgemm(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=7e-7, rtol=7e-7)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_cgemm_strided(array: int, axis: int, order: str):
    """Test the cgemm function, with strides along the non-contiguous dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c8"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    openblas.cgemm(alpha, False, mat_a, False, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=5e-7, rtol=5e-7)


@pytest.mark.parametrize(*_shape_error_params_gemm)
def test_cgemm3m_shape_error(
    mat_a_shape: tuple[int, int], mat_b_shape: tuple[int, int], mat_c_shape: tuple[int, int], match: str
):
    """Test the cgemm3m function, with incompatible matrix shapes."""
    alpha, beta = 1.0, 0.0
    conjugate_a, conjugate_b = False, False
    mat_a = np.zeros(mat_a_shape, dtype="c8", order="C")
    mat_b = np.zeros(mat_b_shape, dtype="c8", order="C")
    mat_c = np.zeros(mat_c_shape, dtype="c8", order="C")
    with pytest.raises(ValueError, match=match):
        openblas.cgemm3m(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_strided_error_params_gemm)
def test_cgemm3m_strided_error(array: int, axis: int, order: str, match: str):
    """Test the cgemm3m function, with strides along the contiguous dimension, which is an error."""
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c8"
    mats = [np.zeros(shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    with pytest.raises(ValueError, match=match):
        openblas.cgemm3m(alpha, False, mat_a, False, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_complex_params_gemm)
def test_cgemm3m(  # noqa: PLR0913
    alpha: complex,
    conjugate_a: bool,
    beta: complex,
    conjugate_b: bool,
    m: int,
    n: int,
    k: int,
    a_order: str,
    b_order: str,
    c_order: str,
):
    """Test the cgemm function."""
    rng = np.random.default_rng(seed=1)
    mat_a = create_array(rng, (m, k), "c8", a_order)
    mat_b = create_array(rng, (k, n), "c8", b_order)
    mat_c = create_array(rng, (m, n), "c8", c_order)
    expected = alpha * conjugate_if(mat_a, conjugate_a) @ conjugate_if(mat_b, conjugate_b) + beta * mat_c
    openblas.cgemm3m(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=2e-6, rtol=7e-7)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_cgemm3m_strided(array: int, axis: int, order: str):
    """Test the cgemm3m function, with strides along the non-contiguous dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c8"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    openblas.cgemm3m(alpha, False, mat_a, False, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=5e-7, rtol=5e-7)


@pytest.mark.parametrize(*_shape_error_params_gemm)
def test_zgemm_shape_error(
    mat_a_shape: tuple[int, int], mat_b_shape: tuple[int, int], mat_c_shape: tuple[int, int], match: str
):
    """Test the zgemm function, with incompatible matrix shapes."""
    alpha, beta = 1.0, 0.0
    conjugate_a, conjugate_b = False, False
    mat_a = np.zeros(mat_a_shape, dtype="c16", order="C")
    mat_b = np.zeros(mat_b_shape, dtype="c16", order="C")
    mat_c = np.zeros(mat_c_shape, dtype="c16", order="C")
    with pytest.raises(ValueError, match=match):
        openblas.zgemm(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_strided_error_params_gemm)
def test_zgemm_strided_error(array: int, axis: int, order: str, match: str):
    """Test the zgemm function, with strides along the contiguous dimension, which is an error."""
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c16"
    mats = [np.zeros(shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    with pytest.raises(ValueError, match=match):
        openblas.zgemm(alpha, False, mat_a, False, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_complex_params_gemm)
def test_zgemm(  # noqa: PLR0913
    alpha: complex,
    conjugate_a: bool,
    beta: complex,
    conjugate_b: bool,
    m: int,
    n: int,
    k: int,
    a_order: str,
    b_order: str,
    c_order: str,
):
    """Test the zgemm function."""
    rng = np.random.default_rng(seed=1)
    mat_a = create_array(rng, (m, k), "c16", a_order)
    mat_b = create_array(rng, (k, n), "c16", b_order)
    mat_c = create_array(rng, (m, n), "c16", c_order)
    expected = alpha * conjugate_if(mat_a, conjugate_a) @ conjugate_if(mat_b, conjugate_b) + beta * mat_c
    openblas.zgemm(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_zgemm_strided(array: int, axis: int, order: str):
    """Test the zgemm function, with strides along the non-contiguous dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c16"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    openblas.zgemm(alpha, False, mat_a, False, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)


@pytest.mark.parametrize(*_shape_error_params_gemm)
def test_zgemm3m_shape_error(
    mat_a_shape: tuple[int, int], mat_b_shape: tuple[int, int], mat_c_shape: tuple[int, int], match: str
):
    """Test the zgemm3m function, with incompatible matrix shapes."""
    alpha, beta = 1.0, 0.0
    conjugate_a, conjugate_b = False, False
    mat_a = np.zeros(mat_a_shape, dtype="c16", order="C")
    mat_b = np.zeros(mat_b_shape, dtype="c16", order="C")
    mat_c = np.zeros(mat_c_shape, dtype="c16", order="C")
    with pytest.raises(ValueError, match=match):
        openblas.zgemm3m(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_strided_error_params_gemm)
def test_zgemm3m_strided_error(array: int, axis: int, order: str, match: str):
    """Test the zgemm3m function, with strides along the contiguous dimension, which is an error."""
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c16"
    mats = [np.zeros(shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    with pytest.raises(ValueError, match=match):
        openblas.zgemm3m(alpha, False, mat_a, False, mat_b, beta, mat_c)


@pytest.mark.parametrize(*_complex_params_gemm)
def test_zgemm3m(  # noqa: PLR0913
    alpha: complex,
    conjugate_a: bool,
    beta: complex,
    conjugate_b: bool,
    m: int,
    n: int,
    k: int,
    a_order: str,
    b_order: str,
    c_order: str,
):
    """Test the zgemm3m function."""
    rng = np.random.default_rng(seed=1)
    mat_a = create_array(rng, (m, k), "c16", a_order)
    mat_b = create_array(rng, (k, n), "c16", b_order)
    mat_c = create_array(rng, (m, n), "c16", c_order)
    expected = alpha * conjugate_if(mat_a, conjugate_a) @ conjugate_if(mat_b, conjugate_b) + beta * mat_c
    openblas.zgemm3m(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_zgemm3m_strided(array: int, axis: int, order: str):
    """Test the zgemm function, with strides along the non-contiguous dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c16"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    openblas.zgemm3m(alpha, False, mat_a, False, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)


_real_params_symm = (
    ("alpha", "beta", "upper", "m", "n", "a_order", "bc_order"),
    [
        (alpha, beta, upper, 8, 9, a_order, bc_order)
        for alpha, beta, upper, a_order, bc_order in itertools.product(
            [0.0, 1.0, 2.2], [0.0, 1.0, 2.2], [True, False], ["C", "F"], ["C", "F"]
        )
    ],
)


@pytest.mark.parametrize(*_real_params_symm)
def test_dsymm_ab(  # noqa: PLR0913
    alpha: float,
    beta: float,
    upper: bool,
    m: int,
    n: int,
    a_order: str,
    bc_order: str,
):
    """Test the dsymm_ab function."""
    rng = np.random.default_rng(seed=1)
    upper_lower = openblas.UpperLower.Upper if upper else openblas.UpperLower.Lower
    mat_a, mat_a_full = create_symmetric_array(rng, upper, m, "f8", a_order)
    assert np.any(np.isnan(mat_a))
    mat_b = create_array(rng, (m, n), "f8", bc_order)
    mat_c = create_array(rng, (m, n), "f8", bc_order)
    expected = alpha * mat_a_full @ mat_b + beta * mat_c
    assert not np.any(np.isnan(mat_c))
    openblas.dsymm_ab(alpha, upper_lower, mat_a, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)

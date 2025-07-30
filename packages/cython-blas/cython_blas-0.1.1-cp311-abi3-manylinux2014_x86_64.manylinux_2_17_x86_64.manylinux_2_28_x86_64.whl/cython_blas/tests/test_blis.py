"""Tests of the blis module."""

import itertools

import numpy as np
import pytest

from cython_blas import blis
from cython_blas.tests.utils import conjugate_if, create_array

_shape_error_params_gemm = (
    ("mat_a_shape", "mat_b_shape", "mat_c_shape", "match"),
    [
        ((3, 9), (4, 4), (3, 4), r"matrix dim.*not compat.*\(3, 9\).*\(4, 4\).*\(3, 4\)"),
        ((3, 4), (4, 4), (9, 4), r"matrix dim.*not compat.*\(3, 4\).*\(4, 4\).*\(9, 4\)"),
        ((3, 4), (4, 4), (3, 9), r"matrix dim.*not compat.*\(3, 4\).*\(4, 4\).*\(3, 9\)"),
    ],
)

_strided_params_gemm = (
    ("array", "axis", "order"),
    [
        (0, 0, "C"),
        (0, 0, "F"),
        (0, 1, "C"),
        (0, 1, "F"),
        (1, 0, "C"),
        (1, 0, "F"),
        (1, 1, "C"),
        (1, 1, "F"),
        (2, 0, "C"),
        (2, 0, "F"),
        (2, 1, "C"),
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
        blis.sgemm(alpha, mat_a, mat_b, beta, mat_c)


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
    """Test the dgemm function."""
    rng = np.random.default_rng(seed=1)
    mat_a = create_array(rng, (m, k), "f4", a_order)
    mat_b = create_array(rng, (k, n), "f4", b_order)
    mat_c = create_array(rng, (m, n), "f4", c_order)
    expected = alpha * mat_a @ mat_b + beta * mat_c
    blis.sgemm(alpha, mat_a, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=5e-7, rtol=5e-7)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_sgemm_strided(array: int, axis: int, order: str):
    """Test the sgemm function, with strides along one dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "f4"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    blis.sgemm(alpha, mat_a, mat_b, beta, mat_c)
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
        blis.dgemm(alpha, mat_a, mat_b, beta, mat_c)


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
    blis.dgemm(alpha, mat_a, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_dgemm_strided(array: int, axis: int, order: str):
    """Test the dgemm function, with strides along one dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "f8"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    blis.dgemm(alpha, mat_a, mat_b, beta, mat_c)
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
        blis.cgemm(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)


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
    blis.cgemm(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=5e-7, rtol=5e-7)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_cgemm_strided(array: int, axis: int, order: str):
    """Test the cgemm function, with strides along one dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c8"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    blis.cgemm(alpha, False, mat_a, False, mat_b, beta, mat_c)
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
        blis.zgemm(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)


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
    blis.zgemm(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_zgemm_strided(array: int, axis: int, order: str):
    """Test the zgemm function, with strides along one dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "c16"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    blis.zgemm(alpha, False, mat_a, False, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)


@pytest.mark.parametrize(
    ("mat_a_shape", "mat_b_shape", "mat_c_shape", "match"),
    [
        ((3, 4, 1), (4, 4), (3, 4), r"matrices A, B, and C must.*two\-dimensional"),
        ((3, 4), (4, 4, 1), (3, 4), r"matrices A, B, and C must.*two\-dimensional"),
        ((3, 4), (4, 4), (3, 4, 1), r"matrices A, B, and C must.*two\-dimensional"),
        ((3, 9), (4, 4), (3, 4), r"matrix dim.*not compat.*\(3, 9\).*\(4, 4\).*\(3, 4\)"),
        ((3, 4), (4, 4), (9, 4), r"matrix dim.*not compat.*\(3, 4\).*\(4, 4\).*\(9, 4\)"),
        ((3, 4), (4, 4), (3, 9), r"matrix dim.*not compat.*\(3, 4\).*\(4, 4\).*\(3, 9\)"),
    ],
)
def test_gemm_shape_error(
    mat_a_shape: tuple[int, int], mat_b_shape: tuple[int, int], mat_c_shape: tuple[int, int], match: str
):
    """Test the dgemm function, with incompatible matrix shapes."""
    alpha, beta = 1.0, 0.0
    mat_a = np.zeros(mat_a_shape, dtype="f8", order="C")
    mat_b = np.zeros(mat_b_shape, dtype="f8", order="C")
    mat_c = np.zeros(mat_c_shape, dtype="f8", order="C")
    with pytest.raises(ValueError, match=match):
        blis.gemm(alpha, False, mat_a, False, mat_b, beta, mat_c)


@pytest.mark.parametrize(
    (
        "alpha",
        "conjugate_a",
        "beta",
        "conjugate_b",
        "m",
        "n",
        "k",
        "a_dtype",
        "b_dtype",
        "c_dtype",
        "precision",
    ),
    [
        (alpha, conjugate_a, beta, conjugate_b, 8, 9, 10, a_dtype, b_dtype, c_dtype, precision)
        for (
            alpha,
            conjugate_a,
            beta,
            conjugate_b,
            a_dtype,
            b_dtype,
            c_dtype,
            precision,
        ) in itertools.product(
            [0.0, 1.2],
            [True, False],
            [0.0 + 0.0j, 1.2 + 1.3j],
            [True, False],
            ["f4", "f8", "c8", "c16"],
            ["f4", "f8", "c8", "c16"],
            ["f4", "f8", "c8", "c16"],
            [blis.Precision.DefaultPrecision, blis.Precision.DoublePrecision, blis.Precision.SinglePrecision],
        )
    ],
)
def test_gemm(  # noqa: PLR0913
    alpha: float,
    conjugate_a: bool,
    beta: complex,
    conjugate_b: bool,
    m: int,
    n: int,
    k: int,
    a_dtype: str,
    b_dtype: str,
    c_dtype: str,
    precision: blis.Precision,
):
    """Test the gemm function."""
    rng = np.random.default_rng(seed=1)
    a_order, b_order, c_order = "F", "F", "C"
    mat_a = create_array(rng, (m, k), a_dtype, a_order)
    mat_b = create_array(rng, (k, n), b_dtype, b_order)
    mat_c = create_array(rng, (m, n), c_dtype, c_order)
    expected = alpha * conjugate_if(mat_a, conjugate_a) @ conjugate_if(mat_b, conjugate_b) + beta * mat_c
    expected = expected.real if c_dtype in ("f4", "f8") else expected
    blis.gemm(alpha, conjugate_a, mat_a, conjugate_b, mat_b, beta, mat_c, precision)
    atol = 5e-6 if c_dtype in ("f4", "c8") else 1e-6
    rtol = 5e-6 if c_dtype in ("f4", "c8") else 1e-6
    np.testing.assert_allclose(mat_c, expected, atol=atol, rtol=rtol)


@pytest.mark.parametrize(*_strided_params_gemm)
def test_gemm_strided(array: int, axis: int, order: str):
    """Test the gemm function, with strides along one dimension."""
    rng = np.random.default_rng(seed=1)
    shapes = [[6, 8], [8, 10], [6, 10]]
    shapes[array][axis] *= 2
    dtype = "f8"
    mats = [create_array(rng, shape, dtype, order) for shape in shapes]
    mats[array] = mats[array][::2, :] if axis == 0 else mats[array][:, ::2]
    alpha, beta = 1.0, 0.0
    mat_a, mat_b, mat_c = mats
    expected = alpha * mat_a @ mat_b + beta * mat_c
    blis.gemm(alpha, False, mat_a, False, mat_b, beta, mat_c)
    np.testing.assert_allclose(mat_c, expected, atol=1e-8, rtol=1e-8)

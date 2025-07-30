"""Tests of the optimize module."""

import re

import numpy as np
import pytest

from cython_blas import optimize
from cython_blas.optimize import Matrix, MultiMatrix

np_einsum_regex = re.compile(r"Optimized FLOP count:[ ]*([\d\.e\-\+]+)\s", re.IGNORECASE)


def parse_optimized_flop_count(string: str) -> int:
    """Parse the optimized FLOP count from np.einsum_path."""
    match = np_einsum_regex.search(string)
    return int(float(match.group(1)))


@pytest.mark.parametrize(
    ("shape", "kind", "itemsize"),
    [
        ((2, 2), "f", 4),
        ((3, 4), "f", 8),
        ((4, 3), "c", 16),
    ],
)
def test_matrix_create_instance(shape: tuple[int, int], kind: str, itemsize: int):
    """Test the Matrix class."""
    matrix = optimize.Matrix(shape, kind, itemsize)
    assert isinstance(matrix, optimize.Matrix)
    assert matrix.shape == shape
    assert matrix.kind == kind
    assert matrix.multiplier == itemsize // 4


@pytest.mark.parametrize(
    ("matrix1", "matrix2", "kind", "itemsize", "expected_weight", "expected_mat"),
    [
        (Matrix((2, 3), "f", 4), Matrix((3, 5), "f", 4), "f", 4, 1 * 2 * (2 * 3 * 5), Matrix((2, 5), "f", 4)),
        (Matrix((2, 3), "c", 4), Matrix((3, 5), "f", 4), "f", 4, 1 * 2 * (2 * 3 * 5), Matrix((2, 5), "f", 4)),
        (Matrix((2, 3), "f", 4), Matrix((3, 5), "c", 4), "f", 4, 1 * 2 * (2 * 3 * 5), Matrix((2, 5), "f", 4)),
        (Matrix((2, 3), "c", 4), Matrix((3, 5), "c", 4), "f", 4, 1 * 4 * (2 * 3 * 5), Matrix((2, 5), "f", 4)),
        (Matrix((2, 3), "c", 4), Matrix((3, 5), "c", 4), "c", 4, 1 * 8 * (2 * 3 * 5), Matrix((2, 5), "c", 4)),
        (Matrix((2, 3), "c", 8), Matrix((3, 5), "c", 4), "c", 4, 1 * 8 * (2 * 3 * 5), Matrix((2, 5), "c", 4)),
        (Matrix((2, 3), "c", 8), Matrix((3, 5), "c", 4), "c", 8, 2 * 8 * (2 * 3 * 5), Matrix((2, 5), "c", 8)),
        (Matrix((2, 3), "f", 4), Matrix((3, 5), "f", 4), "f", 8, 2 * 2 * (2 * 3 * 5), Matrix((2, 5), "f", 8)),
        (Matrix((2, 3), "c", 8), Matrix((3, 5), "c", 8), "c", 8, 2 * 8 * (2 * 3 * 5), Matrix((2, 5), "c", 8)),
    ],
)
def test_matrix_calc_weight(  # noqa: PLR0913
    matrix1: Matrix, matrix2: Matrix, kind: str, itemsize: int, expected_weight: int, expected_mat: Matrix
):
    """Test the Matrix class, calc_weight method."""
    weight, matrix = matrix1.calc_weight(matrix2, kind, itemsize)
    assert isinstance(weight, int)
    assert weight == expected_weight
    assert isinstance(matrix, Matrix)
    assert matrix == expected_mat


@pytest.mark.parametrize(
    ("mats", "expected_n_mats"),
    [
        ([Matrix((2, 2), "f", 4), Matrix((3, 2), "f", 4)], 2),
    ],
)
def test_multimatrix_create_instance(mats: list[Matrix], expected_n_mats: int):
    """Test the MultiMatrix class."""
    multi_matrix = MultiMatrix(mats)
    assert isinstance(multi_matrix, MultiMatrix)
    assert multi_matrix.n_mats == expected_n_mats


@pytest.mark.parametrize(
    ("mats1", "mats2", "kind", "itemsize", "expected_weight", "expected_mats"),
    [
        (
            [Matrix((2, 2), "f", 4), Matrix((3, 4), "f", 4)],
            [Matrix((2, 6), "f", 4), Matrix((4, 12), "f", 4)],
            "f",
            4,
            1 * 2 * (2 * 2 * 6) + 1 * 2 * (3 * 4 * 12),
            [Matrix((2, 6), "f", 4), Matrix((3, 12), "f", 4)],
        ),
        (
            [Matrix((2, 2), "f", 4), Matrix((3, 4), "f", 4)],
            [Matrix((2, 6), "f", 4), Matrix((4, 12), "f", 4)],
            "f",
            8,
            2 * 2 * (2 * 2 * 6) + 2 * 2 * (3 * 4 * 12),
            [Matrix((2, 6), "f", 8), Matrix((3, 12), "f", 8)],
        ),
        (
            [Matrix((2, 2), "f", 4), Matrix((3, 4), "f", 4)],
            [Matrix((2, 6), "c", 4), Matrix((4, 12), "c", 4)],
            "c",
            8,
            2 * 4 * (2 * 2 * 6) + 2 * 4 * (3 * 4 * 12),
            [Matrix((2, 6), "c", 8), Matrix((3, 12), "c", 8)],
        ),
        (
            [Matrix((2, 2), "c", 4), Matrix((3, 4), "c", 4)],
            [Matrix((2, 6), "c", 4), Matrix((4, 12), "c", 4)],
            "c",
            8,
            2 * 8 * (2 * 2 * 6) + 2 * 8 * (3 * 4 * 12),
            [Matrix((2, 6), "c", 8), Matrix((3, 12), "c", 8)],
        ),
    ],
)
def test_multimatrix_calc_weight(  # noqa: PLR0913
    mats1: list[Matrix],
    mats2: list[Matrix],
    kind: str,
    itemsize: int,
    expected_weight: int,
    expected_mats: list[Matrix],
):
    """Test the MultiMatrix class, calc_weight method."""
    weight, multi_matrix = MultiMatrix(mats1).calc_weight(MultiMatrix(mats2), kind, itemsize)
    assert isinstance(weight, int)
    assert weight == expected_weight
    assert isinstance(multi_matrix, MultiMatrix)
    assert multi_matrix.n_mats == len(expected_mats)
    for mat, expected_mat in zip(multi_matrix.mats, expected_mats, strict=False):
        assert mat == expected_mat


@pytest.mark.parametrize(
    "shapes",
    [
        # ((10, 15), (15, 12), (12, 16)),  # noqa: ERA001
        # ((10, 15), (15, 12), (12, 5), (5, 16)),  # noqa: ERA001
        # ((10, 15), (15, 22), (22, 5), (5, 16)),  # noqa: ERA001
    ],
)
def test_optimize_compare_to_einsum(shapes: tuple):
    """Test the optimize function."""
    mats = [optimize.Matrix(shape, "f", 4) for shape in shapes]
    best_path = optimize.optimize(mats)
    expression = ",".join([f"{chr(97 + i)}{chr(97 + i + 1)}" for i in range(len(shapes))])
    (_, *es_path), es_descr = np.einsum_path(expression, *(np.empty(shape) for shape in shapes), optimize="optimal")
    es_flop_count = parse_optimized_flop_count(es_descr)
    assert best_path[1] == es_flop_count - 1
    print(best_path[1])

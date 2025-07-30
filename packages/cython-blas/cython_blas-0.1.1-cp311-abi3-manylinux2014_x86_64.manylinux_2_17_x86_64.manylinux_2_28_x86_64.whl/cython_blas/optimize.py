"""Optimize matrix multiplication."""

import itertools
from typing import TypeVar

Matrix = TypeVar("Matrix", bound="Matrix")
MultiMatrix = TypeVar("MultiMatrix", bound="MultiMatrix")


kind_to_weight = {
    ("f", "f", "f"): 2,
    ("f", "f", "c"): 2,
    ("f", "c", "f"): 2,
    ("f", "c", "c"): 4,
    ("c", "f", "f"): 2,
    ("c", "f", "c"): 4,
    ("c", "c", "f"): 4,
    ("c", "c", "c"): 8,
}


class Matrix:  # noqa: PLW1641
    """Matrix class."""

    def __init__(self, shape: tuple[int, int], kind: str, itemsize: int) -> None:
        """Initialize the class."""
        self.shape = shape
        self.kind = kind
        self.multiplier = itemsize // 4

    def __eq__(self, other: Matrix) -> bool:
        """Check equality."""
        if self.shape != other.shape:
            return False
        if self.kind != other.kind:
            return False
        return self.multiplier == other.multiplier

    def calc_weight(
        self, other: Matrix | MultiMatrix, output_kind: str, output_itemsize: int
    ) -> tuple[int, Matrix | MultiMatrix]:
        """Calculate the weight due to multiplying two matrices."""
        if isinstance(other, MultiMatrix):
            return other.calc_weight_left(self)
        mult = output_itemsize // 4 * kind_to_weight[(output_kind, self.kind, other.kind)]
        m, k = self.shape
        k2, n = other.shape
        if k != k2:
            raise ValueError
        weight = mult * m * k * n
        return weight, Matrix((m, n), output_kind, output_itemsize)


class MultiMatrix:
    """MultiMatrix class."""

    def __init__(self, mats: list[Matrix]) -> None:
        """Initialize the class."""
        self.mats = mats

    @property
    def n_mats(self) -> int:
        """Return the number of matrices."""
        return len(self.mats)

    def _calc_weight_multimatrix(
        self, other: MultiMatrix, output_kind: str, output_itemsize: int
    ) -> tuple[int, MultiMatrix]:
        """Calculate the weight when multiplying two MultiMatrix instances."""
        weight = 0
        mats = []
        for mat1, mat2 in zip(self.mats, other.mats, strict=True):
            weight_i, mats_i = mat1.calc_weight(mat2, output_kind, output_itemsize)
            weight += weight_i
            mats.append(mats_i)
        return weight, MultiMatrix(mats)

    def calc_weight_left(self, other: Matrix, output_kind: str, output_itemsize: int) -> tuple[int, MultiMatrix]:
        """Calculate the weight for other @ self."""
        weight = 0
        mats = []
        for mat2 in self.mats:
            weight_i, mats_i = other.calc_weight(mat2, output_kind, output_itemsize)
            weight += weight_i
            mats.append(mats_i)
        return weight, MultiMatrix(mats)

    def calc_weight(
        self, other: Matrix | MultiMatrix, output_kind: str, output_itemsize: int
    ) -> tuple[int, Matrix | MultiMatrix]:
        """Calculate the weight for self @ other."""
        if isinstance(other, MultiMatrix):
            return self._calc_weight_multimatrix(other, output_kind, output_itemsize)
        weight = 0
        mats = []
        for mat1 in self.mats:
            weight_i, mats_i = mat1.calc_weight(other, output_kind, output_itemsize)
            weight += weight_i
            mats.append(mats_i)
        return weight, MultiMatrix(mats)


def optimize(mats: list[Matrix]) -> tuple[int, int, tuple[int]]:
    """Optimize the order of matrix multiplication."""
    n_mats = len(mats)
    paths = itertools.product(*(range(i) for i in range(n_mats - 1, 0, -1)))
    best_path = (-1, 2**63, ())
    for i, path in enumerate(paths):
        weight = 0
        mats_i = list(mats)
        for pair in path:
            weight_i, remaining = mats_i[pair].calc_weight(mats_i[pair + 1])
            weight += weight_i
            mats_i = [*mats_i[:pair], remaining, *mats_i[pair + 2 :]]
        if weight < best_path[1]:
            best_path = (i, weight, path)
    return best_path

from math import isclose, pi

import pytest

from ki_util.geometry import Circle


def test_circle():
    D = 0.5
    assert isclose(0.25 * pi * D * D, Circle(D).area, rel_tol=1e-9)
    assert isclose(0.25 * pi * D * D, Circle(R=0.5 * D).area, rel_tol=1e-9)


if __name__ == "__main__":
    pytest.main([__file__])

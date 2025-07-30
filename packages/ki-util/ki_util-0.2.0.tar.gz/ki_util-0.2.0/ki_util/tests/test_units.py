from math import isclose

import pytest

from ki_util.units import BaseQuantity, convert_units


def test_convert():
    assert isclose(convert_units(14.6959, "psi", "pascal"), 101325, rel_tol=1e-5)
    assert isclose(convert_units(1, "klbm/hr", "kg/s"), 0.125998, rel_tol=1e-5)


def test_BaseQuantity():
    bq1 = BaseQuantity(1, "degR")
    assert isclose(bq1.magnitude, 5 / 9, rel_tol=1e-8)

    bq2 = 1 / bq1
    bq3 = BaseQuantity(9 / 5, "1/K")
    assert isclose(bq2.magnitude, bq3.magnitude, rel_tol=1e-8)
    assert bq2.units == bq3.units

    assert isclose(bq1.to("K"), 5 / 9, rel_tol=1e-8)


def test_gauge_ureg():
    assert isclose(BaseQuantity(14.6959, "psia").to("Pa"), 101325, rel_tol=1e-5)
    assert isclose(BaseQuantity(1, "bar").to("Pa"), 100000, rel_tol=1e-5)
    assert isclose(BaseQuantity(0, "barg").to("kPa"), 101.325, rel_tol=1e-5)
    assert isclose(BaseQuantity(0, "barg").to("psig"), 0.0, rel_tol=1e-5)
    assert isclose(BaseQuantity(200, "kPag").to("bara"), 3.01325, rel_tol=1e-5)


def test_BQ_arithmetic():
    h1 = BaseQuantity(10, "GJ/kg")
    h2 = BaseQuantity(convert_units(10, "GJ/kg", "MBtu/lbm"), "MBtu/lbm")
    h3 = h1 + h2
    assert isclose(h3.magnitude, 20e9, rel_tol=1e-6)
    h4 = 2.0 * h1
    assert isclose(h4.magnitude, 20e9, rel_tol=1e-6)
    h5 = h1 * 2.0
    assert isclose(h5.magnitude, 20e9, rel_tol=1e-6)
    h5 = h1 * 2.0
    assert isclose(h5.magnitude, 20e9, rel_tol=1e-6)
    h6 = h1 / 2.0
    assert isclose(h6.magnitude, 5e9, rel_tol=1e-6)
    d = BaseQuantity(2, "m")
    a = d**3
    assert isclose(a.magnitude, 8, rel_tol=1e-6)
    g = BaseQuantity(2, "")
    assert isclose(4**g, 16, rel_tol=1e-6)
    assert isclose((d**g).magnitude, 4, rel_tol=1e-6)


def test_BQ_check_units():
    h1 = BaseQuantity(10, "GJ/Mg")
    md1 = BaseQuantity(1, "klbm/hr")
    p1 = md1 * h1
    assert p1.check_units("power")


if __name__ == "__main__":
    pytest.main([__file__])

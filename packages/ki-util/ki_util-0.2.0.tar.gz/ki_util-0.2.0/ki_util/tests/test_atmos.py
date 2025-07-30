import pytest

from ki_util.atmos import atmospheric_pressure


def test_p_at_h():
    h_to_p = {305: 97700, 610: 94200, 914: 90800, 1524: 84300}  # from engineeringtoolbox.com
    for h, p in h_to_p.items():
        assert abs(atmospheric_pressure(h) - p) < 300  # 300 Pa tolerance (0.04 psi)


if __name__ == "__main__":
    pytest.main([__file__])

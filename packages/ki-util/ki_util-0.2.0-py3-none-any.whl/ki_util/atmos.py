from math import exp

from ki_util.constants import R
from ki_util.constants import g0__m_s2 as g
from ki_util.constants import p_atm__Pa as atm


def atmospheric_pressure(h__m: float):
    """
    Calculate atmospheric pressure at a given altitude using barometric formula.

    Args:
        h__m (float): Altitude in meters.

    Returns:
        float: Atmospheric pressure at the given altitude in Pascals.
    """
    M_air = 0.0289644  # molar mass of dry air [kg/mol]
    T = atmospheric_temperature(h__m)
    p = atm * exp(-g * M_air * h__m / (R * T))
    return p


def atmospheric_temperature(h__m: float):
    """
    Calculate atmospheric temperature at a given altitude within the troposphere.

    Args:
        h__m (float): Altitude in meters.

    Returns:
        float: Atmospheric temperature at the given altitude in Kelvin.
    """
    assert h__m < 12000, "Altitude exceeds troposphere range"
    T0 = 288.15  # standard temperature at sea level [K]
    L = 0.0065  # temperature lapse rate in Troposphere [K/m ]
    T = T0 - L * h__m
    return T

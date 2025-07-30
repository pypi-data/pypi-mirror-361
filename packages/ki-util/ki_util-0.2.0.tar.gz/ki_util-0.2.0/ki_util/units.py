from warnings import warn

from numpy import ndarray
from pint import UnitRegistry
from pint import errors as pint_errors

from ki_util.constants import p_atm__Pa

UNITLESS = ["dimensionless", "unitless", "ratio", "-", ""]

# Initialize the unit registry
ureg = UnitRegistry()

ureg.define("lbm = lb")
ureg.define("MMBtu = 1e6 * BTU")
ureg.define("MMBTU = 1e6 * BTU")
ureg.define("cf = cubic_feet")
ureg.define("ccf = 100 * cubic_feet")

PRESSURE_UNITS = ["bar", "psi", "kpsi", "Pa", "kPa", "MPa"]
# pressures that we want to be able to specify as gauge or absolute by appending 'g' or 'a'
for p_u in PRESSURE_UNITS:
    p_atm__Pa = ureg.Quantity(p_atm__Pa, "pascal")
    ureg.define(f"{p_u}g = {p_u}; offset: {p_atm__Pa.to(p_u).magnitude}")
    ureg.define(f"{p_u}a = {p_u}")


def convert_units(value: float | list[float] | tuple[float, ...] | ndarray, in_unit: str, to_unit: str):
    """Convert a value or array of values from one unit to another, using pint.

    Args:
        value (float | list[float] | ArrayLike[float]): The value(s) to convert.
        in_unit (str): The unit of the input value(s).
        to_unit (str): The unit to convert to.

    Returns:
    Converted value(s) in the desired unit.
    """
    if in_unit in UNITLESS:
        if to_unit not in UNITLESS:
            warn(f"Desired output units of '{to_unit}' not possible with unitless input unit '{in_unit}'")
        return value
    else:
        try:
            # Create a quantity for the input value(s)
            quantity = ureg.Quantity(value, in_unit)

            # Convert to the desired unit
            converted_quantity = quantity.to(to_unit)

            # if the input was a single value, return it as a float
            if isinstance(value, (float, int)) or isinstance(value, ndarray):
                return converted_quantity.magnitude

            # if the input was a list, return as the same type
            elif isinstance(value, list):
                return [float(v.magnitude) for v in converted_quantity]

            # if the input was a tuple, return as the same type
            elif isinstance(value, tuple):
                return tuple(float(v.magnitude) for v in converted_quantity)

        except pint_errors.DimensionalityError as e:
            print(f"Error: {e}")
            return None


def convert_to_base(value: float, in_unit: str):
    """Convert a value to base units.

    Args:
        value (float): The value to convert.
        in_unit (str): The unit of the input value.

    Returns:
        float: The value in base units.
    """
    return value if in_unit in UNITLESS else ureg.Quantity(value, in_unit).to_base_units().magnitude


def convert_dict_to_base(dict_in: dict):
    """Convert all values in a dictionary to base units. Keys must contain input units, preceeded by '__'

    Args:
        dict_in (dict): Dictionary to convert.

    Returns:
        dict: Dictionary with all values converted to base units.
    """
    dict_out = {}
    for key, value in dict_in.items():
        if isinstance(value, dict):
            dict_out[key] = convert_dict_to_base(value)
        elif "__" in key:
            base_key, in_unit = key.split("__")
            base_value = ureg.Quantity(value, in_unit).to_base_units()
            dict_out[base_key] = base_value
        else:
            dict_out[key] = value
    return dict_out


class BaseQuantity:
    """Lightweight class to store values in base units."""

    def __init__(self, value: float, unit: str):
        _qty = ureg.Quantity(value, unit).to_base_units()
        self.magnitude = _qty.magnitude
        self.units = _qty.units
        self.u_in = unit

    @property
    def m(self):
        return self.magnitude

    @property
    def isUnitless(self):
        """Check if the quantity is dimensionless."""
        return str(self.units) in UNITLESS

    def check_units(self, property_name: str) -> bool:
        """Check if the units for the input property are consistent with the property type.

        Args:
            property_name (str): The name of the property (e.g., 'pressure', 'temperature').
            value_with_units (str): The value with units (e.g., '101325 Pa', '300 K').

        Returns:
            bool: True if the units are consistent with the property type, False otherwise.
        """
        try:
            quantity = ureg.Quantity(self.magnitude, self.units)
        except pint_errors.UndefinedUnitError:
            return False

        if property_name == "pressure":
            return quantity.check("[pressure]")
        elif property_name == "temperature":
            return quantity.check("[temperature]")
        elif property_name == "mass":
            return quantity.check("[mass]")
        elif property_name == "volume":
            return quantity.check("[length] ** 3")
        elif property_name in ["radius", "diameter", "length", "height"]:
            return quantity.check("[length]")
        elif property_name == "velocity":
            return quantity.check("[length] / [time]")
        elif property_name == "mdot":
            return quantity.check("[mass] / [time]")
        elif property_name == "vdot":
            return quantity.check("[length] ** 3 / [time]")
        elif property_name == "density":
            return quantity.check("[mass] / [length] ** 3")
        elif property_name == "specific_enthalpy":
            return quantity.check("[energy] / [mass]")
        elif property_name == "specific_internal_energy":
            return quantity.check("[energy] / [mass]")
        elif property_name == "specific_entropy":
            return quantity.check("[energy] / [mass] / [temperature]")
        elif property_name == "quality":
            return quantity.dimensionless
        elif property_name == "power":
            return quantity.check("[energy] / [time]")
        else:
            return False

    def to(self, unit: str):
        """Convert the quantity to a different unit, returning a magnitude.

        Args:
            unit (str): The unit to convert to.

        Returns:
            magnitude: The magnitude in the target units.
        """
        converted = ureg.Quantity(self.magnitude, self.units).to(unit)
        return converted.magnitude

    def __add__(self, other):
        if isinstance(other, BaseQuantity):
            if self.units != other.units:
                raise ValueError(f"Cannot add quantities with different units: {self.units} and {other.units}")
            return BaseQuantity(self.magnitude + other.magnitude, str(self.units))
        else:
            raise TypeError("Addition is only supported between BaseQuantity instances.")

    def __sub__(self, other):
        if isinstance(other, BaseQuantity):
            if self.units != other.units:
                raise ValueError(f"Cannot subtract quantities with different units: {self.units} and {other.units}")
            return BaseQuantity(self.magnitude - other.magnitude, str(self.units))
        else:
            raise TypeError("Subtraction is only supported between BaseQuantity instances.")

    def __mul__(self, other):
        if isinstance(other, (int, float)):
            return BaseQuantity(self.magnitude * other, str(self.units))
        elif isinstance(other, BaseQuantity):
            result = ureg.Quantity(self.magnitude, self.units) * ureg.Quantity(other.magnitude, other.units)
            return BaseQuantity(result.magnitude, str(result.units))
        else:
            raise TypeError("Multiplication is only supported with a number or another BaseQuantity.")

    def __rmul__(self, other):
        """Handle scalar * BaseQuantity."""
        return self.__mul__(other)

    def __truediv__(self, other):
        if isinstance(other, (int, float)):
            return BaseQuantity(self.magnitude / other, str(self.units))
        elif isinstance(other, BaseQuantity):
            result = ureg.Quantity(self.magnitude, self.units) / ureg.Quantity(other.magnitude, other.units)
            return BaseQuantity(result.magnitude, str(result.units))
        else:
            raise TypeError("Division is only supported with a number or another BaseQuantity.")

    def __rtruediv__(self, other):
        """Handle scalar / BaseQuantity."""
        if isinstance(other, (int, float)):
            result = ureg.Quantity(other) / ureg.Quantity(self.magnitude, self.units)
            return BaseQuantity(result.magnitude, str(result.units))
        else:
            raise TypeError("Division is only supported with a number or another BaseQuantity.")

    def __pow__(self, exponent):
        if isinstance(exponent, (int, float)):
            result = ureg.Quantity(self.magnitude, self.units) ** exponent
            return BaseQuantity(result.magnitude, str(result.units))
        elif isinstance(exponent, BaseQuantity):
            if not exponent.isUnitless:
                raise ValueError("Exponent must be dimensionless")
            result = ureg.Quantity(self.magnitude, self.units) ** exponent.magnitude
            return BaseQuantity(result.magnitude, str(result.units))
        else:
            raise TypeError("Exponent must be a number or a dimensionless BaseQuantity.")

    def __rpow__(self, base):
        """Handles (base ** BaseQuantity)"""
        if not self.isUnitless:
            raise TypeError("Exponent must be dimesionless.")

        if isinstance(base, (int, float)) or isinstance(base, BaseQuantity):
            return base**self.magnitude
        else:
            raise TypeError("Base must be a number or BaseQuantity.")

    def __repr__(self):
        return f"BaseQuantity({self.magnitude}, '{self.units}')"

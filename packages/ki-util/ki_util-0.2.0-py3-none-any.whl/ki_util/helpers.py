import numpy as np
import pandas as pd
from datetime import datetime as dt
import operator
import warnings
import os


def get_date_as_int():
    """Returns the current date as an integer in the format YYYYMMDD."""
    return int(dt.now().strftime("%Y%m%d"))


def get_datetime_string():
    """
    This will output the current date and time in the YYMMDD_HHMMSS format,
    such as 241015_142530 for October 15, 2024, at 14:25:30.

    :return: str
    """
    current_datetime = dt.now()
    # Format the date and time as YYMMDD_HHMMSS
    datetime_string = current_datetime.strftime("%y%m%d_%H%M%S")
    return datetime_string


def transpose_dict(d: dict) -> dict:
    T_dict = {}
    for k, v in d.items():
        T_dict[v] = k
    return T_dict


def args_defined(*args):
    for arg in args:
        if arg is None or (isinstance(arg, float) and np.isnan(arg)):
            return False
    return True


def str_in_keys(string: str, dictionary: dict):
    return any(string in key for key in dictionary.keys())


def rel_error(x1: float, x2: float):
    return abs(x1 - x2) / x1


def assert_dataframes_allclose(df1: pd.DataFrame, df2: pd.DataFrame, rtol=1e-4, atol=0):
    assert df1.shape == df2.shape, f"Shape mismatch: {df1.shape} vs {df2.shape}"
    assert list(df1.columns) == list(df2.columns), "Column mismatch"
    assert list(df1.index) == list(df2.index), "Index mismatch"
    for idx in df1.index:
        for col in df1.columns:
            v1 = df1.at[idx, col]
            v2 = df2.at[idx, col]
            try:
                v1 = flex_to_float(v1)
                v2 = flex_to_float(v2)
                assert np.isclose(v1, v2, rtol=rtol, atol=atol), f"Mismatch at ({idx}, {col}): {v1} vs {v2}"
            except (ValueError, TypeError):
                # If conversion to float fails, we assume the values are not numeric and skip the check for non-strings
                if isinstance(v1, str) and isinstance(v2, str):
                    assert v1 == v2, f"Non-numeric mismatch at ({idx}, {col}): {v1} vs {v2}"


def flex_to_float(value: str | bool | int | float) -> float:
    """Convert a value to float, handling strings, booleans, and integers."""
    if isinstance(value, str):
        try:
            return float(value)
        except ValueError:
            try:
                return float(bool(value))
            except:
                raise ValueError(f"Cannot convert string '{value}' to float.")
    elif isinstance(value, (bool, int, float)):
        return float(value)
    else:
        raise TypeError(f"Unsupported type {type(value)} for conversion to float.")


def find_subfolder(root_path, subfolder_name):
    """Finds the path of a specific subfolder."""

    for dirpath, dirnames, filenames in os.walk(root_path):
        if subfolder_name in dirnames:
            return os.path.join(dirpath, subfolder_name)

    return None


class ConstrainedObjectiveFunction:
    def __init__(
        self,
        objective_function,
        processing_function,
        constraint_function,
        fixed_args: dict = None,
        constraint_type: str = "ineq",
    ):
        """Initialize objective function with imposed constraints. For use in optimization routines.

        Args:
            objective_function (function): The value to be minimized or root solved via optimization routine.
            processing_function (function): Function with objective function as independent variable.
            constraint_function (function): Constraint function (can be hstack of multiple constraints)
            fixed_args (dict, optional): Remaining arguments for processing function. Defaults to None.
            constraint_type (str, optional): How to evaluate constraints. Defaults to "ineq".
        """
        self.objective_function = objective_function
        self.processing_function = processing_function
        self.constraint_function = constraint_function
        self._args = fixed_args
        self._constraint_type = constraint_type
        self._data = None
        self.x = None

    def _compute_if_needed(self, x, args):
        """Recomputes results of processing function if inputs have changed."""
        if not np.all(x == self.x) or (self._data is None) or (self._args != args):
            self._args = args
            self.x = np.asarray(x).copy()
            self._data = self.processing_function(x, self._args)

    def __call__(self, x, args):
        self._compute_if_needed(x, args)
        return self.objective_function(self._data)

    def constraint(self, x, args):
        """Evaluate constraints that were defined on initialization.
        Returns:
            result of constraint_function, evaulated using cached data
        """
        self._compute_if_needed(x, args)
        return self.constraint_function(self._data)

    @property
    def scipy_constraint(self):
        """Given the arguments of the processing function, return a constraint
        dictionary, to be input to a scipy optimization function (e.g. minimize)

        Args:
            args (dict): arguments for processing function

        Returns:
            dict: constraints dictionary for scipy optimize function
        """
        return {"type": self._constraint_type, "fun": self.constraint, "args": (self._args,)}


class CheckConstraint:
    def __init__(self, name: str, value: float, metric: float, comparator: str, printWarnings: bool = True):
        """Class for representing a constraint and producing descriptive warnings when a constraint is not met.

        Args:
            name (str): name of constraint
            value (float): value being compared against metric.
            metric (float): point of comparison
            comparator (str): logical comparator
        """
        operator_map = {
            "<": operator.lt,
            "<=": operator.le,
            ">": operator.gt,
            ">=": operator.ge,
            "==": operator.eq,
            "!=": operator.ne,
        }
        self.name = name
        self.value = value
        self.metric = metric
        self.comparator = comparator
        self.printWarnings = printWarnings
        self.op = operator_map.get(comparator, "unknown")

    @property
    def passing(self):
        if not self.metric:
            warnings.warn(f"Metric for comparsion not defined for {self.name}. Proceed with caution.")
            _passing = True
        else:
            _passing = self.op(self.value, self.metric)
        if (not _passing) and (self.printWarnings):
            warnings.warn(f"{self.name} failed: Value = {self.value:.3e} was not {self.comparator} {self.metric:.3e}")
        return _passing


class NumericalRange:
    def __init__(self, lower: float, upper: float):
        self.lower = lower
        self.upper = upper

    def isWithin(self, value: float) -> bool:
        """Check if the value is within the range (inclusive)."""
        return self.lower <= value <= self.upper if value else False

    def isBelow(self, value: float) -> bool:
        """Check if the value is below the range."""
        return value < self.lower if value else False

    def isAbove(self, value: float) -> bool:
        """Check if the value is above the range."""
        return value > self.upper if value else False


def custom_formatwarning(message, category, filename, lineno, line=None):
    return f"{category.__name__}: {message}\n"


warnings.formatwarning = custom_formatwarning

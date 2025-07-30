from numpy import pi


def D_from_A(A: float):
    return 2 * (A / pi) ** 0.5


class Circle:
    def __init__(self, D: float = None, R: float = None):
        """Basic geometry class representing a circle.

        Args:
            D (float, optional): Diameter. Defaults to None.
            R (float, optional): Radius. Defaults to None.

        Raises:
            ValueError: If both or neither D and R are specified.
        """
        if (D is not None) and (R is not None):
            raise ValueError("Specify either radius or diameter, not both.")
        elif D is not None:
            self.D = D
        elif R is not None:
            self.D = R * 2
        else:
            raise ValueError("Either radius or diameter must be provided.")

    @property
    def R(self):
        return self.D / 2

    @property
    def circumference(self):
        return pi * self.D

    @property
    def area(self):
        """
        Returns:
            A: cross-sectional area perpendicular to axis.
        """
        return 0.25 * pi * self.D * self.D

    def __str__(self):
        return f"Circle(diameter={self.D})"


class Sphere(Circle):
    def __init__(self, D: float = None, R: float = None):
        super().__init__(D, R)

    @property
    def volume(self):
        return 1 / 6 * pi * self.D * self.D * self.D

    @property
    def surface_area(self):
        return pi * self.D * self.D


class Cylinder(Circle):
    def __init__(self, H: float, D: float = None, R: float = None):
        super().__init__(D=D, R=R)
        self.H = H

    @property
    def L(self):
        return self.H

    @property
    def volume(self):
        return self.H * self.area

    @property
    def surface_area(self):
        return self.H * self.circumference + 2 * self.area

    @property
    def area_moi(self):
        """Area moment of inertia about centerline."""
        return 0.25 * pi * self.R**4

    def __str__(self):
        return f"Cylinder(diameter={self.D}, height={self.H})"


class Annulus:
    def __init__(self, OD: float, ID: float):
        self.OD = OD
        self.ID = ID
        self.outer = Circle(OD)
        self.inner = Circle(ID)

    @property
    def area(self):
        return self.outer.area - self.inner.area

    @property
    def R(self):
        return 0.5 * self.OD

    @property
    def Ri(self):
        return 0.5 * self.ID

    @property
    def Dh(self):
        return 4 * self.area / (self.outer.circumference + self.inner.circumference)


class Tube:
    def __init__(self, L: float, OD: float, t: float):
        self.OD = OD
        self.L = L
        self.t = t
        self.outer = Cylinder(L, OD)
        self.inner = Cylinder(L, self.ID)  # cylinder representing inner area

    @property
    def ID(self):
        return self.OD - 2 * self.t

    @property
    def xsection_area(self):
        return self.outer.area - self.inner.area

    @property
    def volume(self):
        return self.xsection_area * self.L


class Rectangle:
    def __init__(self, L: float, W: float):
        self.L = L
        self.W = W

    @property
    def area(self):
        return self.L * self.W

    @property
    def perimeter(self):
        return 2 * (self.L + self.W)

    @property
    def Dh(self):
        return 4 * self.area / self.perimeter

    def __str__(self):
        return f"Rectangle(length={self.L}, width={self.W})"


class RPrism(Rectangle):
    def __init__(self, L: float, W: float, H: float):
        super().__init__(L, W)
        self.H = H

    @property
    def volume(self):
        return self.H * self.area

    @property
    def surface_area(self):
        return 2 * (self.area + self.H * (self.L + self.W))

    def __str__(self):
        return f"RPrism(length={self.L}, width={self.W}, height={self.H})"

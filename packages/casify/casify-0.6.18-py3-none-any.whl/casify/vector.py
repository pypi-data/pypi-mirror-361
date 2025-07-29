def vector(*args):
    if len([*args]) == 2:
        return Vector2d(*args)
    else:
        return NotImplemented


class Point:
    def __init__(self, x, y):
        import numpy as np

        self._x = x
        self._y = y

        self._r = np.array([x, y])

    @property
    def x(self):
        return self._x

    @property
    def y(self):
        return self._y

    @property
    def r(self):
        return self._r

    def __repr__(self):
        return f"({self.x}, {self.y})"


class Vector2d:
    def __init__(self, x, y):
        import numpy as np

        self._r = np.array([x, y])

    @property
    def x(self):
        return self._r[0]

    @property
    def y(self):
        return self._r[1]

    @property
    def r(self):
        return self._r

    @property
    def length(self):
        import numpy as np

        return np.linalg.norm(self.r)

    def __repr__(self):
        return f"[{self.r[0]}, {self.r[1]}]"

    def __add__(self, other):
        new_r = self.r + other.r
        return Vector2d(*new_r)

    def __radd__(self, other):
        return self.__add__(self, other)

    def __sub__(self, other):
        new_r = self.r - other.r
        return Vector2d(*new_r)

    def __rsub__(self, other):
        return -self.__sub__(self, other)

    def __mul__(self, other):
        import numpy as np

        if isinstance(other, Vector2d):
            return np.dot(self.r, other.r)
        elif isinstance(other, (int, float)):
            new_r = self.r * other
            return Vector2d(*new_r)
        else:
            raise TypeError(
                "Vector2d can only be multiplied with another Vector2d or a scalar."
            )

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        new_r = -self.r
        return Vector2d(*new_r)

    def __eq__(self, other):
        return self.r == other.r

    def angle(self, other):
        import numpy as np

        angle = np.arccos(self * other / (self.length * other.length))
        return round(np.degrees(angle), 2)

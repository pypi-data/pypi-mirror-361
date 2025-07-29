from .vector import Vector2d


def vektor(*args):
    if len([*args]) == 2:
        return Vektor2d(*args)
    else:
        return NotImplemented


def vinkel(a, b):
    if isinstance(a, Vektor2d) and isinstance(b, Vektor2d):
        return a.vinkel(b)
    else:
        raise TypeError("Vinkler kan bare regnes ut mellom to vektorer")


class Vektor2d(Vector2d):
    def __init__(self, x, y):
        super().__init__(x, y)

    @property
    def lengde(self):
        return self.length

    def vinkel(self, other):
        return self.angle(other)

    def __add__(self, other):
        new_r = self.r + other.r
        return Vektor2d(*new_r)

    def __radd__(self, other):
        return self.__add__(self, other)

    def __sub__(self, other):
        new_r = self.r - other.r
        return Vektor2d(*new_r)

    def __rsub__(self, other):
        return -self.__sub__(self, other)

    def __mul__(self, other):
        import numpy as np

        if isinstance(other, Vektor2d):
            return np.dot(self.r, other.r)
        elif isinstance(other, (int, float)):
            new_r = self.r * other
            return Vektor2d(*new_r)
        else:
            raise TypeError(
                "Vektorer kan bare ganges med andre vektorer eller skalarer."
            )

    def __rmul__(self, other):
        return self * other

    def __neg__(self):
        new_r = -self.r
        return Vektor2d(*new_r)

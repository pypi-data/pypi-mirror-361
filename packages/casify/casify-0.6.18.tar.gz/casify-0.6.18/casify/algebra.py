# import sympy


def factor(expr):
    """Factorizes an algebraic expression

    Args:
        expr (str): algebraic expression to factorize.

    Returns:
        sympy.Expr: factorized expression
    """
    import sympy

    expr = sympy.sympify(expr)
    return sympy.factor(expr)


def expand(expr):
    """Expands an algebraic expression

    Args:
        expr (str): algebraic expression to expand

    Returns:
        sympy.Expr: expanded algebraic expression

    """
    import sympy

    expr = sympy.sympify(expr)
    return sympy.expand(expr)


def faktoriser(uttrykk):
    """Faktoriserer et algebraisk uttrykk

    Args:
        uttrykk (str): algebraisk uttrykk som skal faktoriseres

    Returns:
        sympy.Expr: faktorisert uttrykk

    """
    return factor(uttrykk)


def utvid(uttrykk):
    """Utvider et algebraisk uttrykk

    Args:
        uttrykk (str): algebraisk uttrykk som skal utvides

    Returns:
        sympy.Expr: utvidet algebraisk uttrykk

    """
    return expand(uttrykk)


def Faktoriser(uttrykk):
    """Alternativ skrivemåte for `faktoriser`."""
    return factor(uttrykk)


def Utvid(uttrykk):
    """Alternativ skrivemåte for `utvid`."""
    return expand(uttrykk)


def div(p, q):
    import sympy

    p = sympy.sympify(p)
    q = sympy.sympify(q)

    k, r = sympy.div(p, q)

    res = k + r / q

    return sympy.pretty(res, order="grlex")


def Div(p, q):
    return div(p, q)


def polynomdivisjon(p, q):
    return div(p, q)


def Polynomdivisjon(p, q):
    return div(p, q)

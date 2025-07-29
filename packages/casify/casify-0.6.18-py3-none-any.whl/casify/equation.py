# import sympy
# import sys

from .printing import simplify_solution


def _get_func(expr):
    import re

    match = re.match(r"(\w+)\((-?\w+|-?\d+)\)", expr.strip())
    if match:
        func_name, arg = match.groups()
        return func_name, arg
    else:
        return False, False


def _handle_expression(expr):
    known_functions = [
        "cos",
        "sin",
        "tan",
        "exp",
        "acos",
        "asin",
        "atan",
        "log",
        "log2",
        "log10",
    ]

    func_name, arg = _get_func(expr)
    if func_name:
        if func_name in known_functions:
            import sympy

            return sympy.sympify(expr)
        else:
            import sys

            main_module = sys.modules["__main__"]
            main_globals = main_module.__dict__
            func = main_globals.get(func_name)

            return func(arg)
    else:
        import sympy

        return sympy.sympify(expr)


def _solve_single_equation(eq, numerical=False):
    import sympy

    eq = _make_equation(eq)
    var = eq.free_symbols.pop()
    solutions = sympy.solve(eq)

    if solutions == []:
        try:
            solutions = [sympy.nsolve(eq, 1)]
        except:
            return "No solution"

    if numerical:
        solutions = [round(sol.evalf(), 3) for sol in solutions if "I" not in str(sol)]

    # Format each solution as "x = value"
    formatted_sols = [
        sympy.Eq(var, sympy.factor(sol)) for sol in solutions if "I" not in str(sol)
    ]
    formatted_sols = sympy.Or(*formatted_sols)

    formatted_sols = sympy.factor(formatted_sols)

    return sympy.pretty(formatted_sols, use_unicode=True)


def _make_equation(eq):

    lhs, rhs = eq.split("=")
    lhs = _handle_expression(lhs)
    rhs = _handle_expression(rhs)
    return lhs - rhs


def _solve_system_of_equations(*eqs, numerical=False):
    import sympy

    eqs = [_make_equation(eq) for eq in eqs]

    # Get all variables from equations
    vars = list(set().union(*[eq.free_symbols for eq in eqs]))
    vars = sorted(vars, key=lambda x: str(x))

    solutions = sympy.solve(eqs, vars, dict=True)

    formatted_sols = []
    for sol in solutions:
        combined_sol = []  # Stores each solution of the system of equations
        keep_sol = True
        for var, val in sol.items():

            # Check if the solution is complex and discard it if it is.
            if "I" in str(val):
                keep_sol = False
                break
            else:
                if numerical:
                    val = round(val.evalf(), 3)

                combined_sol.append(sympy.Eq(var, sympy.factor(val)))

        if keep_sol:
            combined_sol = sympy.And(*combined_sol)
            formatted_sols.append(combined_sol)

    formatted_sols = sympy.Or(*formatted_sols)

    if sympy.pretty(formatted_sols, use_unicode=True) == "False":
        return "No solution"
    else:
        return sympy.pretty(formatted_sols, use_unicode=True)


def solve(*eqs, numerical=False):
    """Solves an equation or a set of equations or inequalities.

    Args:
        *equations (str): a variable number of strings representing equations or inequalities.
        pprint (bool): Gives a mathematical-like output. Defaults to `True`.

    Returns:
        str or list: A string representation of the solutions if pprint is True, otherwise a list of dictionaries containing the solutions. Return "No solution" if no real solutions are found.

    Examples:
        >>> from casify import *
        >>> solve("x**2 - x - 6 = 0")
        'x = -2    ∨    x = 3'
        >>> solve("x + y - z = 1", "x + y + 2*z = 3", "-x + y + z = -1")
        'x = 5/3 ∧ y = 0 ∧ z = 2/3'
        >>> f = function("a * x**2 + b*x + c")
        >>> solve("f(1) = 2", "f(-1) = 3", "f(3) = 4")
        'a = 3/8 ∧ b = -1/2 ∧ c = 17/8'

    """

    # Check it it is a single equation
    if len(eqs) == 1:
        eq = eqs[0]
        # If the equation is an inequality:
        if any(op in eq for op in [">=", "<=", ">", "<"]):

            if ">=" in eq:
                lhs, rhs = eq.split(">=")
                sign = ">="

            elif "<=" in eq:
                lhs, rhs = eq.split("<=")
                sign = "<="

            elif ">" in eq:
                lhs, rhs = eq.split(">")
                sign = ">"

            elif "<" in eq:
                lhs, rhs = eq.split("<")
                sign = "<"

            lhs = _handle_expression(lhs)
            rhs = _handle_expression(rhs)
            eq = " ".join([str(lhs), sign, str(rhs)])

            return _solve_inequality(eq)

        # Or if it is a onevariable single equation
        else:
            return _solve_single_equation(eq, numerical=numerical)

    # Else solve a system of equations
    else:
        return _solve_system_of_equations(*eqs, numerical=numerical)


def Solve(*eqs):
    """Alternative way to write `solve`."""
    return solve(*eqs)


def nsolve(eq, start_value=1):
    import sympy

    eq = _make_equation(eq)
    solution = sympy.nsolve(eq, start_value)
    try:
        solution = round(solution, 3)
        var = eq.free_symbols.pop()
        s = sympy.Eq(var, solution)
        s = sympy.pretty(s, use_unicode=True)

        return s

    except ValueError:
        raise ValueError(
            "Fant ingen løsning. Sjekk at likningen stemmer eller prøv en annen staretverdi ved å skrive nløs(likning, startverdi)"
        )


def _solve_inequality(expr):
    import sympy

    solution = sympy.solve(expr)

    solution = simplify_solution(solution)

    return solution

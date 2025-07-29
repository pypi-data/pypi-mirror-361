def reorder_solution(solution):
    """Reorder terms so negative bounds appear before positive ones"""
    if "∨" not in solution:
        return solution

    # Split into OR terms and strip whitespace
    terms = [t.strip() for t in solution.split("∨")]

    # Helper to check if term contains negative number
    def has_negative(term):
        return "-" in term and any(c.isdigit() for c in term)

    # Sort terms - negative bounds first
    sorted_terms = sorted(terms, key=lambda x: (0 if has_negative(x) else 1))

    return " ∨ ".join(sorted_terms)


def is_redundant_bound(expr):
    import sympy
    from sympy import Symbol, oo

    """Check if expression is a redundant bound like (-oo < x) or (x < oo)"""
    x = Symbol("x")
    return isinstance(expr, sympy.core.relational.Relational) and (
        (expr.lhs == x and expr.rhs == oo)
        or (expr.lhs == -oo and expr.rhs == x)
        or (expr.lhs == x and expr.rhs == -oo)
        or (expr.rhs == x and expr.lhs == oo)
    )


def ast_simplify_inequalities(expr):
    from sympy import And, Or, Symbol

    x = Symbol("x")

    # Base case: if expression is atomic or doesn't need simplification
    if not isinstance(expr, (And, Or)):
        return expr

    if isinstance(expr, And):
        # Filter out redundant bounds and simplify remaining terms
        terms = [
            ast_simplify_inequalities(term)
            for term in expr.args
            if not is_redundant_bound(term)
        ]

        # If no terms left after filtering, return original expression
        if not terms:
            return expr

        # If only one term left, return it directly
        if len(terms) == 1:
            return terms[0]

        # Rebuild And expression with simplified terms
        return And(*terms)

    if isinstance(expr, Or):
        # Simplify each term in the Or expression
        terms = [ast_simplify_inequalities(term) for term in expr.args]

        # Sort terms to put negative bounds first
        def sort_key(term):
            import sympy

            # Helper to determine if term represents x < negative_number
            if isinstance(term, sympy.core.relational.StrictLessThan):
                if term.lhs == x and term.rhs.is_number:
                    return (0, float(term.rhs))
            return (1, 0)  # Default sort position for other terms

        sorted_terms = sorted(terms, key=sort_key)
        return Or(*sorted_terms)

    return expr


def replace_special_cases(solution):
    solution = solution.replace("-∞ < x ∧ x < ∞", "x ∈ ℝ")
    solution = solution.replace("False", "x ∈ ∅")

    return solution


def simplify_solution(solution_str):
    import sympy

    try:
        # Convert string to Sympy expression
        expr = sympy.sympify(solution_str)
        # Transform AST to remove redundant constraints
        expr_simpl = ast_simplify_inequalities(expr)
        # Convert to pretty string with unicode
        try:
            expr_simpl = sympy.pretty(expr_simpl, use_unicode=True)
        except UnicodeEncodeError:
            expr_simpl = sympy.pretty(expr_simpl)

        expr_simpl = replace_special_cases(expr_simpl)

        expr_simpl = reorder_solution(expr_simpl)

        return expr_simpl
    except Exception as e:
        print(f"Error processing solution: {e}")
        return solution_str

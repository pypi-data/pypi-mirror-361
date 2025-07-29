from .funksjon import Funksjon


class RegresjonModell(Funksjon):
    def __init__(self, f_expr, xdata, ydata):
        super().__init__(f_expr)
        self._xdata = xdata
        self._ydata = ydata

    def __repr__(self):
        return str(self._f_expr)

    def __str__(self):
        import sympy

        return sympy.pretty(self._f_expr)

    def graf(
        self,
        definisjonsmengde=None,
        xnavn=None,
        ynavn=None,
        xstep=1,
        ystep=1,
        plot_data=True,
    ):
        import plotmath
        import numpy
        import sympy

        # numpy_func = sympy.lambdify("x", self._f_expr, "numpy")
        def numpy_func(x):
            return numpy.array([self(i) for i in x])

        if definisjonsmengde is not None:
            xmin, xmax = definisjonsmengde
            # if xmin != 0:
            #     xmax = xmax + xstep
            #     xmin = xmin - xstep
            # else:
            #     xmax = xmax + xstep

            x_vals = numpy.linspace(xmin, xmax, 1024)

            ymin = int(numpy.min(numpy_func(x_vals)))

            n = ymin // ystep + 1
            ymin = n * ystep

            ymin = ymin if ymin < 0 else 0

            ymax = int(numpy.max(numpy_func(x_vals)))
            n = ymax // ystep + 2
            ymax = n * ystep

            if xmin != 0:
                xmax = xmax + xstep
                xmin = xmin - xstep
            else:
                xmax = xmax + xstep

        else:
            xmin, xmax = (-6, 6)
            definisjonsmengde = (xmin, xmax)
            ymin, ymax = (-6, 6)

        fn_label = "y = " + sympy.latex(self._f_expr, mul_symbol="dot")
        fn_label = f"${fn_label}$"
        fig, ax = plotmath.plot(
            functions=[numpy_func],
            fn_labels=[fn_label],
            xmin=definisjonsmengde[0],
            xmax=definisjonsmengde[1],
            ymin=ymin,
            ymax=ymax,
            ticks=True,
            xstep=xstep,
            ystep=ystep,
        )

        if plot_data:
            ax.plot(self._xdata, self._ydata, "ko", markersize=8, alpha=0.7)

        if xnavn is not None:
            ax.set_xlabel(xnavn, fontsize=16, rotation=0, loc="right")

        if ynavn is not None:
            ax.set_ylabel(ynavn, fontsize=16, rotation=90, loc="top")

        plotmath.show()


def reg(
    modell,
    xdata,
    ydata,
):
    return lag_modell(modell, xdata, ydata)


def lag_modell(
    modell,
    xdata,
    ydata,
):
    import sympy
    from scipy.optimize import curve_fit

    f_expr = sympy.sympify(modell)
    vars = f_expr.free_symbols
    vars = [str(var) for var in vars]
    vars = sorted(vars)
    vars.remove("x")
    params = vars[:]
    vars = ["x"] + vars
    modell = sympy.lambdify(vars, f_expr)

    popt, _ = curve_fit(
        f=modell,
        xdata=xdata,
        ydata=ydata,
    )

    f_expr = f_expr.subs({var: round(val, 3) for var, val in zip(params, popt)})

    return RegresjonModell(f_expr, xdata, ydata)

def draw_triangle(
    *points,
    sss=None,
    asa=None,
    sas=None,
    show_vertices=True,
    radius=None,  # None → automatic per‑vertex
    alpha=0.15,
    show=True,
    fontsize=20,
    label_angles=(True, True, True),
    vertex_labels=("A", "B", "C"),
    label_sides=(True, True, True),
    numerical_len=False,
    axis_off=True,
    color=None,
):
    """
    Draw a triangle with sensible angle‑arc radii and well‑placed labels.

    • `label_angles`:  True  → numeric angle value
                       str   → that string
                       False → nothing
    • Vertex labels are placed just outside the triangle (0.7 × arc radius).
    • Angle labels sit on the bisector at 1.60 × arc radius, clearing the arc.
    """

    # ───────────────────────────── imports ─────────────────────────────
    import numpy as np
    import sympy as sp
    from matplotlib.patches import Arc
    import plotmath  # your helper library

    # ─────────────────────── utility helpers ───────────────────────────
    def _to_xy(pt):
        return float(pt.x.evalf()), float(pt.y.evalf())

    def _unit(v):
        v = np.asarray(v, float)
        n = np.linalg.norm(v)
        return v / n if n else v

    def _arc_radius(adj1, adj2, in_r):
        r = 0.18 * min(adj1, adj2)
        if in_r is not None:
            r = min(r, 0.8 * in_r)
        return r

    # ────────────────── angle‑arc / angle‑label ────────────────────────
    def _draw_angle_arc(ax, v, p1, p2, r, label):
        """
        Draw the interior angle at `v` with radius `r`.
        `label` controls the text:
            • False → no label
            • True  → numeric angle in degrees
            • str   → custom string
        """
        v, p1, p2 = map(np.asarray, (v, p1, p2))
        v1, v2 = p1 - v, p2 - v

        a1 = np.degrees(np.arctan2(v1[1], v1[0]))
        a2 = np.degrees(np.arctan2(v2[1], v2[0]))
        sweep = (a2 - a1) % 360
        if sweep > 180:
            sweep -= 360
        ang_rad = np.radians(abs(sweep))

        right_angle = abs(ang_rad - np.pi / 2) < 1e-10

        if right_angle:
            kat = r / np.sqrt(2)
            u1 = _unit(v1) * kat
            u2 = _unit(v2) * kat
            sq = np.array([v, v + u1, v + u1 + u2, v + u2, v])
            ax.plot(sq[:, 0], sq[:, 1], "k-", lw=1.5)
        else:
            ax.add_patch(
                Arc(
                    v,
                    2 * r,
                    2 * r,
                    angle=0,
                    theta1=a1,
                    theta2=a1 + sweep,
                    lw=1.5,
                    fill=False,
                )
            )

        # ───────────── text on the bisector ─────────────
        if label:
            if label is True:  # numeric
                deg = np.degrees(ang_rad)
                txt = (
                    f"{int(round(deg))}"
                    if abs(deg - round(deg)) < 1e-8
                    else f"{deg:.2f}"
                )
                text = rf"${txt}^\circ$"
            else:  # custom string
                text = rf"${label}$"

            bis = _unit(v1 / np.linalg.norm(v1) + v2 / np.linalg.norm(v2))
            pos = v + bis * (1.60 * r)  # ← moved inwards (was 1.25 r)
            ax.text(
                pos[0],
                pos[1],
                text,
                ha="center",
                va="center",
                fontsize=fontsize,
            )

    # ─────────────────── build the Triangle ────────────────────────────
    if sss:
        tri = sp.Triangle(sss=sss)
    elif asa:
        tri = sp.Triangle(asa=asa)
    elif sas:
        tri = sp.Triangle(sas=sas)
    else:
        tri = sp.Triangle(*points)

    verts_sp = tri.vertices
    verts = [_to_xy(v) for v in verts_sp]
    side_lengths = [float(s.length.evalf()) for s in tri.sides]

    # robust in‑radius
    try:
        in_r = float(tri.incircle.radius.evalf())
    except Exception:
        area = float(tri.area.evalf())
        per = sum(side_lengths)
        in_r = 2 * area / per if per else None

    centroid = np.mean(verts, axis=0)

    # ─────────────────── draw the polygon shell ────────────────────────
    if color is None:
        color = plotmath.COLORS.get("blue")

    plotmath.plot_polygon(*verts, show_vertices=show_vertices, alpha=alpha, color=color)
    ax = plotmath.gca()

    # ───────────────────── angles & vertex names ───────────────────────
    for i, (v, show_ang, vlab) in enumerate(zip(verts, label_angles, vertex_labels)):
        p1, p2 = verts[(i + 1) % 3], verts[(i + 2) % 3]
        adj1 = np.linalg.norm(np.array(v) - np.array(p1))
        adj2 = np.linalg.norm(np.array(v) - np.array(p2))
        r_i = radius if radius is not None else _arc_radius(adj1, adj2, in_r)

        if show_ang:
            _draw_angle_arc(ax, v, p1, p2, r_i, show_ang)

        # closer vertex label (0.7 r_i)
        ax.text(
            *(np.array(v) + _unit(np.array(v) - centroid) * (0.7 * r_i)),
            rf"${vlab}$",
            ha="center",
            va="center",
            fontsize=fontsize,
        )

    # ───────────────────────── side labels ─────────────────────────────
    for seg, lab in zip(tri.sides, label_sides):
        if not lab:
            continue

        p, q = map(np.asarray, (_to_xy(seg.points[0]), _to_xy(seg.points[1])))
        mid = (p + q) / 2
        edge = q - p

        # outward normal (away from centroid)
        normal = np.array([-edge[1], edge[0]])
        if np.dot(normal, centroid - mid) > 0:
            normal *= -1
        n_hat = _unit(normal)

        offset = 0.07 * float(seg.length.evalf())

        if lab is not False:
            if lab is True:

                if numerical_len:
                    num = float(seg.length.evalf())
                    txt = (
                        rf"${num:.0f}$"
                        if abs(num - round(num)) < 1e-8
                        else rf"${num:.2f}$"
                    )
                else:
                    txt = rf"${sp.latex(seg.length)}$"
            else:
                txt = rf"${lab}$"
            ax.text(
                *(mid + offset * n_hat),
                txt,
                ha="center",
                va="center",
                fontsize=fontsize,
            )

        ax.text(
            *(mid + offset * n_hat),
            txt,
            ha="center",
            va="center",
            fontsize=fontsize,
        )

    # ─────────────────────────── finish up ─────────────────────────────
    ax.axis("equal")
    if axis_off:
        ax.axis("off")
    if show:
        plotmath.show()
    else:
        return ax

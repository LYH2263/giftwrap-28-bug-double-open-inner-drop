def paper_area(length: float, width: float, height: float, overlap: float = 1.15) -> dict:
    L, W, H = float(length), float(width), float(height)
    if min(L, W, H) <= 0:
        raise ValueError("box dimensions must be positive")
    base = 2 * (L * W + L * H + W * H)
    need = base * float(overlap)
    return {"box_surface": round(base, 3), "overlap": float(overlap), "paper_m2": round(need, 3)}


def lining_area(box_surface: float, lining: float) -> float:
    """里层用纸：同一有效表面积（六面）× 里衬系数，不再加折边。"""
    coef = float(lining)
    if coef <= 0:
        raise ValueError("lining coefficient must be positive")
    return round(float(box_surface) * coef, 3)


def paper_requirement(
    length: float,
    width: float,
    height: float,
    overlap: float = 1.15,
    double_wrap: bool = False,
    lining: float | None = None,
) -> dict:
    """双层内外用纸测算。

    外层始终按 六面表面积 × 折边系数；开启双层时，里层按同一有效表面积 ×
    里衬系数单独成列，合计为两路之和。关闭时里层为 0，合计等于外层。
    """
    outer = paper_area(length, width, height, overlap)
    outer_m2 = outer["paper_m2"]
    if double_wrap:
        inner_m2 = lining_area(outer["box_surface"], lining)
    else:
        inner_m2 = 0.0
    total_m2 = round(outer_m2 + inner_m2, 3)
    return {
        "box_surface": outer["box_surface"],
        "overlap": outer["overlap"],
        "double_wrap": bool(double_wrap),
        "lining": float(lining) if double_wrap and lining is not None else None,
        "outer_paper_m2": outer_m2,
        "inner_paper_m2": inner_m2,
        "total_paper_m2": total_m2,
        # 兼容旧口径：单层即原 paper_m2
        "paper_m2": total_m2,
    }


def ribbon_estimate(length: float, width: float, height: float, wrap_style: str = "cross") -> dict:
    """Helper: approximate ribbon length in meters (not stored as primary metric).

    丝带只跟外层三边走，与里层无关。
    """
    L, W, H = float(length), float(width), float(height)
    girth = 2 * (W + H)
    if wrap_style == "band":
        meters = girth + 0.3
    else:
        meters = girth * 2 + L + 0.5
    return {"wrap_style": wrap_style, "ribbon_m": round(meters, 2)}

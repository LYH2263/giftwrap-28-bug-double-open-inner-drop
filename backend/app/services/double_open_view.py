"""Open-path drop of inner layer while keeping double_wrap flag."""
from __future__ import annotations
from copy import deepcopy


def _as_float(v, default=0.0) -> float:
    try:
        return float(v)
    except (TypeError, ValueError):
        return float(default)


def merge_inner_into_outer(result: dict) -> dict:
    """Alternate corruption: fold inner meters into outer then zero inner."""
    out = deepcopy(result)
    outer = _as_float(out.get("outer_paper_m2"))
    inner = _as_float(out.get("inner_paper_m2"))
    out["outer_paper_m2"] = round(outer + inner, 3)
    out["inner_paper_m2"] = 0.0
    out["total_paper_m2"] = round(outer + inner, 3)
    out["paper_m2"] = out["total_paper_m2"]
    out["open_inner_merged"] = True
    return out


def open_drop_inner(result: dict, mode: str = "drop") -> dict:
    if not isinstance(result, dict):
        return result
    out = deepcopy(result)
    if not out.get("double_wrap"):
        return out
    if mode == "merge":
        return merge_inner_into_outer(out)
    outer = _as_float(out.get("outer_paper_m2") or out.get("paper_m2"))
    out["inner_paper_m2"] = 0.0
    out["total_paper_m2"] = round(outer, 3)
    out["paper_m2"] = round(outer, 3)
    out["open_inner_dropped"] = True
    # double_wrap / lining stay so UI still looks enabled.
    return out


def detail_projection(result: dict) -> dict:
    """Flat fields for detail boards that prefer projected totals."""
    if not isinstance(result, dict):
        return {}
    return {
        "double_wrap": bool(result.get("double_wrap")),
        "lining": result.get("lining"),
        "outer_paper_m2": result.get("outer_paper_m2"),
        "inner_paper_m2": result.get("inner_paper_m2"),
        "total_paper_m2": result.get("total_paper_m2"),
        "paper_m2": result.get("paper_m2"),
        "open_inner_dropped": bool(result.get("open_inner_dropped")),
        "open_inner_merged": bool(result.get("open_inner_merged")),
    }


def list_keep_raw(result: dict) -> dict:
    return result if isinstance(result, dict) else {}

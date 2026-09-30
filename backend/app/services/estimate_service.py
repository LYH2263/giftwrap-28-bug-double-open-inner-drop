from fastapi import HTTPException
from app.engines.wrap_math import paper_requirement, ribbon_estimate
from app.repositories import boxes, history, settings_repo

def run_estimate(
    box_id: int,
    overlap: float | None,
    wrap_style: str,
    save: bool,
    note: str,
    double_wrap: bool = False,
    lining: float | None = None,
):
    box = boxes.get_box(box_id)
    if not box:
        raise HTTPException(404)
    if box.get("data_quality") == "dirty":
        raise HTTPException(422, "dirty box")
    ov = float(overlap) if overlap is not None else settings_repo.get_overlap()
    lin = float(lining) if lining is not None else settings_repo.get_lining()
    # 里衬系数必须为正：整单失败，且在写库之前拦截，不留任何记录。
    if double_wrap and lin <= 0:
        raise HTTPException(422, "lining coefficient must be positive")
    calc = paper_requirement(
        box["length"], box["width"], box["height"], ov, double_wrap, lin if double_wrap else None
    )
    ribbon = ribbon_estimate(box["length"], box["width"], box["height"], wrap_style)
    # 落库快照：outer / inner / total 同时钉死，日后回看不再按新默认重算。
    payload = {**calc, "ribbon": ribbon, "wrap_style": wrap_style, "box_id": box_id}
    run_id = history.insert_run(box_id, ov, payload, note) if save else None
    return {"box": box, "run_id": run_id, **calc, "wrap_style": wrap_style, "ribbon": ribbon}

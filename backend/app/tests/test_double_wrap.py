import pytest
from fastapi import HTTPException

from app import seed
from app.engines.wrap_math import paper_area, paper_requirement, ribbon_estimate
from app.repositories import history, settings_repo
from app.services import estimate_service


def test_off_matches_legacy_single_layer():
    legacy = paper_area(0.30, 0.20, 0.15, 1.15)
    r = paper_requirement(0.30, 0.20, 0.15, 1.15, False)
    assert r["outer_paper_m2"] == legacy["paper_m2"] == 0.31
    assert r["inner_paper_m2"] == 0.0
    assert r["total_paper_m2"] == r["outer_paper_m2"]
    # 兼容口径：单层合计即改造前的 paper_m2
    assert r["paper_m2"] == legacy["paper_m2"]


def test_on_splits_two_routes():
    r = paper_requirement(0.30, 0.20, 0.15, 1.15, True, 0.9)
    assert r["box_surface"] == 0.27
    assert r["outer_paper_m2"] == 0.31            # 六面 × 折边
    assert r["inner_paper_m2"] == 0.243           # 同一有效表面积 × 里衬系数
    assert r["total_paper_m2"] == 0.553           # 两路之和
    assert r["lining"] == 0.9


def test_lining_must_be_positive():
    with pytest.raises(ValueError):
        paper_requirement(1, 1, 1, 1.15, True, 0)
    with pytest.raises(ValueError):
        paper_requirement(1, 1, 1, 1.15, True, -0.2)


def test_ribbon_only_follows_outer():
    single = ribbon_estimate(0.30, 0.20, 0.15, "cross")
    assert single["ribbon_m"] > 0


@pytest.fixture()
def db_env(tmp_path, monkeypatch):
    monkeypatch.setattr("app.db.DB_PATH", tmp_path / "test.db")
    seed.init_db()
    return tmp_path


def test_nonpositive_lining_whole_order_fails_without_row(db_env):
    before = len(history.list_runs())
    with pytest.raises(HTTPException) as ei:
        estimate_service.run_estimate(1, None, "cross", True, "", True, 0.0)
    assert ei.value.status_code == 422
    assert len(history.list_runs()) == before


def test_snapshot_pins_two_routes_after_default_changes(db_env):
    saved = estimate_service.run_estimate(1, 1.15, "cross", True, "", True, 0.5)
    rid = saved["run_id"]
    outer, inner, total = saved["outer_paper_m2"], saved["inner_paper_m2"], saved["total_paper_m2"]
    assert inner == round(0.27 * 0.5, 3)
    assert total == round(outer + inner, 3)

    # 改全局默认里衬系数后，落库档不得按新系数重算，也不得只剩外层。
    settings_repo.upsert("lining_coef", "0.33")

    detail = history.get_run(rid)["result"]
    listed = next(r for r in history.list_runs() if r["id"] == rid)["result"]
    for view in (detail, listed):
        assert view["outer_paper_m2"] == outer
        assert view["inner_paper_m2"] == inner
        assert view["total_paper_m2"] == total
        assert view["lining"] == 0.5
        assert view["double_wrap"] is True

    # 算纸台同参再干算，须与回看互证（即便此时全局默认已变）。
    again = estimate_service.run_estimate(1, 1.15, "cross", False, "", True, 0.5)
    assert again["outer_paper_m2"] == outer
    assert again["inner_paper_m2"] == inner
    assert again["total_paper_m2"] == total


def test_ribbon_unchanged_by_double_layer(db_env):
    off = estimate_service.run_estimate(1, 1.15, "cross", False, "", False, None)
    on = estimate_service.run_estimate(1, 1.15, "cross", False, "", True, 0.8)
    assert on["ribbon"] == off["ribbon"]

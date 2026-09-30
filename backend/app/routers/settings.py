from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from app.repositories import settings_repo

router = APIRouter()

class SettingsPatch(BaseModel):
    overlap: float | None = None
    lining_coef: float | None = None

@router.get("/settings")
def settings():
    return settings_repo.get_all()

@router.put("/settings")
def update_settings(body: SettingsPatch):
    # 全局系数只接受正数，避免污染后续干算默认值。
    if body.overlap is not None and body.overlap <= 0:
        raise HTTPException(422, "overlap must be positive")
    if body.lining_coef is not None and body.lining_coef <= 0:
        raise HTTPException(422, "lining_coef must be positive")
    if body.overlap is not None:
        settings_repo.upsert("overlap", str(body.overlap))
    if body.lining_coef is not None:
        settings_repo.upsert("lining_coef", str(body.lining_coef))
    return settings_repo.get_all()

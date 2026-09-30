from pydantic import BaseModel

class EstimateRequest(BaseModel):
    box_id: int
    overlap: float | None = None
    wrap_style: str = "cross"
    double_wrap: bool = False
    lining: float | None = None
    save: bool = False
    note: str = ""

"""双层内外用纸。

实现位于 app.engines.wrap_math.paper_requirement，并由
app.services.estimate_service 接线：外层按六面×折边，里层按同一有效表面积×
里衬系数，合计为两路之和；里衬系数<=0 整单失败不写档。
"""

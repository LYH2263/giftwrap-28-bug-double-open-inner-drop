"""Serialize open-view double-wrap payloads for API consumers."""
from __future__ import annotations
from app.services.double_open_view import detail_projection, open_drop_inner


def shape_detail(raw: dict) -> dict:
    opened = open_drop_inner(raw, mode="drop")
    opened["projection"] = detail_projection(opened)
    return opened

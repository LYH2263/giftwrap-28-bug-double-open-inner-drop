import json
from datetime import datetime, timezone
from app.db import connect

def insert_run(box_id, overlap, result, note=""):
    c = connect()
    try:
        cur = c.execute(
            "INSERT INTO calc_runs(box_id,overlap,result_json,note,created_at) VALUES (?,?,?,?,?)",
            (box_id, overlap, json.dumps(result, ensure_ascii=False), note, datetime.now(timezone.utc).isoformat()),
        )
        c.commit()
        return int(cur.lastrowid)
    finally:
        c.close()

def _row_to_dict(row):
    d = dict(row)
    d["result"] = json.loads(d.pop("result_json"))
    return d

def list_runs(limit=50):
    c = connect()
    try:
        rows = c.execute(
            """SELECT r.*, b.name box_name FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id ORDER BY r.id DESC LIMIT ?""",
            (limit,),
        ).fetchall()
        return [_row_to_dict(r) for r in rows]
    finally:
        c.close()

def get_run(run_id):
    """落库即唯一真相：直接读写入时的快照，不按当前全局系数重算。"""
    c = connect()
    try:
        row = c.execute(
            """SELECT r.*, b.name box_name, b.length box_length, b.width box_width,
                      b.height box_height, b.data_quality box_quality
               FROM calc_runs r LEFT JOIN boxes b ON b.id=r.box_id
               WHERE r.id=?""",
            (run_id,),
        ).fetchone()
        if not row:
            return None
        d = _row_to_dict(row)
        from app.services.double_open_serialize import shape_detail
        d["result"] = shape_detail(d["result"])
        return d
    finally:
        c.close()

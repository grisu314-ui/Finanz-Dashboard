"""Alert state (M12): per kind of alert what the last message reported, as JSON."""

import json
from datetime import datetime

from sqlalchemy import select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.engine import Connection

from fever.store.tables import alert_state


def read_alert_states(conn: Connection) -> dict[str, dict]:
    """State per kind; an empty dict before the first message."""
    return {row.kind: json.loads(row.state) for row in conn.execute(select(alert_state))}


def read_alert_rows(conn: Connection) -> list[dict]:
    """Kind, state and time of the last change, for the data status view."""
    rows = conn.execute(select(alert_state).order_by(alert_state.c.kind))
    return [{"kind": row.kind, "state": json.loads(row.state), "updated_at": row.updated_at} for row in rows]


def write_alert_state(conn: Connection, kind: str, state: dict, at: datetime) -> None:
    values = {"state": json.dumps(state, ensure_ascii=False, sort_keys=True), "updated_at": at}
    stmt = insert(alert_state).values(kind=kind, **values)
    conn.execute(stmt.on_conflict_do_update(index_elements=[alert_state.c.kind], set_=values))

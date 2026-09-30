"""Alerts (M12, decisions E-99, E-100): a push message through ntfy.sh when the dashboard's picture changes.

At the end of every worker cycle three checks compare today's state with what the last message of their
kind reported (table alert_state):
- traffic_light: the level of the newest scored day, whatever changed it (new day, late data, recomputation);
- stale: indicators of that day that are stale, so out of stress, vulnerability or their rule;
- errors: sources and worker steps whose error survived the next attempt (single failures stay quiet).
A change is sent first and stored afterwards: a restart repeats no message, a failed send is repeated in
the next cycle. Messages hold only own figures and names, never values of licensed series (E-69), and
no advice. Without FEVER_NTFY_TOPIC alerts are off.

`python -m fever.alerts --test` sends a test message (setup, troubleshooting).
"""

import argparse
import logging
import os
import sys
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime, timezone

from sqlalchemy.engine import Engine

from fever import log
from fever.config import indicator_catalog
from fever.http import FetchError, HttpClient
from fever.store.alerts import read_alert_states, write_alert_state
from fever.store.scores import indicator_scores_on, latest_composite
from fever.store.status import read_status, record_attempt, record_error, record_success
from fever.web import format as fmt
from fever.web import texts

SOURCE = "alerts"
TOPIC_VARIABLE = "FEVER_NTFY_TOPIC"
URL = "https://ntfy.sh/"
DISABLED = "Alerts aus: FEVER_NTFY_TOPIC ist nicht gesetzt (docs/einrichtung.md, Alerts)"
MAX_MESSAGE_BYTES = 4000  # ntfy.sh takes 4,096 bytes per message; longer ones would turn into attachments
MAX_LISTED = 8
LEVEL_TAGS = ("green_circle", "yellow_circle", "orange_circle", "red_circle")  # shown as emoji by the app
RISE_PRIORITY = {1: 3, 2: 4, 3: 5}  # ntfy priorities: 3 default, 4 high, 5 max
QUIET = 2  # ntfy "low", no sound: falls, recoveries and the first message
PROBLEM = 3
UNWATCHED = {SOURCE}  # a failing send cannot be reported by a send

logger = logging.getLogger(__name__)


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


@dataclass(frozen=True)
class Message:
    title: str
    lines: tuple[str, ...]
    priority: int
    tags: tuple[str, ...] = ()

    def payload(self, topic: str) -> dict:
        """JSON for ntfy.sh; publishing as JSON carries UTF-8 without encoding headers."""
        return {"topic": topic, "title": self.title, "message": _clip("\n".join(self.lines)),
                "priority": self.priority, "tags": list(self.tags)}


TEST_MESSAGE = Message(
    "Test: Alerts kommen an",
    ("Testnachricht des Fieberthermometers. Echte Alerts melden Ampelwechsel, veraltete Indikatoren "
     "und anhaltende Fehler.",),
    3, ("white_check_mark",),
)


def traffic_light(latest: dict | None, previous: dict | None) -> tuple[dict | None, Message | None]:
    """The level of the newest scored day, reported when it differs from the last reported level."""
    if latest is None:
        return previous, None  # nothing scored yet
    level = latest["level"]
    if previous is not None and previous["level"] == level:
        return previous, None
    name = texts.LEVEL_NAMES[level]
    if previous is None:
        title, priority = f"Alerts aktiv: Ampel {name}", QUIET
    else:
        title = f"Ampel {name} (vorher {texts.LEVEL_NAMES[previous['level']]})"
        priority = RISE_PRIORITY[level] if level > previous["level"] else QUIET
    rules = [texts.rule_text(rule) for rule in latest["active_rules"].split(",") if rule]
    lines = (
        f"Stand {fmt.day(latest['score_date'])}: Stress {fmt.number(latest['stress'])}, "
        f"Fallhöhe {fmt.number(latest['vulnerability'])}, Konfidenz {fmt.number(latest['confidence'], 0)} %",
        *(rules or ["Keine Regel trifft zu."]),
    )
    state = {"level": level, "score_date": latest["score_date"].isoformat()}
    return state, Message(title, lines, priority, (LEVEL_TAGS[level],))


def stale(day_scores: dict[str, dict], previous: dict | None) -> tuple[dict, Message | None]:
    """Indicators of the newest scored day that turned stale, or fresh again, since the last message."""
    now = sorted(indicator_id for indicator_id, row in day_scores.items() if row["status"] == "stale")
    before = previous["indicators"] if previous is not None else []
    new = [indicator_id for indicator_id in now if indicator_id not in before]
    back = [indicator_id for indicator_id in before if indicator_id not in now]
    state = {"indicators": now}
    if not new and not back:
        return state, None
    lines = []
    if new:
        lines += ["Veraltet, zählt deshalb nicht im Score, die Konfidenz sinkt:",
                  *_listed([_described(indicator_id, day_scores[indicator_id]) for indicator_id in new])]
    if back:
        lines += ["Wieder aktuell:", *_listed([_title(indicator_id) for indicator_id in back])]
    if new:
        title = f"Veraltet: {_title(new[0])}" if len(new) == 1 else f"{len(new)} Indikatoren veraltet"
        # the first message after setting up reports the state quietly
        return state, Message(title, tuple(lines), PROBLEM if previous is not None else QUIET, ("warning",))
    title = f"Wieder aktuell: {_title(back[0])}" if len(back) == 1 else f"{len(back)} Indikatoren wieder aktuell"
    return state, Message(title, tuple(lines), QUIET, ("white_check_mark",))


def errors(status: list[dict], previous: dict | None) -> tuple[dict, Message | None]:
    """Sources and worker steps whose error survived the next attempt, and those that recovered since."""
    failing = {
        row["source"]: row["last_error_at"] for row in status
        if row["source"] not in UNWATCHED and row["last_error_at"] is not None
        and (row["last_success_at"] is None or row["last_error_at"] > row["last_success_at"])
    }
    pending = previous["pending"] if previous is not None else {}  # source -> first error seen, not reported
    reported = previous["reported"] if previous is not None else []
    state_pending, state_reported, new = {}, [], []
    for source, error_at in sorted(failing.items()):
        if source in reported:
            state_reported.append(source)
        elif source in pending and error_at > datetime.fromisoformat(pending[source]):
            state_reported.append(source)  # the next attempt failed as well
            new.append(source)
        else:
            state_pending[source] = pending.get(source, error_at.isoformat())
    back = [source for source in reported if source not in failing]
    state = {"pending": state_pending, "reported": state_reported}
    if not new and not back:
        return state, None
    lines = []
    if new:
        lines += ["Fehler auch beim nächsten Versuch, Einzelheiten im Datenstand:",
                  *_listed([f"{_source(source)}: letzter Fehler {fmt.berlin(failing[source])}" for source in new])]
    if back:
        lines += ["Wieder in Ordnung:", *_listed([_source(source) for source in back])]
    if new:
        title = f"Fehler hält an: {_source(new[0])}" if len(new) == 1 else f"Fehler halten an: {len(new)} Quellen"
        return state, Message(title, tuple(lines), PROBLEM, ("warning",))
    title = f"Wieder in Ordnung: {_source(back[0])}" if len(back) == 1 else f"Wieder in Ordnung: {len(back)} Quellen"
    return state, Message(title, tuple(lines), QUIET, ("white_check_mark",))


def run(engine: Engine, send: Callable[[Message], None], *, clock=_utcnow) -> list[str]:
    """Check, send what changed and store it; returns the titles sent. A failed send is logged, recorded
    under "alerts" in source_status and repeated in the next cycle."""
    now = clock()
    with engine.connect() as conn:  # one read transaction: scores and status of the same moment
        states = read_alert_states(conn)
        latest = latest_composite(conn)
        day_scores = indicator_scores_on(conn, latest["score_date"]) if latest else {}
        status = read_status(conn)
    checks = {
        "traffic_light": traffic_light(latest, states.get("traffic_light")),
        "stale": stale(day_scores, states.get("stale")) if latest else (states.get("stale"), None),
        "errors": errors(status, states.get("errors")),
    }
    sent, failures = [], []
    for kind, (state, message) in checks.items():
        if state is None or state == states.get(kind):
            continue
        if message is not None:
            try:
                send(message)
            except FetchError as exc:
                logger.error("Alert nicht gesendet, nächster Versuch im nächsten Takt: %s: %s", message.title, exc)
                failures.append(f"{message.title}: {exc}")
                continue
            sent.append(message.title)
        with engine.begin() as conn:
            write_alert_state(conn, kind, state, now)
    if sent or failures:
        with engine.begin() as conn:
            record_attempt(conn, SOURCE, now)
            if sent:
                record_success(conn, SOURCE, now)
            if failures:
                record_error(conn, SOURCE, now, log.mask(" | ".join(failures)))
    return sent


def sender(client: HttpClient, topic: str) -> Callable[[Message], None]:
    def send(message: Message) -> None:
        client.post_json(URL, message.payload(topic))

    return send


def _clip(text: str) -> str:
    data = text.encode("utf-8")
    if len(data) <= MAX_MESSAGE_BYTES:
        return text
    return data[: MAX_MESSAGE_BYTES - 3].decode("utf-8", errors="ignore") + "…"  # "…" takes 3 bytes


def _listed(items: list[str]) -> list[str]:
    more = len(items) - MAX_LISTED
    return items[:MAX_LISTED] + ([f"und {more} weitere"] if more > 0 else [])


def _title(indicator_id: str) -> str:
    return texts.text(indicator_id).title if texts.has_text(indicator_id) else indicator_id


def _described(indicator_id: str, row: dict) -> str:
    indicator = indicator_catalog().get(indicator_id)
    sources = sorted({texts.SOURCE_NAMES.get(s.source, s.source) for s in indicator.series}) if indicator else []
    origin = f" ({', '.join(sources)})" if sources else ""
    return f"{_title(indicator_id)}{origin}, letzter Wert vom {fmt.day(row['obs_date'])}"


def _source(source: str) -> str:
    return texts.SOURCE_NAMES.get(source, source)


def main(argv: list[str] | None = None) -> int:
    log.setup()
    parser = argparse.ArgumentParser(prog="python -m fever.alerts", description="Alerts über ntfy.sh (M12)")
    parser.add_argument("--test", action="store_true", help="Testnachricht an das Thema aus FEVER_NTFY_TOPIC senden")
    if not parser.parse_args(argv).test:
        parser.print_help()
        return 2
    topic = os.environ.get(TOPIC_VARIABLE)
    if not topic:
        logger.error("Keine Testnachricht gesendet. %s", DISABLED)
        return 2
    try:
        sender(HttpClient(), topic)(TEST_MESSAGE)
    except FetchError as exc:
        logger.error("Testnachricht nicht gesendet: %s", exc)
        return 1
    logger.info("Testnachricht gesendet; sie erscheint in der ntfy-App unter dem abonnierten Thema.")
    return 0


if __name__ == "__main__":
    sys.exit(main())

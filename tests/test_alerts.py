"""Alerts (M12, E-99, E-100): triggers, messages, state and sending, without network."""

import logging
from datetime import date, datetime, timedelta, timezone

import pytest
from sqlalchemy import insert

from fever import alerts, log
from fever.http import FetchError
from fever.store.alerts import read_alert_states
from fever.store.db import make_engine
from fever.store.status import read_status, record_error, record_success
from fever.store.tables import composite_score, indicator_score

NOW = datetime(2026, 9, 30, 20, 0, tzinfo=timezone.utc)
TOPIC = "fever-0123456789abcdef0123456789abcdef01234567"
DAY = date(2026, 9, 29)


def composite(level=0, rules="", stress=36.8, vulnerability=84.8, confidence=89.2, day=DAY) -> dict:
    return {"score_date": day, "level": level, "active_rules": rules, "stress": stress,
            "vulnerability": vulnerability, "confidence": confidence}


# --- traffic light -------------------------------------------------------------------------------


def test_first_message_reports_the_level_quietly():
    state, message = alerts.traffic_light(composite(), None)
    assert state == {"level": 0, "score_date": "2026-09-29"}
    assert message.title == "Alerts aktiv: Ampel Grün" and message.priority == alerts.QUIET
    assert message.lines == ("Stand 29.09.2026: Stress 36,8, Fallhöhe 84,8, Konfidenz 89 %", "Keine Regel trifft zu.")
    assert message.tags == ("green_circle",)


@pytest.mark.parametrize("level, priority", [(1, 3), (2, 4), (3, 5)])
def test_a_rise_is_louder_the_higher_the_level(level, priority):
    rules = {1: "yellow_diffusion", 2: "orange_stress", 3: "red_stress,red_vix_ratio"}[level]
    state, message = alerts.traffic_light(composite(level, rules), {"level": 0, "score_date": "2026-09-28"})
    assert state["level"] == level and message.priority == priority
    assert message.title == f"Ampel {('Grün', 'Gelb', 'Orange', 'Rot')[level]} (vorher Grün)"
    assert all(line.split(":")[0] in ("Stand 29.09.2026", "Gelb", "Orange", "Rot") for line in message.lines)
    if level == 3:
        assert message.lines[1] == "Rot: Stress mindestens 90" and message.lines[2].startswith("Rot: VIX/VIX3M über 1,00")


def test_a_fall_is_quiet_and_an_unchanged_level_sends_nothing():
    previous = {"level": 2, "score_date": "2026-09-28"}
    state, message = alerts.traffic_light(composite(1, "yellow_sos"), previous)
    assert message.title == "Ampel Gelb (vorher Orange)" and message.priority == alerts.QUIET
    assert alerts.traffic_light(composite(2, "orange_stress"), previous) == (previous, None)  # a new day alone is no news
    assert alerts.traffic_light(None, previous) == (previous, None)  # nothing scored


def test_missing_scores_show_a_dash():
    _, message = alerts.traffic_light(composite(stress=None, vulnerability=None), None)
    assert message.lines[0] == "Stand 29.09.2026: Stress –, Fallhöhe –, Konfidenz 89 %"


# --- stale indicators ----------------------------------------------------------------------------


def rows(**statuses):
    return {i: {"status": s, "obs_date": date(2026, 8, 31)} for i, s in statuses.items()}


def test_newly_stale_indicators_are_reported_with_source_and_date():
    state, message = alerts.stale(rows(ebp="stale", vix="ok", nfci="stale"), {"indicators": ["nfci"]})
    assert state == {"indicators": ["ebp", "nfci"]}
    assert message.priority == alerts.PROBLEM and message.tags == ("warning",)
    assert message.title.startswith("Veraltet: ") and "(Federal Reserve Board), letzter Wert vom 31.08.2026" in message.lines[1]
    assert len(message.lines) == 2  # only the new one


def test_first_report_of_stale_indicators_is_quiet_and_recovery_is_quiet():
    _, first = alerts.stale(rows(ebp="stale"), None)
    assert first.priority == alerts.QUIET
    state, back = alerts.stale(rows(ebp="ok", vix="history"), {"indicators": ["ebp"]})
    assert state == {"indicators": []} and back.priority == alerts.QUIET and back.lines[0] == "Wieder aktuell:"
    assert alerts.stale(rows(ebp="stale"), {"indicators": ["ebp"]}) == ({"indicators": ["ebp"]}, None)
    assert alerts.stale(rows(vix="ok"), None) == ({"indicators": []}, None)  # stored quietly as the start


def test_long_lists_are_shortened():
    many = {f"x{i}": {"status": "stale", "obs_date": None} for i in range(12)}
    _, message = alerts.stale(many, {"indicators": []})
    assert message.title == "12 Indikatoren veraltet" and message.lines[-1] == "und 4 weitere"


# --- persistent errors ---------------------------------------------------------------------------


def status(source, success=None, error=None):
    return {"source": source, "last_success_at": success, "last_error_at": error}


def test_an_error_is_reported_only_when_the_next_attempt_fails_too():
    first = NOW - timedelta(hours=1)
    state, message = alerts.errors([status("ecb", NOW - timedelta(days=1), first)], None)
    assert message is None and state == {"pending": {"ecb": first.isoformat()}, "reported": []}
    assert alerts.errors([status("ecb", NOW - timedelta(days=1), first)], state) == (state, None)  # same attempt
    state, message = alerts.errors([status("ecb", NOW - timedelta(days=1), NOW)], state)
    assert state == {"pending": {}, "reported": ["ecb"]}
    assert message.title == "Fehler hält an: EZB" and message.priority == alerts.PROBLEM
    assert message.lines[1] == "EZB: letzter Fehler 30.09.2026, 22:00 MESZ"
    assert alerts.errors([status("ecb", NOW - timedelta(days=1), NOW + timedelta(hours=1))], state) == (state, None)


def test_recovery_of_a_reported_error_is_quiet_and_a_pending_one_is_forgotten():
    previous = {"pending": {"cfe": NOW.isoformat()}, "reported": ["scoring"]}
    rows_ = [status("scoring", NOW + timedelta(minutes=15), NOW), status("cfe", NOW + timedelta(hours=1), NOW)]
    state, message = alerts.errors(rows_, previous)
    assert state == {"pending": {}, "reported": []}
    assert message.title == "Wieder in Ordnung: Scoring (Berechnung im Worker)" and message.priority == alerts.QUIET


def test_dropped_values_and_the_alerts_own_errors_are_no_failure():
    same = status("fred", NOW, NOW)  # values outside the bounds: success and error in one attempt (E-15)
    own = status("alerts", None, NOW)  # a failing send cannot be reported by a send
    assert alerts.errors([same, own], None) == ({"pending": {}, "reported": []}, None)


# --- message format ------------------------------------------------------------------------------


def test_payload_is_ntfy_json_and_stays_below_the_size_limit():
    message = alerts.Message("Ampel Rot (vorher Gelb)", ("ä" * 5000,), 5, ("red_circle",))
    payload = message.payload(TOPIC)
    assert set(payload) == {"topic", "title", "message", "priority", "tags"} and payload["topic"] == TOPIC
    assert payload["priority"] == 5 and payload["tags"] == ["red_circle"]
    assert len(payload["message"].encode("utf-8")) <= alerts.MAX_MESSAGE_BYTES and payload["message"].endswith("…")


# --- run: state, restart, failed send ------------------------------------------------------------


@pytest.fixture
def engine(migrated_dir):
    engine = make_engine(migrated_dir)
    with engine.begin() as conn:
        conn.execute(insert(composite_score), [
            {"score_date": DAY, "confidence": 89.2, "level": 0, "active_rules": "", "stress": 36.8,
             "vulnerability": 84.8, "computed_at": NOW, "config_hash": "x"}])
        conn.execute(insert(indicator_score), [
            {"score_date": DAY, "indicator_id": "ebp", "status": "stale", "obs_date": date(2026, 8, 31)},
            {"score_date": DAY, "indicator_id": "vix", "status": "ok", "obs_date": DAY}])
    yield engine
    engine.dispose()


class Sender:
    def __init__(self, fail=False):
        self.fail, self.messages = fail, []

    def __call__(self, message):
        if self.fail:
            raise FetchError("https://ntfy.sh/: HTTP 503")
        self.messages.append(message)


def test_run_reports_once_and_a_restart_repeats_nothing(engine, migrated_dir):
    send = Sender()
    assert alerts.run(engine, send, clock=lambda: NOW) == ["Alerts aktiv: Ampel Grün", "Veraltet: Excess Bond Premium"]
    assert [m.priority for m in send.messages] == [alerts.QUIET, alerts.QUIET]
    restarted = make_engine(migrated_dir)
    assert alerts.run(restarted, Sender(), clock=lambda: NOW + timedelta(minutes=15)) == []
    with restarted.connect() as conn:
        states = read_alert_states(conn)
        sent = {row["source"]: row for row in read_status(conn)}["alerts"]
    restarted.dispose()
    assert states["traffic_light"] == {"level": 0, "score_date": "2026-09-29"}
    assert states["stale"] == {"indicators": ["ebp"]} and states["errors"] == {"pending": {}, "reported": []}
    assert sent["last_success_at"] == NOW and sent["last_error_at"] is None


def test_a_failed_send_is_recorded_and_repeated_in_the_next_cycle(engine, caplog):
    assert alerts.run(engine, Sender(fail=True), clock=lambda: NOW) == []
    with engine.connect() as conn:
        assert "traffic_light" not in read_alert_states(conn)
        sent = {row["source"]: row for row in read_status(conn)}["alerts"]
    assert sent["last_error_at"] == NOW and "HTTP 503" in sent["last_error_message"]
    assert "Alert nicht gesendet" in caplog.text
    later = NOW + timedelta(minutes=15)
    assert alerts.run(engine, Sender(), clock=lambda: later)[0] == "Alerts aktiv: Ampel Grün"


def test_run_follows_a_level_change_and_an_error_that_persists(engine):
    alerts.run(engine, Sender(), clock=lambda: NOW)
    with engine.begin() as conn:
        conn.execute(insert(composite_score), [
            {"score_date": DAY + timedelta(days=1), "confidence": 90.0, "level": 2, "active_rules": "orange_stress",
             "stress": 81.0, "vulnerability": 84.0, "computed_at": NOW, "config_hash": "x"}])
        record_success(conn, "ecb", NOW - timedelta(days=1))
        record_error(conn, "ecb", NOW, "ecb_ciss: HTTP 500")
    send = Sender()
    assert alerts.run(engine, send, clock=lambda: NOW + timedelta(minutes=15)) == [
        "Ampel Orange (vorher Grün)", "Wieder aktuell: Excess Bond Premium"]  # no ebp row on the new day
    assert send.messages[0].priority == 4 and send.messages[0].lines[1] == "Orange: Stress mindestens 80"
    with engine.begin() as conn:
        record_error(conn, "ecb", NOW + timedelta(hours=1), "ecb_ciss: HTTP 500")
    assert alerts.run(engine, Sender(), clock=lambda: NOW + timedelta(hours=1, minutes=15)) == ["Fehler hält an: EZB"]


# --- test command --------------------------------------------------------------------------------


class FakeClient:
    posts = []
    fail = False

    def post_json(self, url, payload):
        if self.fail:
            raise FetchError(f"{url}: HTTP 429")
        self.posts.append((url, payload))


def test_test_command_sends_and_never_logs_the_topic(monkeypatch, capsys):
    monkeypatch.setenv("FEVER_NTFY_TOPIC", TOPIC)
    monkeypatch.setattr(alerts, "HttpClient", FakeClient)
    FakeClient.posts, FakeClient.fail = [], False
    assert alerts.main(["--test"]) == 0
    url, payload = FakeClient.posts[0]
    assert url == "https://ntfy.sh/" and payload["topic"] == TOPIC and payload["title"] == "Test: Alerts kommen an"
    FakeClient.fail = True
    assert alerts.main(["--test"]) == 1
    logging.getLogger("fever.alerts").error("Thema %s", TOPIC)
    out = capsys.readouterr()
    assert TOPIC not in out.out + out.err and "Testnachricht nicht gesendet" in out.out


def test_test_command_without_topic_or_flag(monkeypatch, capsys):
    monkeypatch.delenv("FEVER_NTFY_TOPIC", raising=False)
    assert alerts.main(["--test"]) == 2 and "FEVER_NTFY_TOPIC ist nicht gesetzt" in capsys.readouterr().out
    assert alerts.main([]) == 2


def test_the_topic_is_a_masked_secret(monkeypatch):
    monkeypatch.setenv("FEVER_NTFY_TOPIC", TOPIC)
    assert log.mask(f"POST https://ntfy.sh/{TOPIC}") == "POST https://ntfy.sh/***"

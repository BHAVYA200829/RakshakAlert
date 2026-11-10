"""Simulated-SMS fallback layer (Phase 2).

Real SMS is NOT sent by this prototype. The default provider is
SIMULATED: every message is written to the delivery / sms_log tables
with status SIMULATED and clearly labelled as such.

A MSG91 / Twilio-shaped provider is available as a *stub only*: it is
selected only when SMS_PROVIDER=msg91|twilio AND the matching API key
env var is set, and even then it does NOT make any HTTP call - it logs
the message as PROVIDER_STUB (not sent) so a demo can never pretend a
real SMS went out. Wiring a real gateway means replacing
RealProviderStub.send() with an actual HTTPS call to that provider.
"""
import os

PROVIDER = os.environ.get("SMS_PROVIDER", "simulated").lower()


def provider_name():
    if PROVIDER in ("msg91", "twilio") and (
        os.environ.get("MSG91_API_KEY") or os.environ.get("TWILIO_API_KEY")
    ):
        return PROVIDER
    return "simulated"


def send(phone, message):
    """Send one SMS. Returns (status, provider).

    status is SIMULATED by default, PROVIDER_STUB when a real provider
    is configured but not wired (no HTTP call is ever made here).
    """
    provider = provider_name()
    if provider == "simulated":
        return "SIMULATED", "simulated"
    return "PROVIDER_STUB", provider


def send_to_citizens(db, alert_id, citizens, message, now):
    """Log one delivery row per citizen for an alert.

    citizens: rows with id and phone. Returns (count, status, provider).
    The existing `deliveries` table keeps working exactly as in Phase 1;
    `sms_log` is the provider-level audit trail.
    """
    count = 0
    status = None
    provider = None
    for c in citizens:
        # Rows may be sqlite3.Row (Flask requests) or plain tuples
        # (init_db seeding, where the query is SELECT id, phone).
        cid = c["id"] if hasattr(c, "keys") else c[0]
        phone = c["phone"] if hasattr(c, "keys") else c[1]
        status, provider = send(phone, message)
        db.execute(
            "INSERT INTO deliveries (alert_id, citizen_id, phone, status,"
            " created_at) VALUES (?, ?, ?, ?, ?)",
            (alert_id, cid, phone, status, now),
        )
        db.execute(
            "INSERT INTO sms_log (phone, message, status, provider,"
            " related_type, related_id, created_at)"
            " VALUES (?, ?, ?, ?, 'alert', ?, ?)",
            (phone, message, status, provider, alert_id, now),
        )
        count += 1
    return count, (status or "SIMULATED"), (provider or "simulated")


def log_single(db, phone, message, related_type, related_id, now):
    """Log a single SMS (e.g. report status update). Returns status."""
    status, provider = send(phone, message)
    db.execute(
        "INSERT INTO sms_log (phone, message, status, provider,"
        " related_type, related_id, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
        (phone, message, status, provider, related_type, related_id, now),
    )
    return status

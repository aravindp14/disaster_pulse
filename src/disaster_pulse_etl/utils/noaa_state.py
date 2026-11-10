import json
import os
from datetime import date
from pathlib import Path

STATE_FILE = Path("data/state/noaa_pending_dates.json")

def load_pending_dates() -> list[str]:
    """
    Read pending NOAA observation dates.
    """
    
    if not STATE_FILE.exists():
        return []

    with STATE_FILE.open("r", encoding="utf-8") as file:
        data = json.load(file)

    dates = data["pending_dates"]

    if not isinstance(dates, list):
        raise ValueError("Invalid NOAA pending date state.")

    for value in dates:
        date.fromisoformat(value)

    return sorted(set(dates))


def save_pending_dates(dates: list[str]) -> None:
    """
    Atomically replace pending-date file.
    """

    STATE_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    payload = {
        "pending_dates": sorted(set(dates))
    }

    temporary_file = STATE_FILE.with_suffix(".tmp")

    with temporary_file.open(
        "w",
        encoding="utf-8"
    ) as file:
        json.dump(payload, file, indent=2)

    os.replace(temporary_file, STATE_FILE)

def add_pending_date(observation_date: str) -> None:
    """
    Register a date that needs processing.
    """

    date.fromisoformat(observation_date)

    dates = load_pending_dates()

    if observation_date not in dates:
        dates.append(observation_date)
        save_pending_dates(dates)

def remove_pending_date(observation_date: str) -> None:
    """
    Remove a date from the pending list.
    """

    dates = load_pending_dates()

    if observation_date in dates:
        dates.remove(observation_date)
        save_pending_dates(dates)
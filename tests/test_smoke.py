"""Live smoke tests against MARTA's public APIs.

These hit the real endpoints: rail tests are skipped when no API key is
configured, bus tests need no key.
"""

import pytest

from marta_mcp.config import MartaConfigError, get_api_key
from marta_mcp.server import (
    get_bus_positions,
    get_bus_trip_updates,
    get_rail_arrivals,
    list_rail_stations,
)
from marta_mcp.stations import match_station


def _has_api_key() -> bool:
    try:
        get_api_key()
        return True
    except MartaConfigError:
        return False


def test_match_station():
    assert match_station("five points") == ["FIVE POINTS STATION"]
    assert match_station("midtown") == ["MIDTOWN STATION"]
    assert "EAST LAKE STATION" in match_station("lake")
    assert match_station("hogwarts") == []


def test_list_rail_stations():
    stations = list_rail_stations()
    assert len(stations) == 38
    assert "FIVE POINTS STATION" in stations


@pytest.mark.skipif(not _has_api_key(), reason="no MARTA API key configured")
@pytest.mark.asyncio
async def test_rail_arrivals_live():
    result = await get_rail_arrivals()
    assert "arrivals" in result
    if result["count"]:  # trains may not run overnight
        first = result["arrivals"][0]
        assert "STATION" in first
        assert "WAITING_TIME" in first


@pytest.mark.skipif(not _has_api_key(), reason="no MARTA API key configured")
@pytest.mark.asyncio
async def test_rail_arrivals_station_filter_live():
    result = await get_rail_arrivals(station="Five Points")
    assert "error" not in result
    for arrival in result["arrivals"]:
        assert arrival["STATION"] == "FIVE POINTS STATION"


@pytest.mark.asyncio
async def test_bus_positions_live():
    result = await get_bus_positions(limit=5)
    assert result["count"] <= 5
    assert "vehicles" in result


@pytest.mark.asyncio
async def test_bus_trip_updates_live():
    result = await get_bus_trip_updates(limit=3, stops_per_trip=2)
    assert result["count"] <= 3
    for trip in result["trips"]:
        assert len(trip["stop_updates"]) <= 2


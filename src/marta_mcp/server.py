"""MARTA MCP server — real-time rail arrivals and bus positions for Atlanta.

Data sources:
- Rail real-time RESTful API (requires an API key, see config.py)
- Bus GTFS-realtime protobuf feeds (no key required)
"""

from __future__ import annotations

from typing import Any

import httpx
from fastmcp import FastMCP
from google.transit import gtfs_realtime_pb2

from .config import get_api_key
from .stations import STATIONS, match_station

RAIL_URL = (
    "https://developerservices.itsmarta.com:18096"
    "/itsmarta/railrealtimearrivals/developerservices/traindata"
)
BUS_POSITIONS_URL = (
    "https://gtfs-rt.itsmarta.com/TMGTFSRealTimeWebService"
    "/vehicle/vehiclepositions.pb"
)
BUS_TRIP_UPDATES_URL = (
    "https://gtfs-rt.itsmarta.com/TMGTFSRealTimeWebService"
    "/tripupdate/tripupdates.pb"
)
TIMEOUT = 30.0

mcp = FastMCP(
    "MARTA Transit",
    instructions=(
        "Real-time Atlanta MARTA transit data. Rail tools cover the four train "
        "lines (RED, GOLD, BLUE, GREEN); bus tools expose live GTFS-realtime "
        "vehicle positions and trip updates."
    ),
)


async def _fetch_rail() -> list[dict[str, Any]]:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(RAIL_URL, params={"apiKey": get_api_key()})
        resp.raise_for_status()
        return resp.json()


async def _fetch_feed(url: str) -> gtfs_realtime_pb2.FeedMessage:
    async with httpx.AsyncClient(timeout=TIMEOUT) as client:
        resp = await client.get(url)
        resp.raise_for_status()
    feed = gtfs_realtime_pb2.FeedMessage()
    feed.ParseFromString(resp.content)
    return feed


@mcp.tool()
async def get_rail_arrivals(
    station: str | None = None,
    line: str | None = None,
    direction: str | None = None,
) -> dict[str, Any]:
    """Get real-time MARTA train arrival predictions.

    Args:
        station: Optional station name filter, e.g. "Five Points" or
            "Midtown". Partial names match; use list_rail_stations for the
            full list.
        line: Optional line filter: RED, GOLD, BLUE, or GREEN.
        direction: Optional direction filter: N, S, E, or W.

    Returns arrivals with station, line, direction, destination, waiting
    time, predicted arrival clock time, and train position (lat/lon).
    """
    arrivals = await _fetch_rail()

    if station:
        matches = match_station(station)
        if not matches:
            return {
                "error": f"No station matching '{station}'.",
                "hint": "Use list_rail_stations to see valid names.",
            }
        wanted = set(matches)
        arrivals = [a for a in arrivals if a.get("STATION") in wanted]
    if line:
        arrivals = [a for a in arrivals if a.get("LINE", "").upper() == line.upper()]
    if direction:
        arrivals = [
            a for a in arrivals if a.get("DIRECTION", "").upper() == direction.upper()
        ]

    arrivals.sort(key=lambda a: int(a.get("WAITING_SECONDS", "0") or 0))
    return {"count": len(arrivals), "arrivals": arrivals}


@mcp.tool()
def list_rail_stations() -> list[str]:
    """List all MARTA rail station names accepted by get_rail_arrivals."""
    return STATIONS


@mcp.tool()
async def get_bus_positions(
    route: str | None = None,
    limit: int = 100,
) -> dict[str, Any]:
    """Get live MARTA bus vehicle positions from the GTFS-realtime feed.

    Args:
        route: Optional GTFS route_id filter (exact match).
        limit: Maximum number of vehicles to return (default 100).

    Returns vehicle id, route, trip, position (lat/lon), bearing, speed,
    and timestamp for each active bus.
    """
    feed = await _fetch_feed(BUS_POSITIONS_URL)

    vehicles = []
    for entity in feed.entity:
        if not entity.HasField("vehicle"):
            continue
        v = entity.vehicle
        if route and v.trip.route_id != route:
            continue
        vehicles.append(
            {
                "vehicle_id": v.vehicle.id,
                "label": v.vehicle.label,
                "route_id": v.trip.route_id,
                "trip_id": v.trip.trip_id,
                "latitude": round(v.position.latitude, 6),
                "longitude": round(v.position.longitude, 6),
                "bearing": v.position.bearing,
                "speed_mps": round(v.position.speed, 2),
                "timestamp": v.timestamp,
            }
        )
        if len(vehicles) >= limit:
            break

    return {
        "feed_timestamp": feed.header.timestamp,
        "count": len(vehicles),
        "vehicles": vehicles,
    }


@mcp.tool()
async def get_bus_trip_updates(
    route: str | None = None,
    stop_id: str | None = None,
    limit: int = 25,
    stops_per_trip: int = 5,
) -> dict[str, Any]:
    """Get live MARTA bus arrival/departure predictions (GTFS-realtime trip updates).

    Args:
        route: Optional GTFS route_id filter (exact match).
        stop_id: Optional GTFS stop_id filter — only trips serving this stop
            are returned, and only that stop's prediction is included.
        limit: Maximum number of trips to return (default 25).
        stops_per_trip: Upcoming stop predictions to include per trip
            (default 5; ignored when stop_id is set).

    Returns per-trip route, vehicle, and predicted arrival/departure times
    (unix timestamps) with delays in seconds.
    """
    feed = await _fetch_feed(BUS_TRIP_UPDATES_URL)

    trips = []
    for entity in feed.entity:
        if not entity.HasField("trip_update"):
            continue
        tu = entity.trip_update
        if route and tu.trip.route_id != route:
            continue

        stop_updates = []
        for stu in tu.stop_time_update:
            if stop_id and stu.stop_id != stop_id:
                continue
            stop_updates.append(
                {
                    "stop_id": stu.stop_id,
                    "stop_sequence": stu.stop_sequence,
                    "arrival_time": stu.arrival.time if stu.HasField("arrival") else None,
                    "arrival_delay_s": stu.arrival.delay if stu.HasField("arrival") else None,
                    "departure_time": stu.departure.time if stu.HasField("departure") else None,
                }
            )
            if not stop_id and len(stop_updates) >= stops_per_trip:
                break

        if stop_id and not stop_updates:
            continue

        trips.append(
            {
                "trip_id": tu.trip.trip_id,
                "route_id": tu.trip.route_id,
                "vehicle_id": tu.vehicle.id,
                "stop_updates": stop_updates,
            }
        )
        if len(trips) >= limit:
            break

    return {
        "feed_timestamp": feed.header.timestamp,
        "count": len(trips),
        "trips": trips,
    }


def main() -> None:
    mcp.run()


if __name__ == "__main__":
    main()

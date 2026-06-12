"""Canonical MARTA rail station names as returned by the rail real-time API."""

STATIONS = [
    "AIRPORT STATION",
    "ARTS CENTER STATION",
    "ASHBY STATION",
    "AVONDALE STATION",
    "BANKHEAD STATION",
    "BROOKHAVEN STATION",
    "BUCKHEAD STATION",
    "CHAMBLEE STATION",
    "CIVIC CENTER STATION",
    "COLLEGE PARK STATION",
    "DECATUR STATION",
    "DORAVILLE STATION",
    "DUNWOODY STATION",
    "EAST LAKE STATION",
    "EAST POINT STATION",
    "EDGEWOOD CANDLER PARK STATION",
    "FIVE POINTS STATION",
    "GARNETT STATION",
    "GEORGIA STATE STATION",
    "HAMILTON E HOLMES STATION",
    "INDIAN CREEK STATION",
    "INMAN PARK STATION",
    "KENSINGTON STATION",
    "KING MEMORIAL STATION",
    "LAKEWOOD STATION",
    "LENOX STATION",
    "LINDBERGH STATION",
    "MEDICAL CENTER STATION",
    "MIDTOWN STATION",
    "NORTH AVE STATION",
    "NORTH SPRINGS STATION",
    "OAKLAND CITY STATION",
    "OMNI DOME STATION",
    "PEACHTREE CENTER STATION",
    "SANDY SPRINGS STATION",
    "VINE CITY STATION",
    "WEST END STATION",
    "WEST LAKE STATION",
]


def match_station(query: str) -> list[str]:
    """Return canonical station names whose name contains the query."""
    q = query.strip().upper().replace("/", " ").replace("-", " ")
    if not q.endswith("STATION"):
        candidates = [s for s in STATIONS if q in s]
    else:
        candidates = [s for s in STATIONS if q == s or q in s]
    return candidates

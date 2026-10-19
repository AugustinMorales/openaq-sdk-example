"""
Daily average PM2.5 for Mueang Chaiyaphum, Thailand (2025), as a line chart.

Based on the official guide:
https://python.openaq.org/guides/querying-measurements/

Unlike the guide, which uses the first location found, this script picks the
location whose reporting period best overlaps the requested date range, since
some stations have stopped reporting.

Requires the OPENAQ_API_KEY environment variable to be set.
Usage: python pm25_chart.py
"""
from datetime import date, datetime

import matplotlib.pyplot as plt
import pandas as pd
from openaq import OpenAQ

CITY = "Mueang Chaiyaphum, Thailand"
COORDINATES = (15.81207, 102.02316)  # (latitude, longitude), from the guide
RADIUS_M = 10_000                    # search radius in meters (10 km)
PM25_PARAMETER_ID = 2                # OpenAQ parameter ID for PM2.5
DATE_FROM = date(2025, 1, 1)
DATE_TO = date(2025, 12, 31)
OUTPUT_FILE = "pm25_chaiyaphum_2025.png"


def to_date(dt_obj):
    """Convert an OpenAQ datetime object (with .utc string) to a date, or None."""
    if dt_obj is None or not dt_obj.utc:
        return None
    return datetime.fromisoformat(dt_obj.utc.replace("Z", "+00:00")).date()


def overlap_days(loc):
    """Days the location's reporting period overlaps DATE_FROM..DATE_TO."""
    first, last = to_date(loc.datetime_first), to_date(loc.datetime_last)
    if first is None or last is None:
        return 0
    start, end = max(first, DATE_FROM), min(last, DATE_TO)
    return max((end - start).days + 1, 0)


with OpenAQ() as client:  # reads OPENAQ_API_KEY; closes automatically
    # 1. Find PM2.5 locations near the city and pick the best-covering one
    locations = client.locations.list(
        parameters_id=PM25_PARAMETER_ID,
        coordinates=COORDINATES,
        radius=RADIUS_M,
        limit=1000,
    )
    candidates = [loc for loc in locations.results if overlap_days(loc) > 0]
    if not candidates:
        raise SystemExit(
            f"No PM2.5 locations within {RADIUS_M} m of {CITY} "
            f"reported data between {DATE_FROM} and {DATE_TO}."
        )
    location = max(candidates, key=overlap_days)
    print(f"Location: {location.name} (ID {location.id}), "
          f"{len(locations.results)} candidates checked")

    # 2. Find the PM2.5 sensor at that location
    sensors = client.locations.sensors(location.id)
    pm25_sensor = next((s for s in sensors.results if "pm25" in s.name), None)
    if pm25_sensor is None:
        raise SystemExit(f"Location {location.id} has no PM2.5 sensor.")
    print(f"Sensor: {pm25_sensor.name} (ID {pm25_sensor.id})")

    # 3. Get daily averages (up to 365 rows; default page size is 1,000)
    response = client.measurements.list(
        pm25_sensor.id,
        data="days",
        date_from=DATE_FROM,
        date_to=DATE_TO,
    )

if not response.results:
    raise SystemExit("No PM2.5 measurements returned for that date range.")

# 4. Build a table of date + value, dropping any missing values
df = pd.DataFrame(
    {
        "date": [pd.to_datetime(m.period.datetime_from.local[:10]) for m in response.results],
        "pm25": [m.value for m in response.results],
    }
).dropna().sort_values("date")
units = response.results[0].parameter.units

print(f"Days with data: {len(df)} of {(DATE_TO - DATE_FROM).days + 1}")
print(df["pm25"].describe().round(1))

# 5. Chart it
fig, ax = plt.subplots(figsize=(11, 5))
ax.plot(df["date"], df["pm25"], linewidth=1.2, label="Daily average PM2.5")
ax.axhline(15, color="red", linestyle="--", linewidth=1,
           label="WHO 24-hour guideline (15 µg/m³)")
ax.set_title(f"Daily average PM2.5, {location.name}, {CITY} ({DATE_FROM.year})")
ax.set_xlabel("Date")
ax.set_ylabel(f"PM2.5 ({units})")
ax.legend()
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(OUTPUT_FILE, dpi=150)
print(f"Chart saved to {OUTPUT_FILE}")

[README.md](https://github.com/user-attachments/files/33689683/README.md)
# OpenAQ PM2.5 SDK Example

A small Python example that uses the [OpenAQ Python SDK](https://python.openaq.org/) to retrieve daily average PM2.5 data for one city and plot it as a chart.

The default query answers the question from OpenAQ's official guide: *What was the daily average PM2.5 in Mueang Chaiyaphum, Thailand for 2025?*

## Requirements

- Python 3.11 or newer
- A free OpenAQ API key ([register here](https://explore.openaq.org/register); the key is on your [account settings](https://explore.openaq.org/account) page)
- Packages listed in `requirements.txt`: `openaq`, `pandas`, `matplotlib`

## Setup

### Windows (PowerShell)

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
$env:OPENAQ_API_KEY = "your-key-here"
```

If activation fails with "running scripts is disabled on this system", run this once, then activate again:

```powershell
Set-ExecutionPolicy -Scope CurrentUser RemoteSigned
```

### macOS / Linux

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
export OPENAQ_API_KEY="your-key-here"
```

The API key is read from the `OPENAQ_API_KEY` environment variable and is never stored in the code. The variable only lasts for the current terminal session, so set it again in each new terminal.

## Usage

Optional: confirm your installation and API key work by running the official quick-start check, which should print `Del Norte`:

```
python quick_start.py
```

Then generate the chart:

```
python pm25_chart.py
```

To change the city, search area, or year, edit the constants at the top of `pm25_chart.py` (`CITY`, `COORDINATES`, `RADIUS_M`, `DATE_FROM`, `DATE_TO`, `OUTPUT_FILE`).

## Output

The script prints:

- The selected monitoring location and how many candidates were checked
- The PM2.5 sensor used
- How many days in the date range had data
- Summary statistics (count, mean, standard deviation, min, quartiles, max)

It saves a line chart to `pm25_chaiyaphum_2025.png` showing daily average PM2.5 in µg/m³, with a dashed reference line at the WHO 24-hour guideline of 15 µg/m³.

## How it works

The script follows OpenAQ's top-down workflow: **location → sensor → measurements**.

1. `client.locations.list()` finds monitoring locations within 10 km of the city that measure PM2.5 (parameter ID 2).
2. `client.locations.sensors()` finds the PM2.5 sensor at the chosen location.
3. `client.measurements.list()` with `data="days"` retrieves pre-computed daily averages for the date range.

## How missing data is handled

The script stops with a clear message instead of crashing or drawing an empty chart when:

- No PM2.5 locations are found near the city
- No nearby location reported data during the requested date range
- The selected location has no PM2.5 sensor
- No measurements are returned for the date range

Days with missing values are dropped before charting, and the script reports how many days had data so gaps are visible.

## Improvements over the official example

- **Location selection by date coverage.** The official guide uses the first location returned. For its own example, that location (Chaiyaphum City Hall) stopped reporting in June 2023, so following the guide returns no 2025 data. This script instead picks the location whose reporting period best overlaps the requested dates.
- **Search radius matches the description.** The guide describes a 10 km search but its code uses `radius=1000` (1 km). This script uses 10,000 m.
- **API key from environment.** The key is read from `OPENAQ_API_KEY` rather than written into the code.
- **Empty-result handling** at every step (see above).
- **Charting** with units, a guideline reference line, and the station name.

## Files

| File | Purpose |
| --- | --- |
| `pm25_chart.py` | Main script: retrieves PM2.5 data and saves the chart |
| `quick_start.py` | Official quick-start check for installation and API key |
| `list_locations.py` | Diagnostic: lists nearby PM2.5 locations and their reporting periods |
| `requirements.txt` | Python dependencies |

## OpenAQ documentation

- [Quick start](https://python.openaq.org/getting-started/quick-start/)
- [Client and API key](https://python.openaq.org/getting-started/client/)
- [Querying measurements guide](https://python.openaq.org/guides/querying-measurements/)
- [Measurements resource](https://python.openaq.org/resources/measurements/)
- [Paging results](https://python.openaq.org/guides/paging-results/)

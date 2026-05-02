# Aircraft Geofence Alert

A small Python portfolio project that demonstrates how public aircraft state data can be transformed into a privacy-aware geofencing and alerting workflow.

The script monitors a configurable public point of interest, retrieves nearby aircraft state data from the OpenSky Network API, estimates whether an aircraft may pass within a selected radius, and optionally sends a notification through ntfy.

This is an educational OSINT / data automation project, not an operational aviation tracking system.

## What it does

- Reads aircraft state data from a public API
- Monitors a configurable latitude/longitude point
- Filters aircraft by distance and altitude
- Estimates closest approach using current speed and heading
- Prints structured alert information in the terminal
- Optionally sends ntfy notifications
- Keeps private configuration outside the source code

## Skills demonstrated

- Python scripting
- Public API usage
- Geospatial filtering
- Basic trajectory estimation
- Environment-based configuration
- Notification automation
- Privacy-aware OSINT documentation
- Defensive data monitoring workflow design

## Project structure

    .
    ├── aircraft_watch.py   # Main monitoring script
    ├── run.sh              # Safe local launcher
    ├── .env.example        # Example configuration template
    ├── .gitignore          # Keeps local secrets out of git
    └── README.md           # Project documentation

## Setup

Clone the repository:

    git clone git@github.com:G-BUZZ/aircraft-geofence-alert.git
    cd aircraft-geofence-alert

Create a local environment file:

    cp .env.example .env

Edit `.env` and configure a public or generic point of interest:

    POINT_LAT=0.0000
    POINT_LON=0.0000
    FETCH_RADIUS_KM=120.0
    ALERT_RADIUS_KM=3.0
    LOOKAHEAD_MINUTES=10.0

Optional ntfy notification topic:

    NTFY_TOPIC=your-private-random-ntfy-topic-here

Do not commit your real `.env` file.

## Usage

Run the script with:

    ./run.sh

Or export variables manually:

    POINT_LAT=0.0000 POINT_LON=0.0000 ALERT_RADIUS_KM=3 python3 aircraft_watch.py

## Configuration

| Variable | Description | Example |
|---|---|---|
| `POINT_LAT` | Latitude of the monitored point | `0.0000` |
| `POINT_LON` | Longitude of the monitored point | `0.0000` |
| `FETCH_RADIUS_KM` | Radius used to fetch aircraft data | `120.0` |
| `ALERT_RADIUS_KM` | Alert radius around the monitored point | `3.0` |
| `LOOKAHEAD_MINUTES` | Linear prediction window | `10.0` |
| `MIN_ALTITUDE_M` | Minimum altitude filter | `0.0` |
| `MAX_ALTITUDE_M` | Maximum altitude filter | `12000.0` |
| `NTFY_TOPIC` | Optional ntfy topic for notifications | `your-private-random-topic` |

## Privacy and safety

This project is designed for educational and portfolio purposes only.

Use only public or generic points of interest. Do not publish private home coordinates, workplace coordinates, notification topics, screenshots containing sensitive configuration values, or real-time alerts linked to private locations.

The notification topic is read from the `NTFY_TOPIC` environment variable, so no private topic is stored in the source code. If using ntfy, choose a long random topic and treat it like a secret.

## Limitations

Closest-approach estimates are based only on the currently reported position, speed, and heading. They are simplified linear estimates and do not account for flight plans, air traffic control instructions, turns, altitude changes, signal delay, missing data, incomplete data, or delayed API updates.

This project should not be used for aviation safety, operational tracking, surveillance, targeting, or decision-making.

## Portfolio note

This repository is intended to demonstrate a small defensive OSINT and data automation workflow. It focuses on responsible use of public data, local configuration hygiene, reproducibility, and privacy-aware documentation.

## License

This project is released under the MIT License.

## API Usage and Terms

This project uses public aircraft state data for educational and portfolio purposes only.

Users are responsible for respecting the terms of the data providers they use, including any rate limits, attribution requirements, non-commercial restrictions, and limitations on operational use.

This project is not intended for commercial use, aviation decision-making, real-time operational tracking, or safety-critical monitoring.

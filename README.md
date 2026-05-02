# Aircraft Geofence Alert

A small Python-based aircraft geofencing monitor.

The tool queries public live aircraft state data around a configurable geographic point, estimates the closest point of approach using current speed and heading, and sends an optional notification when an aircraft is predicted to enter the selected alert radius.

## Features

- Queries public aircraft state vectors from OpenSky Network
- Monitors a configurable geographic point
- Uses a circular geofence alert radius
- Estimates closest point of approach using current velocity and heading
- Supports optional ntfy notifications
- Keeps private notification topics outside the source code

## Example use case

The script can be used to monitor whether an aircraft is predicted to pass within a selected radius of a public point of interest.

This project is intended as a defensive OSINT / data automation portfolio project.

## Configuration

Copy the example environment file:

    cp .env.example .env.local

Then customize the local values:

    POINT_LAT=38.1157
    POINT_LON=13.3615
    FETCH_RADIUS_KM=120
    ALERT_RADIUS_KM=3
    LOOKAHEAD_MINUTES=10
    CHECK_EVERY_SECONDS=30
    NTFY_TOPIC=your-private-ntfy-topic-here

Do not publish your real .env.local file.

## Run

    ./run.sh

Or run directly with temporary values:

    POINT_LAT=38.1157 POINT_LON=13.3615 ALERT_RADIUS_KM=3 python3 aircraft_watch.py

## Notification layer

Notifications are optional and handled through ntfy.

The notification topic is read from the NTFY_TOPIC environment variable, so no private topic or token is stored in the code.

## Limitations

The trajectory prediction is linear and based on current speed and heading. Aircraft may change course, altitude, speed, or disappear from public feeds. The output should be treated as an estimate, not as authoritative aviation tracking.

## Data source

This project uses public aircraft state data from OpenSky Network.

## Privacy note

Do not use private home coordinates in public screenshots, examples, or commits. Use public or generic points of interest for portfolio publication.

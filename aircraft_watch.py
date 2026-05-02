import json
import math
import os
import time
import urllib.request
from datetime import datetime, timezone

# Punto da monitorare.
# Per portfolio usa un punto pubblico/generico, non coordinate personali sensibili.
POINT_LAT = float(os.environ.get("POINT_LAT", "38.1157"))
POINT_LON = float(os.environ.get("POINT_LON", "13.3615"))

# Quanto lontano scaricare aerei da OpenSky.
FETCH_RADIUS_KM = float(os.environ.get("FETCH_RADIUS_KM", "120.0"))

# Quanto vicino deve passare l'aereo per generare alert.
ALERT_RADIUS_KM = float(os.environ.get("ALERT_RADIUS_KM", "3.0"))

# Finestra di previsione.
LOOKAHEAD_MINUTES = float(os.environ.get("LOOKAHEAD_MINUTES", "10.0"))

# Ogni quanti secondi controllare.
CHECK_EVERY_SECONDS = int(os.environ.get("CHECK_EVERY_SECONDS", "30"))

# Evita di ripetere lo stesso alert troppe volte per lo stesso aereo.
ALERT_COOLDOWN_SECONDS = 5 * 60

# Notifiche ntfy.
# Non hardcodiamo il topic nel codice: lo leggiamo da variabile d'ambiente.
NTFY_TOPIC = os.environ.get("NTFY_TOPIC", "").strip()
NTFY_ENABLED = bool(NTFY_TOPIC)
NTFY_URL = f"https://ntfy.sh/{NTFY_TOPIC}" if NTFY_ENABLED else None

last_alert = {}


def send_notification(title, message):
    if not NTFY_ENABLED:
        return

    try:
        req = urllib.request.Request(
            NTFY_URL,
            data=message.encode("utf-8"),
            method="POST",
            headers={
                "Title": title,
                "Priority": "4",
                "Tags": "airplane,warning",
            },
        )

        with urllib.request.urlopen(req, timeout=5) as r:
            r.read()

    except Exception as e:
        print("Errore notifica ntfy:", e)


def haversine_km(lat1, lon1, lat2, lon2):
    R = 6371.0

    phi1 = math.radians(lat1)
    phi2 = math.radians(lat2)
    d_phi = math.radians(lat2 - lat1)
    d_lambda = math.radians(lon2 - lon1)

    a = (
        math.sin(d_phi / 2) ** 2
        + math.cos(phi1) * math.cos(phi2) * math.sin(d_lambda / 2) ** 2
    )

    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c


def bbox_around_point(lat, lon, radius_km):
    lat_delta = radius_km / 111.0
    lon_delta = radius_km / (111.0 * math.cos(math.radians(lat)))

    return (
        lat - lat_delta,
        lon - lon_delta,
        lat + lat_delta,
        lon + lon_delta,
    )


def local_xy_km(lat, lon):
    x = (lon - POINT_LON) * 111.320 * math.cos(math.radians(POINT_LAT))
    y = (lat - POINT_LAT) * 110.574
    return x, y


def predict_closest_approach(lat, lon, velocity_m_s, heading_deg):
    """
    Stima il punto di massimo avvicinamento nei prossimi LOOKAHEAD_MINUTES.
    È una previsione lineare semplice: assume che l'aereo continui con
    velocità e direzione attuali.
    """
    x, y = local_xy_km(lat, lon)

    speed_km_s = velocity_m_s / 1000.0
    theta = math.radians(heading_deg)

    vx = speed_km_s * math.sin(theta)
    vy = speed_km_s * math.cos(theta)

    v2 = vx * vx + vy * vy

    if v2 == 0:
        return 0.0, math.sqrt(x * x + y * y)

    t_star = -((x * vx) + (y * vy)) / v2
    max_t = LOOKAHEAD_MINUTES * 60.0
    t_star = max(0.0, min(t_star, max_t))

    closest_x = x + vx * t_star
    closest_y = y + vy * t_star

    closest_distance = math.sqrt(closest_x * closest_x + closest_y * closest_y)

    return t_star, closest_distance


def fetch_planes():
    lamin, lomin, lamax, lomax = bbox_around_point(
        POINT_LAT,
        POINT_LON,
        FETCH_RADIUS_KM
    )

    url = (
        "https://opensky-network.org/api/states/all"
        f"?lamin={lamin}&lomin={lomin}&lamax={lamax}&lomax={lomax}"
    )

    with urllib.request.urlopen(url, timeout=10) as r:
        return json.load(r)


def check_once():
    now = time.time()

    try:
        data = fetch_planes()
    except Exception as e:
        print("Errore richiesta OpenSky:", e)
        return

    states = data.get("states") or []

    timestamp = data.get("time")
    if timestamp:
        dt = datetime.fromtimestamp(timestamp, tz=timezone.utc)
        print()
        print("=" * 70)
        print("Ora dati UTC:", dt.isoformat())

    print(f"Aerei ricevuti: {len(states)}")

    candidates = []
    alerts = []

    for s in states:
        icao24 = s[0]
        callsign = (s[1] or "").strip()
        country = s[2]
        lon = s[5]
        lat = s[6]
        altitude = s[7]
        velocity = s[9]
        heading = s[10]

        if lat is None or lon is None or velocity is None or heading is None:
            continue

        current_distance = haversine_km(POINT_LAT, POINT_LON, lat, lon)

        t_closest, closest_distance = predict_closest_approach(
            lat,
            lon,
            velocity,
            heading
        )

        plane = {
            "id": icao24,
            "callsign": callsign or icao24,
            "country": country,
            "current_distance": current_distance,
            "closest_distance": closest_distance,
            "minutes_to_closest": t_closest / 60.0,
            "altitude": altitude,
            "velocity": velocity,
            "heading": heading,
        }

        candidates.append(plane)

        if closest_distance <= ALERT_RADIUS_KM:
            alerts.append(plane)

    candidates.sort(key=lambda p: p["closest_distance"])
    alerts.sort(key=lambda p: p["closest_distance"])

    if alerts:
        for p in alerts:
            previous = last_alert.get(p["id"], 0)

            if now - previous < ALERT_COOLDOWN_SECONDS:
                continue

            last_alert[p["id"]] = now

            alt = "?" if p["altitude"] is None else f'{p["altitude"]:.0f} m'

            print()
            print("🚨 ALERT AEREO")
            print(
                f'{p["callsign"]} passerà entro circa '
                f'{p["closest_distance"]:.2f} km dal punto '
                f'tra {p["minutes_to_closest"]:.1f} minuti.'
            )
            print(
                f'Distanza attuale: {p["current_distance"]:.1f} km | '
                f'Quota: {alt} | '
                f'Heading: {p["heading"]:.0f}° | '
                f'Paese: {p["country"]}'
            )

            message = (
                f'{p["callsign"]} passerà entro circa '
                f'{p["closest_distance"]:.2f} km dal punto '
                f'tra {p["minutes_to_closest"]:.1f} minuti.\n'
                f'Distanza attuale: {p["current_distance"]:.1f} km\n'
                f'Quota: {alt}\n'
                f'Heading: {p["heading"]:.0f}°\n'
                f'Paese: {p["country"]}'
            )

            send_notification("Aircraft alert", message)

            print("\a", end="")
    else:
        print("Nessun alert.")

    print()
    print("Più vicini per traiettoria:")
    for p in candidates[:5]:
        alt = "?" if p["altitude"] is None else f'{p["altitude"]:.0f} m'
        print(
            f'{p["callsign"]:10} | '
            f'closest={p["closest_distance"]:6.2f} km | '
            f'tra={p["minutes_to_closest"]:4.1f} min | '
            f'ora={p["current_distance"]:6.1f} km | '
            f'alt={alt:>8} | '
            f'heading={p["heading"]:.0f}°'
        )


def main():
    print("Monitor aerei avviato.")
    print(f"Punto: {POINT_LAT}, {POINT_LON}")
    print(f"Alert se passaggio entro {ALERT_RADIUS_KM} km nei prossimi {LOOKAHEAD_MINUTES} minuti.")

    if NTFY_ENABLED:
        print(f"Notifiche ntfy: attive sul topic {NTFY_TOPIC}")
    else:
        print("Notifiche ntfy: disattivate. Imposta NTFY_TOPIC per attivarle.")

    print("Premi CTRL+C per fermare.")

    try:
        while True:
            check_once()
            time.sleep(CHECK_EVERY_SECONDS)
    except KeyboardInterrupt:
        print()
        print("Monitor fermato manualmente.")


if __name__ == "__main__":
    main()

# GPS Tracking

Stride pulls vehicle positions from a GPS platform and draws them on a map. The
integration currently supports [IOPGPS](https://docs.iopgps.com).

## Object model

| DocType          | Holds                                                                 |
| ---------------- | --------------------------------------------------------------------- |
| **GPS Provider** | One platform account: API URL, credentials, polling interval, token.  |
| **GPS Tracker**  | One physical device: IMEI, its provider, and the vehicle it is on.    |
| **GPS Log**      | One position sample.                                                  |
| **GPS Alarm**    | One alarm event, such as overspeed or SOS.                            |

A vehicle can carry several trackers. Credentials live on the provider, so they
are entered once no matter how many devices the account holds. The Vehicle record
itself holds no GPS field: a tracker names both its provider and its vehicle, and
the Vehicle dashboard lists the trackers fitted to it.

## Setup

1. Ask your provider for API access. IOPGPS issues a **secret key**, which is
   not the account login password.
2. Create a **GPS Provider**. Enter the account name and the secret key. Leave
   the API URL at `https://open.iopgps.com` unless the provider says otherwise.
3. Press **Test Connection**. A green banner shows when the token was issued.
4. Create one **GPS Tracker** per device. Enter its IMEI and select the vehicle.

The polling interval has a five minute minimum, because providers limit how
often you may call them.

## Authentication

IOPGPS does not use a password login. The client sends
`md5(md5(secret_key) + unix_seconds)` and receives a token that is valid for two
hours. Every later call carries that token in the `accessToken` request header.

The handshake is limited to two calls per minute, so Stride stores the token and
its expiry on the GPS Provider and reuses it:

- A scheduled job renews tokens every hour, once they are within 10 minutes
  of expiry. A token that lapses between runs is renewed by the next request.
- If the provider rejects a token during a request, the client authenticates
  again and repeats that one request.
- A file lock stops two workers from authenticating at the same moment.

The token is stored encrypted, like any other password field. It is never
written to the table column in clear text.

## Polling

A cron job runs every five minutes and polls each provider whose own interval
has elapsed. It calls `/api/device/status` once per provider, which returns
every device on the account in a single request, and writes the new positions as
GPS Logs.

`/api/device/location` is **not** polled. The provider forbids it and limits it
to one device per call, so Stride only calls it when a user asks for a live
position.

## On-demand queries

These run only when a user presses a button. They are exposed as whitelisted
methods in `stride/api/gps.py`.

| Method                     | Provider endpoint                              |
| -------------------------- | ---------------------------------------------- |
| `get_device_detail`        | `/api/device/detail`                           |
| `get_device_status`        | `/api/device/status`                           |
| `get_live_location`        | `/api/device/location`                         |
| `get_track_history`        | `/api/device/track/history`                    |
| `get_mileage`              | `/api/device/miles`                            |
| `pull_alarms`              | `/api/device/alarm`                            |
| `get_locations_by_user`    | `/api/device/locations/search-by-organization` |
| `get_vehicle_locations`    | `/api/vehicle/location/v2`                     |
| `get_vehicle_status`       | `/api/vehicle/status/v2`                       |

`pull_alarms` stores what it fetches as GPS Alarms. `poll_now` refreshes one
provider immediately, ignoring its polling interval.

The GPS Tracker form shows Live Location, Device Details, Mileage and Pull
Alarms. The GPS Provider form shows Test Connection and Poll Now.

A history track may not span more than one month, and the provider keeps only
nine months of data.

## Map

The desk page is at **Vehicle Map**. The Vue app has the same view at
`/frontend/vehicle-map`.

The map shows the newest position of each tracked vehicle. A marker is green
when the vehicle moves, blue when it is idle, and red when the vehicle raised an
alarm in the last 24 hours. Select a vehicle and press **Show Route** to draw its
recorded trail for a period, with any alarms marked along it.

## Receiving pushed data

Devices that push to Stride instead of being polled can post to:

- `POST /api/method/stride.api.gps.receive_gps_data`
- `POST /api/method/stride.api.gps.receive_gps_batch`

Both identify the device by `imei` and take unix second timestamps. The caller
needs permission to create GPS Logs.

## Notes for maintainers

- The API client is `stride/gps/iopgps.py`. It only moves requests and responses.
- Ingestion is `stride/gps/sync.py`. It converts provider payloads into records.
- Provider payloads report time in unix seconds and coordinates in WGS84.
- A reading of `0, 0` means the device has no fix. It is discarded.
- Unique constraints on GPS Log and GPS Alarm reject duplicate readings, so two
  workers polling at once cannot write the same reading twice. They are declared
  in each DocType's `on_doctype_update()`, which Frappe runs when the DocType
  syncs, alongside the composite indexes the map queries rely on.

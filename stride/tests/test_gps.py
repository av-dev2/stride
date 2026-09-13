"""Tests for the GPS provider integration: auth, ingestion and map queries."""

import hashlib
from unittest.mock import patch

import frappe
from frappe.tests import IntegrationTestCase
from frappe.utils import add_to_date, now_datetime

from stride.api.gps import receive_gps_data
from stride.gps.iopgps import IOPGPSClient, IOPGPSError
from stride.gps.sync import (
	create_gps_alarm,
	insert_unless_duplicate,
	is_polling_due,
	sync_provider_positions,
	sync_tracker_alarms,
	to_system_datetime,
	to_unix_seconds,
)
from stride.stride.page.vehicle_map.vehicle_map import get_vehicle_locations
from stride.tests.utils import (
	get_or_create_gps_provider,
	get_or_create_gps_tracker,
	get_or_create_vehicle,
)

SAMPLE_GPS_TIME = 1757740000


class FakeResponse:
	"""Stands in for a requests.Response so no network call is made."""

	def __init__(self, payload: dict, status_code: int = 200):
		self.payload = payload
		self.status_code = status_code

	def json(self) -> dict:
		return self.payload

	def raise_for_status(self) -> None:
		if self.status_code >= 400:
			raise AssertionError(f"unexpected HTTP {self.status_code}")


def auth_payload(expires_in_ms: int = 7200000) -> dict:
	return {"code": 0, "accessToken": "token-abc", "expiresIn": expires_in_ms}


def device_payload(imei: str, **overrides) -> dict:
	device = {
		"imei": imei,
		"status": "driving",
		"lat": "-6.7924",
		"lng": "39.2083",
		"speed": 42,
		"course": 180,
		"accStatus": True,
		"positionType": "GPS",
		"gpsTime": SAMPLE_GPS_TIME,
		"chargePercentage": 88,
		"sim": "255700000000",
	}
	device.update(overrides)
	return device


class GPSTestCase(IntegrationTestCase):
	"""Rolls back after every test.

	Frappe v16's IntegrationTestCase only rolls back once per class, so without
	this a fixture built in one test is still visible to the next one and the
	deduplication tests pass or fail depending on execution order.
	"""

	def setUp(self):
		super().setUp()
		self.addCleanup(frappe.db.rollback)


class TestGPSTimestamps(GPSTestCase):
	def test_unix_seconds_round_trip(self):
		self.assertEqual(to_unix_seconds(to_system_datetime(SAMPLE_GPS_TIME)), SAMPLE_GPS_TIME)

	def test_empty_timestamp_is_none(self):
		self.assertIsNone(to_system_datetime(None))
		self.assertIsNone(to_system_datetime(0))


class TestIOPGPSAuthentication(GPSTestCase):
	def setUp(self):
		super().setUp()
		self.provider = frappe.get_doc("GPS Provider", get_or_create_gps_provider())

	def test_signature_is_double_md5_of_secret_and_time(self):
		expected = hashlib.md5(f"{hashlib.md5(b'secret').hexdigest()}1700000000".encode()).hexdigest()

		self.assertEqual(IOPGPSClient._build_signature("secret", 1700000000), expected)

	def test_token_lifetime_is_read_as_milliseconds(self):
		with patch("requests.request", return_value=FakeResponse(auth_payload(7200000))):
			token, lifetime = self.provider.get_client().request_access_token()

		self.assertEqual(token, "token-abc")
		self.assertEqual(lifetime, 7200)

	def test_refresh_stores_token_and_expiry(self):
		with patch("requests.request", return_value=FakeResponse(auth_payload())):
			self.provider.refresh_access_token()

		self.assertEqual(self.provider.get_password("access_token"), "token-abc")
		self.assertTrue(self.provider.has_valid_token)

	def test_token_within_safety_margin_is_not_valid(self):
		self.provider.store_access_token("stale", add_to_date(now_datetime(), minutes=5))
		self.provider.reload()

		self.assertFalse(self.provider.has_valid_token)

	def test_valid_token_is_reused_without_re_authenticating(self):
		with patch("requests.request", return_value=FakeResponse(auth_payload())) as request:
			self.provider.get_access_token()
			self.provider.get_access_token()

		self.assertEqual(request.call_count, 1)

	def test_expired_token_mid_request_is_refreshed_and_the_call_retried(self):
		self.provider.store_access_token("stale", add_to_date(now_datetime(), hours=2))
		self.provider.reload()

		responses = [
			FakeResponse({"code": 10004, "result": "access token is invalid"}),
			FakeResponse(auth_payload()),
			FakeResponse({"code": 0, "data": [device_payload("111111111111111")]}),
		]

		with patch("requests.request", side_effect=responses) as request:
			devices = self.provider.get_client().get_device_status(imei="111111111111111")

		self.assertEqual(len(devices), 1)
		self.assertEqual(request.call_count, 3)
		self.assertEqual(self.provider.get_password("access_token"), "token-abc")

	def test_a_rejected_token_is_replaced_even_when_its_expiry_looks_valid(self):
		"""The refresh must not hand back the same token the provider just refused."""
		self.provider.store_access_token("stale", add_to_date(now_datetime(), hours=2))
		self.provider.reload()

		with patch("requests.request", return_value=FakeResponse(auth_payload())):
			self.assertEqual(self.provider.refresh_access_token(rejected_token="stale"), "token-abc")

	def test_a_concurrent_waiter_reuses_a_token_it_has_not_seen_rejected(self):
		self.provider.store_access_token("fresh", add_to_date(now_datetime(), hours=2))
		self.provider.reload()

		with patch("requests.request") as request:
			self.assertEqual(self.provider.refresh_access_token(), "fresh")

		request.assert_not_called()

	def test_non_auth_error_is_raised_without_retrying(self):
		responses = [
			FakeResponse(auth_payload()),
			FakeResponse({"code": 10007, "result": "device not found"}),
		]

		with patch("requests.request", side_effect=responses):
			with self.assertRaises(IOPGPSError):
				self.provider.get_client().get_device_status(imei="000000000000000")

	def test_the_token_is_not_stored_in_clear_text(self):
		"""A Password field written through db_set would leak the token into the column."""
		with patch("requests.request", return_value=FakeResponse(auth_payload())):
			self.provider.refresh_access_token()

		column_value = frappe.db.get_value("GPS Provider", self.provider.name, "access_token")

		self.assertNotEqual(column_value, "token-abc")
		self.assertEqual(self.provider.get_stored_token(), "token-abc")

	def test_clearing_the_token_removes_the_stored_secret(self):
		with patch("requests.request", return_value=FakeResponse(auth_payload())):
			self.provider.refresh_access_token()

		self.provider.clear_access_token()

		self.assertIsNone(self.provider.get_stored_token())

	def test_changing_the_secret_key_clears_the_stored_token(self):
		self.provider.store_access_token("token-abc", add_to_date(now_datetime(), hours=2))
		self.provider.reload()

		self.provider.secret_key = "rotated-key"
		self.provider.save()

		self.assertFalse(self.provider.has_valid_token)


class TestGPSPositionSync(GPSTestCase):
	def setUp(self):
		super().setUp()
		self.provider = get_or_create_gps_provider()
		self.vehicle = get_or_create_vehicle("STRIDE-GPS-1")
		self.tracker = get_or_create_gps_tracker("111111111111111", self.vehicle, self.provider)

	def poll(self, devices: list[dict]) -> dict:
		responses = [FakeResponse(auth_payload()), FakeResponse({"code": 0, "data": devices})]
		with patch("requests.request", side_effect=responses):
			return sync_provider_positions(self.provider)

	def test_device_status_becomes_a_gps_log(self):
		result = self.poll([device_payload(self.tracker)])

		self.assertEqual(result["created"], 1)

		log = frappe.get_last_doc("GPS Log", filters={"gps_tracker": self.tracker})
		self.assertEqual(log.vehicle, self.vehicle)
		self.assertEqual(log.latitude, -6.7924)
		self.assertEqual(log.longitude, 39.2083)
		self.assertEqual(log.speed, 42)
		self.assertEqual(log.heading, 180)
		self.assertEqual(log.device_status, "driving")
		self.assertEqual(log.acc_status, 1)
		self.assertEqual(log.position_type, "GPS")

	def test_repeated_polls_do_not_duplicate_a_sample(self):
		self.poll([device_payload(self.tracker)])
		result = self.poll([device_payload(self.tracker)])

		self.assertEqual(result["created"], 0)
		self.assertEqual(frappe.db.count("GPS Log", {"gps_tracker": self.tracker}), 1)

	def test_a_racing_duplicate_is_rejected_by_the_database(self):
		"""The existence check is not atomic, so the unique constraint is the real guard."""
		self.poll([device_payload(self.tracker)])

		racing_copy = frappe.get_doc(
			{
				"doctype": "GPS Log",
				"vehicle": self.vehicle,
				"gps_tracker": self.tracker,
				"timestamp": to_system_datetime(SAMPLE_GPS_TIME),
				"latitude": -6.7924,
				"longitude": 39.2083,
			}
		)

		self.assertFalse(insert_unless_duplicate(racing_copy))
		self.assertEqual(frappe.db.count("GPS Log", {"gps_tracker": self.tracker}), 1)

	def test_devices_without_a_tracker_are_skipped(self):
		result = self.poll([device_payload("999999999999999")])

		self.assertEqual(result["created"], 0)
		self.assertEqual(result["skipped"], 1)

	def test_a_device_without_coordinates_is_skipped(self):
		result = self.poll([device_payload(self.tracker, lat="", lng="")])

		self.assertEqual(result["created"], 0)
		self.assertEqual(frappe.db.count("GPS Log", {"gps_tracker": self.tracker}), 0)

	def test_a_null_island_reading_is_not_a_position(self):
		"""A device with no fix reports 0,0; storing it drops a marker off Africa."""
		result = self.poll([device_payload(self.tracker, lat="0", lng="0")])

		self.assertEqual(result["created"], 0)
		self.assertEqual(frappe.db.count("GPS Log", {"gps_tracker": self.tracker}), 0)

	def test_a_push_without_a_sim_keeps_the_recorded_one(self):
		self.poll([device_payload(self.tracker)])

		receive_gps_data(
			imei=self.tracker,
			timestamp=SAMPLE_GPS_TIME + 60,
			latitude=-6.8,
			longitude=39.3,
		)

		self.assertEqual(frappe.db.get_value("GPS Tracker", self.tracker, "sim_number"), "255700000000")

	def test_polling_updates_the_tracker_state_and_provider_timestamp(self):
		self.poll([device_payload(self.tracker)])

		tracker = frappe.get_doc("GPS Tracker", self.tracker)
		self.assertEqual(tracker.last_status, "driving")
		self.assertEqual(tracker.sim_number, "255700000000")
		self.assertTrue(frappe.db.get_value("GPS Provider", self.provider, "last_polled_on"))

	def test_inactive_trackers_are_not_polled(self):
		frappe.db.set_value("GPS Tracker", self.tracker, "is_active", 0)

		result = self.poll([device_payload(self.tracker)])

		self.assertEqual(result["created"], 0)


class TestPollingSchedule(GPSTestCase):
	def test_a_provider_never_polled_is_due(self):
		self.assertTrue(is_polling_due(frappe._dict(last_polled_on=None, polling_interval_minutes=15)))

	def test_a_provider_inside_its_interval_is_not_due(self):
		provider = frappe._dict(
			last_polled_on=add_to_date(now_datetime(), minutes=-5),
			polling_interval_minutes=15,
		)
		self.assertFalse(is_polling_due(provider))

	def test_a_provider_past_its_interval_is_due(self):
		provider = frappe._dict(
			last_polled_on=add_to_date(now_datetime(), minutes=-20),
			polling_interval_minutes=15,
		)
		self.assertTrue(is_polling_due(provider))


class TestGPSAlarms(GPSTestCase):
	def setUp(self):
		super().setUp()
		self.provider = get_or_create_gps_provider()
		self.vehicle = get_or_create_vehicle("STRIDE-GPS-2")
		self.tracker_name = get_or_create_gps_tracker("222222222222222", self.vehicle, self.provider)
		self.tracker = frappe.get_doc("GPS Tracker", self.tracker_name)

	def alarm_payload(self, **overrides) -> dict:
		alarm = {
			"alarmCode": "overspeed",
			"message": "Speed above limit",
			"alarmTime": SAMPLE_GPS_TIME,
			"lat": "-6.8",
			"lng": "39.3",
			"speed": 96,
			"course": 90,
			"address": "Bagamoyo Road",
			"positionType": "GPS",
			"batteryCapacity": 70,
			"extData": {"mp4": "https://media.example/a.mp4", "images": ["https://media.example/a.jpg"]},
		}
		alarm.update(overrides)
		return alarm

	def test_alarm_payload_becomes_a_gps_alarm(self):
		self.assertTrue(create_gps_alarm(self.tracker, self.alarm_payload()))

		alarm = frappe.get_last_doc("GPS Alarm", filters={"gps_tracker": self.tracker_name})
		self.assertEqual(alarm.vehicle, self.vehicle)
		self.assertEqual(alarm.alarm_code, "overspeed")
		self.assertEqual(alarm.speed, 96)
		self.assertEqual(alarm.video_url, "https://media.example/a.mp4")
		self.assertEqual(alarm.image_urls, "https://media.example/a.jpg")

	def test_the_same_alarm_is_not_stored_twice(self):
		create_gps_alarm(self.tracker, self.alarm_payload())

		self.assertFalse(create_gps_alarm(self.tracker, self.alarm_payload()))
		self.assertEqual(frappe.db.count("GPS Alarm", {"gps_tracker": self.tracker_name}), 1)

	def test_an_alarm_without_a_code_is_rejected(self):
		self.assertFalse(create_gps_alarm(self.tracker, self.alarm_payload(alarmCode="")))

	def test_pulling_alarms_stores_only_the_new_ones(self):
		responses = [
			FakeResponse(auth_payload()),
			FakeResponse({"code": 0, "details": [self.alarm_payload(), self.alarm_payload()]}),
		]

		with patch("requests.request", side_effect=responses):
			result = sync_tracker_alarms(
				self.tracker_name,
				add_to_date(now_datetime(), days=-1),
				now_datetime(),
			)

		self.assertEqual(result["fetched"], 2)
		self.assertEqual(result["created"], 1)


class TestGPSPush(GPSTestCase):
	def setUp(self):
		super().setUp()
		self.provider = get_or_create_gps_provider()
		self.vehicle = get_or_create_vehicle("STRIDE-GPS-3")
		self.tracker = get_or_create_gps_tracker("333333333333333", self.vehicle, self.provider)

	def test_a_pushed_point_creates_a_log(self):
		result = receive_gps_data(
			imei=self.tracker,
			timestamp=SAMPLE_GPS_TIME,
			latitude=-6.8,
			longitude=39.3,
			speed=30,
		)

		self.assertTrue(result["gps_log"])
		self.assertFalse(result["gps_alarm"])
		self.assertEqual(frappe.db.count("GPS Log", {"gps_tracker": self.tracker}), 1)

	def test_a_pushed_point_with_an_alarm_code_creates_both_records(self):
		result = receive_gps_data(
			imei=self.tracker,
			timestamp=SAMPLE_GPS_TIME,
			latitude=-6.8,
			longitude=39.3,
			alarm_code="sos",
			alarm_message="Panic button",
		)

		self.assertTrue(result["gps_log"])
		self.assertTrue(result["gps_alarm"])

	def test_an_unknown_imei_is_rejected(self):
		with self.assertRaises(frappe.ValidationError):
			receive_gps_data(imei="444444444444444", timestamp=SAMPLE_GPS_TIME)


class TestVehicleMapQuery(GPSTestCase):
	def setUp(self):
		super().setUp()
		self.provider = get_or_create_gps_provider()
		self.vehicle = get_or_create_vehicle("STRIDE-GPS-4")
		self.tracker = get_or_create_gps_tracker("555555555555555", self.vehicle, self.provider)

	def make_log(self, minutes_ago: int, **overrides) -> None:
		log = {
			"doctype": "GPS Log",
			"vehicle": self.vehicle,
			"gps_tracker": self.tracker,
			"timestamp": add_to_date(now_datetime(), minutes=-minutes_ago),
			"latitude": -6.79,
			"longitude": 39.2,
			"speed": 10,
		}
		log.update(overrides)
		frappe.get_doc(log).insert(ignore_permissions=True)

	def test_only_the_newest_sample_per_vehicle_is_returned(self):
		self.make_log(30, speed=5)
		self.make_log(1, speed=55)

		rows = [row for row in get_vehicle_locations() if row["vehicle"] == self.vehicle]

		self.assertEqual(len(rows), 1)
		self.assertEqual(rows[0]["speed"], 55)
		self.assertEqual(rows[0]["license_plate"], self.vehicle)

	def test_two_trackers_reporting_together_yield_one_marker(self):
		"""A vehicle with several trackers must still draw as a single marker."""
		second_tracker = get_or_create_gps_tracker("666666666666666", self.vehicle, self.provider)
		shared_timestamp = add_to_date(now_datetime(), minutes=-1)

		self.make_log(1, timestamp=shared_timestamp)
		self.make_log(1, timestamp=shared_timestamp, gps_tracker=second_tracker)

		rows = [row for row in get_vehicle_locations() if row["vehicle"] == self.vehicle]

		self.assertEqual(len(rows), 1)

	def test_a_recent_alarm_is_attached_to_the_location(self):
		self.make_log(1)
		frappe.get_doc(
			{
				"doctype": "GPS Alarm",
				"vehicle": self.vehicle,
				"gps_tracker": self.tracker,
				"alarm_code": "overspeed",
				"alarm_description": "Speed above limit",
				"alarm_time": add_to_date(now_datetime(), minutes=-10),
			}
		).insert(ignore_permissions=True)

		row = next(row for row in get_vehicle_locations() if row["vehicle"] == self.vehicle)

		self.assertEqual(row["alarm_code"], "overspeed")
		self.assertEqual(row["alarm_description"], "Speed above limit")

	def test_an_old_alarm_is_not_attached(self):
		self.make_log(1)
		frappe.get_doc(
			{
				"doctype": "GPS Alarm",
				"vehicle": self.vehicle,
				"gps_tracker": self.tracker,
				"alarm_code": "overspeed",
				"alarm_time": add_to_date(now_datetime(), days=-3),
			}
		).insert(ignore_permissions=True)

		row = next(row for row in get_vehicle_locations() if row["vehicle"] == self.vehicle)

		self.assertIsNone(row["alarm_code"])

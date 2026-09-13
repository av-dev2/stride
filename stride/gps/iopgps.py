# Copyright (c) 2026, elius-dev and contributors
# For license information, please see license.txt

"""HTTP client for the IOPGPS Open API.

Reference: https://docs.iopgps.com (OpenAPI spec at /doc?api=iop&lang=en).

Authentication is a signed handshake rather than a password login: the caller
sends ``md5(md5(secret_key) + unix_seconds)`` and receives a token valid for two
hours, which every later call carries in the ``accessToken`` request header.
The handshake is rate limited to two calls per minute, so tokens are stored on
the GPS Provider and reused until they approach expiry.
"""

import hashlib
import time

import frappe
import requests
from frappe import _

DEFAULT_API_URL = "https://open.iopgps.com"
REQUEST_TIMEOUT_SECONDS = 30
DEFAULT_TOKEN_LIFETIME_SECONDS = 2 * 60 * 60


class IOPGPSError(frappe.ValidationError):
	"""Raised when the IOPGPS API rejects a request."""


class IOPGPSClient:
	"""Request layer over the IOPGPS Open API for a single GPS Provider."""

	def __init__(self, provider):
		self.provider = provider
		self.base_url = (provider.api_url or DEFAULT_API_URL).rstrip("/")

	# ------------------------------------------------------------------
	# Authentication
	# ------------------------------------------------------------------

	def request_access_token(self) -> tuple[str, int]:
		"""Perform the auth handshake and return the token and its lifetime in seconds."""
		secret_key = self.provider.get_password("secret_key")

		if not secret_key:
			frappe.throw(_("GPS Provider {0} has no Secret Key.").format(self.provider.name), IOPGPSError)

		if self.provider.authentication_type == "Bearer Token":
			return secret_key, DEFAULT_TOKEN_LIFETIME_SECONDS

		timestamp = int(time.time())
		payload = {
			"appid": self.provider.account_name,
			"time": timestamp,
			"signature": self._build_signature(secret_key, timestamp),
		}
		body = self._send("POST", "/api/auth", json=payload)

		token = body.get("accessToken")
		if not token:
			frappe.throw(
				_("IOPGPS did not return an access token for {0}.").format(self.provider.name),
				IOPGPSError,
			)

		# expiresIn is reported in milliseconds.
		lifetime = int(body.get("expiresIn") or 0) // 1000
		return token, lifetime or DEFAULT_TOKEN_LIFETIME_SECONDS

	@staticmethod
	def _build_signature(secret_key: str, timestamp: int) -> str:
		"""Return md5(md5(secret_key) + timestamp), 32 character lowercase, as IOPGPS requires."""
		hashed_secret = hashlib.md5(secret_key.encode()).hexdigest()
		return hashlib.md5(f"{hashed_secret}{timestamp}".encode()).hexdigest()

	# ------------------------------------------------------------------
	# Transport
	# ------------------------------------------------------------------

	def get(self, path: str, params: dict | None = None) -> dict:
		"""Send an authenticated GET, re-authenticating once if the token is rejected."""
		params = {key: value for key, value in (params or {}).items() if value not in (None, "")}
		token = self.provider.get_access_token()

		try:
			return self._send("GET", path, token=token, params=params)
		except IOPGPSError as error:
			if not getattr(error, "is_auth_failure", False):
				raise

			# The stored expiry said the token was fine, so only the provider's
			# refusal tells us it is not. Pass it along so the refresh cannot
			# hand the same token straight back.
			token = self.provider.refresh_access_token(rejected_token=token)
			return self._send("GET", path, token=token, params=params)

	def _send(self, method: str, path: str, token: str | None = None, **kwargs) -> dict:
		headers = {"accessToken": token} if token else {}

		response = requests.request(
			method,
			f"{self.base_url}{path}",
			headers=headers,
			timeout=REQUEST_TIMEOUT_SECONDS,
			**kwargs,
		)

		if response.status_code in (401, 403):
			raise self._auth_error(
				_("IOPGPS rejected the access token (HTTP {0}).").format(response.status_code)
			)

		response.raise_for_status()
		body = response.json()

		code = body.get("code")
		if code in (None, 0):
			return body

		message = body.get("result") or body.get("message") or _("unknown error")
		error_text = _("IOPGPS {0} failed with code {1}: {2}").format(path, code, message)

		if "token" in str(message).lower():
			raise self._auth_error(error_text)

		frappe.throw(error_text, IOPGPSError)

	@staticmethod
	def _auth_error(message: str) -> IOPGPSError:
		error = IOPGPSError(message)
		error.is_auth_failure = True
		return error

	# ------------------------------------------------------------------
	# Equipment
	# ------------------------------------------------------------------

	def get_device_status(self, imei: str | None = None, account: str | None = None) -> list[dict]:
		"""Return status and position for one device, or every device on an account."""
		body = self.get("/api/device/status", {"imei": imei, "account": account})
		return body.get("data") or []

	def get_device_detail(self, imei: str) -> dict:
		"""Return device, account and bound-vehicle details for one device."""
		body = self.get("/api/device/detail", {"imei": imei})
		return body.get("data") or {}

	def get_device_location(self, imei: str) -> dict:
		"""Return the reverse-geocoded live position of one device.

		IOPGPS forbids polling this endpoint, so call it only on user request.
		"""
		body = self.get("/api/device/location", {"imei": imei})
		return {
			"latitude": body.get("lat"),
			"longitude": body.get("lng"),
			"address": body.get("address"),
			"gps_time": body.get("gpsTime"),
		}

	def get_track_history(
		self, imei: str, start_time: int, end_time: int, only_gps: bool = False
	) -> list[dict]:
		"""Return the position trail of one device. The span may not exceed one month."""
		body = self.get(
			"/api/device/track/history",
			{
				"imei": imei,
				"startTime": start_time,
				"endTime": end_time,
				"onlyGps": 1 if only_gps else 0,
			},
		)
		return body.get("data") or []

	def get_alarms(self, imei: str, start_time: int, end_time: int) -> list[dict]:
		"""Return alarm records raised by one device in a time range."""
		body = self.get(
			"/api/device/alarm",
			{"imei": imei, "startTime": start_time, "endTime": end_time},
		)
		return body.get("details") or []

	def get_mileage(self, imei: str, start_time: int, end_time: int) -> dict:
		"""Return distance travelled and running time for one device in a time range."""
		body = self.get(
			"/api/device/miles",
			{"imei": imei, "startTime": start_time, "endTime": end_time},
		)
		return {"miles": body.get("miles") or 0, "run_time": body.get("runTime") or 0}

	def get_locations_by_organization(
		self, account_id: str | None = None, include_sub: bool = True
	) -> list[dict]:
		"""Return bare positions for every device under an account."""
		body = self.get(
			"/api/device/locations/search-by-organization",
			{"accountId": account_id, "isTakeSub": 1 if include_sub else 0},
		)
		return body.get("data") or []

	# ------------------------------------------------------------------
	# Vehicles
	# ------------------------------------------------------------------

	def get_vehicle_locations(
		self, account_id: str | None = None, include_sub: bool = True, start: int = 0, limit: int = 1000
	) -> dict:
		"""Return a page of vehicle positions keyed by number plate (Vehicle Location 2.0)."""
		body = self.get(
			"/api/vehicle/location/v2",
			{
				"accountId": account_id,
				"isTakeSub": 1 if include_sub else 0,
				"start": start,
				"limit": limit,
				"needCount": 1,
			},
		)
		data = body.get("data") or {}
		return {"total": data.get("countVehicle") or 0, "vehicles": data.get("list") or []}

	def get_vehicle_locations_v1(self, account_id: str | None = None, include_sub: bool = True) -> list[dict]:
		"""Return every vehicle position in one unpaginated call (Vehicle Location 1.0)."""
		body = self.get(
			"/api/vehicle/location",
			{"accountId": account_id, "isTakeSub": 1 if include_sub else 0},
		)
		return (body.get("data") or {}).get("list") or []

	def get_vehicle_status(self, license_number: str | None = None, vin: str | None = None) -> list[dict]:
		"""Return device status for a vehicle by number plate or frame number (car 2.0)."""
		body = self.get(
			"/api/vehicle/status/v2",
			{"licenseNumber": license_number, "vin": vin},
		)
		return body.get("data") or []

	def search_vehicle_status(self, content: str) -> list[dict]:
		"""Return device status for vehicles matching a free-text search (car 1.0)."""
		body = self.get("/api/vehicle/status", {"content": content})
		return body.get("data") or []

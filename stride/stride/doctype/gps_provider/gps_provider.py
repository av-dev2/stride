# Copyright (c) 2026, elius-dev and contributors
# For license information, please see license.txt

import frappe
from frappe import _
from frappe.model.document import Document
from frappe.utils import add_to_date, get_datetime, now_datetime
from frappe.utils.password import (
	get_decrypted_password,
	remove_encrypted_password,
	set_encrypted_password,
)
from frappe.utils.synchronization import filelock

TOKEN_SAFETY_MARGIN_SECONDS = 10 * 60


class GPSProvider(Document):
	"""Credentials and endpoint configuration for one GPS tracking account."""

	# begin: auto-generated types
	# This code is auto-generated. Do not modify anything in this block.

	from typing import TYPE_CHECKING

	if TYPE_CHECKING:
		from frappe.types import DF

		access_token: DF.Password | None
		account_id: DF.Data | None
		account_name: DF.Data
		api_url: DF.Data
		authentication_type: DF.Literal["Signature", "Bearer Token"]
		enabled: DF.Check
		last_polled_on: DF.Datetime | None
		polling_interval_minutes: DF.Int
		provider_name: DF.Data
		provider_type: DF.Literal["IOPGPS"]
		secret_key: DF.Password
		token_expires_on: DF.Datetime | None
	# end: auto-generated types

	def validate(self) -> None:
		self.api_url = (self.api_url or "").strip().rstrip("/")

		if self.polling_interval_minutes and self.polling_interval_minutes < 5:
			frappe.throw(
				_("Polling Interval must be at least 5 minutes to stay within provider rate limits.")
			)

	def on_update(self) -> None:
		if self.has_value_changed("secret_key") or self.has_value_changed("account_name"):
			self.clear_access_token()

	@property
	def has_valid_token(self) -> bool:
		"""True when a stored token exists and is not within the refresh margin of expiry."""
		if not self.access_token or not self.token_expires_on:
			return False

		margin = add_to_date(now_datetime(), seconds=TOKEN_SAFETY_MARGIN_SECONDS)
		return get_datetime(self.token_expires_on) > margin

	def get_client(self):
		"""Return an API client bound to this provider."""
		from stride.gps.iopgps import IOPGPSClient

		return IOPGPSClient(self)

	def get_access_token(self) -> str:
		"""Return a usable access token, refreshing it when missing or near expiry."""
		if self.has_valid_token:
			return self.get_stored_token()

		return self.refresh_access_token()

	def get_stored_token(self) -> str | None:
		return get_decrypted_password(self.doctype, self.name, "access_token", raise_exception=False)

	def refresh_access_token(self, rejected_token: str | None = None) -> str:
		"""Authenticate against the provider and store the new token and its expiry.

		Providers rate limit the handshake hard (IOPGPS allows two calls a minute),
		so the lock serialises attempts rather than letting every worker fire one
		at once. A caller that starts a fresh transaction also sees a token stored
		while it waited and reuses it instead of authenticating again.

		`rejected_token` is the token the caller just had refused. A stored token
		is only reused when it differs from that one; otherwise the expiry column
		says the token is fine while the provider disagrees, and only a fresh
		handshake resolves it.
		"""
		with filelock(f"gps_provider_token_{self.name}", timeout=60):
			self.reload()
			stored_token = self.get_stored_token() if self.has_valid_token else None

			if stored_token and stored_token != rejected_token:
				return stored_token

			token, expires_in_seconds = self.get_client().request_access_token()
			self.store_access_token(token, add_to_date(now_datetime(), seconds=expires_in_seconds))

		return token

	def store_access_token(self, token: str, expires_on) -> None:
		"""Save the token encrypted.

		`db_set` skips the password handling that runs on save, so writing a
		Password field through it would leave the token in clear text in the
		table column.
		"""
		set_encrypted_password(self.doctype, self.name, token, "access_token")
		self.db_set(
			{"access_token": "*" * len(token), "token_expires_on": expires_on},
			update_modified=False,
		)

	def clear_access_token(self) -> None:
		"""Forget the stored token so the next call authenticates again."""
		remove_encrypted_password(self.doctype, self.name, "access_token")
		self.db_set({"access_token": None, "token_expires_on": None}, update_modified=False)


@frappe.whitelist()
def test_connection(provider: str) -> dict:
	"""Authenticate against the provider and report whether the credentials work."""
	frappe.only_for("System Manager")

	doc = frappe.get_doc("GPS Provider", provider)
	doc.refresh_access_token()

	return {"token_expires_on": doc.token_expires_on}

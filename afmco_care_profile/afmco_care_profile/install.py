# Copyright (c) 2026, AFMCO and contributors
import hashlib

import frappe
from helpdesk.consts import DEFAULT_TICKET_TEMPLATE

CARE_PROJECT_ROW = {"fieldname": "care_project", "required": 0, "hide_from_customer": 1}
CLOSE_GUARD = "Care Close Guard"
CLOSE_GUARD_IDENTITY = {
	"script_type": "DocType Event",
	"reference_doctype": "HD Ticket",
	"doctype_event": "Before Save",
}
CLOSE_GUARD_SHA256 = "0eab77af59050f5a2833e44bd223c414a2c8e10a90781d146f13826e549f7b4d"


def install_line(step, outcome, **fields):
	print(" | ".join(["afmco_care_profile", step, outcome, *("%s:%s" % item for item in fields.items())]))


def after_sync():
	care_project_row()
	close_guard_retire()


def care_project_row():
	template = frappe.get_doc("HD Ticket Template", DEFAULT_TICKET_TEMPLATE)
	if any(row.fieldname == CARE_PROJECT_ROW["fieldname"] for row in template.fields):
		install_line("care_project_row", "present", template=template.name)
		return
	if not template.custom_field_exists(CARE_PROJECT_ROW["fieldname"]):
		install_line("care_project_row", "refused", reason="Custom Field HD Ticket-care_project absent")
		return
	template.append("fields", CARE_PROJECT_ROW)
	try:
		template.save()
	except frappe.ValidationError as error:
		install_line("care_project_row", "refused", reason=" ".join(str(error).split()))
		return
	install_line("care_project_row", "added", template=template.name)


def close_guard_retire():
	script = frappe.db.get_value(
		"Server Script", CLOSE_GUARD, [*CLOSE_GUARD_IDENTITY, "disabled", "script"], as_dict=True
	)
	if not script:
		install_line("close_guard_retire", "absent", server_script=CLOSE_GUARD)
		return
	if script.disabled:
		install_line("close_guard_retire", "already_disabled", server_script=CLOSE_GUARD)
		return
	digest = hashlib.sha256((script.script or "").strip().encode()).hexdigest()
	identity = {key: script[key] for key in CLOSE_GUARD_IDENTITY}
	if identity != CLOSE_GUARD_IDENTITY or digest != CLOSE_GUARD_SHA256:
		install_line("close_guard_retire", "refused", reason="identity or payload differs", sha256=digest)
		return
	server_script = frappe.get_doc("Server Script", CLOSE_GUARD)
	server_script.disabled = 1
	server_script.save()
	install_line("close_guard_retire", "disabled", server_script=CLOSE_GUARD, sha256=digest)

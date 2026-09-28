# Copyright (c) 2026, AFMCO and contributors
import hashlib

import frappe
from helpdesk.consts import DEFAULT_TICKET_TEMPLATE

from afmco_care_profile.afmco_care_profile.profile import PROFILE_REQUIRED

CARE_PROJECT_ROW = {"fieldname": "care_project", "required": 0, "hide_from_customer": 1}
CLOSE_GUARD = "Care Close Guard"
CLOSE_GUARD_IDENTITY = {
	"script_type": "DocType Event",
	"reference_doctype": "HD Ticket",
	"doctype_event": "Before Save",
}
CLOSE_GUARD_SHA256 = "0eab77af59050f5a2833e44bd223c414a2c8e10a90781d146f13826e549f7b4d"
MY_WORKSPACES_LABEL = "My Workspaces"
MY_WORKSPACES_LOGO = "/assets/afmco_care_profile/images/desktop-icon-my-workspaces.svg"


def install_line(step, outcome, **fields):
	print(" | ".join(["afmco_care_profile", step, outcome, *("%s:%s" % item for item in fields.items())]))


def reconcile():
	care_project_row()
	required_rows()
	close_guard_retire()
	my_workspaces_logo()


def my_workspaces_logo():
	if not frappe.db.exists("DocType", "Desktop Icon"):
		install_line("my_workspaces_logo", "absent", doctype="Desktop Icon")
		return
	icon = frappe.db.get_value(
		"Desktop Icon", {"label": MY_WORKSPACES_LABEL}, ["name", "logo_url"], as_dict=True
	)
	if not icon:
		install_line("my_workspaces_logo", "absent", label=MY_WORKSPACES_LABEL)
		return
	if icon.logo_url:
		install_line("my_workspaces_logo", "present", logo_url=icon.logo_url)
		return
	frappe.db.set_value("Desktop Icon", icon.name, "logo_url", MY_WORKSPACES_LOGO, update_modified=False)
	frappe.clear_cache()
	install_line("my_workspaces_logo", "filled", logo_url=MY_WORKSPACES_LOGO)


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


def required_rows():
	template = frappe.get_doc("HD Ticket Template", DEFAULT_TICKET_TEMPLATE)
	rows = [row for row in template.fields if row.fieldname in PROFILE_REQUIRED]
	absent = sorted(set(PROFILE_REQUIRED) - {row.fieldname for row in rows})
	optional = [row for row in rows if not row.required]
	if not optional:
		install_line("required_rows", "present", template=template.name, absent=",".join(absent) or "-")
		return
	for row in optional:
		row.required = 1
	try:
		template.save()
	except frappe.ValidationError as error:
		install_line("required_rows", "refused", reason=" ".join(str(error).split()))
		return
	install_line(
		"required_rows",
		"set",
		template=template.name,
		fields=",".join(row.fieldname for row in optional),
		absent=",".join(absent) or "-",
	)


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

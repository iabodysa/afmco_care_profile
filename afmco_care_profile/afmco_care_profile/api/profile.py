# Copyright (c) 2026, AFMCO and contributors
import frappe

from afmco_care_profile.afmco_care_profile.profile import PROFILE_FIELDS, PROFILE_PHONE, profile_prefills


@frappe.whitelist()
def care_profile_get():
	if not profile_prefills():
		return {}
	email = frappe.db.get_value("User", frappe.session.user, "email")
	contact = email and frappe.db.get_value("Contact", {"email_id": email})
	if not contact:
		return {}
	values = frappe.db.get_value("Contact", contact, [*PROFILE_FIELDS, "mobile_no"], as_dict=True)
	return {**{fieldname: values.get(fieldname) for fieldname in PROFILE_FIELDS}, PROFILE_PHONE: values.mobile_no}

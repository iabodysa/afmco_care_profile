# Copyright (c) 2026, AFMCO and contributors
import re

import frappe
from frappe import _
from helpdesk.utils import is_agent

PROFILE_FIELDS = ("employee_name", "iqama_number", "city", "working_id")
PROFILE_PHONE = "phone_number"
PROFILE_REQUIRED = (
    "employee_name",
    "iqama_number",
    "phone_number",
    "city",
    "working_id",
)
PROFILE_IQAMA = re.compile(r"[12][0-9]{9}")
PROFILE_MOBILE = re.compile(r"05[0-9]{8}")
PROFILE_DIGITS = str.maketrans("٠١٢٣٤٥٦٧٨٩۰۱۲۳۴۵۶۷۸۹", "01234567890123456789")
PROFILE_SYSTEM_USERS = ("Guest", "Administrator")


def profile_enforced():
    return frappe.session.user not in PROFILE_SYSTEM_USERS


def profile_prefills():
    return profile_enforced() and not is_agent()


def care_profile_guard(ticket):
    if not profile_prefills():
        return
    for fieldname in (*PROFILE_FIELDS, PROFILE_PHONE):
        ticket.set(
            fieldname, (ticket.get(fieldname) or "").strip().translate(PROFILE_DIGITS)
        )
    missing = [fieldname for fieldname in PROFILE_REQUIRED if not ticket.get(fieldname)]
    if missing:
        labels = ", ".join(_(ticket.meta.get_label(fieldname)) for fieldname in missing)
        frappe.throw(_("Enter {0} before you submit the ticket.").format(labels))
    if not PROFILE_IQAMA.fullmatch(ticket.iqama_number):
        frappe.throw(
            _("{0} must be 10 digits starting with 1 or 2.").format(
                _(ticket.meta.get_label("iqama_number"))
            )
        )
    if not PROFILE_MOBILE.fullmatch(ticket.phone_number):
        frappe.throw(
            _("{0} must be 10 digits starting with 05.").format(
                _(ticket.meta.get_label("phone_number"))
            )
        )


def care_profile_sync(ticket):
    if not profile_enforced():
        return
    if not ticket.contact:
        frappe.log_error(
            title="Care profile sync skipped: ticket has no contact",
            reference_doctype="HD Ticket",
            reference_name=ticket.name,
        )
        return
    contact = frappe.get_doc("Contact", ticket.contact)
    changed = {
        fieldname: ticket.get(fieldname)
        for fieldname in PROFILE_FIELDS
        if ticket.get(fieldname) and ticket.get(fieldname) != contact.get(fieldname)
    }
    phone = ticket.get(PROFILE_PHONE)
    phone_changed = bool(phone) and phone != contact.mobile_no
    if not changed and not phone_changed:
        return
    frappe.db.savepoint("care_profile_sync")
    try:
        contact.update(changed)
        if phone_changed:
            matched = next(
                (row for row in contact.phone_nos if row.phone == phone), None
            )
            for row in contact.phone_nos:
                row.is_primary_mobile_no = int(row is matched)
            if not matched:
                contact.append("phone_nos", {"phone": phone, "is_primary_mobile_no": 1})
        contact.save(ignore_permissions=True)
    except Exception:
        frappe.db.rollback(save_point="care_profile_sync")
        frappe.log_error(
            title="Care profile sync failed",
            reference_doctype="HD Ticket",
            reference_name=ticket.name,
        )

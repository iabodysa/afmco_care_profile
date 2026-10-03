# Copyright (c) 2026, AFMCO and contributors
import frappe
from frappe import _

from afmco_care_profile.afmco_care_profile.profile import (
    PROFILE_FIELDS,
    PROFILE_PHONE,
    profile_apply,
    profile_clean,
    profile_contact,
    profile_prefills,
)


@frappe.whitelist()
def care_profile_get():
    if not profile_prefills():
        return {}
    contact = profile_contact()
    if not contact:
        return {}
    values = frappe.db.get_value(
        "Contact", contact, [*PROFILE_FIELDS, "mobile_no"], as_dict=True
    )
    return {
        **{fieldname: values.get(fieldname) for fieldname in PROFILE_FIELDS},
        PROFILE_PHONE: values.mobile_no,
    }


@frappe.whitelist(methods=["POST"])
def care_profile_set(
    employee_name: str | None = None,
    iqama_number: str | None = None,
    phone_number: str | None = None,
    city: str | None = None,
    working_id: str | None = None,
):
    if not profile_prefills():
        frappe.throw(
            _("Only an employee updates these details."), frappe.PermissionError
        )
    contact = profile_contact()
    if not contact:
        frappe.throw(
            _("Your account has no contact record. Ask the care team to add one.")
        )
    values = profile_clean(
        {
            "employee_name": employee_name,
            "iqama_number": iqama_number,
            PROFILE_PHONE: phone_number,
            "city": city,
            "working_id": working_id,
        },
        _("Enter {0} before you save your details."),
    )
    profile_apply(frappe.get_doc("Contact", contact), values)
    return care_profile_get()

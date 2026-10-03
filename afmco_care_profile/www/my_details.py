# Copyright (c) 2026, AFMCO and contributors
import frappe
from frappe import _
from helpdesk.utils import is_agent

from afmco_care_profile.afmco_care_profile.api.profile import care_profile_get
from afmco_care_profile.afmco_care_profile.profile import PROFILE_REQUIRED
from afmco_care_profile.afmco_care_profile.website import set_language_switch

no_cache = 1


def get_context(context):
    if frappe.session.user == "Guest":
        frappe.local.flags.redirect_location = "/login?redirect-to=/my-details"
        raise frappe.Redirect(302)
    if is_agent():
        frappe.local.flags.redirect_location = "/helpdesk"
        raise frappe.Redirect(302)

    set_language_switch(context)
    context.title = _("My contact details")
    context.body_class = "care-home"
    meta = frappe.get_meta("HD Ticket")
    profile = care_profile_get()
    context.has_contact = bool(profile)
    context.fields = [
        frappe._dict(
            fieldname=fieldname,
            label=_(meta.get_label(fieldname)),
            value=profile.get(fieldname) or "",
        )
        for fieldname in PROFILE_REQUIRED
    ]

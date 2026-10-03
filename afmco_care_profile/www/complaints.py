# Copyright (c) 2026, AFMCO and contributors
import frappe
from frappe import _
from frappe.utils import format_date
from helpdesk.utils import is_agent

from afmco_care_profile.afmco_care_profile.website import set_language_switch

no_cache = 1


def get_context(context):
	if frappe.session.user == "Guest":
		frappe.local.flags.redirect_location = "/login?redirect-to=/complaints"
		raise frappe.Redirect(302)
	if is_agent():
		frappe.local.flags.redirect_location = "/helpdesk"
		raise frappe.Redirect(302)

	set_language_switch(context)
	context.title = _("My complaints")
	context.body_class = "care-home"
	context.first_name = frappe.db.get_value("User", frappe.session.user, "first_name")
	context.tickets = frappe.get_list(
		"HD Ticket",
		fields=["name", "subject", "status", "status_category", "modified"],
		order_by="modified desc",
		limit_page_length=50,
	)
	for ticket in context.tickets:
		ticket.date = format_date(ticket.modified)

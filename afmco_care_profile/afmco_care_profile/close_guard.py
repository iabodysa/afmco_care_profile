# Copyright (c) 2026, AFMCO and contributors
import frappe
from frappe import _
from frappe.utils import now_datetime

CLOSING_STATUSES = ("Closed", "Resolved")


def care_close_guard(doc):
	previous = doc.get_doc_before_save()

	if previous:
		doc.care_resolution_confirmed = previous.care_resolution_confirmed
		doc.care_resolution_confirmed_by = previous.care_resolution_confirmed_by
		doc.care_resolution_confirmed_on = previous.care_resolution_confirmed_on
	else:
		doc.care_resolution_confirmed = 0
		doc.care_resolution_confirmed_by = None
		doc.care_resolution_confirmed_on = None

	raised_by = (doc.raised_by or "").strip().lower()
	if "<" in raised_by and ">" in raised_by:
		raised_by = raised_by.split("<", 1)[1].split(">", 1)[0].strip()

	session_user = (frappe.session.user or "").strip().lower()
	entering_close = doc.status in CLOSING_STATUSES and (
		not previous or previous.status not in CLOSING_STATUSES
	)
	session_is_agent = bool(
		((not previous and raised_by) or entering_close)
		and frappe.db.exists("Has Role", {"parent": frappe.session.user, "parenttype": "User", "role": "Agent"})
		and frappe.db.exists("HD Agent", {"user": frappe.session.user, "is_active": 1})
	)

	if not previous and raised_by and not (session_is_agent and session_user != raised_by):
		open_ticket = frappe.db.get_value(
			"HD Ticket", {"raised_by": raised_by, "status": ["not in", CLOSING_STATUSES]}, "name"
		)
		if open_ticket:
			frappe.throw(
				_(
					"You already have an open ticket #{0}. Please follow up on it instead of opening a new one."
				).format(open_ticket)
			)

	if not entering_close:
		return

	closed_by_employee = bool(raised_by) and session_user == raised_by

	money_ticket = bool(doc.care_involves_payment)
	if doc.ticket_type and not money_ticket:
		money_ticket = bool(frappe.db.get_value("HD Ticket Type", doc.ticket_type, "care_money_category"))

	if money_ticket and closed_by_employee and not doc.care_resolution_confirmed:
		doc.care_resolution_confirmed = 1
		doc.care_resolution_confirmed_by = frappe.session.user
		doc.care_resolution_confirmed_on = now_datetime()

	if not doc.care_project:
		if closed_by_employee:
			doc.status = previous.status if previous else "Open"
			frappe.msgprint(_("Thank you. The care team will close this ticket."))
		else:
			frappe.throw(_("Set the Project field before you close or resolve this ticket."))
	elif money_ticket and not doc.care_resolution_confirmed:
		if not session_is_agent:
			frappe.throw(
				_(
					"This ticket involves a payment. It closes only after the employee confirms the resolution by closing it from the portal, or by the care team with a written Close Reason."
				)
			)
		if not (doc.care_close_reason or "").strip():
			frappe.throw(
				_("Write the reason in Close Reason to close this payment ticket without the employee's confirmation.")
			)

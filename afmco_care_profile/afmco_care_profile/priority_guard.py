# Copyright (c) 2026, AFMCO and contributors
import frappe
from frappe import _

from afmco_care_profile.afmco_care_profile.agent import care_agent_session

PRIORITY_CHOSEN = "care_priority_chosen"


def care_priority_supplied(doc):
    doc.flags.care_priority_supplied = bool(doc.priority)


def care_priority_guard(doc):
    if not doc.meta.has_field(PRIORITY_CHOSEN):
        return

    previous = doc.get_doc_before_save()
    already_chosen = bool(previous and previous.get(PRIORITY_CHOSEN))

    if not (getattr(frappe.local, "request", None) and care_agent_session()):
        doc.set(PRIORITY_CHOSEN, int(already_chosen))
        return

    if previous:
        priority_chosen = doc.has_value_changed("priority")
    else:
        priority_chosen = bool(doc.flags.care_priority_supplied)

    if not (already_chosen or doc.get(PRIORITY_CHOSEN) or priority_chosen):
        frappe.throw(
            _(
                "Choose the ticket priority, or confirm it in the Priority Confirmed field, before you save this ticket."
            )
        )

    doc.set(PRIORITY_CHOSEN, 1)

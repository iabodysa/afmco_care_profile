# Copyright (c) 2026, AFMCO and contributors
import frappe


def care_agent_session():
    return bool(
        frappe.db.exists(
            "Has Role",
            {"parent": frappe.session.user, "parenttype": "User", "role": "Agent"},
        )
        and frappe.db.exists("HD Agent", {"user": frappe.session.user, "is_active": 1})
    )

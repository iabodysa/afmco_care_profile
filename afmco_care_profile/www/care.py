# Copyright (c) 2026, AFMCO and contributors
from urllib.parse import urlencode

import frappe
from frappe import _
from frappe.utils import get_fullname

no_cache = 1


def get_context(context):
	lang = "ar" if (frappe.local.lang or "").startswith("ar") else "en"
	switch_lang = "en" if lang == "ar" else "ar"
	login_query = {"redirect-to": "/helpdesk/home"}
	if frappe.form_dict._lang:
		login_query["_lang"] = lang

	context.title = _("Care")
	context.body_class = "care-home"
	context.is_guest = frappe.session.user == "Guest"
	context.full_name = "" if context.is_guest else get_fullname()
	context.login_url = "/login?" + urlencode(login_query, safe="/")
	context.switch_lang = switch_lang
	context.switch_label = frappe.db.get_value("Language", switch_lang, "language_name") or switch_lang

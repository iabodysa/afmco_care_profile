# Copyright (c) 2026, AFMCO and contributors
from urllib.parse import urlencode

import frappe
from frappe import _
from frappe.utils import get_fullname

from afmco_care_profile.afmco_care_profile.website import set_language_switch

no_cache = 1


def get_context(context):
	lang = set_language_switch(context)
	login_query = {"redirect-to": "/complaints"}
	if frappe.form_dict._lang:
		login_query["_lang"] = lang

	context.title = _("Care")
	context.body_class = "care-home"
	context.is_guest = frappe.session.user == "Guest"
	context.full_name = "" if context.is_guest else get_fullname()
	context.login_url = "/login?" + urlencode(login_query, safe="/")

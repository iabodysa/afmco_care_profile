# Copyright (c) 2026, AFMCO and contributors
import frappe


def set_language_switch(context):
	lang = "ar" if (frappe.local.lang or "").startswith("ar") else "en"
	context.switch_lang = "en" if lang == "ar" else "ar"
	context.switch_label = frappe.db.get_value("Language", context.switch_lang, "language_name") or context.switch_lang
	return lang

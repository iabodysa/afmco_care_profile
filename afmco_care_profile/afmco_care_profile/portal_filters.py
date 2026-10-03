# Copyright (c) 2026, AFMCO and contributors
from helpdesk.helpdesk.doctype.hd_ticket.hd_ticket import customer_not_allowed_fields

CUSTOMER_HIDDEN_FILTERS = (*customer_not_allowed_fields, "care_project")


class CarePortalFilters:
    @staticmethod
    def filter_standard_fields(fields):
        return [field for field in fields if field["name"] not in CUSTOMER_HIDDEN_FILTERS]

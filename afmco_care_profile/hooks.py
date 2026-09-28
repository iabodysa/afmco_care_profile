# Copyright (c) 2026, AFMCO and contributors
app_name = "afmco_care_profile"
app_title = "Care"
app_publisher = "AFMCO"
app_description = "Employee profile fields for the AFMCO Helpdesk portal"
app_email = "afm@afmcoltd.com"
app_license = "MIT"

required_apps = ["helpdesk"]

web_include_css = "/assets/afmco_care_profile/css/login.css"

add_to_apps_screen = [
    {
        "name": app_name,
        "logo": "/assets/helpdesk/desk/desk.png",
        "title": "AFMCO",
        "route": "https://app.afmco.sa/desk",
        "has_permission": "helpdesk.utils.is_agent",
    }
]

extend_doctype_class = {
    "HD Ticket": ["afmco_care_profile.afmco_care_profile.hd_ticket.CareHDTicket"],
}

after_sync = ["afmco_care_profile.afmco_care_profile.install.reconcile"]
after_migrate = ["afmco_care_profile.afmco_care_profile.install.reconcile"]

fixtures = [
    {
        "dt": "Custom Field",
        "filters": [
            [
                "name",
                "in",
                [
                    "HD Ticket-employee_name",
                    "HD Ticket-iqama_number",
                    "HD Ticket-phone_number",
                    "HD Ticket-city",
                    "HD Ticket-working_id",
                    "Contact-employee_name",
                    "Contact-iqama_number",
                    "Contact-city",
                    "Contact-working_id",
                    "HD Ticket-care_priority_chosen",
                ],
            ]
        ],
    },
    {"dt": "HD Form Script", "filters": [["name", "in", ["Care Profile Prefill"]]]},
]

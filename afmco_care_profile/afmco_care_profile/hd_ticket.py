# Copyright (c) 2026, AFMCO and contributors
from afmco_care_profile.afmco_care_profile.close_guard import care_close_guard
from afmco_care_profile.afmco_care_profile.profile import (
    care_profile_guard,
    care_profile_sync,
)


class CareHDTicket:
    def before_insert(self):
        care_profile_guard(self)
        super().before_insert()

    def before_save(self):
        super().before_save()
        care_close_guard(self)

    def after_insert(self):
        super().after_insert()
        care_profile_sync(self)

from django.contrib import admin

from apps.bonuses.models import BonusLedgerEntry, BonusSpendRequest
from apps.referrals.models import ReferralLead
from apps.users.models import Participant


admin.site.register(Participant)
admin.site.register(ReferralLead)
admin.site.register(BonusLedgerEntry)
admin.site.register(BonusSpendRequest)

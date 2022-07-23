from django.contrib import admin

from main.models import Honeypot, Attacker, HoneypotHasAttacker, AttackDump

admin.site.register(Honeypot)
admin.site.register(Attacker)
admin.site.register(HoneypotHasAttacker)
admin.site.register(AttackDump)

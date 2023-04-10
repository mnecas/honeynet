from django.contrib import admin

from main.models import Honeypot, Attacker, HoneypotAttack, AttackDump, Honeynet, HoneypotLog

admin.site.register(Honeypot)
admin.site.register(Attacker)
admin.site.register(HoneypotAttack)
admin.site.register(AttackDump)
admin.site.register(Honeynet)
admin.site.register(HoneypotLog)

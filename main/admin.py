from django.contrib import admin

from main.models import Honeypot, Attacker, HoneypotAttack, AttackDump

admin.site.register(Honeypot)
admin.site.register(Attacker)
admin.site.register(HoneypotAttack)
admin.site.register(AttackDump)

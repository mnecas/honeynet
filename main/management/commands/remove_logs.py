from django.core.management.base import BaseCommand, CommandError
from main.models import HoneypotAttack, Honeypot, AttackDump, Honeynet, HoneypotExport
from ftplib import FTP
from django.shortcuts import get_object_or_404
import os


class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--honeynet",
            action="store",
            help="Specify the honeynet which should be sent",
        )

    def handle(self, *args, **options):
        # The magic line

        honeynet = Honeynet.objects.filter(pk=options["honeynet"])
        if not honeynet:
            raise CommandError("No honeynet")

        honeypots = Honeypot.objects.filter(honeynet=honeynet)
        for honeypot in honeypots:
            pcaps = AttackDump.objects.filter(honeypot=honeypot)
            for pcap in pcaps:
                pcap.delete()

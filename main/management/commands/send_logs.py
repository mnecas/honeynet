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
        honeynet = get_object_or_404(Honeynet, pk=options["honeynet"])
        root_path = os.path.dirname(os.path.dirname(os.path.realpath(__file__)))

        ftp = FTP()
        ftp.connect(honeynet.export.address, 21)
        ftp.login(honeynet.export.username, honeynet.export.password)

        honeypots = Honeypot.objects.filter(honeynet=honeynet)
        for honeypot in honeypots:
            pcaps = AttackDump.objects.filter(honeypot=honeypot)
            for pcap in pcaps:
                print(pcap.path)

        # Read file in binary mode
        file = open('notes.txt','rb')
        ftp.storbinary(f"STOR notes.txt", file)
        file.close()
        folderName='test'
        if folderName not in ftp.nlst():
            ftp.mkd(folderName)
        # change working direcotry
        ftp.cwd("test")
        print(ftp.dir())
        print(ftp.nlst("test"))

        ftp.quit()

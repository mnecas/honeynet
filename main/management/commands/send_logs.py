from django.core.management.base import BaseCommand, CommandError
from main.models import HoneypotAttack, Honeypot, AttackDump, Honeynet, HoneypotExport
from ftplib import FTP
from django.conf import settings
import os


# TODO: CLEANUP CODE!
class Command(BaseCommand):
    def add_arguments(self, parser):
        # Named (optional) arguments
        parser.add_argument(
            "--honeynet",
            action="store",
            help="Specify the honeynet which should be sent",
        )

    def _create_dirs(self, dirname):
        if dirname:
            self._create_dirs(os.path.dirname(dirname))
        if dirname and dirname not in self.ftp.nlst():
            try:
                self.ftp.mkd(dirname)
            except:
                print(f"Dirname '{dirname}' already exists")

    def _change_to_subdir(self, filename):
        dirname = os.path.dirname(filename)
        if dirname:
            self._change_to_subdir(dirname)
            self.ftp.cwd(dirname)

    def _send_file(self, filepath, filename=None):
        ftp_dir = self.ftp.pwd()
        if filename:
            self.ftp.cwd(os.path.dirname(filename))
            filename = os.path.basename(filename)
        else:
            filename = os.path.basename(filepath)
            print(os.path.dirname(filepath))
            self.ftp.cwd(os.path.basename(os.path.dirname(filepath)))
        file = open(filepath, "rb")
        self.ftp.storbinary(f"STOR {filename}", file)
        self.ftp.cwd(ftp_dir)
        file.close()

    def handle(self, *args, **options):
        honeynet = Honeynet.objects.filter(pk=options["honeynet"])
        if not honeynet:
            raise CommandError(f"Could not find the honeynet with id '{honeynet}'.")

        honeynet = honeynet.first()
        if not honeynet.export:
            raise CommandError(f"The honeynet '{honeynet}' does not have a export.")

        self.ftp = FTP()
        self.ftp.connect(honeynet.export.address, 21)
        self.ftp.login(honeynet.export.username, honeynet.export.password)
        if honeynet.export.path:
            self.ftp.cwd(honeynet.export.path)
        self._create_dirs("honeynet")
        self.ftp.cwd("honeynet")

        if honeynet.name not in self.ftp.nlst():
            self.ftp.mkd(honeynet.name)
        self.ftp.cwd(honeynet.name)

        honeypots = Honeypot.objects.filter(honeynet=honeynet)

        for honeypot in honeypots:
            pcaps = AttackDump.objects.filter(honeypot=honeypot)
            if not pcaps:
                continue
            self._create_dirs(os.path.dirname(pcaps.first().path))
            for pcap in pcaps:
                self._send_file(os.path.join(settings.MEDIA_ROOT, pcap.path))
                pcap.delete()

        syslog_path = "/var/log/remote/"
        print(honeynet.name)
        honeypots = [
            f
            for f in os.listdir(os.path.join(syslog_path, honeynet.name))
            if os.path.isdir(os.path.join(syslog_path, honeynet.name, f))
        ]
        for honeypot in honeypots:
            honeypot_logs = [
                f
                for f in os.listdir(os.path.join(syslog_path, honeynet.name, honeypot))
                if os.path.isfile(os.path.join(syslog_path, honeynet.name, honeypot, f))
            ]
            # self._send_file(pcap.path)
            honeypot_dir = honeypot.split("[")[0]
            print(f"[Syslog dir] {honeypot_dir}")
            self._create_dirs(honeypot_dir)
            for log in honeypot_logs:
                print(f"[Syslog log] {log}")
                self._send_file(
                    os.path.join(syslog_path, honeynet.name, honeypot, log),
                    os.path.join(honeypot_dir, log),
                )
                os.remove(os.path.join(syslog_path, honeynet.name, honeypot, log))
        self.ftp.quit()

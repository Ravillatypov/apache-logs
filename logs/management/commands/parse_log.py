import requests
from django.core.management.base import BaseCommand
from django.db.utils import Error
from django_tqdm import BaseCommand as TqdmBaseCommand

from logs.models import AccessLog
from logs.utils import parse_apache_log


class Command(TqdmBaseCommand, BaseCommand):
    help = 'Download and parse apache access log'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)

    def handle(self, *args, **options):
        url = options.get('url', '')
        content = b''
        resp = requests.head(url, allow_redirects=True)
        if resp.status_code >= 300:
            self.info('Not valid url')
            return
        file_size = int(resp.headers.get('Content-Length'))
        header = {'Range': f'bytes=0-{file_size}'}
        progress_bar = self.tqdm(
            total=file_size,
            unit='B',
            unit_scale=True,
            desc=f'Parsing log {url.split("/")[-1]}'
        )
        resp = requests.get(url, headers=header, stream=True, allow_redirects=True)
        for chunk in resp.iter_content(chunk_size=1024):
            if chunk:
                content += chunk
                progress_bar.update(1024)
            *lines, content = content.splitlines()
            for line in lines:
                self.parse_and_save(line.decode())
        if content:
            self.parse_and_save(content.decode())

    def parse_and_save(self, line: str):
        data = parse_apache_log(line)
        if data:
            try:
                AccessLog.objects.create(**data)
            except Error as err:
                self.info(f'Error on saving log: {err}')

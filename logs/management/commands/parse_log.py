from datetime import datetime

import requests
from django.core.management.base import BaseCommand
from django_tqdm import BaseCommand as TqdmBaseCommand

from logs.models import AccessLog, Parsing
from logs.utils import parse_apache_log


class Command(TqdmBaseCommand, BaseCommand):
    help = 'Download and parse apache access log'

    def add_arguments(self, parser):
        parser.add_argument('url', type=str)
        parser.add_argument(
            '-c',
            '--chunk_size',
            type=int,
            default=1,
            help='Chunk size in MB'
        )

    def handle(self, *args, **options):
        url = options.get('url', '')
        started_at = datetime.utcnow()
        parsed_length = 0
        chunk_size = options.get('chunk_size') * 1024 * 1024
        content = b''
        resp = requests.head(url, allow_redirects=True)
        if resp.status_code >= 300:
            self.info('Not valid url')
            return
        file_size = int(resp.headers.get('Content-Length'))
        last_parsing = Parsing.objects.filter(url=url).order_by('-started_at').first()
        if last_parsing:
            first_byte = last_parsing.content_length + 1
        else:
            first_byte = 0
        header = {'Range': f'bytes={first_byte}-{file_size}'}
        progress_bar = self.tqdm(
            total=file_size,
            unit='B',
            unit_scale=True,
            desc=f'Parsing log {url.split("/")[-1]}'
        )
        objects = []
        resp = requests.get(url, headers=header, stream=True, allow_redirects=True)
        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                content += chunk
                progress_bar.update(chunk_size)
                parsed_length += len(chunk)
            *lines, content = content.splitlines()
            for line in lines:
                data = parse_apache_log(line.decode())
                if data:
                    objects.append(
                        AccessLog(**data)
                    )
            if objects:
                AccessLog.objects.bulk_create(objects)
            objects = []
        if content:
            data = parse_apache_log(content.decode())
            if data:
                AccessLog.objects.create(**data)
        progress_bar.close()
        Parsing.objects.create(
            started_at=started_at,
            finished_at=datetime.utcnow(),
            url=url,
            content_length=parsed_length,
        )
        self.stdout.write(f'Parsing is finished')

from datetime import datetime
from typing import Union, BinaryIO

import pytz
import requests
from django.core.management.base import BaseCommand
from django_tqdm import BaseCommand as TqdmBaseCommand

from logs.models import AccessLog, Parsing
from logs.utils import parse_apache_log


class Command(TqdmBaseCommand, BaseCommand):
    help = 'Download and parse apache access log'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.progress_bar = None
        self.first_byte = 0

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
        started_at = datetime.now(tz=pytz.utc)
        parsed_length = 0
        chunk_size = options.get('chunk_size') * 1024 * 1024

        with open(started_at.strftime('unparsed-%Y-%m-%dT%T.log'), 'ab') as unparsed:
            try:
                resp = self.get_stream(url)
                if resp is None:
                    return

                parsed_length = self.parse_and_save(resp, chunk_size, unparsed)
            except (KeyboardInterrupt, OSError):
                pass
            except Exception as err:
                self.stderr.write(f'Error: {err}')
            finally:
                self.progress_bar.close()
                Parsing.objects.create(
                    started_at=started_at,
                    finished_at=datetime.now(tz=pytz.utc),
                    url=url,
                    content_length=parsed_length + self.first_byte,
                )
        self.stdout.write(f'Parsing is finished')

    def get_stream(self, url: str) -> Union[requests.Response, None]:
        resp = requests.head(url, allow_redirects=True)
        if resp.status_code >= 300:
            self.stderr.write('Not valid url')
            return

        # get response size, last parsing info for this url
        file_size = int(resp.headers.get('Content-Length'))
        last_parsing = Parsing.objects.filter(url=url).order_by('-finished_at').first()
        if last_parsing:
            first_byte = last_parsing.content_length + 1
        else:
            first_byte = 0
        header = {'Range': f'bytes={first_byte}-{file_size}'}

        self.progress_bar = self.tqdm(
            total=file_size,
            initial=first_byte,
            unit='B',
            unit_scale=True,
            desc=f'Parsing log {url.split("/")[-1]}'
        )
        self.first_byte = first_byte
        return requests.get(url, headers=header, stream=True, allow_redirects=True)

    def parse_and_save(self, resp: requests.Response, chunk_size: int, log: BinaryIO) -> int:
        objects = []
        content = b''
        parsed_length = 0

        for chunk in resp.iter_content(chunk_size=chunk_size):
            if chunk:
                content += chunk
                self.progress_bar.update(chunk_size)
            parsed_length += len(content)
            *lines, content = content.splitlines()
            parsed_length -= len(content)
            for line in lines:
                data = parse_apache_log(line.decode())
                if data:
                    objects.append(AccessLog(**data))
                else:
                    log.writelines([line])
            if objects:
                AccessLog.objects.bulk_create(objects)
            objects.clear()

        if content:
            data = parse_apache_log(content.decode())
            if data:
                parsed_length += len(content)
                AccessLog.objects.create(**data)
            else:
                log.writelines([content])
        return parsed_length

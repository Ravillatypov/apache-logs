import logging
import re
from datetime import datetime
from typing import Any, Union, Dict

logger = logging.getLogger(__name__)
HTTP_METHODS = ('GET', 'POST', 'PUT', 'PATCH', 'DELETE', 'HEAD', 'OPTIONS', 'CONNECT', 'TRACE')


def get_int(number: str, default: Any = None) -> Union[int, Any]:
    try:
        result = int(number)
    except ValueError:
        return default
    return result


def get_datetime(date_str: str, format: str = '', default: Any = None) -> Union[datetime, Any]:
    try:
        result = datetime.strptime(date_str, format)
    except ValueError:
        return default
    return result


def get_ip(value: str) -> str:
    g = re.match(r'(\d{1,3}\.){3}\d{1,3}', value)
    if g:
        return g.group()
    return ''


def parse_apache_log(line: str) -> Union[Dict[str, Any], None]:
    """
    Parse apache log and return as dict or None
    :param line:
    :return:
    """
    result = []
    current = ''
    for i in line.split():
        if current:
            current += ' ' + i.replace('"', '')
            if i.endswith('"') or i.endswith(']'):
                result.append(current)
                current = ''
            continue
        if i.startswith('"') and i.endswith('"') or i.startswith('[') and i.endswith(']'):
            result.append(i.replace('"', ''))
            continue
        elif i.startswith('"') or i.startswith('['):
            current = i.replace('"', '')
        else:
            result.append(i)

    if len(result) < 9:
        logger.warning(f'Invalid format: {line}')
        return None
    method, path, *_ = result[4].split()
    method = method.strip().upper()
    if method not in HTTP_METHODS:
        logger.warning(f'Invalid http method: {line}')
        return None
    return {
        'ip': get_ip(result[0]),
        'date': get_datetime(result[3], '[%d/%b/%Y:%H:%M:%S %z]'),
        'method': method,
        'path': path.strip()[:255],
        'response_code': get_int(result[5]),
        'response_size': get_int(result[6]),
        'user_agent': result[8].strip()[:255]
    }

from datetime import datetime
from typing import Any, Union, Dict


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
        return None
    method, path, *_ = result[4].split()
    return {
        'ip': result[0],
        'date': get_datetime(result[3], '[%d/%b/%Y:%H:%M:%S %z]'),
        'method': method,
        'path': path,
        'response_code': get_int(result[5]),
        'response_size': get_int(result[6]),
        'user_agent': result[8]
    }

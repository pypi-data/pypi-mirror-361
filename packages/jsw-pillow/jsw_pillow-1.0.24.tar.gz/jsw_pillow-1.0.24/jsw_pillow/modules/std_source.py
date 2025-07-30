import requests
import io


def std_source(target):
    is_str = isinstance(target, str)
    result = target
    if is_str:
        is_remote = target.startswith('http')
        if is_remote:
            # remote url
            result = requests.get(target, stream=True).raw
        else:
            # local file
            result = open(target, 'rb')
    else:
        is_bytes = isinstance(target, bytes)
        if is_bytes:
            result = io.BytesIO(target)

    return result, is_str

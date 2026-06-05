import hashlib


def generate_fingerprint(exception_type, stack_trace, message='', source='backend'):
    if stack_trace:
        lines = [line.strip() for line in stack_trace.split('\n') if line.strip()]
        top_lines = lines[:3]
        raw = source + ':' + exception_type + '|'.join(top_lines)
    else:
        raw = source + ':' + exception_type + message
    return hashlib.md5(raw.encode('utf-8')).hexdigest()

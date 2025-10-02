from flask import request

TRUSTED_PROXIES = ['127.0.0.1', '127.0.0.2']

def get_client_ip():
    client_ip = request.remote_addr
    if client_ip in TRUSTED_PROXIES:
        forwarded_for = request.headers.get('X-Forwarded_For', '')
        if forwarded_for:
            return forwarded_for.split(',')[0].strip()
    return client_ip
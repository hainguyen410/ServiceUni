def request_path(url):
    first_path = None
    if url:
        first_path = url.split('/')[0]
    return first_path

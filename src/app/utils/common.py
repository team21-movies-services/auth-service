from urllib import parse


def append_query_params_to_url(url: str, params: dict) -> str:
    url_parts = list(parse.urlparse(url))
    query_params = dict(parse.parse_qsl(url_parts[4]))
    query_params.update(params)
    url_parts[4] = parse.urlencode(query_params)
    return parse.urlunparse(url_parts)

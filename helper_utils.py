def query_params_to_string(query_params):
    query = ''

    def parse_param(key, value):
        escaped_value = value
        if ' ' in value:
            escaped_value = '\"%s\"' % value
        return ':'.join([key, escaped_value])

    for k, v in query_params.items():

        if type(v) is list:
            for vv in v:
                query = ' '.join([query, parse_param(k, vv)])
        else:
            query = ' '.join([query, parse_param(k, v)])

    return query.strip()

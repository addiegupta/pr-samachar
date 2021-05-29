def query_params_to_string(query_params):
    query = ' '.join('%s:%s' % (k, v) for k, v in query_params.items())
    return query

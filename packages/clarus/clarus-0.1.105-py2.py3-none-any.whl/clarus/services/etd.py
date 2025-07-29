import clarus.services

def etdim(output=None, **params):
    return clarus.services.api_request('ETD', 'ETDIM', output=output, **params)

def im(output=None, **params):
    return clarus.services.api_request('ETD', 'IM', output=output, **params)


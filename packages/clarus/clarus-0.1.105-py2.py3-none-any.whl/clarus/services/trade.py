import clarus.services

def caplets(output=None, **params):
    return clarus.services.api_request('Trade', 'Caplets', output=output, **params)

def cashflows(output=None, **params):
    return clarus.services.api_request('Trade', 'Cashflows', output=output, **params)

def convert(output=None, **params):
    return clarus.services.api_request('Trade', 'Convert', output=output, **params)

def fixings(output=None, **params):
    return clarus.services.api_request('Trade', 'Fixings', output=output, **params)

def marketdatanames(output=None, **params):
    return clarus.services.api_request('Trade', 'MarketDataNames', output=output, **params)

def price(output=None, **params):
    return clarus.services.api_request('Trade', 'Price', output=output, **params)

def transform(output=None, **params):
    return clarus.services.api_request('Trade', 'Transform', output=output, **params)

def validate(output=None, **params):
    return clarus.services.api_request('Trade', 'Validate', output=output, **params)

